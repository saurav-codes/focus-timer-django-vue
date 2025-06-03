from rest_framework import serializers
from .models import Task, Project
from taggit.serializers import TagListSerializerField, TaggitSerializer
from dateutil.rrule import rrulestr
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)


class ProjectSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Project
        fields = "__all__"
        read_only_fields = ["user"]

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data.pop("user", None)
        return super().update(instance, validated_data)


class TaskSerializer(TaggitSerializer, serializers.ModelSerializer):
    tags = TagListSerializerField()
    duration_display = serializers.SerializerMethodField()
    project = ProjectSerializer(read_only=True)
    project_id = serializers.PrimaryKeyRelatedField(
        queryset=Project.objects.all(),
        source="project",
        write_only=True,
        required=False,
    )
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Task
        fields = "__all__"
        read_only_fields = ["user"]

    def get_duration_display(self, obj):
        return obj.get_duration_display

    def validate_recurrence_rule(self, value):
        if value:
            try:
                rrulestr(value)
                logger.info(f"Valid recurrence rule: rule={value}")
            except Exception as e:
                logger.error(f"Invalid recurrence rule '{value}': {e}")
                raise serializers.ValidationError(f"Invalid RRULE: {e}")
        return value

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data.pop("user", None)
        return super().update(instance, validated_data)

    def save(self, **kwargs):
        task = super().save(**kwargs)
        if task.start_at and not task.end_at:
            # calculate end at based on duration
            if not task.duration:
                task.duration = timedelta(minutes=30)
            task.end_at = task.start_at + task.duration
            task.save()
        return task
