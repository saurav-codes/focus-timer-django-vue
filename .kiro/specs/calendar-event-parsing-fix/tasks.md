# Implementation Plan

- [x] 1. Update backend Google Calendar event formatting for FullCalendar compatibility
  - [x] 1.1 Enhance format_event_for_fullcalendar function structure
    - Update `format_event_for_fullcalendar` function in `backend/apps/integrations/google_calendar/utils.py` to follow FullCalendar event object specification exactly
    - Ensure proper FullCalendar-compatible field mapping: id (string), title (string), start (ISO8601 string), end (ISO8601 string), allDay (boolean)
    - Add optional FullCalendar styling fields: backgroundColor, borderColor, textColor
    - Move all Google Calendar-specific data into extendedProps object as per FullCalendar specification
    - Add comprehensive error handling for missing or malformed Google Calendar fields
    - _Requirements: 4.1, 4.2, 6.1, 6.2, 6.3, 6.4_

  - [x] 1.2 Add comprehensive attendee data formatting
    - Replace simple email list with full attendee objects including displayName, responseStatus, organizer flags
    - Preserve attendee metadata like optional status, self identification, and additional guests count
    - Add proper handling for missing attendee information with fallbacks
    - Include creator and organizer information as separate fields for easy access
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

  - [x] 1.3 Add conference and meeting data formatting
    - Include hangoutLink directly in extendedProps for easy access
    - Format conferenceData with entry points, meeting codes, and conference solution information
    - Preserve video call links, phone numbers, and access codes for different meeting platforms
    - Add proper handling for missing conference data
    - _Requirements: 6.1, 6.2_

  - [x] 1.4 Add comprehensive event metadata
    - Include created, updated timestamps in proper ISO format
    - Add event status, visibility, transparency, and eventType fields
    - Include recurrence information (recurrence rules, recurringEventId, originalStartTime)
    - Add reminders, attachments, and other useful metadata
    - Preserve timezone information from start/end date objects
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 6.3, 6.4, 6.5_

- [x] 2. Create frontend date parsing utilities with date-fns
  - [x] 2.1 Install date-fns dependencies and create core parsing functions
    - Install date-fns and date-fns-tz packages for robust timezone handling
    - Write `parseEventDate` function using date-fns parseISO with comprehensive fallback handling
    - Implement `parseGoogleCalendarDate` specifically for Google Calendar's `{dateTime, date, timeZone}` structure using date-fns-tz
    - Create `isAllDayEvent` function to detect all-day events from start/end objects
    - Add `parseWithTimezone` function for timezone-aware parsing using zonedTimeToUtc
    - Add comprehensive error handling with null fallbacks and date-fns isValid checks
    - _Requirements: 1.1, 1.2, 1.3, 4.1, 4.2, 4.3, 4.4, 4.5_

  - [x] 2.2 Create date formatting functions with timezone support
    - Implement `formatEventDateTime` using date-fns format with timezone options
    - Create `calculateEventDuration` using date-fns differenceInMinutes and differenceInDays
    - Write `formatRelativeTime` using date-fns formatDistanceToNow for "in 2 hours" style displays
    - Add `formatInTimezone` function using date-fns-tz for proper timezone display
    - Add timezone preservation and display logic with utcToZonedTime
    - _Requirements: 1.1, 1.2, 2.1, 2.2, 2.3, 2.4, 7.1, 7.2, 7.3, 7.4_

- [x] 3. Create event data normalization utilities
  - [x] 3.1 Create event data normalizer
    - Write `normalizeEventData` to standardize FullCalendar extendedProps data
    - Implement `normalizeAttendeeData` to handle attendee information consistently
    - Create `normalizeConferenceData` for meeting/video call information
    - Add `normalizeEventMetadata` for timestamps and status information
    - _Requirements: 4.1, 4.2, 5.1, 5.2, 5.3, 5.4, 5.5, 6.1, 6.2, 6.3, 6.4, 6.5_

- [x] 4. Create date formatting constants
  - Create constants file with centralized date formatting patterns
  - Define response status labels for attendee status display
  - Add event status labels for confirmed/tentative/cancelled states
  - Include transparency and visibility label mappings
  - _Requirements: 5.2, 6.3, 6.4, 7.1, 7.2_

