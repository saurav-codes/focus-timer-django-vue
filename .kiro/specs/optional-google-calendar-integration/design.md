# Design Document

## Overview

This design outlines the refactoring needed to make Google Calendar integration optional in the Focus Timer application. Currently, users cannot use the calendar functionality without connecting Google Calendar, which creates an unnecessary barrier. The solution will decouple basic calendar functionality from Google Calendar integration while preserving all existing features for connected users.

The design focuses on conditional logic based on connection status, efficient resource management, and clear user experience indicators.

## Architecture

### Current Issues Analysis

1. **Forced Integration**: Calendar component only renders when Google Calendar is connected
2. **Unnecessary API Calls**: Backend attempts Google Calendar operations regardless of connection status
3. **WebSocket Inefficiency**: Google Calendar WebSocket connections are established even for unconnected users
4. **Poor User Experience**: No clear indication of optional vs required integration
5. **Resource Waste**: Polling and API calls happen even when user hasn't connected Google Calendar

### Proposed Architecture

The solution implements a layered conditional approach:

1. **Connection Status Layer**: Centralized connection status management
2. **Conditional Rendering Layer**: UI components adapt based on connection status
3. **Selective API Layer**: Backend operations only execute when appropriate
4. **Resource Management Layer**: Efficient WebSocket and polling management

## Components and Interfaces

### 1. Frontend: Enhanced Calendar Store

**File**: `frontend-vue/src/stores/calendarStore.js`

The calendar store needs to be updated to handle optional Google Calendar integration:

```javascript
export const useCalendarStore = defineStore('calendar', () => {
  // ... existing code ...

  // New computed property for connection status
  const isGoogleConnected = computed(() => isGoogleConnected.value)

  // Modified fetchGcalTask to check connection status
  function fetchGcalTask(date_str = '') {
    // Only fetch if Google Calendar is connected
    if (!isGoogleConnected.value) {
      console.log('Google Calendar not connected, skipping fetch')
      return
    }

    if (!date_str) {
      const today = new Date()
      date_str = getDateStrFromDateObj(today)
    }
    console.log('fetch gcal task with date -', date_str)
    _sendActionToGcalWebsocket('fetch_gcal_task_from_dt', { date_str: date_str })
  }

  // Modified initGcalWs to check connection status
  function initGcalWs() {
    if (!isGoogleConnected.value) {
      console.log('Google Calendar not connected, skipping WebSocket initialization')
      return
    }

    const auth = useAuthStore()
    auth.verify_auth()
    if (auth.isAuthenticated) {
      console.info('user is authenticated opening gcal ws')
      gcalWsOpen()
    }
  }

  // ... rest of existing code ...
})
```

### 2. Frontend: Updated Calendar Integration Component

**File**: `frontend-vue/src/components/sidebar/integrations/CalendarIntegration.vue`

Key changes to the component:

