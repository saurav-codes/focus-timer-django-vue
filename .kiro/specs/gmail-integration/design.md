# Gmail Integration Design Document

## Overview

The Gmail Integration feature will allow users to view and interact with their Gmail inbox directly within the Focus Timer application. This integration leverages the Gmail API to fetch emails from the user's "Primary" and "Important" inboxes and display them in the application sidebar. Users can view email details, star/unstar emails, mark them as read/unread, and convert emails to tasks.

## Architecture

The Gmail integration will extend the existing Google Calendar integration architecture, reusing the authentication flow and credential storage while adding Gmail-specific functionality:

### Backend Components

1. **Extended Google Credentials Model**: Update the existing GoogleCalendarCredentials model to support Gmail scopes
2. **Gmail API Service**: Handle communication with Gmail API
3. **WebSocket Consumer**: Push real-time email updates to frontend
4. **REST API Endpoints**: Handle authentication, settings, and email actions

### Frontend Components

1. **Gmail Integration Vue Component**: Display emails in sidebar
2. **Gmail Store**: Manage email state with Pinia
3. **Email Detail Modal**: Show full email content
4. **Email-to-Task Conversion UI**: Interface for creating tasks from emails

## Components and Interfaces

### Backend

#### Extended Google Credentials Model

We'll extend the existing GoogleCalendarCredentials model to support Gmail functionality:

```python
# Update the existing model
class GoogleCredentials(models.Model):
    """
    Model to store Google OAuth2 credentials for users.
    Supports multiple Google services (Calendar, Gmail, etc.)
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="google_credentials",
    )
    token = models.JSONField(help_text="OAuth2 token and refresh token information")
    calendar_id = models.CharField(
        max_length=255, blank=True, null=True, help_text="Primary Google Calendar ID"
    )
    connected_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Gmail-specific fields
    gmail_sync_enabled = models.BooleanField(default=True)
    gmail_sync_labels = models.JSONField(default=list)  # Store list of labels to sync
    gmail_last_sync = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Google Credentials'
        verbose_name_plural = 'Google Credentials'
```

#### Gmail API Service

The Gmail API service will handle:
- Authentication and token refresh (reusing existing mechanisms)
- Fetching emails from specified labels
- Performing actions (star/unstar, read/unread)
- Webhook registration for real-time updates

```python
# gmail_service.py
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from .models import GoogleCredentials

def build_gmail_service(credentials):
    """Build the Gmail API service with the given credentials."""
    return build('gmail', 'v1', credentials=credentials)

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

    # Get credentials
    credentials = credentials_obj.get_credentials()
    if isinstance(credentials, dict) and "error" in credentials:
        return credentials

    # Build Gmail service
    service = build_gmail_service(credentials)

    # Default to INBOX if no labels specified
    if not label_ids:
        label_ids = ['INBOX']

    # Get messages
    query = {
        'userId': 'me',
        'labelIds': label_ids,
        'maxResults': max_results,
    }

    if page_token:
        query['pageToken'] = page_token

    messages_result = service.users().messages().list(**query).execute()

    # Get message details
    messages = messages_result.get('messages', [])
    emails = []

    for message in messages:
        msg = service.users().messages().get(userId='me', id=message['id']).execute()
        email = format_email_for_frontend(msg)
        emails.append(email)

    return {
        'emails': emails,
        'nextPageToken': messages_result.get('nextPageToken')
    }

def format_email_for_frontend(message):
    """Format a Gmail message for the frontend."""
    # Extract headers
    headers = {}
    for header in message['payload']['headers']:
        headers[header['name'].lower()] = header['value']

    # Get snippet and body
    snippet = message.get('snippet', '')

    # Format email object
    email = {
        'id': message['id'],
        'threadId': message['threadId'],
        'sender': headers.get('from', '').split('<')[0].strip(),
        'senderEmail': extract_email_address(headers.get('from', '')),
        'subject': headers.get('subject', '(No subject)'),
        'preview': snippet,
        'time': format_date(headers.get('date', '')),
        'timestamp': parse_date_to_timestamp(headers.get('date', '')),
        'isStarred': 'STARRED' in message.get('labelIds', []),
        'isRead': 'UNREAD' not in message.get('labelIds', []),
        'hasAttachment': has_attachment(message),
        'labels': message.get('labelIds', []),
        'link': f"https://mail.google.com/mail/u/0/#inbox/{message['id']}"
    }

    return email

def toggle_star(user, message_id, starred=True):
    """Toggle star status for an email."""
    # Implementation details...

def mark_as_read(user, message_id, read=True):
    """Mark an email as read or unread."""
    # Implementation details...

def convert_to_task(user, message_id, task_data):
    """Convert an email to a task."""
    # Implementation details...
```

