<script setup>
import { useTaskForm } from '@/composables/taskform';
const props = defineProps({
  task: {
    type: Object,
    required: true
  }
});
const emit = defineEmits(['close', 'update-task']);

function handleTaskUpdate(updatedValues) {
  console.log("emiting task update from taskeditmodal")
  emit('update-task', { ...props.task, ...updatedValues });
}

// Pass a callback that emits the update event
const { form } = useTaskForm(props.task, handleTaskUpdate);
</script>

<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-content">
      <input
        type="text"
        v-model="form.title"
        placeholder="Task Title"
      />
      <textarea
        v-model="form.description"
        placeholder="Task Description"
      ></textarea>
      <select v-model="form.status">
        <option value="todo">To Do</option>
        <option value="in_progress">In Progress</option>
        <option value="done">Done</option>
      </select>
    </div>
  </div>
</template>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
}
.modal-content {
  background: #fff;
  padding: 20px;
  border-radius: 8px;
  width: 300px;
}
</style>
