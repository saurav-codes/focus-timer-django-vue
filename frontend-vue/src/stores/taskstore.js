import { defineStore } from 'pinia';
import axios from 'axios';
import { useDateFormat } from '@vueuse/core';

const today = new Date();

// Use useDateFormat for consistent date formatting
const formatDate = (date) => {
  return useDateFormat(date, 'ddd, MMM D').value;
};

// Create a date column for a specific date
const createDateColumn = (date, title = null) => {
  // Generate column title based on relative date if not provided
  if (!title) {
    const dateObj = new Date(date);
    const todayObj = new Date(today);

    if (dateObj.toDateString() === todayObj.toDateString()) {
      title = "Today";
    } else {
      const yesterday = new Date(todayObj);
      yesterday.setDate(todayObj.getDate() - 1);

      const tomorrow = new Date(todayObj);
      tomorrow.setDate(todayObj.getDate() + 1);

      if (dateObj.toDateString() === yesterday.toDateString()) {
        title = "Yesterday";
      } else if (dateObj.toDateString() === tomorrow.toDateString()) {
        title = "Tomorrow";
      } else {
        // Use date as title for other days
        title = formatDate(dateObj);
      }
    }
  }

  return {
    tasks: [],
    date: new Date(date),
    dateString: formatDate(date),
    title: title,
  };
};

// Helper function to add days to a date
const addDays = (date, days) => {
  const newDate = new Date(date);
  newDate.setDate(date.getDate() + days);
  return newDate;
};

export const useTaskStore = defineStore('taskStore', {
  state: () => ({
    kanbanColumns: [
      // Initial 4 columns
      createDateColumn(addDays(today, -1), "Yesterday"),
      createDateColumn(today, "Today"),
      createDateColumn(addDays(today, 1), "Tomorrow"),
      createDateColumn(addDays(today, 2))
    ],
    brainDumpTasks: [],
    lastDate: addDays(today, 2), // Track the last date we've added
  }),
  actions: {
    async fetchTasks() {
      try {
        const { data } = await axios.get('http://localhost:8000/api/tasks/');
        this.kanbanColumns.forEach((column) => {
          const filteredTasks = data.filter((task) => {
            const taskDate = new Date(task.start_at || task.created_at);
            const taskDateString = taskDate.toDateString();
            const is_not_in_brain_dump = task.is_in_brain_dump === false;
            return taskDateString === column.date.toDateString() && is_not_in_brain_dump;
          });
          // Use direct assignment to ensure reactivity
          // TODO: possible bug here because we aren't doing deep copy of the array
          column.tasks = [...filteredTasks];
        });
        this.brainDumpTasks = data.filter((task) => {
          return task.is_in_brain_dump;
        });
        return data; // Return the data for chaining
      } catch (error) {
        console.error('Error fetching tasks:', error);
        throw error; // Rethrow to allow error handling by caller
      }
    },

    // Add more date columns for infinite scroll
    async addMoreColumns(count = 3) {
      for (let i = 0; i < count; i++) {
        const nextDate = addDays(this.lastDate, 1);
        this.kanbanColumns.push(createDateColumn(nextDate));
        this.lastDate = nextDate;
      }
      // After adding columns, fetch tasks for the new columns
      // Return the promise so the caller knows when it's done
      return await this.fetchTasks();
    },

    async toggleCompletion(taskId) {
      await axios.post(`http://localhost:8000/api/tasks/${taskId}/toggle_completion/`);
    },
    async createTask(task) {
      const { data } = await axios.post('http://localhost:8000/api/tasks/', task);
      return data;
    },
    async deleteTask(taskId) {
      await axios.delete(`http://localhost:8000/api/tasks/${taskId}/`);
    },
    async updateTask(task) {
      const {data } = await axios.put(`http://localhost:8000/api/tasks/${task.id}/`, task);
      return data
    },
    async taskDroppedToBrainDump({value}) {
      value.is_in_brain_dump = true;
      await this.updateTask(value);
    },
    async updateTaskOrder(tasks_array) {
      this.reInitializeOrder(tasks_array);
      try {
        const data = {
          "tasks": tasks_array,
          "action": "update_order"
        };
        axios.put('http://localhost:8000/api/tasks/', data);
      } catch (error) {
        console.error('Error updating tasks order:', error);
      }
    },
    reInitializeOrder (tasks_array) {
      // reinitialize order based on their existing order
      tasks_array.forEach((task, index) => {
        task.order = index;
      });
    }
  },
});
