import logging
from django.utils import timezone
from backend.celery import app
from .models import Task
import datetime
from django.db import transaction
from django.db.models import OuterRef, Subquery
from django.contrib.auth import get_user_model
from dateutil.rrule import rrulestr
from .selectors import get_future_childrens_of_parent_task, get_task_future_siblings
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .serializers import TaskSerializer

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Helper Celery task to regenerate series when parent template changes
# ---------------------------------------------------------------------------


def _generate_rec_tasks_for_parent(
    parent_task: Task, occurences_dates: list[datetime.datetime]
):
    results = []
    for occurence_date in occurences_dates:
        with transaction.atomic():
            # make sure we don't create two task for same column_date & recurrence_parent
            if not Task.objects.filter(
                column_date__date=occurence_date.date(),
                title=parent_task.title,
                description=parent_task.description,
            ).exists():
                child, created = Task.objects.get_or_create(
                    user=parent_task.user,
                    title=parent_task.title,
                    description=parent_task.description,
                    order=parent_task.order,
                    is_completed=False,
                    duration=parent_task.duration,
                    column_date=occurence_date,
                    start_at=parent_task.start_at,
                    end_at=parent_task.end_at,
                    recurrence_rule=parent_task.recurrence_rule,
                    recurrence_parent=parent_task,
                    project=parent_task.project,
                    status=Task.ON_BOARD,  # TODO: what if task is on calendar?
                )
                if created:
                    # copy over tags
                    child.tags.set(parent_task.tags.all())

                action = "created" if created else "updated"
                msg = f"Recurring task {action}: parent_task_id={parent_task.pk} child_task_id={child.pk} date={occurence_date}"
                logger.info(msg)
                results.append(msg)
    return results


def _gen_rec_tasks_for_parent_or_sibling(
    parent_or_sibling_task: Task,
    max_events: int = 20,
    days_ahead: int = 20,
):
    # every rec task ( wether parent or child ) have a task.start_at
    # if not parent_or_sibling_task.start_at:
    #     logger.warning(
    #         f"No start_at for parent_task_id={parent_or_sibling_task.pk}, setting to now"
    #     )
    #     parent_or_sibling_task.start_at = timezone.now()
    #     parent_or_sibling_task.save()

    start_after = parent_or_sibling_task.column_date or datetime.datetime.today()
    window_end = start_after + datetime.timedelta(days=days_ahead)
    try:
        rule = rrulestr(
            parent_or_sibling_task.recurrence_rule,
            dtstart=start_after,
        )
    except Exception as e:
        result = f"Error parsing recurrence rule for parent_task_id={parent_or_sibling_task.pk}: {e}"
        logger.error(result)
        return result

    occurrences = list(rule.between(after=start_after, before=window_end, inc=True))[
        :max_events
    ]
    if not occurrences:
        result = (
            f"No upcoming recurrence for parent_task_id={parent_or_sibling_task.pk}"
        )
        logger.info(result)
        return result

    return _generate_rec_tasks_for_parent(parent_or_sibling_task, occurrences)


def _notify_frontend(group_name, data):
    # ------------------- Notify connected client(s) --------------------------------------
    try:
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(group_name, data)  # type:ignore
    except Exception as e:
        logger.error(f"Failed to send refresh_tasks event: {e}", exc_info=True)


@app.task(name="regenerate_recurring_series")
def regenerate_recurring_series(parent_or_sibling_id: int):
    """Delete all *future* children of a parent recurring task and rebuild them.

    Called when the user edits a single child and we propagate changes to the
    parent template.  Past instances (start_at <= now) remain untouched.
    """
    try:
        parent_or_sibling_task: Task = Task.objects.get(id=parent_or_sibling_id)
    except Task.DoesNotExist:
        logger.warning(
            f"Parent/Sibling task not found for regeneration: id={parent_or_sibling_id}"
        )
        return "parent-missing"

    deleted_count = 0
    deleted_ids = []
    future_tasks = None
    # if it's a parent task then delete all future childrens
    if parent_or_sibling_task.is_rec_task_parent:
        # that means it's a parent task so let's delete or future series
        future_tasks = get_future_childrens_of_parent_task(
            parent_task=parent_or_sibling_task
        )
    else:
        # it means it's a child task so let's delete its future siblings along with
        # itself too
        future_tasks = get_task_future_siblings(parent_or_sibling_task)

    deleted_ids = list(future_tasks.values_list("id", flat=True))
    deleted_count = future_tasks.delete()[0]

    logger.info(
        f"Deleted {deleted_count} future children/siblings for parent/child task id={parent_or_sibling_id}, ids={deleted_ids}"
    )

    # Regenerate if rule still present
    created_ids = []
    if parent_or_sibling_task.recurrence_rule:
        # Regenerate occurrences only after cutoff date
        _gen_rec_tasks_for_parent_or_sibling(parent_or_sibling_task)
        if parent_or_sibling_task.is_rec_task_parent:
            # it means it's a parent task so get all of it's future childrens
            future_tasks = get_future_childrens_of_parent_task(
                parent_task=parent_or_sibling_task
            )
        else:
            # since it's a sibling, we need to filter with parent
            future_tasks = get_task_future_siblings(parent_or_sibling_task)

        created_ids = future_tasks.values_list("id", flat=True)
        logger.info(
            f"Generated {future_tasks.count()} new children for parent_id={parent_or_sibling_id}, ids={created_ids}"
        )
    _notify_frontend(
        f"tasks_user_{parent_or_sibling_task.user.pk}",
        {
            "type": "refresh_for_rec_task",
            "deleted": deleted_ids,
            "created": TaskSerializer(future_tasks, many=True).data,
        },
    )
    return f"created task IDs: {created_ids}, deleted Tasks IDs: {deleted_ids}"


