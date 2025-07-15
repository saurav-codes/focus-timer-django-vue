<script setup>
import { X, Calendar as CalendarIcon, Clock, MapPin, Users, Link, Info, Eye, ExternalLink } from 'lucide-vue-next'
import { computed } from 'vue'
import {
  format,
  parseISO,
  isValid,
  formatDistanceToNow,
  differenceInMinutes
} from 'date-fns'

const props = defineProps({
  event: {
    type: Object,
    required: true,
  },
  isOpen: {
    type: Boolean,
    required: true,
  },
})

console.log('Raw event data:', props.event)
const emit = defineEmits(['close-modal'])

function closeModal() {
  console.log("emiting to close google cal event modal")
  emit('close-modal')
}

// Helper function to parse and format date/time with timezone support
const formatDateTime = (dateObj, options = {}) => {
  if (!dateObj) return 'Not specified'

  const { includeTime = true, includeTimezone = true } = options

  let parsedDate
  let timezone = null

  try {
    // Handle Google Calendar format
    if (dateObj.dateTime) {
      parsedDate = parseISO(dateObj.dateTime)
      timezone = dateObj.timeZone
    } else if (dateObj.date) {
      // All-day event
      parsedDate = parseISO(dateObj.date + 'T00:00:00')
      includeTime = false
    }
    // Handle FullCalendar format
    else if (dateObj instanceof Date) {
      parsedDate = dateObj
    }
    // Handle ISO string
    else if (typeof dateObj === 'string') {
      parsedDate = parseISO(dateObj)
    }
    // Handle timestamp
    else if (typeof dateObj === 'number') {
      parsedDate = new Date(dateObj)
    }

    if (!parsedDate || !isValid(parsedDate)) {
      return 'Invalid date'
    }

    // Format based on whether it includes time and timezone
    if (!includeTime) {
      return format(parsedDate, 'PPPP') // Full date only
    }

    // Use basic formatting with timezone info if available
    let formattedDate = format(parsedDate, 'PPPp') // Full date and time

    if (includeTimezone && timezone) {
      formattedDate += ` (${timezone})`
    }

    return formattedDate

  } catch (error) {
    console.error('Error parsing date:', error, dateObj)
    return 'Invalid date'
  }
}

// Helper function to get duration between two dates
const getEventDuration = (start, end) => {
  if (!start || !end) return null

  try {
    let startDate, endDate

    // Parse start date
    if (start.dateTime) {
      startDate = parseISO(start.dateTime)
    } else if (start.date) {
      startDate = parseISO(start.date + 'T00:00:00')
    } else if (start instanceof Date) {
      startDate = start
    } else if (typeof start === 'string') {
      startDate = parseISO(start)
    }

    // Parse end date
    if (end.dateTime) {
      endDate = parseISO(end.dateTime)
    } else if (end.date) {
      endDate = parseISO(end.date + 'T00:00:00')
    } else if (end instanceof Date) {
      endDate = end
    } else if (typeof end === 'string') {
      endDate = parseISO(end)
    }

    if (!startDate || !endDate || !isValid(startDate) || !isValid(endDate)) {
      return null
    }

    const minutes = differenceInMinutes(endDate, startDate)

    if (minutes < 60) {
      return `${minutes} minutes`
    } else if (minutes < 1440) { // Less than 24 hours
      const hours = Math.floor(minutes / 60)
      const remainingMinutes = minutes % 60
      return remainingMinutes > 0 ? `${hours}h ${remainingMinutes}m` : `${hours}h`
    } else {
      const days = Math.floor(minutes / 1440)
      const remainingHours = Math.floor((minutes % 1440) / 60)
      return remainingHours > 0 ? `${days}d ${remainingHours}h` : `${days}d`
    }
  } catch (error) {
    console.error('Error calculating duration:', error)
    return null
  }
}

// Helper function to format relative time
const formatRelativeTime = (dateObj) => {
  if (!dateObj) return null

  try {
    let parsedDate

    if (dateObj.dateTime) {
      parsedDate = parseISO(dateObj.dateTime)
    } else if (dateObj.date) {
      parsedDate = parseISO(dateObj.date + 'T00:00:00')
    } else if (dateObj instanceof Date) {
      parsedDate = dateObj
    } else if (typeof dateObj === 'string') {
      parsedDate = parseISO(dateObj)
    }

    if (!parsedDate || !isValid(parsedDate)) {
      return null
    }

    return formatDistanceToNow(parsedDate, { addSuffix: true })
  } catch (error) {
    console.error('Error formatting relative time:', error)
    return null
  }
}

