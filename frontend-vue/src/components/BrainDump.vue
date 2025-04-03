<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { Plus, BrainCircuitIcon, BadgeCheck, ChevronLeft, ChevronRight } from 'lucide-vue-next';
import TaskCard from './TaskCard.vue';
import { useUIStore } from '../stores/uiStore';
import { useTaskStore } from '../stores/taskstore';
import { SlickList, SlickItem } from 'vue-slicksort';

const uiStore = useUIStore();
const taskStore = useTaskStore();

// Add state for controlling the scroll indicator visibility
const showScrollIndicator = ref(true);
const newTaskTitle = ref('');
const isAddingTask = ref(false);

const startAddingTask = () => {
  /* add a new empty task card and focus on it's input box */
  isAddingTask.value = true;
  // Focus the input after the DOM updates
  setTimeout(() => {
    document.getElementById('new-task-input')?.focus();
  }, 0);
};

const addTask = async () => {
  if (newTaskTitle.value.trim()) {
    // make an object and send this values to backend
    const newTask = {
      id: Date.now(),
      title: newTaskTitle.value,
      completed: false,
      duration: '0:30',
      is_in_brain_dump: true,
    };
    // add the new task to the top of the list
    taskStore.brainDumpTasks.unshift(newTask);
    newTaskTitle.value = '';
    const data = await taskStore.createTask(newTask);
    // since we are doing optimistic update, we need to update the id of the task
    taskStore.brainDumpTasks[0].id = data.id;
  }
};

const cancelAddTask = () => {
  newTaskTitle.value = '';
  isAddingTask.value = false;
};

const handleKeyDown = (event) => {
  if (event.key === 'Enter') {
    addTask();
  } else if (event.key === 'Escape') {
    cancelAddTask();
  }
};

// Add event listener for keyboard shortcuts
const handleKeyPress = (event) => {
  // Only trigger if 'a' is pressed and no input/textarea is focused
  if (
    event.key === 'a' &&
    !['INPUT', 'TEXTAREA'].includes(document.activeElement.tagName) &&
    !document.activeElement.isContentEditable
  ) {
    event.preventDefault(); // Prevent 'a' from being typed
    startAddingTask();
  }
};

onMounted(() => {
  // Add event listener for keyboard shortcuts
  document.addEventListener('keydown', handleKeyPress);

  // Hide the indicator after the animation completes
  setTimeout(() => {
    showScrollIndicator.value = false;
  }, 2000); // Hide after 2 seconds (animation + a bit more time)
});

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeyPress);
});

const completed_tasks_vs_total_tasks = computed(() => {
  const completedTasks = taskStore.brainDumpTasks.filter(task => task.is_completed).length;
  const totalTasks = taskStore.brainDumpTasks.length;
  return `${completedTasks} / ${totalTasks}`;
});

// Use the store's computed property and toggle function
const isCollapsed = computed(() => uiStore.isBrainDumpCollapsed);
const toggleBrainDump = () => uiStore.toggleBrainDump();

</script>

<template>
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
  <div class="brain-dump-container" :class="{ 'collapsed': isCollapsed }">
    <div class="header">
      <h2 class="title">
        <span class="icon">
          <BrainCircuitIcon size="18" />
        </span>
        Brain Dump
      </h2>
      <div class="total-task">
        <BadgeCheck class="small-icon" size="14" />
        <span>{{ completed_tasks_vs_total_tasks }}</span>
      </div>
    </div>

    <div v-if="!isAddingTask" class="add-task" @click="startAddingTask">
      <Plus size="16" class="plus-icon" />
      <span>Add a task</span>
    </div>

    <div v-else class="new-task-input">
      <input id="new-task-input" v-model="newTaskTitle" placeholder="What needs to be done?" @keydown="handleKeyDown"
        @blur="cancelAddTask">
    </div>

    <SlickList v-model:list="taskStore.brainDumpTasks" :distance="5" group="brain-dump-group" class="tasks-list"
      :accept="['kanban-group']" @sort-insert="taskStore.taskDroppedToBrainDump"
      @update:list="taskStore.updateTasksOrder">
      <SlickItem v-for="(task, idx) in taskStore.brainDumpTasks" :key="task.id" :index="idx" :item="task">
        <TaskCard :task="task" />
      </SlickItem>
    </SlickList>
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
.brain-dump-container.collapsed .add-task,
.brain-dump-container.collapsed .tasks-list,
.brain-dump-container.collapsed .new-task-input {
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

.add-task {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem;
  border-radius: 0.375rem;
  background-color: var(--color-background-secondary);
  color: var(--color-text-tertiary);
  cursor: pointer;
  transition: background-color var(--transition-base);
  margin-bottom: 1rem;
  font-size: var(--font-size-sm);
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

.add-task:hover {
  background-color: var(--color-background-tertiary);
  color: var(--color-text-secondary);
}

.plus-icon {
  color: var(--color-text-tertiary);
}

.new-task-input {
  margin-bottom: 1rem;
}

.new-task-input input {
  width: 91%;
  padding: 0.75rem;
  border-radius: 0.375rem;
  border: 1px solid var(--color-border);
  background-color: var(--color-input-background);
  color: var(--color-text-primary);
  font-size: var(--font-size-sm);
  outline: none;
  transition: border-color var(--transition-base);
}

.new-task-input input:focus {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 2px var(--color-primary-light);
}
</style>
