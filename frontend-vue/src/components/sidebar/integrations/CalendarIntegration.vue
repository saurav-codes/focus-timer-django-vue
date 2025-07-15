<script setup>
import { ref, onMounted, onBeforeUnmount, onUnmounted, watch, computed, } from 'vue'
import { useCalendarStore } from '../../../stores/calendarStore'
import { useTaskStoreWs } from '../../../stores/taskStoreWs'
import { LucideCalendar, LucideLink, LucideUnlink, LucideChevronLeft, LucideChevronRight, } from 'lucide-vue-next'
import dayGridPlugin from '@fullcalendar/daygrid'
import timeGridPlugin from '@fullcalendar/timegrid'
import interactionPlugin, { ThirdPartyDraggable } from '@fullcalendar/interaction'
import listPlugin from '@fullcalendar/list'
import FullCalendar from '@fullcalendar/vue3'
import Popper from 'vue3-popper'
import TaskEditModal from '../../TaskEditModal.vue'
import { calculateEndAt, getDateStrFromDateObj } from '../../../utils/taskUtils'

// Props
const props = defineProps({
  initialView: {
    type: String,
    default: 'timeGridDay',
  },
})

const calendarStore = useCalendarStore()
const taskStore = useTaskStoreWs()

const isConnected = ref(false)
const isLoading = ref(false)
const showPopper = ref(false)

// Reference to FullCalendar instance
const calendarRef = ref(null)


const localCalTasks = computed(() => taskStore.localCalendarTaskInFcFormat)
const gcalEvents = computed(() => calendarStore.gcalEvents)

// always re-render fullcalendar whenever events changes
watch([localCalTasks, gcalEvents], () => {
  if (calendarRef.value) {
    calendarRef.value.getApi().removeAllEvents()  // remove all events currently displayed
    calendarRef.value.getApi().refetchEvents()   // Refetches events from all sources and rerenders them on the screen.
    console.log("smth changed so all events removed & calendar refetched")
  }
}, { deep: true })

// -------- Calendar Navigation Controls --------
// Tracks the current view date to display in header
const currentDate = ref(new Date())
// Updates currentDate when the calendar view changes
function handleDatesSet(dateInfo) {
  // calling prev/next trigger this function. the dates are already set
  // in fullcalendar and we here are just updating the value
  // on currentDate
  const dt = dateInfo.view.currentStart
  // set time to 0 because later we have to compare 2 dates
  dt.setHours(0,0,0,0)
  currentDate.value = dt
}

// Formatted display for the current date
const currentDateDisplay = computed(() =>{
  return currentDate.value
    ? currentDate.value.toLocaleDateString('en-US', { weekday: 'long', month: 'short', day: 'numeric' })
    : ''
})
// Navigate to previous period
function prev() {
  calendarRef.value?.getApi().prev()
  const leftMostColDt = taskStore.kanbanColumns[0].date
  leftMostColDt.setHours(0,0,0,0)
  if (currentDate.value < leftMostColDt) {
    taskStore.addEarlierColumnsWs(3)
    console.log("Added 3 more col and fetched their tasks since user clicked on date older than what's visible")
  }
  // fetch for the normalized local date
  if (currentDate.value) {
    const dt = getDateStrFromDateObj(currentDate.value)
    calendarStore.fetchGcalTask(dt)
  }
}
// Navigate to next period
function next() {
  calendarRef.value?.getApi().next()
  const rightMostColDt = taskStore.kanbanColumns[taskStore.kanbanColumns.length - 1].date
  rightMostColDt.setHours(0,0,0,0)
  if (currentDate.value > rightMostColDt) {
    taskStore.addMoreColumnsWs(3)
    console.log("Added 3 more col and fetched their tasks since user clicked on date greater than what's visible")
  }
  // fetch for the normalized local date
  if (currentDate.value) {
    const dt = getDateStrFromDateObj(currentDate.value)
    calendarStore.fetchGcalTask(dt)
  }
}
// Determine if the calendar's current view is today
const isToday = computed(() => {
  if (!currentDate.value) return true
  const todayDate = new Date()
  // normalize to midnight
  todayDate.setHours(0, 0, 0, 0)
  // compare timestamps
  return currentDate.value.getTime() === todayDate.getTime()
})
// Jump calendar to today
function today() {
  calendarRef.value?.getApi().today()
}
// -------- Task Edit Modal --------
const isEditModalOpen = ref(false)
const activeTask = ref(null)

function openEditModal(task) {
  activeTask.value = task
  isEditModalOpen.value = true
}

function closeEditModal() {
  isEditModalOpen.value = false
  activeTask.value = null
}

function handleTaskDeleted() {
  closeEditModal()
}

function handleTaskUpdated() {
  // we don't need to update task because
  // websocket request from taskstorews will update the task
  // and all the components will be updated automatically
}

function handleTaskArchived() {
  closeEditModal()
}