// Computed properties for better data parsing
const eventTitle = computed(() => {
  return props.event.title || props.event.summary || 'Untitled Event'
})

const eventStart = computed(() => {
  return formatDateTime(props.event.start)
})

const eventEnd = computed(() => {
  return formatDateTime(props.event.end)
})

const eventDuration = computed(() => {
  return getEventDuration(props.event.start, props.event.end)
})

const eventStartRelative = computed(() => {
  return formatRelativeTime(props.event.start)
})

const isAllDay = computed(() => {
  // FullCalendar property
  if (props.event.allDay !== undefined) {
    return props.event.allDay
  }

  // Google Calendar - if only date (no dateTime), it's all day
  if (props.event.start && props.event.start.date && !props.event.start.dateTime) {
    return true
  }

  return false
})

const eventCreator = computed(() => {
  if (props.event.creator) {
    return props.event.creator.displayName || props.event.creator.email
  }
  return null
})

const eventOrganizer = computed(() => {
  if (props.event.organizer) {
    return props.event.organizer.displayName || props.event.organizer.email
  }
  return null
})

const eventVisibility = computed(() => {
  const visibility = props.event.visibility
  if (visibility === 'default') return 'Default'
  if (visibility === 'public') return 'Public'
  if (visibility === 'private') return 'Private'
  if (visibility === 'confidential') return 'Confidential'
  return visibility
})

const eventTransparency = computed(() => {
  const transparency = props.event.transparency
  if (transparency === 'opaque') return 'Busy'
  if (transparency === 'transparent') return 'Free'
  return transparency
})

const conferenceData = computed(() => {
  return props.event.conferenceData
})

const attachments = computed(() => {
  return props.event.attachments || []
})

const extendedProps = computed(() => {
  // FullCalendar extendedProps
  if (props.event.extendedProps) {
    return props.event.extendedProps
  }

  // Google Calendar extendedProperties
  if (props.event.extendedProperties) {
    return {
      ...props.event.extendedProperties.private,
      ...props.event.extendedProperties.shared
    }
  }

  return null
})

const reminders = computed(() => {
  return props.event.reminders
})

const eventCreatedFormatted = computed(() => {
  if (!props.event.created) return null
  try {
    const createdDate = parseISO(props.event.created)
    return isValid(createdDate) ? format(createdDate, 'PPPp') : null
  } catch (error) {
    return null
  }
})

const eventUpdatedFormatted = computed(() => {
  if (!props.event.updated) return null
  try {
    const updatedDate = parseISO(props.event.updated)
    return isValid(updatedDate) ? format(updatedDate, 'PPPp') : null
  } catch (error) {
    return null
  }
})
</script>

