import { defineStore } from 'pinia'
import { useAuthStore } from './authStore'
import { ref } from 'vue'

export const useGithubStore = defineStore('github', () => {
  const isLoading = ref(false)
  const isGithubConnected = ref(false)
  const isSyncEnabled = ref(false)
  const error = ref(null)
  const githubIssues = ref([])
  const githubUser = ref(null)
  const selectedRepositories = ref([])
  const availableRepositories = ref([])
  const pagination = ref({
    page: 1,
    hasMore: false,
    totalCount: 0,
  })

  const authStore = useAuthStore()

  // Check GitHub connection status
  async function checkGithubConnection() {
    try {
      isLoading.value = true
      const response = await authStore.axios_instance.get('/api/github/status/')
      isGithubConnected.value = response.data.connected
      isSyncEnabled.value = response.data.sync_enabled || false
      githubUser.value = response.data.user || null

      if (isGithubConnected.value) {
        // Fetch settings if connected
        await getSettings()
      }

      return isGithubConnected.value
    } catch (err) {
      error.value = err.response?.data?.error || 'Error checking GitHub connection'
      isGithubConnected.value = false
      isSyncEnabled.value = false
      return false
    } finally {
      isLoading.value = false
    }
  }

  // Start GitHub OAuth flow
  async function connectGithub() {
    try {
      isLoading.value = true
      const response = await authStore.axios_instance.get('/api/github/auth/start/')
      window.location.href = response.data.auth_url
    } catch (err) {
      error.value = err.response?.data?.error || 'Failed to connect to GitHub'
    } finally {
      isLoading.value = false
    }
  }

  // Disconnect GitHub account
  async function disconnectGithub() {
    try {
      isLoading.value = true
      await authStore.axios_instance.delete('/api/github/disconnect/')
      isGithubConnected.value = false
      isSyncEnabled.value = false
      githubIssues.value = []
      githubUser.value = null
      selectedRepositories.value = []
      availableRepositories.value = []
      return true
    } catch (err) {
      error.value = err.response?.data?.error || 'Failed to disconnect GitHub'
      return false
    } finally {
      isLoading.value = false
    }
  }

  // Get GitHub settings
  async function getSettings() {
    if (!isGithubConnected.value) {
      return { error: 'GitHub not connected' }
    }

    try {
      // Get available repositories
      const reposResponse = await authStore.axios_instance.get('/api/github/repositories/')
      availableRepositories.value = reposResponse.data.repositories || []

      // Get user settings
      const settingsResponse = await authStore.axios_instance.get('/api/github/settings/')
      isSyncEnabled.value = settingsResponse.data.github_sync_enabled || false
      selectedRepositories.value = settingsResponse.data.github_sync_repositories || []

      return {
        sync_enabled: isSyncEnabled.value,
        sync_repositories: selectedRepositories.value,
        available_repositories: availableRepositories.value,
      }
    } catch (err) {
      error.value = err.response?.data?.error || 'Failed to fetch GitHub settings'
      return { error: error.value }
    }
  }

  // Update GitHub settings
  async function updateSettings(settings) {
    if (!isGithubConnected.value) {
      return { error: 'GitHub not connected' }
    }

    try {
      const response = await authStore.axios_instance.put('/api/github/settings/', settings)
      isSyncEnabled.value = response.data.github_sync_enabled || false
      selectedRepositories.value = response.data.github_sync_repositories || []

      // If sync was enabled, fetch issues
      if (isSyncEnabled.value && !githubIssues.value.length) {
        await fetchIssues()
      }

      return response.data
    } catch (err) {
      error.value = err.response?.data?.error || 'Failed to update GitHub settings'
      return { error: error.value }
    }
  }

  // Toggle sync enabled/disabled
  async function toggleSync(enabled) {
    return await updateSettings({ github_sync_enabled: enabled })
  }

  // Update selected repositories
  async function updateRepositories(repositories) {
    return await updateSettings({ github_sync_repositories: repositories })
  }

  // Fetch issues assigned to user from selected repositories
  async function fetchIssues(page = 1, perPage = 30) {
    if (!isGithubConnected.value) {
      return { error: 'GitHub not connected' }
    }

    if (!isSyncEnabled.value) {
      return { error: 'GitHub sync is disabled' }
    }

    isLoading.value = true
    try {
      const params = {
        page: page,
        per_page: perPage,
        repositories: selectedRepositories.value.join(','),
        assignee: 'assigned', // Only get issues assigned to the authenticated user
        state: 'open', // Only get open issues
      }

      const response = await authStore.axios_instance.get('/api/github/issues/', { params })

      if (page === 1) {
        // Replace the list if it's the first page
        githubIssues.value = response.data.issues || []
      } else {
        // Append if loading more
        githubIssues.value = [...githubIssues.value, ...(response.data.issues || [])]
      }

      pagination.value.page = page
      pagination.value.hasMore = response.data.has_more || false
      pagination.value.totalCount = response.data.total_count || 0

      return response.data
    } catch (err) {
      error.value = err.response?.data?.error || 'Failed to fetch GitHub issues'
      return { error: error.value }
    } finally {
      isLoading.value = false
    }
  }

  // Load more issues (pagination)
  async function loadMoreIssues(perPage = 30) {
    if (!pagination.value.hasMore) {
      return { issues: [] }
    }

    return await fetchIssues(pagination.value.page + 1, perPage)
  }

  // Reset pagination
  function resetPagination() {
    pagination.value.page = 1
    pagination.value.hasMore = false
    pagination.value.totalCount = 0
  }

  // Get full issue details (including timeline/discussion)
  async function getIssueDetails(issueId) {
    if (!isGithubConnected.value) {
      return { error: 'GitHub not connected' }
    }

    try {
      isLoading.value = true
      const response = await authStore.axios_instance.get(`/api/github/issues/${issueId}/`)
      return response.data
    } catch (err) {
      error.value = err.response?.data?.error || 'Failed to fetch issue details'
      return { error: error.value }
    } finally {
      isLoading.value = false
    }
  }

  // Convert GitHub issue to task
  async function convertIssueToTask(issueId, taskDetails) {
    try {
      // Ensure we have all required fields
      if (!taskDetails.title) {
        return { error: 'Task title is required' }
      }

      const response = await authStore.axios_instance.post(
        `/api/github/issues/${issueId}/convert-to-task/`,
        taskDetails
      )
      return response.data
    } catch (err) {
      error.value = err.response?.data?.error || 'Failed to convert GitHub issue to task'
      return { error: error.value }
    }
  }

  // Update an issue in the list
  function updateIssueInList(issueData) {
    const index = githubIssues.value.findIndex((issue) => issue.id === issueData.id)
    if (index !== -1) {
      githubIssues.value[index] = { ...githubIssues.value[index], ...issueData }
    }
  }

  // Add a new issue to the list
  function addNewIssue(issueData) {
    githubIssues.value.unshift(issueData)
  }

  return {
    isLoading,
    isGithubConnected,
    isSyncEnabled,
    error,
    githubIssues,
    githubUser,
    selectedRepositories,
    availableRepositories,
    pagination,
    checkGithubConnection,
    connectGithub,
    disconnectGithub,
    getSettings,
    updateSettings,
    toggleSync,
    updateRepositories,
    fetchIssues,
    loadMoreIssues,
    resetPagination,
    getIssueDetails,
    convertIssueToTask,
    updateIssueInList,
    addNewIssue,
  }
})
