<script setup>
import { ref, watch, computed, onMounted, onUnmounted } from 'vue';
import { useTaskStore } from '../stores/taskstore';
import { X, Save, Trash2 } from 'lucide-vue-next';
import { useTimeAgo, useDateFormat } from '@vueuse/core';
import { VueSpinner } from 'vue3-spinners';


const props = defineProps({
  task: {
    type: Object,
    required: true
  },
  isOpen: {
    type: Boolean,
    required: true
  }
});

const taskStore = useTaskStore();
const emit = defineEmits(["closeModal"])

// Create a copy of the task to edit
const editedTask = ref({ ...props.task });

// Update local copy when prop changes
watch(() => props.task, (newTask) => {
  editedTask.value = { ...newTask };
}, { deep: true });

const task_start_at = computed({
  get: () => {
    if (editedTask.value.start_at) {
      return useDateFormat(editedTask.value.start_at, 'YYYY-MM-DD HH:mm:ss').value;
    }
    return "";
  },
  set: (value) => {
    console.log("setting start_at", value);
    const start_at_iso_string = new Date(value).toISOString();
    editedTask.value.start_at = start_at_iso_string;
  }
});

const task_end_at = computed({
  get: () => {
    if (editedTask.value.end_at) {
      return useDateFormat(editedTask.value.end_at, 'YYYY-MM-DD HH:mm:ss').value;
    }
    return "";
  },
  set: (value) => {
    console.log("setting end_at", value);
    const end_at_iso_string = new Date(value).toISOString();
    editedTask.value.end_at= end_at_iso_string;
  }
});

// Format the created_at date
const timeAgo = computed(() => {
  if (editedTask.value.created_at) {
    return useTimeAgo(new Date(editedTask.value.created_at)).value;
  }
  return '';
});

const isSaving = ref(false);
const isDeleting = ref(false);

const saveTask = async () => {
  if (isSaving.value) return;
  isSaving.value = true;
  try {
    await taskStore.updateTask(editedTask.value);
  } catch (error) {
    console.error('Error updating task:', error);
  } finally {
    isSaving.value = false;
    closeModal();
  }
};

const deleteTask = async () => {
  if (isDeleting.value) return;
  isDeleting.value = true;
  if (confirm('Are you sure you want to delete this task?')) {
    try {
      await taskStore.deleteTask(editedTask.value.id);
      closeModal()
    } catch (error) {
      console.error('Error deleting task:', error);
    } finally {
      isDeleting.value = false;
    }
  }
};

// Press Escape to close
const handleKeyDown = (event) => {
  if (event.key === 'Escape') {
    closeModal();
  }
};

const closeModal = () => {
  console.log("emiting close event")
  emit("closeModal")
}

onMounted(() => {
  // Esc key for closing modal
  document.addEventListener('keydown', handleKeyDown);
});

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeyDown);
});


</script>

<template>
  <Teleport to="body">
    <div v-if="isOpen" class="modal-overlay" @click.self="closeModal">
      <div class="task-edit-modal">
        <div class="modal-header">
          <h3>Edit Task</h3>
          <button class="close-button" @click="closeModal">
            <X size="18" />
          </button>
        </div>

        <div class="modal-content">
          <div class="form-group">
            <input
              id="task-title"
              v-model="editedTask.title"
              type="text"
              class="form-input"
              placeholder="Task title">
          </div>

          <div class="form-group">
            <textarea
              id="task-description"
              v-model="editedTask.description"
              class="form-textarea"
              placeholder="Add details about this task..."
              rows="4" />
          </div>

          <div class="form-group">
            <input
              id="task-duration"
              v-model="task_start_at"
              type="datetime-local"
              class="form-input">
            <input
              id="task-duration"
              v-model="task_end_at"
              type="datetime-local"
              class="form-input">
          </div>

          <div class="form-group">
            <label class="checkbox-container">
              <input v-model="editedTask.is_completed" type="checkbox">
              <span class="label-text">Completed</span>
            </label>
          </div>

          <div class="meta-info">
            <span class="created-at">Created {{ timeAgo }}</span>
          </div>
        </div>

        <div class="modal-footer">
          <button class="delete-button" @click="deleteTask">
            <Trash2 v-if="!isDeleting" size="16" />
            <VueSpinner v-if="isDeleting" />
            <span>Delete</span>
          </button>

          <button class="save-button" @click="saveTask">
            <Save v-if="!isSaving" size="16" />
            <VueSpinner v-if="isSaving" />
            <span>Save</span>
          </button>
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
  z-index: 1000;
  backdrop-filter: blur(2px);
}

.task-edit-modal {
  background-color: var(--color-background);
  border-radius: 0.5rem;
  width: 90%;
  max-width: 500px;
  box-shadow: var(--shadow-lg);
  overflow: hidden;
  animation: modal-appear 0.2s ease-out;
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

.checkbox-container input[type="checkbox"] {
  margin-right: 0.5rem;
}

.meta-info {
  margin-top: 1rem;
  font-size: var(--font-size-xs);
  color: var(--color-text-tertiary);
}

.modal-footer {
  display: flex;
  justify-content: space-between;
  padding: 1rem 1.5rem;
  border-top: 1px solid var(--color-border);
}

.save-button,
.delete-button {
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

.save-button {
  background-color: var(--color-primary);
  color: white;
  border: none;
}

.save-button:hover {
  background-color: var(--color-primary-dark);
}

.delete-button {
  background-color: transparent;
  color: var(--color-error);
  border: 1px solid var(--color-border);
}

.delete-button:hover {
  background-color: var(--color-background-secondary);
}
</style>
