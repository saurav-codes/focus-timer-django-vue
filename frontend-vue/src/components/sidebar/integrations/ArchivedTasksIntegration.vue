<script setup>
import { ref, computed } from 'vue';
import { CheckCircle, Calendar, Tag } from 'lucide-vue-next';

// Mock archived tasks data
const archivedTasks = ref([
  {
    id: 1,
    title: 'Research competitor features',
    completedDate: '2 days ago',
    project: 'Market Analysis',
    tags: ['Research']
  },
  {
    id: 2,
    title: 'Create wireframes for landing page',
    completedDate: '1 week ago',
    project: 'Website Redesign',
    tags: ['Design', 'UI']
  },
  {
    id: 3,
    title: 'Update user documentation',
    completedDate: '2 weeks ago',
    project: 'Knowledge Base',
    tags: ['Documentation']
  },
  {
    id: 4,
    title: 'Fix login page validation',
    completedDate: '3 weeks ago',
    project: 'Bug Fixes',
    tags: ['Frontend', 'Auth']
  }
]);

// Group tasks by completion date
const groupedTasks = computed(() => {
  const groups = {};

  archivedTasks.value.forEach(task => {
    if (!groups[task.completedDate]) {
      groups[task.completedDate] = [];
    }
    groups[task.completedDate].push(task);
  });

  return groups;
});
</script>

<template>
  <div class="archived-integration">
    <div class="integration-header">
      <h3>Archived Tasks</h3>
      <div class="archived-count">
        {{ archivedTasks.length }} completed
      </div>
    </div>

    <div class="archived-list">
      <div v-for="(tasks, date) in groupedTasks" :key="date" class="archived-group">
        <div class="archived-date">
          <Calendar size="14" />
          <span>{{ date }}</span>
        </div>

        <div v-for="task in tasks" :key="task.id" class="archived-card">
          <div class="archived-status">
            <CheckCircle size="16" class="completed-icon" />
          </div>

          <div class="archived-content">
            <div class="archived-title">
              {{ task.title }}
            </div>
            <div class="archived-project">
              {{ task.project }}
            </div>

            <div class="archived-tags">
              <div v-for="(tag, index) in task.tags" :key="index" class="archived-tag">
                <Tag size="12" />
                <span>{{ tag }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div v-if="archivedTasks.length === 0" class="no-archived">
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

.archived-count {
  font-size: 14px;
  color: var(--color-text-secondary, #a6adc8);
}

.archived-list {
  flex: 1;
}

.archived-group {
  margin-bottom: 16px;
}

.archived-date {
  display: flex;
  align-items: center;
  font-size: 13px;
  font-weight: 500;
  color: var(--color-text-secondary, #a6adc8);
  margin-bottom: 8px;
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

.archived-project {
  font-size: 12px;
  color: var(--color-text-tertiary, #7f849c);
  margin-bottom: 8px;
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

.no-archived {
  text-align: center;
  padding: 24px;
  color: var(--color-text-tertiary, #7f849c);
  font-style: italic;
}
</style>
