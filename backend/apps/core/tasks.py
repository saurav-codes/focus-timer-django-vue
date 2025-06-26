import logging
from django.utils import timezone
from backend.celery import app
from .models import Task, RecurrenceSeries
import datetime
from django.contrib.auth import get_user_model
from dateutil.rrule import rrulestr
from .selectors import get_future_siblings, get_latest_task_of_series
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .serializers import TaskSerializer

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Helper functions to be used by main tasks
# ---------------------------------------------------------------------------
def _gen_rec_tasks_for_parent_or_sibling(
    parent_or_sibling_task: Task,
    max_events: int = 20,
    days_ahead: int = 20,
):
    rec_rule = ""
    if parent_or_sibling_task.recurrence_series:
        if parent_or_sibling_task.recurrence_series.recurrence_rule:
            rec_rule = parent_or_sibling_task.recurrence_series.recurrence_rule
    else:
        raise ValueError("Task must have a recurrence_rule to generate future siblings")

    # Ensure we're working with datetime objects for the dateutil rrule
    start_date = (
        parent_or_sibling_task.column_date
        or timezone.now().date() + datetime.timedelta(days=1)
    )
    # Convert date to datetime at midnight for comparison
    start_after = datetime.datetime.combine(start_date, datetime.time.min)
    window_end = start_after + datetime.timedelta(days=days_ahead)

    try:
        rule = rrulestr(rec_rule, dtstart=start_after)
    except Exception as e:
        result = f"Error parsing recurrence rule for parent_task_id={parent_or_sibling_task.pk}: {e}"
        logger.error(result)
        return result

    # Convert the occurrences to dates since we're working with date fields
    occurrences = [
        dt.date() if isinstance(dt, datetime.datetime) else dt
        for dt in rule.between(after=start_after, before=window_end, inc=True)
    ][:max_events]
    if not occurrences:
        result = (
            f"No upcoming recurrence for parent_task_id={parent_or_sibling_task.pk}"
        )
        logger.info(result)
        return result

    from .services import generate_rec_tasks_for_parent

    return generate_rec_tasks_for_parent(parent_or_sibling_task, occurrences)


# ---------------------------------------------------------------------------
# Celery Tasks to invoke using .delay
# ---------------------------------------------------------------------------
@app.task(name="notify_frontend")
def notify_frontend(group_name, data):
    # ------------------- Notify connected client(s) --------------------------------------
    try:
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(group_name, data)  # type:ignore
    except Exception as e:
        logger.error(f"Failed to send refresh_tasks event: {e}", exc_info=True)


@app.task(name="regenerate_recurring_series")
def regenerate_recurring_series(task_id: int | str):
    """
    Delete all *future* siblings/children of a parent recurring task and rebuild them.

    Called when the user edits a single child or a parent and we propagate changes to the
    parent template or to childrens by deleting all childrens & recreating based on updated fields
    Past instances (start_at <= now) remain untouched.
    """
    try:
        task: Task = Task.objects.get(id=task_id)
        if not task.recurrence_series:
            error = f"Task with id {task.pk} isn't a recurring task.\
                this could be an issue why a non rec task being passed\
                to celery. so dig this issue"
            logger.error(error, exc_info=True)
            return error
    except Task.DoesNotExist:
        logger.warning(f"Parent/Sibling task not found for regeneration: id={task_id}")
        return "parent-missing"

    future_tasks_to_del = get_future_siblings(task)
    deleted_ids = list(future_tasks_to_del.values_list("id", flat=True))
    deleted_count, _ = future_tasks_to_del.delete()

    logger.info(
        f"Deleted {deleted_count} future children/siblings for parent/child task id={task_id}, ids={deleted_ids}"
    )

    # Regenerate if rule still present
    created_ids = []
    tasks = Task.objects.none()
    if task.recurrence_series.recurrence_rule:
        # Regenerate occurrences only after cutoff date
        _gen_rec_tasks_for_parent_or_sibling(task)
        tasks = tasks.union(get_future_siblings(task))
        created_ids = tasks.values_list("id", flat=True)
        logger.info(
            f"Generated {tasks.count()} new children for parent_id={task_id}, ids={created_ids}"
        )

    notify_frontend.delay(  # type: ignore
        f"tasks_user_{task.user.pk}",
        {
            "type": "refresh_for_rec_task",
            "deleted": deleted_ids,
            "created": TaskSerializer(tasks, many=True).data,
        },
    )
    return f"created task IDs: {created_ids}, deleted Tasks IDs: {deleted_ids}"


# ---------------------------------------------------------------------------
# Periodic Celery Tasks to invoke using scheduler ( schedule from admin panel )
# ---------------------------------------------------------------------------
@app.task(name="generate_recurring_sibling_tasks_periodic")
def generate_recurring_sibling_tasks_periodic():
    """
    Runs every 12 hours in low priority Queue
    """
    logger.info("generate_recurring_sibling_tasks_periodic: Starting task gen")
    all_series = RecurrenceSeries.objects.all()
    for series in all_series:
        latest_task = get_latest_task_of_series(series)
        if latest_task:
            logger.info(
                f"regenerating task based on \
                latest task: {latest_task.pk} of\
                series: {series.pk} & user_id: {latest_task.user.pk}"
            )
            regenerate_recurring_series(latest_task.pk)
    return "generate_recurring_sibling_tasks_periodic: task gen completed"


@app.task(name="archive_old_tasks_periodic")
def archive_old_tasks_periodic():
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


@app.task(name="move_old_tasks_to_backlogs_periodic")
def move_old_tasks_to_backlogs_periodic():
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


@app.task(name="move_yesterday_task_to_today_periodic")
def move_yesterday_task_to_today_periodic():
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
            column_date=yesterday_date,
            recurrence_series__isnull=True,  # isn't a recurring task
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
        notify_frontend.delay(  # type: ignore
            f"tasks_user_{user.pk}",
            {
                "type": "full_refresh",
            },
        )

    logger.info(f"Total moved tasks: {total_moved}")

    return f"Moved {total_moved} tasks across all users"
