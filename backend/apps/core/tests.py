import pytest
import json
from django.urls import reverse
from datetime import timedelta, datetime, timezone
from django.contrib.auth import get_user_model
from apps.core.models import Task, Project
from django.utils.duration import _get_duration_components

User = get_user_model()

# Unit Tests for Models
@pytest.mark.unit
def test_project_model_creation(project, authenticated_user):
    """Test creating a project."""
    assert project.title == "Test Project"
    assert project.description == "This is a test project"
    assert project.user == authenticated_user
    assert str(project) == "Test Project"

@pytest.mark.unit
def test_task_model_creation(task, authenticated_user, project):
    """Test creating a task."""
    assert task.title == "Test Task"
    assert task.description == "This is a test task"
    assert task.user == authenticated_user
    assert task.project == project
    assert task.order == 1
    assert task.is_completed is False
    assert task.duration == timedelta(minutes=30)
    assert str(task) == "Test Task"
    assert task.get_duration_display == "30m"

@pytest.mark.unit
def test_task_duration_display_hours_and_minutes():
    """Test the duration display with hours and minutes."""
    duration = timedelta(hours=2, minutes=15)
    _, hours, minutes, _, _ = _get_duration_components(duration)

    assert hours == 2
    assert minutes == 15

    # Formatting check
    task = Task(duration=duration)
    assert task.get_duration_display == "2h 15m"

@pytest.mark.unit
def test_task_duration_display_hours_only():
    """Test the duration display with only hours."""
    duration = timedelta(hours=3)
    task = Task(duration=duration)
    assert task.get_duration_display == "3h"

@pytest.mark.unit
def test_task_duration_display_minutes_only():
    """Test the duration display with only minutes."""
    duration = timedelta(minutes=45)
    task = Task(duration=duration)
    assert task.get_duration_display == "45m"

@pytest.mark.unit
def test_task_duration_display_none():
    """Test the duration display when duration is None."""
    task = Task(duration=None)
    assert task.get_duration_display is None

# Integration Tests for Views
@pytest.mark.integration
def test_get_all_tasks(authenticated_client, task, kanban_task, calendar_task):
    """Test getting all tasks for a user."""
    url = reverse('tasks')
    response = authenticated_client.get(url)
    assert response.status_code == 200
    assert len(response.json()) == 3  # All 3 tasks should be returned

@pytest.mark.integration
def test_get_tasks_with_filter(authenticated_client, task, kanban_task, calendar_task, completed_task):
    """Test getting tasks with filtering."""
    # Create a specific test case for filtering
    url = reverse('tasks')
    # Filter by completion status
    response = authenticated_client.get(f"{url}?is_completed=true")
    assert response.status_code == 200
    assert len(response.json()) == 1  # Only the completed task
    assert response.json()[0]['is_completed'] is True

@pytest.mark.integration
def test_create_task(authenticated_client, authenticated_user, project):
    """Test creating a new task."""
    url = reverse('tasks')
    data = {
        'user': authenticated_user.id,
        'title': 'New Task',
        'description': 'This is a new task',
        'order': 2,
        'duration': '00:45:00',  # 45 minutes
        'project': project.id,
        'tags': ['work', 'important']
    }

    response = authenticated_client.post(
        url,
        data=json.dumps(data),
        content_type='application/json'
    )
    assert response.status_code == 201
    assert Task.objects.filter(title='New Task').exists()

    task = Task.objects.get(title='New Task')
    assert task.description == 'This is a new task'
    assert task.order == 2
    assert task.duration == timedelta(minutes=45)
    assert task.project.id == project.id
    assert list(task.tags.names()) == ['work', 'important']

@pytest.mark.integration
def test_update_task_order_bulk(authenticated_client, task, kanban_task):
    """Test updating the order of multiple tasks."""
    url = reverse('tasks')
    data = {
        'action': 'update_order',
        'tasks': [
            {'id': kanban_task.id},
            {'id': task.id}
        ]
    }

    response = authenticated_client.put(
        url,
        data=json.dumps(data),
        content_type='application/json'
    )
    assert response.status_code == 200

    # Reload from database
    task.refresh_from_db()
    kanban_task.refresh_from_db()

    assert kanban_task.order == 1
    assert task.order == 2

@pytest.mark.integration
def test_get_single_task(authenticated_client, task):
    """Test getting a single task by ID."""
    url = reverse('task-detail', args=[task.id])
    response = authenticated_client.get(url)
    assert response.status_code == 200
    assert response.json()['id'] == task.id
    assert response.json()['title'] == task.title

