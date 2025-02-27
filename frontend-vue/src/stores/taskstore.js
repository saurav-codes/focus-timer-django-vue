import { defineStore } from 'pinia';
import axios from 'axios';

export const useTaskStore = defineStore('taskStore', {
  state: () => ({
    // Define three date-based columns:
    // - Yesterday, Today, and Tomorrow.
    columns: [
      {
        date: new Date(new Date().setDate(new Date().getDate() - 1)), // Yesterday
        tasks: [],
      },
      {
        date: new Date(), // Today
        tasks: [],
      },
      {
        date: new Date(new Date().setDate(new Date().getDate() + 1)), // Tomorrow
        tasks: [],
      },
    ],
  }),
  actions: {
    async fetchTasks() {
      try {
        const { data } = await axios.get('http://localhost:8000/api/tasks/');
        console.log("Fetched tasks from API:", data); // Debug log

        this.columns.forEach((column) => {
          const targetDateStr = column.date.toDateString();
          // console.log(`Processing column ${index}, date: ${targetDateStr}`); // Debug log

          const filteredTasks = data.filter((task) => {
            const taskDate = new Date(task.created_at);
            const matches = taskDate.toDateString() === targetDateStr;
            // console.log(`Task ${task.id} date: ${taskDate.toDateString()}, matches: ${matches}`); // Debug log
            return matches;
          });

          // Use direct assignment to ensure reactivity
          column.tasks = [...filteredTasks];
          // console.log("updated tasks data with - ", column.tasks)
          // console.log(`Column ${index} tasks updated, length: ${column.tasks.length}`); // Debug log
        });
      } catch (error) {
        console.error('Error fetching tasks:', error);
      }
    },
    async updateTaskStatus(task, newStatus) {
      try {
        await axios.patch(`http://localhost:8000/api/tasks/${task.id}/`, { status: newStatus });
        // Optionally update the task's local status.
        task.status = newStatus;
      } catch (error) {
        console.error('Error updating task:', error);
      }
    },
    reorderColumnTasksOnBackend(columnIndex, newTasks) {
      // Replace the existing tasks for this column with the new ordering.
      this.columns[columnIndex].tasks = newTasks;
      // TODO: Optionally send a request to the backend to persist the new order.
    },
    // TODO: add a task to a column
    addTaskToColumn(columnIndex, task) {
      this.columns[columnIndex].tasks.push(task);
      // send a request to the backend to persist the new task
    },
  },
});
