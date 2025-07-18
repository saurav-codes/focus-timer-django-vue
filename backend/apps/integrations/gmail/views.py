from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
import logging

from apps.integrations.google_calendar.models import GoogleCredentials

logger = logging.getLogger(__name__)


# Create your views here.
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def check_gmail_connection(request):
    """Check if the user has connected their Google Calendar."""
    try:
        credentials_instance = GoogleCredentials.objects.filter(
            user=request.user
        ).first()
        if credentials_instance:
            credentials_data = credentials_instance.get_credentials()
            if isinstance(credentials_data, dict):  # dict instance means error dict
                return Response(credentials_data, status=400)
            if credentials_instance.is_gmail_scope_granted is False:
                return Response({"connected": False}, status=400)
            return Response({"connected": True}, status=200)
        else:
            return Response(
                {"connected": False, "error": "Google Calendar not connected"},
                status=404,
            )

    except Exception as e:
        logger.error(f"Error checking Google connection: {str(e)}")
        return Response({"connected": False, "error": str(e)}, status=500)
