from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
import json
from .serializers import UserSerializer

from django.views.decorators.http import require_http_methods
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate, login, logout
from .forms import CreateUserForm
from django.contrib.auth import get_user_model


User = get_user_model()


@ensure_csrf_cookie
@require_http_methods(["GET"])
def set_csrf_token(request):
    """
    We set the CSRF cookie on the frontend.
    """
    return JsonResponse({"message": "CSRF cookie set"})


@require_http_methods(["POST"])
def login_view(request):
    try:
        data = json.loads(request.body.decode("utf-8"))
        email = data["email"]
        password = data["password"]
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "message": "Invalid JSON"}, status=400)

    user = authenticate(request, username=email, password=password)

    if user:
        login(request, user)
        return JsonResponse({"success": True})
    return JsonResponse(
        {"success": False, "message": "Invalid credentials"}, status=401
    )


def logout_view(request):
    logout(request)
    return JsonResponse({"message": "Logged out"})


@require_http_methods(["GET"])
def user(request):
    if request.user.is_authenticated:
        user = get_object_or_404(User, pk=request.user.id)
        user_serializer = UserSerializer(user)
        return JsonResponse(user_serializer.data, status=200)
    return JsonResponse({"message": "Not logged in"}, status=401)


@require_http_methods(["POST"])
def register(request):
    data = json.loads(request.body.decode("utf-8"))
    form = CreateUserForm(data)
    if form.is_valid():
        user = form.save()
        user_serializer = UserSerializer(user)
        return JsonResponse(user_serializer.data, status=201)
    else:
        errors = form.errors.as_json()
        return JsonResponse({"error": errors}, status=400)
