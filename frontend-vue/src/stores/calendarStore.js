import { defineStore } from 'pinia'
import { useAuthStore } from './authStore'
import { useWebSocket } from '@vueuse/core'
import { watch, ref } from 'vue'
import { getDateStrFromDateObj } from '../../src/utils/taskUtils'

export const useCalendarStore = defineStore('calendar', () => {
  const host = import.meta.env.PROD ? import.meta.env.VITE_API_BASE_URL || 'tymr.online' : 'localhost:8000'
  const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws'
  const wsUrl = `${protocol}://${host}/ws/gcal/`
  const {
    status: gcalWsStatus,
    data: gcalWsData,
    open: gcalWsOpen,
    close: gcalWsClose,
    send: gcalWsSend,
  } = useWebSocket(wsUrl, {
    immediate: false,
    autoReconnect: { retries: 0, delay: 5000 },
  })

  const isLoading = ref(false)
  const isGoogleConnected = ref(false)
  const error = ref(null)
  const gcalEvents = ref([])

  const authStore = useAuthStore()

  async function checkGoogleConnection() {
    // methods using API
    try {
      isLoading.value = true
      const response = await authStore.axios_instance.get('api/gcalendar/status/')
      isGoogleConnected.value = response.data.connected
      return isGoogleConnected.value
    } catch (err) {
      error.value = err.response?.data?.error || 'Error checking Google connection'
      isGoogleConnected.value = false
      return false
    } finally {
      isLoading.value = false
    }
  }
  async function startGoogleAuth() {
    try {
      isLoading.value = true
      const response = await authStore.axios_instance.get('api/gcalendar/auth/start/')
      window.location.href = response.data.auth_url
    } catch (err) {
      error.value = err.response?.data?.error || 'Failed to connect to Google Calendar'
    } finally {
      isLoading.value = false
    }
  }
  async function disconnectGoogleCalendar() {
    try {
      isLoading.value = true
      await authStore.axios_instance.delete('api/gcalendar/disconnect/')
      isGoogleConnected.value = false
      gcalEvents.value = []
      return true
    } catch (err) {
      error.value = err.response?.data?.error || 'Failed to disconnect Google Calendar'
      return false
    } finally {
      isLoading.value = false
    }
  }
  async function updateGoogleCalendarEvent(eventId, updateData) {
    try {
      isLoading.value = true
      // Ensure the updateData contains all required fields in the correct format
      // The API expects specific format for updating Google Calendar events
      // Make the API call to update the event
      return await authStore.axios_instance.put(`api/gcalendar/events/${eventId}/`, updateData)
    } catch (error) {
      // Handle error and provide feedback
      if (error.response && error.response.data) {
        error.value = error.response.data.error || 'Failed to update Google Calendar event'
      } else {
        error.value = 'Network error while updating event'
      }
      return false
    } finally {
      isLoading.value = false
    }
  }
  // websocket methods
  function fetchGcalTask(date_str = '') {
    // Accept a local date string (YYYY-MM-DD). If none provided, use today's local date.
    if (!date_str) {
      const today = new Date()
      date_str = getDateStrFromDateObj(today)
      // console.log("no date passed so using today's local date -", date_str)
    }
    console.log('fetch gcal task with date -', date_str)
    _sendActionToGcalWebsocket('fetch_gcal_task_from_dt', { date_str: date_str })
  }
  function routeGcalMessage(msg) {
    switch (msg.type) {
      case 'connected': {
        console.log('google cal ws connected successfully: ', msg)
        fetchGcalTask()
        break
      }
      case 'gcal_event':
      case 'gcal.events': {
        const updates = msg.data || []
        updates.forEach((ev) => {
          const idx = gcalEvents.value.findIndex((e) => e.id === ev.id)
          if (idx !== -1) {
            gcalEvents.value.splice(idx, 1, ev)
          } else {
            gcalEvents.value.push(ev)
          }
        })
        break
      }
      default:
        console.warn('[GCAL WS] unhandled message type:', msg.type)
    }
  }
  // Generic send helper
  function _sendActionToGcalWebsocket(action, payload = {}) {
    if (gcalWsStatus.value === 'OPEN') {
      gcalWsSend(JSON.stringify({ action, payload }))
    } else {
      console.info('[WS] not initialized, ws status yet:', gcalWsStatus.value)
    }
  }

  // watch incoming data
  watch(gcalWsData, (raw) => {
    if (!raw) return
    let msg
    try {
      msg = JSON.parse(raw.data ?? raw)
    } catch {
      console.error('[CalendarStore GCAL WS] invalid JSON:', raw)
      return
    }
    if (msg) {
      routeGcalMessage(msg)
    }
  })
  function initGcalWs() {
    const auth = useAuthStore()
    auth.verify_auth() // sends a fetchuserdata request to make sure user is logged in
    if (auth.isAuthenticated) {
      console.info('user is authenticated opening gcal ws')
      gcalWsOpen()
    }
  }

  return {
    gcalEvents,
    fetchGcalTask,
    gcalWsStatus,
    initGcalWs,
    gcalWsClose,
    checkGoogleConnection,
    startGoogleAuth,
    disconnectGoogleCalendar,
    updateGoogleCalendarEvent,
  }
})
