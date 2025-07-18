<script setup>
import {
  ref,
  onMounted,
  onUnmounted,
  watch
} from 'vue'
import { useGmailStore } from '../../../stores/gmailStore'
import { useCalendarStore } from '../../../stores/calendarStore'
import { useTaskStoreApi } from '../../../stores/taskStoreApi'
import { useIntervalFn } from '@vueuse/core'
import {
  LucideInbox,
  LucideLink,
  LucideUnlink,
  LucideRefreshCw,
  LucideStar,
  LucideStarOff,
  LucideMail,
  LucideMailOpen,
  LucideCheckSquare,
  LucideX,
  LucideExternalLink,
  LucideSettings,
  LucideToggleLeft,
  LucideToggleRight,
  LucideCheck
} from 'lucide-vue-next'
import Popper from 'vue3-popper'

const gmailStore = useGmailStore()
const calStore = useCalendarStore()
const taskStore = useTaskStoreApi()

const isConnected = ref(false)
const isSyncEnabled = ref(false)
const isLoading = ref(false)
const selectedEmail = ref(null)
const showConvertModal = ref(false)
const showSettingsModal = ref(false)
const taskForm = ref({
  title: '',
  description: '',
  status: 'ON_BOARD',
  start_date: new Date().toISOString(),
})

// Popper visibility states - use separate refs for each button
const refreshPopperVisible = ref(false)
const disconnectPopperVisible = ref(false)
const connectPopperVisible = ref(false)
const settingsPopperVisible = ref(false)

// Email action popper states
const starPopperStates = ref({})
const readPopperStates = ref({})
const convertPopperStates = ref({})
const openPopperVisible = ref(false)

// Format date to local timezone
const formatLocalTime = (timestamp) => {
  if (!timestamp) return ''

  const date = new Date(timestamp * 1000)

  // Today's date for comparison
  const today = new Date()
  const isToday = date.getDate() === today.getDate() &&
                 date.getMonth() === today.getMonth() &&
                 date.getFullYear() === today.getFullYear()

  // Yesterday's date for comparison
  const yesterday = new Date(today)
  yesterday.setDate(yesterday.getDate() - 1)
  const isYesterday = date.getDate() === yesterday.getDate() &&
                     date.getMonth() === yesterday.getMonth() &&
                     date.getFullYear() === yesterday.getFullYear()

  // Format based on how recent the email is
  if (isToday) {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  } else if (isYesterday) {
    return 'Yesterday'
  } else if (date.getFullYear() === today.getFullYear()) {
    // Same year, show month and day
    return date.toLocaleDateString([], { month: 'short', day: 'numeric' })
  } else {
    // Different year, show date with year
    return date.toLocaleDateString([], { month: 'short', day: 'numeric', year: 'numeric' })
  }
}