- [x] 5. Update ReadOnlyModal component with robust date parsing
  - [x] 5.1 Replace existing date parsing logic
    - Remove current `parseDateTime` and `formatDateTime` functions
    - Import and use new date parsing utilities
    - Update all computed properties to use new parsing functions
    - Add proper error handling for all date operations
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 3.1, 3.2, 3.3, 3.4_

  - [x] 5.2 Enhance event time display section
    - Update start/end time formatting with consistent patterns
    - Improve duration calculation and display
    - Add relative time display with proper fallbacks
    - Enhance all-day event detection and display
    - Add timezone information display
    - _Requirements: 1.1, 1.2, 1.3, 2.1, 2.2, 2.3, 2.4, 7.1, 7.2, 7.3, 7.4_

- [ ] 6. Enhance attendee information display
  - [ ] 6.1 Improve attendee data parsing
    - Update attendee data access to use normalized event data
    - Add fallback logic for missing attendee names (use email)
    - Implement proper organizer identification and display
    - Add handling for optional attendees and self identification
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

  - [ ] 6.2 Update attendee status display
    - Replace hardcoded status mapping with constants
    - Improve status indicator styling and accessibility
    - Add proper handling for missing or invalid response status
    - Enhance organizer badge display and distinction
    - _Requirements: 5.1, 5.2, 5.4, 5.5_

- [ ] 7. Add comprehensive event metadata display
  - [ ] 7.1 Enhance event details section
    - Add proper location display with formatting
    - Improve description handling with HTML content safety
    - Add event status display with meaningful labels
    - Implement visibility level display
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

  - [ ] 7.2 Add video call and conference information
    - Display hangout links prominently for remote meetings
    - Add conference data display with entry points and meeting codes
    - Show conference solution names (Google Meet, Zoom, etc.)
    - Add proper link handling and security validation
    - _Requirements: 6.1, 6.2_

  - [ ] 7.3 Add event metadata timestamps
    - Display creation and update timestamps with consistent formatting
    - Add proper RFC3339 timestamp parsing
    - Implement graceful handling of missing timestamp data
    - Use relative time display where appropriate
    - _Requirements: 3.1, 3.2, 3.3, 3.4_

- [ ] 8. Implement comprehensive error handling
  - [ ] 8.1 Add date parsing error handling
    - Replace "Invalid date" displays with "Date not available" fallbacks
    - Add graceful handling of missing date fields
    - Implement timezone error handling with UTC fallback
    - Add logging for date parsing failures in development mode
    - _Requirements: 1.3, 2.3, 4.5_

  - [ ] 8.2 Add data structure error handling
    - Implement fallbacks for missing required fields
    - Add handling for malformed attendee data
    - Create graceful degradation for empty event objects
    - Add validation for event data before display
    - _Requirements: 4.5, 5.5, 6.5_

- [ ] 9. Improve modal accessibility and user experience
  - [ ] 9.1 Enhance accessibility features
    - Add proper ARIA labels for date/time information
    - Implement semantic HTML structure for event details
    - Add screen reader support for attendee status indicators
    - Ensure proper keyboard navigation through event details
    - _Requirements: 7.1, 7.2, 7.3, 7.4_

  - [ ] 9.2 Optimize information display priority
    - Reorganize modal sections based on information priority (title, time, location, video links first)
    - Hide sections with no data instead of showing empty states
    - Implement responsive design for different screen sizes
    - Add loading states for event data processing
    - _Requirements: 6.5, 7.1, 7.2, 7.3, 7.4_

- [ ] 10. Add comprehensive testing
  - [ ] 10.1 Create unit tests for date parsing utilities
    - Test various input formats (Google Calendar objects, ISO strings, Date objects)
    - Test edge cases (null values, malformed strings, timezone variations)
    - Test all-day event detection with different input formats
    - Test error handling and fallback mechanisms
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 2.1, 2.2, 2.3, 2.4, 4.1, 4.2, 4.3, 4.4, 4.5_

  - [ ] 10.2 Create integration tests for modal component
    - Test modal with real Google Calendar event data
    - Test modal with malformed or incomplete event data
    - Test attendee display with various response statuses
    - Test conference data display with different meeting platforms
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 6.1, 6.2, 6.3, 6.4, 6.5, 7.1, 7.2, 7.3, 7.4_
