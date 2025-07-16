# Design Document

## Overview

The ReadOnlyModal.vue component currently suffers from multiple date parsing issues that result in "Invalid date" displays and poor handling of various calendar event data formats. This design outlines a comprehensive solution to create robust date parsing logic that can handle multiple input formats from different calendar sources (Google Calendar, FullCalendar) while maintaining code simplicity for beginner developers.

The solution focuses on creating a centralized date parsing utility with fallback mechanisms, improving error handling, and enhancing the display of all event metadata including attendees, locations, and other event details.

## Architecture

### Current Issues Analysis

1. **Date Parsing Problems**: The current `parseDateTime` function only handles ISO strings and doesn't account for various date formats from different sources
2. **Error Handling**: "Invalid date" is displayed instead of graceful fallbacks
3. **Data Structure Variations**: Different calendar sources provide data in different structures (Google Calendar API vs FullCalendar objects)
4. **Missing Field Handling**: Limited handling of attendee information, event metadata, and optional fields
5. **Inconsistent Formatting**: Date formatting varies across different sections of the modal

### Proposed Architecture

The solution will implement a layered approach:

1. **Date Parsing Layer**: Centralized date parsing utilities with multiple format support
2. **Data Normalization Layer**: Standardize event data from different sources
3. **Display Layer**: Consistent formatting and graceful error handling
4. **Validation Layer**: Input validation and fallback mechanisms

## Components and Interfaces

### 1. Backend: Enhanced format_event_for_fullcalendar Function

**File**: `backend/apps/integrations/google_calendar/utils.py`

The existing `format_event_for_fullcalendar` function needs to be updated to preserve essential Google Calendar fields:

```python
def format_event_for_fullcalendar(event):
    """
    Format a Google Calendar event for FullCalendar with comprehensive event data.
    Focus on essential information users need without overwhelming them.
    """
    start = event["start"].get("dateTime", event["start"].get("date"))
    end = event["end"].get("dateTime", event["end"].get("date"))

    return {
        "id": event["id"],
        "title": event.get("summary", "(No title)"),
        "start": start,
        "end": end,
        "allDay": "date" in event["start"],
        "backgroundColor": event.get("colorId", "#4285F4"),
        "borderColor": event.get("colorId", "#4285F4"),
        "textColor": "#FFFFFF",
        "extendedProps": {
            # Essential event details
            "description": event.get("description", ""),
            "location": event.get("location", ""),
            "status": event.get("status", ""),
            "htmlLink": event.get("htmlLink", ""),

            # People information
            "creator": event.get("creator", {}),
            "organizer": event.get("organizer", {}),
            "attendees": event.get("attendees", []),

            # Meeting/Conference info (essential for remote work)
            "hangoutLink": event.get("hangoutLink", ""),
            "conferenceData": event.get("conferenceData", {}),

            # Time metadata
            "created": event.get("created", ""),
            "updated": event.get("updated", ""),
            "transparency": event.get("transparency", ""),

            # Recurrence info (helps users understand event patterns)
            "recurringEventId": event.get("recurringEventId", ""),
            "recurrence": event.get("recurrence", []),
            "originalStartTime": event.get("originalStartTime", {}),

            # Privacy and access
            "visibility": event.get("visibility", ""),
            "eventType": event.get("eventType", "default"),

            # Additional useful features
            "reminders": event.get("reminders", {}),
            "attachments": event.get("attachments", []),

            # Source identification
            "source": "google"
        }
    }
```

### 2. Frontend: Date Parsing Utilities with date-fns

**File**: `frontend-vue/src/utils/dateParsingUtils.js`

```javascript
import { parseISO, format, formatDistanceToNow, differenceInMinutes, differenceInDays, isValid } from 'date-fns'
import { zonedTimeToUtc, utcToZonedTime, format as formatTz } from 'date-fns-tz'

// Core date parsing functions
export function parseEventDate(dateInput, fallbackValue = null)
export function formatEventDateTime(dateObj, options = {})
export function calculateEventDuration(startDate, endDate)
export function formatRelativeTime(date)
export function isAllDayEvent(startObj, endObj)
export function parseGoogleCalendarDate(dateObj)
export function parseWithTimezone(dateString, timezone)
export function formatInTimezone(date, timezone, formatString)
```

**Key Features**:

- **date-fns Integration**: Leverages date-fns for robust date parsing and formatting
- **Timezone Support**: Uses date-fns-tz for proper timezone handling across different user timezones
- **Google Calendar Compatibility**: Support for Google Calendar date objects (`{dateTime, date, timeZone}`)
- **Multiple Input Formats**: Support for ISO strings, Date objects, and timezone-aware parsing
- **Graceful Fallback Handling**: Comprehensive error handling with meaningful fallbacks
- **All-day Event Detection**: Reliable detection of all-day vs timed events
- **Performance Optimized**: Tree-shakable imports to minimize bundle size

### 3. Frontend: Event Data Normalizer

**File**: `frontend-vue/src/utils/eventDataNormalizer.js`

```javascript
// Event data normalization functions
export function normalizeEventData(rawEvent)
export function normalizeAttendeeData(attendees)
export function normalizeConferenceData(conferenceData)
export function normalizeEventMetadata(event)
```

**Key Features**:

- Standardize data from FullCalendar extendedProps
- Handle missing or malformed data
- Preserve original data structure for debugging

### 4. Frontend: Enhanced ReadOnlyModal Component

**Essential Information Display Strategy**:

Based on user needs, the modal will display information in this priority order:

**High Priority (Always Show)**:

1. **Event Title** - Primary identifier
2. **Date & Time** - When the event occurs
3. **Duration** - How long it lasts
4. **Location** - Where it happens (if provided)
5. **Video Call Link** - Essential for remote meetings
6. **Description** - Event details (if provided)

**Medium Priority (Show if Available)**:
7. **Attendees & Status** - Who's invited and their responses
8. **Organizer** - Who created the event
9. **Event Status** - Confirmed/Tentative/Cancelled
10. **Recurrence Info** - If it's a recurring event

**Low Priority (Show if Space/Relevant)**:
11. **Reminders** - Notification settings
12. **Attachments** - Files attached to event
13. **Privacy Level** - Public/Private status
14. **Created/Updated** - Metadata timestamps

**Never Show (Too Technical)**:

- Raw recurrence rules (RRULE strings)
- Event IDs, ETags
- Extended properties
- Conference signatures
- Working location details

### 5. Frontend: Date Formatting Constants

**File**: `frontend-vue/src/constants/dateFormats.js`

```javascript
// Centralized date formatting patterns
export const DATE_FORMATS = {
  FULL_DATETIME: 'PPPp',
  DATE_ONLY: 'PPPP',
  TIME_ONLY: 'p',
  RELATIVE: 'relative',
  COMPACT_DATETIME: 'Pp'
}

export const RESPONSE_STATUS_LABELS = {
  'accepted': 'Accepted',
  'declined': 'Declined',
  'tentative': 'Maybe',
  'needsAction': 'Pending'
}

export const EVENT_STATUS_LABELS = {
  'confirmed': 'Confirmed',
  'tentative': 'Tentative',
  'cancelled': 'Cancelled'
}
```

## Data Models

### Input Data Structures

The component needs to handle the complete Google Calendar API event structure. Based on the actual API format, here are the key fields we'll work with:

#### Google Calendar API Event Structure (Complete)

```javascript
{
  kind: "calendar#event",
  etag: string,
  id: string,
  status: string, // "confirmed", "tentative", "cancelled"
  htmlLink: string,
  created: datetime, // RFC3339 timestamp
  updated: datetime, // RFC3339 timestamp
  summary: string, // Event title
  description: string,
  location: string,
  colorId: string,
  creator: {
    id: string,
    email: string,
    displayName: string,
    self: boolean
  },
  organizer: {
    id: string,
    email: string,
    displayName: string,
    self: boolean
  },
  start: {
    date: date, // For all-day events
    dateTime: datetime, // For timed events
    timeZone: string
  },
  end: {
    date: date,
    dateTime: datetime,
    timeZone: string
  },
  endTimeUnspecified: boolean,
  recurrence: [string], // RRULE strings
  recurringEventId: string,
  originalStartTime: {
    date: date,
    dateTime: datetime,
    timeZone: string
  },
  transparency: string, // "opaque" (busy) or "transparent" (free)
  visibility: string, // "default", "public", "private", "confidential"
  attendees: [
    {
      id: string,
      email: string,
      displayName: string,
      organizer: boolean,
      self: boolean,
      resource: boolean,
      optional: boolean,
      responseStatus: string, // "needsAction", "declined", "tentative", "accepted"
      comment: string,
      additionalGuests: integer
    }
  ],
  attendeesOmitted: boolean,
  hangoutLink: string,
  conferenceData: {
    entryPoints: [
      {
        entryPointType: string, // "video", "phone", "sip", "more"
        uri: string,
        label: string,
        pin: string,
        accessCode: string,
        meetingCode: string,
        passcode: string,
        password: string
      }
    ],
    conferenceSolution: {
      key: { type: string },
      name: string, // "Google Meet", "Zoom", etc.
      iconUri: string
    },
    conferenceId: string,
    signature: string,
    notes: string
  },
  reminders: {
    useDefault: boolean,
    overrides: [
      {
        method: string, // "email", "popup"
        minutes: integer
      }
    ]
  },
  attachments: [
    {
      fileUrl: string,
      title: string,
      mimeType: string,
      iconLink: string,
      fileId: string
    }
  ],
  eventType: string // "default", "outOfOffice", "focusTime", "workingLocation"
}
```

