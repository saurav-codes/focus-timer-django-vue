<script setup>
import { ref, watch, computed, onUnmounted } from 'vue'
import { useTaskStoreWs } from '../stores/taskStoreWs'
import { useTagsProjectStore } from '../stores/tagsProjectStore'
import { X, Trash2, PencilLine, Archive, AlarmClock } from 'lucide-vue-next'
import { useTimeAgo } from '@vueuse/core'
import { VueSpinner } from 'vue3-spinners'
import Multiselect from '@vueform/multiselect'
import RecurringTaskEditor from './RecurringTaskEditor.vue'
import ProjectDropdownPopup from './ProjectDropdownPopup.vue'
import { useStartAt } from '../composables/useStartAt'

const props = defineProps({
  task: {
    type: Object,
    required: true,
  },
  isOpen: {
    type: Boolean,
    required: true,
  },
})

const taskStore = useTaskStoreWs()
const tagsProjectStore = useTagsProjectStore()
const emit = defineEmits(['closeModal', 'task-deleted', 'task-updated', 'task-archived'])

// Create a copy of the task to edit
const editedTask = ref({ ...props.task })

// Update local copy when prop changes
watch(
  () => props.task,
  (newTask) => {
    editedTask.value = { ...newTask }
  },
  { deep: true, immediate: true }
)

// Format the created_at date
const timeAgo = computed(() => {
  if (editedTask.value.created_at) {
    return useTimeAgo(new Date(editedTask.value.created_at)).value
  }
  return ''
})

const saveTask = async (force_save=false) => {
  /*
  `force_save` kwarg will ignore recurrence_rule & will
  save the task to backend
  */
  if (editedTask.value.recurrence_series?.recurrence_rule && !force_save) return
  try {
    taskStore.updateTaskWs(editedTask.value)
    emit('task-updated', editedTask.value)
  } catch (error) {
    console.error('Error updating task:', error)
  }
}

const isDeleting = ref(false)
const deleteTask = async () => {
  if (isDeleting.value) return
  isDeleting.value = true
  try {
    taskStore.deleteTaskWs(editedTask.value.id)
    emit('task-deleted', editedTask.value.id)
    closeModal()
  } catch (error) {
    console.error('Error deleting task:', error)
  } finally {
    isDeleting.value = false
  }
}

const isArchiving = ref(false)
const archiveTask = async () => {
  if (isArchiving.value) return
  isArchiving.value = true
  try {
    // Archive the task
    editedTask.value.status = 'ARCHIVED'
    taskStore.updateTaskWs(editedTask.value)
    taskStore.pushToArchiveTask(editedTask.value)
    emit('task-archived', editedTask.value.id)
    closeModal()
  } catch (error) {
    console.error('Error archiving task:', error)
  } finally {
    isArchiving.value = false
  }
}

// Press Escape to close
const handleKeyDown = (event) => {
  if (event.key === 'Escape') {
    closeModal()
  }
}

const selectedTags = computed({
  get() {
    return editedTask.value.tags || []
  },
  set(newTags) {
    editedTask.value.tags = newTags
    saveTask()
  },
})

const closeModal = () => {
  emit('closeModal')
}

// Handle project assignment
const assignProject = async (projectId) => {
  try {
    // Make the API call to assign the project
    taskStore.assignProjectWs(editedTask.value.id, projectId)
    emit('task-updated', editedTask.value)
  } catch (error) {
    console.error('Error assigning project to task:', error)
  }
}

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeyDown)
})

const isModalOpen = computed(() => props.isOpen)
watch(isModalOpen, (newVal) => {
  if (newVal) {
    console.log('TaskEditModal opened')
    tagsProjectStore.fetchTags()
  } else {
    console.log('TaskEditModal closed')
  }
})
const { startTime } = useStartAt(editedTask)
// Save only when the user changes the start time (skip initial backend sync)
const startTimeInitialized = ref(false)
watch(startTime, () => {
  if (startTimeInitialized.value) {
    saveTask(true)
  } else {
    startTimeInitialized.value = true
  }
}, {immediate: true})
</script>

