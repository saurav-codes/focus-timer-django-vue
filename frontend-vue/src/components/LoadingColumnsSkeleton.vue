<script setup>
// This component displays a skeleton loading animation for columns
</script>

<template>
  <div class="loading-skeleton-container">
    <div v-for="n in 3" :key="n" class="loading-column-skeleton">
      <div class="column-header-skeleton">
        <div class="title-skeleton pulse" />
        <div class="date-skeleton pulse" />
      </div>
      <div v-for="task in 3" :key="task" class="task-skeleton pulse" />
    </div>
  </div>
</template>

<style scoped>
.loading-skeleton-container {
  display: flex;
  gap: 1rem;
}

.loading-column-skeleton {
  background-color: var(--color-background);
  border: 1px solid var(--color-border);
  border-radius: 0.5rem;
  width: 300px;
  height: 90vh;
  display: flex;
  flex-direction: column;
  padding: 1rem;
}

.column-header-skeleton {
  margin-bottom: 1rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid var(--color-border);
}

.title-skeleton {
  height: 24px;
  width: 60%;
  background-color: var(--color-background-secondary);
  border-radius: 4px;
  margin-bottom: 8px;
}

.date-skeleton {
  height: 16px;
  width: 40%;
  background-color: var(--color-background-secondary);
  border-radius: 4px;
}

.task-skeleton {
  height: 80px;
  background-color: var(--color-background-secondary);
  border-radius: 0.375rem;
  margin-bottom: 0.5rem;
}

/* Pulse animation */
.pulse {
  animation: pulse-animation 1.5s infinite;
}

@keyframes pulse-animation {
  0% {
    opacity: 0.6;
  }
  50% {
    opacity: 0.3;
  }
  100% {
    opacity: 0.6;
  }
}
</style>