```vue
<template>
  <div class="calendar-integration">
    <div class="integration-header">
      <div class="left-header">
        <h3>
          <LucideCalendar :size="14" />
          Calendar
        </h3>
        <div class="date-display">
          <!-- Navigation controls -->
        </div>
      </div>

      <!-- Connection status indicators -->
      <div class="connection-controls">
        <Popper v-if="isConnected" arrow content="Disconnect Google Calendar" :show="showPopper">
          <LucideUnlink
            class="disconnect-button"
            :class="{ 'disabled-div': isLoading }"
            :size="14"
            @click="disconnectGoogleCalendar" />
        </Popper>

        <Popper v-else arrow content="Connect Google Calendar" :show="showConnectPopper">
          <LucideLink
            class="connect-button-icon"
            :class="{ 'disabled-div': isLoading }"
            :size="14"
            @click="connectGoogleCalendar" />
        </Popper>
      </div>
    </div>

    <!-- Always show calendar, regardless of Google connection -->
    <div class="calendar-container">
      <div v-if="isLoading" class="loading">
        <div class="spinner" />
        <span>Loading...</span>
      </div>

      <!-- FullCalendar always renders -->
      <FullCalendar v-else ref="calendarRef" :options="calendarOptions" />
    </div>

    <!-- Modals -->
    <TaskEditModal
      v-if="activeTask"
      :task="activeTask"
      :is-open="isEditModalOpen"
      @close-modal="closeEditModal"
      @task-updated="handleTaskUpdated"
      @task-archived="handleTaskArchived"
      @task-deleted="handleTaskDeleted" />

    <ReadOnlyModal
      v-if="activeEvent"
      :event="activeEvent"
      :is-open="isReadOnlyModalOpen"
      @close-modal="closeReadOnlyModal" />
  </div>
</template>

<script setup>
// ... existing imports ...

// Modified onMounted to not block calendar rendering
onMounted(async () => {
  isLoading.value = true

  // Check connection status but don't block calendar functionality
  isConnected.value = await calendarStore.checkGoogleConnection()

  // Only initialize Google Calendar WebSocket if connected
  if (isConnected.value) {
    calendarStore.initGcalWs()
  }

  // Initialize draggable for task dropping (works regardless of Google connection)
  draggableInstance.value = new ThirdPartyDraggable(document.body, {
    itemSelector: '.task-item',
    mirrorSelector: '.task-item',
    eventData: function (eventEl) {
      if (eventEl.dataset.event) {
        const eventData = JSON.parse(eventEl.dataset.event)
        return { ...eventData }
      }
      return null
    },
  })

  // Watch for calendar errors
  watch(calendarError, (new_error) => {
    if (new_error) {
      alert(new_error)
      calendarStore.error = null
    }
  }, { deep: true })

  isLoading.value = false

  // Only start polling if Google Calendar is connected
  if (isConnected.value) {
    const { pause } = useIntervalFn(() => {
      if (calendarRef.value) {
        calendarStore.fetchGcalTask(getDateStrFromDateObj(currentDate.value))
      }
    }, 5 * 60 * 1000)
    stopPolling = pause
  }
})

// Modified navigation functions to conditionally fetch Google events
function prev() {
  calendarRef.value?.getApi().prev()
  const leftMostColDt = taskStore.kanbanColumns[0].date
  leftMostColDt.setHours(0,0,0,0)
  if (currentDate.value < leftMostColDt) {
    taskStore.addEarlierColumnsWs(3)
  }

  // Only fetch Google Calendar events if connected
  if (isConnected.value && currentDate.value) {
    const dt = getDateStrFromDateObj(currentDate.value)
    calendarStore.fetchGcalTask(dt)
  }
}

function next() {
  calendarRef.value?.getApi().next()
  const rightMostColDt = taskStore.kanbanColumns[taskStore.kanbanColumns.length - 1].date
  rightMostColDt.setHours(0,0,0,0)
  if (currentDate.value > rightMostColDt) {
    taskStore.addMoreColumnsWs(3)
  }

  // Only fetch Google Calendar events if connected
  if (isConnected.value && currentDate.value) {
    const dt = getDateStrFromDateObj(currentDate.value)
    calendarStore.fetchGcalTask(dt)
  }
}

// Modified calendar options to handle conditional event sources
const calendarOptions = ref({
  plugins: [dayGridPlugin, timeGridPlugin, interactionPlugin, listPlugin],
  initialView: props.initialView,
  headerToolbar: false,
  allDaySlot: false,
  eventTimeFormat: { hour: '2-digit', minute: '2-digit', meridiem: false },
  slotMinTime: '00:00:00',
  slotMaxTime: '23:59:59',
  snapDuration: '00:01:00',
  height: 'auto',
  expandRows: true,
  stickyHeaderDates: false,
  navLinks: false,
  dayMaxEvents: false,
  eventClick: handleEventClick,
  datesSet: handleDatesSet,
  eventSources: [
    // Always show local tasks
    { events: (info, success) => success(localCalTasks.value) },
    // Only show Google Calendar events if connected
    {
      events: (info, success) => {
        if (isConnected.value) {
          success(gcalEvents.value)
        } else {
          success([]) // Return empty array if not connected
        }
      }
    }
  ],
  selectable: false,
  eventResizableFromStart: true,
  editable: true,
  droppable: true, // Always allow task dropping
  drop: handleTaskDropped,
  eventDrop: handleCalendarEventUpdated,
  eventResize: handleCalendarEventUpdated,
})
</script>
```

### 3. Backend: Enhanced Google Calendar Consumer

**File**: `backend/apps/integrations/google_calendar/consumers.py`

The WebSocket consumer needs to check connection status before processing requests:

