import pytest
from django.urls import reverse, resolve

@pytest.mark.unit
def test_admin_url():
    """Test that admin URL is correctly configured."""
    url = reverse('admin:index')
    assert url == '/admin/'
    resolver = resolve(url)
    assert resolver.app_name == 'admin'

@pytest.mark.unit
def test_authentication_urls():
    """Test that authentication URLs are correctly configured."""
    # Login URL
    url = reverse('login')
    assert url == '/auth/login/'
    resolver = resolve(url)
    assert resolver.view_name == 'login'

    # Logout URL
    url = reverse('logout')
    assert url == '/auth/logout/'
    resolver = resolve(url)
    assert resolver.view_name == 'logout'

    # User info URL
    url = reverse('user')
    assert url == '/auth/user/'
    resolver = resolve(url)
    assert resolver.view_name == 'user'

    # Register URL
    url = reverse('register')
    assert url == '/auth/register/'
    resolver = resolve(url)
    assert resolver.view_name == 'register'

    # CSRF token URL
    url = reverse('set-csrf')
    assert url == '/auth/set-csrf/'
    resolver = resolve(url)
    assert resolver.view_name == 'set-csrf'

@pytest.mark.unit
def test_core_api_urls():
    """Test that core API URLs are correctly configured."""
    # Tasks list URL
    url = reverse('tasks')
    assert url == '/api/tasks/'
    resolver = resolve(url)
    assert resolver.view_name == 'tasks'

    # Task detail URL (with parameter)
    url = reverse('task-detail', args=[1])
    assert url == '/api/tasks/1/'
    resolver = resolve(url)
    assert resolver.view_name == 'task-detail'

    # Toggle task completion URL
    url = reverse('toggle-task-completion', args=[1])
    assert url == '/api/tasks/1/toggle-completion/'
    resolver = resolve(url)
    assert resolver.view_name == 'toggle-task-completion'

    # Projects URL
    url = reverse('projects')
    assert url == '/api/projects/'
    resolver = resolve(url)
    assert resolver.view_name == 'projects'

    # Create project URL
    url = reverse('create-project')
    assert url == '/api/projects/create/'
    resolver = resolve(url)
    assert resolver.view_name == 'create-project'

    # Tags URL
    url = reverse('tags')
    assert url == '/api/tags/'
    resolver = resolve(url)
    assert resolver.view_name == 'tags'
