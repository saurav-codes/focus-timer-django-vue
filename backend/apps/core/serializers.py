from rest_framework import serializers
from .models import Task

class TaskSerializer(serializers.ModelSerializer):
    # timezone = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = '__all__'

    # def get_timezone(self, obj):
    #     if obj.timezone:
    #         return obj.timezone.key
    #     return None

    # def save(self, **kwargs):
    #     start_at = self.validated_data.get('start_at')
    #     if start_at:
    #         self.validated_data["timezone"] = start_at.tzname()
    #     return super().save(**kwargs)