#### REST API Endpoints

- `GET /api/integrations/google/auth/`: Initiate OAuth flow (reuse existing)
- `GET /api/integrations/google/auth/callback/`: OAuth callback handler (reuse existing)
- `GET /api/integrations/google/gmail/emails/`: List emails
- `PUT /api/integrations/google/gmail/emails/{id}/star/`: Star/unstar email
- `PUT /api/integrations/google/gmail/emails/{id}/read/`: Mark email as read/unread
- `POST /api/integrations/google/gmail/emails/{id}/convert-to-task/`: Convert email to task
- `GET /api/integrations/google/gmail/settings/`: Get integration settings
- `PUT /api/integrations/google/gmail/settings/`: Update integration settings
- `DELETE /api/integrations/google/gmail/disconnect/`: Disconnect Gmail integration

```python
# views.py
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_gmail_emails(request):
    """Get emails from the user's Gmail account."""
    # Get query parameters
    label_ids = request.GET.getlist('labelIds', ['INBOX'])
    max_results = int(request.GET.get('maxResults', 20))
    page_token = request.GET.get('pageToken')

    # Get emails
    result = get_emails(
        user=request.user,
        label_ids=label_ids,
        max_results=max_results,
        page_token=page_token
    )

    if 'error' in result:
        return Response({'error': result['error']}, status=400)

    return Response(result)
```

#### WebSocket Consumer

```python
class GmailConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        if not self.user.is_authenticated:
            await self.close()
            return

        self.room_name = f"gmail_{self.user.id}"
        self.room_group_name = f"gmail_{self.user.id}"

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def email_update(self, event):
        """Send email updates to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'email_update',
            'data': event['data']
        }))
```

### Frontend

#### Gmail Store (Pinia)

```javascript
// stores/gmailStore.js
import { defineStore } from 'pinia'
import axios from 'axios'

export const useGmailStore = defineStore('gmail', {
  state: () => ({
    emails: [],
    isConnected: false,
    isLoading: false,
    error: null,
    settings: {
      syncLabels: ['INBOX', 'IMPORTANT'],
      syncFrequency: 5 // minutes
    },
    pagination: {
      nextPageToken: null,
      hasMore: false
    }
  }),

  actions: {
    async fetchEmails() {
      this.isLoading = true
      try {
        const response = await axios.get('/api/integrations/google/gmail/emails/')
        this.emails = response.data.emails
        this.pagination.nextPageToken = response.data.nextPageToken
        this.pagination.hasMore = !!response.data.nextPageToken
        this.isConnected = true
      } catch (error) {
        this.error = error.response?.data?.message || 'Failed to fetch emails'
        this.isConnected = false
      } finally {
        this.isLoading = false
      }
    },

    async loadMoreEmails() {
      if (!this.pagination.hasMore) return

      this.isLoading = true
      try {
        const response = await axios.get('/api/integrations/google/gmail/emails/', {
          params: { pageToken: this.pagination.nextPageToken }
        })
        this.emails = [...this.emails, ...response.data.emails]
        this.pagination.nextPageToken = response.data.nextPageToken
        this.pagination.hasMore = !!response.data.nextPageToken
      } catch (error) {
        this.error = error.response?.data?.message || 'Failed to load more emails'
      } finally {
        this.isLoading = false
      }
    },

    async toggleStar(emailId) {
      const email = this.emails.find(e => e.id === emailId)
      if (!email) return

      const originalStarred = email.isStarred
      // Optimistic update
      email.isStarred = !email.isStarred

      try {
        await axios.put(`/api/integrations/google/gmail/emails/${emailId}/star/`, {
          starred: email.isStarred
        })
      } catch (error) {
        // Revert on failure
        email.isStarred = originalStarred
        this.error = error.response?.data?.message || 'Failed to update star status'
      }
    },

    async markAsRead(emailId, read = true) {
      const email = this.emails.find(e => e.id === emailId)
      if (!email) return

      const originalReadStatus = email.isRead
      // Optimistic update
      email.isRead = read

      try {
        await axios.put(`/api/integrations/google/gmail/emails/${emailId}/read/`, {
          read: email.isRead
        })
      } catch (error) {
        // Revert on failure
        email.isRead = originalReadStatus
        this.error = error.response?.data?.message || 'Failed to update read status'
      }
    },

    async convertToTask(emailId, taskDetails) {
      try {
        await axios.post(`/api/integrations/google/gmail/emails/${emailId}/convert-to-task/`, taskDetails)
        return true
      } catch (error) {
        this.error = error.response?.data?.message || 'Failed to convert email to task'
        return false
      }
    },

    async updateSettings(settings) {
      try {
        await axios.put('/api/integrations/google/gmail/settings/', settings)
        this.settings = { ...this.settings, ...settings }
        return true
      } catch (error) {
        this.error = error.response?.data?.message || 'Failed to update settings'
        return false
      }
    },

    async disconnect() {
      try {
        await axios.delete('/api/integrations/google/gmail/disconnect/')
        this.isConnected = false
        this.emails = []
        return true
      } catch (error) {
        this.error = error.response?.data?.message || 'Failed to disconnect'
        return false
      }
    },

    // WebSocket handlers
    handleEmailUpdate(data) {
      const index = this.emails.findIndex(e => e.id === data.id)
      if (index >= 0) {
        // Update existing email
        this.emails[index] = { ...this.emails[index], ...data }
      } else {
        // Add new email at the beginning
        this.emails.unshift(data)
      }
    }
  }
})
```

