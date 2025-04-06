<script setup>
import TaskEditModal from './TaskEditModal.vue';
import { useTaskStore } from '../stores/taskstore';
import { ref, computed } from 'vue';

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

</script>

<template>
  <TaskEditModal :task="localTask" :is-open="isEditModalOpen" @close-modal="closeEditModal" />
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
</style>
