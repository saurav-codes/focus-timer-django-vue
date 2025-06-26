<script setup>
/**
 * RecurringTaskEditor ⏰
 * ---------------------
 * UI wrapper around the head-less `useRecurrenceRule` composable.  This file is
 * intentionally light: all the heavy-lifting (parsing/generating RRULE strings,
 * syncing `editableTask`, helpers, etc.) lives in the composable so the template
 * can stay declarative.  If you want to tweak the business-logic reach for
 * `useRecurrenceRule.js` – *not* this component.
 */
import { ref, watch } from 'vue'
import { RRule } from 'rrule'
import {
  Calendar,
  LucideRepeat,
  LucideRepeat2,
  LucideMinus,
  LucidePlus,
  CircleDot,
  Clock,
  X,
} from 'lucide-vue-next'
import { useTaskStoreWs } from '../stores/taskStoreWs'
import { useRecurrenceRule } from '../composables/useRecurrenceRule'

const emit = defineEmits(['close-modal'])
const taskStore = useTaskStoreWs()

const props = defineProps({
  task: { type: Object, required: true },
})

// Local editable copy of the task
const editableTask = ref({ ...props.task })

/* ------------------------------------------------------------------
 *  Recurrence-rule composable
 * -----------------------------------------------------------------*/
const {
  frequency,
  interval,
  weekdaysOptions,
  selectedWeekDays,
  count,
  until,
  ruleDescription,
  currentFrequencyLabel,
  frequenciesOptions,
  generated_rrule,
  handleFrequencyOptionClicked,
  toggleWeekday,
  handleEndAfterToggle,
  formatDate,
  assignRecRule,
} = useRecurrenceRule(editableTask)

/* ------------------------------------------------------------------
 *  UI-level state
 * -----------------------------------------------------------------*/
const isOpen = ref(false)
// for first time opening of task modal, open the rec modal too incase
// there is already an rec rule.
watch(editableTask, ()=>{
  if (editableTask.value.recurrence_series?.recurrence_rule) {
    isOpen.value = true
  }
}, {immediate: true})

function toggleRecurringEditor() {
  isOpen.value = !isOpen.value
  if (isOpen.value) {
    // just update rec rule since user
    // we have dedicated buttons for saving
    // rec task series.
    assignRecRule()
  } else {
    // update the backend since user closed
    // rec editor
    if (editableTask.value.recurrence_series?.recurrence_rule) {
      editableTask.value.recurrence_series = null
      taskStore.turnOffRepeat(editableTask.value.id)
    }
  }
}

/* ------------------------------------------------------------------
 *  Backend commit
 * -----------------------------------------------------------------*/
async function commitSeries(scope) {
  try {
    editableTask.value.series_scope = scope;
    editableTask.value.recurrence_series.recurrence_rule = generated_rrule.value;
    await taskStore.updateTaskWs(editableTask.value);
    emit('close-modal');
  } catch (err) {
    /* eslint-disable no-console */
    console.error('Error committing recurring task', err)
  }
}

/* ------------------------------------------------------------------
 *  Keep editableTask synced with incoming prop
 * -----------------------------------------------------------------*/
