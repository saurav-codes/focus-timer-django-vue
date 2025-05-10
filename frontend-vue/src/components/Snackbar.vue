<script setup>
import { ref, watch } from 'vue';
// Import commonly used icons from lucide
import {
  Undo2 as Undo,
  X,
  Check,
  AlertCircle,
  Info
} from 'lucide-vue-next';

const snackbarItems = ref([]);

// Function to determine which icon to use based on action text
const getActionIcon = (actionText) => {
  const text = actionText.toLowerCase();
  switch (text) {
    case 'undo':
      return Undo;
    case 'close':
      return X;
    case 'ok':
    case 'done':
      return Check;
    case 'retry':
      return AlertCircle;
    default:
      return Info;
  }
};

const snackbarItemsTimeoutIds = ref({});
// Watch for changes in the snackbar items array
watch(snackbarItems, (newItems) => {
  // When a new item is added
  if (newItems.length > 0) {
    // Get the latest item
    const latestItem = newItems[newItems.length - 1];
    const timeout = latestItem.timeout;
    // Create a timeout to remove the item after 4 seconds
    const timeoutId = setTimeout(() => {
      // Remove this specific item from the array
      const index = snackbarItems.value.indexOf(latestItem);
      if (index > -1) {
        snackbarItems.value.splice(index, 1);
      };
      // execute final action
      if (latestItem.finalAction) {
       latestItem.finalAction();
      }
      delete snackbarItemsTimeoutIds.value[latestItem.id];
    }, timeout);
    snackbarItemsTimeoutIds.value[latestItem.id] = timeoutId;
  }
}, { deep: true });

// Function to add a new snackbar item
const addSnackbarItem = (message, actionText, buttonAction, finalAction, timeout=4000) => {
  snackbarItems.value.push({
    id: Date.now(), // Unique ID for each snackbar
    message,
    actionText,
    buttonAction,
    finalAction,
    timeout,
  });
};

// Function to remove a specific snackbar item
const removeSnackbarItem = (id) => {
  const index = snackbarItems.value.findIndex(item => item.id === id);
  if (index > -1) {
    snackbarItems.value.splice(index, 1);
  }
};

function executeAction(item) {
  // as of now, this is executing undo action
  item.buttonAction();
  removeSnackbarItem(item.id);
  clearTimeout(snackbarItemsTimeoutIds.value[item.id]);
  delete snackbarItemsTimeoutIds.value[item.id];
}

// Expose these functions to parent components
defineExpose({
  addSnackbarItem,
  removeSnackbarItem
});

</script>

<template>
  <div class="snackbar-container">
    <TransitionGroup name="snackbar">
      <div
        v-for="item in snackbarItems"
        :key="item.id"
        class="snackbar">
        <div class="snackbar-content">
          <span class="message">{{ item.message }}</span>
          <button
            v-if="item.buttonAction"
            class="action-button"
            @click="() => executeAction(item)">
            <component
              :is="getActionIcon(item.actionText)"
              class="action-icon"
              :size="16" />
            {{ item.actionText }}
          </button>
        </div>
      </div>
    </TransitionGroup>
  </div>
</template>

<style scoped>
.snackbar-container {
  position: fixed;
  bottom: 1rem;
  left: 50%;
  transform: translateX(-50%);
  z-index: 6;
  display: flex;
  flex-direction: column-reverse;
  gap: 0.5rem;
}

.snackbar {
  background-color: var(--color-background-secondary);
  color: var(--color-text-primary);
  padding: 0.75rem 1rem;
  border-radius: 0.375rem;
  box-shadow: var(--shadow-md);
  min-width: 300px;
  max-width: 500px;
}

.snackbar-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

.message {
  flex: 1;
  font-size: var(--font-size-sm);
}

.action-button {
  background: transparent;
  border: none;
  color: var(--color-primary);
  font-weight: var(--font-weight-medium);
  cursor: pointer;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  transition: background-color var(--transition-base);
  display: flex;
  align-items: center;
  gap: 0.25rem; /* Space between icon and text */
}

.action-icon {
  /* Optional: add a subtle transition for icon */
  transition: transform var(--transition-base);
}

.action-button:hover .action-icon {
  /* Optional: add a subtle rotation on hover for undo icon */
  transform: scale(1.1);
}

/* Animation */
.snackbar-enter-active,
.snackbar-leave-active {
  transition: all 0.3s ease;
}

.snackbar-enter-from,
.snackbar-leave-to {
  opacity: 0;
  transform: translateY(100%);
}
</style>
