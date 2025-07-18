from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import logging
import email
from datetime import datetime
import re
from apps.integrations.google_calendar.models import GoogleCredentials
from apps.core.models import Task

logger = logging.getLogger(__name__)


def build_gmail_service(credentials):
    """Build the Gmail API service with the given credentials."""
    return build("gmail", "v1", credentials=credentials)


def get_emails(user, label_ids=None, max_results=20, page_token=None):
    """
    Get emails from the user's Gmail account.

    Args:
        user: The user to get emails for
        label_ids: List of label IDs to filter by (default: INBOX)
        max_results: Maximum number of results to return
        page_token: Token for pagination

    Returns:
        dict: Email data and next page token
    """
    # Get credentials
    credentials_obj = GoogleCredentials.objects.filter(user=user).first()
    if not credentials_obj:
        return {"error": "Google account not connected"}

    # Check if Gmail scope is granted
    if not credentials_obj.is_gmail_scope_granted():
        return {"error": "Gmail permissions not granted"}

    # Get credentials
    credentials = credentials_obj.get_credentials()
    if isinstance(credentials, dict) and "error" in credentials:
        return credentials

    # Build Gmail service
    try:
        service = build_gmail_service(credentials)
    except Exception as e:
        logger.error(f"Error building Gmail service: {str(e)}")
        return {"error": f"Error connecting to Gmail: {str(e)}"}

    # Default to INBOX if no labels specified
    if not label_ids:
        label_ids = ["INBOX"]

    # Get messages
    try:
        query = {
            "userId": "me",
            "labelIds": label_ids,
            "maxResults": max_results,
        }

        if page_token:
            query["pageToken"] = page_token

        messages_result = service.users().messages().list(**query).execute()

        # Get message details
        messages = messages_result.get("messages", [])
        emails = []

        for message in messages:
            try:
                msg = (
                    service.users()
                    .messages()
                    .get(userId="me", id=message["id"])
                    .execute()
                )
                email_data = format_email_for_frontend(msg)
                emails.append(email_data)
            except Exception as e:
                logger.error(f"Error fetching email {message['id']}: {str(e)}")
                continue

        return {"emails": emails, "nextPageToken": messages_result.get("nextPageToken")}
    except HttpError as error:
        logger.error(f"Gmail API error: {str(error)}")
        return {"error": f"Gmail API error: {str(error)}"}
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return {"error": f"Unexpected error: {str(e)}"}


def format_email_for_frontend(message):
    """Format a Gmail message for the frontend."""
    # Extract headers
    headers = {}
    for header in message["payload"]["headers"]:
        headers[header["name"].lower()] = header["value"]

    # Get snippet and body
    snippet = message.get("snippet", "")

    # Format email object
    email_data = {
        "id": message["id"],
        "threadId": message["threadId"],
        "sender": headers.get("from", "").split("<")[0].strip(),
        "senderEmail": extract_email_address(headers.get("from", "")),
        "subject": headers.get("subject", "(No subject)"),
        "preview": snippet,
        "time": format_date(headers.get("date", "")),
        "timestamp": parse_date_to_timestamp(headers.get("date", "")),
        "isStarred": "STARRED" in message.get("labelIds", []),
        "isRead": "UNREAD" not in message.get("labelIds", []),
        "hasAttachment": has_attachment(message),
        "labels": message.get("labelIds", []),
        "link": f"https://mail.google.com/mail/u/0/#inbox/{message['id']}",
    }

    return email_data


def extract_email_address(from_header):
    """Extract email address from From header."""
    if not from_header:
        return ""

    # Try to extract email address using regex
    match = re.search(r"<([^>]+)>", from_header)
    if match:
        return match.group(1)

    # If no angle brackets, assume the whole string is an email
    return from_header.strip()


def format_date(date_str):
    """Format date string for frontend display."""
    if not date_str:
        return ""

    try:
        # Parse the email date format
        dt = email.utils.parsedate_to_datetime(date_str)

        # Format based on how recent the email is
        now = datetime.now(dt.tzinfo)
        diff = now - dt

        if diff.days == 0:
            # Today, show time only
            return dt.strftime("%I:%M %p")
        elif diff.days < 7:
            # This week, show day name
            return dt.strftime("%a")
        else:
            # Older, show date
            return dt.strftime("%b %d")
    except Exception:
        # Fall back to original string if parsing fails
        return date_str


def parse_date_to_timestamp(date_str):
    """Parse date string to timestamp for sorting and client-side timezone conversion."""
    if not date_str:
        return 0

    try:
        # Parse the email date format to a datetime object
        dt = email.utils.parsedate_to_datetime(date_str)
        # Return UTC timestamp for consistent client-side timezone conversion
        return int(dt.timestamp())
    except Exception:
        return 0


def get_labels(user):
    """Get available Gmail labels for the user."""
    credentials_obj = GoogleCredentials.objects.filter(user=user).first()
    if not credentials_obj:
        return {"error": "Google account not connected"}

    # Check if Gmail scope is granted
    if not credentials_obj.is_gmail_scope_granted():
        return {"error": "Gmail permissions not granted"}

    # Get credentials
    credentials = credentials_obj.get_credentials()
    if isinstance(credentials, dict) and "error" in credentials:
        return credentials

    try:
        service = build_gmail_service(credentials)

        # Get labels
        results = service.users().labels().list(userId="me").execute()
        labels = results.get("labels", [])

        # Format labels for frontend
        formatted_labels = []
        for label in labels:
            # Include only system labels and user labels (exclude categories)
            if label["type"] == "system" or label["type"] == "user":
                formatted_labels.append({"id": label["id"], "name": label["name"]})

        return {"labels": formatted_labels}
    except HttpError as error:
        logger.error(f"Gmail API error: {str(error)}")
        return {"error": f"Gmail API error: {str(error)}"}
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return {"error": f"Unexpected error: {str(e)}"}