// Format full date and time for email detail view
const formatFullDateTime = (timestamp) => {
  if (!timestamp) return ''
  const date = new Date(timestamp * 1000)
  return date.toLocaleString([], {
    weekday: 'short',
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// Auto-refresh emails every 5 minutes
let stopPolling = () => {}

onMounted(async () => {
  isLoading.value = true
  try {
    // Check connection status
    isConnected.value = await gmailStore.checkGmailConnection()
    isSyncEnabled.value = gmailStore.isSyncEnabled

    // Fetch emails if connected and sync is enabled
    if (isConnected.value && isSyncEnabled.value) {
      await gmailStore.fetchEmails()

      // Set up polling for new emails every 5 minutes
      const { pause } = useIntervalFn(() => {
        if (isConnected.value && isSyncEnabled.value) {
          gmailStore.resetPagination()
          gmailStore.fetchEmails()
        }
      }, 5 * 60 * 1000) // 5 minutes

      stopPolling = pause
    }
  } catch (error) {
    console.error('Error checking Gmail connection:', error)
    isConnected.value = false
  } finally {
    isLoading.value = false
  }
})

onUnmounted(() => {
  // Stop polling when component is unmounted
  stopPolling()
})

// Watch for changes in sync status
watch(() => gmailStore.isSyncEnabled, (newValue) => {
  isSyncEnabled.value = newValue
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
  isSyncEnabled.value = false
  isLoading.value = false
}

const refreshEmails = async () => {
  isLoading.value = true
  gmailStore.resetPagination()
  await gmailStore.fetchEmails()
  isLoading.value = false
}

const loadMoreEmails = async () => {
  isLoading.value = true
  await gmailStore.loadMoreEmails()
  isLoading.value = false
}

const toggleEmailStar = async (emailId) => {
  await gmailStore.toggleStar(emailId)
}

const toggleEmailRead = async (emailId, isRead) => {
  await gmailStore.markAsRead(emailId, !isRead)
}

const openEmailDetail = (email) => {
  selectedEmail.value = email

  // Mark as read when opening
  if (!email.isRead) {
    gmailStore.markAsRead(email.id, true)
  }
}

const closeEmailDetail = () => {
  selectedEmail.value = null
}

const showConvertToTaskModal = (email) => {
  taskForm.value = {
    title: email.subject,
    description: `From: ${email.sender} (${email.senderEmail})\n\n${email.preview}\n\nView in Gmail: ${email.link}`,
    status: 'ON_BOARD',
    start_date: new Date().toISOString(),
  }
  showConvertModal.value = true
  selectedEmail.value = email
}

const closeConvertModal = () => {
  showConvertModal.value = false
}

const openSettingsModal = async () => {
  await gmailStore.getSettings()
  showSettingsModal.value = true
}

const closeSettingsModal = () => {
  showSettingsModal.value = false
}

const toggleSync = async () => {
  isLoading.value = true
  await gmailStore.toggleSync(!isSyncEnabled.value)
  isSyncEnabled.value = gmailStore.isSyncEnabled

  // If sync was enabled, fetch emails
  if (isSyncEnabled.value && !gmailStore.gmailEmails.length) {
    await gmailStore.fetchEmails()
  }

  isLoading.value = false
}

const toggleLabel = async (labelId) => {
  const currentLabels = [...gmailStore.selectedLabels]
  const index = currentLabels.indexOf(labelId)

  if (index === -1) {
    currentLabels.push(labelId)
  } else {
    currentLabels.splice(index, 1)
  }

  isLoading.value = true
  await gmailStore.updateLabels(currentLabels)
  isLoading.value = false
}

const isLabelSelected = (labelId) => {
  return gmailStore.selectedLabels.includes(labelId)
}

const convertEmailToTask = async () => {
  if (!selectedEmail.value) return

  isLoading.value = true
  try {
    const result = await gmailStore.convertToTask(selectedEmail.value.id, taskForm.value)

    if (result.error) {
      alert(result.error)
      return
    }

    // Refresh tasks if conversion was successful
    await taskStore.fetchTasks()

    // Close modals
    closeConvertModal()
    closeEmailDetail()
  } catch (error) {
    console.error('Error converting email to task:', error)
    alert('Failed to convert email to task')
  } finally {
    isLoading.value = false
  }
}

// Close modal when clicking outside
const handleModalOverlayClick = (event) => {
  // Only close if clicking directly on the overlay, not its children
  if (event.target === event.currentTarget) {
    closeEmailDetail()
  }
}

const handleSettingsOverlayClick = (event) => {
  // Only close if clicking directly on the overlay, not its children
  if (event.target === event.currentTarget) {
    closeSettingsModal()
  }
}

const handleConvertOverlayClick = (event) => {
  // Only close if clicking directly on the overlay, not its children
  if (event.target === event.currentTarget) {
    closeConvertModal()
  }
}

// Helper functions for popper visibility
const showStarPopper = (emailId) => {
  starPopperStates.value = { [emailId]: true }
}

const hideStarPopper = () => {
  starPopperStates.value = {}
}

const showReadPopper = (emailId) => {
  readPopperStates.value = { [emailId]: true }
}

const hideReadPopper = () => {
  readPopperStates.value = {}
}

const showConvertPopper = (emailId) => {
  convertPopperStates.value = { [emailId]: true }
}

const hideConvertPopper = () => {
  convertPopperStates.value = {}
}
</script>

<template>
  <div class="gmail-integration">
    <div class="integration-header">
      <div class="left-header">
        <h3>
          <LucideInbox :size="14" />
          Gmail
        </h3>
        <div v-if="isConnected && isSyncEnabled" class="refresh-control">
          <Popper arrow content="Refresh emails" :show="refreshPopperVisible">
            <button
              class="refresh-btn"
              :disabled="isLoading"
              @click="refreshEmails"
              @mouseover="refreshPopperVisible = true"
              @mouseleave="refreshPopperVisible = false">
              <LucideRefreshCw :size="14" :class="{ 'rotating': isLoading }" />
            </button>
          </Popper>
        </div>
      </div>
      <!-- Connection status controls -->
      <div class="connection-controls">
        <Popper v-if="isConnected" arrow content="Settings" :show="settingsPopperVisible">
          <button
            class="settings-button"
            :class="{ 'disabled-div': isLoading }"
            @click="openSettingsModal"
            @mouseover="settingsPopperVisible = true"
            @mouseleave="settingsPopperVisible = false">
            <LucideSettings :size="14" />
          </button>
        </Popper>

        <Popper v-if="isConnected" arrow content="Disconnect Google Account" :show="disconnectPopperVisible">
          <button
            class="disconnect-button"
            :class="{ 'disabled-div': isLoading }"
            @click="disconnectGmail"
            @mouseover="disconnectPopperVisible = true"
            @mouseleave="disconnectPopperVisible = false">
            <LucideUnlink :size="14" />
          </button>
        </Popper>

        <Popper v-else arrow content="Connect Gmail" :show="connectPopperVisible">
          <div
            class="google-connect-button"
            :class="{ 'disabled-div': isLoading }"
            @mouseover="connectPopperVisible = true"
            @mouseleave="connectPopperVisible = false"
            @click="connectGoogleCalendar">
            <span class="google-icon">Gmail</span>
            <LucideLink :size="10" class="link-icon" />
          </div>
        </Popper>
      </div>
    </div>

    <div class="emails-container">
      <div v-if="isLoading && !gmailStore.gmailEmails.length" class="loading">
        <div class="spinner" />
        <span class="text-sm">Loading emails...</span>
      </div>

      <div v-else-if="!isConnected" class="not-connected">
        <p class="text-sm">
          Connect your Gmail account to view and manage emails.
        </p>
        <button class="connect-button" @click="connectGoogleCalendar">
          Connect Gmail
        </button>
      </div>

      <div v-else-if="!isSyncEnabled" class="sync-disabled">
        <p class="text-sm">
          Gmail sync is currently disabled.
        </p>
        <button class="enable-sync-button" @click="toggleSync">
          Enable Sync
        </button>
      </div>

      <div v-else-if="gmailStore.gmailEmails.length === 0" class="no-emails">
        <p class="text-sm">
          No emails found.
        </p>
      </div>

      <div v-else class="email-list">
        <div
          v-for="email in gmailStore.gmailEmails"
          :key="email.id"
          class="email-item"
          :class="{ 'unread': !email.isRead }"
          @click="openEmailDetail(email)">
          <div class="email-header">
            <div class="sender text-sm font-medium">
              {{ email.sender }}
            </div>
            <div class="time text-xs">
              {{ formatLocalTime(email.timestamp) }}
            </div>
          </div>
          <div class="subject text-sm">
            {{ email.subject }}
          </div>
          <div class="preview text-xs">
            {{ email.preview }}
          </div>
          <div class="email-actions" @click.stop>
            <Popper arrow content="Toggle star" :show="starPopperStates[email.id]">
              <button
                class="action-button"
                :class="{ 'starred': email.isStarred }"
                @click="toggleEmailStar(email.id)"
                @mouseover="showStarPopper(email.id)"
                @mouseleave="hideStarPopper">
                <LucideStar v-if="email.isStarred" :size="14" />
                <LucideStarOff v-else :size="14" />
              </button>
            </Popper>

            <Popper arrow :content="email.isRead ? 'Mark as unread' : 'Mark as read'" :show="readPopperStates[email.id]">
              <button
                class="action-button"
                @click="toggleEmailRead(email.id, email.isRead)"
                @mouseover="showReadPopper(email.id)"
                @mouseleave="hideReadPopper">
                <LucideMailOpen v-if="email.isRead" :size="14" />
                <LucideMail v-else :size="14" />
              </button>
            </Popper>

            <Popper arrow content="Convert to task" :show="convertPopperStates[email.id]">
              <button
                class="action-button"
                @click="showConvertToTaskModal(email)"
                @mouseover="showConvertPopper(email.id)"
                @mouseleave="hideConvertPopper">
                <LucideCheckSquare :size="14" />
              </button>
            </Popper>
          </div>
        </div>

        <div v-if="gmailStore.pagination.hasMore" class="load-more">
          <button class="load-more-button" :disabled="isLoading" @click="loadMoreEmails">
            <span v-if="isLoading">Loading...</span>
            <span v-else>Load More</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Email Detail Modal -->
    <div v-if="selectedEmail" class="modal-overlay" @click="handleModalOverlayClick">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3 class="text-lg font-medium">
            {{ selectedEmail.subject }}
          </h3>
          <button class="close-button" @click="closeEmailDetail">
            <LucideX :size="18" />
          </button>
        </div>
        <div class="modal-body">
          <div class="email-info">
            <div class="sender-info text-sm">
              <div><strong>From:</strong> {{ selectedEmail.sender }} &lt;{{ selectedEmail.senderEmail }}&gt;</div>
              <div class="email-date text-xs">
                {{ formatFullDateTime(selectedEmail.timestamp) }}
              </div>
            </div>
            <div class="email-actions">
              <Popper arrow content="Toggle star" :show="starPopperStates['detail']">
                <button
                  class="action-button"
                  :class="{ 'starred': selectedEmail.isStarred }"
                  @click="toggleEmailStar(selectedEmail.id)"
                  @mouseover="showStarPopper('detail')"
                  @mouseleave="hideStarPopper">
                  <LucideStar v-if="selectedEmail.isStarred" :size="14" />
                  <LucideStarOff v-else :size="14" />
                </button>
              </Popper>

              <Popper arrow :content="selectedEmail.isRead ? 'Mark as unread' : 'Mark as read'" :show="readPopperStates['detail']">
                <button
                  class="action-button"
                  @click="toggleEmailRead(selectedEmail.id, selectedEmail.isRead)"
                  @mouseover="showReadPopper('detail')"
                  @mouseleave="hideReadPopper">
                  <LucideMailOpen v-if="selectedEmail.isRead" :size="14" />
                  <LucideMail v-else :size="14" />
                </button>
              </Popper>

              <Popper arrow content="Convert to task" :show="convertPopperStates['detail']">
                <button
                  class="action-button"
                  @click="showConvertToTaskModal(selectedEmail)"
                  @mouseover="showConvertPopper('detail')"
                  @mouseleave="hideConvertPopper">
                  <LucideCheckSquare :size="14" />
                </button>
              </Popper>

              <Popper arrow content="Open in Gmail" :show="openPopperVisible">
                <a
                  :href="selectedEmail.link"
                  target="_blank"
                  class="open-in-gmail"
                  @mouseover="openPopperVisible = true"
                  @mouseleave="openPopperVisible = false">
                  <LucideExternalLink :size="14" />
                  Open in Gmail
                </a>
              </Popper>
            </div>
          </div>
          <div class="email-preview text-sm">
            {{ selectedEmail.preview }}
          </div>
          <div class="email-link">
            <a :href="selectedEmail.link" target="_blank" class="view-original-link">
              View original email in Gmail
            </a>
          </div>
        </div>
      </div>
    </div>

    <!-- Convert to Task Modal -->
    <div v-if="showConvertModal" class="modal-overlay" @click="handleConvertOverlayClick">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3 class="text-lg font-medium">
            Convert Email to Task
          </h3>
          <button class="close-button" @click="closeConvertModal">
            <LucideX :size="18" />
          </button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="convertEmailToTask">
            <div class="form-group">
              <label for="task-title" class="text-sm">Title</label>
              <input id="task-title" v-model="taskForm.title" type="text" required>
            </div>
            <div class="form-group">
              <label for="task-description" class="text-sm">Description</label>
              <textarea id="task-description" v-model="taskForm.description" rows="4" />
            </div>
            <div class="form-group checkbox">
              <input id="mark-as-read" v-model="taskForm.mark_as_read" type="checkbox">
              <label for="mark-as-read" class="text-sm">Mark email as read</label>
            </div>
            <div class="form-actions">
              <button type="button" class="cancel-button" @click="closeConvertModal">
                Cancel
              </button>
              <button type="submit" class="submit-button" :disabled="isLoading">
                <span v-if="isLoading">Creating...</span>
                <span v-else>Create Task</span>
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- Settings Modal -->
    <div v-if="showSettingsModal" class="modal-overlay" @click="handleSettingsOverlayClick">
      <div class="modal-content settings-modal" @click.stop>
        <div class="modal-header">
          <h3 class="text-lg font-medium">
            Gmail Settings
          </h3>
          <button class="close-button" @click="closeSettingsModal">
            <LucideX :size="18" />
          </button>
        </div>
        <div class="modal-body">
          <div class="settings-section">
            <div class="setting-item">
              <div class="setting-label">
                <h4 class="text-base font-medium">
                  Gmail Sync
                </h4>
                <p class="text-sm text-muted">
                  Enable or disable Gmail synchronization
                </p>
              </div>
              <button class="toggle-button" :disabled="isLoading" @click="toggleSync">
                <LucideToggleLeft v-if="!isSyncEnabled" :size="24" />
                <LucideToggleRight v-else :size="24" class="active" />
              </button>
            </div>

            <div v-if="isSyncEnabled" class="setting-item">
              <div class="setting-label">
                <h4 class="text-base font-medium">
                  Labels to Sync
                </h4>
                <p class="text-sm text-muted">
                  Select which Gmail labels to display
                </p>
              </div>
              <div class="labels-list">
                <div
                  v-for="label in gmailStore.availableLabels"
                  :key="label.id"
                  class="label-item"
                  :class="{ 'selected': isLabelSelected(label.id) }"
                  @click="toggleLabel(label.id)">
                  <span class="label-name">{{ label.name }}</span>
                  <LucideCheck v-if="isLabelSelected(label.id)" :size="16" class="check-icon" />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.gmail-integration {
  display: flex;
  flex-direction: column;
  height: 100%;
  background-color: var(--color-background);
  color: var(--color-text-primary);
}

.integration-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px;
  border-bottom: 1px solid var(--color-border);
}

.left-header {
  display: flex;
  align-items: center;
}

.left-header h3 {
  display: flex;
  align-items: center;
  gap: 5px;
  margin: 0;
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-semibold);
}

.refresh-control {
  margin-left: 10px;
}

.refresh-btn, .settings-button, .disconnect-button {
  background: none;
  border: none;
  cursor: pointer;
  padding: 5px;
  border-radius: 50%;
  color: var(--color-text-secondary);
}

.refresh-btn:hover, .settings-button:hover {
  background-color: var(--color-background-secondary);
  color: var(--color-text-primary);
}

.disconnect-button:hover {
  color: var(--color-error);
}

.rotating {
  animation: rotate 1s linear infinite;
}

@keyframes rotate {
  from {
    transform: rotate(0deg);
  }

  to {
    transform: rotate(360deg);
  }
}

.connection-controls {
  display: flex;
  align-items: center;
  gap: 8px;
}

.google-connect-button {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 5px 10px;
  border-radius: 4px;
  background-color: var(--color-primary);
  color: var(--color-text-selected);
  cursor: pointer;
  font-size: var(--font-size-xs);
}

.google-connect-button:hover {
  background-color: var(--color-primary-light);
}

.emails-container {
  flex: 1;
  overflow-y: auto;
  padding: 10px;
}

.loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100px;
  color: var(--color-text-secondary);
}

.spinner {
  border: 2px solid var(--color-background-tertiary);
  border-top: 2px solid var(--color-primary);
  border-radius: 50%;
  width: 20px;
  height: 20px;
  animation: spin 1s linear infinite;
  margin-bottom: 10px;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }

  100% {
    transform: rotate(360deg);
  }
}

