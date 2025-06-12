from rest_framework import serializers
from .models import User
from timezone_field.rest_framework import TimeZoneSerializerField


class UserSerializer(serializers.ModelSerializer):
    timezone = TimeZoneSerializerField(use_pytz=True)
    # Expose computed full name
    # Allow reading and writing full_name: will be combined and split
    full_name = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = [
            "id",
            # "username" removed
            "email",
            "first_name",
            "last_name",
            "full_name",
            "timezone",
        ]

    def to_representation(self, instance):
        # Combine first_name and last_name into full_name for output
        data = super().to_representation(instance)
        first = data.get("first_name", "") or ""
        last = data.get("last_name", "") or ""
        data["full_name"] = f"{first} {last}".strip()
        return data

    def update(self, instance, validated_data):
        # Allow updating full_name: split it into first_name and last_name
        full = validated_data.pop("full_name", None)
        if full is not None:
            parts = full.strip().split(" ", 1)
            validated_data["first_name"] = parts[0]
            validated_data["last_name"] = parts[1] if len(parts) > 1 else ""
        return super().update(instance, validated_data)
