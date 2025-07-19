<script setup>
import {
  ref,
  onMounted,
  onUnmounted,
  watch
} from 'vue'
import { useGithubStore } from '../../../stores/githubStore'
import { useTaskStoreWs } from '../../../stores/taskStoreWs'
import { useIntervalFn } from '@vueuse/core'
import {
  LucideGithub,
  LucideLink,
  LucideUnlink,
  LucideRefreshCw,
  LucideCheckSquare,
  LucideX,
  LucideExternalLink,
  LucideSettings,
  LucideToggleLeft,
  LucideToggleRight,
  LucideCheck,
  LucideShieldHalf,
  LucideGitPullRequest,
  LucideAlertCircle,
  LucideUser,
  LucideCalendar,
  LucideMessageSquare,
  LucideTag,
  FolderGit2,
} from 'lucide-vue-next'
import Popper from 'vue3-popper'

const githubStore = useGithubStore()
const taskStore = useTaskStoreWs()

const isConnected = ref(false)
const isSyncEnabled = ref(false)
const isLoading = ref(false)
const selectedIssue = ref(null)
const showConvertModal = ref(false)
const showSettingsModal = ref(false)
const taskForm = ref({
  title: '',
  description: '',
  status: 'ON_BOARD',
})

// Simple popper visibility states
const showPopper = ref(false)
const showConnectPopper = ref(false)
const showSettingPopper = ref(false)
const showRefreshPopper = ref(false)
const showConvertToTaskPopper = ref(false)

