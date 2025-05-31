import { defineStore } from 'pinia'
import { useDateFormat } from '@vueuse/core'
import { useAuthStore } from './authStore'

const today = new Date()

// Use useDateFormat for consistent date formatting
const formatDate = (date) => {
  return useDateFormat(date, 'ddd, MMM D').value
}

// Create a date column for a specific date
const createDateColumn = (date, title = null) => {
  // Generate column title based on relative date if not provided
  if (!title) {
    const colDateObj = new Date(date)

    if (colDateObj.toDateString() === today.toDateString()) {
      title = 'Today'
    } else {
      const yesterday = new Date(today)
      yesterday.setDate(today.getDate() - 1)

      const tomorrow = new Date(today)
      tomorrow.setDate(today.getDate() + 1)

      if (colDateObj.toDateString() === yesterday.toDateString()) {
        title = 'Yesterday'
      } else if (colDateObj.toDateString() === tomorrow.toDateString()) {
        title = 'Tomorrow'
      } else {
        // Use date as title for other days
        title = formatDate(colDateObj)
      }
    }
  }

  return {
    tasks: [],
    date: new Date(date),
    dateString: formatDate(date),
    title: title,
  }
}

// Helper function to add days to a date
const addDays = (date, days) => {
  const newDate = new Date(date)
  newDate.setDate(date.getDate() + days)
  return newDate
}

// Add a helper function to format duration
const formatDurationForAPI = (duration) => {
  if (!duration) return null

  // If already in ISO format, return as is
  if (duration.includes('P') && duration.includes('T')) {
    return duration
  }

  // Parse HH:MM format
  const [hours, minutes] = duration.split(':').map(Number)

  // Convert to ISO 8601 duration format
  return `PT${hours}H${minutes}M`
}

