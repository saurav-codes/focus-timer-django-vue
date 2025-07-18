from django.urls import path
from . import views

app_name = "gmail"

urlpatterns = [
    path("status/", views.check_gmail_connection, name="check_gmail_connection"),
    path("emails/", views.get_gmail_emails, name="get_gmail_emails"),
    path(
        "emails/<str:email_id>/star/", views.toggle_email_star, name="toggle_email_star"
    ),
    path("emails/<str:email_id>/read/", views.mark_email_read, name="mark_email_read"),
    path(
        "emails/<str:email_id>/convert-to-task/",
        views.convert_email_to_task,
        name="convert_email_to_task",
    ),
    path("labels/", views.get_gmail_labels_view, name="get_gmail_labels"),
    path("settings/", views.gmail_settings, name="gmail_settings"),
]
