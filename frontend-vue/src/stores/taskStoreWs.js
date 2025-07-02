import { defineStore } from 'pinia'
import { useWebSocket } from '@vueuse/core'
import { ref, computed, watch } from 'vue'
import { useAuthStore } from './authStore'
import { useTagsProjectStore } from './tagsProjectStore'
import {
  today,
  addDays,
  createInitialColumns,
  formatDurationForAPI,
  fetchTaskType,
  pushForwardColumns,
  prependEarlierColumns,
  reInitializeOrder,
} from '../utils/taskUtils'

export const useTaskStoreWs = defineStore('taskStoreWs', () => {
  // Build WebSocket URL
  const host = import.meta.env.PROD ? import.meta.env.VITE_API_BASE_URL || 'tymr.online' : 'localhost:8000'
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
    immediate: false,
    autoReconnect: { retries: 12, delay: 5000 },
    // heartbeat: { message: 'ping', interval: 30000, pongTimeout: 10000 },
  })

  // Reactive state mirroring taskStore.js
  const status = ref(wsStatus.value) // CONNECTING | OPEN | CLOSED ...
  const kanbanColumns = ref(createInitialColumns())
  const brainDumpTasks = ref([])
  const backlogs = ref([])
  const archivedTasks = ref([])
  // filters are managed centrally in tagsProjectStore
  const tagsProjectStore = useTagsProjectStore()
  const selectedProjects = computed(() => tagsProjectStore.selectedProjects)
  const selectedTags = computed(() => tagsProjectStore.selectedTags)
  const firstDate = ref(addDays(today, -1))
  const lastDate = ref(addDays(today, 2))
  const minDate = ref(addDays(today, -7))

  // Refetch tasks whenever project or tag filters change
  watch(
    [selectedProjects, selectedTags],
    () => {
      fetchTasksWs()
    },
    { deep: true }
  )

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
    if (msg) {
      routeMessage(msg)
    }
  })

  function assignTasksToBoard(tasks) {
    // Distribute tasks to kanban columns
    fetchTaskType(tasks, 'ON_BOARD')
    let boardOrCalTasks = tasks.filter((task) => {
      return task.status === 'ON_BOARD' || task.status === 'ON_CAL'
    })
    kanbanColumns.value.forEach((column) => {
      const filteredTasks = boardOrCalTasks.filter((task) => {
        return task.column_date === column.date.toISOString().split('T')[0]
      })
      // Use direct assignment to ensure reactivity
      column.tasks = [...filteredTasks]
    })
  }

  function _getColumnTasksFromColName(colName, column_date_from_backend = null) {
    switch (colName) {
      case 'BRAINDUMP':
        return brainDumpTasks.value
      case 'BACKLOG':
        return backlogs.value
      case 'ARCHIVED':
        return archivedTasks.value
      case 'ON_BOARD':
      case 'ON_CAL': {
        // now both cases lead to the same block
        if (!column_date_from_backend) {
          console.log('column date is required for search columns with status ON_BOARD')
          return []
        }
        const column = kanbanColumns.value.find(
          (column) => column.date.toISOString().split('T')[0] === column_date_from_backend
        )
        if (!column) {
          console.log('column not found with date - ', column_date_from_backend)
          return []
        }
        return column.tasks
      }
      default:
        console.log('No column found with name - ', colName)
        return []
    }
  }

  function _delete_task_from_all_cols(task_id) {
    kanbanColumns.value.forEach((col) => (col.tasks = col.tasks.filter((t) => t.id !== task_id)))
    brainDumpTasks.value = brainDumpTasks.value.filter((t) => t.id !== task_id)
    backlogs.value = backlogs.value.filter((t) => t.id !== task_id)
    archivedTasks.value = archivedTasks.value.filter((t) => t.id !== task_id)
  }

  function _put_task_on_board(updatedTask) {
    // find the array where we have to place this task
    const colTasksArray = _getColumnTasksFromColName(updatedTask.status, updatedTask.column_date)
    colTasksArray.splice(updatedTask.order, 0, updatedTask)
  }

  // handle msg from backend
  function routeMessage(msg) {
    switch (msg.type) {
      case 'connected': {
        console.info('fetching tasks after rec-d connected msg from backend')
        fetchTasksWs()
        break
      }
      case 'tasks.list': {
        const tasks_list = msg.data
        assignTasksToBoard(tasks_list)
        brainDumpTasks.value = fetchTaskType(tasks_list, 'BRAINDUMP')
        backlogs.value = fetchTaskType(tasks_list, 'BACKLOG')
        archivedTasks.value = fetchTaskType(tasks_list, 'ARCHIVED')
        // TODO: handle other tasks type too
        break
      }
      case 'task.created': {
        const newTask = msg.data
        if (newTask.status === 'BRAINDUMP') {
          // remove the task from braindumpTasks ( generated during optmistic UI updates )
          brainDumpTasks.value = brainDumpTasks.value.filter((t) => t.frontend_id !== newTask.frontend_id)
          // add the task to braindumpTasks ( from backend task data)
          brainDumpTasks.value.unshift(newTask)
          // Update task order since new task is added & other tasks are re-indexed
          updateTaskOrderWs(brainDumpTasks.value)
        } else {
          console.error(
            'task must be created with status as BRAINDUMP but this task got created with status - ',
            newTask.status
          )
          console.error('full task data - ', newTask)
        }
        break
      }
      case 'task.deleted': {
        const id = msg.id
        // purge from all
        _delete_task_from_all_cols(id)
        break
      }
      // tasks.refresh legacy handler
      case 'task.refresh_for_rec': {
        const { deleted = [], created = [] } = msg.data
        // Remove deleted tasks
        deleted.forEach((id) => {
          // remove from all arrays/columns
          _delete_task_from_all_cols(id)
        })
        // Upsert created tasks
        created.forEach((task) => {
          if (task.status === 'ON_BOARD') {
            const column_date = task.column_date
            const column = kanbanColumns.value.find((c) => c.date.toISOString().split('T')[0] === column_date)
            if (column) {
              column.tasks.push(task)
              // update task orders
              console.log('updating all task order for column with title -> ', column.title)
              updateTaskOrderWs(column.tasks)
            }
          }
        })
        break
      }
      case 'full_refresh': {
        fetchTasksWs()
        break
      }
      case 'task_updated':
      case 'task.updated': {
        const updatedTask = msg.data
        _apply_updates_to_task(updatedTask)
        console.log('saving order after updating task')
        const taskColArr = _getColumnTasksFromColName(updatedTask.status, updatedTask.column_date)
        updateTaskOrderWs(taskColArr)
        break
      }
      case 'task.cal_task_updated': {
        console.log('executed task.cal_task_updated')
        const updatedTask = msg.data
        // put this task back to same place where it was.
        _put_task_on_board(updatedTask)
        const colTasksArray = _getColumnTasksFromColName(updatedTask.status, updatedTask.column_date)
        console.log('updating task order after cal_task_updated from backend')
        updateTaskOrderWs(colTasksArray)
        break
      }

      case 'error': {
        // Display error message using global snackbar if available
        let errorMessage = 'Oh no! Something went wrong. trust me bro! everything was okay when i tested it'
        if (typeof window !== 'undefined' && typeof window.__addSnackbar === 'function') {
          window.__addSnackbar(
            `❌ ${errorMessage}`,
            'OK',
            () => {},
            () => {},
            4000
          )
          console.log('error recd from webscoket', msg)
        } else {
          console.error('[WS] Error:', errorMessage)
        }
        break
      }
      default:
        console.warn('[WS] unhandled message type:', msg.type)
    }
  }

  // Generic send helper
  function sendAction(action, payload = {}) {
    if (wsStatus.value === 'OPEN') {
      wsSend(JSON.stringify({ action, payload }))
    } else {
      console.info('[WS] not initialized, ws status yet:', wsStatus.value)
    }
  }

  function _apply_updates_to_task(updated_task) {
    // first find the column where the task is present
    const tasks_array = _getColumnTasksFromColName(updated_task.status, updated_task.column_date)
    const task_index = tasks_array.findIndex((task) => task.id === updated_task.id)
    if (task_index === -1) {
      console.warn("task not found with id so it's a bug - ", updated_task.id)
      return
    }
    // tasks_array[task_index] = updated_task
    tasks_array.splice(task_index, 1, updated_task)
  }

  function pushToArchiveTask(task) {
    archivedTasks.value.unshift(task)
  }

  // Exposed actions mirroring taskStore.js
  function initWs() {
    const auth = useAuthStore()
    auth.verify_auth() // sends a fetchuserdata request to make sure user is logged in
    if (auth.isAuthenticated) {
      console.info('user is authenticated opening ws')
      wsOpen()
    }
  }
  function closeWs() {
    console.info('closing ws')
    wsClose()
  }

  // send msg to backend
  function fetchTasksWs() {
    sendAction('fetch_tasks', {
      start_date: firstDate.value.toISOString().split('T')[0],
      end_date: lastDate.value.toISOString().split('T')[0],
      projects: selectedProjects.value,
      tags: selectedTags.value,
    })
  }

  // Add more date columns for infinite scroll
  async function addMoreColumnsForward(c = 3) {
    pushForwardColumns(kanbanColumns, lastDate, c)
    return fetchTasksWs()
  }

  // Add earlier date columns for backward infinite scroll
  async function addEarlierColumns(count = 3) {
    const added = prependEarlierColumns(kanbanColumns, firstDate, minDate, count)
    if (added > 0) {
      return fetchTasksWs()
    }
    return Promise.resolve()
  }

  async function createTaskWs(task) {
    // Format duration before sending to API
    const taskWithFormattedDuration = {
      ...task,
      duration: formatDurationForAPI(task.duration),
    }
    return sendAction('create_task', taskWithFormattedDuration)
  }

  async function updateTaskWs(task) {
    // Format duration before sending to API
    const taskWithFormattedDuration = {
      ...task,
      duration: formatDurationForAPI(task.duration),
    }
    return sendAction('update_task', taskWithFormattedDuration)
  }

  async function taskDroppedToCal(droppedTask) {
    // Format duration before sending to API
    _delete_task_from_all_cols(droppedTask.id)
    const taskWithFormattedDuration = {
      ...droppedTask,
      duration: formatDurationForAPI(droppedTask.duration),
    }
    return sendAction('task_dropped_to_cal', taskWithFormattedDuration)
  }

  async function turnOffRepeat(task_id) {
    return sendAction('turn_off_repeat', task_id)
  }

  async function archiveTaskWs(task) {
    // push task to archive
    task.status = 'ARCHIVED'
    updateTaskWs(task)
  }

  async function taskDroppedToBrainDumpWs(task) {
    task.column_date = null
    task.start_at = null
    task.end_at = null
    task.status = 'BRAINDUMP'
    updateTaskWs(task)
  }

  async function updateTaskOrderWs(tasks_array) {
    // reinitialize order based on their existing order
    reInitializeOrder(tasks_array)
    sendAction('update_task_order', tasks_array)
  }
  function addMoreColumnsWs(c = 3) {
    addMoreColumnsForward(c)
  }
  function addEarlierColumnsWs(c = 3) {
    addEarlierColumns(c)
  }
  function toggleCompletionWs(task_id) {
    sendAction('toggle_completion', task_id)
  }
  function assignProjectWs(tid, pid) {
    sendAction('assign_project', { task_id: tid, project_id: pid })
  }
  function deleteTaskWs(task_id) {
    sendAction('delete_task', task_id)
    // remove this task from UI
    _delete_task_from_all_cols(task_id)
  }

  return {
    // state
    status,
    kanbanColumns,
    brainDumpTasks,
    backlogs,
    archivedTasks,
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
    addMoreColumnsWs,
    addEarlierColumnsWs,
    toggleCompletionWs,
    assignProjectWs,
    createTaskWs,
    deleteTaskWs,
    updateTaskWs,
    taskDroppedToCal,
    archiveTaskWs,
    updateTaskOrderWs,
    pushToArchiveTask,
    taskDroppedToBrainDumpWs,
    turnOffRepeat,
  }
})
