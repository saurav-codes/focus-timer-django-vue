<script setup>
import { ref, computed, watch, useTemplateRef} from 'vue';
import { RRule } from 'rrule';
import { Calendar, LucideRepeat, CircleDot, Calendar1, CalendarDays, Clock, X, CalendarRange, CalendarClock } from 'lucide-vue-next';
import Snackbar from './Snackbar.vue';

const snackbarRef = useTemplateRef('snackbarRef');

const props = defineProps({
  value: {
    type: String,
    default: ''
  },
});

const emit = defineEmits(['update:value']);
const isOpen = ref(Boolean(props.value));

const toggleRecurringEditor = () => {
  isOpen.value = !isOpen.value;
  if (isOpen.value === true) {
    // assign a basic rrule if rrule string is not provided
    if (!props.value) {
      frequency.value = RRule.DAILY;
      interval.value = 1;
      updateRule();  // emit a update event with rrule string based on form values
      snackbarRef.value.addSnackbarItem(
        'Task Repeat On',
        'OK',
        () => {},
        () => {},
        1000
      );
    }
  } else {
    // close the editor
    // and remove the recurrence rule
    emit('update:value', null);
    snackbarRef.value.addSnackbarItem(
      'Task Repeat off',
      'OK',
      () => {},
      () => {},
      1000
    );
  }
};

// Frequency options with more user-friendly labels
const frequenciesOptions = [
  { value: RRule.DAILY, label: 'Daily', label2:'Day', icon: CalendarDays },
  { value: RRule.WEEKLY, label: 'Weekly',label2:'Week', icon: CalendarRange },
  { value: RRule.MONTHLY, label: 'Monthly',label2:'Month', icon: CalendarClock },
  { value: RRule.YEARLY, label: 'Yearly', label2:'Year', icon: Calendar1 }
];


function handleFrequencyOptionClicked(option) {
  frequency.value = option.value;
  if (option.value === RRule.WEEKLY) {
    // add initial one weekday by default
    if (selectedWeekDays.value.length === 0) {
      selectedWeekDays.value.push(weekdaysOptions[0].value);
      // changing week day will automatically update rule
      // since we are using watcher on selectedWeekDays
    } else {
      // this means that user already have some frequency options selected
      // so we will just trigger updateRule() here
      updateRule();
    }
  } else {
    // we aren't updating rule on click of frequency option so
    // we will update it now.
    updateRule();
  }
}

// Weekday options
const weekdaysOptions = [
  { value: RRule.MO, label: 'M', fullLabel: 'Monday' },
  { value: RRule.TU, label: 'T', fullLabel: 'Tuesday' },
  { value: RRule.WE, label: 'W', fullLabel: 'Wednesday' },
  { value: RRule.TH, label: 'T', fullLabel: 'Thursday' },
  { value: RRule.FR, label: 'F', fullLabel: 'Friday' },
  { value: RRule.SA, label: 'S', fullLabel: 'Saturday' },
  { value: RRule.SU, label: 'S', fullLabel: 'Sunday' }
];

// Form state variables that will be used to generate RFC string (iCal format)
// These variables work together to create a recurring schedule pattern

// Which type of recurrence: daily (0), weekly (1), monthly (2), or yearly (3)
const frequency = ref(RRule.DAILY);

// How many units of frequency to skip
// Example: interval of 2 with DAILY means "every 2 days"
const interval = ref(1);

// Only used for weekly frequency
// Contains array of selected weekdays (0 = Monday to 6 = Sunday)
// Example: [0,2,4] means "every Monday, Wednesday, and Friday"
const selectedWeekDays = ref([]);

// Two ways to end a recurring pattern (can't use both):
// 1. count: Stop after this many occurrences
// Example: count = 10 means "repeat 10 times then stop"
const count = ref(null);

// 2. until: Stop on this date
// Example: until = "2024-12-31" means "repeat until December 31, 2024"
const until = ref(null);

function getSelectedWeekDays(byweekday) {
  if (!byweekday) return []
  return Array.isArray(byweekday)
    ? byweekday.slice()          // make a shallow copy of the array
    : [byweekday]                // wrap single object in array
}

// Parse existing rule if provided
const parseRule = () => {
  if (!props.value) {
    return;
  }
  // this usually triggers when user open a task card to edit &
  // that task has a recurrence rule
  // this will parse the rule string and assign values to form state variables
  // so that user can see the current recurrence rule in the form
  try {
    const rruleObj = RRule.fromString(props.value);
    // assign frequency based on rule string
    frequency.value = rruleObj.options.freq;
    // assign interval based on rule string
    interval.value = rruleObj.options.interval || 1;

    // assign selectedWeekDays based on rule string
    // Grab the byweekday option from the parsed rule
    const byweekday = rruleObj.options.byweekday;
    selectedWeekDays.value = getSelectedWeekDays(byweekday);

    count.value = rruleObj.options.count || null;
    until.value = rruleObj.options.until ? formatDate(rruleObj.options.until) : null;
  } catch (e) {
    console.error('Error parsing RRULE:', e);
  }
};

