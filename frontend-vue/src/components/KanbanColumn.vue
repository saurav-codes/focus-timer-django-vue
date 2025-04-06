<script setup>
import { computed, ref, watch } from 'vue';
import { BadgeCheck } from 'lucide-vue-next';
import TaskCard from './TaskCard.vue';
import { SlickList, SlickItem } from 'vue-slicksort';
import { useTaskStore } from '../stores/taskstore';

const taskStore = useTaskStore();

const props = defineProps({
  dateString: {
    type: String,
    required: true
  },
  dateObj: {
    type: Date,
    required:true
  },
  title: {
    type: String,
    required: true
  },
  tasks: {
    type: Array,
    default: () => []
  },
  columnWidth: {
    type: String,
    default: '300px'
  },
});

// Initialize with empty array
const localTasks = ref([]);

// Watch for changes to props.tasks and update localTasks
watch(() => props.tasks, (newTasks) => {
  // Create a deep copy of the tasks to avoid reference issues
  localTasks.value = JSON.parse(JSON.stringify(newTasks));
}, { immediate: true }); // immediate: true makes it run on component mount

const completedTasksCount = computed(() => {
  return localTasks.value.filter(task => task.is_completed).length;
});

function handleTaskDroppedToKanban ( { value }) {
  // This function is called when a task is dropped into the kanban column
  // TODO: extract the time of task from `value` and set it to the task
  // but use the date from the kanban column props
  value.start_at = props.dateObj.toISOString()
  value.end_at = props.dateObj.toISOString()
  value.is_in_brain_dump = false
  console.log("task value before update", value)
  // we also need to reorder the task since order is changed after dropping
  taskStore.updateTask(value);
}

function handleTaskOrderUpdate (new_tasks_array) {
  // Update the order of the tasks in the store
  setTimeout(() => {
    taskStore.updateTaskOrder(new_tasks_array);
  }, 2000);  // 2 second delay is just to make sure that task update operation is done
}

</script>

<template>
  <div class="kanban-column" :style="{ width: columnWidth }">
    <div class="column-header">
      <div class="title-section">
        <h3>{{ title }}</h3>
        <span class="date">{{ dateString }}</span>
      </div>
      <div class="stats">
        <BadgeCheck class="small-icon" size="14" />
        <span>{{ completedTasksCount }} / {{ localTasks.length }}</span>
      </div>
    </div>
    <div class="tasks-container">
      <SlickList
        v-model:list="localTasks"
        :distance="5"
        class="tasks-list"
        group="kanban-group"
        :accept="['brain-dump-group']"
        @sort-insert="handleTaskDroppedToKanban"
        @update:list="handleTaskOrderUpdate">
        <SlickItem v-for="(task, idx) in localTasks" :key="task.id" :index="idx" :item="task">
          <TaskCard :task="task" />
        </SlickItem>
      </SlickList>
    </div>
  </div>
</template>

<style scoped>
.kanban-column {
  background-color: var(--color-background);
  border: 1px solid var(--color-border);
  border-radius: 0.5rem;
  width: 300px;
  min-height: 90vh;
  height: 90vh;
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
  height: 100%;
  overflow-y: scroll;
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
