<script setup>
import { ref, onMounted } from 'vue';
import { useCalendarStore } from '../../../stores/calendarStore';
import { LucideCalendar, LucideLink, LucideUnlink } from 'lucide-vue-next';
import dayGridPlugin from '@fullcalendar/daygrid';
import timeGridPlugin from '@fullcalendar/timegrid';
import interactionPlugin from '@fullcalendar/interaction';
import listPlugin from '@fullcalendar/list';
import FullCalendar from '@fullcalendar/vue3';
import Popper from 'vue3-popper';

const calendarStore = useCalendarStore();
const isConnected = ref(false);
const isLoading = ref(false);
const showPopper = ref(false);

onMounted(async () => {
  isLoading.value = true;
  isConnected.value = await calendarStore.checkGoogleConnection();
  isLoading.value = false;
});

const connectGoogleCalendar = () => {
  calendarStore.startGoogleAuth();
};

const disconnectGoogleCalendar = async () => {
  isLoading.value = true;
  await calendarStore.disconnectGoogleCalendar();
  isConnected.value = false;
  isLoading.value = false;
};

const calendarOptions = ref({
  plugins: [dayGridPlugin, timeGridPlugin, interactionPlugin, listPlugin],
  initialView: 'timeGridDay',
  headerToolbar: false,
  allDaySlot: false,
  eventTimeFormat: {
    hour: '2-digit',
    minute: '2-digit',
    meridiem: false
  },
  slotMinTime: '00:00:00',
  slotMaxTime: '23:59:00',
  height: 'auto',
  expandRows: true,
  stickyHeaderDates: false,
  navLinks: false,
  dayMaxEvents: false,
  // eventClick: handleEventClick,
  // dateClick: handleDateClick,
  // datesSet: handleDatesSet,
  // events: events.value
  selectable: true,
});
</script>

<template>
  <div class="calendar-integration">
    <div class="integration-header">
      <div class="left-header">
        <h3>
          <LucideCalendar :size="14" />
          Calendar
        </h3>
        <div class="date-display">
          {{ new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'short', day: 'numeric' }) }}
        </div>
      </div>
      <Popper v-if="isConnected" arrow content="Disconnect Google Calendar" :show="showPopper">
        <LucideUnlink
          class="disconnect-button"
          :class="{'disabled-div': isLoading}"
          :size="14"
          @mouseover="showPopper=true"
          @mouseleave="showPopper=false"
          @click="disconnectGoogleCalendar" />
      </Popper>
    </div>
    <div class="google-calendar-connect">
      <div v-if="isLoading" class="loading">
        <div class="spinner" />
        <span>Loading...</span>
      </div>
      <div v-else-if="!isConnected" class="connect-prompt">
        <p>Sync your tasks with Google Calendar to manage your schedule more effectively.</p>
        <button
          class="connect-button"
          :disabled="calendarStore.isLoading"
          @click="connectGoogleCalendar">
          {{ calendarStore.isLoading ? 'Connecting...' : 'Connect Google Calendar' }}
          <div v-if="!calendarStore.isLoading">
            <LucideLink class="link-icon" size="16" />
          </div>
        </button>
      </div>

      <!-- Render FullCalendar component here -->
      <FullCalendar v-else :options="calendarOptions" />
    </div>
  </div>
</template>

<style scoped>
.calendar-integration {
  height: 100%;
  display: flex;
  flex-direction: column;
  flex: 1;
}

.integration-header {
  margin-bottom: 20px;
  display: flex;
  justify-content: space-between;
  padding-left: 0.4rem;
  padding-right: 0.4rem;
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
.google-calendar-connect {
  background-color: var(--color-background);
  border-radius: 0.5rem;
  margin-bottom: 1.5rem;
  border: 1px solid var(--color-border);
}

.loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  padding: 1rem;
}

.spinner {
  width: 20px;
  height: 20px;
  border: 2px solid rgba(0, 0, 0, 0.1);
  border-top-color: var(--color-primary);
  border-radius: 50%;
  animation: spinner 0.8s linear infinite;
}

@keyframes spinner {
  to {transform: rotate(360deg);}
}

.connect-prompt {
  text-align: center;
}

.connect-prompt h3 {
  margin-top: 0;
  margin-bottom: 0.5rem;
  font-size: var(--font-size-lg);
}

.connect-prompt p {
  color: var(--color-text-secondary);
  margin-bottom: 1.5rem;
}

.connect-button, .disconnect-button {
  background-color: var(--color-primary);
  color: white;
  border: none;
  border-radius: 0.375rem;
  padding: 0.75rem 1.5rem;
  font-weight: var(--font-weight-medium);
  cursor: pointer;
  transition: background-color 0.2s;
}

.connect-button:hover, .disconnect-button:hover {
  background-color: var(--color-primary-dark);
}

.connect-button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.disconnect-button {
  background-color: var(--color-error);
  margin-top: 1rem;
  padding: 0.3rem;
  background: transparent;
}

.disconnect-button:hover {
  background-color: var(--color-error-dark, #dc2626);
}

.disabled-div {
  pointer-events: none;
  opacity: 0.5;
  cursor: not-allowed;
}

</style>
