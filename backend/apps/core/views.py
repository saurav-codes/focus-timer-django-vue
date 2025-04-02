from django.shortcuts import get_object_or_404
from .models import Task
from .serializers import TaskSerializer
from django_filters import rest_framework as filters
from django import forms
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.views import APIView
# Create your views here.


class TasksApiView(APIView):

    def get(self, request):
        """
        Get all tasks
        """
        tasks = Task.objects.all().order_by('order', '-id')
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


class TaskApiView(APIView):
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
        task = Task.objects.get(pk=pk)
        task.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@csrf_exempt
@api_view(['POST'])
def toggle_task_completion(request, pk):
    """
    Toggle the completion status of a task
    best to use since we aren't sending/receiving any data unlike the TaskApiView
    """
    task:Task = get_object_or_404(Task, pk=pk)
    task.is_completed = not task.is_completed
    task.save()
    return Response(status=status.HTTP_200_OK)