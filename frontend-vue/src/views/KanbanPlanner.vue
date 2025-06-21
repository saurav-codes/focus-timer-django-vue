<script setup>
  import { onMounted, ref, useTemplateRef, onUnmounted } from 'vue'
  import BrainDump from '../components/BrainDump.vue'
  import KanbanColumn from '../components/KanbanColumn.vue'
  import IntegrationSidebar from '../components/sidebar/IntegrationSidebar.vue'
  import LoadingColumnsSkeleton from '../components/LoadingColumnsSkeleton.vue'
  import FilterSidebar from '../components/sidebar/FilterSidebar.vue'

  import { useTaskStoreWs } from '../stores/taskStoreWs'
  import { useUIStore } from '../stores/uiStore'

  const taskStore = useTaskStoreWs()

  // Ref for the scroll container
  const kanbanColumnsWrapper = useTemplateRef('kanbanColumnsWrapper')
  const uiStore = useUIStore()
  const hasScrolledRight = ref(false)
  const scrollThreshold = 100

  const hasHorizontalScrollbar = () =>
    kanbanColumnsWrapper.value
      ? kanbanColumnsWrapper.value.scrollWidth > kanbanColumnsWrapper.value.clientWidth
      : false

  // Simple native scroll handler
  const onScroll = async () => {
    const wrapper = kanbanColumnsWrapper.value
    if (!wrapper) return
    const { scrollLeft, scrollWidth, clientWidth } = wrapper

    // 1) Track right scroll to enable backward load
    if (scrollLeft > scrollThreshold) {
      hasScrolledRight.value = true
    }

    // 2) Backward load: at left edge after right scroll
    if (
      scrollLeft === 0 &&
      hasScrolledRight.value &&
      !uiStore.isLoadingEarlierColumns
    ) {
      hasScrolledRight.value = false
      uiStore.setLoadingEarlierColumns(true)
      try {
        taskStore.addEarlierColumnsWs(7)
      } catch (e) {
        console.error(e)
      } finally {
        uiStore.setLoadingEarlierColumns(false)
      }
    }

    // 3) Forward load: if near right edge or no scrollbar
    if (
      (scrollWidth - (scrollLeft + clientWidth) < scrollThreshold ||
        !hasHorizontalScrollbar()) &&
      !uiStore.isLoadingMoreColumns
    ) {
      uiStore.setLoadingMoreColumns(true)
      try {
        taskStore.addMoreColumnsWs(3)
      } catch (e) {
        console.error(e)
      } finally {
        uiStore.setLoadingMoreColumns(false)
      }
    }
  }


  onMounted(() => {
    taskStore.initWs()
    const wrapper = kanbanColumnsWrapper.value
    if (wrapper) {
      wrapper.scrollLeft = 0
      wrapper.addEventListener('scroll', onScroll)
    }
  })

  onUnmounted(() => {
    const wrapper = kanbanColumnsWrapper.value
    if (wrapper) {
      wrapper.removeEventListener('scroll', onScroll)
    }
    taskStore.closeWs()
  })
</script>

<template>
  <div ref="kanbanPlanner" class="kanban-planner">
    <div class="brain-dump-wrapper">
      <BrainDump />
    </div>

    <!-- Scrollable columns container -->
    <div ref="kanbanColumnsWrapper" class="kanban-columns-wrapper">
      <div class="kanban-columns">
        <!-- Loading skeleton for backward infinite scroll -->
        <LoadingColumnsSkeleton v-if="uiStore.isLoadingEarlierColumns" />
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

    <!-- Filter Sidebar (conditionally shown) -->
    <FilterSidebar />
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
