from rest_framework import serializers
from .models import Task, Project
from taggit.serializers import (TagListSerializerField,
                                TaggitSerializer)
from dateutil.rrule import rrulestr
from datetime import timedelta



class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'


class TaskSerializer(TaggitSerializer, serializers.ModelSerializer):
    tags = TagListSerializerField()
    duration_display = serializers.SerializerMethodField()
    project = ProjectSerializer(read_only=True)

    class Meta:
        model = Task
        fields = '__all__'

    def get_duration_display(self, obj):
        return obj.get_duration_display

    def validate_recurrence_rule(self, value):
        if not value:
            return value
        try:
            # test‑parse the string
            rrulestr(value)
            print(f"value {value} is valid rrule")
        except Exception as e:
            print(e)
            raise serializers.ValidationError(f"Invalid RRULE: {e}")
        return value

    def save(self, **kwargs):
        task = super().save(**kwargs)
        if task.start_at and not task.end_at:
            # calculate end at based on duration
            if not task.duration:
                task.duration = timedelta(minutes=30)
            task.end_at = task.start_at + task.duration
            task.save()
        return task

