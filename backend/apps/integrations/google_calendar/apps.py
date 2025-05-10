from django.apps import AppConfig

class GoogleCalendarConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.integrations.google_calendar'
    verbose_name = 'Google Calendar Integration'
