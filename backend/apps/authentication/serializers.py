from rest_framework import serializers
from .models import User
from timezone_field.rest_framework import TimeZoneSerializerField


class UserSerializer(serializers.ModelSerializer):
    timezone = TimeZoneSerializerField(use_pytz=True)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "timezone",
        ]