def has_attachment(message):
    """Check if message has attachments."""
    if "payload" not in message:
        return False

    # Check for parts with filename
    if "parts" in message["payload"]:
        for part in message["payload"]["parts"]:
            if part.get("filename") and part.get("filename") != "":
                return True

    return False


def toggle_star(user, message_id, starred=True):
    """Toggle star status for an email."""
    credentials_obj = GoogleCredentials.objects.filter(user=user).first()
    if not credentials_obj:
        return {"error": "Google account not connected"}

    # Check if Gmail scope is granted
    if not credentials_obj.is_gmail_scope_granted():
        return {"error": "Gmail permissions not granted"}

    # Get credentials
    credentials = credentials_obj.get_credentials()
    if isinstance(credentials, dict) and "error" in credentials:
        return credentials

    try:
        service = build_gmail_service(credentials)

        # Add or remove STARRED label
        if starred:
            service.users().messages().modify(
                userId="me", id=message_id, body={"addLabelIds": ["STARRED"]}
            ).execute()
        else:
            service.users().messages().modify(
                userId="me", id=message_id, body={"removeLabelIds": ["STARRED"]}
            ).execute()

        return {"success": True, "starred": starred}
    except HttpError as error:
        logger.error(f"Gmail API error: {str(error)}")
        return {"error": f"Gmail API error: {str(error)}"}
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return {"error": f"Unexpected error: {str(e)}"}


def mark_as_read(user, message_id, read=True):
    """Mark an email as read or unread."""
    credentials_obj = GoogleCredentials.objects.filter(user=user).first()
    if not credentials_obj:
        return {"error": "Google account not connected"}

    # Check if Gmail scope is granted
    if not credentials_obj.is_gmail_scope_granted():
        return {"error": "Gmail permissions not granted"}

    # Get credentials
    credentials = credentials_obj.get_credentials()
    if isinstance(credentials, dict) and "error" in credentials:
        return credentials

    try:
        service = build_gmail_service(credentials)

        # Add or remove UNREAD label
        if read:
            service.users().messages().modify(
                userId="me", id=message_id, body={"removeLabelIds": ["UNREAD"]}
            ).execute()
        else:
            service.users().messages().modify(
                userId="me", id=message_id, body={"addLabelIds": ["UNREAD"]}
            ).execute()

        return {"success": True, "read": read}
    except HttpError as error:
        logger.error(f"Gmail API error: {str(error)}")
        return {"error": f"Gmail API error: {str(error)}"}
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return {"error": f"Unexpected error: {str(e)}"}


def convert_to_task(user, message_id, task_data):
    """Convert an email to a task."""
    credentials_obj = GoogleCredentials.objects.filter(user=user).first()
    if not credentials_obj:
        return {"error": "Google account not connected"}

    # Check if Gmail scope is granted
    if not credentials_obj.is_gmail_scope_granted():
        return {"error": "Gmail permissions not granted"}

    # Get credentials
    credentials = credentials_obj.get_credentials()
    if isinstance(credentials, dict) and "error" in credentials:
        return credentials

    try:
        service = build_gmail_service(credentials)

        # Get email details
        msg = service.users().messages().get(userId="me", id=message_id).execute()
        email_data = format_email_for_frontend(msg)

        # Create task from email
        task = Task.objects.create(
            user=user,
            title=task_data.get("title", email_data["subject"]),
            description=task_data.get(
                "description",
                f"From: {email_data['sender']} ({email_data['senderEmail']})\n\n{email_data['preview']}\n\nView in Gmail: {email_data['link']}",
            ),
            status=task_data.get("status", "TODO"),
            column_date=task_data.get("column_date"),
            start_at=task_data.get("start_at"),
            end_at=task_data.get("end_at"),
            project=task_data.get("project", ""),
        )

        # Mark email as read if requested
        if task_data.get("mark_as_read", False):
            mark_as_read(user, message_id, True)

        return {
            "success": True,
            "task_id": task.id,
            "task": {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "status": task.status,
                "column_date": task.column_date,
                "start_at": task.start_at,
                "end_at": task.end_at,
                "project": task.project,
            },
        }
    except HttpError as error:
        logger.error(f"Gmail API error: {str(error)}")
        return {"error": f"Gmail API error: {str(error)}"}
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return {"error": f"Unexpected error: {str(e)}"}


def get_gmail_labels(user):
    """Get all Gmail labels for the user."""
    credentials_obj = GoogleCredentials.objects.filter(user=user).first()
    if not credentials_obj:
        return {"error": "Google account not connected"}

    # Check if Gmail scope is granted
    if not credentials_obj.is_gmail_scope_granted():
        return {"error": "Gmail permissions not granted"}

    # Get credentials
    credentials = credentials_obj.get_credentials()
    if isinstance(credentials, dict) and "error" in credentials:
        return credentials

    try:
        service = build_gmail_service(credentials)

        # Get all labels
        results = service.users().labels().list(userId="me").execute()
        labels = results.get("labels", [])

        # Format labels for frontend
        formatted_labels = []
        for label in labels:
            formatted_labels.append(
                {"id": label["id"], "name": label["name"], "type": label["type"]}
            )

        return {"labels": formatted_labels}
    except HttpError as error:
        logger.error(f"Gmail API error: {str(error)}")
        return {"error": f"Gmail API error: {str(error)}"}
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return {"error": f"Unexpected error: {str(e)}"}
