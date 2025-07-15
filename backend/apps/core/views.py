from django.shortcuts import get_object_or_404
from .models import Task, Project
from .serializers import TaskSerializer, ProjectSerializer, TaskDurationUpdateSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from taggit.models import Tag, TaggedItem
from django.db import transaction
import logging
from .tasks import notify_frontend
from datetime import timedelta
from .services import save_task

logger = logging.getLogger(__name__)
# Create your views here.


@csrf_protect
@api_view(["POST"])
@login_required
def update_task_duration(request):
    task_id = request.data["task_id"]
    logger.info(
        f"updating task duration: task_id={task_id} by user_id={request.user.id}"
    )
    # filter by user to ensure the task and project belong to the same user
    task = get_object_or_404(Task, pk=task_id, user=request.user)
    duration_serializer = TaskDurationUpdateSerializer(data=request.data)
    if duration_serializer.is_valid():
        task.duration = duration_serializer.validated_data["duration"]  # type:ignore
        # also set end time according to the duration.
        if task.start_at and isinstance(task.duration, timedelta):
            task.end_at = task.start_at + task.duration  # type:ignore
        save_task(task)
        serialized_task = TaskSerializer(task).data
        notify_frontend.delay(  # type: ignore
            f"tasks_user_{task.user.pk}",
            {
                "type": "task_updated",
                "data": serialized_task,
            },
        )
        return Response(serialized_task, status=status.HTTP_200_OK)
    return Response(duration_serializer.errors, status=400)


@csrf_protect
@api_view(["POST"])
@login_required
def assign_project_to_task(request, task_id, project_id):
    """
    Assign a project to a task
    """
    logger.info(
        f"Assigning project to task: task_id={task_id} project_id={project_id} by user_id={request.user.id}"
    )
    # filter by user to ensure the task and project belong to the same user
    task = get_object_or_404(Task, pk=task_id, user=request.user)
    project = get_object_or_404(Project, pk=project_id, user=request.user)
    task.project = project
    save_task(task)  # save() returns None, so we don't assign it
    serializer = TaskSerializer(task)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["GET"])
@login_required
def get_all_projects(request):
    """
    Get all projects
    """
    logger.info(f"Fetching projects for user_id={request.user.id}")
    projects = Project.objects.filter(user=request.user)
    logger.info(f"Found {projects.count()} projects for user_id={request.user.id}")
    serializer = ProjectSerializer(projects, many=True)
    return Response(serializer.data)


class ProjectDetailApiView(LoginRequiredMixin, APIView):
    def get(self, request, pk):
        """
        Get a project by id
        """
        logger.info(f"Fetching project: project_id={pk} by user_id={request.user.id}")
        project = get_object_or_404(Project, pk=pk, user=request.user)
        serializer = ProjectSerializer(project)
        return Response(serializer.data)

    def put(self, request, pk):
        """
        Update a project
        """
        logger.info(f"Updating project: project_id={pk} by user_id={request.user.id}")
        project = get_object_or_404(Project, pk=pk, user=request.user)
        serializer = ProjectSerializer(
            project, data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            with transaction.atomic():
                serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        logger.info(f"Deleting project: project_id={pk} by user_id={request.user.id}")
        project = get_object_or_404(Project, pk=pk, user=request.user)
        with transaction.atomic():
            project.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@csrf_protect
@api_view(["POST"])
@login_required
def create_project(request):
    """
    Create a new project
    """
    logger.info(f"Creating project by user_id={request.user.id}")
    serializer = ProjectSerializer(data={**request.data}, context={"request": request})
    if serializer.is_valid():
        with transaction.atomic():
            serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@login_required
def get_all_tags(request):
    """
    Get all tags that are used in tasks
    """
    logger.info(f"Fetching tags for user_id={request.user.id}")
    # Get IDs of tasks owned by the current user
    user_task_ids = Task.objects.filter(user=request.user).values_list("id", flat=True)

    # Get unique tags associated with those tasks
    tag_ids = (
        TaggedItem.objects.filter(
            object_id__in=user_task_ids, content_type__model="task"
        )
        .values_list("tag_id", flat=True)
        .distinct()
    )

    # Get the actual tags with proper formatting
    user_tags = Tag.objects.filter(id__in=tag_ids).values("name", "id")

    return Response(user_tags)
