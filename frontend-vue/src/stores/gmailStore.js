import { defineStore } from 'pinia'
import { useAuthStore } from './authStore'
import { useWebSocket } from '@vueuse/core'
import { watch, ref } from 'vue'

export const useGmailStore = defineStore('gmail', () => {
  const host = import.meta.env.PROD ? import.meta.env.VITE_API_BASE_URL || 'tymr.online' : 'localhost:8000'
  const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws'
  const wsUrl = `${protocol}://${host}/ws/gmail/`
  const {
    status: gmailWsStatus,
    data: gmailWsData,
    open: gmailWsOpen,
    close: gmailWsClose,
    send: gmailWsSend,
  } = useWebSocket(wsUrl, {
    immediate: false,
    autoReconnect: { retries: 0, delay: 5000 },
  })

  const isLoading = ref(false)
  const isGmailConnected = ref(false)
  const error = ref(null)
  const gmailEmails = ref([])

  const authStore = useAuthStore()

  async function checkGmailConnection() {
    try {
      isLoading.value = true
      const response = await authStore.axios_instance.get('/api/gmail/status/')
      isGmailConnected.value = response.data.connected
      return isGmailConnected.value
    } catch (err) {
      error.value = err.response?.data?.error || 'Error checking Gmail connection'
      isGmailConnected.value = false
      return false
    } finally {
      isLoading.value = false
    }
  }

  // Fetch emails from Gmail API
  async function fetchEmails(page = 1, pageSize = 20) {
    if (!isGmailConnected.value) {
      console.log('Gmail not connected, skipping fetch')
      return
    }

    isLoading.value = true
    try {
      const response = await authStore.axios_instance.get('/api/gmail/emails/', {
        params: { page, page_size: pageSize },
      })
      gmailEmails.value = response.data.emails || []
      return response.data
    } catch (err) {
      error.value = err.response?.data?.error || 'Failed to fetch emails'
      return { error: error.value }
    } finally {
      isLoading.value = false
    }
  }

  // Handle WebSocket messages
  function routeGmailMessage(msg) {
    switch (msg.type) {
      case 'connected': {
        console.log('Gmail WS connected successfully: ', msg)
        fetchEmails()
        break
      }
      case 'email_update': {
        console.log('Received email update: ', msg.data)
        updateEmailInList(msg.data)
        break
      }
      case 'new_email': {
        console.log('Received new email: ', msg.data)
        addNewEmail(msg.data)
        break
      }
      default:
        console.warn('[GMAIL WS] unhandled message type:', msg.type)
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

  // Send action to WebSocket
  function _sendActionToGmailWebsocket(action, payload = {}) {
    if (!isGmailConnected.value) {
      console.log('Gmail not connected, skipping WebSocket message')
      return
    }

    if (gmailWsStatus.value === 'OPEN') {
      gmailWsSend(JSON.stringify({ action, payload }))
    } else {
      console.info('[WS] not initialized, ws status:', gmailWsStatus.value)
    }
  }

  // Watch incoming WebSocket data
  watch(gmailWsData, (raw) => {
    if (!raw) return
    let msg
    try {
      msg = JSON.parse(raw.data ?? raw)
    } catch {
      console.error('[GmailStore WS] invalid JSON:', raw)
      return
    }
    if (msg) {
      routeGmailMessage(msg)
    }
  })

  // Initialize WebSocket connection
  function initGmailWs() {
    if (!isGmailConnected.value) {
      console.log('Gmail not connected, skipping WebSocket initialization')
      return
    }

    const auth = useAuthStore()
    auth.verify_auth()
    if (auth.isAuthenticated) {
      console.info('User is authenticated, opening Gmail WebSocket')
      gmailWsOpen()
    }
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
      await authStore.axios_instance.post(`/api/gmail/emails/${emailId}/convert-to-task/`, taskDetails)
      return true
    } catch (err) {
      error.value = err.response?.data?.error || 'Failed to convert email to task'
      return false
    }
  }

  return {
    isLoading,
    isGmailConnected,
    error,
    gmailEmails,
    gmailWsStatus,
    fetchEmails,
    toggleStar,
    markAsRead,
    convertToTask,
    initGmailWs,
    gmailWsClose,
    checkGmailConnection,
  }
})
