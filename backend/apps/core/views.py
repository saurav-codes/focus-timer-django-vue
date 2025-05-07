from django.shortcuts import get_object_or_404
from .models import Task, Project
from .serializers import TaskSerializer, ProjectSerializer
from django_filters import rest_framework as filters
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from .filters import TaskFilter
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from taggit.models import Tag, TaggedItem
from django.db import transaction
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
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)

    def post(self, request):
        """
        Create a new task
        """
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            with transaction.atomic():
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
                with transaction.atomic():
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
            with transaction.atomic():
                serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        task = get_object_or_404(Task, pk=pk)
        with transaction.atomic():
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
    with transaction.atomic():
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


class ProjectDetailApiView(LoginRequiredMixin, APIView):
    def get(self, request, pk):
        """
        Get a project by id
        """
        project = get_object_or_404(Project, pk=pk)
        serializer = ProjectSerializer(project)
        return Response(serializer.data)

    def put(self, request, pk):
        """
        Update a project
        """
        project = get_object_or_404(Project, pk=pk)
        serializer = ProjectSerializer(project, data=request.data)
        if serializer.is_valid():
            with transaction.atomic():
                serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        project = get_object_or_404(Project, pk=pk)
        with transaction.atomic():
            project.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
@login_required
def create_project(request):
    """
    Create a new project
    """
    serializer = ProjectSerializer(data={**request.data, 'user': request.user.id})
    if serializer.is_valid():
        with transaction.atomic():
            serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@login_required
def get_all_tags(request):
    """
    Get all tags that are used in tasks
    """
    # Get IDs of tasks owned by the current user
    user_task_ids = Task.objects.filter(user=request.user).values_list('id', flat=True)

    # Get unique tags associated with those tasks
    tag_ids = TaggedItem.objects.filter(
        object_id__in=user_task_ids,
        content_type__model='task'
    ).values_list('tag_id', flat=True).distinct()

    # Get the actual tags with proper formatting
    user_tags = Tag.objects.filter(id__in=tag_ids).values('name', 'id')

    return Response(user_tags)
