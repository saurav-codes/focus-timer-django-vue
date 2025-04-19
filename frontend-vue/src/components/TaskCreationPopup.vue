<script setup>
import { ref, watch } from 'vue';
import { X, Plus } from 'lucide-vue-next';
import { useTaskStore } from '../stores/taskstore';
import { useAuthStore } from '../stores/authStore';
import { onKeyStroke } from '@vueuse/core';

const props = defineProps({
  isVisible: {
    type: Boolean,
    default: false
  }
});

const emit = defineEmits(['close']);

const taskStore = useTaskStore();
const authStore = useAuthStore();

const newTaskTitle = ref('');
const inputRef = ref(null);

// Watch for visibility changes and focus input when visible
watch(() => props.isVisible, (newVal) => {
  if (newVal) {
    // Focus the input after the DOM updates
    setTimeout(() => {
      inputRef.value?.focus();
    }, 0);
  }
});

// Add task and close popup
const addTask = async () => {
  if (newTaskTitle.value.trim()) {
    // Create new task object
    const newTask = {
      id: Date.now(),
      title: newTaskTitle.value,
      is_completed: false,
      planned_duration: '0:30', // Default 30 minutes duration
      planned_duration_display: '30m',
      order: 0,
      tags: [],
      user: authStore.userData.id,
    };

    // Add the task to the brain dump tasks (optimistic update)
    taskStore.brainDumpTasks.unshift(newTask);

    // Reset input and close popup
    newTaskTitle.value = '';

    // Create task in backend
    const data = await taskStore.createTask(newTask);

    // Update task ID with the one from backend
    taskStore.brainDumpTasks[0].id = data.id;

    // Update task order
    taskStore.updateTaskOrder(taskStore.brainDumpTasks);
  } else {
    // Close popup if task is empty
    emit('close');
  }
};

// Handle keyboard events
const handleKeyDown = (event) => {
  if (event.key === 'Enter') {
    addTask();
  } else if (event.key === 'Escape') {
    emit('close');
  }
};

// Register Escape key listener globally
onKeyStroke('Escape', () => {
  if (props.isVisible) {
    emit('close');
  }
});
</script>

<template>
  <Teleport to="body">
    <div v-if="isVisible" class="popup-overlay" @click="$emit('close')">
      <div class="popup-container" @click.stop>
        <div class="popup-header">
          <span class="popup-title">Create Task</span>
          <button class="close-button" @click="$emit('close')"><X size="18" /></button>
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
              @keydown="handleKeyDown" />
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
.popup-overlay {
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
  z-index: 1000;
  animation: fadeIn 0.2s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
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
  from { transform: translateY(-20px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
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
  transition: border-color 0.2s, box-shadow 0.2s;
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

.shortcuts-hint {
  display: flex;
  gap: 16px;
  margin-top: 16px;
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
