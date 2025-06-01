<script setup>
  import { computed } from 'vue'
  import { Clock, Tag, Calendar, ListTodo } from 'lucide-vue-next'
  import Draggable from 'vuedraggable'
  import { useTaskStore } from '../../../stores/taskstore'
  import { useTimeAgo } from '@vueuse/core'

  const taskStore = useTaskStore()

  // Format the created_at date
  const timeAgo = (timestamp) => {
    return useTimeAgo(new Date(timestamp)).value
  }

  // Generate consistent tag colors based on tag name
  const getTagColor = (tagName) => {
    const colors = ['purple', 'blue', 'green', 'red', 'yellow', 'indigo', 'orange', 'pink']
    // Simple hash function to generate a consistent index for each tag
    const hash = tagName.split('').reduce((acc, char) => {
      return acc + char.charCodeAt(0)
    }, 0)
    return colors[hash % colors.length]
  }

  async function handleTaskDroppedToBacklog({ added, moved }) {
    // Handle when a task is added to the backlog list
    if (added) {
      const element = added.element
      // Update the task with backlog status
      element.status = 'BACKLOG'
      await taskStore.updateTask(element)
      await taskStore.updateTaskOrder(taskStore.backlogs)
    }

    // If tasks are reordered within the backlog list
    if (moved) {
      await taskStore.updateTaskOrder(taskStore.backlogs)
    }
  }

  const backlogCount = computed(() => {
    return taskStore.backlogs.length
  })
</script>

<template>
  <div class="backlog-integration">
    <div class="integration-header">
      <h3>Backlog</h3>
      <div class="backlog-subtitle">
        Tasks will be automatically added to the backlog after 15 days of inactivity
      </div>
      <div class="backlog-count">
        <ListTodo size="14" />
        <span>{{ backlogCount }} Tasks</span>
      </div>
    </div>

    <div class="backlog-list">
      <Draggable
        v-model="taskStore.backlogs"
        drag-class="dragging"
        ghost-class="ghost-card"
        class="backlog-tasks-list"
        :force-fallback="true"
        group="kanban-group"
        item-key="id"
        @change="handleTaskDroppedToBacklog">
        <template #item="{ element }">
          <div class="backlog-card">
            <div class="backlog-content">
              <div class="backlog-title">
                {{ element.title }}
              </div>

              <div class="backlog-meta">
                <div class="backlog-time">
                  <Clock size="14" />
                  <span>{{ element.duration_display }}</span>
                </div>

                <div class="backlog-date">
                  <Calendar size="14" />
                  <span>Added {{ timeAgo(element.created_at) }}</span>
                </div>
              </div>

              <div class="backlog-tags">
                <div v-for="(tag, index) in element.tags" :key="index" class="backlog-tag">
                  <Tag size="12" :class="`tag-${getTagColor(tag)}`" />
                  <span>{{ tag }}</span>
                </div>
              </div>
            </div>
          </div>
        </template>
      </Draggable>

      <div v-if="backlogCount === 0" class="no-backlog">No backlog items found</div>
    </div>
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

  .backlog-subtitle {
    font-size: 12px;
    color: var(--color-text-tertiary, #7f849c);
    margin-top: 4px;
    margin-bottom: 8px;
  }

  .backlog-count {
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

  .backlog-list {
    flex: 1;
    overflow-y: auto;
  }

  .backlog-tasks-list {
    margin-bottom: 8px;
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

  .backlog-time,
  .backlog-date {
    display: flex;
    align-items: center;
    font-size: 12px;
    color: var(--color-text-tertiary, #7f849c);
  }

  .backlog-time svg,
  .backlog-date svg {
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
