from django_filters import rest_framework as filters
from .models import Task, Project
from taggit.models import Tag

class TaskFilter(filters.FilterSet):
    project = filters.ModelChoiceFilter(queryset=Project.objects.all())
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__name',
        to_field_name='name',
        queryset=Tag.objects.all()
    )

    class Meta:
        model = Task
        fields = ['project', 'tags']