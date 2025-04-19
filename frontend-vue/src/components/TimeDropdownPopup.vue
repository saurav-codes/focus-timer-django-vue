<script setup>
import { ref, useTemplateRef, onMounted, onUnmounted } from 'vue';
import { onClickOutside } from '@vueuse/core';
import { ChevronUp, ChevronDown} from 'lucide-vue-next';

const props = defineProps({
  // Pass in the current hour and minute (numbers)
  initialHours: { type: Number, default: 0 },
  initialMinutes: { type: Number, default: 0 }
});
const emit = defineEmits(['save', 'cancel']);

const hours = ref(props.initialHours);
const minutes = ref(props.initialMinutes);
const popupRef = useTemplateRef('popupRef');

// Handle keyboard events
const handleKeyDown = (e) => {
  if (e.key === 'Escape') {
    handleCancel();
  }
};

onMounted(() => {
  document.addEventListener('keydown', handleKeyDown);
});

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeyDown);
});

// Increase/decrease functions with range limits
const incrementHours = () => {
  // TODO: verify this limit later
  if (hours.value < 99) hours.value++;
  updateDuration(); // Update but don't close popup
};

const decrementHours = () => {
  if (hours.value > 0) hours.value--;
  updateDuration(); // Update but don't close popup
};

const incrementMinutes = () => {
  if (minutes.value < 59) minutes.value++;
  updateDuration(); // Update but don't close popup
};

const decrementMinutes = () => {
  if (minutes.value > 0) minutes.value--;
  updateDuration(); // Update but don't close popup
};

// Update duration without closing the popup
const updateDuration = () => {
  const formatted = formatDuration(hours.value, minutes.value);

  // Emit save but with a flag indicating it's just an update, not a final save
  emit('save', {
    hours: hours.value,
    minutes: minutes.value,
    formatted,
    keepOpen: true
  });
};

// Format the duration nicely
const formatDuration = (hrs, mins) => {
  return `${hrs}h ${mins}m`;
};

// This is the final save that should close the popup
const handleSave = () => {
  const formatted = formatDuration(hours.value, minutes.value);
  emit('save', {
    hours: hours.value,
    minutes: minutes.value,
    formatted
  });
};

const handleCancel = () => {
  emit('cancel');
};

// When clicking outside the popup, save changes
onClickOutside(popupRef, handleSave);

</script>

<template>
  <div ref="popupRef" class="time-popup" @click.stop>
    <div class="popup-content">
      <div class="popup-header">
        <span>Duration</span>
      </div>
      <div class="input-section">
        <!-- Hours input with increment/decrement -->
        <div class="input-group">
          <span>Hours</span>
          <div class="input-controls">
            <ChevronUp class="inc-dec-btn" size="16" @click="incrementHours" />
            <input
              v-model.number="hours"
              type="number"
              min="0"
              max="99"
              @change="updateDuration">
            <ChevronDown class="inc-dec-btn" size="16" @click="decrementHours" />
          </div>
        </div>
        <!-- Minutes input with increment/decrement -->
        <div class="input-group">
          <span>Minutes</span>
          <div class="input-controls">
            <ChevronUp class="inc-dec-btn" size="16" @click="incrementMinutes" />
            <input
              v-model.number="minutes"
              type="number"
              min="0"
              max="59"
              @change="updateDuration">
            <ChevronDown class="inc-dec-btn" size="16" @click="decrementMinutes" />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.inc-dec-btn {
  cursor: pointer;
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 50px;
}
.inc-dec-btn:hover {
  background-color: var(--color-background-secondary);
}

.time-popup {
  z-index: 1100; /* Ensure it appears above other elements */
  background: var(--color-background);
  border: 1px solid var(--color-border);
  border-radius: 0.375rem;
  box-shadow: var(--shadow-lg);
  width: 200px;
}

.popup-content {
  display: flex;
  flex-direction: column;
}

.popup-header {
  padding: 0.75rem;
  border-bottom: 1px solid var(--color-border);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-secondary);
}

.input-section {
  display: flex;
  padding: 0.75rem;
  gap: 1rem;
  justify-content: space-between;
}

.input-group {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.input-group span {
  font-size: var(--font-size-xs);
  color: var(--color-text-tertiary);
}

.input-controls {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.25rem;
  background-color: var(--color-background-secondary);
  border-radius: 6px;
  padding: 0.5rem;
}

.inc-dec-btn {
  cursor: pointer;
  color: var(--color-text-tertiary);
  padding: 0.25rem;
  border-radius: 4px;
  transition: all 0.2s;
}

.inc-dec-btn:hover {
  color: var(--color-text-primary);
  background-color: var(--color-background-tertiary);
}

.input-group input {
  width: 2.5rem;
  height: 2rem;
  text-align: center;
  border: 1px solid var(--color-border);
  border-radius: 4px;
  background-color: var(--color-background);
  color: var(--color-text-primary);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
}

.input-group input:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 1px var(--color-primary-light);
}

/* Action buttons */
.popup-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  padding: 0.75rem;
  border-top: 1px solid var(--color-border);
}

.action-button {
  padding: 0.375rem 0.75rem;
  border-radius: 4px;
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-medium);
  cursor: pointer;
  transition: all 0.2s;
}

.cancel-button {
  background-color: transparent;
  border: 1px solid var(--color-border);
  color: var(--color-text-secondary);
}

.cancel-button:hover {
  background-color: var(--color-background-secondary);
  color: var(--color-text-primary);
}

.save-button {
  background-color: var(--color-primary);
  border: 1px solid var(--color-primary);
  color: white;
}

.save-button:hover {
  background-color: var(--color-primary-dark, var(--color-primary));
  filter: brightness(90%);
}

/* For Chrome, Safari, Edge, and Opera */
input::-webkit-outer-spin-button,
input::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

/* For Firefox */
input[type=number] {
  -moz-appearance: textfield;
}
</style>
