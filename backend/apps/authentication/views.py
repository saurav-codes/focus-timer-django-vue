from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
import json
from .serializers import UserSerializer

from django.views.decorators.http import require_http_methods
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate, login, logout
from .forms import CreateUserForm
from django.contrib.auth import get_user_model
import logging

logger = logging.getLogger(__name__)


User = get_user_model()


@ensure_csrf_cookie
@require_http_methods(["GET"])
def set_csrf_token(request):
    """
    We set the CSRF cookie on the frontend.
    """
    logger.info("CSRF cookie set for session")
    return JsonResponse({"message": "CSRF cookie set"})


@require_http_methods(["POST"])
def login_view(request):
    try:
        data = json.loads(request.body.decode("utf-8"))
        email = data["email"]
        password = data["password"]
    except json.JSONDecodeError:
        logger.error("Invalid JSON in login request")
        return JsonResponse({"success": False, "message": "Invalid JSON"}, status=400)

    user = authenticate(request, username=email, password=password)

    if user:
        login(request, user)
        logger.info(f"User login success: user_id={user.id}")
        return JsonResponse({"success": True})
    logger.warning("User login failed: invalid credentials")
    return JsonResponse(
        {"success": False, "message": "Invalid credentials"}, status=401
    )


def logout_view(request):
    logout(request)
    logger.info(f"User logout: user_id={request.user.id}")
    return JsonResponse({"message": "Logged out"})


@require_http_methods(["GET"])
def user(request):
    if request.user.is_authenticated:
        logger.info(f"Fetched user details: user_id={request.user.id}")
        user = get_object_or_404(User, pk=request.user.id)
        user_serializer = UserSerializer(user)
        return JsonResponse(user_serializer.data, status=200)
    logger.warning("Unauthenticated access to user endpoint")
    return JsonResponse({"message": "Not logged in"}, status=401)


@require_http_methods(["POST"])
def register(request):
    data = json.loads(request.body.decode("utf-8"))
    form = CreateUserForm(data)
    logger.info("User registration attempt")
    if form.is_valid():
        user = form.save()
        logger.info(f"User registered: user_id={user.id}")
        user_serializer = UserSerializer(user)
        return JsonResponse(user_serializer.data, status=201)
    else:
        errors = form.errors.as_json()
        logger.warning("User registration failed: validation errors")
        return JsonResponse({"error": errors}, status=400)
