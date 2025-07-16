import json
import datetime
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request as GoogleRequest
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from django.conf import settings


# Define the scopes needed for Google Calendar
# Read-only is used for the initial integration
SCOPES = [
    "https://www.googleapis.com/auth/calendar.events",  # Manage events
    "https://www.googleapis.com/auth/calendar.settings.readonly",
    "https://www.googleapis.com/auth/calendar.readonly",  # Read calendar settings
]

# Full access scope for future use if needed
# SCOPES = ['https://www.googleapis.com/auth/calendar']


def create_flow(redirect_uri=None, state=None):
    """
    Create an OAuth2 flow for Google Calendar authorization.

    Args:
        redirect_uri (str, optional): Redirect URI for the OAuth2 flow.
        state (str, optional): State parameter for CSRF protection.

    Returns:
        Flow: OAuth2 flow object.
    """
    client_config = {
        "web": {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [redirect_uri or settings.GOOGLE_REDIRECT_URI],
        }
    }

    flow = Flow.from_client_config(
        client_config,
        scopes=SCOPES,
        redirect_uri=redirect_uri or settings.GOOGLE_REDIRECT_URI,
        state=state,
    )

    return flow


def credentials_from_dict(token_data):
    """
    Create a Google OAuth2 Credentials object from token dictionary.

    Args:
        token_data (dict): Dictionary containing token information.

    Returns:
        Credentials: Google OAuth2 credentials object.
    """
    return Credentials(
        token=token_data.get("token"),
        refresh_token=token_data.get("refresh_token"),
        token_uri=token_data.get("token_uri", "https://oauth2.googleapis.com/token"),
        client_id=token_data.get("client_id", settings.GOOGLE_CLIENT_ID),
        client_secret=token_data.get("client_secret", settings.GOOGLE_CLIENT_SECRET),
        scopes=token_data.get("scopes", SCOPES),
    )


def refresh_credentials(credentials):
    """
    Refresh Google OAuth2 credentials if expired.

    Args:
        credentials (Credentials): Google OAuth2 credentials object.

    Returns:
        tuple: (Credentials, dict) - Refreshed credentials and token data.
    """
    if not credentials.valid:
        if credentials.refresh_token:
            credentials.refresh(GoogleRequest())

            # Convert to token dict
            token_data = {
                "token": credentials.token,
                "refresh_token": credentials.refresh_token,
                "token_uri": credentials.token_uri,
                "client_id": credentials.client_id,
                "client_secret": credentials.client_secret,
                "scopes": credentials.scopes,
                "expiry": credentials.expiry.isoformat()
                if credentials.expiry
                else None,
            }

            return credentials, token_data
        else:
            raise ValueError(
                "No refresh token available. User needs to re-authenticate."
            )

    return credentials, None


def build_calendar_service(credentials):
    """
    Build the Google Calendar API service with the given credentials.

    Args:
        credentials (Credentials): Google OAuth2 credentials.

    Returns:
        Resource: Google Calendar API service.
    """
    try:
        return build("calendar", "v3", credentials=credentials)
    except Exception as e:
        raise Exception(f"Failed to build Google Calendar service: {str(e)}")


def _format_person_data(person_obj):
    """
    Format person data (creator/organizer) with fallbacks.

    Args:
        person_obj (dict): Person object from Google Calendar API.

    Returns:
        dict: Formatted person data with fallbacks.
    """
    if not person_obj:
        return {}

    return {
        "id": person_obj.get("id", ""),
        "email": person_obj.get("email", ""),
        "displayName": person_obj.get("displayName", person_obj.get("email", "")),
        "self": person_obj.get("self", False),
    }


def _format_attendees_data(attendees_list):
    """
    Format attendee data with comprehensive information and fallbacks.

    Args:
        attendees_list (list): List of attendee objects from Google Calendar API.

    Returns:
        list: List of formatted attendee objects.
    """
    if not attendees_list:
        return []

    formatted_attendees = []

    for attendee in attendees_list:
        if not isinstance(attendee, dict):
            continue

        # Use email as fallback for displayName
        display_name = attendee.get("displayName", "")
        email = attendee.get("email", "")

        if not display_name and email:
            display_name = email
        elif not display_name and not email:
            continue  # Skip attendees with no identifying information

        formatted_attendee = {
            "id": attendee.get("id", ""),
            "email": email,
            "displayName": display_name,
            "organizer": attendee.get("organizer", False),
            "self": attendee.get("self", False),
            "resource": attendee.get("resource", False),
            "optional": attendee.get("optional", False),
            "responseStatus": attendee.get("responseStatus", "needsAction"),
            "comment": attendee.get("comment", ""),
            "additionalGuests": attendee.get("additionalGuests", 0),
        }

        formatted_attendees.append(formatted_attendee)

    return formatted_attendees


