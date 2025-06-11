import { defineStore } from 'pinia'
import { useWebSocket } from '@vueuse/core'
import { ref, computed, watch } from 'vue'
import { useDateFormat } from '@vueuse/core'
import { useAuthStore } from './authStore'

// Date utilities (from taskStore.js)
const today = new Date()
const addDays = (date, days) => {
  const d = new Date(date)
  d.setDate(d.getDate() + days)
  return d
}
const formatDate = (date) => useDateFormat(date, 'ddd, MMM D').value
const createInitialColumns = () => [
  { tasks: [], date: addDays(today, -1), title: 'Yesterday', dateString: formatDate(addDays(today, -1)) },
  { tasks: [], date: today, title: 'Today', dateString: formatDate(today) },
  { tasks: [], date: addDays(today, 1), title: 'Tomorrow', dateString: formatDate(addDays(today, 1)) },
  {
    tasks: [],
    date: addDays(today, 2),
    title: formatDate(addDays(today, 2)),
    dateString: formatDate(addDays(today, 2)),
  },
]
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

// helper function to format duration
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

export const useTaskStoreWs = defineStore('taskStoreWs', () => {
  // Build WebSocket URL
  const host = import.meta.env.PROD ? 'tymr.online' : 'localhost:8000'
  const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws'
  const wsUrl = computed(() => `${protocol}://${host}/ws/tasks/`)

  // Initialize WebSocket with vueuse
  const {
    status: wsStatus,
    data: wsData,
    send: wsSend,
    open: wsOpen,
    close: wsClose,
  } = useWebSocket(wsUrl, {
    lazy: true,
    autoReconnect: { retries: 12, delay: 5000 },
    heartbeat: { message: 'ping', interval: 30000, pongTimeout: 10000 },
  })

  // Reactive state mirroring taskStore.js
  const status = ref(wsStatus.value) // CONNECTING | OPEN | CLOSED ...
  const kanbanColumns = ref(createInitialColumns())
  const brainDumpTasks = ref([])
  const backlogs = ref([])
  const archivedTasks = ref([])
  const calendarTasks = ref([])
  const projects = ref([])
  const tags = ref([])
  const selectedProjects = ref([]) // selected from filter bar
  const selectedTags = ref([]) // selected from filter bar
  const firstDate = ref(addDays(today, -1))
  const lastDate = ref(addDays(today, 2))
  const minDate = ref(addDays(today, -7))

  // Watch and reflect status
  watch(wsStatus, (v) => {
    status.value = v
  })

  // Handle incoming messages
  watch(wsData, (raw) => {
    if (!raw) return
    let msg
    try {
      msg = JSON.parse(raw.data ?? raw)
    } catch {
      console.error('[WS] invalid JSON:', raw)
      return
    }
    routeMessage(msg)
  })

  function routeMessage(msg) {
    switch (msg.type) {
      case 'tasks_fetched': {
        const p = msg.payload
        console.log('on task fetched, this is payload- ', p)
        kanbanColumns.value = p.kanbanColumns
        brainDumpTasks.value = p.brainDumpTasks
        backlogs.value = p.backlogs
        archivedTasks.value = p.archivedTasks
        calendarTasks.value = p.calendarTasks
        firstDate.value = new Date(p.firstDate)
        lastDate.value = new Date(p.lastDate)
        minDate.value = new Date(p.minDate)
        break
      }
      case 'projects_fetched':
        projects.value = msg.payload
        console.log('on project fetched - ', msg.payload)
        break
      case 'tags_fetched':
        tags.value = msg.payload
        console.log('on tags fetched - ', msg.payload)
        break
      // TODO: handle create/update/delete events here
      default:
        console.warn('[WS] unhandled message type:', msg.type)
    }
  }

  // Generic send helper
  function sendAction(action, payload = {}) {
    if (wsStatus.value === 'OPEN') {
      wsSend(JSON.stringify({ action, payload }))
    } else {
      console.warn('[WS] cannot send, ws status:', wsStatus.value)
    }
  }

  // Exposed actions mirroring taskStore.js
  function initWs() {
    wsOpen()
    const auth = useAuthStore()
    if (auth.isAuthenticated) {
      fetchTasksWs()
      fetchProjectsWs()
      fetchTagsWs()
    }
  }
  function closeWs() {
    wsClose()
  }

  function fetchTasksWs() {
    sendAction('fetch_tasks', {
      firstDate: firstDate.value.toISOString(),
      lastDate: lastDate.value.toISOString(),
      projects: selectedProjects.value,
      tags: selectedTags.value,
    })
  }

  // Add more date columns for infinite scroll
  async function addMoreColumnsForward(c = 3) {
    for (let i = 0; i < c; i++) {
      const nextDate = addDays(lastDate.value, 1)
      kanbanColumns.value.push(createDateColumn(nextDate))
      lastDate.value = nextDate
    }
    // After adding columns, fetch tasks for the new columns
    // Return the promise so the caller knows when it's done
    return fetchTasksWs()
  }

  // Add earlier date columns for backward infinite scroll
  async function addEarlierColumns(count = 3) {
    let added = 0
    for (let i = 0; i < count; i++) {
      const prevDate = addDays(firstDate.value, -1)
      if (prevDate < minDate.value) break
      kanbanColumns.value.unshift(createDateColumn(prevDate))
      firstDate.value = prevDate
      added++
    }
    if (added > 0) {
      // After adding columns, fetch tasks for the new columns
      return fetchTasksWs()
    }
    return Promise.resolve()
  }

  async function createTask(task) {
    // Format duration before sending to API
    const taskWithFormattedDuration = {
      ...task,
      duration: formatDurationForAPI(task.duration),
    }
    return sendAction('create_task', taskWithFormattedDuration)
  }

  async function updateTask(task) {
    // Format duration before sending to API
    const taskWithFormattedDuration = {
      ...task,
      duration: formatDurationForAPI(task.duration),
    }
    return sendAction('update_task', taskWithFormattedDuration)
  }

  async function archiveTask(task) {
    // push task to archive
    task.status = 'ARCHIVED'
    const updated_task = await updateTask(task)
    archivedTasks.value.unshift(updated_task)
  }

  async function taskDroppedToBrainDump(task) {
    task.column_date = null
    task.status = 'BRAINDUMP'
    return await updateTask(task)
  }

  async function updateTaskOrder(tasks_array) {
    // reinitialize order based on their existing order
    tasks_array.forEach((task, index) => {
      task.order = index
    })
    sendAction('update_task_order', tasks_array)
  }

  function fetchProjectsWs() {
    sendAction('fetch_projects')
  }
  function createProjectWs(data) {
    sendAction('create_project', data)
  }
  function deleteProjectWs(id) {
    sendAction('delete_project', { projectId: id })
  }
  function fetchTagsWs() {
    sendAction('fetch_tags')
  }
  function setSelectedProjectsWs(arr) {
    selectedProjects.value = arr
    fetchTasksWs()
  }
  function setSelectedTagsWs(arr) {
    selectedTags.value = arr
    fetchTasksWs()
  }
  function clearFiltersWs() {
    selectedProjects.value = []
    selectedTags.value = []
    fetchTasksWs()
  }
  function addMoreColumnsWs(c = 3) {
    addMoreColumnsForward(c)
  }
  function addEarlierColumnsWs(c = 3) {
    addEarlierColumns(c)
  }
  function toggleCompletionWs(id) {
    sendAction('toggle_completion', { taskId: id })
  }
  function assignProjectWs(tid, pid) {
    sendAction('assign_project', { taskId: tid, projectId: pid })
  }
  function createTaskWs(task) {
    createTask(task)
  }
  function deleteTaskWs(id) {
    sendAction('delete_task', { taskId: id })
  }
  function updateTaskWs(task) {
    updateTask(task)
  }
  function archiveTaskWs(task) {
    archiveTask(task)
  }
  function braindumpTaskWs(task) {
    taskDroppedToBrainDump(task)
  }
  function updateTaskOrderWs(arr) {
    updateTaskOrder(arr)
  }

  return {
    // state
    status,
    kanbanColumns,
    brainDumpTasks,
    backlogs,
    archivedTasks,
    calendarTasks,
    projects,
    tags,
    selectedProjects,
    selectedTags,
    firstDate,
    lastDate,
    minDate,
    // ws url & raw data
    wsUrl,
    wsStatus,
    wsData,
    // actions
    initWs,
    closeWs,
    fetchTasksWs,
    fetchProjectsWs,
    createProjectWs,
    deleteProjectWs,
    fetchTagsWs,
    setSelectedProjectsWs,
    setSelectedTagsWs,
    clearFiltersWs,
    addMoreColumnsWs,
    addEarlierColumnsWs,
    toggleCompletionWs,
    assignProjectWs,
    createTaskWs,
    deleteTaskWs,
    updateTaskWs,
    archiveTaskWs,
    braindumpTaskWs,
    updateTaskOrderWs,
  }
})
