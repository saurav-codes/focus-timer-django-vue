from django_filters import rest_framework as filters
from .models import Task, Project
from taggit.models import Tag
from django.db.models import Q

# Exported for reuse in other modules (e.g., selectors, docs)
TASK_FILTER_FIELDS: list[str] = [
    "project",
    "projects",
    "tags",
    "start_date",
    "end_date",
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
    start_date = filters.DateFilter(method="filter_start_date")
    end_date = filters.DateFilter(method="filter_end_date")

    class Meta:
        model = Task
        # Re-use the shared constant so changes remain DRY
        fields = TASK_FILTER_FIELDS

    def filter_start_date(self, queryset, name, value):
        return queryset.filter(
            Q(column_date__date__gte=value) | Q(column_date__isnull=True)
        )

    def filter_end_date(self, queryset, name, value):
        return queryset.filter(
            Q(column_date__date__lte=value) | Q(column_date__isnull=True)
        )