<template>
  <Teleport to="body">
    <div v-if="props.isOpen" class="modal-overlay" @click.self="closeModal">
      <div class="readonly-modal">
        <div class="modal-header">
          <h3 class="modal-header-title">
            <CalendarIcon size="18" />
            Event Details
          </h3>
          <button class="close-button" @click="closeModal">
            <X size="18" />
          </button>
        </div>

        <div class="modal-content">
          <!-- Event Title -->
          <div class="form-group">
            <h2 class="event-title">
              {{ eventTitle }}
            </h2>
          </div>

          <div class="form-group">
            <label class="form-label">
              <Clock size="16" />
              Time
            </label>
            <div class="info-value">
              <div class="time-info">
                <div><strong>Start:</strong> {{ eventStart }}</div>
                <div><strong>End:</strong> {{ eventEnd }}</div>
                <div v-if="eventDuration" class="duration-info">
                  <strong>Duration:</strong> {{ eventDuration }}
                </div>
                <div v-if="eventStartRelative" class="relative-time">
                  {{ eventStartRelative }}
                </div>
                <div v-if="isAllDay" class="all-day-badge">All Day Event</div>
              </div>
            </div>
          </div>

          <div v-if="props.event.description" class="form-group">
            <label class="form-label">
              <Info size="16" />
              Description
            </label>
            <div class="info-value description" v-html="props.event.description">
            </div>
          </div>

          <div v-if="props.event.location" class="form-group">
            <label class="form-label">
              <MapPin size="16" />
              Location
            </label>
            <div class="info-value">
              {{ props.event.location }}
            </div>
          </div>

          <!-- People Information -->
          <div v-if="eventCreator" class="form-group">
            <label class="form-label">
              <Users size="16" />
              Created By
            </label>
            <div class="info-value">
              {{ eventCreator }}
            </div>
          </div>

          <div v-if="eventOrganizer" class="form-group">
            <label class="form-label">
              <Users size="16" />
              Organizer
            </label>
            <div class="info-value">
              {{ eventOrganizer }}
            </div>
          </div>

          <div v-if="props.event.attendees && props.event.attendees.length > 0" class="form-group">
            <label class="form-label">
              <Users size="16" />
              Attendees ({{ props.event.attendees.length }})
            </label>
            <div class="attendees-list">
              <div v-for="attendee in props.event.attendees" :key="attendee.email" class="attendee-item">
                <div class="attendee-info">
                  <div class="attendee-name">
                    {{ attendee.displayName || attendee.email }}
                  </div>
                  <div class="attendee-email" v-if="attendee.displayName">
                    {{ attendee.email }}
                  </div>
                </div>
                <div class="attendee-badges">
                  <span v-if="attendee.organizer" class="badge organizer">Organizer</span>
                  <span v-if="attendee.optional" class="badge optional">Optional</span>
                  <span v-if="attendee.self" class="badge self">You</span>
                  <span class="badge status" :class="attendee.responseStatus">
                    {{ attendee.responseStatus || 'needsAction' }}
                  </span>
                </div>
              </div>
            </div>
          </div>

          <!-- Conference/Meeting Information -->
          <div v-if="conferenceData" class="form-group">
            <label class="form-label">
              <Link size="16" />
              Conference
            </label>
            <div class="info-value">
              <div v-if="conferenceData.conferenceSolution" class="conference-solution">
                <strong>{{ conferenceData.conferenceSolution.name }}</strong>
              </div>
              <div v-if="conferenceData.conferenceId" class="conference-id">
                ID: {{ conferenceData.conferenceId }}
              </div>
              <div v-if="conferenceData.entryPoints && conferenceData.entryPoints.length > 0" class="entry-points">
                <div v-for="entryPoint in conferenceData.entryPoints" :key="entryPoint.uri" class="entry-point">
                  <a v-if="entryPoint.uri" :href="entryPoint.uri" target="_blank" class="conference-link">
                    {{ entryPoint.label || entryPoint.entryPointType }}
                  </a>
                  <span v-if="entryPoint.meetingCode" class="meeting-code">
                    Code: {{ entryPoint.meetingCode }}
                  </span>
                </div>
              </div>
            </div>
          </div>

          <div v-if="props.event.hangoutLink" class="form-group">
            <label class="form-label">
              <Link size="16" />
              Hangout Link
            </label>
            <div class="info-value">
              <a :href="props.event.hangoutLink" target="_blank" class="conference-link">
                Join Hangout
              </a>
            </div>
          </div>

          <!-- Attachments -->
          <div v-if="attachments.length > 0" class="form-group">
            <label class="form-label">
              <Link size="16" />
              Attachments ({{ attachments.length }})
            </label>
            <div class="attachments-list">
              <div v-for="attachment in attachments" :key="attachment.fileId" class="attachment-item">
                <a :href="attachment.fileUrl" target="_blank" class="attachment-link">
                  {{ attachment.title }}
                </a>
                <span class="attachment-type">{{ attachment.mimeType }}</span>
              </div>
            </div>
          </div>

          <!-- Recurrence Information -->
          <div v-if="props.event.recurringEventId" class="form-group">
            <label class="form-label">
              <Info size="16" />
              Recurring Event
            </label>
            <div class="info-value">
              This is part of a recurring series
            </div>
          </div>

          <div v-if="props.event.recurrence && props.event.recurrence.length > 0" class="form-group">
            <label class="form-label">
              <Info size="16" />
              Recurrence Rules
            </label>
            <div class="info-value">
              <div v-for="rule in props.event.recurrence" :key="rule" class="recurrence-rule">
                {{ rule }}
              </div>
            </div>
          </div>

          <!-- Reminders -->
          <div v-if="reminders" class="form-group">
            <label class="form-label">
              <Clock size="16" />
              Reminders
            </label>
            <div class="info-value">
              <div v-if="reminders.useDefault">Using default reminders</div>
              <div v-if="reminders.overrides && reminders.overrides.length > 0" class="reminder-overrides">
                <div v-for="reminder in reminders.overrides" :key="reminder.minutes" class="reminder-item">
                  {{ reminder.minutes }} minutes before ({{ reminder.method }})
                </div>
              </div>
            </div>
          </div>

          <!-- Status and Visibility -->
          <div v-if="props.event.status" class="form-group">
            <label class="form-label">
              <Info size="16" />
              Status
            </label>
            <div class="info-value">
              <span class="status-badge" :class="props.event.status">
                {{ props.event.status }}
              </span>
            </div>
          </div>

          <div v-if="eventVisibility" class="form-group">
            <label class="form-label">
              <Eye size="16" />
              Visibility
            </label>
            <div class="info-value">
              {{ eventVisibility }}
            </div>
          </div>

          <div v-if="eventTransparency" class="form-group">
            <label class="form-label">
              <Clock size="16" />
              Show As
            </label>
            <div class="info-value">
              {{ eventTransparency }}
            </div>
          </div>

          <!-- Extended Properties -->
          <div v-if="extendedProps && Object.keys(extendedProps).length > 0" class="form-group">
            <label class="form-label">
              <Info size="16" />
              Additional Properties
            </label>
            <div class="info-value">
              <div v-for="(value, key) in extendedProps" :key="key" class="extended-prop">
                <strong>{{ key }}:</strong> {{ value }}
              </div>
            </div>
          </div>

          <!-- Timestamps -->
          <div v-if="eventCreatedFormatted" class="form-group">
            <label class="form-label">
              <Info size="16" />
              Created
            </label>
            <div class="info-value timestamp">
              {{ eventCreatedFormatted }}
            </div>
          </div>

          <div v-if="eventUpdatedFormatted" class="form-group">
            <label class="form-label">
              <Info size="16" />
              Last Updated
            </label>
            <div class="info-value timestamp">
              {{ eventUpdatedFormatted }}
            </div>
          </div>

          <!-- Calendar Link -->
          <div v-if="props.event.extendedProps.htmlLink" class="form-group">
            <div class="info-value">
              <a :href="props.event.extendedProps.htmlLink" target="_blank" class="calendar-link-button">
                <ExternalLink size="16" />
                Open on Calendar
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 5;
  backdrop-filter: blur(2px);
}