.not-connected, .sync-disabled, .no-emails {
  text-align: center;
  padding: 20px;
  color: var(--color-text-secondary);
}

.connect-button, .enable-sync-button {
  background-color: var(--color-primary);
  color: var(--color-text-selected);
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  margin-top: 10px;
  font-size: var(--font-size-sm);
}

.connect-button:hover, .enable-sync-button:hover {
  background-color: var(--color-primary-light);
}

.email-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.email-item {
  padding: 10px;
  border-radius: 4px;
  background-color: var(--color-background-secondary);
  cursor: pointer;
  position: relative;
  border: 1px solid var(--color-border);
  transition: background-color var(--transition-base);
}

.email-item:hover {
  background-color: var(--color-background-tertiary);
}

.email-item.unread {
  border-left: 3px solid var(--color-primary);
}

.email-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 5px;
}

.sender {
  color: var(--color-text-primary);
}

.time {
  color: var(--color-text-tertiary);
}

.subject {
  margin-bottom: 5px;
  color: var(--color-text-primary);
}

.preview {
  color: var(--color-text-tertiary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.email-actions {
  display: flex;
  gap: 5px;
  position: absolute;
  top: 10px;
  right: 10px;
  opacity: 0;
  transition: opacity var(--transition-base);
}

.email-item:hover .email-actions {
  opacity: 1;
}

.action-button {
  background: none;
  border: none;
  cursor: pointer;
  padding: 5px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-text-secondary);
}

.action-button:hover {
  background-color: var(--color-background-tertiary);
}

.action-button.starred {
  color: var(--color-warning);
}

.load-more {
  text-align: center;
  margin-top: 10px;
}

.load-more-button {
  background-color: var(--color-background-secondary);
  border: 1px solid var(--color-border);
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  color: var(--color-text-primary);
  font-size: var(--font-size-sm);
}

.load-more-button:hover {
  background-color: var(--color-background-tertiary);
}

.load-more-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Modal styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background-color: var(--color-background);
  border-radius: 8px;
  width: 90%;
  max-width: 600px;
  max-height: 80vh;
  overflow-y: auto;
  box-shadow: var(--shadow-lg);
  border: 1px solid var(--color-border);
}

