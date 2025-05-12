import pytest
from django.contrib.auth import get_user_model
from datetime import timedelta, datetime, timezone

from rest_framework.test import APIClient
User = get_user_model()

@pytest.fixture
def api_client():
    """Return an API client for testing."""
    return APIClient()

@pytest.fixture
def user_data():
    """Return test user data."""
    return {
        'email': 'testuser@example.com',
        'password': 'securepassword123',
        'first_name': 'Test',
        'last_name': 'User'
    }

@pytest.fixture
def authenticated_user(user_data):
    """Create and return an authenticated user."""
    user = User.objects.create_user(
        email=user_data['email'],
        password=user_data['password'],
        first_name=user_data['first_name'],
        last_name=user_data['last_name']
    )
    return user

@pytest.fixture
def authenticated_client(api_client, authenticated_user, user_data):
    """Return an authenticated API client."""
    api_client.login(username=user_data['email'], password=user_data['password'])
    return api_client

@pytest.fixture
def project(authenticated_user):
    """Create and return a test project."""
    from apps.core.models import Project
    return Project.objects.create(
        user=authenticated_user,
        title="Test Project",
        description="This is a test project"
    )

@pytest.fixture
def task(authenticated_user, project):
    """Create and return a test task."""
    from apps.core.models import Task
    return Task.objects.create(
        user=authenticated_user,
        title="Test Task",
        description="This is a test task",
        order=1,
        is_completed=False,
        duration=timedelta(minutes=30),
        project=project
    )

@pytest.fixture
def kanban_task(authenticated_user):
    """Create and return a task in a kanban column."""
    from apps.core.models import Task
    today = datetime.now(timezone.utc)
    return Task.objects.create(
        user=authenticated_user,
        title="Kanban Task",
        description="This is a task in a kanban column",
        order=1,
        is_completed=False,
        duration=timedelta(minutes=45),
        column_date=today
    )

@pytest.fixture
def calendar_task(authenticated_user):
    """Create and return a task with calendar dates."""
    from apps.core.models import Task
    now = datetime.now(timezone.utc)
    start = now.replace(hour=10, minute=0, second=0, microsecond=0)
    end = start + timedelta(hours=1)

    return Task.objects.create(
        user=authenticated_user,
        title="Calendar Task",
        description="This is a task in the calendar",
        order=1,
        is_completed=False,
        duration=timedelta(hours=1),
        start_at=start,
        end_at=end
    )

@pytest.fixture
def completed_task(authenticated_user):
    """Create and return a completed task."""
    from apps.core.models import Task
    return Task.objects.create(
        user=authenticated_user,
        title="Completed Task",
        description="This is a completed task",
        order=1,
        is_completed=True,
        duration=timedelta(minutes=15)
    )