def _format_conference_data(conference_data):
    """
    Format conference data with entry points and meeting information.

    Args:
        conference_data (dict): Conference data from Google Calendar API.

    Returns:
        dict: Formatted conference data with fallbacks.
    """
    if not conference_data:
        return {}

    # Format entry points
    entry_points = []
    for entry_point in conference_data.get("entryPoints", []):
        if not isinstance(entry_point, dict):
            continue

        formatted_entry_point = {
            "entryPointType": entry_point.get("entryPointType", ""),
            "uri": entry_point.get("uri", ""),
            "label": entry_point.get("label", ""),
            "meetingCode": entry_point.get("meetingCode", ""),
            "accessCode": entry_point.get("accessCode", ""),
            "pin": entry_point.get("pin", ""),
            "passcode": entry_point.get("passcode", ""),
            "password": entry_point.get("password", ""),
        }
        entry_points.append(formatted_entry_point)

    # Format conference solution
    conference_solution = {}
    solution_data = conference_data.get("conferenceSolution", {})
    if solution_data:
        conference_solution = {
            "key": solution_data.get("key", {}),
            "name": solution_data.get("name", ""),
            "iconUri": solution_data.get("iconUri", ""),
        }

    return {
        "entryPoints": entry_points,
        "conferenceSolution": conference_solution,
        "conferenceId": conference_data.get("conferenceId", ""),
        "signature": conference_data.get("signature", ""),
        "notes": conference_data.get("notes", ""),
    }


def format_event_for_fullcalendar(event):
    """
    Format a Google Calendar event for FullCalendar with comprehensive event data.

    This function transforms Google Calendar API events into FullCalendar-compatible
    objects while preserving all essential information users need.

    Args:
        event (dict): Google Calendar event from the API.

    Returns:
        dict: FullCalendar compatible event object with comprehensive data.

    Raises:
        ValueError: If event is missing required fields (id, start).
    """
    # Validate required fields
    if not event:
        raise ValueError("Event data is required")

    if not event.get("id"):
        raise ValueError("Event must have an id field")

    if not event.get("start"):
        raise ValueError("Event must have a start field")

    # Extract start and end times with error handling
    try:
        start_obj = event["start"]
        end_obj = event.get("end", {})

        # Get start time (dateTime for timed events, date for all-day events)
        start = start_obj.get("dateTime") or start_obj.get("date")
        if not start:
            raise ValueError("Event start must have either dateTime or date")

        # Get end time with fallback
        end = None
        if end_obj:
            end = end_obj.get("dateTime") or end_obj.get("date")

        # Determine if event is all-day
        all_day = "date" in start_obj and "dateTime" not in start_obj

    except (KeyError, TypeError) as e:
        raise ValueError(f"Invalid event date structure: {str(e)}")

    # Get color information with fallbacks
    color_id = event.get("colorId")
    background_color = "#4285F4"  # Default Google blue
    border_color = "#4285F4"

    # Map common Google Calendar color IDs to hex colors
    color_map = {
        "1": "#7986CB",  # Lavender
        "2": "#33B679",  # Sage
        "3": "#8E24AA",  # Grape
        "4": "#E67C73",  # Flamingo
        "5": "#F6BF26",  # Banana
        "6": "#F4511E",  # Tangerine
        "7": "#039BE5",  # Peacock
        "8": "#616161",  # Graphite
        "9": "#3F51B5",  # Blueberry
        "10": "#0B8043",  # Basil
        "11": "#D50000",  # Tomato
    }

    if color_id and color_id in color_map:
        background_color = color_map[color_id]
        border_color = color_map[color_id]

    # Build FullCalendar event object following exact specification
    fullcalendar_event = {
        # Required FullCalendar fields
        "id": str(event["id"]),  # Ensure string type
        "title": event.get("summary", "(No title)"),
        "start": start,
        "allDay": all_day,
        # Optional FullCalendar styling fields
        "backgroundColor": background_color,
        "borderColor": border_color,
        "textColor": "#FFFFFF",
    }

    # Add end time if available
    if end:
        fullcalendar_event["end"] = end

    # All Google Calendar-specific data goes in extendedProps
    fullcalendar_event["extendedProps"] = {
        # Essential event details
        "description": event.get("description", ""),
        "location": event.get("location", ""),
        "status": event.get("status", "confirmed"),
        "htmlLink": event.get("htmlLink", ""),
        # People information - comprehensive attendee data
        "creator": _format_person_data(event.get("creator", {})),
        "organizer": _format_person_data(event.get("organizer", {})),
        "attendees": _format_attendees_data(event.get("attendees", [])),
        # Meeting/Conference information - essential for remote work
        "hangoutLink": event.get("hangoutLink", ""),
        "conferenceData": _format_conference_data(event.get("conferenceData", {})),
        # Time metadata - timestamps in ISO format
        "created": event.get("created", ""),
        "updated": event.get("updated", ""),
        # Event properties
        "transparency": event.get("transparency", "opaque"),
        "visibility": event.get("visibility", "default"),
        "eventType": event.get("eventType", "default"),
        # Recurrence information - helps users understand event patterns
        "recurringEventId": event.get("recurringEventId", ""),
        "recurrence": event.get("recurrence", []),
        "originalStartTime": event.get("originalStartTime", {}),
        # Additional useful features
        "reminders": event.get("reminders", {}),
        "attachments": event.get("attachments", []),
        # Privacy and access
        "guestsCanModify": event.get("guestsCanModify", False),
        "guestsCanInviteOthers": event.get("guestsCanInviteOthers", True),
        "guestsCanSeeOtherGuests": event.get("guestsCanSeeOtherGuests", True),
        # Source identification
        "source": "google",
        # Raw Google Calendar data for debugging/advanced use
        "googleEventId": event.get("id", ""),
        "etag": event.get("etag", ""),
    }

    return fullcalendar_event


