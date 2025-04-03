<script setup>
import { onMounted, ref, useTemplateRef, watch } from 'vue';
import { ChevronRight } from 'lucide-vue-next';
import BrainDump from '../components/BrainDump.vue';
import KanbanColumn from '../components/KanbanColumn.vue';
import IntegrationSidebar from '../components/sidebar/IntegrationSidebar.vue';
import { useScroll, usePointer, useMouseInElement, useWindowSize } from '@vueuse/core';

import { useTaskStore } from '../stores/taskstore';

// Add state for controlling the scroll indicator visibility
const showScrollIndicator = ref(true);
const taskStore = useTaskStore();

// need this reference to scroll the kanban columns wrapper when the page loads
const kanbanColumnsWrapper = useTemplateRef('kanbanColumnsWrapper');
const scroll_data = useScroll(kanbanColumnsWrapper, {behavior: 'smooth'});

// const { x: mouse_x, pressure:mouse_pressure } = usePointer()
const { x: mouse_x} = useMouseInElement(kanbanColumnsWrapper)
const {pressure:mouse_pressure} = usePointer()
const { width: window_width } = useWindowSize()

function _scroll_threshold() {
  // mouse x/total window width x 100
  const scrolled_percent = (mouse_x/window_width)*100
    if (scrolled_percent > 5) {
      return _mouse_near_left_edge() ? 600 : 200
    } else if (scrolled_percent >10) {
      return _mouse_near_left_edge() ? 500 : 400
    } else if (scrolled_percent > 20 ) {
      return _mouse_near_left_edge() ? 400 : 500
    } else if ( scrolled_percent > 30 ) {
      return _mouse_near_left_edge() ? 300 : 600
    } else {
      return 200
    }
}

function _mouse_near_right_edge() {
  const right_edge = window_width.value - 100;
  return mouse_x.value > right_edge;
}

function _mouse_near_left_edge() {
  const left_edge = 100;
  return mouse_x.value < left_edge;
}

function _should_scroll_right() {
  return _mouse_near_right_edge() && mouse_pressure.value >= 0.5;
}

function _should_scroll_left() {
  return _mouse_near_left_edge() && mouse_pressure.value >= 0.5;
}

watch(mouse_x, (new_mouse_x) => {
  if (_should_scroll_right()) {
    scroll_data.x.value += _scroll_threshold();
  }
  if (_should_scroll_left()) {
    scroll_data.x.value -= _scroll_threshold();
  }
});

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

    // Hide the indicator after the animation completes
    setTimeout(() => {
      showScrollIndicator.value = false;
    }, 2000); // Hide after 2 seconds (animation + a bit more time)
  }, 100);

  // Fetch tasks when component mounts
  taskStore.fetchTasks();
});

</script>

<template>
  <div ref="kanbanPlanner" class="kanban-planner">
    <div class="brain-dump-wrapper">
      <BrainDump />
      <!-- Scroll indicator -->
      <div v-if="showScrollIndicator" class="scroll-indicator">
        <ChevronRight size="24" />
      </div>
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

