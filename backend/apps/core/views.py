from django.shortcuts import get_object_or_404
from .models import Task, Project
from .serializers import TaskSerializer, ProjectSerializer
from django_filters import rest_framework as filters
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from .filters import TaskFilter
from taggit.models import Tag
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
# Create your views here.


class TasksApiView(LoginRequiredMixin, APIView):
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = TaskFilter

    def get(self, request):
        """
        Get all tasks
        """
        tasks = Task.objects.filter(user=request.user)
        # Apply filtering
        filterset = TaskFilter(request.GET, queryset=tasks)
        if filterset.is_valid():
            tasks = filterset.qs
        # above we sorted task by order & of same order then sort by id
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)

    def post(self, request):
        """
        Create a new task
        """
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        """
        Update the Tasks in bulk
        """
        action = request.data.get('action')
        if action == 'update_order':
            tasks = request.data.get('tasks')
            for idx, task in enumerate(tasks, start=1):
                task_obj = get_object_or_404(Task, pk=task['id'])
                task_obj.order = idx
                task_obj.save()
            return Response(status=status.HTTP_200_OK)
        return Response({"error": "unknown action"}, status=status.HTTP_400_BAD_REQUEST)


class TaskApiView(LoginRequiredMixin, APIView):
    def get(self, request, pk):
        """
        Get a task by id
        """
        task = Task.objects.get(pk=pk)
        serializer = TaskSerializer(task)
        return Response(serializer.data)

    def put(self, request, pk):
        """
        Update a task
        use `toggle_task_completion` for toggling the completion status and this
        one for updating other fields.
        """
        task = get_object_or_404(Task, pk=pk)
        serializer = TaskSerializer(task, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        task = get_object_or_404(Task, pk=pk)
        task.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
@login_required
def toggle_task_completion(request, pk):
    """
    Toggle the completion status of a task
    best to use since we aren't sending/receiving any data unlike the TaskApiView
    """
    task:Task = get_object_or_404(Task, pk=pk)
    task.is_completed = not task.is_completed
    task.save()
    return Response(status=status.HTTP_200_OK)


@api_view(['GET'])
@login_required
def get_all_projects(request):
    """
    Get all projects
    """
    projects = Project.objects.filter(user=request.user)
    serializer = ProjectSerializer(projects, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@login_required
def create_project(request):
    """
    Create a new project
    """
    serializer = ProjectSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@login_required
def get_all_tags(request):
    """
    Get all tags that are used in tasks
    """
    # Get tags only from tasks
    tags = Tag.objects.filter(
        task__isnull=False,
        user=request.user,
    ).distinct().values_list('name', flat=True)
    return Response(tags)
