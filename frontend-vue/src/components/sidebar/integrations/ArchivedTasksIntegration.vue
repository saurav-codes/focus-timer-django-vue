<script setup>
import { computed } from 'vue';
import { CheckCircle, Calendar, Tag, Clock, CircleDashed, LucideListCheck } from 'lucide-vue-next';
import Draggable from 'vuedraggable';
import { useTaskStore } from '../../../stores/taskstore';
import { useTimeAgo } from '@vueuse/core';

const taskStore = useTaskStore();

// Format the created_at date
const timeAgo = (timestamp) => {
  return useTimeAgo(new Date(timestamp)).value;
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

async function handleTaskDroppedToArchived({ added, moved }) {
  // Handle when a task is added to the archived list
  if (added) {
    const element = added.element;
    // Update the task with archived status
    element.status = "ARCHIVED";
    await taskStore.updateTask(element);
    await taskStore.updateTaskOrder(taskStore.archivedTasks);
  }

  // If tasks are reordered within the archived list
  if (moved) {
    await taskStore.updateTaskOrder(taskStore.archivedTasks);
  }
}

const completedTasksCount = computed(() => {
  return taskStore.archivedTasks.filter(task => task.is_completed)?.length;
});
</script>

<template>
  <div class="archived-integration">
    <div class="integration-header">
      <h3>Archived Tasks</h3>
      <div class="archived-subtitle">
        Tasks will be auto-archived after 30 days
      </div>
      <div class="archived-count">
        <LucideListCheck size="14" />
        <span>{{ completedTasksCount }} Completed</span>
      </div>
    </div>

    <div
      class="archived-list">
      <div class="archived-group">
        <Draggable
          v-model="taskStore.archivedTasks"
          drag-class="dragging"
          ghost-class="ghost-card"
          class="archived-tasks-list"
          :force-fallback="true"
          group="kanban-group"
          item-key="id"
          @change="handleTaskDroppedToArchived">
          <template #item="{element}">
            <div class="archived-card">
              <div class="archived-status">
                <CheckCircle v-if="element.is_completed" size="18" class="completed-icon" />
                <CircleDashed v-else size="18" />
              </div>

              <div class="archived-content">
                <div class="archived-title">
                  {{ element.title }}
                </div>

                <div class="archived-meta">
                  <div v-if="element.project" class="archived-project">
                    {{ element.project && typeof element.project === 'object' ? element.project.title : element.project }}
                  </div>
                  <div class="right-part">
                    <div v-if="element.duration_display" class="archived-time">
                      <Clock size="14" />
                      <span>{{ element.duration_display }}</span>
                    </div>
                    <div class="archived-date">
                      <Calendar size="14" />
                      <span>{{ timeAgo(element.created_at) }}</span>
                    </div>
                  </div>
                </div>

                <div class="archived-tags">
                  <div v-for="(tag, index) in element.tags" :key="index" class="archived-tag">
                    <Tag size="12" :class="`tag-${getTagColor(tag)}`" />
                    <span>{{ tag }}</span>
                  </div>
                </div>
              </div>
            </div>
          </template>
        </Draggable>
      </div>

      <div v-if="completedTasksCount === 0" class="no-archived">
        No archived tasks found
      </div>
    </div>
  </div>
</template>

<style scoped>
.archived-integration {
  padding: 16px;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.integration-header {
  display: flex;
  flex-direction: column;
  margin-bottom: 20px;
  position: relative;
}

.integration-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: var(--color-text, #cdd6f4);
}

.archived-subtitle {
  font-size: 12px;
  color: var(--color-text-tertiary, #7f849c);
  margin-top: 4px;
  margin-bottom: 8px;
}

.archived-count {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: var(--color-text-secondary, #a6adc8);
  position: absolute;
  top: 0;
  right: 0;
}

.archived-list {
  flex: 1;
  overflow-y: auto;
}

.archived-tasks-list {
  margin-bottom: 8px;
}

.archived-group {
  margin-bottom: 16px;
}

.archived-date {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: var(--color-text-secondary);
}

.archived-card {
  display: flex;
  align-items: flex-start;
  padding: 12px;
  margin-bottom: 8px;
  background-color: var(--color-background);
  border-radius: 8px;
  border: 1px solid var(--color-border);
  opacity: 0.8;
  cursor: grab;
}

.archived-status {
  margin-right: 10px;
  display: flex;
  align-items: flex-start;
  padding-top: 1px;
}

.completed-icon {
  color: var(--color-success, #a6e3a1);
}

.archived-content {
  flex: 1;
}

.archived-title {
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 6px;
  text-decoration: line-through;
  color: var(--color-text-secondary);
}

.archived-meta {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 8px;
}

.archived-time, .archived-project {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: var(--color-text-tertiary);
}

.archived-meta .right-part {
  display: flex;
  flex-direction: column;
  gap: 4px;
  align-items: flex-end;
}

.archived-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.archived-tag {
  display: flex;
  align-items: center;
  gap: 4px;
  background-color: var(--color-background-secondary);
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 11px;
  color: var(--color-text-tertiary);
}

.no-archived {
  text-align: center;
  padding: 24px;
  color: var(--color-text-tertiary);
  font-style: italic;
}
</style>
