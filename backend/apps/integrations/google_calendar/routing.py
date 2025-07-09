"""WebSocket routing for Google-Calendar consumer."""

from django.urls import path
from .consumers import GoogleCalendarConsumer

websocket_urlpatterns = [
    path("ws/gcal/", GoogleCalendarConsumer.as_asgi()),
]
