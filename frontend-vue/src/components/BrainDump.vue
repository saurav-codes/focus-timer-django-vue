<script setup>
  import { ref, computed, onMounted, onUnmounted } from 'vue'
  import { Plus, BrainCircuitIcon, BadgeCheck, ChevronLeft, ChevronRight, Filter, Keyboard } from 'lucide-vue-next'
  import TaskCard from './TaskCard.vue'
  import { useUIStore } from '../stores/uiStore'
  import { useTaskStoreWs } from '../stores/taskStoreWs'
  import TaskCreationPopup from './TaskCreationPopup.vue'
  import Popper from 'vue3-popper'
  import Draggable from 'vuedraggable'

  const uiStore = useUIStore()
  const taskStore = useTaskStoreWs()

  // Add state for controlling the scroll indicator visibility
  const showScrollIndicator = ref(true)
  const showTaskCreationPopup = ref(false)
  const showPopper = ref(false)

  const openTaskCreationPopup = () => {
    showTaskCreationPopup.value = true
  }

  const closeTaskCreationPopup = () => {
    showTaskCreationPopup.value = false
  }

  // Add event listener for keyboard shortcuts
  const handleKeyPress = (event) => {
    // Only trigger if 'a' is pressed and no input/textarea is focused
    if (
      event.key === 'a' &&
      !['INPUT', 'TEXTAREA'].includes(document.activeElement.tagName) &&
      !document.activeElement.isContentEditable
    ) {
      event.preventDefault() // Prevent 'a' from being typed
      openTaskCreationPopup()
    }
  }

  onMounted(() => {
    // Add event listener for keyboard shortcuts
    document.addEventListener('keydown', handleKeyPress)

    // Hide the indicator after the animation completes
    setTimeout(() => {
      showScrollIndicator.value = false
    }, 2000) // Hide after 2 seconds (animation + a bit more time)
  })

  onUnmounted(() => {
    document.removeEventListener('keydown', handleKeyPress)
  })

  const completed_tasks_vs_total_tasks = computed(() => {
    const completedTasks = taskStore.brainDumpTasks.filter((task) => task.is_completed).length
    const totalTasks = taskStore.brainDumpTasks.length
    return `${completedTasks} / ${totalTasks}`
  })

  // Use the store's computed property and toggle function
  const isCollapsed = computed(() => uiStore.isBrainDumpCollapsed)
  const toggleBrainDump = () => uiStore.toggleBrainDump()

  async function handleTaskDeleted(taskId) {
    // remove task from braindumpTasks because we already handling the DB update in the store
    taskStore.brainDumpTasks = taskStore.brainDumpTasks.filter((task) => task.id !== taskId)
  }

  function handleTaskUpdated(updatedTask) {
    // update the task in the store
    taskStore.brainDumpTasks = taskStore.brainDumpTasks.map((task) => (task.id === updatedTask.id ? updatedTask : task))
  }

  function handleTaskArchived(taskId) {
    taskStore.brainDumpTasks = taskStore.brainDumpTasks.filter((task) => task.id !== taskId)
  }

  async function handleTaskDroppedToBrainDump({ added, moved }) {
    if (uiStore.isPointerOverIntegration) {
      return
    }
    // Handle when a task is added to this column
    if (added) {
      const element = added.element
      console.log('task added. to braindump')
      console.log('added element', element)
      await taskStore.braindumpTaskWs(element)
      await taskStore.updateTaskOrderWs(taskStore.brainDumpTasks)
    }

    // Handle when a task is moved within the same column
    if (moved) {
      // Just update the order since the task is staying in the same column
      console.log('task moved. so updating task order')
      await taskStore.updateTaskOrder(taskStore.brainDumpTasks)
    }

    // We don't need to handle removed here as the source column will handle it
  }

  async function handleTagRemoved(updated_tags_list, taskId) {
    // remove the tag from the task
    const task = taskStore.brainDumpTasks.find((task) => task.id === taskId)
    if (!task) {
      console.error('Task not found while removing tags for task', taskId)
      return
    }
    task.tags = updated_tags_list
    await taskStore.updateTaskWs(task)
  }
</script>