@pytest.mark.integration
def test_update_task(authenticated_client, task):
    """Test updating a task."""
    url = reverse('task-detail', args=[task.id])
    data = {
        'title': 'Updated Task',
        'description': 'This task has been updated',
        'is_completed': True,
        'duration': '01:00:00',  # 1 hour
        'user': task.user.id,
        'tags': ['updated', 'important']
    }

    response = authenticated_client.put(
        url,
        data=json.dumps(data),
        content_type='application/json'
    )
    assert response.status_code == 200

    # Reload from database
    task.refresh_from_db()
    assert task.title == 'Updated Task'
    assert task.description == 'This task has been updated'
    assert task.is_completed is True
    assert task.duration == timedelta(hours=1)
    assert set(task.tags.names()) == {'updated', 'important'}

@pytest.mark.integration
def test_delete_task(authenticated_client, task):
    """Test deleting a task."""
    task_id = task.id
    url = reverse('task-detail', args=[task_id])
    response = authenticated_client.delete(url)
    assert response.status_code == 204
    assert not Task.objects.filter(id=task_id).exists()

@pytest.mark.integration
def test_toggle_task_completion(authenticated_client, task):
    """Test toggling a task's completion status."""
    assert task.is_completed is False

    url = reverse('toggle-task-completion', args=[task.id])
    response = authenticated_client.post(url)
    assert response.status_code == 200

    # Reload from database
    task.refresh_from_db()
    assert task.is_completed is True

    # Toggle back to incomplete
    response = authenticated_client.post(url)
    assert response.status_code == 200

    # Reload from database
    task.refresh_from_db()
    assert task.is_completed is False

@pytest.mark.integration
def test_get_all_projects(authenticated_client, project):
    """Test getting all projects for a user."""
    url = reverse('projects')
    response = authenticated_client.get(url)
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]['id'] == project.id
    assert response.json()[0]['title'] == project.title

@pytest.mark.integration
def test_create_project(authenticated_client, authenticated_user):
    """Test creating a new project."""
    url = reverse('create-project')
    data = {
        'user': authenticated_user.id,
        'title': 'New Project',
        'description': 'This is a new project'
    }

    response = authenticated_client.post(
        url,
        data=json.dumps(data),
        content_type='application/json'
    )
    assert response.status_code == 201
    assert Project.objects.filter(title='New Project').exists()

    project = Project.objects.get(title='New Project')
    assert project.description == 'This is a new project'
    assert project.user == authenticated_user

@pytest.mark.integration
def test_get_all_tags(authenticated_client, task):
    """Test getting all tags used by a user's tasks."""
    # Add tags to the task
    task.tags.add('work', 'important', 'urgent')

    url = reverse('tags')
    response = authenticated_client.get(url)
    assert response.status_code == 200

    # Extract tag names from the response
    tag_names = [tag['name'] for tag in response.json()]
    assert 'work' in tag_names
    assert 'important' in tag_names
    assert 'urgent' in tag_names
    assert len(tag_names) == 3

# Edge Cases and Security Tests
@pytest.mark.integration
def test_task_access_control(api_client, authenticated_client, authenticated_user):
    """Test that users can only access their own tasks."""
    # Create a second user with their own task
    second_user = User.objects.create_user(
        email='seconduser@example.com',
        password='securepass123'
    )
    second_user_task = Task.objects.create(
        user=second_user,
        title="Second User's Task",
        description="This task belongs to the second user",
        order=1
    )

    # First user should not be able to access second user's task
    url = reverse('task-detail', args=[second_user_task.id])
    response = authenticated_client.get(url)
    assert response.status_code in [403, 404]  # Either forbidden or not found

    # Unauthenticated user should not be able to access any tasks
    url = reverse('tasks')
    response = api_client.get(url)
    assert response.status_code in [401, 403]  # Either unauthorized or forbidden

@pytest.mark.integration
def test_validation_on_task_creation(authenticated_client, authenticated_user):
    """Test validation on task creation with invalid data."""
    url = reverse('tasks')

    # Test with empty title (required field)
    data = {
        'user': authenticated_user.id,
        'title': '',  # Empty title should fail validation
        'description': 'This task has no title',
        'order': 1
    }

    response = authenticated_client.post(
        url,
        data=json.dumps(data),
        content_type='application/json'
    )
    assert response.status_code == 400
    assert 'title' in response.json()
