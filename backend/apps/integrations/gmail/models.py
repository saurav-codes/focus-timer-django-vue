from django.db import models
from django.conf import settings


class GmailSettings(models.Model):
    """
    Model to store Gmail-specific settings for users.
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="gmail_settings",
    )
    sync_enabled = models.BooleanField(default=True)
    sync_labels = models.JSONField(
        default=list, help_text="List of Gmail labels to sync"
    )
    last_sync = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Gmail Settings"
        verbose_name_plural = "Gmail Settings"

    def __str__(self):
        return f"{self.user.email}'s Gmail Settings"

    @classmethod
    def get_or_create_for_user(cls, user):
        """Get or create Gmail settings for a user with default values."""
        settings, _ = cls.objects.get_or_create(
            user=user,
            defaults={"sync_enabled": True, "sync_labels": ["INBOX", "IMPORTANT"]},
        )
        return settings
