import { defineStore } from 'pinia'
import { useAuthStore } from './authStore'
import { useWebSocket } from '@vueuse/core'
import { watch, ref } from 'vue'
import { getDateStrFromDateObj } from '../../src/utils/taskUtils'

export const useCalendarStore = defineStore('calendar', () => {
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
    // methods using API
    try {
      isLoading.value = true
      const response = await authStore.axios_instance.get('api/gmail/status/')
      isGmailConnected.value = response.data.connected
      return isGmailConnected.value
    } catch (err) {
      error.value = err.response?.data?.error || 'Error checking Google connection'
      isGmailConnected.value = false
      return false
    } finally {
      isLoading.value = false
    }
  }

  // websocket methods
  function fetchEmails(date_str = '') {
    // Only fetch if Google Calendar is connected
    if (!isGmailConnected.value) {
      console.log('Google Calendar not connected, skipping fetch')
      return
    }

    // Accept a local date string (YYYY-MM-DD). If none provided, use today's local date.
    if (!date_str) {
      const today = new Date()
      date_str = getDateStrFromDateObj(today)
      // console.log("no date passed so using today's local date -", date_str)
    }
    console.log('fetch gmail with date -', date_str)
    _sendActionToGmailWebsocket('fetch_gcal_task_from_dt', { date_str: date_str })
  }
  function routeGcalMessage(msg) {
    switch (msg.type) {
      case 'connected': {
        console.log('gmail ws connected successfully: ', msg)
        fetchEmails()
        break
      }
      default:
        console.warn('[GMAIL WS] unhandled message type:', msg.type)
    }
  }
  // Generic send helper
  function _sendActionToGmailWebsocket(action, payload = {}) {
    // Only send WebSocket messages if Google Calendar is connected
    if (!isGmailConnected.value) {
      console.log('Google Calendar not connected, skipping WebSocket message')
      return
    }

    if (gmailWsStatus.value === 'OPEN') {
      gmailWsSend(JSON.stringify({ action, payload }))
    } else {
      console.info('[WS] not initialized, ws status yet:', gmailWsStatus.value)
    }
  }

  // watch incoming data
  watch(gmailWsData, (raw) => {
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
    // Only initialize WebSocket when Google Calendar is connected
    if (!isGmailConnected.value) {
      console.log('Google Calendar not connected, skipping WebSocket initialization')
      return
    }

    const auth = useAuthStore()
    auth.verify_auth() // sends a fetchuserdata request to make sure user is logged in
    if (auth.isAuthenticated) {
      console.info('user is authenticated opening gmail ws')
      gmailWsOpen()
    }
  }

  return {
    gmailEmails,
    fetchEmails,
    gmailWsStatus,
    initGcalWs,
    gmailWsClose,
    checkGmailConnection,
  }
})