@app.task(name="generate_recurring_tasks")
def generate_recurring_sibling_tasks():
    """
    Runs every 12 hours.  For each "template" task (recurrence_rule set,
    recurrence_parent is null), parse the rule, find the next up-to-5
    occurrences after now (that haven't already been cloned), and create them.
    """
    logger.info("Starting generate_recurring_tasks task")

    latest_task_ids = (
        Task.objects.filter(
            recurrence_parent=OuterRef("recurrence_parent"),
            column_date__gte=timezone.now(),
            status=Task.ON_BOARD,
        )
        .order_by("-column_date")
        .values("id")[:1]
    )

    templates_tasks = (
        Task.objects.filter(
            recurrence_rule__isnull=False,  # has a recurrence rule
            recurrence_parent__isnull=False,
            id__in=Subquery(latest_task_ids),
        )
        .order_by("-column_date")
        .distinct("recurrence_parent")
    )

    results = []
    for sibling_task in templates_tasks:
        results.append(_gen_rec_tasks_for_parent_or_sibling(sibling_task, days_ahead=5))
    return f"Generated recurring tasks results array containing data of every rec task -> : {results}"


@app.task(name="archive_old_tasks")
def archive_old_tasks():
    """
    Archives tasks that haven't been updated in 30 days.
    This task runs daily at midnight.
    """
    logger.info("Starting archive_old_tasks task")

    # Calculate the date 30 days ago
    thirty_days_ago = timezone.now() - datetime.timedelta(days=30)

    # Find tasks that haven't been updated in 30 days and aren't already archived
    old_tasks = Task.objects.filter(
        updated_at__lt=thirty_days_ago,
    ).exclude(status=Task.ARCHIVED)

    count = 0
    for task in old_tasks:
        task.status = Task.ARCHIVED
        task.save(update_fields=["status"])
        count += 1

    logger.info(f"Archived {count} old tasks")
    return f"Archived {count} old tasks"


@app.task(name="move_old_tasks_to_backlogs")
def move_old_tasks_to_backlogs():
    """
    Moves tasks that haven't been updated in 15 days to the backlogs.
    This task runs daily at midnight.
    """
    logger.info("Starting move_old_tasks_to_backlogs task")

    # Calculate the date 15 days ago
    fifteen_days_ago = timezone.now() - datetime.timedelta(days=15)

    # Find tasks that haven't been updated in 15 days and aren't already archived
    old_tasks = Task.objects.filter(
        updated_at__lt=fifteen_days_ago,
        is_completed=False,
    ).exclude(status=Task.ARCHIVED)

    count = 0
    for task in old_tasks:
        task.status = Task.BACKLOG
        task.save(update_fields=["status"])
        count += 1

    logger.info(f"Moved {count} old tasks to backlogs")
    return f"Moved {count} old tasks to backlogs"


@app.task(name="move_yesterday_task_to_today")
def move_yesterday_task_to_today():
    """
    Move yesterday's tasks to today's date using each user's timezone.
    """
    logger.info("Starting move_yesterday_task_to_today task")
    User = get_user_model()
    total_moved = 0

    # Iterate through all users and adjust based on their local midnight
    for user in User.objects.all():
        now_local = timezone.now().astimezone(user.timezone)  # type:ignore
        yesterday_date = (now_local - datetime.timedelta(days=1)).date()

        old_tasks = Task.objects.filter(
            user=user,
            status=Task.ON_BOARD,
            is_completed=False,
            column_date__date=yesterday_date,
            recurrence_rule__isnull=True,  # isn't a recurring task
        ).exclude(status=Task.ARCHIVED)

        moved = 0
        for task in old_tasks:
            task.column_date = now_local
            task.save(update_fields=["column_date"])
            moved += 1

        if moved:
            logger.info(
                f"Moved {moved} tasks for user_id={user.pk} for date={yesterday_date}"
            )
        total_moved += moved

    logger.info(f"Total moved tasks: {total_moved}")
    return f"Moved {total_moved} tasks across all users"