#### FullCalendar Event Format (After Backend Processing)

The backend `format_event_for_fullcalendar` function will be updated to preserve essential Google Calendar fields:

```javascript
{
  id: string,
  title: string, // from summary
  start: string, // ISO datetime or date
  end: string,
  allDay: boolean,
  backgroundColor: string,
  borderColor: string,
  textColor: string,
  extendedProps: {
    // Essential event details
    description: string,
    location: string,
    status: string,
    htmlLink: string,

    // People information
    creator: object,
    organizer: object,
    attendees: array,

    // Meeting/Conference info
    hangoutLink: string,
    conferenceData: object,

    // Metadata
    created: string,
    updated: string,
    visibility: string,
    transparency: string,

    // Recurrence info
    recurringEventId: string,
    recurrence: array,

    // Additional features
    reminders: object,
    attachments: array,
    eventType: string,

    // Source identification
    source: "google"
  }
}
```

### FullCalendar Event Object Structure

The backend must format Google Calendar events to match the FullCalendar event object specification:

```javascript
{
  // Required FullCalendar fields
  id: string,                    // Unique event identifier
  title: string,                 // Event title (from Google Calendar 'summary')
  start: string,                 // ISO8601 string (from dateTime or date)
  end: string,                   // ISO8601 string (from dateTime or date)
  allDay: boolean,               // true if using 'date' instead of 'dateTime'

  // Optional FullCalendar styling fields
  backgroundColor: string,       // Event background color
  borderColor: string,          // Event border color
  textColor: string,            // Event text color

  // All Google Calendar data goes in extendedProps
  extendedProps: {
    // Essential event information
    description: string,
    location: string,
    status: string,              // "confirmed", "tentative", "cancelled"
    htmlLink: string,

    // People information
    creator: {
      id: string,
      email: string,
      displayName: string,
      self: boolean
    },
    organizer: {
      id: string,
      email: string,
      displayName: string,
      self: boolean
    },
    attendees: [
      {
        id: string,
        email: string,
        displayName: string,
        organizer: boolean,
        self: boolean,
        resource: boolean,
        optional: boolean,
        responseStatus: string,    // "needsAction", "declined", "tentative", "accepted"
        comment: string,
        additionalGuests: integer
      }
    ],

    // Meeting/Conference information
    hangoutLink: string,
    conferenceData: {
      entryPoints: [
        {
          entryPointType: string,  // "video", "phone", "sip", "more"
          uri: string,
          label: string,
          meetingCode: string,
          accessCode: string,
          pin: string,
          passcode: string,
          password: string
        }
      ],
      conferenceSolution: {
        key: { type: string },
        name: string,              // "Google Meet", "Zoom", etc.
        iconUri: string
      },
      conferenceId: string,
      notes: string
    },

    // Time and recurrence metadata
    created: string,               // RFC3339 timestamp
    updated: string,               // RFC3339 timestamp
    transparency: string,          // "opaque" (busy) or "transparent" (free)
    visibility: string,            // "default", "public", "private", "confidential"
    eventType: string,             // "default", "outOfOffice", "focusTime", etc.

    // Recurrence information
    recurringEventId: string,
    recurrence: [string],          // RRULE strings
    originalStartTime: {
      date: string,
      dateTime: string,
      timeZone: string
    },

    // Additional features
    reminders: {
      useDefault: boolean,
      overrides: [
        {
          method: string,          // "email", "popup"
          minutes: integer
        }
      ]
    },
    attachments: [
      {
        fileUrl: string,
        title: string,
        mimeType: string,
        iconLink: string,
        fileId: string
      }
    ],

    // Source identification
    source: "google"
  }
}
```