watch(
  () => props.task,
  (t) => (editableTask.value = { ...t }),
  { deep: true }
)
</script>
<template>
  <!-- Recurring Task Button -->
  <div class="form-group">
    <button class="recurring-button" @click="toggleRecurringEditor">
      <LucideRepeat size="16" />
      Repeat Task
      <CircleDot :class="{ green: Boolean(editableTask.recurrence_series?.recurrence_rule) }" size="16" />
    </button>
  </div>

  <transition name="slide-fade" enter-active-class="animate-in" leave-active-class="animate-out">
    <div v-if="isOpen" class="recurring-task-editor">
      <div class="editor-header">
        <h3 class="editor-title">
          <Calendar size="16" />
          <span>Repeat Task Schedule</span>
        </h3>
        <button class="close-button" @click="toggleRecurringEditor">
          <X size="16" />
        </button>
      </div>

      <div class="editor-content">
        <!-- Recurring Options -->
        <div class="recurring-options">
          <!-- Frequency Selector -->
          <div class="frequency-selector">
            <div
              v-for="option in frequenciesOptions"
              :key="option.value"
              class="frequency-option"
              :class="{ selected: frequency === option.value }"
              @click="handleFrequencyOptionClicked(option)">
              <component :is="option.icon" class="frequency-icon" />
              <span class="frequency-label">{{ option.label }}</span>
            </div>
          </div>

          <!-- Interval Selector -->
          <div class="interval-selector">
            <span>Repeat every</span>
            <div class="interval-controls">
              <button
                class="interval-button"
                :disabled="interval <= 1"
                @click="interval -= 1">
                <LucideMinus :size="16" />
              </button>
              <span class="interval-value">{{ interval }}</span>
              <button
                class="interval-button"
                @click="interval += 1">
                <LucidePlus :size="16" />
              </button>
            </div>
            <span>{{ currentFrequencyLabel }}</span>
          </div>

          <!-- Weekday Selector (only for weekly) -->
          <div v-if="frequency === RRule.WEEKLY" class="weekday-selector">
            <button
              v-for="day in weekdaysOptions"
              :key="day.dayObj.weekday"
              class="weekday-button"
              :class="{ selected: selectedWeekDays.includes(day.dayObj.weekday)}"
              :title="day.fullLabel"
              @click="toggleWeekday(day.dayObj.weekday)">
              {{ day.label }}
            </button>
          </div>

          <!-- End Options -->
          <div class="end-options">
            <div class="end-option-label">
              Ends:
            </div>
            <div class="end-option-choices">
              <label class="end-option">
                <input
                  type="radio"
                  name="end-type"
                  :checked="!count && !until"
                  @change="count = null;until = null;">
                <span>Never</span>
              </label>

              <label class="end-option">
                <input
                  type="radio"
                  name="end-type"
                  :checked="Boolean(count)"
                  @click="handleEndAfterToggle()">
                <span>After</span>
                <input
                  v-if="!!count"
                  v-model.number="count"
                  type="number"
                  min="1"
                  class="small-input">
                <span v-if="!!count">times</span>
              </label>

              <label class="end-option">
                <input
                  type="radio"
                  name="end-type"
                  :checked="!!until"
                  @change="
                    until = until || formatDate(new Date());
                    count = null">
                <span>On</span>
                <input
                  v-if="!!until"
                  v-model="until"
                  type="date"
                  class="date-input">
              </label>
            </div>
          </div>

          <!-- Summary -->
          <div class="rule-summary">
            <Clock size="14" />
            <span>{{ ruleDescription }}</span>
          </div>
          <!-- Recurrence scope buttons -->
          <div v-if="!!editableTask.recurrence_series?.recurrence_rule" class="left-action-btn-group">
            <button class="save-button" @click="commitSeries('single')">
              <LucideRepeat2 :size="16" />
              Save this only
            </button>
            <button class="save-button" @click="commitSeries('future')">
              <LucideRepeat2 :size="16" />
              Save this &amp; generate/regenerate future tasks
            </button>
            <button class="save-button" @click="commitSeries('all')">
              <LucideRepeat2 :size="16" />
              Save this &amp; update All Tasks from this series
            </button>
          </div>
          <div v-else>
            <button class="save-button" @click="commitSeries('future')">
              <LucideRepeat2 :size="16" />
              Generate Recurring Tasks
            </button>
          </div>
        </div>
      </div>
    </div>
  </transition>
</template>