// Format date for until input
const formatDate = (date) => {
  // remove time from date
  // output format: YYYY-MM-DD
  if (!date) return null;
  const d = new Date(date);
  return d.toISOString().split('T')[0];
};

const toggleWeekday = (day) => {
  // either remove or add weekday to selectedWeekDays ref array
  const index = selectedWeekDays.value.indexOf(day);
  if (index === -1) {
    selectedWeekDays.value.push(day);
  } else {
    if (selectedWeekDays.value.length > 1) {
      selectedWeekDays.value.splice(index, 1);
    }
  }
  updateRule();
};

const updateRule = () => {
  // this function Generate RRULE string from form values
  const options = {
    freq: frequency.value,
    interval: interval.value
  };

  // Add weekdays for weekly frequency
  if (frequency.value === RRule.WEEKLY && selectedWeekDays.value.length > 0) {
    options.byweekday = selectedWeekDays.value;
  }

  // Add count or until if specified
  if (count.value) {
    options.count = parseInt(count.value);
  } else if (until.value) {
    options.until = new Date(until.value);
  }

  const rule = new RRule(options);
  const ruleString = rule.toString();
  emit('update:value', ruleString);
};

// Human-readable description of the rule
const ruleDescription = computed(() => {
  if (!props.value) {
    return 'No Repeat Schedule';
  }
  try {
    const rule = RRule.fromString(props.value);
    return rule.toText();
  } catch (e) {
    console.log(e)
    return 'Invalid recurrence rule';
  }
});

// Get current frequency label
const currentFrequencyLabel = computed(() => {
  const found = frequenciesOptions.find(f => f.value === frequency.value);
  const label = found? found.label2 : 'Daily';
  if (interval.value > 1 && label) {
    return label +'s';
  }
  return label;
});

function handleEndAfterToggle() {
  // user have just clicked on end after radio button
  // so we will set count to 10 as initial value
  // because the visibility of endAfter is controlled by count variable
  if (!count.value) {
    count.value = 10;
  }
  // also set until to null because count and until can't be used together
  // to form a recurrence rule string
  until.value = null;
}

// Initialize form when component mounts or value changes
watch(() => props.value, () => {
  parseRule();
}, { immediate: true, deep: true });

</script>
<template>
  <Snackbar ref="snackbarRef" />
  <!-- Recurring Task Button -->
  <div class="form-group">
    <button
      class="recurring-button"
      @click="toggleRecurringEditor">
      <LucideRepeat size="16" />
      Repeat Task
      <CircleDot :class="{'green': Boolean(props.value)}" size="16" />
    </button>
  </div>

  <transition
    name="slide-fade"
    enter-active-class="animate-in"
    leave-active-class="animate-out">
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
              :class="{ 'selected': frequency === option.value }"
              @click="handleFrequencyOptionClicked(option)">
              <component
                :is="option.icon"
                class="frequency-icon" />
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
                @click="interval -= 1; updateRule()">
                -
              </button>
              <span class="interval-value">{{ interval }}</span>
              <button
                class="interval-button"
                @click="interval += 1; updateRule()">
                +
              </button>
            </div>
            <span>{{ currentFrequencyLabel }}</span>
          </div>

          <!-- Weekday Selector (only for weekly) -->
          <div v-if="frequency === 2" class="weekday-selector">
            <button
              v-for="day in weekdaysOptions"
              :key="day.value.weekday"
              class="weekday-button"
              :class="{ 'selected': selectedWeekDays.includes(day.value.weekday) }"
              :title="day.fullLabel"
              @click="toggleWeekday(day.value.weekday)">
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
                  @change="count = null; until = null; updateRule()">
                <span>Never</span>
              </label>

              <label class="end-option">
                <input
                  type="radio"
                  name="end-type"
                  :checked="Boolean(count)"
                  @click="handleEndAfterToggle">
                <span>After</span>
                <input
                  v-if="!!count"
                  v-model.number="count"
                  type="number"
                  min="1"
                  class="small-input"
                  @change="updateRule()">
                <span v-if="!!count">times</span>
              </label>

              <label class="end-option">
                <input
                  type="radio"
                  name="end-type"
                  :checked="!!until"
                  @change="until = until || formatDate(new Date()); count = null; updateRule()">
                <span>On</span>
                <input
                  v-if="!!until"
                  v-model="until"
                  type="date"
                  class="date-input"
                  @change="updateRule()">
              </label>
            </div>
          </div>

          <!-- Summary -->
          <div class="rule-summary">
            <Clock size="14" />
            <span>{{ ruleDescription }}</span>
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
  0% { opacity: 1; }
  50% { opacity: 0.5; }
  100% { opacity: 1; }
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
  background: radial-gradient(circle, rgba(255,255,255,0.2) 0%, rgba(255,255,255,0) 70%);
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

input {
  color: var(--color-text-primary)
}

</style>
