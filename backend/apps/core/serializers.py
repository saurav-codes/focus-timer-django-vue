from rest_framework import serializers
from .models import Task, Project, RecurrenceSeries
from taggit.serializers import TagListSerializerField, TaggitSerializer
from drf_writable_nested.serializers import WritableNestedModelSerializer
from dateutil.rrule import rrulestr
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)


class RecurrenceSeriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecurrenceSeries
        fields = ["id", "recurrence_rule"]

    def validate_recurrence_rule(self, value):
        if value:
            try:
                rrulestr(value)
                logger.info(f"Valid recurrence rule: rule={value}")
            except Exception as e:
                logger.error(f"Invalid recurrence rule '{value}': {e}")
                raise serializers.ValidationError(f"Invalid RRULE: {e}")
        return value


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


class TaskSerializer(TaggitSerializer, WritableNestedModelSerializer):
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
    recurrence_series = RecurrenceSeriesSerializer(required=False, allow_null=True)

    class Meta:
        model = Task
        fields = [
            "id",
            "frontend_id",
            "title",
            "description",
            "order",
            "is_completed",
            "status",
            "created_at",
            "updated_at",
            "duration",
            "column_date",
            "start_at",
            "end_at",
            "tags",
            "duration_display",
            "project",
            "project_id",
            "user",
            "recurrence_series",
        ]
        read_only_fields = ["user"]

    def get_duration_display(self, obj):
        return obj.get_duration_display

    def create(self, validated_data):
        # assign user from request.user while creating a task
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data.pop("user", None)
        return super().update(instance, validated_data)

    def validate(self, attrs):
        validated_data = super().validate(attrs)
        start_at = validated_data.get("start_at")
        end_at = validated_data.get("end_at")
        if start_at and not end_at:
            # calculate end at based on duration
            if not validated_data["duration"]:
                validated_data["duration"] = timedelta(minutes=30)
            validated_data["end_at"] = start_at + validated_data["duration"]
        elif start_at and end_at:
            # make sure both are in UTC timezones
            if start_at < end_at:
                validated_data["duration"] = end_at - start_at
            else:
                validated_data["duration"] = timedelta(minutes=30)
                validated_data["end_at"] = None
        return validated_data


class TaskDurationUpdateSerializer(serializers.Serializer):
    duration = serializers.DurationField()