```python
class GoogleCalendarConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.user = self.scope.get("user")
        if not self.user or not self.user.is_authenticated:
            await self.close(code=401)
            return

        # Check if user has Google Calendar connected
        self.has_google_calendar = await self._check_google_calendar_connection()

        await self.accept()
        self.group_name = f"gcal_user_{self.user.id}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)

        # Send connection status
        await self.send_json({
            "type": "connected",
            "google_calendar_connected": self.has_google_calendar
        })

    async def receive_json(self, content, **kwargs):
        action = content.get("action")

        if not action:
            logger.warning("No action specified in WebSocket message")
            await self.send_json({
                "type": "error",
                "error": "No action specified",
                "details": 'The message must contain an "action" field',
            })
            return

        # Check if user has Google Calendar connected before processing requests
        if not self.has_google_calendar:
            logger.info(f"User {self.user.id} attempted Google Calendar action without connection")
            await self.send_json({
                "type": "gcal.events",
                "data": []  # Return empty events array
            })
            return

        if action == "fetch_gcal_task_from_dt":
            payload = content.get("payload")
            date_str = payload.get("date_str")
            if not date_str:
                return await self.send_json(
                    {"type": "error", "error": "no `date_str` found"}
                )
            resp = await self.fetch_cal_taks_from_dt(date_str)
            return resp

    @database_sync_to_async
    def _check_google_calendar_connection(self):
        """Check if user has Google Calendar credentials."""
        from .models import GoogleCalendarCredentials
        return GoogleCalendarCredentials.objects.filter(user=self.user).exists()

    @database_sync_to_async
    def _fetch_events(self, date_str: str):
        """Fetch Google Calendar events only if user is connected."""
        from .models import GoogleCalendarCredentials

        # Double-check connection status
        creds_obj = GoogleCalendarCredentials.objects.filter(user=self.user).first()
        if not creds_obj:
            logger.info(f"No Google Calendar credentials for user {self.user.id}")
            return []

        # ... rest of existing fetch logic ...
```

### 4. Backend: Updated Views

**File**: `backend/apps/integrations/google_calendar/views.py`

Views need to handle requests from users without Google Calendar connections:

```python
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

        # Always get local tasks first
        formatted_events = []

        # Get tasks with status ON_CAL for the current user
        on_cal_tasks = Task.objects.filter(
            user=request.user,
            status=Task.ON_CAL,
            start_at__isnull=False,
            end_at__isnull=False,
        )

        # Format tasks for FullCalendar
        for task in on_cal_tasks:
            formatted_task = {
                "id": f"task-{task.id}",
                "title": task.title,
                "start": task.start_at.isoformat(),
                "end": task.end_at.isoformat(),
                "allDay": False,
                "backgroundColor": "#E69553",
                "borderColor": "#DF892E",
                "textColor": "#0C0000",
                "extendedProps": {
                    "description": task.description or "",
                    "source": "task",
                    "taskId": task.pk,
                    "status": task.status,
                    "isCompleted": task.is_completed,
                    "duration": task.duration,
                    "raw": task,  # Include raw task data for editing
                },
            }
            formatted_events.append(formatted_task)

        # Only fetch Google Calendar events if user is connected
        credentials_obj = GoogleCalendarCredentials.objects.filter(
            user=request.user
        ).first()

        if credentials_obj:
            try:
                # Validate ISO8601 format and timezone awareness
                start_dt = parse_datetime(start)
                end_dt = parse_datetime(end)
                if not start_dt or not end_dt:
                    raise ValueError("Invalid ISO8601 datetime")

                # Get the calendar service
                credentials = credentials_obj.get_credentials()
                if isinstance(credentials, dict) and credentials.get("error"):
                    logger.warning(f"Google Calendar credentials error for user {request.user.id}: {credentials.get('error')}")
                    # Don't fail the entire request, just skip Google events
                    return Response(formatted_events)

                service = build_calendar_service(credentials)
                calendar_id = credentials_obj.calendar_id or "primary"

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
                    f"Google events fetched count={len(events_result.get('items', []))} for user_id={request.user.id}"
                )
                events = events_result.get("items", [])

                # Transform Google events to FullCalendar format
                google_events = [
                    format_event_for_fullcalendar(event) for event in events
                ]
                formatted_events.extend(google_events)

            except Exception as e:
                logger.error(f"Error fetching Google Calendar events for user {request.user.id}: {str(e)}")
                # Don't fail the entire request, just skip Google events
                pass
        else:
            logger.info(f"User {request.user.id} has no Google Calendar connection, returning only local tasks")

        return Response(formatted_events)

    except Exception as e:
        logger.error(f"Unexpected error in get_calendar_events: {str(e)}")
        return Response({"error": str(e)}, status=500)
```

## Data Models

### Connection Status Detection

The system will use the existing `GoogleCalendarCredentials` model to determine connection status:

```python
# In views and consumers
def is_google_calendar_connected(user):
    """Check if user has valid Google Calendar credentials."""
    from apps.integrations.google_calendar.models import GoogleCalendarCredentials
    return GoogleCalendarCredentials.objects.filter(user=user).exists()
```

