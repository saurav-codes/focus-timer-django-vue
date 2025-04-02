from django.urls import path
from .views import TasksApiView, TaskApiView, toggle_task_completion


urlpatterns = [
    path('api/tasks/', TasksApiView.as_view(), name='task_list'),
    path('api/tasks/<int:pk>/', TaskApiView.as_view(), name='task_detail'),
    path('api/tasks/<int:pk>/toggle_completion/', toggle_task_completion, name='toggle_task_completion'),
]
