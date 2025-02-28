<script setup>
import { useDateFormat } from '@vueuse/core';
import BrainDumpVue from '@/components/BrainDump.vue';
import KanbanColumn from '@/components/KanbanColumn.vue';

const today = new Date();

// Use useDateFormat for consistent date formatting
const formatDate = (date) => {
  return useDateFormat(date, 'ddd, MMM D').value;
};

// Create a new date object to avoid mutation issues
const getTomorrow = () => {
  const tomorrow = new Date(today);
  tomorrow.setDate(today.getDate() + 1);
  return tomorrow;
};

const getDayAfter = () => {
  const dayAfter = new Date(today);
  dayAfter.setDate(today.getDate() + 2);
  return dayAfter;
};

const dates = {
  today: formatDate(today),
  tomorrow: formatDate(getTomorrow()),
  dayAfter: formatDate(getDayAfter())
};

const handleTaskCompletion = (data) => {
  console.log('Task completion toggled:', data);
  // Here you would update your global state or make API calls
};

const handleAddTask = (task) => {
  console.log('New task added:', task);
  // Here you would update your global state or make API calls
};
</script>

<template>
  <div class="kanban-planner">
    <BrainDumpVue />
    <div class="kanban-columns">
      <KanbanColumn
        title="Today"
        :date="dates.today"
        :allow-add-task="true"
        @toggle-completion="handleTaskCompletion"
        @add-task="handleAddTask" />
      <KanbanColumn
        title="Tomorrow"
        :date="dates.tomorrow"
        @toggle-completion="handleTaskCompletion" />
      <KanbanColumn
        title="Day After"
        :date="dates.dayAfter"
        @toggle-completion="handleTaskCompletion" />
    </div>
  </div>
</template>

<style scoped>
.kanban-planner {
  display: flex;
  height: 100vh;
  overflow: hidden;
}

.kanban-columns {
  flex: 1;
  display: flex;
  gap: 1rem;
  padding: 1rem;
  overflow-x: auto;
}
</style>
