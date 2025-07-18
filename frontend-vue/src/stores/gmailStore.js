import { defineStore } from 'pinia'
import { useAuthStore } from './authStore'
import { ref } from 'vue'

export const useGmailStore = defineStore('gmail', () => {
  const isLoading = ref(false)
  const isGmailConnected = ref(false)
  const isSyncEnabled = ref(false)
  const error = ref(null)
  const gmailEmails = ref([])
  const availableLabels = ref([])
  const selectedLabels = ref(['INBOX'])
  const pagination = ref({
    nextPageToken: null,
    hasMore: false,
  })

  const authStore = useAuthStore()

  async function checkGmailConnection() {
    try {
      isLoading.value = true
      const response = await authStore.axios_instance.get('/api/gmail/status/')
      isGmailConnected.value = response.data.connected
      isSyncEnabled.value = response.data.sync_enabled || false

      if (isGmailConnected.value) {
        // Fetch settings if connected
        await getSettings()
      }

      return isGmailConnected.value
    } catch (err) {
      error.value = err.response?.data?.error || 'Error checking Gmail connection'
      isGmailConnected.value = false
      isSyncEnabled.value = false
      return false
    } finally {
      isLoading.value = false
    }
  }

  // Get Gmail settings
  async function getSettings() {
    if (!isGmailConnected.value) {
      return { error: 'Gmail not connected' }
    }

    try {
      // Get available labels
      const labelsResponse = await authStore.axios_instance.get('/api/gmail/labels/')
      availableLabels.value = labelsResponse.data.labels || []

      // Get user settings
      const settingsResponse = await authStore.axios_instance.get('/api/gmail/settings/')
      isSyncEnabled.value = settingsResponse.data.gmail_sync_enabled
      selectedLabels.value = settingsResponse.data.gmail_sync_labels || ['INBOX']

      return {
        sync_enabled: isSyncEnabled.value,
        sync_labels: selectedLabels.value,
        available_labels: availableLabels.value,
      }
    } catch (err) {
      error.value = err.response?.data?.error || 'Failed to fetch Gmail settings'
      return { error: error.value }
    }
  }

  // Update Gmail settings
  async function updateSettings(settings) {
    if (!isGmailConnected.value) {
      return { error: 'Gmail not connected' }
    }

    try {
      const response = await authStore.axios_instance.put('/api/gmail/settings/', settings)
      isSyncEnabled.value = response.data.gmail_sync_enabled
      selectedLabels.value = response.data.gmail_sync_labels || ['INBOX']

      // If sync was enabled, fetch emails
      if (isSyncEnabled.value && !gmailEmails.value.length) {
        await fetchEmails()
      }

      return response.data
    } catch (err) {
      error.value = err.response?.data?.error || 'Failed to update Gmail settings'
      return { error: error.value }
    }
  }

  // Toggle sync enabled/disabled
  async function toggleSync(enabled) {
    return await updateSettings({ gmail_sync_enabled: enabled })
  }

  // Update selected labels
  async function updateLabels(labels) {
    return await updateSettings({ gmail_sync_labels: labels })
  }

  // Fetch emails from Gmail API
  async function fetchEmails(pageSize = 20) {
    if (!isGmailConnected.value) {
      return { error: 'Gmail not connected' }
    }

    if (!isSyncEnabled.value) {
      return { error: 'Gmail sync is disabled' }
    }

    isLoading.value = true
    try {
      const params = {
        maxResults: pageSize,
        labelIds: selectedLabels.value.join(','),
      }

      if (pagination.value.nextPageToken) {
        params.pageToken = pagination.value.nextPageToken
      }

      const response = await authStore.axios_instance.get('/api/gmail/emails/', { params })

      if (pagination.value.nextPageToken) {
        // If we're loading more emails, append them
        gmailEmails.value = [...gmailEmails.value, ...(response.data.emails || [])]
      } else {
        // Otherwise replace the list
        gmailEmails.value = response.data.emails || []
      }

      pagination.value.nextPageToken = response.data.nextPageToken
      pagination.value.hasMore = !!response.data.nextPageToken

      return response.data
    } catch (err) {
      error.value = err.response?.data?.error || 'Failed to fetch emails'
      return { error: error.value }
    } finally {
      isLoading.value = false
    }
  }

  // Load more emails (pagination)
  async function loadMoreEmails(pageSize = 20) {
    if (!pagination.value.hasMore) {
      return { emails: [] }
    }

    return await fetchEmails(pageSize)
  }

  // Reset pagination
  function resetPagination() {
    pagination.value.nextPageToken = null
    pagination.value.hasMore = false
  }

  // Toggle star status for an email
  async function toggleStar(emailId) {
    const email = gmailEmails.value.find((e) => e.id === emailId)
    if (!email) return

    const originalStarred = email.isStarred
    // Optimistic update
    email.isStarred = !email.isStarred

    try {
      await authStore.axios_instance.put(`/api/gmail/emails/${emailId}/star/`, {
        starred: email.isStarred,
      })
      return true
    } catch (err) {
      // Revert on failure
      email.isStarred = originalStarred
      error.value = err.response?.data?.error || 'Failed to update star status'
      return false
    }
  }

  // Mark email as read/unread
  async function markAsRead(emailId, read = true) {
    const email = gmailEmails.value.find((e) => e.id === emailId)
    if (!email) return

    const originalReadStatus = email.isRead
    // Optimistic update
    email.isRead = read

    try {
      await authStore.axios_instance.put(`/api/gmail/emails/${emailId}/read/`, {
        read: email.isRead,
      })
      return true
    } catch (err) {
      // Revert on failure
      email.isRead = originalReadStatus
      error.value = err.response?.data?.error || 'Failed to update read status'
      return false
    }
  }

  // Convert email to task
  async function convertToTask(emailId, taskDetails) {
    try {
      // Ensure we have all required fields
      if (!taskDetails.title) {
        return { error: 'Task title is required' }
      }

      if (!taskDetails.start_date) {
        taskDetails.start_date = new Date().toISOString()
      }

      const response = await authStore.axios_instance.post(`/api/gmail/emails/${emailId}/convert-to-task/`, taskDetails)

      // If mark as read is true, update the email in our local state
      if (taskDetails.mark_as_read) {
        const email = gmailEmails.value.find((e) => e.id === emailId)
        if (email) {
          email.isRead = true
        }
      }

      return response.data
    } catch (err) {
      error.value = err.response?.data?.error || 'Failed to convert email to task'
      return { error: error.value }
    }
  }

  // Update an email in the list
  function updateEmailInList(emailData) {
    const index = gmailEmails.value.findIndex((email) => email.id === emailData.id)
    if (index !== -1) {
      gmailEmails.value[index] = { ...gmailEmails.value[index], ...emailData }
    }
  }

  // Add a new email to the list
  function addNewEmail(emailData) {
    gmailEmails.value.unshift(emailData)
  }

  return {
    isLoading,
    isGmailConnected,
    isSyncEnabled,
    error,
    gmailEmails,
    pagination,
    availableLabels,
    selectedLabels,
    fetchEmails,
    loadMoreEmails,
    resetPagination,
    toggleStar,
    markAsRead,
    convertToTask,
    updateEmailInList,
    addNewEmail,
    checkGmailConnection,
    getSettings,
    updateSettings,
    toggleSync,
    updateLabels,
  }
})
