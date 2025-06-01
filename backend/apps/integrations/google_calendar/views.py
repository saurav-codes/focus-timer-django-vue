from django.shortcuts import redirect
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
import uuid
import logging
from googleapiclient.errors import HttpError
from django.views.decorators.csrf import csrf_protect

from .models import GoogleCalendarCredentials
from .utils import (
    create_flow,
    can_modify_event,
    build_calendar_service,
    format_event_for_fullcalendar,
    handle_calendar_api_error,
)
from apps.core.models import Task

logger = logging.getLogger(__name__)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def check_google_connection(request):
    """Check if the user has connected their Google Calendar."""
    try:
        credentials_instance = GoogleCalendarCredentials.objects.filter(
            user=request.user
        ).first()
        if credentials_instance:
            credentials_data = credentials_instance.get_credentials()
            if isinstance(credentials_data, dict):
                return Response(credentials_data, status=400)
            return Response({"connected": True}, status=200)
        else:
            return Response(
                {"connected": False, "error": "Google Calendar not connected"},
                status=404,
            )

    except Exception as e:
        logger.error(f"Error checking Google connection: {str(e)}")
        return Response({"connected": False, "error": str(e)}, status=500)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def start_google_auth(request):
    """Start the Google OAuth2 flow."""
    try:
        # Generate a unique state parameter to prevent CSRF
        state = str(uuid.uuid4())

        # Store the state in the session
        request.session["google_auth_state"] = state

        # Create the OAuth2 flow
        flow = create_flow(state=state)

        # Generate the authorization URL with offline access and force consent
        auth_url, _ = flow.authorization_url(
            access_type="offline", include_granted_scopes="true", prompt="consent"
        )

        return Response({"auth_url": auth_url})
    except Exception as e:
        logger.error(f"Error starting Google auth: {str(e)}")
        return Response({"error": str(e)}, status=500)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def google_auth_callback(request):
    """Handle the callback from Google OAuth2 flow."""
    try:
        # Get the state from the request and session
        request_state = request.GET.get("state")
        session_state = request.session.get("google_auth_state")

        # Verify the state to prevent CSRF attacks
        if not request_state or request_state != session_state:
            return Response({"error": "Invalid state parameter"}, status=400)

        # Clear the state from the session
        if "google_auth_state" in request.session:
            del request.session["google_auth_state"]

        # Get the authorization code
        code = request.GET.get("code")
        if not code:
            return Response({"error": "No authorization code provided"}, status=400)

        # Recreate the flow with the same state
        flow = create_flow(state=request_state)

        # Exchange the authorization code for credentials
        flow.fetch_token(code=code)
        credentials = flow.credentials

        # Format the credentials for storage
        token_data = {
            "token": credentials.token,
            "refresh_token": credentials.refresh_token,
            "token_uri": credentials.token_uri,
            "client_id": credentials.client_id,
            "client_secret": credentials.client_secret,
            "scopes": credentials.scopes,
            "expiry": credentials.expiry.isoformat() if credentials.expiry else None,
        }

        # Get user from session
        if not request.user.is_authenticated:
            return redirect(f"{settings.FRONTEND_URL}/login?error=auth_required")

        # Store or update the credentials in the database
        credentials_obj, created = GoogleCalendarCredentials.objects.update_or_create(
            user=request.user, defaults={"token": token_data}
        )

        # If this is a new connection, get the primary calendar ID
        if created or not credentials_obj.calendar_id:
            try:
                service = build_calendar_service(credentials)
                primary_calendar = (
                    service.calendars().get(calendarId="primary").execute()
                )
                credentials_obj.calendar_id = primary_calendar["id"]
                credentials_obj.save(update_fields=["calendar_id"])
            except Exception as e:
                logger.error(f"Error getting primary calendar ID: {str(e)}")

        # Redirect back to the calendar page in the frontend
        return redirect(f"{settings.FRONTEND_URL}/kanban-planner")
    except Exception as e:
        logger.error(f"Error in Google auth callback: {str(e)}")
        return redirect(f"{settings.FRONTEND_URL}/kanban-planner?error={str(e)}")


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_calendar_events(request):
    """Get events from the user's Google Calendar & apps' tasks which are on cal"""
    try:
        # Get the date range from the request
        start = request.GET.get("start")
        end = request.GET.get("end")

        if not start or not end:
            return Response(
                {"error": "start and end parameters are required"}, status=400
            )

        # Get the credentials for the user
        credentials_obj = GoogleCalendarCredentials.objects.filter(
            user=request.user
        ).first()
        if not credentials_obj:
            return Response({"error": "Google Calendar not connected"}, status=404)

        # Get the calendar service
        credentials = credentials_obj.get_credentials()
        if isinstance(credentials, dict) and credentials.get("error"):
            return Response(credentials, status=401)
        service = build_calendar_service(credentials)

        # Get the calendar ID (default to primary if not specified)
        calendar_id = credentials_obj.calendar_id or "primary"

        try:
            # Call the Calendar API
            events_result = (
                service.events()
                .list(
                    calendarId=calendar_id,
                    timeMin=start,
                    timeMax=end,
                    singleEvents=True,
                    orderBy="startTime",
                )
                .execute()
            )

            logger.info(
                f"Google events fetched count={len(events_result.get('items', []))} for user_id={request.user.id} calendar_id={calendar_id} time_range=({start},{end})"
            )
            events = events_result.get("items", [])

            # Transform to FullCalendar format
            formatted_events = [
                format_event_for_fullcalendar(event) for event in events
            ]

            # Get tasks with status ON_CAL for the current user
            on_cal_tasks = Task.objects.filter(
                user=request.user,
                status=Task.ON_CAL,
                start_at__isnull=False,  # Only include tasks with a start time
                end_at__isnull=False,  # Only include tasks with an end time
            )

            # Format tasks for FullCalendar and add to events list
            for task in on_cal_tasks:
                formatted_task = {
                    "id": f"task-{task.id}",  # Prefix with 'task-' to distinguish from Google events
                    "title": task.title,
                    "start": task.start_at.isoformat(),
                    "end": task.end_at.isoformat(),
                    "allDay": False,  # Tasks are not all-day events by default
                    "backgroundColor": "#4285F4",  # You can customize the color
                    "borderColor": "#4285F4",
                    "textColor": "#FFFFFF",
                    "extendedProps": {
                        "description": task.description or "",
                        "source": "task",  # Mark as a task source
                        "taskId": task.pk,
                        "status": task.status,
                        "isCompleted": task.is_completed,
                        "duration": task.duration,
                    },
                }
                formatted_events.append(formatted_task)

            return Response(formatted_events)
        except HttpError as e:
            error_details = handle_calendar_api_error(e)
            return Response(error_details)
        except Exception as e:
            logger.error(f"Error fetching calendar events: {str(e)}")
            return Response({"error": str(e)}, status=500)
    except Exception as e:
        logger.error(f"Unexpected error in get_calendar_events: {str(e)}")
        return Response({"error": str(e)}, status=500)