.settings-modal {
  max-width: 500px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  border-bottom: 1px solid var(--color-border);
}

.modal-header h3 {
  margin: 0;
}

.close-button {
  background: none;
  border: none;
  cursor: pointer;
  padding: 5px;
  color: var(--color-text-secondary);
}

.close-button:hover {
  color: var(--color-text-primary);
}

.modal-body {
  padding: 15px;
}

.email-info {
  display: flex;
  justify-content: space-between;
  margin-bottom: 15px;
}

.sender-info {
  color: var(--color-text-secondary);
}

.email-date {
  margin-top: 4px;
  color: var(--color-text-tertiary);
}

.email-preview {
  line-height: var(--line-height-normal);
  white-space: pre-wrap;
  color: var(--color-text-primary);
  margin-bottom: 15px;
}

.email-link {
  margin-top: 15px;
  text-align: center;
}

.view-original-link {
  color: var(--color-primary);
  text-decoration: none;
  font-size: var(--font-size-sm);
  display: inline-block;
  padding: 8px 16px;
  border: 1px solid var(--color-primary);
  border-radius: 4px;
  transition: background-color var(--transition-base);
}

.view-original-link:hover {
  background-color: var(--color-primary);
  color: var(--color-text-selected);
}

.open-in-gmail {
  display: flex;
  align-items: center;
  gap: 5px;
  color: var(--color-primary);
  text-decoration: none;
  font-size: var(--font-size-sm);
}

