from django.urls import path
from . import views

app_name = "gmail"

urlpatterns = [
    path("status/", views.check_gmail_connection, name="check_google_connection"),
]
