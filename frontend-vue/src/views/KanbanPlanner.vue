<script setup>
import { onMounted, ref } from 'vue';
import { useDateFormat } from '@vueuse/core';
import { ChevronRight } from 'lucide-vue-next';
import BrainDumpVue from '@/components/BrainDump.vue';
import KanbanColumn from '@/components/KanbanColumn.vue';

// Add state for controlling the scroll indicator visibility
const showScrollIndicator = ref(true);

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

const getYesterday = () => {
  const yesterday = new Date(today);
  yesterday.setDate(today.getDate() - 1);
  return yesterday;
};

// Add functions for additional date columns
const getNextWeek = () => {
  const nextWeek = new Date(today);
  nextWeek.setDate(today.getDate() + 7);
  return nextWeek;
};

const getAfterNextWeek = () => {
  const afterNextWeek = new Date(today);
  afterNextWeek.setDate(today.getDate() + 14);
  return afterNextWeek;
};

const getNextMonth = () => {
  const nextMonth = new Date(today);
  nextMonth.setMonth(today.getMonth() + 1);
  return nextMonth;
};

const dates = {
  yesterday: formatDate(getYesterday()),
  today: formatDate(today),
  tomorrow: formatDate(getTomorrow()),
  nextWeek: formatDate(getNextWeek()),
  afterNextWeek: formatDate(getAfterNextWeek()),
  nextMonth: formatDate(getNextMonth()),
};

const handleTaskCompletion = (data) => {
  console.log('Task completion toggled:', data);
  // Here you would update your global state or make API calls
};

const handleAddTask = (task) => {
  console.log('New task added:', task);
  // Here you would update your global state or make API calls
};

// Add this function for scroll animation when page load to indicate user can scroll to the right
const animateScroll = () => {
  const container = document.querySelector('.kanban-columns-wrapper');
  if (!container) return;

  const originalScroll = container.scrollLeft;
  const targetScroll = 100; // Scroll right by 100px

  // Animate scroll right
  container.scrollTo({
    left: targetScroll,
    behavior: 'smooth'
  });

  // After 1 second, scroll back
  setTimeout(() => {
    container.scrollTo({
      left: originalScroll,
      behavior: 'smooth'
    });
  }, 1000);
};

// Run animation when component mounts and hide the indicator after animation
onMounted(() => {
  // Small delay to ensure content is rendered
  setTimeout(() => {
    animateScroll();

    // Hide the indicator after the animation completes
    setTimeout(() => {
      showScrollIndicator.value = false;
    }, 2000); // Hide after 2 seconds (animation + a bit more time)
  }, 500);
});
</script>

<template>
  <div class="kanban-planner">
    <!-- Brain Dump will be fixed -->
    <div class="brain-dump-wrapper">
      <BrainDumpVue />

      <!-- Scroll indicator -->
      <div v-if="showScrollIndicator" class="scroll-indicator">
        <ChevronRight size="24" />
      </div>
    </div>

    <!-- Scrollable columns container -->
    <div class="kanban-columns-wrapper">
      <div class="kanban-columns">
        <KanbanColumn
          title="Yesterday"
          :date="dates.yesterday"
          @toggle-completion="handleTaskCompletion"
          @add-task="handleAddTask" />
        <KanbanColumn
          title="Today"
          :date="dates.today"
          @toggle-completion="handleTaskCompletion"
          @add-task="handleAddTask" />
        <KanbanColumn
          title="Tomorrow"
          :date="dates.tomorrow"
          @toggle-completion="handleTaskCompletion"
          @add-task="handleAddTask" />
        <KanbanColumn
          title="Next Week"
          :date="dates.nextWeek"
          @toggle-completion="handleTaskCompletion"
          @add-task="handleAddTask" />
        <KanbanColumn
          title="After Next Week"
          :date="dates.afterNextWeek"
          @toggle-completion="handleTaskCompletion"
          @add-task="handleAddTask" />
        <KanbanColumn
          title="Next Month"
          :date="dates.nextMonth"
          @toggle-completion="handleTaskCompletion"
          @add-task="handleAddTask" />
      </div>
    </div>
  </div>
</template>

<style scoped>
.kanban-planner {
  display: flex;
  height: 100vh;
  overflow: hidden;
}

/* Fixed Brain Dump sidebar */
.brain-dump-wrapper {
  position: sticky;
  top: 0;
  left: 0;
  height: 100vh;
  z-index: 10;
  position: relative;
  /* Keep right shadow for depth */
  box-shadow: 4px 0 10px -3px rgba(0, 0, 0, 0.15);
}

/* Scroll indicator styling */
.scroll-indicator {
  position: absolute;
  right: -12px;
  top: 50%;
  transform: translateY(-50%);
  background-color: var(--color-background);
  color: var(--color-primary);
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: var(--shadow-md);
  z-index: 20;
  animation: bounce-right 1.5s infinite;
  opacity: 0.9;
}

/* Bouncing animation */
@keyframes bounce-right {
  0%, 100% {
    transform: translateY(-50%) translateX(0);
  }
  50% {
    transform: translateY(-50%) translateX(5px);
  }
}

/* Scrollable columns container */
.kanban-columns-wrapper {
  flex: 1;
  overflow-x: auto;
  overflow-y: hidden;
  scroll-behavior: smooth;
  /* Keep slight padding for spacing */
  padding-left: 10px;
}

.kanban-columns-wrapper::-webkit-scrollbar {
  height: 8px;
}

.kanban-columns-wrapper::-webkit-scrollbar-track {
  background: var(--color-background-secondary);
  border-radius: 4px;
}

.kanban-columns-wrapper::-webkit-scrollbar-thumb {
  background: var(--color-border);
  border-radius: 4px;
}

.kanban-columns-wrapper::-webkit-scrollbar-thumb:hover {
  background: var(--color-text-tertiary);
}

.kanban-columns {
  display: flex;
  gap: 1rem;
  padding: 1rem;
  min-width: min-content; /* Ensures columns don't shrink below their natural width */
}

:deep(.kanban-column) {
  /* Keep a subtle shadow for depth but not as pronounced */
  box-shadow: 0 2px 8px -2px rgba(0, 0, 0, 0.08);
}

:deep(.kanban-column:nth-child(1)),
:deep(.kanban-column:nth-child(2)),
:deep(.kanban-column:nth-child(3)),
:deep(.kanban-column:nth-child(n+4)) {
  transform: none;
  z-index: auto;
}

:deep(.kanban-column:hover) {
  transform: none;
  z-index: auto;
}
</style>
