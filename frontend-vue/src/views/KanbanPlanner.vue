<script setup>
import { onMounted, ref } from 'vue';
import { useDateFormat } from '@vueuse/core';
import { ChevronRight } from 'lucide-vue-next';
import BrainDumpVue from '@/components/BrainDump.vue';
import KanbanColumn from '@/components/KanbanColumn.vue';
import IntegrationSidebar from '@/components/sidebar/IntegrationSidebar.vue';

// Capture scrollable container reference to handle scroll during drag
const scrollContainerRef = ref(null);

// Make this global so SlickList components can access it
window.SCROLL_CONTAINER_REF = null;

onMounted(() => {
  // Store reference to the scrollable container for drag operations
  window.SCROLL_CONTAINER_REF = scrollContainerRef.value;
});

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

// Create refs for each column to access their methods
const brainDumpRef = ref(null);
const columnRefs = {
  yesterday: ref(null),
  today: ref(null),
  tomorrow: ref(null),
  nextWeek: ref(null),
  afterNextWeek: ref(null),
  nextMonth: ref(null)
};

// Handle task moved from brain dump to a kanban column
const handleTaskMovedToColumn = ({ task, columnId }) => {
  console.log('Task moved from brain dump to column:', columnId, task);
  columnRefs[columnId].value?.addTaskFromExternal(task);
};

// Handle task moved from a kanban column to brain dump
const handleTaskMovedToBrainDump = (task) => {
  console.log('Task moved to brain dump:', task);
  brainDumpRef.value?.addTaskFromColumn(task);
};

// Handle task moved between kanban columns
const handleTaskMovedBetweenColumns = ({ task, toColumnId }) => {
  console.log('Task moved between columns:', toColumnId, task);
  columnRefs[toColumnId].value?.addTaskFromExternal(task);
};

// Handle task reordering within a column
const handleTaskReordering = ({ columnId, tasks, oldIndex, newIndex }) => {
  console.log(`Tasks reordered in ${columnId}:`, { oldIndex, newIndex });
  // Here you would typically update your backend/store with the new order
  // For example, if using a store:
  // store.dispatch('updateTaskOrder', { columnId, tasks, oldIndex, newIndex });

  // Or if you need to make a backend call:
  // api.updateTaskOrder(columnId, tasks);
};

</script>

<template>
  <div class="kanban-planner">
    <div class="brain-dump-wrapper">
      <BrainDumpVue
        ref="brainDumpRef"
        @task-moved-to-column="handleTaskMovedToColumn"
        @reorder-tasks="handleTaskReordering" />

      <!-- Scroll indicator -->
      <div v-if="showScrollIndicator" class="scroll-indicator">
        <ChevronRight size="24" />
      </div>
    </div>

    <!-- Integration Sidebar (conditionally shown) -->
    <IntegrationSidebar class="integration-sidebar-wrapper" />

    <!-- Scrollable columns container -->
    <div ref="scrollContainerRef" class="kanban-columns-wrapper">
      <div class="kanban-columns">
        <KanbanColumn
          :ref="el => columnRefs.yesterday = el"
          title="Yesterday"
          column-id="yesterday"
          :date="dates.yesterday"
          @toggle-completion="handleTaskCompletion"
          @add-task="handleAddTask"
          @task-moved-to-brain-dump="handleTaskMovedToBrainDump"
          @task-moved-between-columns="handleTaskMovedBetweenColumns"
          @reorder-tasks="handleTaskReordering" />
        <KanbanColumn
          :ref="el => columnRefs.today = el"
          title="Today"
          column-id="today"
          :date="dates.today"
          :allow-add-task="true"
          @toggle-completion="handleTaskCompletion"
          @add-task="handleAddTask"
          @task-moved-to-brain-dump="handleTaskMovedToBrainDump"
          @task-moved-between-columns="handleTaskMovedBetweenColumns"
          @reorder-tasks="handleTaskReordering" />
        <KanbanColumn
          :ref="el => columnRefs.tomorrow = el"
          title="Tomorrow"
          column-id="tomorrow"
          :date="dates.tomorrow"
          :allow-add-task="true"
          @toggle-completion="handleTaskCompletion"
          @add-task="handleAddTask"
          @task-moved-to-brain-dump="handleTaskMovedToBrainDump"
          @task-moved-between-columns="handleTaskMovedBetweenColumns"
          @reorder-tasks="handleTaskReordering" />
        <KanbanColumn
          :ref="el => columnRefs.nextWeek = el"
          title="Next Week"
          column-id="nextWeek"
          :date="dates.nextWeek"
          @toggle-completion="handleTaskCompletion"
          @add-task="handleAddTask"
          @task-moved-to-brain-dump="handleTaskMovedToBrainDump"
          @task-moved-between-columns="handleTaskMovedBetweenColumns"
          @reorder-tasks="handleTaskReordering" />
        <KanbanColumn
          :ref="el => columnRefs.afterNextWeek = el"
          title="After Next Week"
          column-id="afterNextWeek"
          :date="dates.afterNextWeek"
          @toggle-completion="handleTaskCompletion"
          @add-task="handleAddTask"
          @task-moved-to-brain-dump="handleTaskMovedToBrainDump"
          @task-moved-between-columns="handleTaskMovedBetweenColumns"
          @reorder-tasks="handleTaskReordering" />
        <KanbanColumn
          :ref="el => columnRefs.nextMonth = el"
          title="Next Month"
          column-id="nextMonth"
          :date="dates.nextMonth"
          @toggle-completion="handleTaskCompletion"
          @add-task="handleAddTask"
          @task-moved-to-brain-dump="handleTaskMovedToBrainDump"
          @task-moved-between-columns="handleTaskMovedBetweenColumns"
          @reorder-tasks="handleTaskReordering" />
      </div>
    </div>
  </div>
</template>

<style scoped>
.kanban-planner {
  display: flex;
  height: 100vh;
  overflow: hidden;
  position: relative;
  /* Add this to position the toggle wrapper */
}

/* Fixed Brain Dump sidebar */
.brain-dump-wrapper {
  position: sticky;
  top: 0;
  left: 0;
  height: 100vh;
  position: relative;
  /* Keep right shadow for depth */
  box-shadow: 4px 0 10px -3px rgba(0, 0, 0, 0.15);
  transition: width 0.3s ease;
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
  animation: bounce-right 1.5s infinite;
  opacity: 0.9;
}

/* Bouncing animation */
@keyframes bounce-right {

  0%,
  100% {
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
  min-width: min-content;
  /* Ensures columns don't shrink below their natural width */
}

.integration-sidebar-wrapper {
  position: absolute;
  top: 0;
  right: 0;
}

</style>