def get_event_time_boundaries(event):
    """
    Extract start and end times from a Google Calendar event.

    Args:
        event (dict): Google Calendar event.

    Returns:
        tuple: (start_datetime, end_datetime) - Start and end datetimes.
    """
    start_str = event["start"].get("dateTime", event["start"].get("date"))
    end_str = event["end"].get("dateTime", event["end"].get("date"))

    # Parse the strings to datetime objects
    if "T" in start_str:  # dateTime format (e.g., "2023-11-15T10:00:00Z")
        start_dt = datetime.datetime.fromisoformat(start_str.replace("Z", "+00:00"))
    else:  # date format (e.g., "2023-11-15")
        start_dt = datetime.datetime.fromisoformat(f"{start_str}T00:00:00")

    if "T" in end_str:
        end_dt = datetime.datetime.fromisoformat(end_str.replace("Z", "+00:00"))
    else:
        end_dt = datetime.datetime.fromisoformat(f"{end_str}T23:59:59")

    return start_dt, end_dt


def handle_calendar_api_error(
    error, default_message="An error occurred with the Calendar API"
):
    """
    Handle Google Calendar API errors.

    Args:
        error (Exception): The exception that occurred.
        default_message (str): Default message to return if error can't be parsed.

    Returns:
        dict: Error details including message, status, and reason.
    """
    error_details = {"message": default_message, "status": 500, "reason": str(error)}

    if isinstance(error, HttpError):
        error_details["status"] = error.resp.status
        try:
            error_content = json.loads(error.content.decode("utf-8"))
            error_details["message"] = error_content.get("error", {}).get(
                "message", default_message
            )
            error_details["reason"] = (
                error_content.get("error", {})
                .get("errors", [{}])[0]
                .get("reason", "unknown")
            )
        except (json.JSONDecodeError, KeyError, IndexError):
            error_details["message"] = (
                error.reason if hasattr(error, "reason") else default_message
            )

    return error_details


def can_modify_event(event: dict):
    """Check if the authenticated user can modify this Google Calendar event."""
    # Self-created events (you're the organizer)
    if event.get("organizer", {}).get("self", False):
        return True

    # Events where guests can modify is enabled
    if event.get("guestsCanModify", False):
        return True

    return False
