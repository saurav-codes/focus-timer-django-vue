import logging
from channels.db import database_sync_to_async
from .models import Task, RecurrenceSeries
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


def get_future_siblings(task: Task) -> QuerySet[Task]:
    return Task.objects.filter(
        recurrence_series=task.recurrence_series,
        start_at__gte=task.start_at or timezone.now().date(),
    ).exclude(id=task.pk)


def get_past_siblings(task: Task) -> QuerySet[Task]:
    return Task.objects.filter(
        recurrence_series=task.recurrence_series,
        start_at__lte=task.start_at or timezone.now().date(),
    ).exclude(id=task.pk)


def get_all_task_from_series(series: RecurrenceSeries) -> QuerySet[Task]:
    return Task.objects.filter(recurrence_series=series)


def get_latest_task_of_series(series: RecurrenceSeries) -> Task | None:
    return get_all_task_from_series(series).order_by("-start_at").first()
