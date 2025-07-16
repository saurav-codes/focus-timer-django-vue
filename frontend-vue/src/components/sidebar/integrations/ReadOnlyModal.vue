<script setup>
import { X, Calendar as CalendarIcon, Clock, MapPin, Users, Link, Info, Eye, ExternalLink, Video, Phone } from 'lucide-vue-next'
import { computed } from 'vue'
import {
  parseEventDate,
  formatEventDateTime,
  calculateEventDuration,
  formatRelativeTime,
  isAllDayEvent,
  getUserTimezone,
} from '../../../utils/dateParsingUtils'

import {
  normalizeEventData,
  getResponseStatusLabel,
  getEventStatusLabel,
  getTransparencyLabel,
  getVisibilityLabel,
  getAttendeeInitials,
  hasConferenceData
} from '../../../utils/eventDataNormalizer'


const props = defineProps({
  event: {
    type: Object,
    default: () => ({})
  },
  isOpen: Boolean
})

const emit = defineEmits(['close-modal'])

const closeModal = () => emit('close-modal')

// Normalize the event data using our utility
const normalizedEvent = computed(() => normalizeEventData(props.event))

// Event basic information
const eventTitle = computed(() => normalizedEvent.value.title)
const eventDescription = computed(() => normalizedEvent.value.description)
const eventLocation = computed(() => normalizedEvent.value.location)

// Date and time computations using our new utilities
const eventStart = computed(() => {
  const startDate = parseEventDate(normalizedEvent.value.start)
  if (!startDate) return 'Date not available'

  const userTz = getUserTimezone()
  const formatOptions = {
    format: isAllDay.value ? 'date' : 'full',
    timezone: userTz,
    relative: false
  }

  return formatEventDateTime(startDate, formatOptions)
})

const eventEnd = computed(() => {
  const endDate = parseEventDate(normalizedEvent.value.end)
  if (!endDate) return 'Date not available'

  const userTz = getUserTimezone()
  const formatOptions = {
    format: isAllDay.value ? 'date' : 'full',
    timezone: userTz,
    relative: false
  }

  return formatEventDateTime(endDate, formatOptions)
})

const eventDuration = computed(() => {
  const duration = calculateEventDuration(normalizedEvent.value.start, normalizedEvent.value.end)
  return duration.formatted
})

const eventStartRelative = computed(() => {
  const startDate = parseEventDate(normalizedEvent.value.start)
  if (!startDate) return null

  return formatRelativeTime(startDate, { addSuffix: true })
})

const isAllDay = computed(() => {
  return isAllDayEvent(normalizedEvent.value.start, normalizedEvent.value.end)
})

// People information
const eventCreator = computed(() => {
  const creator = normalizedEvent.value.creator
  return creator ? (creator.displayName || creator.email) : null
})

const eventOrganizer = computed(() => {
  const organizer = normalizedEvent.value.organizer
  return organizer ? (organizer.displayName || organizer.email) : null
})

const attendees = computed(() => normalizedEvent.value.attendees)

// Conference and meeting information
const conferenceInfo = computed(() => normalizedEvent.value.conferenceData)
const hangoutLink = computed(() => normalizedEvent.value.hangoutLink)
const hasConferenceInfo = computed(() => hasConferenceData(conferenceInfo.value) || hangoutLink.value)

// Status and metadata
const eventStatus = computed(() => getEventStatusLabel(normalizedEvent.value.status))
const eventVisibility = computed(() => getVisibilityLabel(normalizedEvent.value.visibility))
const eventTransparency = computed(() => getTransparencyLabel(normalizedEvent.value.transparency))

// Timestamps
const eventCreated = computed(() => {
  const created = parseEventDate(normalizedEvent.value.created)
  return created ? formatEventDateTime(created, { format: 'compact' }) : null
})

const eventUpdated = computed(() => {
  const updated = parseEventDate(normalizedEvent.value.updated)
  return updated ? formatEventDateTime(updated, { format: 'compact' }) : null
})

// Attachments and reminders
const attachments = computed(() => normalizedEvent.value.attachments)
const reminders = computed(() => normalizedEvent.value.reminders)

