<script setup>
import { onMounted, useTemplateRef, watch, onUnmounted } from 'vue';
import BrainDump from '../components/BrainDump.vue';
import KanbanColumn from '../components/KanbanColumn.vue';
import IntegrationSidebar from '../components/sidebar/IntegrationSidebar.vue';
import { useScroll, usePointer, useMouseInElement, useWindowSize, useRafFn } from '@vueuse/core';

import { useTaskStore } from '../stores/taskstore';

const taskStore = useTaskStore();

// need this reference to scroll the kanban columns wrapper when the page loads
const kanbanColumnsWrapper = useTemplateRef('kanbanColumnsWrapper');
const scroll_data = useScroll(kanbanColumnsWrapper, {behavior: 'smooth'});

const { x: mouse_x} = useMouseInElement(kanbanColumnsWrapper)
const {pressure:mouse_pressure} = usePointer()
const { width: window_width } = useWindowSize()

function _mouse_near_right_edge() {
  const right_edge = window_width.value - 150;
  return mouse_x.value > right_edge;
}

function _mouse_near_left_edge() {
  const left_edge = 400;
  return mouse_x.value < left_edge;
}

function _should_scroll_right() {
  return _mouse_near_right_edge() && mouse_pressure.value >= 0.5;
}

function _should_scroll_left() {
  return _mouse_near_left_edge() && mouse_pressure.value >= 0.5;
}

// Setup your conditions
const { pause, resume } = useRafFn(() => {
  if (_should_scroll_right()) {
    scroll_data.x.value += 500;
  } else if (_should_scroll_left()) {
    scroll_data.x.value -= 500;
  }
})

// Start/stop based on mouse position
watch([mouse_x, mouse_pressure], () => {
  if (_should_scroll_right() || _should_scroll_left()) {
    resume()
  } else {
    pause()
  }
})

// Clean up
onUnmounted(() => {
  pause()
})

const animateScroll = () => {
  // scroll to right by 500
  scroll_data.x.value = 500;
  setTimeout(() => {
    scroll_data.x.value = 0;
  }, 1000);
}

// Run animation when component mounts and hide the indicator after animation
onMounted(() => {
  // Small delay to ensure content is rendered
  setTimeout(() => {
    animateScroll();
  }, 100);

  // Fetch tasks when component mounts
  taskStore.fetchTasks();
});

</script>

<template>
  <div ref="kanbanPlanner" class="kanban-planner">
    <div class="brain-dump-wrapper">
      <BrainDump />

    </div>

    <!-- Scrollable columns container -->
    <div ref="kanbanColumnsWrapper" class="kanban-columns-wrapper">
      <div class="kanban-columns">
        <div v-for="column in taskStore.kanbanColumns" :key="column.title">
          <KanbanColumn
            :date-string="column.dateString"
            :title="column.title"
            :tasks="column.tasks" />
        </div>
      </div>
    </div>

    <!-- Integration Sidebar (conditionally shown) -->
    <IntegrationSidebar class="integration-sidebar-wrapper" />
  </div>
</template>

<style scoped>
.kanban-planner {
  display: flex;
  height: 100vh;
  overflow: hidden;
  position: relative;
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