onBeforeUnmount(() => {

  // Clean up the draggable instance to prevent memory leaks
  if (draggableInstance.value) {
    draggableInstance.value.destroy()
    draggableInstance.value = null
  }
})

const calendarError = computed(() => {
  return calendarStore.error
})

// Store reference to the draggable instance
const draggableInstance = ref(null)

onMounted(async () => {
  isLoading.value = true
  isConnected.value = await calendarStore.checkGoogleConnection()
  if (isConnected.value) {
    calendarStore.initGcalWs()
    console.log("current date during gcal ws initi call - ", currentDate.value)
    // taskStore.fetchGcalTask(currentDate)
  }

  // Initialize a single draggable instance for calendar integration only
  // Use a more specific selector to avoid conflicts with vuedraggable
  // Only target task items that are not being handled by vuedraggable
  draggableInstance.value = new ThirdPartyDraggable(document.body, {
    itemSelector: '.task-item',
    mirrorSelector: '.task-item',
    // Add event data to make dragging work properly
    eventData: function (eventEl) {
      // Get the event data from the element's dataset
      if (eventEl.dataset.event) {
        const eventData = JSON.parse(eventEl.dataset.event)
        // Event data available for drag operation
        return {
          ...eventData,
        }
      }
      return null
    },
  })

  // show alert if calendarstore has error
  watch(
    calendarError,
    (new_error) => {
      if (new_error) {
        alert(new_error)
        calendarStore.error = null
      }
    },
    { deep: true }
  )


  isLoading.value = false

})

onUnmounted(async () => {
  // close gcal event ws connection
  calendarStore.gcalWsClose()
})

const connectGoogleCalendar = () => {
  calendarStore.startGoogleAuth()
}

const disconnectGoogleCalendar = async () => {
  isLoading.value = true
  await calendarStore.disconnectGoogleCalendar()
  isConnected.value = false
  isLoading.value = false
}

async function handleTaskDropped(dropInfo) {
  // Triggers when task dropped into calendar sidebar from external
  try {
    // Ensure we have valid data from the dragged element
    if (!dropInfo.draggedEl || !dropInfo.draggedEl.dataset.event) {
      // No valid task data found in dragged element
      return false // Return false to prevent the post drop action
    }

    const droppedTask = JSON.parse(dropInfo.draggedEl.dataset.event)

    // Update task status and start time
    droppedTask.status = 'ON_CAL'
    droppedTask.start_at = dropInfo.dateStr
    droppedTask.end_at = calculateEndAt(droppedTask.start_at, droppedTask.duration)

    // First update the task in the database
    taskStore.taskDroppedToCal(droppedTask)
    return true
  } catch (error) {
    // Error handling task drop
    alert('Failed to add task to calendar. Please try again.')
    console.log('Error during task drop:', error)
    return false // Return false to indicate failed drop
  }
}

function handleEventClick(eventClickInfo) {
  const source = eventClickInfo.event.extendedProps.source
  if (source === 'google') {
    console.log("event is from google so no feature to show event ")
    return
  }
  console.log("opening event")
  const task = eventClickInfo.event.extendedProps.raw
  if (task) {
    // Open modal for non-Google calendar tasks
    openEditModal({ ...task })
  }
}

async function handleCalendarEventUpdated(eventDropInfo) {
  // Triggers when events are draggedend inside the calendar sidebar
  const eventSource = eventDropInfo.event.extendedProps.source
  if (eventSource === 'google') {
    // Updating Google Calendar event after drag
    const updates = {
      start: {
        dateTime: eventDropInfo.event.start.toISOString(),
        timeZone: Intl.DateTimeFormat().resolvedOptions().timeZone,
      },
      end: {
        dateTime: eventDropInfo.event.end.toISOString(),
        timeZone: Intl.DateTimeFormat().resolvedOptions().timeZone,
      },
    }
    const updated = await calendarStore.updateGoogleCalendarEvent(eventDropInfo.event.id, updates)
    if (updated === false) {
      eventDropInfo.revert()
    }
  } else {
    // get the main event object
    const rawEventData = eventDropInfo.event.extendedProps.raw;
    rawEventData.start_at = eventDropInfo.event.start?.toISOString();
    rawEventData.end_at = eventDropInfo.event.end?.toISOString();
    taskStore.updateTaskWs(rawEventData);
  }
}