// Helper functions for attendee display
const getAttendeeStatusClass = (attendee) => `avatar-${attendee.responseStatus || 'needsAction'}`

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
                <div v-if="isAllDay" class="all-day-badge">
                  All Day Event
                </div>
              </div>
            </div>
          </div>

          <div v-if="eventDescription" class="form-group">
            <label class="form-label">
              <Info size="16" />
              Description
            </label>
            <div class="info-value description" v-text="eventDescription" />
          </div>

          <div v-if="eventLocation" class="form-group">
            <label class="form-label">
              <MapPin size="16" />
              Location
            </label>
            <div class="info-value">
              {{ eventLocation }}
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

          <div v-if="attendees && attendees.length > 0" class="form-group">
            <label class="form-label">
              <Users size="16" />
              Attendees ({{ attendees.length }})
            </label>
            <div class="attendees-grid">
              <div v-for="attendee in attendees" :key="attendee.email" class="attendee-card">
                <div class="attendee-avatar">
                  <div class="avatar-circle" :class="getAttendeeStatusClass(attendee)">
                    {{ getAttendeeInitials(attendee) }}
                  </div>
                </div>
                <div class="attendee-content">
                  <div class="attendee-header">
                    <div class="attendee-name">
                      {{ attendee.displayName || attendee.email }}
                    </div>
                    <div class="attendee-status">
                      <span class="status-indicator" :class="attendee.responseStatus">
                        {{ getResponseStatusLabel(attendee.responseStatus) }}
                      </span>
                    </div>
                  </div>
                  <div v-if="attendee.displayName && attendee.email !== attendee.displayName" class="attendee-email">
                    {{ attendee.email }}
                  </div>
                  <div v-if="attendee.organizer || attendee.optional || attendee.self" class="attendee-badges">
                    <span v-if="attendee.organizer" class="badge organizer-badge">
                      <Users size="10" />
                      Organizer
                    </span>
                    <span v-if="attendee.optional" class="badge optional-badge">Optional</span>
                    <span v-if="attendee.self" class="badge self-badge">You</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Conference/Meeting Information -->
          <div v-if="hasConferenceInfo" class="form-group">
            <label class="form-label">
              <Video size="16" />
              Meeting
            </label>
            <div class="info-value">
              <!-- Hangout Link (Google Meet) -->
              <div v-if="hangoutLink" class="conference-entry">
                <a :href="hangoutLink" target="_blank" class="conference-link primary-meeting-link">
                  <Video size="16" />
                  Join Google Meet
                </a>
              </div>

              <!-- Conference Data -->
              <div v-if="conferenceInfo">
                <div v-if="conferenceInfo.conferenceSolution" class="conference-solution">
                  <strong>{{ conferenceInfo.conferenceSolution.name }}</strong>
                </div>
                <div v-if="conferenceInfo.conferenceId" class="conference-id">
                  Meeting ID: {{ conferenceInfo.conferenceId }}
                </div>
                <div v-if="conferenceInfo.entryPoints && conferenceInfo.entryPoints.length > 0" class="entry-points">
                  <div v-for="entryPoint in conferenceInfo.entryPoints" :key="entryPoint.uri" class="entry-point">
                    <a v-if="entryPoint.uri" :href="entryPoint.uri" target="_blank" class="conference-link">
                      <Video v-if="entryPoint.entryPointType === 'video'" size="14" />
                      <Phone v-else-if="entryPoint.entryPointType === 'phone'" size="14" />
                      <Link v-else size="14" />
                      {{ entryPoint.label || entryPoint.entryPointType }}
                    </a>
                    <div v-if="entryPoint.meetingCode || entryPoint.accessCode" class="meeting-codes">
                      <span v-if="entryPoint.meetingCode" class="meeting-code">
                        Code: {{ entryPoint.meetingCode }}
                      </span>
                      <span v-if="entryPoint.accessCode" class="meeting-code">
                        Access: {{ entryPoint.accessCode }}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
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
          <div v-if="normalizedEvent.recurringEventId" class="form-group">
            <label class="form-label">
              <Info size="16" />
              Recurring Event
            </label>
            <div class="info-value">
              This is part of a recurring series
            </div>
          </div>

          <div v-if="normalizedEvent.recurrence && normalizedEvent.recurrence.length > 0" class="form-group">
            <label class="form-label">
              <Info size="16" />
              Recurrence Rules
            </label>
            <div class="info-value">
              <div v-for="rule in normalizedEvent.recurrence" :key="rule" class="recurrence-rule">
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
              <div v-if="reminders.useDefault">
                Using default reminders
              </div>
              <div v-if="reminders.overrides && reminders.overrides.length > 0" class="reminder-overrides">
                <div v-for="reminder in reminders.overrides" :key="reminder.minutes" class="reminder-item">
                  {{ reminder.minutes }} minutes before ({{ reminder.method }})
                </div>
              </div>
            </div>
          </div>

          <!-- Status and Visibility -->
          <div v-if="eventStatus && eventStatus !== 'Confirmed'" class="form-group">
            <label class="form-label">
              <Info size="16" />
              Status
            </label>
            <div class="info-value">
              <span class="status-badge" :class="normalizedEvent.status">
                {{ eventStatus }}
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



          <!-- Timestamps -->
          <div v-if="eventCreated" class="form-group">
            <label class="form-label">
              <Info size="16" />
              Created
            </label>
            <div class="info-value timestamp">
              {{ eventCreated }}
            </div>
          </div>

          <div v-if="eventUpdated" class="form-group">
            <label class="form-label">
              <Info size="16" />
              Last Updated
            </label>
            <div class="info-value timestamp">
              {{ eventUpdated }}
            </div>
          </div>

          <!-- Calendar Link -->
          <div v-if="normalizedEvent.htmlLink" class="form-group">
            <div class="info-value">
              <a :href="normalizedEvent.htmlLink" target="_blank" class="calendar-link-button">
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

