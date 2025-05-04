<script setup>
import { ref, watch, computed, onUnmounted} from 'vue';
import { useTaskStore } from '../stores/taskstore';
import { X, Trash2, PencilLine } from 'lucide-vue-next';
import { useTimeAgo } from '@vueuse/core';
import { VueSpinner } from 'vue3-spinners';
import Multiselect from '@vueform/multiselect';
import RecurringTaskEditor from './RecurringTaskEditor.vue';


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
const emit = defineEmits(["closeModal", "task-deleted", "task-updated"])

// Create a copy of the task to edit
const editedTask = ref({ ...props.task });

// Update local copy when prop changes
watch(() => props.task, (newTask) => {
  editedTask.value = { ...newTask };
}, { deep: true });

// Format the created_at date
const timeAgo = computed(() => {
  if (editedTask.value.created_at) {
    return useTimeAgo(new Date(editedTask.value.created_at)).value;
  }
  return '';
});

const saveTask = async () => {
  try {
    await taskStore.updateTask(editedTask.value);
    // emit event for parent to update the task card
    emit("task-updated", editedTask.value);
  } catch (error) {
    console.error('Error updating task:', error);
  }
};

const isDeleting = ref(false);
const deleteTask = async () => {
  if (isDeleting.value) return;
  isDeleting.value = true;
  try {
    emit("task-deleted", editedTask.value.id);
    closeModal();
  } catch (error) {
    console.error('Error deleting task:', error);
  } finally {
    isDeleting.value = false;
  }
};

// Press Escape to close
const handleKeyDown = (event) => {
  if (event.key === 'Escape') {
    closeModal();
  }
};

const selectedTags = computed({
  get() {
    return editedTask.value.tags || [];
  },
  set(newTags) {
    editedTask.value.tags = newTags;
    saveTask();
  }
});

const tagCreated = () => {
  // fetch tags again to update the dropdown
  // we added delay so task update request is completed first
  // otherwise the tag is not available in the dropdown
  // this is a hack to make it work
  // TODO: a better to do this is use useFetch from vuecore which allows
  // to line up the requests to avoid race condition
  setTimeout(() => {
    taskStore.fetchTags();
  }, 2000);
}

const closeModal = () => {
  emit("closeModal")
}

const updateRecurrenceRule = (value) => {
  console.log("updateRecurrenceRule called with value -> ", value);
  editedTask.value.recurrence_rule = value;
  saveTask();
}

const updateStartTime = (value) => {
  console.log("updateStartTime called with value -> ", value);
  editedTask.value.start_at = value;
  saveTask();
}

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeyDown);
});


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
              @blur="saveTask">
          </div>

          <div class="form-group">
            <textarea
              id="task-description"
              v-model.lazy="editedTask.description"
              class="form-textarea"
              placeholder="Add details about this task..."
              rows="4"
              @blur="saveTask" />
          </div>
          <div class="form-group">
            <label class="form-label">Tags</label>
            <Multiselect
              v-model="selectedTags"
              mode="tags"
              :options="taskStore.tags.map(tag => tag.name)"
              :create-option="true"
              :close-on-select="false"
              :caret="true"
              :searchable="true"
              placeholder="Search or add tags"
              @tag="tagCreated" />
          </div>
          <div class="form-group">
            <label class="checkbox-container">
              <input v-model.lazy="editedTask.is_completed" type="checkbox" @change="saveTask">
              <span class="label-text">Completed</span>
            </label>
          </div>

          <!-- Recurring Task Editor -->
          <RecurringTaskEditor
            :value="editedTask.recurrence_rule"
            :start-at="editedTask.start_at"
            @update:start-at="updateStartTime"
            @update:value="updateRecurrenceRule" />

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

.delete-button {
  background-color: transparent;
  color: var(--color-error);
  border: 1px solid var(--color-border);
}

.delete-button:hover {
  background-color: var(--color-background-secondary);
}
</style>