const calendarOptions = ref({
  plugins: [dayGridPlugin, timeGridPlugin, interactionPlugin, listPlugin],
  initialView: props.initialView,
  headerToolbar: false,
  allDaySlot: false,
  eventTimeFormat: { hour: '2-digit', minute: '2-digit', meridiem: false },
  slotMinTime: '00:00:00',
  slotMaxTime: '23:59:59',
  snapDuration: '00:01:00',
  height: 'auto',
  expandRows: true,
  stickyHeaderDates: false,
  navLinks: false,
  dayMaxEvents: false,
  eventClick: handleEventClick,
  datesSet: handleDatesSet,
  // Two event sources: local ON_CAL tasks and Google Calendar WebSocket events
  eventSources: [
    // Local tasks marked ON_CAL
    { events: (info, success) => success(localCalTasks.value) },
    // Google Calendar events via WebSocket
    { events: (info, success) => success(gcalEvents.value) }
  ],
  selectable: false,
  eventResizableFromStart: true,
  editable: true,
  droppable: true,
  drop: handleTaskDropped,  // task dropped from outside into fullcalendar
  eventDrop: handleCalendarEventUpdated,  // Triggered when dragging stops and the event has moved to a different day/time.
  eventResize: handleCalendarEventUpdated,  // Triggered when resizing stops and the event has changed in duration.
})
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
          <button class="nav-btn prev-btn" @click="prev">
            <LucideChevronLeft :size="14" />
          </button>
          <!-- Show Today button only when not viewing today -->
          <button v-if="!isToday" class="nav-btn today-btn" @click="today">
            Today
          </button>
          {{ currentDateDisplay }}
          <button class="nav-btn next-btn" @click="next">
            <LucideChevronRight :size="14" />
          </button>
        </div>
      </div>
      <Popper v-if="isConnected" arrow content="Disconnect Google Calendar" :show="showPopper">
        <LucideUnlink
          class="disconnect-button"
          :class="{ 'disabled-div': isLoading }"
          :size="14"
          @mouseover="showPopper = true"
          @mouseleave="showPopper = false"
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
        <button class="connect-button" :disabled="calendarStore.isLoading" @click="connectGoogleCalendar">
          {{ calendarStore.isLoading ? 'Connecting...' : 'Connect Google Calendar' }}
          <div v-if="!calendarStore.isLoading">
            <LucideLink class="link-icon" size="16" />
          </div>
        </button>
      </div>

      <!-- Render FullCalendar component here -->
      <FullCalendar v-else ref="calendarRef" :options="calendarOptions" />

      <!-- Task Edit Modal -->
      <TaskEditModal
        v-if="activeTask"
        :task="activeTask"
        :is-open="isEditModalOpen"
        @close-modal="closeEditModal"
        @task-updated="handleTaskUpdated"
        @task-archived="handleTaskArchived"
        @task-deleted="handleTaskDeleted" />
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

/* Styled header for calendar integration with improved spacing and separation */
.integration-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1rem;
  border-bottom: 1px solid var(--color-border);
  margin-bottom: 1rem;
}

/* Group title and date vertically */
.left-header {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

/* Title with icon aligned */
.integration-header h3 {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin: 0;
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
}

/* Secondary date label */
.integration-header .date-display {
  font-size: var(--font-size-sm);
  color: var(--color-text-tertiary);
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
  to {
    transform: rotate(360deg);
  }
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

.connect-button,
.disconnect-button {
  background-color: var(--color-background-tertiary);
  color: var(--color-text-primary);
  border: none;
  border-radius: 0.375rem;
  padding: 0.75rem 1.5rem;
  font-weight: var(--font-weight-medium);
  cursor: pointer;
  transition: background-color 0.2s;
}

.connect-button:hover,
.disconnect-button:hover {
  background-color: var(--color-primary);
  color: var(--color-text-primary);
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
  color: white;
}

/* Event Popover Styles */
.event-popover {
  position: fixed;
  z-index: 10;
  background-color: var(--color-background);
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  width: 220px;
  transform: translateX(-50%);
  border: 1px solid var(--color-border);
}

.event-popover-content {
  padding: 12px;
}

.event-popover-actions {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.popover-action-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px;
  background-color: var(--color-background);
  border: 1px solid var(--color-border);
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.2s;
  color: var(--color-text);
  font-size: 13px;
}

.popover-action-btn:hover {
  background-color: var(--color-background-hover);
}

.popover-action-btn.delete {
  color: var(--color-error);
}

.popover-action-btn.delete:hover {
  background-color: rgba(var(--color-error-rgb), 0.1);
}

.event-popover-arrow {
  position: absolute;
  top: -8px;
  left: 50%;
  transform: translateX(-50%);
  width: 16px;
  height: 8px;
  overflow: hidden;
}

.event-popover-arrow::after {
  content: '';
  position: absolute;
  width: 12px;
  height: 12px;
  background: var(--color-background-secondary);
  transform: translateX(-50%) translateY(50%) rotate(45deg);
  left: 50%;
  border-left: 1px solid var(--color-border);
  border-top: 1px solid var(--color-border);
}

.event-popover-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 10;
}

.disabled-div {
  pointer-events: none;
  opacity: 0.5;
  cursor: not-allowed;
}

.checked {
  background-color: var(--color-success);
  border-color: var(--color-success);
  color: var(--color-text-primary);
}
</style>
