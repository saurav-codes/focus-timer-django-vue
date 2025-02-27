<script setup>
import { RouterView } from 'vue-router'
import FloatingDock from '@/components/ui/FloatingDock.vue'
</script>

<template>
  <div class="app-container">
    <RouterView />
    <FloatingDock />
  </div>
</template>
