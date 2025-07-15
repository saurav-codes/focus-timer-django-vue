<script setup>
import { X, Calendar as CalendarIcon } from 'lucide-vue-next'

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

console.log(props.event)
const emit = defineEmits(['close-modal'])

function closeModal() {
  console.log("emiting to close google cal event modal")
  emit('close-modal')
}
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
          <div class="form-group">
            <label class="form-label">Title</label>
            <div class="info-value">
              {{ props.event.summary || 'No Title' }}
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">Time</label>
            <div class="info-value">
              <div><strong>Start:</strong> {{ props.event.start }}</div>
              <div><strong>End:</strong> {{ props.event.end }}</div>
            </div>
          </div>

          <div v-if="props.event.description" class="form-group">
            <label class="form-label">Description</label>
            <div class="info-value description">
              {{ props.event.description }}
            </div>
          </div>

          <div v-if="props.event.location" class="form-group">
            <label class="form-label">Location</label>
            <div class="info-value">
              {{ props.event.location }}
            </div>
          </div>

          <div v-if="props.event.attendees && props.event.attendees.length > 0" class="form-group">
            <label class="form-label">Attendees ({{ props.event.attendees.length }})</label>
            <div class="attendees-list">
              <div v-for="attendee in props.event.attendees" :key="attendee.email" class="attendee-item">
                <div class="attendee-name">
                  {{ attendee.displayName || attendee.email }}
                </div>
                <div class="attendee-status" :class="attendee.responseStatus">
                  {{ attendee.responseStatus }}
                </div>
              </div>
            </div>
          </div>

          <div v-if="props.event.recurringEventId" class="form-group">
            <label class="form-label">Recurring Event</label>
            <div class="info-value">
              This is part of a recurring series
            </div>
          </div>

          <div v-if="props.event.status" class="form-group">
            <label class="form-label">Status</label>
            <div class="info-value" :class="props.event.status">
              {{ props.event.status }}
            </div>
          </div>

          <div v-if="props.event.htmlLink" class="form-group">
            <label class="form-label">Google Calendar</label>
            <div class="info-value">
              <a :href="props.event.htmlLink" target="_blank" class="calendar-link">
                View in Google Calendar
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
</style>
