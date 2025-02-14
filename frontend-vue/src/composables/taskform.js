// composables/useTaskForm.js
import { ref, watch } from 'vue';

// Function to handle changes and submission
// Pass 'original' and 'emitUpdate' as additional parameters
function handleTaskFormChange(newVal, original, emitUpdate) {
  if (
    newVal.title !== original.value.title ||
    newVal.description !== original.value.description ||
    newVal.status !== original.value.status
  ) {
    // Auto-submit updates
    emitUpdate(newVal);
    // Update original values after successful update
    original.value = { ...newVal };
  }
}

export function useTaskForm(task, emitUpdate) {
  // Clone the task to be used as initial state
  const taskForm = ref({
    title: task.title,
    description: task.description,
    status: task.status,
  });

  // Keep a copy of the original values
  const original = ref({ ...taskForm.value });

  // Watch form changes and auto-submit only if there's a modification
  // Use an inline function to call 'handleTaskFormChange' with necessary arguments
  watch(taskForm, function(newVal) {
    handleTaskFormChange(newVal, original, emitUpdate);
  }, { deep: true });

  return { form: taskForm };
}
