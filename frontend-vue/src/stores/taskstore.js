import { defineStore } from 'pinia';
import axios from 'axios';

export const useTaskStore = defineStore('taskStore', {
  state: () => ({
    columns: [
      {
        date: new Date(),
        tasks: [],
      },
    ],
  }),
  actions: {
    async fetchTasks() {
      try {
        const { data } = await axios.get('http://localhost:8000/api/tasks/');
        // For simplicity, add tasks to first column
        this.columns[0].tasks = data;
        // TODO: handle logic to add task to suitable column
      } catch (error) {
        console.error('Error fetching tasks:', error);
      }
    },
    async updateTaskStatus(task, newStatus) {
      try {
        await axios.patch(`http://localhost:8000/api/tasks/${task.id}/`, { status: newStatus });
        // Optionally update local state
        task.status = newStatus;
      } catch (error) {
        console.error('Error updating task:', error);
      }
    },
    reorderColumnTasksOnBackend(columnIndex, newTasks) {
      // TODO: simplify this task ordering logic as it's lot messed up.
      console.log("new tasks passed are :", newTasks)
      // since task columns may have more or less task, so replace existing tasks
      // with new ones.
      this.columns[columnIndex].tasks = newTasks;
      // TODO: we also need a target column so when user dropped tasks in that
      // column then we need to update that column too.
      // send request to backend to update this
    },
  },
});