@csrf_protect
@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def disconnect_google_calendar(request):
    """Disconnect the user's Google Calendar."""
    try:
        # Delete the credentials for the user
        deleted, _ = GoogleCalendarCredentials.objects.filter(
            user=request.user
        ).delete()

        if deleted:
            return Response({"message": "Google Calendar disconnected successfully"})
        else:
            return Response({"message": "No Google Calendar connection found"})
    except Exception as e:
        logger.error(f"Error disconnecting Google Calendar: {str(e)}")
        return Response({"error": str(e)}, status=500)


@csrf_protect
@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_calendar_event(request, event_id):
    """Update an event in Google Calendar."""
    try:
        # Get the event data from the request
        event_data = request.data

        # Get the credentials for the user
        credentials_obj = GoogleCalendarCredentials.objects.filter(
            user=request.user
        ).first()
        if not credentials_obj:
            return Response({"error": "Google Calendar not connected"}, status=404)

        # Create credentials from stored token and refresh if needed
        credentials = credentials_obj.get_credentials()
        if isinstance(credentials, dict):
            return Response(credentials, status=401)

        # Get the calendar service
        service = build_calendar_service(credentials)

        # Get the calendar ID
        calendar_id = credentials_obj.calendar_id or "primary"

        # Get the existing event
        event = service.events().get(calendarId=calendar_id, eventId=event_id).execute()

        # Check if the event can be modified
        if not can_modify_event(event):
            return Response(
                {
                    "error": "You do not have permission to modify this event",
                    "editable": False,
                },
                status=401,
            )

        # Update the event properties from event_data
        # (Only update allowed fields)
        if "start" in event_data:
            event["start"] = event_data["start"]
        if "end" in event_data:
            event["end"] = event_data["end"]

        # Update the event
        updated_event = (
            service.events()
            .update(
                calendarId=calendar_id,
                eventId=event_id,
                body=event,
                sendUpdates="none",  # Don't send emails for updates from our app
            )
            .execute()
        )

        # Format for response
        formatted_event = format_event_for_fullcalendar(updated_event)
        return Response(formatted_event)

    except Exception as e:
        logger.error(f"Error updating calendar event: {str(e)}")
        return Response({"error": str(e)}, status=500)
