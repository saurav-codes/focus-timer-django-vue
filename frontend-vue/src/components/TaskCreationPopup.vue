<script setup>
  import { ref, watch } from 'vue'
  import { X, Plus, Clock, PlusIcon, LucideBrainCircuit } from 'lucide-vue-next'
  import { useTaskStoreWs } from '../stores/taskStoreWs'
  import { onKeyStroke } from '@vueuse/core'
  import TimeDropdownPopup from './TimeDropdownPopup.vue'
  import ProjectDropdownPopup from './ProjectDropdownPopup.vue'
  import { useFloating, autoUpdate } from '@floating-ui/vue'
  import { offset, flip, shift } from '@floating-ui/dom'

  const props = defineProps({
    isVisible: {
      type: Boolean,
      default: false,
    },
  })

  const emit = defineEmits(['close'])

  const taskStore = useTaskStoreWs()

  const newTaskTitle = ref('')
  const inputRef = ref(null)

  // Duration state
  const taskHours = ref(0)
  const taskMinutes = ref(30)
  const taskDurationDisplay = ref('30m')
  const isTimePopupOpen = ref(false)

  // Set up floating UI for time popup
  const durationButtonRef = ref(null)
  const timePopupRef = ref(null)

  const { floatingStyles: timeFloatingStyles } = useFloating(durationButtonRef, timePopupRef, {
    whileElementsMounted: autoUpdate, // keep the popup close to the button while screen size changes
    placement: 'bottom-start',
    middleware: [
      offset(8), // Add some space between the button and popup
      flip(), // Flip to the opposite side if there's not enough space
      shift(), // Shift the popup if needed to ensure visibility
    ],
  })

  // Watch for visibility changes and focus input when visible
  watch(
    () => props.isVisible,
    (newVal) => {
      if (newVal) {
        // Focus the input after the DOM updates
        setTimeout(() => {
          inputRef.value?.focus()
        }, 0)
      } else {
        // Reset task data when popup is closed
        resetTaskData()
      }
    }
  )

  // Reset all task input data
  const resetTaskData = () => {
    newTaskTitle.value = ''
    taskHours.value = 0
    taskMinutes.value = 30
    taskDurationDisplay.value = '30m'
    isTimePopupOpen.value = false
  }

  // Open time popup
  const openTimePopup = () => {
    isTimePopupOpen.value = true
  }

  // Handle time popup save event
  const handleTimePopupSave = ({ hours, minutes, formatted, keepOpen }) => {
    taskHours.value = hours
    taskMinutes.value = minutes
    taskDurationDisplay.value = formatted

    // Only close the popup if it's not just an update
    if (!keepOpen) {
      isTimePopupOpen.value = false
    }
  }

  // Handle time popup cancel event
  const handleTimePopupCancel = () => {
    isTimePopupOpen.value = false
  }

  const selectedProjectId = ref(null)
  const assignProject = (projectId) => {
    selectedProjectId.value = projectId
  }

  // Add task and close popup
  const addTask = async () => {
    if (newTaskTitle.value.trim()) {
      // Format duration string for backend
      const durationString = `${taskHours.value}:${taskMinutes.value}`

      // Create new task object
      const newTask = {
        frontend_id: Date.now(),
        title: newTaskTitle.value,
        is_completed: false,
        duration: durationString, // Format for backend
        duration_display: taskDurationDisplay.value, // For display
        order: 0,
        tags: [],
        status: 'BRAINDUMP',
        column_date: null, // Explicitly set to null
        recurrence_series: null,
      }
      if (selectedProjectId.value) {
        newTask.project_id = selectedProjectId.value
      }
      // Add the task to the brain dump tasks (optimistic update)
      taskStore.brainDumpTasks.unshift(newTask)

      // Reset input
      resetTaskData()

      // Create task in backend
      taskStore.createTaskWs(newTask)
    } else {
      // Close popup if task is empty
      console.log('Task title cannot be empty')
      emit('close')
    }
  }

  // Handle keyboard events
  const handleKeyDown = (event) => {
    if (event.key === 'Enter') {
      addTask()
    } else if (event.key === 'Escape') {
      emit('close')
    }
  }

  // Register Escape key listener globally
  onKeyStroke('Escape', () => {
    if (props.isVisible) {
      emit('close')
    }
  })
</script>

