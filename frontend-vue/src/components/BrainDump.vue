<script setup>
import { ref, computed } from 'vue';
import { Plus, BrainCircuitIcon, BadgeCheck, ChevronLeft, ChevronRight } from 'lucide-vue-next';
import TaskCard from '@/components/TaskCard.vue';
import { useUIStore } from '@/stores/uiStore';
import { SlickList, SlickItem } from 'vue-slicksort';
// Use the UI store instead of local state
const uiStore = useUIStore();

const tasks = ref([
  {
    id: 1,
    title: 'Q3 Goal Planning',
    completed: false,
    duration: '1:00',
    tag: { name: 'Admin', color: 'purple' }
  },
  {
    id: 2,
    title: 'Invoice Creation - Mobile optimization',
    completed: false,
    duration: '2:00',
    tag: { name: 'AloaPay', color: 'blue' }
  },
  {
    id: 3,
    title: 'Invoice Updating - Mobile Optimization',
    completed: false,
    duration: '1:30',
    tag: { name: 'AloaPay', color: 'blue' }
  }
]);

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

const addTask = () => {
  if (newTaskTitle.value.trim()) {
    // make an object and send this values to backend
    tasks.value.push({
      id: Date.now(),
      title: newTaskTitle.value,
      completed: false,
      duration: '0:30',
      tag: null
    });
    newTaskTitle.value = '';
  }
  isAddingTask.value = false;
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

const toggleTaskCompletion = (taskId) => {
  const task = tasks.value.find(t => t.id === taskId);
  if (task) {
    task.completed = !task.completed;
  }
};

const completed_tasks_vs_total_tasks = computed(() => {
  const completedTasks = tasks.value.filter(task => task.completed).length;
  const totalTasks = tasks.value.length;
  return `${completedTasks} / ${totalTasks}`;
});

// Use the store's computed property and toggle function
const isCollapsed = computed(() => uiStore.isBrainDumpCollapsed);
const toggleBrainDump = () => uiStore.toggleBrainDump();

// Emit events for task movement
const emit = defineEmits(['task-moved-to-column', 'task-added-from-column', 'reorder-tasks']);

// Handle task being added from a column
const addTaskFromColumn = (task) => {
  tasks.value.push(task);
};

// Expose the method for parent components to call
defineExpose({
  addTaskFromColumn
});

</script>

<template>
  <div class="brain-dump-container" :class="{ 'collapsed': isCollapsed }">
    <!-- Brain Dump toggle button in a box -->
    <div class="brain-dump-toggle-btn-wrapper" @click="toggleBrainDump">
      <button class="brain-dump-toggle-btn" :title="isCollapsed ? 'Expand' : 'Collapse'">
        <component :is="isCollapsed ? ChevronRight : ChevronLeft" size="18" />
      </button>
    </div>

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
      <input
        id="new-task-input"
        v-model="newTaskTitle"
        placeholder="What needs to be done?"
        @keydown="handleKeyDown"
        @blur="cancelAddTask">
    </div>

    <SlickList v-model:list="tasks" group="kanban-group">
      <div class="tasks-list">
        <SlickItem v-for="(task, idx) in tasks" :key="task.id" :index="idx" :item="task">
          <TaskCard :task="task" @toggle-completion="toggleTaskCompletion" />
        </SlickItem>
      </div>
    </SlickList>
  </div>
</template>

<style scoped>
.brain-dump-container {
  background-color: var(--color-background);
  border-right: 1px solid var(--color-border);
  height: 100vh;
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

.tasks-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
</style>
