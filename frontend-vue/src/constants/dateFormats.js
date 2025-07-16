// Centralized date formatting patterns using date-fns format strings
export const DATE_FORMATS = {
  FULL_DATETIME: 'PPPp', // "April 29th, 2021 at 9:00 AM"
  DATE_ONLY: 'PPPP', // "Thursday, April 29th, 2021"
  TIME_ONLY: 'p', // "9:00 AM"
  RELATIVE: 'relative', // Special flag for relative time
  COMPACT_DATETIME: 'Pp', // "Apr 29, 2021, 9:00 AM"
  SHORT_DATETIME: 'MMM d, p', // "Apr 29, 9:00 AM"
  DATE_SHORT: 'MMM d, yyyy', // "Apr 29, 2021"
  TIME_WITH_TIMEZONE: 'p zzz', // "9:00 AM EST"
}

// Response status labels for attendee status display
export const RESPONSE_STATUS_LABELS = {
  accepted: 'Accepted',
  declined: 'Declined',
  tentative: 'Maybe',
  needsAction: 'Pending',
}

// Event status labels for confirmed/tentative/cancelled states
export const EVENT_STATUS_LABELS = {
  confirmed: 'Confirmed',
  tentative: 'Tentative',
  cancelled: 'Cancelled',
}

// Transparency labels for busy/free status
export const TRANSPARENCY_LABELS = {
  opaque: 'Busy',
  transparent: 'Free',
}

// Visibility labels for privacy levels
export const VISIBILITY_LABELS = {
  default: 'Default',
  public: 'Public',
  private: 'Private',
  confidential: 'Confidential',
}

// Event type labels
export const EVENT_TYPE_LABELS = {
  default: 'Default',
  outOfOffice: 'Out of Office',
  focusTime: 'Focus Time',
  workingLocation: 'Working Location',
}

// Conference entry point type labels
export const CONFERENCE_ENTRY_POINT_LABELS = {
  video: 'Video Call',
  phone: 'Phone',
  sip: 'SIP',
  more: 'More Options',
}
