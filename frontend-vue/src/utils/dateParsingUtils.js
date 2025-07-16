import { parseISO, format, formatDistanceToNow, differenceInMinutes, differenceInDays, isValid } from 'date-fns'
import { fromZonedTime, formatInTimeZone } from 'date-fns-tz'

/**
 * Parse various date input formats with comprehensive error handling
 * @param {string|Date|Object} dateInput - Date in various formats
 * @param {*} fallbackValue - Value to return if parsing fails
 * @returns {Date|null} Parsed date or fallback value
 */
export function parseEventDate(dateInput, fallbackValue = null) {
  if (!dateInput) {
    return fallbackValue
  }

  try {
    // Handle Date objects
    if (dateInput instanceof Date) {
      return isValid(dateInput) ? dateInput : fallbackValue
    }

    // Handle Google Calendar date objects
    if (typeof dateInput === 'object' && (dateInput.dateTime || dateInput.date)) {
      return parseGoogleCalendarDate(dateInput)
    }

    // Handle ISO strings and other string formats
    if (typeof dateInput === 'string') {
      const parsed = parseISO(dateInput)
      return isValid(parsed) ? parsed : fallbackValue
    }

    return fallbackValue
  } catch (error) {
    console.warn('Date parsing failed:', error, 'Input:', dateInput)
    return fallbackValue
  }
}

/**
 * Parse Google Calendar date objects with timezone support
 * @param {Object} dateObj - Google Calendar date object {dateTime?, date?, timeZone?}
 * @returns {Date|null} Parsed date or null
 */
export function parseGoogleCalendarDate(dateObj) {
  if (!dateObj || typeof dateObj !== 'object') {
    return null
  }

  try {
    // Handle timed events (dateTime)
    if (dateObj.dateTime) {
      const parsed = parseISO(dateObj.dateTime)
      if (isValid(parsed)) {
        // If timezone is specified, convert from that timezone to UTC
        if (dateObj.timeZone) {
          return parseWithTimezone(dateObj.dateTime, dateObj.timeZone)
        }
        return parsed
      }
    }

    // Handle all-day events (date)
    if (dateObj.date) {
      const parsed = parseISO(dateObj.date + 'T00:00:00')
      return isValid(parsed) ? parsed : null
    }

    return null
  } catch (error) {
    console.warn('Google Calendar date parsing failed:', error, 'Input:', dateObj)
    return null
  }
}

/**
 * Parse date string with specific timezone using date-fns-tz
 * @param {string} dateString - ISO date string
 * @param {string} timezone - IANA timezone identifier
 * @returns {Date|null} Parsed date in UTC or null
 */
export function parseWithTimezone(dateString, timezone) {
  if (!dateString || !timezone) {
    return parseEventDate(dateString)
  }

  try {
    // Parse the date string as if it's in the specified timezone
    const parsed = parseISO(dateString)
    if (!isValid(parsed)) {
      return null
    }

    // If the date string already includes timezone info, use it directly
    if (dateString.includes('Z') || dateString.includes('+') || dateString.includes('-')) {
      return parsed
    }

    // Otherwise, treat it as being in the specified timezone and convert to UTC
    return fromZonedTime(parsed, timezone)
  } catch (error) {
    console.warn('Timezone-aware date parsing failed:', error, 'Input:', dateString, 'Timezone:', timezone)
    return parseEventDate(dateString)
  }
}

/**
 * Detect if an event is all-day based on start/end objects
 * @param {Object} startObj - Event start object
 * @param {Object} endObj - Event end object
 * @returns {boolean} True if all-day event
 */
export function isAllDayEvent(startObj) {
  if (!startObj || typeof startObj !== 'object') {
    return false
  }

  // Google Calendar format: all-day events use 'date' instead of 'dateTime'
  if (startObj.date && !startObj.dateTime) {
    return true
  }

  // FullCalendar format: check allDay property
  if (typeof startObj.allDay === 'boolean') {
    return startObj.allDay
  }

  // Fallback: check if start and end are date-only strings (YYYY-MM-DD format)
  if (typeof startObj === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(startObj)) {
    return true
  }

  return false
}

/**
 * Format date in specific timezone using date-fns-tz
 * @param {Date} date - Date to format
 * @param {string} timezone - IANA timezone identifier
 * @param {string} formatString - date-fns format string
 * @returns {string} Formatted date string
 */
