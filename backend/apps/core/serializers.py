from rest_framework import serializers
from .models import Task
from taggit.serializers import (TagListSerializerField,
                                TaggitSerializer)


class TaskSerializer(TaggitSerializer, serializers.ModelSerializer):
    tags = TagListSerializerField()

    class Meta:
        model = Task
        fields = '__all__'
