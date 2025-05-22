<script setup>
import { ref, onMounted, onBeforeUnmount, watch, computed} from 'vue';
import { useIntervalFn } from '@vueuse/core';
import { useCalendarStore } from '../../../stores/calendarStore';
import { useAuthStore } from '../../../stores/authStore';
import { useTaskStore } from '../../../stores/taskstore';
import { LucideCalendar, LucideLink, LucideUnlink } from 'lucide-vue-next';
import dayGridPlugin from '@fullcalendar/daygrid';
import timeGridPlugin from '@fullcalendar/timegrid';
import interactionPlugin, { ThirdPartyDraggable } from '@fullcalendar/interaction';
import listPlugin from '@fullcalendar/list';
import FullCalendar from '@fullcalendar/vue3';
import Popper from 'vue3-popper';

const calendarStore = useCalendarStore();
const taskStore = useTaskStore();
const authStore = useAuthStore();
const isConnected = ref(false);
const isLoading = ref(false);
const showPopper = ref(false);
// Reference to FullCalendar instance
const calendarRef = ref(null);

const { pause: stopPolling } = useIntervalFn(
  () => {
    if (calendarRef.value) {
      calendarRef.value.getApi().refetchEvents();
    }
  },
  3 * 60 * 1000 // 3 minutes
);

onBeforeUnmount(() => {
  stopPolling();

  // Clean up the draggable instance to prevent memory leaks
  if (draggableInstance.value) {
    draggableInstance.value.destroy();
    draggableInstance.value = null;
  }
});

const calendarError = computed(() => {
  return calendarStore.error
})

// Store reference to the draggable instance
const draggableInstance = ref(null);

onMounted(async () => {
  isLoading.value = true;
  isConnected.value = await calendarStore.checkGoogleConnection();
  isLoading.value = false;

  // Initialize a single draggable instance for calendar integration only
  // Use a more specific selector to avoid conflicts with vuedraggable
  // Only target task items that are not being handled by vuedraggable
  draggableInstance.value = new ThirdPartyDraggable(document.body, {
    itemSelector: ".task-item",
    mirrorSelector: ".task-item",
    // Add event data to make dragging work properly
    eventData: function(eventEl) {
      // Get the event data from the element's dataset
      if (eventEl.dataset.event) {
        const eventData = JSON.parse(eventEl.dataset.event);
        // Event data available for drag operation
        return {
          ...eventData,
        };
      }
      return null;
    }
  });

  // show alert if calendarstore have error
  watch(calendarError, (new_error) => {
    if (new_error) {
      alert(new_error);
      calendarStore.error = null;
    }
  }, {deep:true})
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

async function handleTaskDropped(dropInfo) {
  // Triggers when task dropped into calendar sidebar from external
  try {
    // Ensure we have valid data from the dragged element
    if (!dropInfo.draggedEl || !dropInfo.draggedEl.dataset.event) {
      // No valid task data found in dragged element
      return false; // Return false to prevent the post drop action
    }

    const droppedTask = JSON.parse(dropInfo.draggedEl.dataset.event);

    // Update task status and start time
    droppedTask.status = "ON_CAL";
    droppedTask.column_date = null;
    droppedTask.start_at = dropInfo.dateStr;

    // First update the task in the database
    await taskStore.updateTask(droppedTask);

    // Then remove it from its source location (kanban or braindump)
    await taskStore.searchAndRemoveTaskFromKanbanOrBraindump(droppedTask.id);

    // remove again after 1 second incase of task was dropped after remove operation
    setTimeout(() => {
      // Remove the task from the calendar after 1 second
      taskStore.searchAndRemoveTaskFromKanbanOrBraindump(droppedTask.id);
    }, 1000);

    return true;

  } catch (error) {
    // Error handling task drop
    alert("Failed to add task to calendar. Please try again.");
    console.log("Error during task drop:", error);
    return false; // Return false to indicate failed drop
  }
}

function fetchCalendarEvents(fetchInfo, successCallback, failureCallback) {
  // Fetching calendar events
  const axiosInstance = authStore.axios_instance;
  axiosInstance.get('/api/gcalendar/events/', {
    params: {
      start: fetchInfo.startStr,
      end: fetchInfo.endStr
    }
  })
  .then(res => successCallback(res.data))
  .catch(err => {
    failureCallback(err);
  });
}

async function handleCalendarEventUpdated( eventDropInfo ) {
  // Triggers when events are draggedend inside the calendar sidebar
  const eventSource = eventDropInfo.event.extendedProps.source
  if (eventSource === "google") {
    // Updating Google Calendar event after drag
    const updates = {
      start: {
        dateTime: eventDropInfo.event.start.toISOString(),
        timeZone: Intl.DateTimeFormat().resolvedOptions().timeZone
      },
      end: {
        dateTime: eventDropInfo.event.end.toISOString(),
        timeZone: Intl.DateTimeFormat().resolvedOptions().timeZone
      }
    };
    const updated = await calendarStore.updateGoogleCalendarEvent(eventDropInfo.event.id, updates)
    if (updated === false) {
      eventDropInfo.revert()
    }
  } else {
    alert("event is dropped but not a google event so handle it")
  }
}

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
  events: fetchCalendarEvents,
  selectable: false,
  eventResizableFromStart: true,
  editable: true,
  droppable: true,
  // Other calendar options...
  drop: handleTaskDropped,
  eventDrop: handleCalendarEventUpdated,
  eventResize: handleCalendarEventUpdated,
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
