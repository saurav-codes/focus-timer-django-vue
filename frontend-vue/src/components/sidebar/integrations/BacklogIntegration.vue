<script setup>
import { ref } from 'vue';
import { Clock, Tag, Calendar } from 'lucide-vue-next';

// Mock backlog data
const backlogTasks = ref([
  {
    id: 1,
    title: 'Implement dark mode toggle',
    category: 'Feature',
    estimatedTime: '4h',
    addedDate: '2 weeks ago',
    tags: ['UI', 'Theme']
  },
  {
    id: 2,
    title: 'Fix mobile responsiveness issues',
    category: 'Bug',
    estimatedTime: '3h',
    addedDate: '1 week ago',
    tags: ['Mobile', 'CSS']
  },
  {
    id: 3,
    title: 'Add export to CSV functionality',
    category: 'Feature',
    estimatedTime: '5h',
    addedDate: '3 days ago',
    tags: ['Data', 'Export']
  },
  {
    id: 4,
    title: 'Optimize database queries',
    category: 'Performance',
    estimatedTime: '8h',
    addedDate: 'yesterday',
    tags: ['Backend', 'Database']
  }
]);

// Get category color
const getCategoryColor = (category) => {
  switch (category.toLowerCase()) {
    case 'feature':
      return 'var(--color-primary, #89b4fa)';
    case 'bug':
      return 'var(--color-error, #f38ba8)';
    case 'performance':
      return 'var(--color-warning, #f9e2af)';
    default:
      return 'var(--color-text-tertiary, #7f849c)';
  }
};
</script>

<template>
  <div class="backlog-integration">
    <div class="integration-header">
      <h3>Backlog</h3>
      <div class="backlog-count">{{ backlogTasks.length }} items</div>
    </div>
    
    <div class="backlog-list">
      <div v-for="task in backlogTasks" :key="task.id" class="backlog-card">
        <div class="backlog-category" :style="{ backgroundColor: getCategoryColor(task.category) }">
          {{ task.category }}
        </div>
        
        <div class="backlog-content">
          <div class="backlog-title">{{ task.title }}</div>
          
          <div class="backlog-meta">
            <div class="backlog-time">
              <Clock size="14" />
              <span>{{ task.estimatedTime }}</span>
            </div>
            
            <div class="backlog-date">
              <Calendar size="14" />
              <span>Added {{ task.addedDate }}</span>
            </div>
          </div>
          
          <div class="backlog-tags">
            <div v-for="(tag, index) in task.tags" :key="index" class="backlog-tag">
              <Tag size="12" />
              <span>{{ tag }}</span>
            </div>
          </div>
        </div>
      </div>
      
      <div v-if="backlogTasks.length === 0" class="no-backlog">
        No backlog items found
      </div>
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

.backlog-category {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 500;
  color: var(--color-background, #1e1e2e);
  margin-bottom: 8px;
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