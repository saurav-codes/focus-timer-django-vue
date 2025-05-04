from django.utils import timezone
from backend.celery import app
from dateutil.rrule import rrulestr
from .models import Task
import datetime
from django.db import transaction


def _generate_rec_tasks_for_parent(parent_task:Task, occurences_dates:list[datetime.datetime]):
    for occurence_date in occurences_dates:
        with transaction.atomic():
            child, created = Task.objects.update_or_create(
                user=parent_task.user,
                title=parent_task.title,
                description=parent_task.description,
                order=parent_task.order,
                is_completed=False,
                planned_duration=parent_task.planned_duration,
                column_date=occurence_date,
                start_at=occurence_date,
                end_at=parent_task.end_at,
                recurrence_rule=parent_task.recurrence_rule,
                recurrence_parent=parent_task,
                project=parent_task.project,
            )
            if created:
                # copy over tags
                child.tags.set(parent_task.tags.all())

        action = "created" if created else "updated"
        print(f"{action} task: {child.title} for date: {occurence_date}")


def gen_rec_tasks_for_parent(parent_task:Task):
    # every rec task ( wether parent or child ) have a task.start_at
    if not parent_task.start_at:
        print("No start_at date for task so adding current date")
        parent_task.start_at = timezone.now()
        parent_task.save()

    try:
        rule = rrulestr(parent_task.recurrence_rule, dtstart=parent_task.start_at)
    except Exception as e:
        print(f"Error parsing rule for task {parent_task.title}: {e}")
        return

    last_task_date = timezone.now()
    nxt_task_date = rule.after(last_task_date, inc=False)

    if nxt_task_date:
        _generate_rec_tasks_for_parent(parent_task, [nxt_task_date])
    else:
        print(f"No dates to create for task {parent_task.title}")


@app.task(name="generate_recurring_tasks")
def generate_recurring_tasks():
    """
    Runs every 12 hours.  For each "template" task (recurrence_rule set,
    recurrence_parent is null), parse the rule, find the next up-to-5
    occurrences after now (that haven't already been cloned), and create them.
    """
    print("Generating recurring tasks...")

    # 1) Grab only the *original* recurring tasks (no parents, with an RRULE)
    templates_tasks = Task.objects.filter(
        recurrence_rule__isnull=False,
        recurrence_parent__isnull=True,
    )

    for parent in templates_tasks:
        gen_rec_tasks_for_parent(parent)
    return "done"
