from django.contrib import admin
from .models import GitHubCredentials, GitHubSettings


@admin.register(GitHubCredentials)
class GitHubCredentialsAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "github_username",
        "github_user_id",
        "connected_at",
        "updated_at",
    ]
    search_fields = ["user__email", "github_username"]
    list_filter = ["connected_at", "updated_at"]
    readonly_fields = [
        "connected_at",
        "updated_at",
        "access_token",
    ]  # Don't show token in admin


@admin.register(GitHubSettings)
class GitHubSettingsAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "sync_enabled",
        "sync_only_assigned",
        "sync_only_open",
        "last_sync",
    ]
    search_fields = ["user__email"]
    list_filter = ["sync_enabled", "sync_only_assigned", "sync_only_open", "last_sync"]
    readonly_fields = ["last_sync"]
