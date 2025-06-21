import logging
from channels.db import database_sync_to_async
from .models import Task
from .filters import TaskFilter, TASK_FILTER_FIELDS
from .serializers import TaskSerializer
from django.db.models.query import QuerySet
from django.utils import timezone

logger = logging.getLogger(__name__)


@database_sync_to_async
def get_filtered_tasks_for_user_serialized(user_id: int | str, filters: dict):
    """Synchronous method to fetch and filter tasks"""
    tasks = Task.objects.filter(user_id=user_id)
    filterset = TaskFilter(filters, queryset=tasks)

    if filterset.is_valid():
        tasks = filterset.qs
        logger.info(f"Found {tasks.count()} tasks for user_id={user_id}")
        return TaskSerializer(tasks, many=True).data

    # Extract structured error information to avoid HTML in messages
    error_dict = filterset.errors.get_json_data()

    logger.warning(
        f"TaskFilter invalid for user_id={user_id}, "
        f"errors={error_dict}, filters={filters}"
    )
    # Prepare detailed error with valid filter keys and an example structure
    valid_filters = TASK_FILTER_FIELDS
    example_filters = {field: "<value>" for field in valid_filters}
    raise ValueError(
        "Invalid filters provided. "
        f"Errors: {error_dict}. "
        f"Valid filter keys are: {valid_filters}. "
        f"Example: {example_filters}"
    )


def get_task_future_siblings(child_task: Task) -> QuerySet[Task]:
    """Return all future siblings for a given Task ( other than given task )"""
    parent_task = child_task.recurrence_parent
    if not parent_task:
        raise ValueError(
            "\
            `get_task_future_siblings` must be called with a sibling task arg"
        )
    return Task.objects.filter(
        recurrence_parent=parent_task,
        column_date__gt=child_task.column_date or timezone.now(),
    )


def get_future_childrens_of_parent_task(parent_task: Task):
    """
    Return all future childrens for a given Task ( other than given task )
    """
    if not parent_task.is_rec_task_parent:
        raise ValueError(
            "\
            `get_future_childrens_of_parent_task` must be called with a parent task arg"
        )
    return Task.objects.filter(
        recurrence_parent=parent_task,
        column_date__gt=parent_task.column_date or timezone.now(),
    )