.readonly-modal {
  background-color: var(--color-background);
  border-radius: 0.5rem;
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  box-shadow: var(--shadow-lg);
  animation: modal-appear 0.2s ease-out;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  overflow-y: scroll;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid var(--color-border);
}

.modal-header-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.close-button {
  background: transparent;
  border: none;
  color: var(--color-text-tertiary);
  cursor: pointer;
  padding: 0.25rem;
  border-radius: 0.25rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-button:hover {
  background-color: var(--color-background-secondary);
  color: var(--color-text-primary);
}

.modal-content {
  padding: 1.5rem;
}

.form-group {
  margin-bottom: 1.25rem;
  width: 95%;
}

.form-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: var(--font-weight-medium);
  color: var(--color-text-primary);
  margin-bottom: 0.5rem;
  font-size: var(--font-size-sm);
}

.info-value {
  color: var(--color-text-primary);
  line-height: 1.5;
}

.info-value.description {
  white-space: pre-wrap;
  max-height: 150px;
  overflow-y: auto;
  padding: 0.75rem;
  background: var(--color-input-background);
  border-radius: 0.375rem;
  border: 1px solid var(--color-border);
  font-size: var(--font-size-sm);
}

.info-value.code {
  font-family: var(--font-family-mono);
  background: var(--color-background-secondary);
  padding: 0.5rem;
  border-radius: 0.25rem;
  font-size: var(--font-size-sm);
}

.info-value.timestamp {
  font-size: var(--font-size-sm);
  color: var(--color-text-tertiary);
}

.time-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.duration-info {
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
}

.relative-time {
  color: var(--color-text-tertiary);
  font-size: var(--font-size-sm);
  font-style: italic;
}

