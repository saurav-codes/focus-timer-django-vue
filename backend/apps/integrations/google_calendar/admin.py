from django.contrib import admin
from .models import GoogleCalendarCredentials


@admin.register(GoogleCalendarCredentials)
class GoogleCalendarCredentialsAdmin(admin.ModelAdmin):
    list_display = ("user", "calendar_id", "connected_at", "updated_at", "is_expired")
    search_fields = ("user__email", "calendar_id")
    readonly_fields = ("connected_at", "updated_at", "is_expired")

    def is_expired(self, obj):
        return obj.is_expired

    is_expired.boolean = True
    is_expired.short_description = "Token Expired"
