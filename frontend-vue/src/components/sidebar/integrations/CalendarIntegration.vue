<script setup>
  import { ref, onMounted, onBeforeUnmount, watch, computed, reactive } from 'vue'
  import { useCalendarStore } from '../../../stores/calendarStore'
  import { useTaskStoreWs } from '../../../stores/taskStoreWs'
  import { LucideCalendar, LucideLink, LucideUnlink, CheckCircle, Trash2 } from 'lucide-vue-next'
  import dayGridPlugin from '@fullcalendar/daygrid'
  import timeGridPlugin from '@fullcalendar/timegrid'
  import interactionPlugin, { ThirdPartyDraggable } from '@fullcalendar/interaction'
  import listPlugin from '@fullcalendar/list'
  import FullCalendar from '@fullcalendar/vue3'
  import Popper from 'vue3-popper'
  import { tasksToFcEvents } from '../../../utils/calendarSerializer'

  // Props
  const props = defineProps({
    initialView: {
      type: String,
      default: 'timeGridDay',
    },
  })

  const calendarStore = useCalendarStore()
  const taskStore = useTaskStoreWs()
  const calendarEvents = computed({
    get() {
      const allTaskOnKanban = taskStore.kanbanColumns.flatMap(col => col.tasks)
      const calTasks = allTaskOnKanban.filter(task => task.status === 'ON_CAL')
      return tasksToFcEvents(calTasks)
    },
    // set() {
    //   console.log('Setting calendar events')
    // },
  })
  const isConnected = ref(false)
  const isLoading = ref(false)
  const showPopper = ref(false)
  const eventPopover = reactive({
    show: false,
    event: null,
    position: { x: 0, y: 0 },
  })
  // Reference to FullCalendar instance
  const calendarRef = ref(null)

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
    isLoading.value = false

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

    // show alert if calendarstore have error
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

    watch(
      calendarEvents,          // recomputed any time tasks change
      () => {
        if (calendarRef.value) {
          calendarRef.value.getApi().removeAllEvents()  // remove all events currently displayed
          calendarRef.value.getApi().refetchEvents()   // tells FullCalendar to re-run the events() function
        }
      },
      { deep: true, immediate: true }           // watch inside the array
    )

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
      // use today's data if task don't have col date ( happens if user directing dropping task from braindump since
      // braindump tasks don't have column dates )
      droppedTask.column_date = dropInfo.dateStr.split("T")[0]

      // First update the task in the database
      taskStore.taskDroppedToCal(droppedTask)

      // Then remove it from its source location (kanban or braindump)
      // console.log('Removing task from kanban or braindump')
      // await taskStore.searchAndRemoveTaskFromKanbanOrBraindump(droppedTask.id)

      // remove again ( hackish way ) as tasks doesn't get removed if snapped to a kanban col while dragging to fullcalendar
      // const taskCardElement = document.getElementById(`task-card-${droppedTask.id}`)
      // if (taskCardElement) {
      //   taskCardElement.remove()
      //   console.log('Task card removed from DOM')
      // }

      // Remove the specific event that was just added by the drag and drop
      // we do this to avoid duplicate events as fetching from backend + frontend
      // keeping old event in frontend will lead to duplicate events
      // TODO: find a better way to remove duplicate events from stackoverflow
      // if (calendarRef.value) {
      //   const calendar = calendarRef.value.getApi()

      //   // Find the event by ID and remove it before fetching from backend
      //   const event = calendar.getEventById(droppedTask.id)
      //   if (event) {
      //     event.remove()
      //     console.log('Event removed from calendar')
      //   }

      //   // Now fetch the clean data from backend
      //   calendar.refetchEvents()
      // }

      return true
    } catch (error) {
      // Error handling task drop
      alert('Failed to add task to calendar. Please try again.')
      console.log('Error during task drop:', error)
      return false // Return false to indicate failed drop
    }
  }

  // function fetchCalendarEvents(fetchInfo, successCallback, failureCallback) {
  //   // Fetching calendar events
  //   const axiosInstance = authStore.axios_instance
  //   axiosInstance
  //     .get('/api/gcalendar/events/', {
  //       params: {
  //         start: fetchInfo.startStr,
  //         end: fetchInfo.endStr,
  //       },
  //     })
  //     .then((res) => successCallback(res.data))
  //     .catch((err) => {
  //       failureCallback(err)
  //     })
  // }


  // function handleEventClick(info) {
  //   // Prevent default behavior
  //   info.jsEvent.preventDefault()
  //   // Only show popover for our app's tasks, not Google Calendar events
  //   if (info.event.extendedProps.source !== 'google') {
  //     // Position the popover near the clicked event
  //     eventPopover.event = info.event
  //     const rect = info.el.getBoundingClientRect()
  //     eventPopover.position.x = rect.left + rect.width / 2
  //     eventPopover.position.y = rect.top
  //     eventPopover.show = true
  //   }
  // }

  // function _getTaskIdFromEvent(event) {
  //   // Extract task ID from the event's extended properties
  //   if (event.extendedProps.taskId) {
  //     return event.extendedProps.taskId
  //   }
  //   if (event.id) {
  //     return event.id
  //   }
  //   console.error('No valid task ID found in event properties:', event)
  // }

  // async function markTaskAsCompleted(event) {
  //   const taskId = _getTaskIdFromEvent(event)
  //   try {
  //     if (taskId) {
  //       await taskStore.toggleCompletion(taskId)
  //       // Refresh calendar events
  //       if (calendarRef.value) {
  //         calendarRef.value.getApi().refetchEvents()
  //         console.log('Calendar events refetched')
  //       } else {
  //         console.error('Calendar reference not found while marking task as completed')
  //       }
  //       // Close the popover
  //       eventPopover.show = false
  //     } else {
  //       console.error('No task ID found to mark as completed')
  //     }
  //   } catch (error) {
  //     console.error('Error updating task completion status:', error)
  //   }
  // }

  // async function deleteCalendarTask(event) {
  //   const taskId = _getTaskIdFromEvent(event)
  //   console.log('Deleting task:', taskId)
  //   try {
  //     await taskStore.deleteTask(taskId)
  //     // Close the popover
  //     eventPopover.show = false
  //     // Refresh calendar events
  //     if (calendarRef.value) {
  //       calendarRef.value.getApi().refetchEvents()
  //       console.log('Calendar events refetched after deletion')
  //     } else {
  //       console.error('Calendar reference not found')
  //     }
  //   } catch (error) {
  //     console.error('Error deleting task:', error)
  //   }
  // }

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
    eventTimeFormat: {
      hour: '2-digit',
      minute: '2-digit',
      meridiem: false,
    },
    slotMinTime: '00:00:00',
    slotMaxTime: '23:59:00',
    // Set 1-minute granularity for dragging / resizing
    snapDuration: '00:01:00',
    height: 'auto',
    expandRows: true,
    stickyHeaderDates: false,
    navLinks: false,
    dayMaxEvents: false,
    // eventClick: handleEventClick,
    // dateClick: handleDateClick,
    // datesSet: handleDatesSet,
    events: (fetchInfo, successCallback, failureCallback) => successCallback(calendarEvents.value),
    selectable: false,
    eventResizableFromStart: true,
    editable: true,
    droppable: true,
    // Other calendar options...
    drop: handleTaskDropped,
    eventDrop: handleCalendarEventUpdated, // event dragged to another time slot
    eventResize: handleCalendarEventUpdated,
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
          {{ new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'short', day: 'numeric' }) }}
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

      <!-- Event Popover -->
      <div
        v-if="eventPopover.show"
        class="event-popover"
        :style="{
          left: `${eventPopover.position.x}px`,
          top: `${eventPopover.position.y + 20}px`,
        }">
        <div class="event-popover-content">
          <div class="event-popover-actions">
            <button class="popover-action-btn" @click="markTaskAsCompleted(eventPopover.event)">
              <CheckCircle size="16" :class="{ checked: eventPopover.event?.extendedProps.isCompleted }" />
              {{ eventPopover.event?.extendedProps.isCompleted ? 'Mark as Incomplete' : 'Mark as Completed' }}
            </button>
            <button class="popover-action-btn delete" @click="deleteCalendarTask(eventPopover.event)">
              <Trash2 size="16" />
              Delete Task
            </button>
          </div>
        </div>
        <div class="event-popover-arrow" />
      </div>

      <!-- Backdrop to close popover when clicking outside -->
      <div v-if="eventPopover.show" class="event-popover-backdrop" @click="eventPopover.show = false" />
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