.open-in-gmail:hover {
  text-decoration: underline;
}

/* Form styles */
.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  color: var(--color-text-secondary);
}

.form-group input[type="text"],
.form-group input[type="date"],
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 8px;
  border: 1px solid var(--color-border);
  border-radius: 4px;
  background-color: var(--color-input-background);
  color: var(--color-text-primary);
  font-size: var(--font-size-sm);
}

.form-group input[type="text"]:focus,
.form-group input[type="date"]:focus,
.form-group select:focus,
.form-group textarea:focus {
  border-color: var(--color-primary);
  outline: none;
}

.form-group.checkbox {
  display: flex;
  align-items: center;
  gap: 5px;
}

.form-group.checkbox label {
  margin-bottom: 0;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
}

.cancel-button {
  background-color: var(--color-background-secondary);
  border: 1px solid var(--color-border);
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  color: var(--color-text-primary);
  font-size: var(--font-size-sm);
}

.cancel-button:hover {
  background-color: var(--color-background-tertiary);
}

.submit-button {
  background-color: var(--color-primary);
  color: var(--color-text-selected);
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-size: var(--font-size-sm);
}

.submit-button:hover {
  background-color: var(--color-primary-light);
}

.submit-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.disabled-div {
  opacity: 0.5;
  pointer-events: none;
}

/* Settings styles */
.settings-section {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.setting-item {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding-bottom: 15px;
  border-bottom: 1px solid var(--color-border);
}

.setting-item:last-child {
  border-bottom: none;
}

.setting-label {
  flex: 1;
}

.setting-label h4 {
  margin: 0 0 5px 0;
}

.setting-label p {
  margin: 0;
  color: var(--color-text-tertiary);
}

.toggle-button {
  background: none;
  border: none;
  cursor: pointer;
  padding: 0;
  color: var(--color-text-secondary);
}

.toggle-button .active {
  color: var(--color-primary);
}

.labels-list {
  margin-top: 15px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-height: 200px;
  overflow-y: auto;
  width: 100%;
}

.label-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  border-radius: 4px;
  background-color: var(--color-background-secondary);
  cursor: pointer;
  transition: background-color var(--transition-base);
}

.label-item:hover {
  background-color: var(--color-background-tertiary);
}

.label-item.selected {
  background-color: var(--color-primary-light);
  color: var(--color-text-selected);
}

.check-icon {
  color: var(--color-text-selected);
}

.text-muted {
  color: var(--color-text-tertiary);
}
</style>
