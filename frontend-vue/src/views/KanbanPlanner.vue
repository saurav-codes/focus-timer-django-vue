<script setup>
import { onMounted, useTemplateRef, watch, onUnmounted, ref } from 'vue';
import BrainDump from '../components/BrainDump.vue';
import KanbanColumn from '../components/KanbanColumn.vue';
import IntegrationSidebar from '../components/sidebar/IntegrationSidebar.vue';
import LoadingColumnsSkeleton from '../components/LoadingColumnsSkeleton.vue';
import { useScroll, usePointer, useMouseInElement, useWindowSize, useRafFn } from '@vueuse/core';

import { useTaskStore } from '../stores/taskstore';
import { useUIStore } from '../stores/uiStore';

const taskStore = useTaskStore();
const uiStore = useUIStore();

// need this reference to scroll the kanban columns wrapper when the page loads
const kanbanColumnsWrapper = useTemplateRef('kanbanColumnsWrapper');
const scroll_data = useScroll(kanbanColumnsWrapper, {behavior: 'smooth'});

const { x: mouse_x} = useMouseInElement(kanbanColumnsWrapper)
const {pressure:mouse_pressure} = usePointer()
const { width: window_width } = useWindowSize()

// Track if we're near the right edge to load more columns
const isNearRightEdge = ref(false);

function _should_scroll_right() {
  const right_edge = window_width.value - 150;
  const _mouse_near_right_edge = mouse_x.value > right_edge;
  return _mouse_near_right_edge && mouse_pressure.value >= 0.5;
}

// Setup scroll conditions
const { pause, resume } = useRafFn(() => {
  if (_should_scroll_right()) {
    scroll_data.x.value += 500;
  }
});

// Load more columns when near right edge
const checkScrollPosition = async () => {
  if (!kanbanColumnsWrapper.value) return;

  // Calculate if we're near the right edge
  const { scrollLeft, scrollWidth, clientWidth } = kanbanColumnsWrapper.value;
  const scrollThreshold = 300; // Pixel threshold before the end to trigger loading more columns

  if (scrollWidth - (scrollLeft + clientWidth) < scrollThreshold) {
    // We're near the right edge, load more columns if not already loading
    if (!isNearRightEdge.value && !uiStore.isLoadingMoreColumns) {
      isNearRightEdge.value = true;
      uiStore.setLoadingMoreColumns(true);

      try {
        // Wait for the columns to be added and tasks to be fetched
        await taskStore.addMoreColumns(3);
      } catch (error) {
        console.error('Error loading more columns:', error);
      } finally {
        // Always reset loading state after completion (success or error)
        uiStore.setLoadingMoreColumns(false);
        isNearRightEdge.value = false;
      }
    }
  }
};

// Start/stop based on mouse position
watch([mouse_x, mouse_pressure], () => {
  if (_should_scroll_right()) {
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
    scroll_data.x.value = 310;
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

  // Add scroll event listener to detect end of scroll for infinite loading
  if (kanbanColumnsWrapper.value) {
    kanbanColumnsWrapper.value.addEventListener('scroll', checkScrollPosition);
  }
});

// Clean up event listener when component is unmounted
onUnmounted(() => {
  if (kanbanColumnsWrapper.value) {
    kanbanColumnsWrapper.value.removeEventListener('scroll', checkScrollPosition);
  }
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
        <div v-for="column in taskStore.kanbanColumns" :key="column.title + column.dateString">
          <KanbanColumn
            :date-string="column.dateString"
            :title="column.title"
            :date-obj="column.date"
            :tasks="column.tasks" />
        </div>

        <!-- Loading skeleton to show when loading more columns -->
        <LoadingColumnsSkeleton v-if="uiStore.isLoadingMoreColumns" />
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

