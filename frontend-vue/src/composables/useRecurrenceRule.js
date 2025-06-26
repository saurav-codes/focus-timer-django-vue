import { ref, computed, watch } from 'vue'
import { RRule } from 'rrule'
import { CalendarDays, CalendarRange, CalendarClock, Calendar1 } from 'lucide-vue-next'

/**
 * A **head-less** module that encapsulates *all* recurrence-rule logic for a
 * task.  Give it a `ref` to the task you are editing and it will:
 *  • expose reactive state (`frequency`, `interval`, `selectedWeekDays`, …) that
 *    your component can bind to inputs.
 *  • keep `task.recurrence_rule` in sync with the UI by generating an RFC-5545
 *    RRULE string whenever something changes.
 *  • watch `task.recurrence_rule` & re-populate the UI when the user opens an
 *    already-recurring task for editing.
 *  • expose small helper/handler functions so the consuming component stays
 *    declarative and tiny.
 *
 * Returned values are grouped in three blocks:
 *  • *state* – bind these to form controls
 *  • *derived* – read-only values computed from the state (e.g. `ruleDescription`)
 *  • *handlers* – call these from the template (`@click`, `@input`, …)
 *
 * @param {import('vue').Ref<import('../types').Task>} task  A *reactive*
 *        copy of the task being edited (NOT the Pinia store object).  The
 *        composable will mutate `editableTask.value` directly so remember to
 *        commit or discard it from outside.
 */
