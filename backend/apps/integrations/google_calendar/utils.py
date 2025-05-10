import json
import datetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from django.conf import settings

# Define the scopes needed for Google Calendar
# Read-only is used for the initial integration
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

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
            "redirect_uris": [redirect_uri or settings.GOOGLE_REDIRECT_URI]
        }
    }

    flow = Flow.from_client_config(
        client_config,
        scopes=SCOPES,
        redirect_uri=redirect_uri or settings.GOOGLE_REDIRECT_URI,
        state=state
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
        token=token_data.get('token'),
        refresh_token=token_data.get('refresh_token'),
        token_uri=token_data.get('token_uri', 'https://oauth2.googleapis.com/token'),
        client_id=token_data.get('client_id', settings.GOOGLE_CLIENT_ID),
        client_secret=token_data.get('client_secret', settings.GOOGLE_CLIENT_SECRET),
        scopes=token_data.get('scopes', SCOPES)
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
            credentials.refresh(Request())

            # Convert to token dict
            token_data = {
                'token': credentials.token,
                'refresh_token': credentials.refresh_token,
                'token_uri': credentials.token_uri,
                'client_id': credentials.client_id,
                'client_secret': credentials.client_secret,
                'scopes': credentials.scopes,
                'expiry': credentials.expiry.isoformat() if credentials.expiry else None
            }

            return credentials, token_data
        else:
            raise ValueError("No refresh token available. User needs to re-authenticate.")

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
        return build('calendar', 'v3', credentials=credentials)
    except Exception as e:
        raise Exception(f"Failed to build Google Calendar service: {str(e)}")

def format_event_for_fullcalendar(event):
    """
    Format a Google Calendar event for FullCalendar.

    Args:
        event (dict): Google Calendar event.

    Returns:
        dict: FullCalendar compatible event object.
    """
    start = event['start'].get('dateTime', event['start'].get('date'))
    end = event['end'].get('dateTime', event['end'].get('date'))

    return {
        'id': f"google-{event['id']}",
        'title': event.get('summary', '(No title)'),
        'start': start,
        'end': end,
        'allDay': 'date' in event['start'],
        'backgroundColor': event.get('colorId', '#4285F4'),  # Default Google blue
        'borderColor': event.get('colorId', '#4285F4'),
        'textColor': '#FFFFFF',
        'extendedProps': {
            'description': event.get('description', ''),
            'location': event.get('location', ''),
            'source': 'google',
            'htmlLink': event.get('htmlLink', ''),
            'organizer': event.get('organizer', {}).get('email', ''),
            'attendees': [a.get('email') for a in event.get('attendees', [])],
            'status': event.get('status', ''),
            'recurringEventId': event.get('recurringEventId', None)
        }
    }

def get_event_time_boundaries(event):
    """
    Extract start and end times from a Google Calendar event.

    Args:
        event (dict): Google Calendar event.

    Returns:
        tuple: (start_datetime, end_datetime) - Start and end datetimes.
    """
    start_str = event['start'].get('dateTime', event['start'].get('date'))
    end_str = event['end'].get('dateTime', event['end'].get('date'))

    # Parse the strings to datetime objects
    if 'T' in start_str:  # dateTime format (e.g., "2023-11-15T10:00:00Z")
        start_dt = datetime.datetime.fromisoformat(start_str.replace('Z', '+00:00'))
    else:  # date format (e.g., "2023-11-15")
        start_dt = datetime.datetime.fromisoformat(f"{start_str}T00:00:00")

    if 'T' in end_str:
        end_dt = datetime.datetime.fromisoformat(end_str.replace('Z', '+00:00'))
    else:
        end_dt = datetime.datetime.fromisoformat(f"{end_str}T23:59:59")

    return start_dt, end_dt

def handle_calendar_api_error(error, default_message="An error occurred with the Calendar API"):
    """
    Handle Google Calendar API errors.

    Args:
        error (Exception): The exception that occurred.
        default_message (str): Default message to return if error can't be parsed.

    Returns:
        dict: Error details including message, status, and reason.
    """
    error_details = {
        'message': default_message,
        'status': 500,
        'reason': str(error)
    }

    if isinstance(error, HttpError):
        error_details['status'] = error.resp.status
        try:
            error_content = json.loads(error.content.decode('utf-8'))
            error_details['message'] = error_content.get('error', {}).get('message', default_message)
            error_details['reason'] = error_content.get('error', {}).get('errors', [{}])[0].get('reason', 'unknown')
        except (json.JSONDecodeError, KeyError, IndexError):
            error_details['message'] = error.reason if hasattr(error, 'reason') else default_message

    return error_details
