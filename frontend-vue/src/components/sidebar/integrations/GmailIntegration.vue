<script setup>
import {
  ref,
  onMounted,
  onUnmounted,
  watch,
  computed,
} from 'vue'
import { useGmailStore } from '../../../stores/gmailStore'
import { useCalendarStore } from '../../../stores/calendarStore'
import {
  LucideCalendar,
  LucideLink,
  LucideUnlink,
  LucideChevronLeft,
  LucideChevronRight,
} from 'lucide-vue-next'
import Popper from 'vue3-popper'
import { useIntervalFn } from '@vueuse/core'

const gmailStore = useGmailStore()
const calStore = useCalendarStore()

const isConnected = ref(false)
const isLoading = ref(false)
const showPopper = ref(false)
const gmailError = computed(() => {
  return gmailStore.error
})

// Define stopPolling in the parent scope so it's accessible in onUnmounted
let stopPolling = () => { }

// --- Connection Status Indicator for Header ---
const showConnectPopper = ref(false)

onMounted(async () => {
  isLoading.value = true
  try {
    // Check connection status
    isConnected.value = await gmailStore.checkGmailConnection()

    // Only initialize Gmail WebSocket if connected
    if (isConnected.value) {
      gmailStore.initGmailWs()
    }
  } catch (error) {
    console.error('Error checking Gmail connection:', error)
    isConnected.value = false
  }

  // Watch for Gmail errors
  watch(gmailError, (newError) => {
    if (newError) {
      alert(newError)
      gmailStore.error = null
    }
  }, { deep: true })

  isLoading.value = false

  // Only start polling if Gmail is connected
  if (isConnected.value) {
    const { pause } = useIntervalFn(() => {
      gmailStore.fetchEmails()
    }, 5 * 60 * 1000)
    stopPolling = pause
  }
})

onUnmounted(async () => {
  // close gcal event ws connection
  gmailStore.gmailWsClose()
  stopPolling()
})

const connectGoogleCalendar = () => {
  // Use the calendar store's auth method since Gmail uses the same OAuth flow
  calStore.startGoogleAuth()
}

const disconnectGmail = async () => {
  isLoading.value = true
  // For now, we'll use the calendar store's disconnect method
  // This will be updated when we implement Gmail-specific disconnect
  await calStore.disconnectGoogleCalendar()
  isConnected.value = false
  isLoading.value = false
}

</script>

<template>
  <div class="gmail-integration">
    <div class="integration-header">
      <div class="left-header">
        <h3>
          <LucideCalendar :size="14" />
          Gmail
        </h3>
        <div class="date-navigation">
          <div class="nav-controls">
            <button class="nav-btn prev-btn">
              <LucideChevronLeft :size="16" />
            </button>
            <button class="nav-btn next-btn">
              <LucideChevronRight :size="16" />
            </button>
          </div>
        </div>
      </div>
      <!-- Connection status controls -->
      <div class="connection-controls">
        <Popper v-if="isConnected" arrow content="Disconnect Google Account" :show="showPopper">
          <LucideUnlink
            class="disconnect-button"
            :class="{ 'disabled-div': isLoading }"
            :size="14"
            @mouseover="showPopper = true"
            @mouseleave="showPopper = false"
            @click="disconnectGmail" />
        </Popper>
        <Popper v-else arrow content="Connect Gmail" :show="showConnectPopper">
          <div
            class="google-connect-button"
            :class="{ 'disabled-div': isLoading }"
            @mouseover="showConnectPopper = true"
            @mouseleave="showConnectPopper = false"
            @click="connectGoogleCalendar">
            <span class="google-icon">Gmail</span>
            <LucideLink :size="10" class="link-icon" />
          </div>
        </Popper>
      </div>
    </div>
    <div class="calendar-container">
      <div v-if="isLoading" class="loading">
        <div class="spinner" />
        <span>Loading...</span>
      </div>
    </div>
  </div>
</template>