## Error Handling

### Date Parsing Errors

- **Invalid Date Strings**: Return null and use fallback display
- **Missing Date Fields**: Hide time-related sections gracefully
- **Timezone Issues**: Preserve original timezone info, fallback to UTC

### Data Structure Errors

- **Missing Required Fields**: Use sensible defaults
- **Malformed Attendee Data**: Skip invalid entries, show email as fallback for missing names
- **Empty Event Objects**: Display minimal event information with clear indicators

### Display Fallbacks

- **Invalid Dates**: Show "Date not available" instead of "Invalid date"
- **Missing Titles**: Show "Untitled Event"
- **Missing Descriptions**: Hide description section entirely
- **Missing Attendees**: Hide attendee section entirely

## Testing Strategy

### Unit Tests

1. **Date Parsing Functions**
   - Test various input formats (ISO strings, Date objects, Google Calendar objects)
   - Test edge cases (null values, malformed strings, timezone variations)
   - Test all-day event detection

2. **Data Normalization**
   - Test Google Calendar API event normalization
   - Test FullCalendar event normalization
   - Test handling of missing/malformed data

3. **Component Logic**
   - Test computed properties with various event data
   - Test error handling scenarios
   - Test display formatting consistency

### Integration Tests

1. **End-to-End Event Display**
   - Test modal with real Google Calendar events
   - Test modal with FullCalendar events
   - Test modal with malformed event data

2. **User Experience Tests**
   - Test accessibility with screen readers
   - Test responsive design on different screen sizes
   - Test keyboard navigation

### Manual Testing Scenarios

1. **Real Calendar Data**
   - Import events from Google Calendar
   - Test with various event types (all-day, recurring, with attendees)
   - Test with events in different timezones

2. **Edge Cases**
   - Events with missing end times
   - Events with malformed attendee data
   - Events with HTML in descriptions
   - Events with very long titles/descriptions

## Implementation Phases

### Phase 1: Core Date Parsing (Priority: High)

- Create date parsing utilities
- Implement fallback mechanisms
- Update ReadOnlyModal to use new utilities
- Fix "Invalid date" issues

### Phase 2: Data Normalization (Priority: High)

- Create event data normalizer
- Handle different calendar source formats
- Implement consistent data structure

### Phase 3: Enhanced Display (Priority: Medium)

- Improve attendee information display
- Add comprehensive event metadata
- Implement consistent formatting

### Phase 4: Error Handling & Polish (Priority: Medium)

- Comprehensive error handling
- Accessibility improvements
- Performance optimizations

### Phase 5: Testing & Documentation (Priority: Low)

- Unit and integration tests
- Code documentation
- User documentation updates

## Performance Considerations

### Optimization Strategies

1. **Lazy Loading**: Only parse dates when needed for display
2. **Memoization**: Cache parsed dates to avoid repeated parsing
3. **Tree Shaking**: Keep utility functions small and modular
4. **Bundle Size**: Use date-fns selectively to minimize bundle impact

### Memory Management

- Avoid storing large amounts of parsed date objects
- Clean up event listeners and watchers properly
- Use computed properties for reactive date formatting

## Security Considerations

### Input Sanitization

- Sanitize HTML content in event descriptions
- Validate date strings before parsing
- Escape user-generated content in attendee names

### XSS Prevention

- Use v-text instead of v-html where possible
- Sanitize HTML content in descriptions using a trusted library
- Validate URLs in event links before rendering

## Accessibility

### Screen Reader Support

- Proper ARIA labels for date/time information
- Semantic HTML structure for event details
- Clear focus management in modal

### Keyboard Navigation

- Tab order through event details
- Escape key to close modal
- Enter key to activate links

### Visual Accessibility

- High contrast for status indicators
- Clear visual hierarchy
- Responsive text sizing

## Browser Compatibility

### Target Support

- Modern browsers (Chrome 90+, Firefox 88+, Safari 14+, Edge 90+)
- Mobile browsers (iOS Safari 14+, Chrome Mobile 90+)

### Polyfills

- Date parsing fallbacks for older browsers
- Intl.DateTimeFormat polyfill if needed
- CSS Grid fallbacks for older browsers

## Monitoring and Debugging

### Error Tracking

- Log date parsing failures with context
- Track "Invalid date" occurrences
- Monitor performance of date parsing operations

### Debug Tools

- Console logging for development mode
- Event data inspection utilities
- Date parsing test helpers
