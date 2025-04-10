from django.urls import path
from .views import TasksApiView, TaskApiView, toggle_task_completion, get_all_projects, get_all_tags, create_project


urlpatterns = [
    path('api/tasks/', TasksApiView.as_view(), name='task_list'),
    path('api/tasks/<int:pk>/', TaskApiView.as_view(), name='task_detail'),
    path('api/tasks/<int:pk>/toggle_completion/', toggle_task_completion, name='toggle_task_completion'),
    path('api/projects/', get_all_projects, name='project_list'),
    path('api/projects/create/', create_project, name='create_project'),
    path('api/tags/', get_all_tags, name='tag_list'),
]
