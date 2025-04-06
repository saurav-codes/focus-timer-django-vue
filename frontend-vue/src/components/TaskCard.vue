<script setup>
import TaskEditModal from './TaskEditModal.vue';
import { useTaskStore } from '../stores/taskstore';
import { ref, computed, defineEmits } from 'vue';
import { Trash2 } from 'lucide-vue-next';

const emit = defineEmits(['task-deleted']);
const taskStore = useTaskStore();
const props = defineProps({
  task: {
    type: Object,
    required: true
  },
  showCheckbox: {
    type: Boolean,
    default: true
  },
});

const localTask = computed(() => {
  return props.task;
});

const tags = computed(() => {
  if (localTask.value.tags) {
    if (Array.isArray(localTask.value.tags)) {
      return localTask.value.tags.flatMap(tag => {
        if (typeof tag === 'string' && tag.includes(',')) {
          return tag.split(',');
        }
        return tag;
      });
    }
  }
  return [];
});

// Generate consistent tag colors based on tag name
const getTagColor = (tagName) => {
  const colors = ['purple', 'blue', 'green', 'red', 'yellow', 'indigo', 'orange', 'pink'];
  // Simple hash function to generate a consistent index for each tag
  const hash = tagName.split('').reduce((acc, char) => {
    return acc + char.charCodeAt(0);
  }, 0);
  return colors[hash % colors.length];
};

const toggleCompletion = () => {
  if (props.showCheckbox) {
    localTask.value.is_completed = !localTask.value.is_completed;
    taskStore.toggleCompletion(props.task.id);
  }
};

const isEditModalOpen = ref(false)
const openEditModal = () => {
  isEditModalOpen.value = true
}

const closeEditModal = () => {
  isEditModalOpen.value = false
}

const handleTaskDeleted = (taskId) => {
  // edittaskmodal already deleted the task
  // so we just need to emit the event to parent so
  // kanban column can update the task order and also
  // remove the task from the UI.
  emit('task-deleted', taskId);
}

const deleteTask = () => {
  // delete the task using hover delete button
  if (confirm('Are you sure you want to delete this task?')) {
    taskStore.deleteTask(props.task.id);
    emit('task-deleted', props.task.id);
  }
};

</script>

<template>
  <TaskEditModal :task="localTask" :is-open="isEditModalOpen" @close-modal="closeEditModal" @task-deleted="handleTaskDeleted" />
  <div
    class="task-item"
    :class="{ 'completed': localTask.is_completed }"
    @click="openEditModal">
    <div v-if="showCheckbox" class="task-checkbox" @click.stop="toggleCompletion">
      <div class="checkbox" :class="{ 'checked': localTask.is_completed }" />
    </div>
    <div class="task-content">
      <div class="task-title">
        {{ localTask.title }}
      </div>
      <div v-if="tags.length" class="task-meta">
        <span
          v-for="(tag, index) in tags"
          :key="index"
          class="task-tag"
          :class="`tag-${getTagColor(tag)}`">
          {{ tag }}
        </span>
      </div>
    </div>
    <div class="task-duration">
      {{ localTask.duration }}
    </div>

    <!-- Delete button that shows on hover -->
    <button
      class="delete-button"
      aria-label="Delete task"
      @click.stop="deleteTask">
      <Trash2 size="16" />
    </button>
  </div>
</template>

<style scoped>
.task-item {
  display: flex;
  align-items: flex-start;
  padding: 0.75rem;
  border-radius: 0.375rem;
  background-color: var(--color-background);
  border: 1px solid var(--color-border);
  transition: background-color var(--transition-base);
  cursor: move;
  user-select: none;
  position: relative; /* Add this for absolute positioning of delete button */
}

.task-item:hover {
  background-color: var(--color-background-secondary);
}

.task-checkbox {
  margin-right: 0.75rem;
  padding-top: 0.125rem;
}

.checkbox {
  width: 18px;
  height: 18px;
  border: 2px solid var(--color-neutral-400);
  border-radius: 50%;
  cursor: pointer;
  transition: all var(--transition-base);
}

.checkbox:hover {
  border-color: var(--color-primary);
}

.checkbox.checked {
  background-color: var(--color-success);
  border-color: var(--color-success);
  position: relative;
}

.checkbox.checked::after {
  content: '';
  position: absolute;
  left: 5px;
  top: 2px;
  width: 5px;
  height: 9px;
  border: solid white;
  border-width: 0 2px 2px 0;
  transform: rotate(45deg);
}

.task-content {
  flex: 1;
  min-width: 0;
  cursor: pointer;
}

.task-title {
  font-size: var(--font-size-sm);
  color: var(--color-text-primary);
  margin-bottom: 0.25rem;
  word-break: break-word;
  line-height: 1.4;
}

.completed .task-title {
  text-decoration: line-through;
  color: var(--color-text-tertiary);
}

.task-meta {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.task-tag {
  font-size: var(--font-size-xs);
  padding: 0.125rem 0.375rem;
  border-radius: 1rem;
  color: white;
  display: inline-flex;
  align-items: center;
}

.task-duration {
  font-size: var(--font-size-xs);
  color: var(--color-text-tertiary);
  white-space: nowrap;
  padding-left: 0.5rem;
}

.tag-purple {
  background-color: #9333ea;
}

.tag-blue {
  background-color: #3b82f6;
}

.tag-green {
  background-color: #10b981;
}

.tag-red {
  background-color: #ef4444;
}

.tag-yellow {
  background-color: #f59e0b;
}

.tag-indigo {
  background-color: #6366f1;
}

.tag-orange {
  background-color: #f97316;
}

.tag-pink {
  background-color: #ec4899;
}

/* Delete button styling */
.delete-button {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  width: 1.5rem;
  height: 1.5rem;
  border-radius: 50%;
  background-color: var(--color-danger, #ef4444);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  cursor: pointer;
  opacity: 0;
  transform: scale(0.8);
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.task-item:hover .delete-button {
  opacity: 0.85;
  transform: scale(1);
}

.delete-button:hover {
  opacity: 1;
  transform: scale(1.05);
}

.delete-button:focus {
  outline: 2px solid var(--color-primary);
  opacity: 1;
}
</style>
