from rest_framework import serializers
from .models import Task, Project
from taggit.serializers import (TagListSerializerField,
                                TaggitSerializer)


class TaskSerializer(TaggitSerializer, serializers.ModelSerializer):
    tags = TagListSerializerField()
    duration = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = '__all__'

    def get_duration(self, obj):
        return obj.get_duration_display



class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'