#### Gmail Integration Component

The main component will display emails from the Gmail API and provide interaction options. It will include:
- Connection status and setup UI
- Email list with infinite scrolling
- Email interaction buttons (star, mark as read)
- Email detail view
- Email-to-task conversion UI

## Data Models

### Email Object Structure

```javascript
{
  id: String,           // Gmail message ID
  threadId: String,     // Gmail thread ID
  sender: String,       // Sender name
  senderEmail: String,  // Sender email address
  subject: String,      // Email subject
  preview: String,      // Short preview of content
  snippet: String,      // Longer snippet of content
  body: String,         // Full HTML body (lazy loaded)
  time: String,         // Formatted time (e.g., "10:23 AM")
  timestamp: Number,    // Unix timestamp for sorting
  isStarred: Boolean,   // Star status
  isRead: Boolean,      // Read status
  hasAttachment: Boolean, // Attachment indicator
  labels: Array,        // Gmail labels
  link: String          // Link to open in Gmail
}
```

### Settings Object Structure

```javascript
{
  syncLabels: Array,    // Gmail labels to sync
  syncFrequency: Number // Sync frequency in minutes
}
```

## OAuth Scope Management

To support both Google Calendar and Gmail integrations with a single OAuth flow:

1. **Unified Scopes**: Update the OAuth scopes to include both Calendar and Gmail:
   ```python
   SCOPES = [
       # Calendar scopes
       "https://www.googleapis.com/auth/calendar.events",
       "https://www.googleapis.com/auth/calendar.settings.readonly",
       "https://www.googleapis.com/auth/calendar.readonly",
       # Gmail scopes
       "https://www.googleapis.com/auth/gmail.readonly",
       "https://www.googleapis.com/auth/gmail.modify",
   ]
   ```

2. **Incremental Authorization**: For users who already connected Google Calendar:
   - Detect missing Gmail scopes during API calls
   - Prompt for additional permissions using incremental authorization
   - Preserve existing tokens while adding new scopes

3. **Selective Disconnection**: Allow users to disconnect Gmail integration while keeping Calendar integration active by:
   - Removing Gmail-specific scopes from the token
   - Updating the credentials model to disable Gmail sync
   - Preserving Calendar functionality

## Error Handling

### Frontend Error Handling

- Display connection errors with retry option
- Show loading states during API operations
- Implement optimistic updates with rollback on failure
- Provide clear error messages for failed operations

### Backend Error Handling

- Handle Gmail API rate limits with exponential backoff
- Implement token refresh logic for expired OAuth tokens
- Log detailed error information for debugging
- Return appropriate HTTP status codes and error messages

## Testing Strategy

### Frontend Tests

- Unit tests for Gmail store actions and mutations
- Component tests for Gmail integration UI
- Integration tests for email-to-task conversion flow

### Backend Tests

- Unit tests for Gmail API service methods
- Integration tests for API endpoints
- Authentication flow tests
- WebSocket communication tests

### Manual Testing Scenarios

1. Connect Google account with various permission combinations
2. Test incremental authorization for existing Calendar users
3. Verify email display and pagination
4. Test star/unstar functionality
5. Test read/unread functionality
6. Test email-to-task conversion
7. Verify real-time updates via WebSockets
8. Test selective disconnection of Gmail while preserving Calendar integration
