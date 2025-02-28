<script setup>
import { ref, computed } from 'vue';
import { BadgeCheck, Plus } from 'lucide-vue-next';
import TaskCard from '@/components/TaskCard.vue';

const props = defineProps({
  date: {
    type: String,
    required: true
  },
  title: {
    type: String,
    required: true
  },
  tasks: {
    type: Array,
    default: () => []
  },
  allowAddTask: {
    type: Boolean,
    default: false
  },
  columnWidth: {
    type: String,
    default: '300px'
  }
});

const emit = defineEmits(['toggle-completion', 'add-task']);

const localTasks = ref(props.tasks.length ? props.tasks : [
  {
    id: 1,
    title: 'Design system implementation',
    completed: false,
    duration: '2:00',
    tag: { name: 'Design', color: 'purple' }
  },
  {
    id: 2,
    title: 'API Integration for tasks',
    completed: false,
    duration: '3:00',
    tag: { name: 'Development', color: 'blue' }
  }
]);

const newTaskTitle = ref('');
const isAddingTask = ref(false);

const completedTasksCount = computed(() => {
  return localTasks.value.filter(task => task.completed).length;
});

const toggleTaskCompletion = (taskId) => {
  const task = localTasks.value.find(t => t.id === taskId);
  if (task) {
    task.completed = !task.completed;
    emit('toggle-completion', { taskId, completed: task.completed });
  }
};

const startAddingTask = () => {
  isAddingTask.value = true;
  setTimeout(() => {
    document.getElementById(`new-task-input-${props.title}`)?.focus();
  }, 0);
};

const addTask = () => {
  if (newTaskTitle.value.trim()) {
    const newTask = {
      id: Date.now(),
      title: newTaskTitle.value,
      completed: false,
      duration: '0:30',
      tag: null
    };

    localTasks.value.push(newTask);
    emit('add-task', newTask);
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
</script>

<template>
  <div class="kanban-column" :style="{ width: columnWidth }">
    <div class="column-header">
      <div class="title-section">
        <h3>{{ title }}</h3>
        <span class="date">{{ date }}</span>
      </div>
      <div class="stats">
        <BadgeCheck class="small-icon" size="14" />
        <span>{{ completedTasksCount }} / {{ localTasks.length }}</span>
      </div>
    </div>

    <div v-if="allowAddTask && !isAddingTask" class="add-task" @click="startAddingTask">
      <Plus size="16" class="plus-icon" />
      <span>Add a task</span>
    </div>

    <div v-if="allowAddTask && isAddingTask" class="new-task-input">
      <input
        :id="`new-task-input-${title}`"
        v-model="newTaskTitle"
        placeholder="What needs to be done?"
        @keydown="handleKeyDown"
        @blur="cancelAddTask">
    </div>

    <div class="tasks-container">
      <TaskCard
        v-for="task in localTasks"
        :key="task.id"
        :task="task"
        @toggle-completion="toggleTaskCompletion" />
    </div>
  </div>
</template>

<style scoped>
.kanban-column {
  background-color: var(--color-background);
  border: 1px solid var(--color-border);
  border-radius: 0.5rem;
  width: 300px;
  min-height: 400px;
  display: flex;
  flex-direction: column;
  padding: 1rem;
}

.column-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid var(--color-border);
}

.title-section {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.title-section h3 {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin: 0;
}

.date {
  font-size: var(--font-size-xs);
  color: var(--color-text-tertiary);
}

.stats {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-size: var(--font-size-xs);
  color: var(--color-text-tertiary);
}

.small-icon {
  color: var(--color-text-tertiary);
}

.tasks-container {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  flex-grow: 1;
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
  width: 100%;
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
