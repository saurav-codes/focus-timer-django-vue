// Utils to convert backend task objects into FullCalendar event objects
// Each function is kept tiny so that it can be tree-shaken in production builds.
// If your backend adds / removes fields, adjust the mapping here only.

/**
 * Convert a single task coming from the Django backend to a FullCalendar-compatible event.
 * @param {Object} task Task object from API
 * @returns {Object} FullCalendar event object
 */
export function taskToFcEvent(task) {
  // Use ISO strings directly; FullCalendar accepts them.
  const start = task.start_at || null
  const end = task.end_at || null

  return {
    id: task.id,
    title: task.title,
    start,
    end,
    allDay: false,
    extendedProps: {
      description: task.description,
      status: task.status,
      project: task.project,
      tags: task.tags,
      raw: task, // keep full object for future needs
    },
  }
}

/**
 * Convert an array of tasks.
 * @param {Array<Object>} tasks
 * @returns {Array<Object>} Array of FullCalendar events
 */
export function tasksToFcEvents(tasks = []) {
  return tasks.map(taskToFcEvent)
}
