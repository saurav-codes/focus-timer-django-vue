from django.urls import path
from .views import (
    get_all_projects,
    get_all_tags,
    create_project,
    ProjectDetailApiView,
    assign_project_to_task,
    update_task_duration,
)

app_name = "core"

urlpatterns = [
    path(
        "update_task_duration/",
        update_task_duration,
        name="update_task_duration",
    ),
    path(
        "assign_project/<int:task_id>/<int:project_id>/",
        assign_project_to_task,
        name="assign_project_to_task",
    ),
    path("projects/", get_all_projects, name="project_list"),
    path("projects/<int:pk>/", ProjectDetailApiView.as_view(), name="project_detail"),
    path("projects/create/", create_project, name="create_project"),
    path("tags/", get_all_tags, name="tag_list"),
]
