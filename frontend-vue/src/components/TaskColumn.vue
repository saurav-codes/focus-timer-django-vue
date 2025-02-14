<script setup>
import { computed, ref } from 'vue';
import draggable from 'vuedraggable';
import TaskItem from './TaskItem.vue';
import TaskEditModal from './TaskEditModal.vue';

const props = defineProps({
  date: {
    type: Date,
    required: true,
  },
  tasks: {
    type: Array,
    default: () => [],
  },
  columnIndex: {
    type: Number,
    required: true,
  },
});
const emit = defineEmits(['update-task', 'reorder-tasks-on-backend']);

// Use a computed property as a two-way binding proxy for tasks
const tasksProxy = computed({
  get() {
    return props.tasks;
  },
  set(newTasks) {
    // TODO: fix this mess as i dont understand how this ordering working
    console.log("emiting reorder-tasks event but we dont have any listener for this")
    emit('reorder-tasks-on-backend', newTasks);
  }
});

const onDragEnd = () => {
  // Recalculate the order property for each task
  tasksProxy.value.forEach((task, index) => {
    task.order = index;
  });
  // Emit the updated order
  console.log("user dragged a task so emiting reorder-tasks-on-backend")
  emit('reorder-tasks-on-backend', tasksProxy.value);
};

const formattedDate = computed(() =>
  new Intl.DateTimeFormat('en-US', {
    weekday: 'long',
    month: 'long',
    day: 'numeric',
  }).format(props.date)
);

const updateTask = (task, newStatus) => {
  emit('update-task', task, newStatus);
};

const selectedTaskToOpen = ref(null)

const openTaskEditModal = (task) => {
  selectedTaskToOpen.value = task;
}

const handleTaskUpdate = (updatedTask) => {
  // TODO: Update your task in the store or locally as needed
  // For example: taskStore.updateTaskStatus(updatedTask, updatedTask.status);
  console.log("selected task is emptied now but we also need to send req to back using store")
};

</script>

<template>
  <div class="task-column">
    <div class="column-header">
      <h2>{{ formattedDate }}</h2>
    </div>
    <div class="task-list">
      <draggable @end="onDragEnd" ghost-class="task-drop-shadow" v-model="tasksProxy" item-key="id">
        <template v-auto-animate #item="{ element: taskItem }">
          <TaskItem :task="taskItem" @click="openTaskEditModal(taskItem)" @update="updateTask(taskItem, $event)" />
        </template>
      </draggable>
      <!-- Render the modal if a task is selected -->
      <TaskEditModal
        v-if="selectedTaskToOpen"
        :task="selectedTaskToOpen"
        @close="selectedTaskToOpen = null"
        @update-task="handleTaskUpdate"
      />
    </div>
  </div>
</template>

<style scoped>
.task-column {
  flex: 1;
  min-width: 300px;
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  margin: 1rem;
  display: flex;
  flex-direction: column;
}
.column-header {
  padding: 1rem;
  background-color: #f7f8fa;
  border-bottom: 1px solid #e1e4e8;
  text-align: center;
}
.column-header h2 {
  margin: 0;
  font-size: 1.2rem;
  font-weight: 600;
  color: #333;
}
.task-list {
  flex: 1;
  padding: 1rem;
  background-color: #fafbfc;
  overflow-y: auto;
}
.task-drop-shadow {
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.3);
}
</style>
