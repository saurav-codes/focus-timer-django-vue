<script setup>
import { ref } from 'vue';

// Mock calendar data
const calendarEvents = ref([
  {
    id: 1,
    title: 'Team Standup',
    date: new Date(new Date().setHours(10, 0, 0)),
    duration: 30, // minutes
    color: '#89b4fa'
  },
  {
    id: 2,
    title: 'Product Review',
    date: new Date(new Date().setHours(13, 0, 0)),
    duration: 60,
    color: '#f38ba8'
  },
  {
    id: 3,
    title: 'Client Meeting',
    date: new Date(new Date().setHours(15, 30, 0)),
    duration: 45,
    color: '#a6e3a1'
  }
]);

// Format time (e.g., "10:00 AM")
const formatTime = (date) => {
  return date.toLocaleTimeString('en-US', {
    hour: 'numeric',
    minute: '2-digit',
    hour12: true
  });
};

// Get event duration in human-readable format
const getEventDuration = (minutes) => {
  if (minutes < 60) {
    return `${minutes}m`;
  }
  const hours = Math.floor(minutes / 60);
  const remainingMinutes = minutes % 60;
  return remainingMinutes > 0 ? `${hours}h ${remainingMinutes}m` : `${hours}h`;
};
</script>

<template>
  <div class="calendar-integration">
    <div class="integration-header">
      <h3>Calendar</h3>
      <div class="date-display">
        {{ new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'short', day: 'numeric' }) }}
      </div>
    </div>

    <div class="events-list">
      <div v-for="event in calendarEvents" :key="event.id" class="event-card">
        <div class="event-time">
          {{ formatTime(event.date) }}
        </div>
        <div class="event-details">
          <div class="event-title">
            {{ event.title }}
          </div>
          <div class="event-duration">
            {{ getEventDuration(event.duration) }}
          </div>
        </div>
        <div class="event-color" :style="{ backgroundColor: event.color }" />
      </div>

      <div v-if="calendarEvents.length === 0" class="no-events">
        No events scheduled for today
      </div>
    </div>
  </div>
</template>

<style scoped>
.calendar-integration {
  padding: 16px;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.integration-header {
  margin-bottom: 20px;
}

.integration-header h3 {
  margin: 0 0 4px 0;
  font-size: 18px;
  font-weight: 600;
  color: var(--color-text, #cdd6f4);
}

.date-display {
  font-size: 14px;
  color: var(--color-text-secondary, #a6adc8);
}

.events-list {
  flex: 1;
}

.event-card {
  display: flex;
  align-items: center;
  padding: 12px;
  margin-bottom: 8px;
  background-color: var(--color-background, #1e1e2e);
  border-radius: 8px;
  border: 1px solid var(--color-border, #313244);
}

.event-time {
  font-size: 14px;
  font-weight: 500;
  color: var(--color-text-secondary, #a6adc8);
  width: 80px;
}

.event-details {
  flex: 1;
}

.event-title {
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 4px;
}

.event-duration {
  font-size: 12px;
  color: var(--color-text-tertiary, #7f849c);
}

.event-color {
  width: 4px;
  height: 36px;
  border-radius: 2px;
  margin-left: 12px;
}

.no-events {
  text-align: center;
  padding: 24px;
  color: var(--color-text-tertiary, #7f849c);
  font-style: italic;
}
</style>
