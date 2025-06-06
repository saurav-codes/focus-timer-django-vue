from django_filters import rest_framework as filters
from .models import Task, Project
from taggit.models import Tag
from django.db.models import Q


class TaskFilter(filters.FilterSet):
    project = filters.ModelChoiceFilter(queryset=Project.objects.all())
    tags = filters.ModelMultipleChoiceFilter(
        field_name="tags__name", to_field_name="name", queryset=Tag.objects.all()
    )
    start_date = filters.DateFilter(method="filter_start_date")
    end_date = filters.DateFilter(method="filter_end_date")

    class Meta:
        model = Task
        fields = ["project", "tags", "start_date", "end_date"]

    def filter_start_date(self, queryset, name, value):
        return queryset.filter(
            Q(column_date__date__gte=value) | Q(column_date__isnull=True)
        )

    def filter_end_date(self, queryset, name, value):
        return queryset.filter(
            Q(column_date__date__lte=value) | Q(column_date__isnull=True)
        )