<template>
  <Teleport to="body">
    <div v-if="isVisible" class="task-create-popup-overlay" @click="$emit('close')">
      <div class="popup-container" @click.stop>
        <div class="popup-header">
          <span class="popup-title">
            Create Task (<LucideBrainCircuit size="14" /> Brain Dump )
          </span>
          <button class="close-button" @click="$emit('close')">
            <X size="18" />
          </button>
        </div>
        <div class="popup-content">
          <div class="input-wrapper">
            <Plus size="18" class="input-icon" />
            <input
              ref="inputRef"
              v-model="newTaskTitle"
              type="text"
              placeholder="What needs to be done?"
              class="task-input"
              @keydown="handleKeyDown">
          </div>

          <!-- Task duration selector -->
          <div class="task-options">
            <button ref="durationButtonRef" class="duration-button" @click.stop="openTimePopup">
              <Clock size="16" />
              <span>{{ taskDurationDisplay }}</span>
            </button>

            <!-- Time dropdown popup portal -->
            <Teleport to="body">
              <TimeDropdownPopup
                v-if="isTimePopupOpen"
                ref="timePopupRef"
                :style="timeFloatingStyles"
                :initial-hours="taskHours"
                :initial-minutes="taskMinutes"
                @save="handleTimePopupSave"
                @cancel="handleTimePopupCancel" />
            </Teleport>

            <!-- Project dropdown popup portal -->
            <ProjectDropdownPopup @project-selected="assignProject" />
            <button class="create-task-button key" @click.stop="addTask">
              Create Task
              <PlusIcon size="16" />
            </button>
          </div>

          <div class="shortcuts-hint">
            <div class="shortcut-item">
              <span class="key">Enter</span>
              <span>to create task</span>
            </div>
            <div class="shortcut-item">
              <span class="key">Esc</span>
              <span>to close</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<style scoped>
  .task-create-popup-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    background-color: rgba(0, 0, 0, 0.5);
    display: flex;
    justify-content: center;
    align-items: flex-start;
    padding-top: 15vh;
    z-index: 6;
    animation: fadeIn 0.2s ease-out;
  }

  @keyframes fadeIn {
    from {
      opacity: 0;
    }
    to {
      opacity: 1;
    }
  }

  .popup-container {
    width: 600px;
    background-color: var(--color-background);
    border-radius: 8px;
    overflow: hidden;
    box-shadow: var(--shadow-lg, 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05));
    animation: slideDown 0.2s ease-out;
  }

  @keyframes slideDown {
    from {
      transform: translateY(-20px);
      opacity: 0;
    }
    to {
      transform: translateY(0);
      opacity: 1;
    }
  }

  .popup-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 16px;
    border-bottom: 1px solid var(--color-border);
  }

  .popup-title {
    font-weight: var(--font-weight-medium);
    color: var(--color-text-secondary);
    font-size: var(--font-size-sm);
    display: flex;
    align-items: center;
    gap: 4px;
  }

  .close-button {
    background: transparent;
    border: none;
    color: var(--color-text-tertiary);
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 4px;
    border-radius: 4px;
    transition: all 0.2s;
  }

  .close-button:hover {
    background-color: var(--color-background-tertiary);
    color: var(--color-text-secondary);
  }

  .popup-content {
    padding: 16px;
  }

  .input-wrapper {
    display: flex;
    align-items: center;
    border: 1px solid var(--color-border);
    border-radius: 6px;
    padding: 0 12px;
    background-color: var(--color-input-background, var(--color-background-secondary));
    transition:
      border-color 0.2s,
      box-shadow 0.2s;
    margin-bottom: 12px;
  }

  .input-wrapper:focus-within {
    border-color: var(--color-primary);
    box-shadow: 0 0 0 2px var(--color-primary-light, rgba(147, 51, 234, 0.1));
  }

  .input-icon {
    margin-right: 8px;
    color: var(--color-text-tertiary);
  }

  .task-input {
    width: 100%;
    padding: 12px 0;
    border: none;
    background: transparent;
    color: var(--color-text-primary);
    font-size: var(--font-size-md);
    outline: none;
  }

  .task-input::placeholder {
    color: var(--color-text-tertiary);
  }

  /* Task options styling */
  .task-options {
    display: flex;
    gap: 10px;
    margin-bottom: 16px;
    position: relative;
    z-index: 7; /* Ensure the options are above other elements in the popup */
  }

  .duration-button {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 6px 12px;
    background-color: var(--color-background-secondary);
    border: 1px solid var(--color-border);
    border-radius: 4px;
    font-size: var(--font-size-xs);
    color: var(--color-text-secondary);
    cursor: pointer;
    transition: all 0.2s;
  }

  .duration-button:hover,
  .create-task-button:hover {
    background-color: var(--color-background-tertiary);
    border-color: var(--color-primary);
    color: var(--color-text-primary);
  }

  .create-task-button {
    display: flex !important;
    align-items: center;
    justify-content: center;
    color: var(--color-text-primary);
    cursor: pointer;
  }

  .shortcuts-hint {
    display: flex;
    gap: 16px;
    padding-top: 12px;
    border-top: 1px solid var(--color-border);
    color: var(--color-text-tertiary);
    font-size: var(--font-size-xs);
  }

  .shortcut-item {
    display: flex;
    align-items: center;
    gap: 6px;
  }

  .key {
    display: inline-block;
    padding: 2px 6px;
    background-color: var(--color-background-tertiary);
    border-radius: 4px;
    border: 1px solid var(--color-border);
    font-size: 10px;
    font-weight: var(--font-weight-medium);
  }
</style>