// Format date to local timezone
const formatLocalTime = (timestamp) => {
  if (!timestamp) return ''

  const date = new Date(timestamp)

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

  // Format based on how recent the issue is
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

// Format full date and time for issue detail view
const formatFullDateTime = (timestamp) => {
  if (!timestamp) return ''
  const date = new Date(timestamp)
  return date.toLocaleString([], {
    weekday: 'short',
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// Auto-refresh issues every 5 minutes
let stopPolling = () => { }

onMounted(async () => {
  isLoading.value = true
  try {
    // Check connection status
    isConnected.value = await githubStore.checkGithubConnection()
    isSyncEnabled.value = githubStore.isSyncEnabled

    // Fetch issues if connected and sync is enabled
    if (isConnected.value && isSyncEnabled.value) {
      await githubStore.fetchIssues()

      // Set up polling for new issues every 5 minutes
      const { pause } = useIntervalFn(() => {
        if (isConnected.value && isSyncEnabled.value) {
          githubStore.resetPagination()
          githubStore.fetchIssues()
        }
      }, 5 * 60 * 1000) // 5 minutes

      stopPolling = pause
    }
  } catch (error) {
    console.error('Error checking GitHub connection:', error)
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
watch(() => githubStore.isSyncEnabled, (newValue) => {
  isSyncEnabled.value = newValue
})

const connectGithub = () => {
  githubStore.connectGithub()
}

const disconnectGithub = async () => {
  isLoading.value = true
  await githubStore.disconnectGithub()
  isConnected.value = false
  isSyncEnabled.value = false
  isLoading.value = false
}

const refreshIssues = async () => {
  isLoading.value = true
  githubStore.resetPagination()
  await githubStore.fetchIssues()
  isLoading.value = false
}

const loadMoreIssues = async () => {
  isLoading.value = true
  await githubStore.loadMoreIssues()
  isLoading.value = false
}

const openIssueDetail = async (issue) => {
  selectedIssue.value = issue

  // Fetch full issue details including timeline
  if (issue.id) {
    const details = await githubStore.getIssueDetails(issue.id)
    if (!details.error) {
      selectedIssue.value = { ...selectedIssue.value, ...details }
    }
  }
}

const closeIssueDetail = () => {
  selectedIssue.value = null
}

const showConvertToTaskModal = (issue) => {
  const repository = issue.repository?.full_name || issue.repository || 'Unknown Repository'
  taskForm.value = {
    title: issue.title,
    description: `GitHub Issue: ${issue.title}\n\nRepository: ${repository}\nIssue #${issue.number}\n\nDescription:\n${issue.body || 'No description provided'}\n\nView on GitHub: ${issue.html_url}`,
    status: 'ON_BOARD',
  }
  showConvertModal.value = true
  selectedIssue.value = issue
}

const closeConvertModal = () => {
  showConvertModal.value = false
}

const openSettingsModal = async () => {
  await githubStore.getSettings()
  showSettingsModal.value = true
}

const closeSettingsModal = () => {
  showSettingsModal.value = false
}

const toggleSync = async () => {
  isLoading.value = true
  await githubStore.toggleSync(!isSyncEnabled.value)
  isSyncEnabled.value = githubStore.isSyncEnabled

  // If sync was enabled, fetch issues
  if (isSyncEnabled.value && !githubStore.githubIssues.length) {
    await githubStore.fetchIssues()
  }

  isLoading.value = false
}

const toggleRepository = async (repositoryId) => {
  const currentRepos = [...githubStore.selectedRepositories]
  const index = currentRepos.indexOf(repositoryId)

  if (index === -1) {
    currentRepos.push(repositoryId)
  } else {
    currentRepos.splice(index, 1)
  }

  isLoading.value = true
  await githubStore.updateRepositories(currentRepos)
  await githubStore.fetchIssues()
  isLoading.value = false
}

const isRepositorySelected = (repositoryId) => {
  return githubStore.selectedRepositories.includes(repositoryId)
}

const convertIssueToTask = async () => {
  if (!selectedIssue.value) return

  isLoading.value = true
  try {
    const result = await githubStore.convertIssueToTask(selectedIssue.value.id, taskForm.value)

    if (result.error) {
      alert(result.error)
      return
    }

    // Refresh tasks if conversion was successful
    taskStore.fetchTasksWs()

    // Close modals
    closeConvertModal()
    closeIssueDetail()
  } catch (error) {
    console.error('Error converting issue to task:', error)
    alert('Failed to convert issue to task')
  } finally {
    isLoading.value = false
  }
}

// Close modal when clicking outside
const handleModalOverlayClick = (event) => {
  // Only close if clicking directly on the overlay, not its children
  if (event.target === event.currentTarget) {
    closeIssueDetail()
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

// Get priority color for issues
const getPriorityColor = (priority) => {
  switch (priority) {
    case 'critical':
    case 'high':
      return 'var(--color-error)'
    case 'medium':
      return 'var(--color-warning)'
    case 'low':
      return 'var(--color-success)'
    default:
      return 'var(--color-text-secondary)'
  }
}
</script>

<template>
  <div class="github-integration">
    <div class="integration-header">
      <div class="left-header">
        <h3>
          <LucideGithub :size="14" />
          GitHub
        </h3>
        <div v-if="isConnected && isSyncEnabled" class="refresh-control">
          <Popper arrow content="Refresh issues" :show="showRefreshPopper">
            <button
              class="refresh-btn"
              :disabled="isLoading"
              @mouseenter="showRefreshPopper = true"
              @mouseleave="showRefreshPopper = false"
              @click="refreshIssues">
              <LucideRefreshCw :size="14" :class="{ 'rotating': isLoading }" />
            </button>
          </Popper>
        </div>
      </div>
      <!-- Connection status controls -->
      <div class="connection-controls">
        <Popper v-if="isConnected" arrow content="Settings" :show="showSettingPopper">
          <button
            class="settings-button"
            :class="{ 'disabled-div': isLoading }"
            @mouseenter="showSettingPopper = true"
            @mouseleave="showSettingPopper = false"
            @click="openSettingsModal">
            <LucideSettings :size="14" />
          </button>
        </Popper>

        <Popper v-if="isConnected" arrow content="Disconnect GitHub Account" :show="showPopper">
          <LucideUnlink
            class="disconnect-button"
            :class="{ 'disabled-div': isLoading }"
            :size="14"
            @mouseover="showPopper = true"
            @mouseleave="showPopper = false"
            @click="disconnectGithub" />
        </Popper>

        <Popper v-else arrow content="Connect GitHub" :show="showConnectPopper">
          <div
            class="github-connect-button"
            :class="{ 'disabled-div': isLoading }"
            @mouseover="showConnectPopper = true"
            @mouseleave="showConnectPopper = false"
            @click="connectGithub">
            <span class="github-icon">GitHub</span>
            <LucideLink :size="10" class="link-icon" />
          </div>
        </Popper>
      </div>
    </div>

    <div class="issues-container">
      <div v-if="isLoading && !githubStore.githubIssues.length" class="loading">
        <div class="spinner" />
        <span class="text-sm">Loading issues...</span>
      </div>

      <div v-else-if="!isConnected" class="not-connected">
        <p class="text-sm">
          Connect your GitHub account to view and manage issues.
        </p>
        <button class="connect-button" @click="connectGithub">
          Connect GitHub
        </button>
      </div>

      <div v-else-if="!isSyncEnabled" class="sync-disabled">
        <p class="text-sm">
          GitHub sync is currently disabled.
        </p>
        <button class="enable-sync-button" @click="toggleSync">
          Enable Sync
        </button>
      </div>

      <div v-else-if="githubStore.githubIssues.length === 0" class="no-issues">
        <p class="text-sm">
          No issues found assigned to you.
        </p>
      </div>

      <div v-else class="issue-list">
        <div
          v-for="issue in githubStore.githubIssues"
          :key="issue.id"
          class="issue-item"
          @click="openIssueDetail(issue)">
          <div class="issue-header">
            <div class="issue-title text-sm font-medium">
              {{ issue.title }}
            </div>
            <div class="time text-xs">
              {{ formatLocalTime(issue.created_at) }}
            </div>
          </div>
          <div class="issue-meta">
            <div class="repository text-xs">
              <FolderGit2 :size="12" />
              {{ issue.repository?.full_name || issue.repository }}
            </div>
            <div class="issue-number text-xs">
              #{{ issue.number }}
            </div>
          </div>
          <div class="issue-labels" v-if="issue.labels && issue.labels.length">
            <span
              v-for="label in issue.labels.slice(0, 3)"
              :key="label.name"
              class="label-tag text-xs"
              :style="{ backgroundColor: `#${label.color}` }">
              {{ label.name }}
            </span>
          </div>
          <div class="issue-preview text-xs">
            {{ issue.body ? issue.body.substring(0, 100) + (issue.body.length > 100 ? '...' : '') : 'No description' }}
          </div>
          <div class="issue-actions" @click.stop>
            <Popper arrow content="Convert to task" :show="showConvertToTaskPopper">
              <button class="action-button" @mouseenter="showConvertToTaskPopper = true" @mouseleave="showConvertToTaskPopper = false" @click="showConvertToTaskModal(issue)">
                <LucideCheckSquare :size="14" />
              </button>
            </Popper>
          </div>
        </div>

        <div v-if="githubStore.pagination.hasMore" class="load-more">
          <button class="load-more-button" :disabled="isLoading" @click="loadMoreIssues">
            <span v-if="isLoading">Loading...</span>
            <span v-else>Load More</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Issue Detail Modal -->
    <div v-if="selectedIssue" class="modal-overlay" @click="handleModalOverlayClick">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3 class="text-lg font-medium">
            {{ selectedIssue.title }}
          </h3>
          <button class="close-button" @click="closeIssueDetail">
            <LucideX :size="18" />
          </button>
        </div>
        <div class="modal-body">
          <div class="issue-info">
            <div class="issue-meta-info text-sm">
              <div><strong>Repository:</strong> {{ selectedIssue.repository?.full_name || selectedIssue.repository }}</div>
              <div><strong>Issue #:</strong> {{ selectedIssue.number }}</div>
              <div><strong>Author:</strong> {{ selectedIssue.user?.login }}</div>
              <div class="issue-date text-xs">
                Created: {{ formatFullDateTime(selectedIssue.created_at) }}
              </div>
              <div v-if="selectedIssue.assignees && selectedIssue.assignees.length" class="assignees">
                <strong>Assignees:</strong>
                <span v-for="assignee in selectedIssue.assignees" :key="assignee.login" class="assignee">
                  <LucideUser :size="12" /> {{ assignee.login }}
                </span>
              </div>
            </div>
            <div class="issue-actions">
              <Popper arrow content="Convert to task">
                <button class="action-button" @click="showConvertToTaskModal(selectedIssue)">
                  <LucideCheckSquare :size="14" />
                </button>
              </Popper>

              <Popper arrow content="Open on GitHub">
                <a :href="selectedIssue.html_url" target="_blank" class="open-in-github">
                  <LucideExternalLink :size="14" />
                  Open on GitHub
                </a>
              </Popper>
            </div>
          </div>

          <div v-if="selectedIssue.labels && selectedIssue.labels.length" class="issue-labels">
            <strong class="text-sm">Labels:</strong>
            <div class="labels-list">
              <span
                v-for="label in selectedIssue.labels"
                :key="label.name"
                class="label-tag"
                :style="{ backgroundColor: `#${label.color}` }">
                {{ label.name }}
              </span>
            </div>
          </div>

          <div class="issue-body text-sm">
            <strong>Description:</strong>
            <div class="issue-content">
              {{ selectedIssue.body || 'No description provided' }}
            </div>
          </div>

          <div v-if="selectedIssue.timeline && selectedIssue.timeline.length" class="issue-timeline">
            <strong class="text-sm">Timeline:</strong>
            <div class="timeline-items">
              <div v-for="item in selectedIssue.timeline" :key="item.id" class="timeline-item">
                <div class="timeline-header">
                  <LucideUser :size="12" />
                  <span class="author">{{ item.actor?.login }}</span>
                  <span class="action">{{ item.event }}</span>
                  <span class="time">{{ formatLocalTime(item.created_at) }}</span>
                </div>
                <div v-if="item.body" class="timeline-body">
                  {{ item.body }}
                </div>
              </div>
            </div>
          </div>

          <div v-if="selectedIssue.pull_requests && selectedIssue.pull_requests.length" class="linked-prs">
            <strong class="text-sm">Linked Pull Requests:</strong>
            <div class="pr-list">
              <div v-for="pr in selectedIssue.pull_requests" :key="pr.id" class="pr-item">
                <LucideGitPullRequest :size="14" />
                <a :href="pr.html_url" target="_blank" class="pr-link">
                  {{ pr.title }} #{{ pr.number }}
                </a>
                <span class="pr-state" :class="pr.state">{{ pr.state }}</span>
              </div>
            </div>
          </div>

          <div class="issue-link">
            <a :href="selectedIssue.html_url" target="_blank" class="view-original-link">
              View original issue on GitHub
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
            Convert Issue to Task
          </h3>
          <button class="close-button" @click="closeConvertModal">
            <LucideX :size="18" />
          </button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="convertIssueToTask">
            <div class="form-group">
              <label for="task-title" class="text-sm">Title</label>
              <input id="task-title" v-model="taskForm.title" type="text" required>
            </div>
            <div class="form-group">
              <label for="task-description" class="text-sm">Description</label>
              <textarea id="task-description" v-model="taskForm.description" rows="6" />
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
          <div class="modal-header-left">
            <h3 class="text-lg font-medium">
              GitHub Settings
            </h3>
            <span class="text-sm text-muted privacy-notice">
              <LucideShieldHalf :size="14" color="green" />
              We only access issues assigned to you.
            </span>
          </div>
          <button class="close-button" @click="closeSettingsModal">
            <LucideX :size="18" />
          </button>
        </div>
        <div class="modal-body">
          <div class="settings-section">
            <div class="setting-item">
              <div class="setting-label">
                <h4 class="text-base font-medium">
                  GitHub Sync
                </h4>
                <p class="text-sm text-muted">
                  Enable or disable GitHub issue synchronization
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
                  Repositories to Sync
                </h4>
                <p class="text-sm text-muted">
                  Select which repositories to sync issues from
                </p>
              </div>
              <div class="repositories-list">
                <div
                  v-for="repo in githubStore.availableRepositories"
                  :key="repo.id"
                  class="repository-item"
                  :class="{ 'selected': isRepositorySelected(repo.id) }"
                  @click="toggleRepository(repo.id)">
                  <FolderGit2 :size="16" />
                  <span class="repo-name">{{ repo.full_name }}</span>
                  <LucideCheck v-if="isRepositorySelected(repo.id)" :size="16" class="check-icon" />
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
  .github-integration {
    padding: 16px;
    height: 100%;
    display: flex;
    flex-direction: column;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  }

  /* Header Styles */
  .integration-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    padding-bottom: 12px;
    border-bottom: 1px solid var(--color-border, #313244);
  }

  .left-header {
    display: flex;
    align-items: center;
    gap: 12px;
  }

  .integration-header h3 {
    margin: 0;
    font-size: 16px;
    font-weight: 600;
    color: var(--color-text, #cdd6f4);
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .refresh-control {
    display: flex;
    align-items: center;
  }

  .refresh-btn {
    background: none;
    border: none;
    padding: 6px;
    border-radius: 6px;
    color: var(--color-text-secondary, #a6adc8);
    cursor: pointer;
    transition: all 0.2s ease;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .refresh-btn:hover {
    background: var(--color-surface, #313244);
    color: var(--color-text, #cdd6f4);
  }

  .refresh-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .rotating {
    animation: spin 1s linear infinite;
  }

  @keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
  }

  /* Connection Controls */
  .connection-controls {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .settings-button,
  .disconnect-button {
    background: none;
    border: none;
    padding: 6px;
    border-radius: 6px;
    color: var(--color-text-secondary, #a6adc8);
    cursor: pointer;
    transition: all 0.2s ease;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .settings-button:hover {
    background: var(--color-surface, #313244);
    color: var(--color-primary, #89b4fa);
  }

  .disconnect-button:hover {
    background: var(--color-error-surface, #f38ba820);
    color: var(--color-error, #f38ba8);
  }

  .github-connect-button {
    display: flex;
    align-items: center;
    gap: 6px;
    background: var(--color-primary, #89b4fa);
    color: var(--color-background, #1e1e2e);
    border: none;
    padding: 8px 12px;
    border-radius: 8px;
    font-size: 12px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s ease;
  }

  .github-connect-button:hover {
    background: var(--color-primary-hover, #74a5f5);
    transform: translateY(-1px);
  }

  .disabled-div {
    opacity: 0.5;
    pointer-events: none;
  }

  /* Issues Container */
  .issues-container {
    flex: 1;
    overflow-y: auto;
    min-height: 0;
  }

  /* Loading State */
  .loading {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 40px;
    gap: 12px;
  }

  .spinner {
    width: 24px;
    height: 24px;
    border: 2px solid var(--color-surface, #313244);
    border-top: 2px solid var(--color-primary, #89b4fa);
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }

  /* Not Connected State */
  .not-connected,
  .sync-disabled,
  .no-issues {
    text-align: center;
    padding: 32px 16px;
    color: var(--color-text-secondary, #a6adc8);
  }

  .connect-button,
  .enable-sync-button {
    background: var(--color-primary, #89b4fa);
    color: var(--color-background, #1e1e2e);
    border: none;
    padding: 10px 20px;
    border-radius: 8px;
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    margin-top: 12px;
    transition: all 0.2s ease;
  }

  .connect-button:hover,
  .enable-sync-button:hover {
    background: var(--color-primary-hover, #74a5f5);
    transform: translateY(-1px);
  }

  /* Issue List */
  .issue-list {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  .issue-item {
    background: var(--color-surface, #313244);
    border: 1px solid var(--color-border, #45475a);
    border-radius: 12px;
    padding: 16px;
    cursor: pointer;
    transition: all 0.2s ease;
    position: relative;
  }

  .issue-item:hover {
    background: var(--color-surface-hover, #45475a);
    border-color: var(--color-primary-dim, #89b4fa40);
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  }

  .issue-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 8px;
    gap: 12px;
  }

  .issue-title {
    font-weight: 500;
    color: var(--color-text, #cdd6f4);
    line-height: 1.4;
    flex: 1;
  }

  .time {
    color: var(--color-text-tertiary, #7f849c);
    font-size: 11px;
    white-space: nowrap;
    margin-top: 2px;
  }

  .issue-meta {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 8px;
  }

  .repository {
    display: flex;
    align-items: center;
    gap: 4px;
    color: var(--color-text-secondary, #a6adc8);
    background: var(--color-background, #1e1e2e);
    padding: 2px 6px;
    border-radius: 4px;
    font-size: 11px;
  }

  .issue-number {
    color: var(--color-text-tertiary, #7f849c);
    font-weight: 500;
  }

  .issue-labels {
    display: flex;
    flex-wrap: wrap;
    gap: 4px;
    margin-bottom: 8px;
  }

  .label-tag {
    padding: 2px 6px;
    border-radius: 4px;
    font-size: 10px;
    font-weight: 500;
    color: #000;
    opacity: 0.9;
  }

  .issue-preview {
    color: var(--color-text-secondary, #a6adc8);
    line-height: 1.4;
    margin-bottom: 8px;
  }

  .issue-actions {
    position: absolute;
    top: 12px;
    right: 12px;
    opacity: 0;
    transition: opacity 0.2s ease;
  }

  .issue-item:hover .issue-actions {
    opacity: 1;
  }

  .action-button {
    background: var(--color-primary, #89b4fa);
    color: var(--color-background, #1e1e2e);
    border: none;
    padding: 6px;
    border-radius: 6px;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.2s ease;
  }

  .action-button:hover {
    background: var(--color-primary-hover, #74a5f5);
    transform: scale(1.1);
  }

  /* Load More */
  .load-more {
    text-align: center;
    padding: 16px;
  }

  .load-more-button {
    background: var(--color-surface, #313244);
    color: var(--color-text, #cdd6f4);
    border: 1px solid var(--color-border, #45475a);
    padding: 10px 20px;
    border-radius: 8px;
    cursor: pointer;
    font-size: 14px;
    transition: all 0.2s ease;
  }

  .load-more-button:hover {
    background: var(--color-surface-hover, #45475a);
    border-color: var(--color-primary, #89b4fa);
  }

  .load-more-button:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  /* Modal Styles */
  .modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.7);
    backdrop-filter: blur(4px);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
    padding: 20px;
  }

  .modal-content {
    background: var(--color-background, #1e1e2e);
    border: 1px solid var(--color-border, #313244);
    border-radius: 12px;
    width: 100%;
    max-width: 600px;
    max-height: 90vh;
    overflow-y: auto;
    animation: modalEnter 0.2s ease-out;
  }

  .settings-modal {
    max-width: 500px;
  }

  @keyframes modalEnter {
    from {
      opacity: 0;
      transform: scale(0.95) translateY(-20px);
    }
    to {
      opacity: 1;
      transform: scale(1) translateY(0);
    }
  }

  .modal-header {
    padding: 24px;
    border-bottom: 1px solid var(--color-border, #313244);
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 16px;
  }

  .modal-header-left {
    flex: 1;
  }

  .modal-header h3 {
    margin: 0 0 4px 0;
    font-size: 18px;
    font-weight: 600;
    color: var(--color-text, #cdd6f4);
  }

  .privacy-notice {
    color: var(--color-success, #a6e3a1);
    display: flex;
    align-items: center;
    gap: 4px;
  }

  .close-button {
    background: none;
    border: none;
    color: var(--color-text-secondary, #a6adc8);
    cursor: pointer;
    padding: 4px;
    border-radius: 4px;
    transition: all 0.2s ease;
  }

  .close-button:hover {
    background: var(--color-surface, #313244);
    color: var(--color-text, #cdd6f4);
  }

  .modal-body {
    padding: 24px;
  }

  /* Issue Detail Modal */
  .issue-info {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 20px;
    gap: 16px;
  }

  .issue-meta-info {
    flex: 1;
  }

  .issue-meta-info > div {
    margin-bottom: 8px;
  }

  .issue-date {
    color: var(--color-text-tertiary, #7f849c);
  }

  .assignees {
    display: flex;
    align-items: center;
    gap: 8px;
    flex-wrap: wrap;
  }

  .assignee {
    display: flex;
    align-items: center;
    gap: 4px;
    background: var(--color-surface, #313244);
    padding: 4px 8px;
    border-radius: 6px;
    font-size: 12px;
  }

  .issue-actions {
    display: flex;
    gap: 8px;
  }

  .open-in-github {
    display: flex;
    align-items: center;
    gap: 6px;
    background: var(--color-surface, #313244);
    color: var(--color-text, #cdd6f4);
    text-decoration: none;
    padding: 8px 12px;
    border-radius: 6px;
    font-size: 12px;
    transition: all 0.2s ease;
  }

  .open-in-github:hover {
    background: var(--color-surface-hover, #45475a);
    color: var(--color-primary, #89b4fa);
  }

  .labels-list {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    margin-top: 8px;
  }

  .issue-body {
    margin: 20px 0;
  }

  .issue-content {
    background: var(--color-surface, #313244);
    padding: 16px;
    border-radius: 8px;
    margin-top: 8px;
    white-space: pre-wrap;
    line-height: 1.5;
  }

  /* Settings Modal */
  .settings-section {
    display: flex;
    flex-direction: column;
    gap: 24px;
  }

  .setting-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 16px;
  }

  .setting-label {
    flex: 1;
  }

  .setting-label h4 {
    margin: 0 0 4px 0;
    color: var(--color-text, #cdd6f4);
  }

  .text-muted {
    color: var(--color-text-secondary, #a6adc8);
  }

  .toggle-button {
    background: none;
    border: none;
    cursor: pointer;
    color: var(--color-text-secondary, #a6adc8);
    transition: all 0.2s ease;
  }

  .toggle-button:hover {
    color: var(--color-text, #cdd6f4);
  }

  .toggle-button .active {
    color: var(--color-success, #a6e3a1);
  }

  .repositories-list {
    max-height: 300px;
    overflow-y: auto;
    border: 1px solid var(--color-border, #313244);
    border-radius: 8px;
    padding: 8px;
  }

  .repository-item {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px;
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.2s ease;
  }

  .repository-item:hover {
    background: var(--color-surface, #313244);
  }

  .repository-item.selected {
    background: var(--color-primary-dim, #89b4fa20);
    color: var(--color-primary, #89b4fa);
  }

  .repo-name {
    flex: 1;
    font-size: 14px;
  }

  .check-icon {
    color: var(--color-success, #a6e3a1);
  }

  /* Form Styles */
  .form-group {
    margin-bottom: 20px;
  }

  .form-group label {
    display: block;
    margin-bottom: 6px;
    font-weight: 500;
    color: var(--color-text, #cdd6f4);
  }

  .form-group input,
  .form-group textarea {
    width: 100%;
    padding: 10px 12px;
    background: var(--color-surface, #313244);
    border: 1px solid var(--color-border, #45475a);
    border-radius: 6px;
    color: var(--color-text, #cdd6f4);
    font-size: 14px;
    transition: all 0.2s ease;
    font-family: inherit;
  }

  .form-group input:focus,
  .form-group textarea:focus {
    outline: none;
    border-color: var(--color-primary, #89b4fa);
    box-shadow: 0 0 0 2px var(--color-primary-dim, #89b4fa20);
  }

  .form-actions {
    display: flex;
    gap: 12px;
    justify-content: flex-end;
    margin-top: 24px;
  }

  .cancel-button {
    background: var(--color-surface, #313244);
    color: var(--color-text, #cdd6f4);
    border: 1px solid var(--color-border, #45475a);
    padding: 10px 20px;
    border-radius: 6px;
    cursor: pointer;
    font-size: 14px;
    transition: all 0.2s ease;
  }

  .cancel-button:hover {
    background: var(--color-surface-hover, #45475a);
  }

  .submit-button {
    background: var(--color-primary, #89b4fa);
    color: var(--color-background, #1e1e2e);
    border: none;
    padding: 10px 20px;
    border-radius: 6px;
    cursor: pointer;
    font-size: 14px;
    font-weight: 500;
    transition: all 0.2s ease;
  }

  .submit-button:hover {
    background: var(--color-primary-hover, #74a5f5);
  }

  .submit-button:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  /* Utility Classes */
  .text-sm {
    font-size: 12px;
  }

  .text-xs {
    font-size: 11px;
  }

  .text-lg {
    font-size: 16px;
  }

  .text-base {
    font-size: 14px;
  }

  .font-medium {
    font-weight: 500;
  }

  .font-semibold {
    font-weight: 600;
  }
</style>
