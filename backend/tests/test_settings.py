import pytest
from django.conf import settings
import os


@pytest.mark.unit
def test_base_settings():
    """Test that base settings are correctly configured."""
    # Test installed apps
    assert "django.contrib.admin" in settings.INSTALLED_APPS
    assert "django.contrib.auth" in settings.INSTALLED_APPS
    assert "apps.core" in settings.INSTALLED_APPS
    assert "apps.authentication" in settings.INSTALLED_APPS

    # Test middleware
    assert "corsheaders.middleware.CorsMiddleware" in settings.MIDDLEWARE
    assert "django.middleware.security.SecurityMiddleware" in settings.MIDDLEWARE
    assert "simple_history.middleware.HistoryRequestMiddleware" in settings.MIDDLEWARE

    # Test authentication
    assert settings.AUTH_USER_MODEL == "authentication.User"

    # Test debug mode (should be True for tests)
    assert settings.DEBUG is True

    # Test REST Framework settings
    assert "DEFAULT_AUTHENTICATION_CLASSES" in settings.REST_FRAMEWORK
    assert "DEFAULT_PERMISSION_CLASSES" in settings.REST_FRAMEWORK


@pytest.mark.unit
def test_database_settings():
    """Test that database settings are correctly configured."""
    # For testing, we should be using SQLite
    assert settings.DATABASES["default"]["ENGINE"] == "django.db.backends.sqlite3"

    # The database name should be specified
    assert "NAME" in settings.DATABASES["default"]


@pytest.mark.unit
def test_cors_settings():
    """Test that CORS settings are correctly configured."""
    # CORS settings should be defined
    assert hasattr(settings, "CORS_ALLOWED_ORIGINS")
    assert hasattr(settings, "CORS_ALLOW_CREDENTIALS")

    # For development, localhost should be included
    assert "http://localhost:5173" in settings.CORS_ALLOWED_ORIGINS


@pytest.mark.unit
def test_security_settings():
    """Test security settings are properly configured based on DEBUG setting."""
    if not settings.DEBUG:
        # Production settings
        assert settings.SESSION_COOKIE_SECURE is True
        assert settings.CSRF_COOKIE_SECURE is True
        assert settings.SECURE_SSL_REDIRECT is True
        assert settings.SECURE_HSTS_SECONDS == 31536000  # 1 year
        assert settings.SECURE_HSTS_INCLUDE_SUBDOMAINS is True
        assert settings.SECURE_HSTS_PRELOAD is True
        assert settings.SECURE_CONTENT_TYPE_NOSNIFF is True
        assert settings.SECURE_BROWSER_XSS_FILTER is True
        assert settings.X_FRAME_OPTIONS == "DENY"
    else:
        # Development settings (these checks would be optional)
        # For completeness, we can check if some security settings are still enabled even in DEBUG
        assert settings.CSRF_COOKIE_SAMESITE == "None"
        assert settings.SESSION_COOKIE_SAMESITE == "None"


@pytest.mark.unit
def test_file_paths():
    """Test that important file paths are correctly set."""
    # BASE_DIR should be the directory containing the settings file
    assert os.path.exists(settings.BASE_DIR)

    # Static and media settings
    assert hasattr(settings, "STATIC_URL")
