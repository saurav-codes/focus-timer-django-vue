import {
  RESPONSE_STATUS_LABELS,
  EVENT_STATUS_LABELS,
  TRANSPARENCY_LABELS,
  VISIBILITY_LABELS,
} from '../constants/dateFormats'

/**
 * Normalize event data from FullCalendar extendedProps
 * @param {Object} rawEvent - Raw event object from FullCalendar
 * @returns {Object} Normalized event data
 */
export function normalizeEventData(rawEvent) {
  if (!rawEvent || typeof rawEvent !== 'object') {
    return {
      title: 'Untitled Event',
      description: '',
      location: '',
      status: 'confirmed',
      attendees: [],
      creator: null,
      organizer: null,
      conferenceData: null,
      hangoutLink: '',
      attachments: [],
      reminders: null,
      visibility: 'default',
      transparency: 'opaque',
      eventType: 'default',
    }
  }

  // Handle both direct properties and extendedProps structure
  const props = rawEvent.extendedProps || rawEvent

  return {
    // Basic event information
    title: rawEvent.title || rawEvent.summary || props.title || props.summary || 'Untitled Event',
    description: props.description || rawEvent.description || '',
    location: props.location || rawEvent.location || '',
    status: props.status || rawEvent.status || 'confirmed',

    // Time information (preserve original structure)
    start: rawEvent.start,
    end: rawEvent.end,
    allDay: rawEvent.allDay,

    // People information
    attendees: normalizeAttendeeData(props.attendees || rawEvent.attendees || []),
    creator: props.creator || rawEvent.creator || null,
    organizer: props.organizer || rawEvent.organizer || null,

    // Conference and meeting data
    conferenceData: normalizeConferenceData(props.conferenceData || rawEvent.conferenceData),
    hangoutLink: props.hangoutLink || rawEvent.hangoutLink || '',

    // Additional metadata
    attachments: props.attachments || rawEvent.attachments || [],
    reminders: props.reminders || rawEvent.reminders || null,

    // Privacy and visibility
    visibility: props.visibility || rawEvent.visibility || 'default',
    transparency: props.transparency || rawEvent.transparency || 'opaque',
    eventType: props.eventType || rawEvent.eventType || 'default',

    // Timestamps
    created: props.created || rawEvent.created || null,
    updated: props.updated || rawEvent.updated || null,

    // Links and IDs
    htmlLink: props.htmlLink || rawEvent.htmlLink || '',
    recurringEventId: props.recurringEventId || rawEvent.recurringEventId || null,
    recurrence: props.recurrence || rawEvent.recurrence || [],
  }
}

/**
 * Normalize attendee data with fallbacks
 * @param {Array} attendees - Raw attendee array
 * @returns {Array} Normalized attendee data
 */
export function normalizeAttendeeData(attendees) {
  if (!Array.isArray(attendees)) {
    return []
  }

  return attendees
    .map((attendee) => {
      if (!attendee || typeof attendee !== 'object') {
        return null
      }

      return {
        email: attendee.email || '',
        displayName: attendee.displayName || attendee.email || 'Unknown',
        responseStatus: attendee.responseStatus || 'needsAction',
        organizer: Boolean(attendee.organizer),
        self: Boolean(attendee.self),
        optional: Boolean(attendee.optional),
        resource: Boolean(attendee.resource),
        comment: attendee.comment || '',
        additionalGuests: attendee.additionalGuests || 0,
      }
    })
    .filter(Boolean) // Remove null entries
}

/**
 * Normalize conference data for meeting/video call information
 * @param {Object} conferenceData - Raw conference data
 * @returns {Object|null} Normalized conference data
 */
export function normalizeConferenceData(conferenceData) {
  if (!conferenceData || typeof conferenceData !== 'object') {
    return null
  }

  return {
    conferenceId: conferenceData.conferenceId || '',
    conferenceSolution: conferenceData.conferenceSolution
      ? {
          name: conferenceData.conferenceSolution.name || 'Unknown Platform',
          iconUri: conferenceData.conferenceSolution.iconUri || '',
        }
      : null,
    entryPoints: Array.isArray(conferenceData.entryPoints)
      ? conferenceData.entryPoints.map((entry) => ({
          entryPointType: entry.entryPointType || 'video',
          uri: entry.uri || '',
          label: entry.label || entry.entryPointType || 'Join Meeting',
          meetingCode: entry.meetingCode || '',
          accessCode: entry.accessCode || '',
          pin: entry.pin || '',
          passcode: entry.passcode || '',
          password: entry.password || '',
        }))
      : [],
    notes: conferenceData.notes || '',
  }
}

/**
 * Get user-friendly label for response status
 * @param {string} status - Response status
 * @returns {string} User-friendly label
 */
export function getResponseStatusLabel(status) {
  return RESPONSE_STATUS_LABELS[status] || 'Pending'
}

/**
 * Get user-friendly label for event status
 * @param {string} status - Event status
 * @returns {string} User-friendly label
 */
export function getEventStatusLabel(status) {
  return EVENT_STATUS_LABELS[status] || status || 'Confirmed'
}

/**
 * Get user-friendly label for transparency
 * @param {string} transparency - Transparency value
 * @returns {string} User-friendly label
 */
export function getTransparencyLabel(transparency) {
  return TRANSPARENCY_LABELS[transparency] || transparency || 'Busy'
}

/**
 * Get user-friendly label for visibility
 * @param {string} visibility - Visibility value
 * @returns {string} User-friendly label
 */
export function getVisibilityLabel(visibility) {
  return VISIBILITY_LABELS[visibility] || visibility || 'Default'
}

/**
 * Get attendee initials for avatar display
 * @param {Object} attendee - Attendee object
 * @returns {string} Initials (1-2 characters)
 */
export function getAttendeeInitials(attendee) {
  if (!attendee) return '?'

  const name = attendee.displayName || attendee.email || '?'
  const words = name.split(' ').filter((word) => word.length > 0)

  if (words.length >= 2) {
    return (words[0][0] + words[1][0]).toUpperCase()
  } else if (words.length === 1) {
    return words[0].substring(0, 2).toUpperCase()
  }

  return '?'
}

/**
 * Check if event has meaningful conference data
 * @param {Object} conferenceData - Conference data object
 * @returns {boolean} True if has useful conference info
 */
export function hasConferenceData(conferenceData) {
  if (!conferenceData) return false

  return Boolean(
    conferenceData.conferenceId ||
      conferenceData.conferenceSolution?.name ||
      (conferenceData.entryPoints && conferenceData.entryPoints.length > 0)
  )
}
