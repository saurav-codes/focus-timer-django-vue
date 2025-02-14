<script setup>
import { onMounted } from 'vue';
import TaskColumn from './TaskColumn.vue';
import { useTaskStore } from '../stores/taskstore';

const taskStore = useTaskStore();

onMounted(() => {
  taskStore.fetchTasks();
});

const handleUpdateTask = (task, status) => {
  taskStore.updateTaskStatus(task, status);
};

const handleReorderTasksOnBackend = (columnIndex, newTasks) => {
  taskStore.reorderColumnTasksOnBackend(columnIndex, newTasks);
};
</script>

<template>
  <div class="app-container">
    <div class="main-content">
      <div class="calendar-view">
        <TaskColumn
          v-for="(column, index) in taskStore.columns"
          :key="column.date"
          :column-index="index"
          :date="column.date"
          :tasks="column.tasks"
          @update-task="handleUpdateTask"
          @reorder-tasks-on-backend="handleReorderTasksOnBackend(index, $event)"
        />
      </div>
    </div>
  </div>
</template>

<style scoped>
.app-container {
  display: flex;
  height: 100vh;
  background: #f2f3f5;
  color: #333;
}
.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: #fff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}
.calendar-view {
  flex: 1;
  display: flex;
  overflow-x: auto;
  padding: 1rem;
  background: #f7f8fa;
  gap: 1rem;
}
</style>
