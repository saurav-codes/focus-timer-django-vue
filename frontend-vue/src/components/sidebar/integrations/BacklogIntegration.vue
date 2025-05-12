<script setup>
import { Clock, Tag, Calendar } from 'lucide-vue-next';
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

function handleTaskOrderUpdate (new_tasks_array) {
  // Update the order of the tasks in the store
  setTimeout(() => {
    taskStore.updateTaskOrder(new_tasks_array);
  }, 2000);
  // 2 second delay is just to make sure that task update
  // operation is done before saving the new order of tasks in that column
}

function handleTaskDroppedToBacklog ( { value }) {
  value.status = "BACKLOG"
  taskStore.updateTask(value);
}


</script>

<template>
  <div class="backlog-integration">
    <div class="integration-header">
      <h3>Backlog</h3>
      <div class="backlog-count">
        {{ taskStore.backlogs.length }} items
      </div>
    </div>

    <SlickList
      v-model:list="taskStore.backlogs"
      :distance="5"
      group="backlog-group"
      :accept="['kanban-group', 'brain-dump-group']"
      class="backlog-list"
      @sort-insert="handleTaskDroppedToBacklog"
      @update:list="handleTaskOrderUpdate">
      <SlickItem
        v-for="(task, idx) in taskStore.backlogs"
        :key="task.id"
        :item="task"
        :index="idx"
        class="backlog-card">
        <div class="backlog-content">
          <div class="backlog-title">
            {{ task.title }}
          </div>

          <div class="backlog-meta">
            <div class="backlog-time">
              <Clock size="14" />
              <span>{{ task.duration_display }}</span>
            </div>

            <div class="backlog-date">
              <Calendar size="14" />
              <span>Added {{ timeAgo(task.created_at) }}</span>
            </div>
          </div>

          <div class="backlog-tags">
            <div v-for="(tag, index) in task.tags" :key="index" class="backlog-tag">
              <Tag size="12" :class="`tag-${getTagColor(tag)}`" />
              <span>{{ tag }}</span>
            </div>
          </div>
        </div>
      </SlickItem>
      <div v-if="taskStore.backlogs.length === 0" class="no-backlog">
        No backlog items found
      </div>
    </SlickList>
  </div>
</template>

<style scoped>
.backlog-integration {
  padding: 16px;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.integration-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.integration-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: var(--color-text, #cdd6f4);
}

.backlog-count {
  font-size: 14px;
  color: var(--color-text-secondary, #a6adc8);
}

.backlog-list {
  flex: 1;
}

.backlog-card {
  position: relative;
  padding: 12px;
  margin-bottom: 8px;
  background-color: var(--color-background, #1e1e2e);
  border-radius: 8px;
  border: 1px solid var(--color-border, #313244);
}

.backlog-title {
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 8px;
}

.backlog-meta {
  display: flex;
  gap: 12px;
  margin-bottom: 8px;
}

.backlog-time, .backlog-date {
  display: flex;
  align-items: center;
  font-size: 12px;
  color: var(--color-text-tertiary, #7f849c);
}

.backlog-time svg, .backlog-date svg {
  margin-right: 4px;
}

.backlog-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.backlog-tag {
  display: flex;
  align-items: center;
  background-color: var(--color-background-secondary, #313244);
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 11px;
  color: var(--color-text-secondary, #a6adc8);
}

.backlog-tag svg {
  margin-right: 4px;
}

.no-backlog {
  text-align: center;
  padding: 24px;
  color: var(--color-text-tertiary, #7f849c);
  font-style: italic;
}
</style>
