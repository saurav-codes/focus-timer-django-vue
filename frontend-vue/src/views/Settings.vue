<script setup>
  import { useAuthStore } from '../stores/authStore'

  const authStore = useAuthStore()
</script>

<template>
  <div>
    <main>
      <h2>settings will be here</h2>
      <code>{{ authStore.userData }}</code>
      <button @click="authStore.logout">logout</button>
    </main>
  </div>
</template>