export const useTaskStore = defineStore('taskStore', {
  state: () => ({
    kanbanColumns: [
      // Initial 4 columns
      createDateColumn(addDays(today, -1), 'Yesterday'),
      createDateColumn(today, 'Today'),
      createDateColumn(addDays(today, 1), 'Tomorrow'),
      createDateColumn(addDays(today, 2)),
    ],
    brainDumpTasks: [],
    lastDate: addDays(today, 2), // Track the last date we've added
    // Add filter-related state
    projects: [],
    tags: [],
    selectedProjects: [],
    selectedTags: [],
    backlogs: [],
    archivedTasks: [],
    calendarTasks: [],
  }),
  getters: {
    axios_instance() {
      const authStore = useAuthStore()
      return authStore.axios_instance
    },
  },
  actions: {
    async fetchTasks() {
      try {
        // Create query parameters from filters
        const params = new URLSearchParams()

        if (this.selectedProjects.length > 0) {
          params.append('project', this.selectedProjects[0])
        }

        if (this.selectedTags.length > 0) {
          this.selectedTags.forEach((tag) => {
            params.append('tags', tag)
          })
        }

        const { data } = await this.axios_instance.get(`api/tasks/?${params}`)

        // Reset task arrays
        this.kanbanColumns.forEach((column) => {
          column.tasks = []
        })
        this.brainDumpTasks = []

        // Distribute tasks to columns
        this.kanbanColumns.forEach((column) => {
          const filteredTasks = data.filter((task) => {
            if (task.status === 'ON_BOARD') {
              const taskDate = new Date(task.column_date)
              const taskDateString = taskDate.toDateString()
              return taskDateString === column.date.toDateString()
            }
            return false
          })
          // Use direct assignment to ensure reactivity
          // TODO: possible bug here because we aren't doing deep copy of the array
          column.tasks = [...filteredTasks]
        })

        this.brainDumpTasks = data.filter((task) => {
          return task.status === 'BRAINDUMP'
        })

        // Update backlogs
        this.backlogs = data.filter((task) => {
          return task.status === 'BACKLOG'
        })

        // Update archived tasks
        this.archivedTasks = data.filter((task) => {
          return task.status === 'ARCHIVED'
        })
        // Sort archived tasks by created_at date (newest first)
        this.archivedTasks.sort((a, b) => new Date(b.updated_at) - new Date(a.updated_at))

        this.calendarTasks = data.filter((task) => {
          return task.status === 'ON_CAL'
        })

        return data
      } catch (error) {
        console.error('Error fetching tasks:', error)
        throw error
      }
    },

    async fetchProjects() {
      try {
        const { data } = await this.axios_instance.get('api/projects/')
        this.projects = data
        return data
      } catch (error) {
        console.error('Error fetching projects:', error)
        throw error
      }
    },

    async createProject(projectData) {
      try {
        const { data } = await this.axios_instance.post('api/projects/create/', projectData)
        // Add the new project to the projects array
        this.projects.push(data)
        return data
      } catch (error) {
        console.error('Error creating project:', error)
        throw error
      }
    },

    async deleteProject(projectId) {
      try {
        // Remove the deleted project from the projects array
        this.projects = this.projects.filter((project) => project.id !== projectId)
        return await this.axios_instance.delete(`api/projects/${projectId}/`)
      } catch (error) {
        console.error('Error deleting project:', error)
        throw error
      }
    },

    async fetchTags() {
      try {
        const { data } = await this.axios_instance.get('api/tags/')
        this.tags = data
        return data
      } catch (error) {
        console.error('Error fetching tags:', error)
        throw error
      }
    },

    setSelectedProjects(projects) {
      this.selectedProjects = projects
      this.fetchTasks()
    },

    setSelectedTags(tags) {
      this.selectedTags = tags
      this.fetchTasks()
    },

    clearFilters() {
      this.selectedProjects = []
      this.selectedTags = []
      this.fetchTasks()
    },

    // Add more date columns for infinite scroll
    async addMoreColumns(count = 3) {
      for (let i = 0; i < count; i++) {
        const nextDate = addDays(this.lastDate, 1)
        this.kanbanColumns.push(createDateColumn(nextDate))
        this.lastDate = nextDate
      }
      // After adding columns, fetch tasks for the new columns
      // Return the promise so the caller knows when it's done
      return this.fetchTasks()
    },

    async toggleCompletion(taskId) {
      return this.axios_instance.post(`api/tasks/${taskId}/toggle_completion/`)
    },

    async assignProject(taskId, projectId) {
      return this.axios_instance.post(`api/assign_project/${taskId}/${projectId}/`)
    },

    async createTask(task) {
      // Format duration before sending to API
      const taskWithFormattedDuration = {
        ...task,
        duration: formatDurationForAPI(task.duration),
      }

      return this.axios_instance.post('api/tasks/', taskWithFormattedDuration)
    },

    async deleteTask(taskId) {
      return this.axios_instance.delete(`api/tasks/${taskId}/`)
    },

    async updateTask(task) {
      console.log('update task called')
      // Format duration before sending to API
      const taskWithFormattedDuration = {
        ...task,
        duration: formatDurationForAPI(task.duration),
      }

      console.log('sending post request for updating task')
      return this.axios_instance.put(`api/tasks/${task.id}/`, taskWithFormattedDuration)
    },

    async pushToArchiveTask(task) {
      // push task to archive
      this.archivedTasks.unshift(task)
    },

    async taskDroppedToBrainDump(task) {
      task.column_date = null
      task.status = 'BRAINDUMP'
      await this.updateTask(task)
    },

    async _getKanbanColumnTasks(taskId) {
      // search for this task first in braindump column
      const index = this.brainDumpTasks.findIndex((task) => task.id === taskId)
      if (index !== -1) {
        return this.brainDumpTasks
      }
      // if not found in brainDumpTasks, search in all kanban columns
      for (let i = 0; i < this.kanbanColumns.length; i++) {
        const column = this.kanbanColumns[i]
        const taskIndex = column.tasks.findIndex((task) => task.id === taskId)
        if (taskIndex !== -1) {
          return column.tasks
        }
      }
      console.log("we didn't find this task with id", taskId, ' anywhere ')
      return null
    },

    async updateTaskOrderOfKanban(taskId) {
      // first find the column tasks to save order
      const columnTasks = await this._getKanbanColumnTasks(taskId)
      if (columnTasks) {
        await this.updateTaskOrder(columnTasks)
      }
    },

    async searchAndRemoveTaskFromKanbanOrBraindump(taskId) {
      // Search for this task first in braindump column
      const index = this.brainDumpTasks.findIndex((task) => task.id === taskId)
      if (index !== -1) {
        this.brainDumpTasks.splice(index, 1)
        console.log(`Removed task with index ${index} from braindump column`)
        return
      }

      // If not found in brainDumpTasks, search in all kanban columns
      for (let i = 0; i < this.kanbanColumns.length; i++) {
        const column = this.kanbanColumns[i]
        const taskIndex = column.tasks.findIndex((task) => task.id === taskId)

        if (taskIndex !== -1) {
          // Remove the task from this column's tasks array
          column.tasks.splice(taskIndex, 1)
          console.log(`Removed task with index ${taskIndex} from kanban column ${column.title}`)
          return
        }
      }
      console.log('Could not find task with id', taskId, 'in any column')
    },

    async updateTaskOrder(tasks_array) {
      this.reInitializeOrder(tasks_array)
      try {
        const data = {
          tasks: tasks_array,
          action: 'update_order',
        }
        return this.axios_instance.put('api/tasks/', data)
      } catch (error) {
        console.error('Error updating tasks order:', error)
      }
    },

    reInitializeOrder(tasks_array) {
      // reinitialize order based on their existing order
      tasks_array.forEach((task, index) => {
        task.order = index
      })
    },
  },
})