.attendees-grid {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.attendee-card {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  padding: 1rem;
  background: var(--color-background-secondary);
  border-radius: 0.5rem;
  border: 1px solid var(--color-border);
  transition: all var(--transition-base);
}

.attendee-card:hover {
  background: var(--color-background-tertiary);
  transform: translateY(-1px);
  box-shadow: var(--shadow-sm);
}

.attendee-avatar {
  flex-shrink: 0;
}

.avatar-circle {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: var(--font-weight-semibold);
  font-size: var(--font-size-sm);
  color: white;
  background: var(--color-neutral-400);
  border: 2px solid var(--color-background);
}

.avatar-circle.avatar-accepted {
  background: var(--color-success);
}

.avatar-circle.avatar-declined {
  background: var(--color-error);
}

.avatar-circle.avatar-tentative {
  background: var(--color-warning);
}

.avatar-circle.avatar-needsAction {
  background: var(--color-neutral-400);
}

.attendee-content {
  flex: 1;
  min-width: 0;
}

.attendee-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.25rem;
}

.attendee-name {
  font-weight: var(--font-weight-medium);
  color: var(--color-text-primary);
  font-size: var(--font-size-base);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  flex: 1;
}

.attendee-status {
  flex-shrink: 0;
  margin-left: 0.5rem;
}

.status-indicator {
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-medium);
  padding: 0.25rem 0.5rem;
  border-radius: 0.375rem;
  text-transform: uppercase;
  letter-spacing: 0.025em;
}

.status-indicator.accepted {
  background: var(--color-success);
  color: white;
}

.status-indicator.declined {
  background: var(--color-error);
  color: white;
}

.status-indicator.tentative {
  background: var(--color-warning);
  color: white;
}

.status-indicator.needsAction {
  background: var(--color-background-tertiary);
  color: var(--color-text-secondary);
  border: 1px solid var(--color-border);
}

.attendee-email {
  font-size: var(--font-size-sm);
  color: var(--color-text-tertiary);
  margin-bottom: 0.5rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.attendee-badges {
  display: flex;
  flex-wrap: wrap;
  gap: 0.25rem;
  align-items: center;
}

.badge {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.125rem 0.375rem;
  border-radius: 0.25rem;
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-medium);
  text-transform: none;
}

.organizer-badge {
  background: var(--color-primary);
  color: white;
}

.optional-badge {
  background: var(--color-warning);
  color: white;
}

.self-badge {
  background: var(--color-secondary);
  color: white;
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

.primary-meeting-link {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  background: var(--color-primary);
  color: white;
  text-decoration: none;
  border-radius: 0.5rem;
  font-weight: var(--font-weight-medium);
  margin-bottom: 1rem;
  transition: all var(--transition-base);
}

.primary-meeting-link:hover {
  background: var(--color-primary-dark);
  transform: translateY(-1px);
  box-shadow: var(--shadow-sm);
  text-decoration: none;
  color: white;
}

.conference-entry {
  margin-bottom: 1rem;
}

.entry-point {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  margin-bottom: 0.5rem;
}

.meeting-codes {
  display: flex;
  gap: 0.5rem;
  margin-top: 0.25rem;
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