.all-day-badge {
  display: inline-block;
  background: var(--color-primary);
  color: white;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-medium);
  margin-top: 0.5rem;
}

.attendees-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.attendee-item {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 0.75rem;
  background: var(--color-background-secondary);
  border-radius: 0.375rem;
  border: 1px solid var(--color-border);
}

.attendee-info {
  flex: 1;
}

.attendee-name {
  font-weight: 500;
  color: var(--color-text-primary);
}

.attendee-email {
  font-size: var(--font-size-sm);
  color: var(--color-text-tertiary);
  margin-top: 0.25rem;
}

.attendee-badges {
  display: flex;
  flex-wrap: wrap;
  gap: 0.25rem;
  align-items: center;
}

.badge {
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-medium);
  text-transform: capitalize;
}

.badge.organizer {
  background: var(--color-primary);
  color: white;
}

.badge.optional {
  background: var(--color-warning);
  color: white;
}

.badge.self {
  background: var(--color-success);
  color: white;
}

.badge.status {
  background: var(--color-background-tertiary);
  color: var(--color-text-secondary);
}

.badge.status.accepted {
  background: var(--color-success);
  color: white;
}

.badge.status.declined {
  background: var(--color-error);
  color: white;
}

.badge.status.tentative {
  background: var(--color-warning);
  color: white;
}

.badge.status.needsAction {
  background: var(--color-background-tertiary);
  color: var(--color-text-secondary);
}

.conference-solution {
  font-weight: 500;
  margin-bottom: 0.5rem;
}

.conference-id {
  font-size: var(--font-size-sm);
  color: var(--color-text-tertiary);
  margin-bottom: 0.5rem;
}

.entry-points {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.entry-point {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.conference-link {
  color: var(--color-primary);
  text-decoration: none;
  font-weight: var(--font-weight-medium);
}

.conference-link:hover {
  text-decoration: underline;
}

.meeting-code {
  font-size: var(--font-size-sm);
  color: var(--color-text-tertiary);
  background: var(--color-background-secondary);
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  font-family: var(--font-family-mono);
}

.attachments-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.attachment-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem;
  background: var(--color-background-secondary);
  border-radius: 0.25rem;
  border: 1px solid var(--color-border);
}

.attachment-link {
  color: var(--color-primary);
  text-decoration: none;
  font-weight: var(--font-weight-medium);
}

.attachment-link:hover {
  text-decoration: underline;
}

.attachment-type {
  font-size: var(--font-size-xs);
  color: var(--color-text-tertiary);
  background: var(--color-background-tertiary);
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
}

.recurrence-rule {
  font-family: var(--font-family-mono);
  font-size: var(--font-size-sm);
  background: var(--color-background-secondary);
  padding: 0.5rem;
  border-radius: 0.25rem;
  margin-bottom: 0.5rem;
}

.reminder-overrides {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.reminder-item {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.status-badge {
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  text-transform: capitalize;
}

.status-badge.confirmed {
  background: var(--color-success);
  color: white;
}

.status-badge.tentative {
  background: var(--color-warning);
  color: white;
}

.status-badge.cancelled {
  background: var(--color-error);
  color: white;
}

.extended-prop {
  margin-bottom: 0.5rem;
  font-size: var(--font-size-sm);
}

.extended-prop:last-child {
  margin-bottom: 0;
}

.calendar-link {
  color: var(--color-primary);
  text-decoration: none;
  font-weight: var(--font-weight-medium);
}

.calendar-link:hover {
  text-decoration: underline;
}

.event-title {
  font-size: var(--font-size-2xl);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin: 0 0 0.5rem 0;
  line-height: var(--line-height-tight);
}

.calendar-link-button {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.625rem 1rem;
  background: transparent;
  color: var(--color-text-secondary);
  text-decoration: none;
  border-radius: 0.375rem;
  border: 1px solid var(--color-border);
  font-weight: var(--font-weight-medium);
  font-size: var(--font-size-sm);
  transition: background-color var(--transition-base);
}

.calendar-link-button:hover {
  background-color: var(--color-background-secondary);
  color: var(--color-text-primary);
  text-decoration: none;
}

@keyframes modal-appear {
  from {
    opacity: 0;
    transform: scale(0.9);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}
</style>
