import { useDateFormat } from '@vueuse/core'

// Global reference date for today
export const today = new Date()

// Helper function to add or subtract days from a given date
export const addDays = (date, days) => {
  const d = new Date(date)
  d.setDate(d.getDate() + days)
  return d
}

// Consistent date formatting helper (Mon, Jan 1)
export const formatDate = (date) => useDateFormat(date, 'ddd, MMM D').value

// Create a kanban column object for a given date with a human-readable title
export const createDateColumn = (date, title = null) => {
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
        title = formatDate(colDateObj)
      }
    }
  }

  return {
    tasks: [],
    date: new Date(date),
    dateString: formatDate(date),
    title,
  }
}

// Pre-populate the first four kanban columns (Yesterday, Today, Tomorrow, +1 day)
export const createInitialColumns = () => [
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
    const prevDate = addDays(firstDateRef.value, -1)
    if (prevDate < minDateRef.value) break
    kanbanColumnsRef.value.unshift(createDateColumn(prevDate))
    firstDateRef.value = prevDate
    added++
  }
  return added
}
