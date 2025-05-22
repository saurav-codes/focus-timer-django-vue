from django.db import models
from django.conf import settings
from django.utils import timezone
import datetime
from google.auth.transport.requests import Request as GoogleRequest
from .utils import credentials_from_dict
from google.auth.exceptions import RefreshError


class GoogleCalendarCredentials(models.Model):
    """
    Model to store Google Calendar OAuth2 credentials for users.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='google_calendar_credentials'
    )
    token = models.JSONField(
        help_text="OAuth2 token and refresh token information"
    )
    calendar_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Primary Google Calendar ID"
    )
    connected_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Google Calendar Credentials"
        verbose_name_plural = "Google Calendar Credentials"

    def __str__(self):
        return f"{self.user.email}'s Google Calendar"

    @property
    def is_expired(self):
        """Check if the access token is expired."""
        try:
            expiry = self.token.get('expiry', None)
            if not expiry:
                return True

            # Convert expiry to datetime
            expiry_datetime = datetime.datetime.fromisoformat(expiry.replace('Z', '+00:00'))

            # get current time in UTC
            datetime_now = timezone.now().replace(tzinfo=None)
            # Add a buffer of 5 minutes
            return expiry_datetime <= datetime_now + datetime.timedelta(minutes=-5)
        except (ValueError, AttributeError):
            # If there's any error parsing the expiry, consider it expired
            return True

    @property
    def access_token(self):
        """Get the access token."""
        return self.token.get('token', '')

    @property
    def refresh_token(self):
        """Get the refresh token."""
        return self.token.get('refresh_token', '')

    def update_token(self, token_data):
        """
        Update the token with new token data.

        Args:
            token_data (dict): New token data from OAuth2 flow
        """
        # If the new token doesn't have a refresh token but we have one stored,
        # make sure we keep it
        if 'refresh_token' not in token_data and 'refresh_token' in self.token:
            token_data['refresh_token'] = self.token['refresh_token']

        self.token = token_data
        self.save(update_fields=['token', 'updated_at'])

    def get_credentials(self):
        credentials = credentials_from_dict(self.token)

        # Check if the credentials are expired and try to refresh
        if self.is_expired:
            if not credentials.refresh_token:
                self.delete()
                return {
                    'error': 'Refresh token missing. Please reconnect your Google Calendar.',
                }
            try:
                credentials.refresh(request=GoogleRequest())
            except RefreshError:
                self.delete()
                return {
                    'error': 'Google Calendar authentication expired. Please reconnect.',
                }
            # Update the stored token
            token_data = {
                'token': credentials.token,
                'refresh_token': credentials.refresh_token,
                'token_uri': credentials.token_uri,
                'client_id': credentials.client_id,
                'client_secret': credentials.client_secret,
                'scopes': credentials.scopes,
                'expiry': credentials.expiry.isoformat() if credentials.expiry else None
            }
            self.token = token_data
            self.save(update_fields=['token'])
        return credentials
