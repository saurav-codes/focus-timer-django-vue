# Implementation Plan

- [ ] 1. Update frontend calendar store for conditional Google Calendar operations
  - Modify fetchGcalTask function to check connection status before making requests
  - Update initGcalWs function to only initialize WebSocket when Google Calendar is connected
  - Add conditional logic to prevent unnecessary Google Calendar operations
  - _Requirements: 1.4, 4.1, 4.4_

- [ ] 2. Refactor CalendarIntegration component to always render calendar
  - Remove conditional rendering that blocks calendar when Google Calendar is not connected
  - Update onMounted lifecycle to not block calendar functionality based on Google connection
  - Modify navigation functions (prev/next) to conditionally fetch Google events only when connected
  - Update calendar options to handle conditional event sources
  - _Requirements: 1.1, 1.2, 1.3_

- [ ] 3. Add connection status indicators to calendar header
  - Implement connect button icon when Google Calendar is not connected
  - Ensure disconnect button shows when Google Calendar is connected
  - Add proper tooltips and hover states for connection controls
  - Style connection control buttons consistently with existing design
  - _Requirements: 2.1, 2.4, 5.1, 5.2_

- [ ] 4. Update calendar store polling logic for connected users only
  - Modify polling setup to only start when Google Calendar is connected
  - Ensure polling stops when user disconnects Google Calendar
  - Add proper cleanup of polling intervals
  - _Requirements: 4.4_

- [ ] 5. Enhance backend WebSocket consumer with connection status checking
  - Add _check_google_calendar_connection method to verify user credentials
  - Update connect method to check Google Calendar connection status
  - Modify receive_json to return empty events array for unconnected users
  - Add proper logging for connection status and request handling
  - _Requirements: 4.2, 4.3_

- [ ] 6. Update backend views to handle disconnected users gracefully
  - Modify get_calendar_events view to always return local tasks
  - Add conditional Google Calendar event fetching based on credential existence
  - Implement proper error handling that doesn't fail entire request
  - Add logging for users without Google Calendar connections
  - _Requirements: 4.1, 4.2_

- [ ] 7. Implement efficient connection status detection utility
  - Create is_google_calendar_connected helper function
  - Use GoogleCalendarCredentials model to check connection status
  - Optimize database queries for connection status checking
  - _Requirements: 4.3_

- [ ] 8. Add proper error handling for Google Calendar operations
  - Update error handling to gracefully degrade to local tasks only
  - Implement proper logging for Google Calendar API failures
  - Ensure frontend receives appropriate error messages
  - Add fallback behavior for expired or invalid credentials
  - _Requirements: 5.3_

- [ ] 9. Update calendar event source handling for conditional Google events
  - Modify FullCalendar event sources to conditionally include Google events
  - Ensure local tasks always display regardless of Google Calendar connection
  - Test event source switching when connection status changes
  - _Requirements: 1.3, 2.3, 2.5_

- [ ] 10. Test and validate optional Google Calendar integration
  - Test calendar functionality without Google Calendar connection
  - Test connecting Google Calendar mid-session
  - Test disconnecting Google Calendar mid-session
  - Verify no unnecessary API calls are made for unconnected users
  - Test drag and drop functionality works regardless of connection status
  - _Requirements: 1.1, 1.2, 2.2, 2.5, 3.1, 3.2, 3.3, 3.4_
