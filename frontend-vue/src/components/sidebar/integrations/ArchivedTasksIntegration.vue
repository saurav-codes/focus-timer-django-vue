<script setup>
import { computed } from 'vue';
import { CheckCircle, Calendar, Tag, Clock, CircleDashed, LucideListCheck } from 'lucide-vue-next';
import { SlickItem, SlickList } from 'vue-slicksort';
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

async function handleTaskDroppedToArchived ( { value }) {
  value.status = "ARCHIVED"
  await taskStore.updateTask(value);
}

const completedTasksCount = computed(() => {
  return taskStore.archivedTasks.filter(task => task.is_completed).length;
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
        <LucideListCheck size="12" />
        {{ completedTasksCount }} Completed
      </div>
    </div>

    <div
      class="archived-list">
      <div class="archived-group">
        <SlickList
          v-model:list="taskStore.archivedTasks"
          :distance="5"
          group="archived-group"
          class="archived-tasks-list"
          :accept="['kanban-group', 'brain-dump-group']"
          @sort-insert="handleTaskDroppedToArchived">
          <SlickItem
            v-for="(task,idx) in taskStore.archivedTasks"
            :key="task.id"
            :item="task"
            :index="idx"
            class="archived-card">
            <div class="archived-status">
              <CheckCircle v-if="task.is_completed" size="16" class="completed-icon" />
              <CircleDashed v-else size="16" />
            </div>

            <div class="archived-content">
              <div class="archived-title">
                {{ task.title }}
              </div>

              <div class="archived-meta">
                <div v-if="task.planned_duration_display" class="archived-time">
                  <Clock size="14" />
                  <span>{{ task.planned_duration_display }}</span>
                </div>

                <div v-if="task.project" class="archived-project">
                  {{ task.project && typeof task.project === 'object' ? task.project.title : task.project }}
                </div>
                <div class="archived-date">
                  <Calendar size="14" />
                  <span>{{ timeAgo(task.created_at) }}</span>
                </div>
              </div>

              <div class="archived-tags">
                <div v-for="(tag, index) in task.tags" :key="index" class="archived-tag">
                  <Tag size="12" :class="`tag-${getTagColor(tag)}`" />
                  <span>{{ tag }}</span>
                </div>
              </div>
            </div>
          </SlickItem>
        </SlickList>
      </div>

      <div v-if="taskStore.archivedTasks.length === 0" class="no-archived">
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
  font-size: 12px;
  color: var(--color-text-secondary, #a6adc8);
}

.archived-date svg {
  margin-right: 6px;
}

.archived-card {
  display: flex;
  align-items: flex-start;
  padding: 12px;
  margin-bottom: 8px;
  background-color: var(--color-background, #1e1e2e);
  border-radius: 8px;
  border: 1px solid var(--color-border, #313244);
  opacity: 0.8;
}

.archived-status {
  margin-right: 12px;
  padding-top: 2px;
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
  margin-bottom: 4px;
  text-decoration: line-through;
  color: var(--color-text-secondary, #a6adc8);
}

.archived-meta {
  display: flex;
  gap: 12px;
  margin-bottom: 8px;
}

.archived-time, .archived-project {
  display: flex;
  align-items: center;
  font-size: 12px;
  color: var(--color-text-tertiary, #7f849c);
}

.archived-time svg {
  margin-right: 4px;
}

.archived-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.archived-tag {
  display: flex;
  align-items: center;
  background-color: var(--color-background-secondary, #313244);
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 11px;
  color: var(--color-text-tertiary, #7f849c);
}

.archived-tag svg {
  margin-right: 4px;
}

/* Tag colors */
.tag-purple { color: #c678dd; }
.tag-blue { color: #61afef; }
.tag-green { color: #98c379; }
.tag-red { color: #e06c75; }
.tag-yellow { color: #e5c07b; }
.tag-indigo { color: #7c7cff; }
.tag-orange { color: #d19a66; }
.tag-pink { color: #ff79c6; }

.no-archived {
  text-align: center;
  padding: 24px;
  color: var(--color-text-tertiary, #7f849c);
  font-style: italic;
}
</style>
