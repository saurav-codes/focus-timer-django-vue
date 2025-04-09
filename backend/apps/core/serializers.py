from rest_framework import serializers
from .models import Task, Project
from taggit.serializers import (TagListSerializerField,
                                TaggitSerializer)


class TaskSerializer(TaggitSerializer, serializers.ModelSerializer):
    tags = TagListSerializerField()
    planned_duration_display = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = '__all__'

    def get_planned_duration_display(self, obj):
        return obj.get_planned_duration_display



class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'
