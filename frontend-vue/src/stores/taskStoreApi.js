import { defineStore } from 'pinia'
import { useAuthStore } from './authStore'
import { formatDurationForAPI } from '../utils/taskUtils'

export const useTaskStoreApi = defineStore('taskStoreApi', {
  getters: {
    axios_instance() {
      const authStore = useAuthStore()
      return authStore.axios_instance
    },
  },
  actions: {
    async updateTaskDuration(taskId, durationStr) {
      try {
        const payload = { task_id: taskId, duration: formatDurationForAPI(durationStr) }
        return this.axios_instance.post('api/update_task_duration/', payload)
      } catch (error) {
        console.error('Error updating task duration:', error)
        throw error
      }
    },
  },
})
