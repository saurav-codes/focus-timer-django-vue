import { useDateFormat } from '@vueuse/core'
import { addDays, subDays, startOfToday as today_dt_fn, set, parseISO, add } from 'date-fns'

// Consistent date formatting helper (Mon, Jan 1)
export const formatDate = (date) => useDateFormat(date, 'ddd, MMM D').value

// Create a kanban column object for a given date with a human-readable title
export const createDateColumn = (colDateObj, title = null) => {
  if (!title) {
    if (colDateObj.toDateString() === today_dt_fn().toDateString()) {
      title = 'Today'
    } else {
      const yesterday = subDays(today_dt_fn(), 1)

      const tomorrow = addDays(today_dt_fn(), 1)

      if (colDateObj.toDateString() === yesterday.toDateString()) {
        title = 'Yesterday'
      } else if (colDateObj.toDateString() === tomorrow.toDateString()) {
        title = 'Tomorrow'
      } else {
        title = formatDate(colDateObj)
      }
    }
  }

  return {
    tasks: [],
    date: colDateObj,
    dateString: formatDate(colDateObj),
    title,
  }
}

// Pre-populate the first four kanban columns (Yesterday, today(), Tomorrow, +1 day)
export const createInitialColumns = () => [
  { ...createDateColumn(subDays(today_dt_fn(), 1)) },
  { ...createDateColumn(today_dt_fn()) },
  { ...createDateColumn(addDays(today_dt_fn(), 1)) },
  { ...createDateColumn(addDays(today_dt_fn(), 2)) },
]

// Convert an HH:MM duration string to ISO-8601 (PT#H#M) expected by the API
export const formatDurationForAPI = (duration) => {
  if (!duration) return null

  // If already in ISO duration format, return as-is
  if (duration.includes('P') && duration.includes('T')) {
    return duration
  }

  const [hours, minutes] = duration.split(':').map(Number)
  return `PT${hours}H${minutes}M`
}

// Re-index tasks so their order field matches their array index
export const reInitializeOrder = (tasksArray) => {
  tasksArray.forEach((task, index) => {
    task.order = index
  })
}

/**
 * Upsert tasks into a target array (update if exists, insert if not).
 * This function mutates the targetArray in place for Vue reactivity.
 *
 * @param {Array<Object>} targetArray - The array to update (will be mutated)
 * @param {Array<Object>} newTasks - The tasks to upsert
 * @param {string} [idKey='id'] - The key to use for matching tasks (defaults to 'id')
 *
 * @example
 * // Update existing tasks or add new ones
 * upsertTasks(brainDumpTasks.value, newTasksFromServer)
 *
 * // Use a different key for matching
 * upsertTasks(tasks, newTasks, 'frontend_id')
 */
export const upsertTasks = (targetArray, newTasks, idKey = 'id') => {
  newTasks.forEach((newTask) => {
    const existingIndex = targetArray.findIndex((task) => task[idKey] === newTask[idKey])
    if (existingIndex >= 0) {
      // Update existing task in place to maintain Vue reactivity
      targetArray.splice(existingIndex, 1, newTask)
    } else {
      // Add new task
      targetArray.push(newTask)
    }
  })
}

/**
 * Return a subset of tasks that belong to the supplied status category.
 *
 * This helper is called from `taskStoreWs.js` immediately after the task list
 * is fetched over the WebSocket.  The store keeps separate reactive arrays
 * for each high-level status so we can update the UI in O(1) instead of
 * repeatedly filtering in computed properties.
 *
 * Supported categories (mirrors the backend `status` field):
 *   • 'ON_BOARD'   – Tasks shown in the kanban date columns
 *   • 'ON_CAL'     – Tasks scheduled on the calendar view
 *   • 'BRAINDUMP'  – Un-triaged tasks that live in the Brain-dump list
 *   • 'BACKLOG'    – Accepted tasks that are not yet scheduled
 *   • 'ARCHIVED'   – Archived / completed tasks, kept for reference
 *
 * @param {Array<Object>} tasks    Full list of task objects received from the
 *                                 server.  Each object must have a `status`
 *                                 string property.
 * @param {string}        category One of the status constants shown above.
 *
 * @returns {Array<Object>} A new array containing only the tasks whose
 *                          `status` matches `category`.  If an invalid
 *                          category is supplied the function logs a warning
 *                          and returns an empty array.
 */
export const fetchTaskType = (tasks, category) => {
  switch (category) {
    case 'BRAINDUMP':
      return tasks.filter((t) => t.status === 'BRAINDUMP')
    case 'BACKLOG':
      return tasks.filter((t) => t.status === 'BACKLOG')
    case 'ARCHIVED':
      return tasks.filter((t) => t.status === 'ARCHIVED')
    case 'ON_CAL':
      return tasks.filter((t) => t.status === 'ON_CAL')
    case 'ON_BOARD':
      return tasks.filter((t) => t.status === 'ON_BOARD')
    default:
      console.warn('Invalid task category:', category)
      return []
  }
}

// ---------------------------
// Kanban column helpers
// ---------------------------

// Push `count` new columns after the current lastDate
export const pushForwardColumns = (kanbanColumnsRef, lastDateRef, count = 3) => {
  for (let i = 0; i < count; i++) {
    const nextDate = addDays(lastDateRef.value, 1)
    kanbanColumnsRef.value.push(createDateColumn(nextDate))
    lastDateRef.value = nextDate
  }
}

// Prepend `count` new columns before the current firstDate while respecting minDate
export const prependEarlierColumns = (kanbanColumnsRef, firstDateRef, minDateRef, count = 3) => {
  let added = 0
  for (let i = 0; i < count; i++) {
    const prevDate = subDays(firstDateRef.value, 1)
    if (prevDate < minDateRef.value) break
    kanbanColumnsRef.value.unshift(createDateColumn(prevDate))
    firstDateRef.value = prevDate
    added++
  }
  return added
}

export function getDateStrFromDateObj(dt) {
  const y = dt.getFullYear()
  const m = String(dt.getMonth() + 1).padStart(2, '0')
  const d = String(dt.getDate()).padStart(2, '0')
  return `${y}-${m}-${d}`
}

export function replaceDt(datetime_str_of_task, datetime_obj_of_col) {
  // assign the given date to a given task and keep the time info as it is
  const datetime_obj_of_task = parseISO(datetime_str_of_task)
  const updated_datetime = set(datetime_obj_of_task, {
    year: datetime_obj_of_col.getFullYear(),
    month: datetime_obj_of_col.getMonth(), // getMonth() returns 0-11, which is what date-fns expects
    date: datetime_obj_of_col.getDate(), // Use 'date' parameter name as per date-fns docs
  })
  // Return ISO string to maintain consistency with the rest of the codebase
  return updated_datetime.toISOString()
}

export function calculateEndAt(startAt, duration) {
  if (!startAt || !duration) return ''
  try {
    const startDate = parseISO(startAt)

    const [hours, minutes, seconds] = duration.split(':').map(Number)

    const endDate = add(startDate, {
      hours: hours,
      minutes: minutes,
      seconds: seconds,
    })

    return endDate.toISOString()
  } catch (err) {
    console.log(`error while calculating end_at of task - ${err}`)
    return ''
  }
}
