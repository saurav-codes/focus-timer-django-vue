from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.conf import settings
import logging
import requests
import uuid

from .models import GitHubCredentials, GitHubSettings
from .services import (
    get_repositories as fetch_repositories,
    get_issues as fetch_issues,
    get_issue_details as fetch_issue_details,
    convert_to_task as convert_issue_to_task_service,
)

logger = logging.getLogger(__name__)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def check_github_connection(request):
    """Check if the user has connected their GitHub account."""
    try:
        credentials_instance = GitHubCredentials.objects.filter(
            user=request.user
        ).first()
        if credentials_instance:
            if credentials_instance.test_token_validity():
                # Get or create GitHub settings
                github_settings = GitHubSettings.get_or_create_for_user(request.user)

                return Response(
                    {"connected": True, "sync_enabled": github_settings.sync_enabled},
                    status=200,
                )
        else:
            return Response(
                {"connected": False, "error": "GitHub account not connected"},
                status=404,
            )

    except Exception as e:
        logger.error(f"Error checking GitHub connection: {str(e)}")
        return Response({"connected": False, "error": str(e)}, status=500)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def start_github_auth(request):
    """Start the GitHub OAuth2 flow."""
    try:
        # Generate a unique state parameter to prevent CSRF
        state = str(uuid.uuid4())

        # Store the state in the session
        request.session["github_auth_state"] = state

        # GitHub OAuth2 parameters
        client_id = getattr(settings, "GITHUB_CLIENT_ID", "")
        if not client_id:
            return Response({"error": "GitHub OAuth not configured"}, status=500)

        redirect_uri = getattr(
            settings,
            "GITHUB_REDIRECT_URI",
            f"{settings.FRONTEND_URL}/auth/github/callback",
        )
        scope = "repo"

        auth_url = (
            f"https://github.com/login/oauth/authorize"
            f"?client_id={client_id}"
            f"&redirect_uri={redirect_uri}"
            f"&scope={scope}"
            f"&state={state}"
        )

        return Response({"auth_url": auth_url})
    except Exception as e:
        logger.error(f"Error starting GitHub auth: {str(e)}")
        return Response({"error": str(e)}, status=500)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def github_auth_callback(request):
    """Handle the callback from GitHub OAuth2 flow."""
    try:
        # Get the state from the request and session
        request_state = request.GET.get("state")
        session_state = request.session.get("github_auth_state")

        # Verify the state to prevent CSRF attacks
        if not request_state or request_state != session_state:
            return Response({"error": "Invalid state parameter"}, status=400)

        # Clear the state from the session
        if "github_auth_state" in request.session:
            del request.session["github_auth_state"]

        # Get the authorization code
        code = request.GET.get("code")
        if not code:
            return Response({"error": "No authorization code provided"}, status=400)

        # Exchange code for access token
        client_id = getattr(settings, "GITHUB_CLIENT_ID", "")
        client_secret = getattr(settings, "GITHUB_CLIENT_SECRET", "")

        token_response = requests.post(
            "https://github.com/login/oauth/access_token",
            data={
                "client_id": client_id,
                "client_secret": client_secret,
                "code": code,
            },
            headers={"Accept": "application/json"},
            timeout=30,
        )

        if token_response.status_code != 200:
            return Response({"error": "Failed to exchange code for token"}, status=400)

        token_data = token_response.json()

        if "error" in token_data:
            return Response(
                {"error": token_data.get("error_description", "OAuth error")},
                status=400,
            )

        access_token = token_data.get("access_token")
        if not access_token:
            return Response({"error": "No access token received"}, status=400)

        # Get user info from GitHub
        user_response = requests.get(
            "https://api.github.com/user",
            headers={
                "Authorization": f"token {access_token}",
                "Accept": "application/vnd.github.v3+json",
            },
            timeout=30,
        )

        if user_response.status_code != 200:
            return Response({"error": "Failed to get user info"}, status=400)

        user_data = user_response.json()

        # Store or update credentials
        credentials, created = GitHubCredentials.objects.update_or_create(
            user=request.user,
            defaults={
                "access_token": access_token,
                "token_type": token_data.get("token_type", "bearer"),
                "scope": token_data.get("scope", ""),
                "github_username": user_data.get("login"),
                "github_user_id": user_data.get("id"),
            },
        )

        return Response({"success": True, "username": user_data.get("login")})

    except Exception as e:
        logger.error(f"Error in GitHub auth callback: {str(e)}")
        return Response({"error": str(e)}, status=500)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def disconnect_github(request):
    """Disconnect GitHub account."""
    try:
        GitHubCredentials.objects.filter(user=request.user).delete()
        GitHubSettings.objects.filter(user=request.user).delete()
        return Response({"success": True})
    except Exception as e:
        logger.error(f"Error disconnecting GitHub: {str(e)}")
        return Response({"error": str(e)}, status=500)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_repositories(request):
    """Get list of repositories accessible to the user."""
    try:
        result = fetch_repositories(request.user)

        if "error" in result:
            return Response({"error": result["error"]}, status=400)

        return Response(result)
    except Exception as e:
        logger.error(f"Error fetching repositories: {str(e)}")
        return Response({"error": str(e)}, status=500)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_github_issues(request):
    """Get issues assigned to the user from GitHub repositories."""
    try:
        # Get query parameters
        repositories = (
            request.GET.get("repositories", "").split(",")
            if request.GET.get("repositories")
            else None
        )
        repositories = (
            [r.strip() for r in repositories if r.strip()] if repositories else None
        )

        assignee = request.GET.get("assignee", "assigned")
        state = request.GET.get("state", "open")
        page = int(request.GET.get("page", 1))
        per_page = int(request.GET.get("per_page", 30))

        # Get issues using service
        result = fetch_issues(
            user=request.user,
            repositories=repositories,
            page=page,
            per_page=per_page,
            assignee=assignee,
            state=state,
        )

        if "error" in result:
            return Response({"error": result["error"]}, status=400)

        return Response(result)
    except Exception as e:
        logger.error(f"Error fetching GitHub issues: {str(e)}")
        return Response({"error": str(e)}, status=500)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_issue_details(request, issue_id):
    """Get detailed information about a specific issue."""
    try:
        result = fetch_issue_details(request.user, issue_id)

        if "error" in result:
            return Response({"error": result["error"]}, status=400)

        return Response(result)
    except Exception as e:
        logger.error(f"Error fetching issue details: {str(e)}")
        return Response({"error": str(e)}, status=500)