export function useRecurrenceRule(task) {
  /* ------------------------------------------------------------------
   * 1. Reactive state used by the editor UI
   * -----------------------------------------------------------------*/
  const frequency = ref(RRule.DAILY)
  const interval = ref(1)

  // Store RRule weekday **instances** so that we can feed them back directly.
  const weekdaysOptions = [
    { dayObj: RRule.MO, label: 'M', fullLabel: 'Monday' },
    { dayObj: RRule.TU, label: 'T', fullLabel: 'Tuesday' },
    { dayObj: RRule.WE, label: 'W', fullLabel: 'Wednesday' },
    { dayObj: RRule.TH, label: 'T', fullLabel: 'Thursday' },
    { dayObj: RRule.FR, label: 'F', fullLabel: 'Friday' },
    { dayObj: RRule.SA, label: 'S', fullLabel: 'Saturday' },
    { dayObj: RRule.SU, label: 'S', fullLabel: 'Sunday' },
  ]

  const selectedWeekDays = ref([]) // Array<Weekday>
  const count = ref(null) // number | null
  const until = ref(null) // YYYY-MM-DD string | null
  const generated_rrule = ref('')

  const frequenciesOptions = [
    { value: RRule.DAILY, label: 'Daily', label2: 'Day', icon: CalendarDays },
    { value: RRule.WEEKLY, label: 'Weekly', label2: 'Week', icon: CalendarRange },
    { value: RRule.MONTHLY, label: 'Monthly', label2: 'Month', icon: CalendarClock },
    { value: RRule.YEARLY, label: 'Yearly', label2: 'Year', icon: Calendar1 },
  ]
  /* ------------------------------------------------------------------
   * 2. Helpers
   * -----------------------------------------------------------------*/

  /**
   * Converts a date to YYYY-MM-DD format, suitable for date inputs.
   * @example
   * _formatDate('2025-06-17T14:30:00Z') // '2025-06-17'
   * _formatDate(new Date(2025, 5, 17)) // '2025-06-17'
   * _formatDate(null) // null
   *
   * @param {Date|string|null} date - Date to format
   * @returns {string|null} Formatted date or null if input is falsy
   */
  const formatDate = (date) => {
    if (!date) return null
    // Convert to Date, then to ISO string, and extract YYYY-MM-DD part
    return new Date(date).toISOString().split('T')[0]
  }

  /* ------------------------------------------------------------------
   * 3. RRULE generation & parsing
   * -----------------------------------------------------------------*/
  const rruleObject = computed(() => {
    /** @type {import('rrule').Options} */
    const opts = { freq: frequency.value, interval: interval.value }

    if (frequency.value === RRule.WEEKLY && selectedWeekDays.value.length) {
      opts.byweekday = selectedWeekDays.value
    }

    if (count.value) opts.count = parseInt(count.value)
    else if (until.value) opts.until = new Date(until.value)

    return new RRule(opts)
  })

  const ruleDescription = computed(() => rruleObject.value.toText())
  const rruleString = computed(() => rruleObject.value.toString())

  const currentFrequencyLabel = computed(() => {
    const found = [
      { v: RRule.DAILY, l: 'Day' },
      { v: RRule.WEEKLY, l: 'Week' },
      { v: RRule.MONTHLY, l: 'Month' },
      { v: RRule.YEARLY, l: 'Year' },
    ].find((f) => f.v === frequency.value)
    const base = found ? found.l : 'Day'
    return interval.value > 1 ? base + 's' : base
  })

  /**
   * Updates the task's recurrence_rule with the current rruleString.
   * This is called whenever any recurrence-related state changes.
   * @example
   * // When frequency changes from DAILY to WEEKLY
   * frequency.value = RRule.WEEKLY
   * assignRecRule() // Updates task.recurrence_rule
   */
  const assignRecRule = () => {
    if (!task.value.recurrence_series) {
      task.value.recurrence_series = {}
    }
    // task.value.recurrence_series.recurrence_rule = rruleString.value
    generated_rrule.value = rruleString.value
    // console.log('Recurrence rule assigned:', task.value.recurrence_series.recurrence_rule)
    console.log('Recurrence rule assigned:', generated_rrule.value)
  }

  /**
   * Parses an RRULE string and updates the UI state accordingly.
   * Called when loading an existing recurring task.
   * @private
   * @example
   * // Given a task with a weekly recurrence
   * editableTask.value = { recurrence_rule: 'FREQ=WEEKLY;BYDAY=MO,WE,FR' }
   * _parseRule() // Updates frequency, selectedWeekDays, etc.
   */
  const _parseRule = () => {
    // Skip if no rule to parse
    if (!task.value.recurrence_series?.recurrence_rule) return

    try {
      // Parse the RRULE string into a rule object
      const parsed = RRule.fromString(task.value.recurrence_series.recurrence_rule)

      // Update frequency (DAILY, WEEKLY, etc.)
      frequency.value = parsed.options.freq

      // Default interval to 1 if not specified
      interval.value = parsed.options.interval || 1

      // Handle weekdays selection (can be array, single value, or undefined)
      selectedWeekDays.value = Array.isArray(parsed.options.byweekday)
        ? parsed.options.byweekday.slice() // Clone array to avoid reference issues
        : parsed.options.byweekday
          ? [parsed.options.byweekday] // Wrap single value in array
          : [] // Default to empty array

      // Handle end conditions
      count.value = parsed.options.count || null
      until.value = parsed.options.until ? formatDate(parsed.options.until) : null
    } catch (e) {
      /* eslint-disable no-console */
      console.error('Failed to parse RRULE', e)
    }
  }

  /* ------------------------------------------------------------------
   * 4. UI event handlers exposed to the component
   * -----------------------------------------------------------------*/
  function handleFrequencyOptionClicked(option) {
    frequency.value = option.value
    if (option.value === RRule.WEEKLY && !selectedWeekDays.value.length) {
      selectedWeekDays.value.push(weekdaysOptions[0].dayObj.weekday)
    }
  }

  function toggleWeekday(weekday) {
    const idx = selectedWeekDays.value.indexOf(weekday)
    if (idx === -1) selectedWeekDays.value.push(weekday)
    else selectedWeekDays.value.splice(idx, 1)
  }

  function handleEndAfterToggle() {
    if (!count.value) count.value = 10
    until.value = null
  }

  /* ------------------------------------------------------------------
   * 5. Keep local state synced with the incoming editableTask
   * -----------------------------------------------------------------*/
  // --- React to external changes -------------------------------------------------
  /**
   * Watch for changes to the task's recurrence_rule (e.g., when loading a saved task)
   * and parse the RRULE string to update the UI state.
   */
  watch(
    () => task.value.recurrence_series?.recurrence_rule,
    () => _parseRule(),
    { immediate: true }
  )

  // Whenever the user tweaks *any* primitive that influences the rule we
  // regenerate the RRULE string so `editableTask` is always ready to be saved.
  // Update the task's recurrence rule whenever any of these reactive values change
  watch([frequency, interval, selectedWeekDays, count, until], assignRecRule, { deep: true, immediate: true })

  return {
    /* state */
    frequency,
    interval,
    weekdaysOptions,
    selectedWeekDays,
    count,
    until,
    frequenciesOptions,

    /* derived */
    ruleDescription,
    currentFrequencyLabel,
    rruleString,
    generated_rrule,

    /* handlers */
    handleFrequencyOptionClicked,
    toggleWeekday,
    handleEndAfterToggle,
    formatDate,
    assignRecRule,
  }
}
