from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
import logging

from apps.integrations.google_calendar.models import GoogleCredentials
from .models import GmailSettings
from .services import (
    get_emails,
    toggle_star,
    mark_as_read,
    convert_to_task,
    get_gmail_labels,
)

logger = logging.getLogger(__name__)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def check_gmail_connection(request):
    """Check if the user has connected their Google account with Gmail permissions."""
    try:
        credentials_instance = GoogleCredentials.objects.filter(
            user=request.user
        ).first()
        if credentials_instance:
            credentials_data = credentials_instance.get_credentials()
            if isinstance(credentials_data, dict):  # dict instance means error dict
                return Response(credentials_data, status=400)
            if credentials_instance.is_gmail_scope_granted() is False:
                return Response({"connected": False}, status=400)

            # Get or create Gmail settings
            gmail_settings = GmailSettings.get_or_create_for_user(request.user)

            return Response(
                {"connected": True, "sync_enabled": gmail_settings.sync_enabled},
                status=200,
            )
        else:
            return Response(
                {"connected": False, "error": "Google account not connected"},
                status=404,
            )

    except Exception as e:
        logger.error(f"Error checking Gmail connection: {str(e)}")
        return Response({"connected": False, "error": str(e)}, status=500)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_gmail_emails(request):
    """Get emails from the user's Gmail account."""
    try:
        # Get query parameters
        label_ids = request.GET.get("labelIds", "INBOX").split(",")
        max_results = int(request.GET.get("maxResults", 20))
        page_token = request.GET.get("pageToken")

        # Get Gmail settings
        gmail_settings = GmailSettings.get_or_create_for_user(request.user)

        # Check if sync is enabled
        if not gmail_settings.sync_enabled:
            return Response({"error": "Gmail sync is disabled"}, status=400)

        # Get emails
        result = get_emails(
            user=request.user,
            label_ids=label_ids,
            max_results=max_results,
            page_token=page_token,
        )

        if "error" in result:
            return Response({"error": result["error"]}, status=400)

        return Response(result)
    except Exception as e:
        logger.error(f"Error fetching Gmail emails: {str(e)}")
        return Response({"error": str(e)}, status=500)


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def toggle_email_star(request, email_id):
    """Toggle star status for an email."""
    try:
        starred = request.data.get("starred", True)
        result = toggle_star(request.user, email_id, starred)

        if "error" in result:
            return Response({"error": result["error"]}, status=400)

        return Response(result)
    except Exception as e:
        logger.error(f"Error toggling email star: {str(e)}")
        return Response({"error": str(e)}, status=500)


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def mark_email_read(request, email_id):
    """Mark an email as read or unread."""
    try:
        read = request.data.get("read", True)
        result = mark_as_read(request.user, email_id, read)

        if "error" in result:
            return Response({"error": result["error"]}, status=400)

        return Response(result)
    except Exception as e:
        logger.error(f"Error marking email as read: {str(e)}")
        return Response({"error": str(e)}, status=500)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def convert_email_to_task(request, email_id):
    """Convert an email to a task."""
    try:
        task_data = request.data
        result = convert_to_task(request.user, email_id, task_data)

        if "error" in result:
            return Response({"error": result["error"]}, status=400)

        return Response(result)
    except Exception as e:
        logger.error(f"Error converting email to task: {str(e)}")
        return Response({"error": str(e)}, status=500)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_gmail_labels_view(request):
    """Get available Gmail labels."""
    try:
        result = get_gmail_labels(request.user)

        if "error" in result:
            return Response({"error": result["error"]}, status=400)

        return Response(result)
    except Exception as e:
        logger.error(f"Error fetching Gmail labels: {str(e)}")
        return Response({"error": str(e)}, status=500)


@api_view(["GET", "PUT"])
@permission_classes([IsAuthenticated])
def gmail_settings(request):
    """Get or update Gmail integration settings."""
    try:
        # Check if Gmail is connected
        credentials_instance = GoogleCredentials.objects.filter(
            user=request.user
        ).first()
        if (
            not credentials_instance
            or not credentials_instance.is_gmail_scope_granted()
        ):
            return Response({"error": "Gmail not connected"}, status=400)

        # Get Gmail settings
        gmail_settings = GmailSettings.get_or_create_for_user(request.user)

        if request.method == "GET":
            # Get current settings
            settings = {
                "gmail_sync_enabled": gmail_settings.sync_enabled,
                "gmail_sync_labels": gmail_settings.sync_labels or ["INBOX"],
            }
            return Response(settings)

        elif request.method == "PUT":
            # Update settings
            data = request.data
            if "gmail_sync_enabled" in data:
                gmail_settings.sync_enabled = data["gmail_sync_enabled"]
            if "gmail_sync_labels" in data:
                gmail_settings.sync_labels = data["gmail_sync_labels"]

            gmail_settings.save()

            settings = {
                "gmail_sync_enabled": gmail_settings.sync_enabled,
                "gmail_sync_labels": gmail_settings.sync_labels or ["INBOX"],
            }
            return Response(settings)

    except Exception as e:
        logger.error(f"Error handling Gmail settings: {str(e)}")
        return Response({"error": str(e)}, status=500)
