from django.db import models
from django.conf import settings
import requests
import logging

logger = logging.getLogger(__name__)


class GitHubCredentials(models.Model):
    """
    Model to store GitHub OAuth2 credentials for users.
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="github_credentials",
    )
    access_token = models.CharField(max_length=255, help_text="GitHub access token")
    token_type = models.CharField(max_length=50, default="bearer")
    scope = models.TextField(blank=True, null=True, help_text="Granted scopes")
    github_username = models.CharField(max_length=100, blank=True, null=True)
    github_user_id = models.BigIntegerField(blank=True, null=True)
    connected_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "GitHub Credentials"
        verbose_name_plural = "GitHub Credentials"

    def __str__(self):
        return f"{self.user.email}'s GitHub Creds"

    def get_auth_headers(self):
        """Get authorization headers for GitHub API calls."""
        return {
            "Authorization": f"token {self.access_token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "Focus-Timer-App",
        }

    def test_token_validity(self):
        """Test if the stored token is still valid."""
        try:
            response = requests.get(
                "https://api.github.com/user",
                headers=self.get_auth_headers(),
                timeout=10,
            )
            if response.status_code == 200:
                user_data = response.json()
                # Update user info if needed
                if not self.github_username or not self.github_user_id:
                    self.github_username = user_data.get("login")
                    self.github_user_id = user_data.get("id")
                    self.save(update_fields=["github_username", "github_user_id"])
                return True
            elif response.status_code == 401:
                logger.warning(f"GitHub token invalid for user {self.user.id}")
                return False
            else:
                logger.error(
                    f"GitHub API error {response.status_code}: {response.text}"
                )
                return False
        except requests.RequestException as e:
            logger.error(f"GitHub API request failed: {str(e)}")
            return False


class GitHubSettings(models.Model):
    """
    Model to store GitHub-specific settings for users.
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="github_settings",
    )
    sync_enabled = models.BooleanField(default=True)
    sync_repositories = models.JSONField(
        default=list, help_text="List of repository IDs to sync issues from"
    )
    last_sync = models.DateTimeField(null=True, blank=True)
    sync_only_assigned = models.BooleanField(
        default=True, help_text="Only sync issues assigned to the user"
    )
    sync_only_open = models.BooleanField(
        default=True, help_text="Only sync open issues"
    )

    class Meta:
        verbose_name = "GitHub Settings"
        verbose_name_plural = "GitHub Settings"

    def __str__(self):
        return f"{self.user.email}'s GitHub Settings"

    @classmethod
    def get_or_create_for_user(cls, user):
        """Get or create GitHub settings for a user with default values."""
        settings, _ = cls.objects.get_or_create(
            user=user,
            defaults={
                "sync_enabled": True,
                "sync_repositories": [],
                "sync_only_assigned": True,
                "sync_only_open": True,
            },
        )
        return settings