@api_view(["GET", "PUT"])
@permission_classes([IsAuthenticated])
def github_settings(request):
    """Get or update GitHub integration settings."""
    try:
        # Check if GitHub is connected
        credentials_instance = GitHubCredentials.objects.filter(
            user=request.user
        ).first()
        if not credentials_instance:
            return Response({"error": "GitHub not connected"}, status=400)

        # Get GitHub settings
        github_settings = GitHubSettings.get_or_create_for_user(request.user)

        if request.method == "GET":
            # Get current settings
            settings_data = {
                "github_sync_enabled": github_settings.sync_enabled,
                "github_sync_repositories": github_settings.sync_repositories,
            }
            return Response(settings_data)

        elif request.method == "PUT":
            # Update settings
            data = request.data
            if "github_sync_enabled" in data:
                github_settings.sync_enabled = data["github_sync_enabled"]
            if "github_sync_repositories" in data:
                github_settings.sync_repositories = data["github_sync_repositories"]

            github_settings.save()

            settings_data = {
                "github_sync_enabled": github_settings.sync_enabled,
                "github_sync_repositories": github_settings.sync_repositories,
            }
            return Response(settings_data)

    except Exception as e:
        logger.error(f"Error handling GitHub settings: {str(e)}")
        return Response({"error": str(e)}, status=500)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def convert_issue_to_task(request, issue_id):
    """Convert a GitHub issue to a task."""
    try:
        task_data = request.data

        result = convert_issue_to_task_service(request.user, issue_id, task_data)

        if "error" in result:
            return Response({"error": result["error"]}, status=400)

        return Response(result)
    except Exception as e:
        logger.error(f"Error converting issue to task: {str(e)}")
        return Response({"error": str(e)}, status=500)
