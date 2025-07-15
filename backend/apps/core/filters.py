from django_filters import rest_framework as filters
from .models import Task, Project
from taggit.models import Tag


# Exported for reuse in other modules (e.g., selectors, docs)
TASK_FILTER_FIELDS: list[str] = [
    "project",
    "projects",
    "tags",
    "start_at",
]


class TaskFilter(filters.FilterSet):
    project = filters.ModelChoiceFilter(queryset=Project.objects.all())
    # allow filtering by multiple projects
    projects = filters.ModelMultipleChoiceFilter(
        field_name="project__id", to_field_name="id", queryset=Project.objects.all()
    )
    tags = filters.ModelMultipleChoiceFilter(
        field_name="tags__name", to_field_name="name", queryset=Tag.objects.all()
    )
    start_at = filters.IsoDateTimeFromToRangeFilter(field_name="start_at")

    class Meta:
        model = Task
        fields = TASK_FILTER_FIELDS