### Event Source Identification

Events will continue to use the `source` field in `extendedProps` to distinguish between:
- `"task"` - Local tasks from the application
- `"google"` - Google Calendar events

## Error Handling

### Connection Status Errors

- **Missing Credentials**: Return empty Google events array instead of error
- **Expired Tokens**: Attempt refresh, fallback to local tasks only
- **API Failures**: Log error, continue with local tasks

### WebSocket Handling

- **Unconnected Users**: Return empty events array for Google Calendar requests
- **Connection Loss**: Gracefully handle disconnection without affecting local tasks
- **Invalid Requests**: Validate connection status before processing

### Frontend Resilience

- **API Failures**: Show local tasks even if Google Calendar fails
- **WebSocket Errors**: Continue calendar functionality with local tasks only
- **Loading States**: Show appropriate loading indicators for each integration

## Testing Strategy

### Unit Tests

1. **Connection Status Detection**
   - Test `is_google_calendar_connected()` with various user states
   - Test credential validation and expiry handling
   - Test fallback behavior when credentials are missing

2. **Conditional Logic**
   - Test calendar store methods with connected/disconnected states
   - Test WebSocket consumer behavior for both user types
   - Test view responses for connected/disconnected users

3. **Event Source Handling**
   - Test event source filtering based on connection status
   - Test calendar options with conditional event sources
   - Test drag and drop functionality for both user types

### Integration Tests

1. **End-to-End Calendar Functionality**
   - Test complete calendar workflow without Google Calendar
   - Test complete calendar workflow with Google Calendar
   - Test switching between connected/disconnected states

2. **WebSocket Communication**
   - Test WebSocket messages for connected users
   - Test WebSocket messages for disconnected users
   - Test connection status changes during active sessions

### Manual Testing Scenarios

1. **User Journey Testing**
   - New user accessing calendar without Google connection
   - User connecting Google Calendar mid-session
   - User disconnecting Google Calendar mid-session
   - User with expired Google Calendar credentials

2. **Error Scenarios**
   - Google Calendar API failures
   - Network connectivity issues
   - Invalid credential states

## Implementation Phases

### Phase 1: Frontend Conditional Logic (Priority: High)

- Update calendar store to check connection status
- Modify CalendarIntegration component to always render
- Add connection status indicators
- Implement conditional Google Calendar operations

### Phase 2: Backend Optimization (Priority: High)

- Update WebSocket consumer to check connection status
- Modify views to handle disconnected users gracefully
- Implement efficient credential checking
- Add proper error handling and logging

### Phase 3: User Experience Enhancements (Priority: Medium)

- Improve connection status indicators
- Add smooth transitions between connected/disconnected states
- Implement better error messaging
- Add loading states for connection operations

### Phase 4: Testing & Polish (Priority: Medium)

- Comprehensive unit and integration tests
- Performance optimization for connection checks
- Documentation updates
- User experience testing

## Performance Considerations

### Optimization Strategies

1. **Lazy Connection Checking**: Only check Google Calendar connection when needed
2. **Cached Connection Status**: Cache connection status to avoid repeated database queries
3. **Conditional WebSocket Initialization**: Only establish Google Calendar WebSocket for connected users
4. **Efficient Event Filtering**: Filter events at the source rather than in the frontend

### Resource Management

- **WebSocket Connections**: Close Google Calendar WebSocket when user disconnects
- **Polling**: Stop Google Calendar polling for disconnected users
- **API Calls**: Eliminate unnecessary Google Calendar API calls
- **Memory Usage**: Clean up Google Calendar event data when disconnected

## Security Considerations

### Access Control

- **Credential Validation**: Always validate Google Calendar credentials before API calls
- **User Isolation**: Ensure users can only access their own calendar data
- **Token Management**: Properly handle token refresh and expiry

### Error Information

- **Minimal Error Exposure**: Don't expose sensitive Google Calendar API errors to frontend
- **Logging**: Log security-relevant events for monitoring
- **Graceful Degradation**: Fail securely by falling back to local functionality

## Monitoring and Debugging

### Metrics to Track

- **Connection Status Distribution**: How many users have Google Calendar connected
- **API Call Efficiency**: Reduction in unnecessary Google Calendar API calls
- **Error Rates**: Track Google Calendar-related errors separately
- **User Experience**: Monitor calendar usage patterns for connected vs disconnected users

### Debug Tools

- **Connection Status Logging**: Clear logs for connection status changes
- **Conditional Logic Tracing**: Debug information for conditional operations
- **Performance Monitoring**: Track performance improvements from reduced API calls
