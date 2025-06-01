<script setup>
import { useRouter } from 'vue-router'
import { ArrowRight } from 'lucide-vue-next'

const router = useRouter()
const goHome = () => {
  router.push('/')
}
</script>

<template>
  <div class="notfound-page">
    <div class="container notfound-container">
      <h1 class="notfound-code">
        404
      </h1>
      <p class="notfound-message">
        Well, this is awkward... Looks like you took a wrong turn into the void.
      </p>
      <button class="cta-button" @click="goHome">
        <ArrowRight class="button-icon" size="16" />
        Take me back home
      </button>
    </div>
  </div>
</template>

<style scoped>
.notfound-page {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100vh;
  background-color: var(--color-background);
  color: var(--color-text-primary);
}

.notfound-container {
  text-align: center;
  max-width: 600px;
  padding: 0 1rem;
}

.notfound-code {
  font-size: 6rem;
  font-weight: var(--font-weight-bold);
  margin: 0;
  color: var(--color-primary);
}

.notfound-message {
  font-size: 1.25rem;
  color: var(--color-text-secondary);
  margin: 1rem 0 2rem;
}

.cta-button {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  background-color: var(--color-primary);
  color: white;
  padding: 0.75rem 1.5rem;
  border-radius: 0.375rem;
  border: none;
  cursor: pointer;
  font-weight: var(--font-weight-medium);
  transition: background-color 0.2s;
}

.cta-button:hover {
  background-color: var(--color-primary-dark);
}

.button-icon {
  color: white;
}
</style>