<template>
  <TaskCreationPopup :is-visible="showTaskCreationPopup" @close="closeTaskCreationPopup" />

  <!-- Brain Dump toggle button in a box -->
  <div class="brain-dump-toggle-btn-wrapper" @click="toggleBrainDump">
    <button class="brain-dump-toggle-btn" :title="isCollapsed ? 'Expand' : 'Collapse'">
      <component :is="isCollapsed ? ChevronRight : ChevronLeft" size="18" />
    </button>
  </div>

  <!-- Scroll indicator -->
  <div v-if="showScrollIndicator" class="scroll-indicator" @click="toggleBrainDump">
    <ChevronRight v-if="isCollapsed" size="24" />
    <ChevronLeft v-else size="24" />
  </div>

  <div class="brain-dump-container" :class="{ collapsed: isCollapsed }">
    <div class="header">
      <div class="header-top">
        <h2 class="title">
          <span class="icon">
            <BrainCircuitIcon size="18" />
          </span>
          Brain Dump
        </h2>
        <!-- Update the filter toggle button -->
        <Popper arrow content="Filter Tasks based on tags and projects" :show="showPopper">
          <button
            class="filter-toggle-btn"
            title="Filter tasks"
            @mouseenter="showPopper = true"
            @mouseleave="showPopper = false"
            @click.stop="uiStore.toggleFilterSidebar">
            <Filter size="16" />
          </button>
        </Popper>
      </div>
      <div class="total-task">
        <BadgeCheck class="small-icon" size="14" />
        <span>{{ completed_tasks_vs_total_tasks }}</span>
      </div>
    </div>

    <!-- New task creation button with keyboard shortcut hint -->
    <div class="add-task-container" @click="openTaskCreationPopup">
      <div class="add-task">
        <Plus size="16" class="plus-icon" />
        <span>Add a task</span>
      </div>
      <div class="keyboard-shortcut-hint">
        <Keyboard size="14" class="keyboard-icon" />
        <span>Press <span class="key-hint">a</span></span>
      </div>
    </div>

    <Draggable
      v-model="taskStore.brainDumpTasks"
      class="tasks-list"
      drag-class="dragging"
      ghost-class="ghost-card"
      group="kanban-group"
      :force-fallback="true"
      item-key="id"
      @change="handleTaskDroppedToBrainDump">
      <template #item="{ element }">
        <TaskCard
          :task="element"
          @tag-removed="handleTagRemoved"
          @task-deleted="handleTaskDeleted"
          @task-archived="handleTaskArchived"
          @task-updated="handleTaskUpdated" />
      </template>
    </Draggable>
  </div>
</template>

<style scoped>
  .brain-dump-container {
    background-color: var(--color-background);
    border-right: 1px solid var(--color-border);
    height: 92vh;
    width: 280px;
    position: sticky;
    top: 0;
    left: 0;
    display: flex;
    flex-direction: column;
    box-shadow: var(--shadow-sm);
    overflow-y: auto;
    padding: 1rem;
    transition: width 0.1s ease-in-out;
  }

  .brain-dump-container.collapsed {
    width: 0.1rem;
    overflow: visible;
  }

  .brain-dump-container.collapsed .title,
  .brain-dump-container.collapsed .total-task,
  .brain-dump-container.collapsed .add-task-container,
  .brain-dump-container.collapsed .tasks-list {
    display: none;
  }

  .header {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    margin-bottom: 1rem;
    padding-bottom: 0.75rem;
    border-bottom: 1px solid var(--color-border);
    position: relative;
  }

  .brain-dump-toggle-btn-wrapper {
    position: absolute;
    top: 50%;
    right: -1.2rem;
    background-color: var(--color-background-secondary, #1e1e2e);
    border-radius: 50px;
    width: 2rem;
    height: 2rem;
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 2;
  }

  .brain-dump-toggle-btn {
    background: transparent;
    border: none;
    color: var(--color-text-tertiary);
    cursor: pointer;
    width: 28px;
    height: 28px;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: border 1s ease-in-out;
  }

  .brain-dump-toggle-btn:hover {
    background-color: var(--color-background-secondary);
    color: var(--color-text);
    border: 1px solid var(--color-border, #313244);
    border-radius: 50%;
  }

  .title {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: var(--font-size-lg);
    font-weight: var(--font-weight-semibold);
    color: var(--color-text-primary);
    margin: 0;
  }

  .icon {
    font-size: 1.25rem;
  }

  .total-task {
    display: flex;
    align-items: center;
    gap: 0.25rem;
    font-size: var(--font-size-xs);
    color: var(--color-text-tertiary);
  }

  .small-icon {
    color: var(--color-text-tertiary);
  }

  /* Add task container for button and shortcut hint */
  .add-task-container {
    display: flex;
    flex-direction: column;
    margin-bottom: 1rem;
    cursor: pointer;
  }

  .add-task {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.75rem;
    border-radius: 0.375rem 0.375rem 0 0;
    background-color: var(--color-background-secondary);
    color: var(--color-text-tertiary);
    transition: background-color var(--transition-base);
    font-size: var(--font-size-sm);
  }

  .keyboard-shortcut-hint {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem 0.75rem;
    border-radius: 0 0 0.375rem 0.375rem;
    background-color: var(--color-background-tertiary);
    color: var(--color-text-tertiary);
    font-size: var(--font-size-xs);
    border-top: 1px solid var(--color-border);
  }

  .keyboard-icon {
    color: var(--color-text-tertiary);
  }

  .key-hint {
    display: inline-block;
    padding: 0 4px;
    margin: 0 2px;
    background-color: var(--color-background-secondary);
    border-radius: 3px;
    font-family: monospace;
    font-weight: bold;
    border: 1px solid var(--color-border);
  }

  /* Scroll indicator styling */
  .scroll-indicator {
    position: absolute;
    right: -1.1rem;
    top: 52.5%;
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
    z-index: 3;
    cursor: pointer;
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

  .add-task-container:hover .add-task {
    background-color: var(--color-background-tertiary);
    color: var(--color-text-secondary);
  }

  .plus-icon {
    color: var(--color-text-tertiary);
  }

  .filter-toggle-btn {
    background-color: var(--color-background-secondary);
    border: none;
    border-radius: 4px;
    cursor: pointer;
    color: var(--color-text-tertiary);
    padding: 0.5rem;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.2s;
  }

  .filter-toggle-btn:hover {
    background-color: var(--color-background-tertiary);
    color: var(--color-text-secondary);
  }

  .header-top {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.25rem;
  }
</style>
