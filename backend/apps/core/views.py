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
from django.views.decorators.csrf import csrf_protect
from taggit.models import Tag, TaggedItem
from django.db import transaction
import logging

logger = logging.getLogger(__name__)
# Create your views here.


class TasksApiView(LoginRequiredMixin, APIView):
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = TaskFilter

    def get(self, request):
        """
        Get all tasks
        """
        logger.info(
            f"Fetching tasks for user_id={request.user.id} filters={request.GET.dict()}"
        )
        tasks = Task.objects.filter(user=request.user)
        # Apply filtering
        filterset = TaskFilter(request.GET, queryset=tasks)
        if not filterset.is_valid():
            logger.warning(
                f"TaskFilter invalid for user_id={request.user.id}, errors={filterset.errors}"
            )
        tasks = filterset.qs if filterset.is_valid() else tasks
        logger.info(f"Found {tasks.count()} tasks for user_id={request.user.id}")
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)

    def post(self, request):
        """
        Create a new task
        """
        serializer = TaskSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            with transaction.atomic():
                serializer.save()
                logger.info(
                    f"Task created: task_id={serializer.instance.id} by user_id={request.user.id}"
                )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        """
        Update the Tasks in bulk
        """
        action = request.data.get("action")
        if action == "update_order":
            tasks = request.data.get("tasks")
            logger.info(
                f"Bulk update order by user_id={request.user.id} for task_ids={[t['id'] for t in tasks]}"
            )
            for idx, task in enumerate(tasks, start=1):
                task_obj = get_object_or_404(Task, pk=task["id"], user=request.user)
                with transaction.atomic():
                    task_obj.order = idx
                    task_obj.save()
            return Response(status=status.HTTP_200_OK)
        return Response({"error": "unknown action"}, status=status.HTTP_400_BAD_REQUEST)


class TaskDetailApiView(LoginRequiredMixin, APIView):
    def get(self, request, pk):
        """
        Get a task by id
        """
        logger.info(f"Fetching task: task_id={pk} by user_id={request.user.id}")
        task = get_object_or_404(Task, pk=pk, user=request.user)
        serializer = TaskSerializer(task)
        return Response(serializer.data)

    def put(self, request, pk):
        """
        Update a task
        use `toggle_task_completion` for toggling the completion status and this
        one for updating other fields.
        """
        logger.info(f"Updating task: task_id={pk} by user_id={request.user.id}")
        task = get_object_or_404(Task, pk=pk, user=request.user)
        serializer = TaskSerializer(
            task, data=request.data, context={"request": request}, partial=True
        )
        if serializer.is_valid():
            with transaction.atomic():
                serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        logger.info(f"Deleting task: task_id={pk} by user_id={request.user.id}")
        task = get_object_or_404(Task, pk=pk, user=request.user)
        with transaction.atomic():
            task.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@csrf_protect
@api_view(["POST"])
@login_required
def toggle_task_completion(request, pk):
    """
    Toggle the completion status of a task
    best to use since we aren't sending/receiving any data unlike the TaskApiView
    """
    task: Task = get_object_or_404(Task, pk=pk, user=request.user)
    logger.info(
        f"Toggling completion: task_id={pk} old_status={task.is_completed} by user_id={request.user.id}"
    )
    with transaction.atomic():
        task.is_completed = not task.is_completed
        task.save()
    logger.info(f"New completion status: task_id={pk} new_status={task.is_completed}")
    return Response(status=status.HTTP_200_OK)


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
    task.save()  # save() returns None, so we don't assign it
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
