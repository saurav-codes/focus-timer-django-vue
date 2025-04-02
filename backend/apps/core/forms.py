from taggit.serializers import (TagListSerializerField,
                                TaggitSerializer)
from .models import Task
from rest_framework import serializers


class TaskSerializer(TaggitSerializer, serializers.ModelSerializer):

    tags = TagListSerializerField()

    class Meta:
        model = Task
        fields = '__all__'