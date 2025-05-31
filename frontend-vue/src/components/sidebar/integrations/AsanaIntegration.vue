<script setup>
  import { ref } from 'vue'
  import { CheckCircle, Clock, AlertTriangle } from 'lucide-vue-next'

  // Mock Asana data
  const tasks = ref([
    {
      id: 1,
      title: 'Design system implementation',
      project: 'Website Redesign',
      dueDate: 'Tomorrow',
      priority: 'high',
      status: 'in_progress',
    },
    {
      id: 2,
      title: 'API Integration for tasks',
      project: 'Backend Development',
      dueDate: 'Next week',
      priority: 'medium',
      status: 'todo',
    },
    {
      id: 3,
      title: 'User testing session',
      project: 'UX Research',
      dueDate: 'Today',
      priority: 'high',
      status: 'in_progress',
    },
    {
      id: 4,
      title: 'Documentation update',
      project: 'Knowledge Base',
      dueDate: 'Yesterday',
      priority: 'low',
      status: 'completed',
    },
  ])

  // Get status icon based on task status
  const getStatusIcon = (task) => {
    if (task.status === 'completed') {
      return CheckCircle
    } else if (task.status === 'in_progress') {
      return Clock
    } else {
      return AlertTriangle
    }
  }

  // Get status color based on task priority and status
  const getStatusColor = (task) => {
    if (task.status === 'completed') {
      return 'var(--color-success, #a6e3a1)'
    } else if (task.priority === 'high') {
      return 'var(--color-error, #f38ba8)'
    } else if (task.priority === 'medium') {
      return 'var(--color-warning, #f9e2af)'
    } else {
      return 'var(--color-text-tertiary, #7f849c)'
    }
  }
</script>

<template>
  <div class="asana-integration">
    <div class="integration-header">
      <h3>Asana</h3>
      <div class="task-count">{{ tasks.length }} tasks</div>
    </div>

    <div class="tasks-list">
      <div v-for="task in tasks" :key="task.id" class="task-card">
        <div class="task-status" :style="{ color: getStatusColor(task) }">
          <component :is="getStatusIcon(task)" size="16" />
        </div>

        <div class="task-content">
          <div class="task-title">{{ task.title }}</div>
          <div class="task-project">{{ task.project }}</div>
          <div class="task-due-date">Due: {{ task.dueDate }}</div>
        </div>

        <div class="task-priority" :class="task.priority">
          {{ task.priority }}
        </div>
      </div>

      <div v-if="tasks.length === 0" class="no-tasks">No tasks found</div>
    </div>
  </div>
</template>

<style scoped>
  .asana-integration {
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

  .task-count {
    font-size: 14px;
    color: var(--color-text-secondary, #a6adc8);
  }

  .tasks-list {
    flex: 1;
  }

  .task-card {
    display: flex;
    align-items: flex-start;
    padding: 12px;
    margin-bottom: 8px;
    background-color: var(--color-background, #1e1e2e);
    border-radius: 8px;
    border: 1px solid var(--color-border, #313244);
  }

  .task-status {
    margin-right: 12px;
    padding-top: 2px;
  }

  .task-content {
    flex: 1;
  }

  .task-title {
    font-size: 14px;
    font-weight: 500;
    margin-bottom: 4px;
  }

  .task-project {
    font-size: 12px;
    color: var(--color-text-secondary, #a6adc8);
    margin-bottom: 4px;
  }

  .task-due-date {
    font-size: 12px;
    color: var(--color-text-tertiary, #7f849c);
  }

  .task-priority {
    font-size: 11px;
    padding: 2px 6px;
    border-radius: 4px;
    text-transform: uppercase;
    font-weight: 500;
  }

  .task-priority.high {
    background-color: rgba(243, 139, 168, 0.2);
    color: var(--color-error, #f38ba8);
  }

  .task-priority.medium {
    background-color: rgba(249, 226, 175, 0.2);
    color: var(--color-warning, #f9e2af);
  }

  .task-priority.low {
    background-color: rgba(166, 227, 161, 0.2);
    color: var(--color-success, #a6e3a1);
  }

  .no-tasks {
    text-align: center;
    padding: 24px;
    color: var(--color-text-tertiary, #7f849c);
    font-style: italic;
  }
</style>