<style scoped>
  .green {
    color: var(--color-success);
    filter: brightness(1.4) saturate(1.3);
    text-shadow: 0 0 3px rgba(0, 255, 0, 0.3);
    animation: pulse 1s infinite;
  }
  @keyframes pulse {
    0% {
      opacity: 1;
    }
    50% {
      opacity: 0.5;
    }
    100% {
      opacity: 1;
    }
  }

  /* Add new styles for recurring task features */
  .recurring-button {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.625rem 1rem;
    border-radius: 0.375rem;
    font-size: var(--font-size-sm);
    font-weight: var(--font-weight-medium);
    background-color: var(--color-background-secondary);
    border: 1px solid var(--color-border);
    cursor: pointer;
    transition: all var(--transition-base);
    color: var(--color-text-primary);
  }

  .recurring-button:hover {
    background-color: var(--color-background-tertiary);
  }

  .recurring-task-editor {
    background-color: var(--color-background);
    border-radius: 0.5rem;
    border: 1px solid var(--color-border);
    margin-top: 0.75rem;
    overflow: hidden;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    max-width: 100%;
  }

  .editor-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.5rem 0.75rem;
    border-bottom: 1px solid var(--color-border);
    background-color: var(--color-background-secondary);
  }

  .editor-title {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: var(--font-size-sm);
    font-weight: var(--font-weight-medium);
    margin: 0;
  }

  .close-button {
    background: transparent;
    border: none;
    color: var(--color-text-tertiary);
    cursor: pointer;
    padding: 0.25rem;
    border-radius: 0.25rem;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .close-button:hover {
    background-color: var(--color-background-tertiary);
    color: var(--color-text-primary);
  }

  .editor-content {
    padding: 0.75rem;
  }

  .recurring-options {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
  }

  .frequency-selector {
    display: flex;
    justify-content: space-between;
    gap: 0.25rem;
    margin-bottom: 0.5rem;
  }

  .frequency-option {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 0.5rem 0.25rem;
    border-radius: 0.375rem;
    border: 1px solid var(--color-border);
    background-color: var(--color-background-secondary);
    color: var(--color-text-secondary);
    cursor: pointer;
    transition: all 0.2s ease;
  }

  .frequency-option.selected {
    background-color: var(--color-primary);
    border-color: var(--color-primary);
    color: var(--color-text-selected);
  }

  .frequency-icon {
    font-size: 1rem;
    margin-bottom: 0.25rem;
  }

  .frequency-label {
    font-size: var(--font-size-xs);
    font-weight: var(--font-weight-medium);
  }

  .interval-selector {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: var(--font-size-sm);
    margin-bottom: 0.5rem;
  }

  .interval-controls {
    display: flex;
    align-items: center;
  }

  .interval-button {
    width: 1.5rem;
    height: 1.5rem;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
    border: 1px solid var(--color-border);
    background-color: var(--color-background-secondary);
    color: var(--color-text-primary);
    cursor: pointer;
  }

  .interval-button:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .interval-value {
    padding: 0 0.5rem;
    font-weight: var(--font-weight-medium);
  }
  .weekday-selector {
    display: flex;
    justify-content: space-between;
    gap: 0.5rem;
    margin: 0.75rem 0;
  }

  .weekday-button {
    flex: 1;
    width: 2.5rem;
    height: 2.5rem;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
    border: 1px solid var(--color-border);
    background-color: var(--color-background-secondary);
    color: var(--color-text-secondary);
    font-size: var(--font-size-xs);
    font-weight: var(--font-weight-medium);
    cursor: pointer;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
    overflow: hidden;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
  }

  .weekday-button:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    border-color: var(--color-primary-light);
  }

  .weekday-button:active {
    transform: translateY(0);
  }

  .weekday-button.selected {
    background-color: var(--color-primary);
    color: white;
    border-color: var(--color-primary);
    box-shadow: 0 0 0 2px var(--color-primary-light);
  }

  .weekday-button.selected:hover {
    background-color: var(--color-primary-dark);
  }

  .weekday-button::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: radial-gradient(circle, rgba(255, 255, 255, 0.2) 0%, rgba(255, 255, 255, 0) 70%);
    opacity: 0;
    transition: opacity 0.3s ease;
  }

  .weekday-button:hover::before {
    opacity: 1;
  }

  .end-options {
    margin-top: 0.5rem;
  }

  .end-option-label {
    font-size: var(--font-size-sm);
    margin-bottom: 0.5rem;
    color: var(--color-text-secondary);
  }

  .end-option-choices {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .end-option {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: var(--font-size-sm);
    cursor: pointer;
  }

  .small-input {
    width: 3rem;
    padding: 0.25rem 0.5rem;
    border-radius: 0.25rem;
    border: 1px solid var(--color-border);
    background-color: var(--color-input-background);
    color: var(--color-text-primary);
  }

  .date-input {
    padding: 0.25rem 0.5rem;
    border-radius: 0.25rem;
    border: 1px solid var(--color-border);
    background-color: var(--color-input-background);
    color: var(--color-text-primary);
  }

  .rule-summary {
    margin-top: 0.75rem;
    padding: 0.5rem 0.75rem;
    background-color: var(--color-background-secondary);
    border-radius: 0.375rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: var(--font-size-xs);
    color: var(--color-text-secondary);
  }

  /* Animation classes */
  .animate-in {
    animation: slideDown 0.1s ease-in;
  }

  .animate-out {
    animation: slideUp 0.1s ease-out;
  }

  @keyframes slideDown {
    from {
      opacity: 0;
    }
    to {
      opacity: 1;
    }
  }

  @keyframes slideUp {
    from {
      opacity: 1;
    }
    to {
      opacity: 0;
    }
  }

  /* Add smooth transitions to interactive elements */
  .frequency-option,
  .interval-button,
  .weekday-button {
    transition: all 0.1s ease;
  }

  .frequency-option:hover {
    transform: translateY(-2px);
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  }

  .interval-button:not(:disabled):hover,
  .weekday-button:not(.selected):hover {
    background-color: var(--color-background-tertiary);
    transform: scale(1.05);
  }

</style>
