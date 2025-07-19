from django.urls import path
from . import views

app_name = "github"

urlpatterns = [
    path("status/", views.check_github_connection, name="check_github_connection"),
    path("auth/start/", views.start_github_auth, name="start_github_auth"),
    path("auth/callback/", views.github_auth_callback, name="github_auth_callback"),
    path("disconnect/", views.disconnect_github, name="disconnect_github"),
    path("repositories/", views.get_repositories, name="get_repositories"),
    path("issues/", views.get_github_issues, name="get_github_issues"),
    path(
        "issues/<str:issue_id>/",
        views.get_issue_details,
        name="get_issue_details",
    ),
    path(
        "issues/<str:issue_id>/convert-to-task/",
        views.convert_issue_to_task,
        name="convert_issue_to_task",
    ),
    path("settings/", views.github_settings, name="github_settings"),
]
