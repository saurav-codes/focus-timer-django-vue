import logging
from django.utils import timezone
from backend.celery import app
from dateutil.rrule import rrulestr
from .models import Task
import datetime
from django.db import transaction

logger = logging.getLogger(__name__)


def _generate_rec_tasks_for_parent(
    parent_task: Task, occurences_dates: list[datetime.datetime]
):
    for occurence_date in occurences_dates:
        with transaction.atomic():
            child, created = Task.objects.update_or_create(
                user=parent_task.user,
                title=parent_task.title,
                description=parent_task.description,
                order=parent_task.order,
                is_completed=False,
                duration=parent_task.duration,
                column_date=occurence_date,
                start_at=occurence_date,
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
        result = f"Recurring task {action}: parent_task_id={parent_task.id} child_task_id={child.id} date={occurence_date}"
        logger.info(result)
        return result
    return f"No new occurrences generated for parent_task_id={parent_task.id}, dates={occurences_dates}"


def gen_rec_tasks_for_parent(parent_task: Task):
    # every rec task ( wether parent or child ) have a task.start_at
    if not parent_task.start_at:
        logger.warning(
            f"No start_at for parent_task_id={parent_task.id}, setting to now"
        )
        parent_task.start_at = timezone.now()
        parent_task.save()

    try:
        rule = rrulestr(parent_task.recurrence_rule, dtstart=parent_task.start_at)
    except Exception as e:
        result = (
            f"Error parsing recurrence rule for parent_task_id={parent_task.id}: {e}"
        )
        logger.error(result)
        return result

    last_task_date = timezone.now()
    nxt_task_date = rule.after(last_task_date, inc=False)

    if nxt_task_date:
        return _generate_rec_tasks_for_parent(parent_task, [nxt_task_date])
    else:
        result = f"No upcoming recurrence for parent_task_id={parent_task.id}"
        logger.info(result)
        return result


@app.task(name="generate_recurring_tasks")
def generate_recurring_tasks():
    """
    Runs every 12 hours.  For each "template" task (recurrence_rule set,
    recurrence_parent is null), parse the rule, find the next up-to-5
    occurrences after now (that haven't already been cloned), and create them.
    """
    logger.info("Starting generate_recurring_tasks task")

    # 1) Grab only the *original* recurring tasks (no parents, with an RRULE)
    templates_tasks = Task.objects.filter(
        recurrence_rule__isnull=False,
        recurrence_parent__isnull=True,
    )

    results = []

    for parent in templates_tasks:
        results.append(gen_rec_tasks_for_parent(parent))
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
    Move yesterday's tasks to today's date.
    """
    logger.info("Starting move_yesterday_task_to_today task")

    # Calculate the date for yesterday
    yesterday = timezone.now() - datetime.timedelta(days=1)

    # Find tasks that were due yesterday and aren't already completed
    old_tasks = Task.objects.filter(
        status=Task.ON_BOARD,
        is_completed=False,
        column_date__date=yesterday.date(),
    ).exclude(status=Task.ARCHIVED)

    count = 0
    for task in old_tasks:
        task.column_date = timezone.now()
        task.save(update_fields=["column_date"])
        count += 1

    logger.info(f"Moved {count} old tasks to today's date")
    return f"Moved {count} old tasks to today's date"
