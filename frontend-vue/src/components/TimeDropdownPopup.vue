<script setup>
import { ref, useTemplateRef } from 'vue';
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

// Increase/decrease functions with range limits
const incrementHours = () => {
  // TODO: verify this limit later
  if (hours.value < 99) hours.value++;
  handleSave();
};
const decrementHours = () => {
  if (hours.value > 0) hours.value--;
  handleSave();
};
const incrementMinutes = () => {
  if (minutes.value < 59) minutes.value++;
  handleSave();
};
const decrementMinutes = () => {
  if (minutes.value > 0) minutes.value--;
  handleSave();
};

const handleSave = () => {
  // Format duration for display ("1h 30m")
  console.log("saving", hours.value, minutes.value);
  const formatted = `${hours.value}h ${minutes.value}m`;
  emit('save', { hours: hours.value, minutes: minutes.value, formatted });
};

const handleCancel = () => {
  emit('cancel');
};

// When clicking outside the popup, cancel
onClickOutside(popupRef,handleCancel);

</script>

<template>
  <div ref="popupRef" class="time-popup" @click.stop>
    <div class="popup-content">
      <div class="input-section">
        <!-- Hours input with increment/decrement -->
        <div class="input-group">
          <span>Hours</span>
          <ChevronUp class="inc-dec-btn" size="16" @click="incrementHours" />
          <input
            v-model.number="hours"
            type="number"
            min="0"
            max="99"
            @change="handleSave">
          <ChevronDown class="inc-dec-btn" size="16" @click="decrementHours" />
        </div>
        <!-- Minutes input with increment/decrement -->
        <div class="input-group">
          <span>Minutes</span>
          <ChevronUp class="inc-dec-btn" size="16" @click="incrementMinutes" />
          <input
            v-model.number="minutes"
            type="number"
            min="0"
            max="59"
            @change="handleSave">
          <ChevronDown class="inc-dec-btn" size="16" @click="decrementMinutes" />
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
  z-index: 100;
  background: var(--color-background);
  border: 1px solid var(--color-border);
  border-radius: 0.375rem;
  box-shadow: var(--shadow-md);
  padding: 0.5rem;
  width: 120px;
}
.popup-content {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  justify-content: center;
  align-items: center;
}
.input-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.input-group {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.25rem;
  flex-direction: column;
}
.input-group input {
  width: 40px;
  height: 30px;
  text-align: center;
  padding: 0.25rem;
  border: 1px solid var(--color-border);
  border-radius: 0.25rem;
}
/* For Chrome, Safari, Edge, and Opera */
input::-webkit-outer-spin-button,
input::-webkit-inner-spin-button {
  -webkit-appearance: none; /* Removes the default appearance */
  margin: 0; /* Removes the default margin */
}

/* For Firefox */
input[type=number] {
  -moz-appearance: textfield;
}
</style>
