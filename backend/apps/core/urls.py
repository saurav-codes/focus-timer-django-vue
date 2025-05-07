from django.urls import path
from .views import (
    TasksApiView,
    TaskApiView,
    toggle_task_completion,
    get_all_projects,
    get_all_tags,
    create_project,
    ProjectDetailApiView,
)

app_name = 'core'

urlpatterns = [
    path('tasks/', TasksApiView.as_view(), name='task_list'),
    path('tasks/<int:pk>/', TaskApiView.as_view(), name='task_detail'),
    path('tasks/<int:pk>/toggle_completion/', toggle_task_completion, name='toggle_task_completion'),
    path('projects/', get_all_projects, name='project_list'),
    path('projects/<int:pk>/', ProjectDetailApiView.as_view(), name='project_detail'),
    path('projects/create/', create_project, name='create_project'),
    path('tags/', get_all_tags, name='tag_list'),
]
