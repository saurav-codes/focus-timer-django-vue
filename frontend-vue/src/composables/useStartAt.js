import { ref, watch } from 'vue'

export function useStartAt(editedTask) {
  const startTime = ref('00:00') // HH:MM (local, 24-hour)

  /**
   * Formats a Date or ISO string into a 24-hour HH:MM time string.
   * @private
   * @example
   * _formatTimeToHHMM(new Date('2025-01-01T14:30:00')) // '14:30'
   * _formatTimeToHHMM('2025-01-01T09:15:00Z') // '14:45' (IST)
   * _formatTimeToHHMM() // Current time, e.g. '09:30'
   *
   * @param {Date|string} [dateObj] - Optional Date object or ISO string. Defaults to now.
   * @returns {string} Time in 24-hour format, e.g. '14:30'
   */
  const _formatTimeToHHMM = (dateObj) => {
    // Use current time if no date provided
    if (!dateObj) dateObj = new Date()

    // Ensure we have a Date object (handles both Date instances and ISO strings)
    const d = new Date(dateObj)

    // Format hours and minutes with leading zeros
    return `${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
  }

  /**
   * Updates the task's start_at timestamp based on the current startTime value.
   * @private
   * @example
   * // If startTime is '14:30', updates task.start_at to today at 14:30:00.000Z
   * _setStartTimeOnTask()
   */
  const _setStartTimeOnTask = () => {
    // Split HH:MM into hours and minutes, converting to numbers
    const [hours, minutes] = startTime.value.split(':').map(Number)

    // Create a new date object with current date but override time
    const currentDate = new Date()
    currentDate.setHours(hours, minutes, 0, 0) // Set seconds and ms to 0

    // Update the task's start_at with ISO string
    editedTask.value.start_at = currentDate.toISOString()
  }

  /**
   * Keep the time input in sync with the task's start_at.
   * When the task's start_at changes, update the startTime value.
   */
  watch(
    () => editedTask.value.start_at,
    (val) => {
      if (val) startTime.value = _formatTimeToHHMM(val)
    },
    { immediate: true }
  )
  watch(startTime, _setStartTimeOnTask)

  return { startTime }
}
