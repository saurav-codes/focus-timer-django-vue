<script setup>

const props = defineProps({
  task: {
    type: Object,
    required: true
  },
  showCheckbox: {
    type: Boolean,
    default: true
  }
});

const emit = defineEmits(['toggle-completion']);

const toggleCompletion = () => {
  if (props.showCheckbox) {
    emit('toggle-completion', props.task.id);
  }
};
</script>

<template>
  <div
    class="task-item"
    :class="{ 'completed': task.completed }">
    <div v-if="showCheckbox" class="task-checkbox" @click="toggleCompletion">
      <div class="checkbox" :class="{ 'checked': task.completed }" />
    </div>
    <div class="task-content">
      <div class="task-title">
        {{ task.title }}
      </div>
      <div class="task-meta">
        <span v-if="task.tag" class="task-tag" :class="`tag-${task.tag.color}`">
          {{ task.tag.name }}
        </span>
      </div>
    </div>
    <div class="task-duration">
      {{ task.duration }}
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
</style>
