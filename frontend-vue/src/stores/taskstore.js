import { defineStore } from 'pinia';
import axios from 'axios';
import { useDateFormat } from '@vueuse/core';

const today = new Date();

// Use useDateFormat for consistent date formatting
const formatDate = (date) => {
  return useDateFormat(date, 'ddd, MMM D').value;
};

// Create a new date object to avoid mutation issues
const getTomorrow = () => {
  const tomorrow = new Date(today);
  tomorrow.setDate(today.getDate() + 1);
  return tomorrow;
};

const getYesterday = () => {
  const yesterday = new Date(today);
  yesterday.setDate(today.getDate() - 1);
  return yesterday;
};

// Add functions for additional date columns
const getNextWeek = () => {
  const nextWeek = new Date(today);
  nextWeek.setDate(today.getDate() + 7);
  return nextWeek;
};

const getAfterNextWeek = () => {
  const afterNextWeek = new Date(today);
  afterNextWeek.setDate(today.getDate() + 14);
  return afterNextWeek;
};

const getNextMonth = () => {
  const nextMonth = new Date(today);
  nextMonth.setMonth(today.getMonth() + 1);
  return nextMonth;
};

export const useTaskStore = defineStore('taskStore', {
  state: () => ({
    kanbanColumns: [
      {
        tasks: [],
        date: getYesterday(),
        dateString: formatDate(getYesterday()),
        title: "Yesterday",
      },
      {
        tasks: [],
        date: today,
        dateString: formatDate(today),
        title: "Today",
      },
      {
        tasks: [],
        date: getTomorrow(),
        dateString: formatDate(getTomorrow()),
        title: "Tomorrow",
      },
      {
        tasks: [],
        date: getNextWeek(),
        dateString: formatDate(getNextWeek()),
        title: "Next Week",
      },
      {
        tasks: [],
        date: getAfterNextWeek(),
        dateString: formatDate(getAfterNextWeek()),
        title: "After Next Week",
      },
      {
        tasks: [],
        date: getNextMonth(),
        dateString: formatDate(getNextMonth()),
        title: "Next Month",
      },
    ],
    brainDumpTasks: [],
  }),
  actions: {
    async fetchTasks() {
      try{
        const { data } = await axios.get('http://localhost:8000/api/tasks/');
        this.kanbanColumns.forEach((column) => {
          const filteredTasks = data.filter((task) => {
            const taskDate = new Date(task.created_at);
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
      } catch (error) {
        console.error('Error fetching tasks:', error);
      };
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
      // also remove from kanban
      this.kanbanColumns.forEach((column) => {
        column.tasks = column.tasks.filter((task) => task.id !== taskId);
      });
      // also remove from brain dump
      this.brainDumpTasks = this.brainDumpTasks.filter((task) => task.id !== taskId);
    },
    async updateTask(task) {
      await axios.put(`http://localhost:8000/api/tasks/${task.id}/`, task);
    },
    async updateTasksOrder(tasks_array) {
      try {
        const data = {
          "tasks": tasks_array,
          "action": "update_order"
        };
        await axios.put('http://localhost:8000/api/tasks/', data);
      } catch (error) {
        console.error('Error updating tasks order:', error);
      }
    },
  },
});