export function formatInTimezone(date, timezone, formatString = 'PPPp') {
  if (!date || !isValid(date)) {
    return 'Date not available'
  }

  try {
    if (timezone) {
      return formatInTimeZone(date, timezone, formatString)
    }
    return format(date, formatString)
  } catch (error) {
    console.warn('Date formatting failed:', error, 'Date:', date, 'Timezone:', timezone)
    return 'Date not available'
  }
}
/**
 * Format event date/time with various display options
 * @param {Date|string|Object} dateInput - Date to format
 * @param {Object} options - Formatting options
 * @param {string} options.format - Format type ('full', 'date', 'time', 'compact')
 * @param {string} options.timezone - IANA timezone identifier
 * @param {boolean} options.relative - Show relative time if recent
 * @returns {string} Formatted date string
 */
export function formatEventDateTime(dateInput, options = {}) {
  const { format: formatType = 'full', timezone = null, relative = false } = options

  const date = parseEventDate(dateInput)
  if (!date || !isValid(date)) {
    return 'Date not available'
  }

  try {
    // Show relative time for recent dates if requested
    if (relative) {
      const now = new Date()
      const diffInMinutes = Math.abs(differenceInMinutes(date, now))

      // Show relative time for events within 24 hours
      if (diffInMinutes < 1440) {
        return formatDistanceToNow(date, { addSuffix: true })
      }
    }

    // Format strings for different display contexts
    const formatStrings = {
      full: 'PPPp', // "April 29th, 2021 at 9:00 AM"
      date: 'PPP', // "April 29th, 2021"
      time: 'p', // "9:00 AM"
      compact: 'Pp', // "Apr 29, 2021, 9:00 AM"
      short: 'MMM d, p', // "Apr 29, 9:00 AM"
    }

    const formatString = formatStrings[formatType] || formatStrings.full

    if (timezone) {
      return formatInTimezone(date, timezone, formatString)
    }

    return format(date, formatString)
  } catch (error) {
    console.warn('Date formatting failed:', error, 'Date:', dateInput, 'Options:', options)
    return 'Date not available'
  }
}

/**
 * Calculate duration between two dates
 * @param {Date|string|Object} startDate - Event start date
 * @param {Date|string|Object} endDate - Event end date
 * @returns {Object} Duration information {minutes, hours, days, formatted}
 */
export function calculateEventDuration(startDate, endDate) {
  const start = parseEventDate(startDate)
  const end = parseEventDate(endDate)

  if (!start || !end || !isValid(start) || !isValid(end)) {
    return {
      minutes: 0,
      hours: 0,
      days: 0,
      formatted: 'Duration not available',
    }
  }

  try {
    const totalMinutes = Math.abs(differenceInMinutes(end, start))
    const totalDays = Math.abs(differenceInDays(end, start))

    // For all-day events or multi-day events
    if (totalDays >= 1) {
      const days = totalDays
      return {
        minutes: totalMinutes,
        hours: Math.round(totalMinutes / 60),
        days: days,
        formatted: days === 1 ? '1 day' : `${days} days`,
      }
    }

    // For timed events
    const hours = Math.floor(totalMinutes / 60)
    const minutes = totalMinutes % 60

    let formatted = ''
    if (hours > 0) {
      formatted += `${hours}h`
      if (minutes > 0) {
        formatted += ` ${minutes}m`
      }
    } else {
      formatted = `${minutes}m`
    }

    return {
      minutes: totalMinutes,
      hours: Math.round(totalMinutes / 60),
      days: 0,
      formatted,
    }
  } catch (error) {
    console.warn('Duration calculation failed:', error, 'Start:', startDate, 'End:', endDate)
    return {
      minutes: 0,
      hours: 0,
      days: 0,
      formatted: 'Duration not available',
    }
  }
}

/**
 * Format relative time with enhanced options
 * @param {Date|string|Object} dateInput - Date to format
 * @param {Object} options - Formatting options
 * @param {boolean} options.addSuffix - Add "ago" or "in" suffix
 * @param {boolean} options.includeSeconds - Include seconds in output
 * @returns {string} Relative time string
 */
export function formatRelativeTime(dateInput, options = {}) {
  const { addSuffix = true, includeSeconds = false } = options

  const date = parseEventDate(dateInput)
  if (!date || !isValid(date)) {
    return 'Date not available'
  }

  try {
    return formatDistanceToNow(date, {
      addSuffix,
      includeSeconds,
    })
  } catch (error) {
    console.warn('Relative time formatting failed:', error, 'Date:', dateInput)
    return 'Date not available'
  }
}

/**
 * Get user's timezone or fallback to UTC
 * @returns {string} IANA timezone identifier
 */
export function getUserTimezone() {
  try {
    return Intl.DateTimeFormat().resolvedOptions().timeZone || 'UTC'
  } catch (error) {
    console.warn('Could not determine user timezone, falling back to UTC')
    return 'UTC'
  }
}
