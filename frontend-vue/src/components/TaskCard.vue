<script setup>
import TaskEditModal from './TaskEditModal.vue';
import TimeDropdownPopup from './TimeDropdownPopup.vue';
import { useTaskStore } from '../stores/taskstore';
import { ref, computed, useTemplateRef } from 'vue';
import { Clock, XIcon } from 'lucide-vue-next';
import {useFloating } from '@floating-ui/vue';
import { useElementHover } from '@vueuse/core'


const taskItem = useTemplateRef('taskItem');
const isHovered = useElementHover(taskItem);


const emit = defineEmits(['task-deleted', 'task-updated', 'tag-removed']);
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

const durationFloatingReference = ref(null);
const floatingComponent = ref(null);
const { floatingStyles} = useFloating(
  durationFloatingReference,
  floatingComponent,
);

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

const removeTag = (tag) => {
  console.log("emiting removing tag", tag);
  console.log("the tags list is", tags.value);
  const updated_tags_list = tags.value.filter(t => t !== tag);
  console.log("the updated tags list is", updated_tags_list);
  emit('tag-removed', updated_tags_list, localTask.value.id);
};

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

const handleTaskUpdated = (updatedTask) => {
  // just emit the event to parent so kanban column can update the task card
  emit('task-updated', updatedTask);
}

// ----- Time Dropdown Popup integration -----
const isTimePopupOpen = ref(false);
// Set default hours/minutes parsed out of the current duration_display
const timePopupHours = ref(0);
const timePopupMinutes = ref(0);

// Helper: parse a string like "1h 30m" into numbers
const parseDurationDisplay = (str) => {
  let hrs = 0, mins = 0;
  if (str) {
    const hourMatch = str.match(/(\d+)h/);
    const minMatch = str.match(/(\d+)m/);
    if (hourMatch) hrs = parseInt(hourMatch[1], 10);
    if (minMatch) mins = parseInt(minMatch[1], 10);
  }
  return { hrs, mins };
};

const openTimeDropdown = () => {
  // Parse current duration if available
  const { hrs, mins } = parseDurationDisplay(localTask.value.planned_duration_display);
  timePopupHours.value = hrs;
  timePopupMinutes.value = mins;
  isTimePopupOpen.value = true;
};

const onTimePopupSave = ({ hours, minutes, formatted, keepOpen }) => {
  // Update localTask duration. Here we update the raw duration (e.g. "1:30")
  // and the display text. You might wish to reformat as needed.
  localTask.value.planned_duration = `${hours}:${minutes}`;
  localTask.value.planned_duration_display = formatted;

  // Only close the popup if it's not just an update
  if (!keepOpen) {
    isTimePopupOpen.value = false;
  }

  // Save the update via the task store.
  taskStore.updateTask(localTask.value);
  handleTaskUpdated(localTask.value);
};

const onTimePopupCancel = () => {
  isTimePopupOpen.value = false;
};

</script>

<template>
  <TaskEditModal
    :task="localTask"
    :is-open="isEditModalOpen"
    @close-modal="closeEditModal"
    @task-updated="handleTaskUpdated"
    @task-deleted="handleTaskDeleted" />
  <div
    ref="taskItem"
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
      <div v-if="tags.length" v-auto-animate class="task-meta">
        <span
          v-for="(tag, index) in tags"
          :key="index"
          class="task-tag"
          :class="`tag-${getTagColor(tag)}`">
          {{ tag }}
          <XIcon v-if="isHovered" class="tag-remove-icon" size="12" @click.stop="removeTag(tag)" />
        </span>
      </div>
    </div>
    <div ref="durationFloatingReference" class="task-duration" @click.stop="openTimeDropdown">
      <Clock v-if="localTask.planned_duration && isHovered" size="14" />
      {{ localTask.planned_duration_display }}
    </div>
    <TimeDropdownPopup
      v-if="isTimePopupOpen"
      ref="floatingComponent"
      :style="floatingStyles"
      :initial-hours="timePopupHours"
      :initial-minutes="timePopupMinutes"
      @save="onTimePopupSave"
      @cancel="onTimePopupCancel" />
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

.tag-remove-icon {
  margin-left: 0.25rem;
  cursor: pointer;
  border-radius: 50%;
}
.tag-remove-icon:hover {
  padding: 0.03rem;
  transform: scale(1.2);
  transition: ease-out 0.01s;
  background-color: var(--color-background-secondary);
  color: var(--color-text-secondary);
}

.task-duration {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.25rem;
  font-size: var(--font-size-xs);
  color: var(--color-text-tertiary);
  white-space: nowrap;
  padding: 0.25rem;
  border-radius: 0.5rem;
  cursor: pointer;
}
.task-duration:hover {
  background-color: var(--color-background-tertiary);
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
