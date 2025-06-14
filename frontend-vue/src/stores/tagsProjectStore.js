import { defineStore } from 'pinia'
import { useAuthStore } from './authStore'

export const useTagsProjectStore = defineStore('tagsProjectStore', {
  state: () => ({
    projects: [],
    tags: [],
    selectedProjects: [],
    selectedTags: [],
  }),
  getters: {
    axios_instance() {
      const authStore = useAuthStore()
      return authStore.axios_instance
    },
  },
  actions: {
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
    },

    setSelectedTags(tags) {
      this.selectedTags = tags
    },

    clearFilters() {
      this.selectedProjects = []
      this.selectedTags = []
    },

    async assignProject(taskId, projectId) {
      return this.axios_instance.post(`api/assign_project/${taskId}/${projectId}/`)
    },
  },
})
