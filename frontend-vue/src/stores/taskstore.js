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
    const colDateObj = new Date(date);

    if (colDateObj.toDateString() === today.toDateString()) {
      title = "Today";
    } else {
      const yesterday = new Date(today);
      yesterday.setDate(today.getDate() - 1);

      const tomorrow = new Date(today);
      tomorrow.setDate(today.getDate() + 1);

      if (colDateObj.toDateString() === yesterday.toDateString()) {
        title = "Yesterday";
      } else if (colDateObj.toDateString() === tomorrow.toDateString()) {
        title = "Tomorrow";
      } else {
        // Use date as title for other days
        title = formatDate(colDateObj);
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
            if (task.column_date) {
              const taskDate = new Date(task.column_date);
              const taskDateString = taskDate.toDateString();
              return taskDateString === column.date.toDateString();
            }
          });
          // Use direct assignment to ensure reactivity
          // TODO: possible bug here because we aren't doing deep copy of the array
          column.tasks = [...filteredTasks];
        });
        this.brainDumpTasks = data.filter((task) => {
          return !task.column_date;
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
      const {data} = await axios.put(`http://localhost:8000/api/tasks/${task.id}/`, task);

      // find the task in the kanbanColumns array or the brainDumpTasks array and update the task
      let taskFound = false;

      // Search in kanban columns
      for (const column of this.kanbanColumns) {
        const taskIndex = column.tasks.findIndex(t => t.id === data.id);
        if (taskIndex !== -1) {
          column.tasks[taskIndex] = { ...data };
          console.log("task found in kanban columns and updated");
          taskFound = true;
          break;
        }
      }

      // If not found in columns, search in brain dump
      if (!taskFound) {
        const brainDumpIndex = this.brainDumpTasks.findIndex(t => t.id === data.id);
        if (brainDumpIndex !== -1) {
          this.brainDumpTasks[brainDumpIndex] = { ...data };
          console.log("task found in brain dump and updated");
          taskFound = true;
        }
      }

      if (!taskFound) {
        console.log("hell no.. task not found in kanban columns or brain dump, something is wrong");
      }

      return data;
    },
    async taskDroppedToBrainDump({value}) {
      value.column_date = null;
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
