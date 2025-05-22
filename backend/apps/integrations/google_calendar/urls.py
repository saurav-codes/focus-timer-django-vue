from django.urls import path
from . import views

app_name = 'google_calendar'

urlpatterns = [
    path('status/', views.check_google_connection, name='check_google_connection'),
    path('auth/start/', views.start_google_auth, name='start_google_auth'),
    path('auth/callback/', views.google_auth_callback, name='google_auth_callback'),
    path('events/', views.get_calendar_events, name='get_calendar_events'),
    path('events/<str:event_id>/', views.update_calendar_event, name='update_calendar_event'),
    path('disconnect/', views.disconnect_google_calendar, name='disconnect_google_calendar'),
]