<template>
  <Teleport to="body">
    <div v-if="isOpen" class="modal-overlay" @click.self="closeModal">
      <div class="task-edit-modal">
        <div class="modal-header">
          <h3 class="modal-header-title">
            <PencilLine size="18" />
            Edit Task
          </h3>
          <button class="close-button" @click="closeModal">
            <X size="18" />
          </button>
        </div>

        <div class="modal-content">
          <div class="form-group">
            <input
              id="task-title"
              v-model.lazy="editedTask.title"
              type="text"
              class="form-input"
              placeholder="Task title"
              @blur="saveTask(true)">
          </div>

          <div class="form-group">
            <textarea
              id="task-description"
              v-model.lazy="editedTask.description"
              class="form-textarea"
              placeholder="Add details about this task..."
              rows="4"
              @blur="saveTask(true)" />
          </div>
          <div class="form-group">
            <label class="form-label">Tags</label>
            <Multiselect
              v-model="selectedTags"
              mode="tags"
              :options="tagsProjectStore.tags.map((tag) => tag.name)"
              :create-option="true"
              :close-on-select="false"
              :caret="true"
              :searchable="true"
              placeholder="Search or add tags" />
          </div>

          <!-- Project assignment -->
          <div class="form-group">
            <label class="form-label">Project</label>
            <div class="project-selector">
              <ProjectDropdownPopup :project="editedTask.project" @project-selected="assignProject" />
            </div>
            <!-- Start Time Selector -->
            <div class="start-time-selector">
              <div class="start-time-label">
                <AlarmClock :size="16" />
                <span>Start</span>
              </div>
              <input v-model="startTime" type="time" class="time-input">
            </div>
          </div>
          <div class="form-group">
            <label class="checkbox-container">
              <input v-model.lazy="editedTask.is_completed" type="checkbox" @change="saveTask">
              <span class="label-text">Completed</span>
            </label>
          </div>

          <!-- Recurring Task Editor -->
          <RecurringTaskEditor v-if="editedTask.status == 'ON_BOARD'" :task="editedTask" @close-modal="closeModal" />

          <div class="meta-info">
            <span class="created-at">Created {{ timeAgo }}</span>
          </div>
        </div>

        <div class="modal-footer">
          <div class="footer-buttons">
            <button class="archive-button" @click="archiveTask">
              <Archive v-if="!isArchiving" size="16" />
              <VueSpinner v-if="isArchiving" />
              <span>Archive</span>
            </button>
            <button class="delete-button" @click="deleteTask">
              <Trash2 v-if="!isDeleting" size="16" />
              <VueSpinner v-if="isDeleting" />
              <span>Delete</span>
            </button>
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

.task-edit-modal {
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

.modal-header h3 {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin: 0;
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
  display: block;
  margin-bottom: 0.5rem;
  font-size: var(--font-size-sm);
  color: var(--color-text-primary);
}

.form-input,
.form-textarea {
  width: 100%;
  padding: 0.75rem;
  border-radius: 0.375rem;
  border: 1px solid var(--color-border);
  background-color: var(--color-input-background);
  color: var(--color-text-primary);
  font-size: var(--font-size-sm);
  transition: border-color var(--transition-base);
}

.form-input:focus,
.form-textarea:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 2px var(--color-primary-light);
}

.checkbox-container {
  display: flex;
  align-items: center;
  cursor: pointer;
}

.checkbox-container input[type='checkbox'] {
  margin-right: 0.5rem;
}

.meta-info {
  margin-top: 1rem;
  color: var(--color-text-tertiary);
  font-size: var(--font-size-xs);
}

.project-selector {
  display: flex;
  margin-top: 0.5rem;
}

.project-button {
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

.project-button:hover {
  background-color: var(--color-background-tertiary);
  border-color: var(--color-primary);
  color: var(--color-text-primary);
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  padding: 1rem 1.5rem;
  border-top: 1px solid var(--color-border);
}

.footer-buttons {
  display: flex;
  gap: 0.75rem;
}

.left-action-btn-group {
  display: flex;
  justify-content: center;
}

.save-button,
.delete-button,
.archive-button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.625rem 1rem;
  border-radius: 0.375rem;
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  cursor: pointer;
  transition: background-color var(--transition-base);
}

.delete-button {
  background-color: transparent;
  color: var(--color-error);
  border: 1px solid var(--color-border);
}

.delete-button:hover {
  background-color: var(--color-background-secondary);
}

.archive-button,
.save-button {
  background-color: transparent;
  color: var(--color-text-secondary);
  border: 1px solid var(--color-border);
}

.archive-button:hover,
.save-button:hover {
  background-color: var(--color-background-secondary);
  color: var(--color-text-primary);
}

input {
  color: var(--color-text-primary);
}

.start-time-selector {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin: 0.75rem 0;
  padding: 0.5rem;
  background-color: var(--color-background-secondary);
  border-radius: 0.375rem;
}

.start-time-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.time-input {
  padding: 0.375rem 0.5rem;
  border-radius: 0.25rem;
  border: 1px solid var(--color-border);
  background-color: var(--color-input-background);
  font-size: var(--font-size-sm);
}
</style>
