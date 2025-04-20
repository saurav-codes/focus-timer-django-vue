import pytest
import json
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

# Unit Tests
@pytest.mark.unit
def test_user_model_create(user_data):
    """Test creating a user with the custom user model."""
    user = User.objects.create_user(
        email=user_data['email'],
        password=user_data['password']
    )
    assert user.email == user_data['email']
    assert user.is_active is True
    assert user.is_staff is False
    assert user.is_superuser is False

@pytest.mark.unit
def test_user_model_create_superuser():
    """Test creating a superuser with the custom user model."""
    email = "admin@example.com"
    password = "adminpassword123"
    user = User.objects.create_superuser(
        email=email,
        password=password
    )
    assert user.email == email
    assert user.is_active is True
    assert user.is_staff is True
    assert user.is_superuser is True

@pytest.mark.unit
def test_user_model_email_required():
    """Test that email field is required."""
    with pytest.raises(ValueError):
        User.objects.create_user(email="", password="testpass123")

@pytest.mark.unit
def test_user_model_str_method(authenticated_user, user_data):
    """Test the string representation of user objects."""
    assert str(authenticated_user) == user_data['email']

# Integration Tests
@pytest.mark.integration
def test_set_csrf_token(api_client):
    """Test the CSRF token view returns a 200 OK response."""
    url = reverse('set-csrf')
    response = api_client.get(url)
    assert response.status_code == 200
    assert 'message' in response.json()
    assert 'CSRF cookie set' in response.json()['message']

@pytest.mark.integration
def test_login_success(api_client, user_data, authenticated_user):
    """Test successful login."""
    url = reverse('login')
    data = {
        'email': user_data['email'],
        'password': user_data['password']
    }
    response = api_client.post(
        url,
        data=json.dumps(data),
        content_type='application/json'
    )
    assert response.status_code == 200
    assert response.json()['success'] is True

@pytest.mark.integration
def test_login_invalid_credentials(api_client, user_data, authenticated_user):
    """Test login with invalid credentials."""
    url = reverse('login')
    data = {
        'email': user_data['email'],
        'password': 'wrongpassword'
    }
    response = api_client.post(
        url,
        data=json.dumps(data),
        content_type='application/json'
    )
    assert response.status_code == 401
    assert response.json()['success'] is False
    assert 'Invalid credentials' in response.json()['message']

@pytest.mark.integration
def test_login_invalid_json(api_client):
    """Test login with invalid JSON data."""
    url = reverse('login')
    response = api_client.post(
        url,
        data='invalid json',
        content_type='application/json'
    )
    assert response.status_code == 400
    assert response.json()['success'] is False
    assert 'Invalid JSON' in response.json()['message']

@pytest.mark.integration
def test_logout(authenticated_client):
    """Test logout view."""
    url = reverse('logout')
    response = authenticated_client.post(url)
    assert response.status_code == 200
    assert 'message' in response.json()
    assert 'Logged out' in response.json()['message']

@pytest.mark.integration
def test_user_info_authenticated(authenticated_client, authenticated_user):
    """Test user info view with authenticated user."""
    url = reverse('user')
    response = authenticated_client.get(url)
    assert response.status_code == 200
    assert response.json()['email'] == authenticated_user.email

@pytest.mark.integration
def test_user_info_unauthenticated(api_client):
    """Test user info view with unauthenticated user."""
    url = reverse('user')
    response = api_client.get(url)
    assert response.status_code == 401
    assert 'message' in response.json()
    assert 'Not logged in' in response.json()['message']

@pytest.mark.integration
def test_registration_success(api_client):
    """Test successful user registration."""
    url = reverse('register')
    data = {
        'email': 'newuser@example.com',
        'password1': 'securepass123',
        'password2': 'securepass123',
        'first_name': 'New',
        'last_name': 'User'
    }
    response = api_client.post(
        url,
        data=json.dumps(data),
        content_type='application/json'
    )
    assert response.status_code == 201
    assert User.objects.filter(email='newuser@example.com').exists()
    assert response.json()['email'] == 'newuser@example.com'

@pytest.mark.integration
def test_registration_password_mismatch(api_client):
    """Test registration with mismatched passwords."""
    url = reverse('register')
    data = {
        'email': 'newuser@example.com',
        'password1': 'securepass123',
        'password2': 'differentpass',
        'first_name': 'New',
        'last_name': 'User'
    }
    response = api_client.post(
        url,
        data=json.dumps(data),
        content_type='application/json'
    )
    assert response.status_code == 400
    assert 'error' in response.json()
    assert not User.objects.filter(email='newuser@example.com').exists()

@pytest.mark.integration
def test_registration_existing_email(api_client, authenticated_user, user_data):
    """Test registration with an email that already exists."""
    url = reverse('register')
    data = {
        'email': user_data['email'],  # Email already exists
        'password1': 'securepass123',
        'password2': 'securepass123',
        'first_name': 'New',
        'last_name': 'User'
    }
    response = api_client.post(
        url,
        data=json.dumps(data),
        content_type='application/json'
    )
    assert response.status_code == 400
    assert 'error' in response.json()
