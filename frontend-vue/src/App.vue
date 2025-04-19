<script setup>
import { RouterView, useRoute } from 'vue-router'
import FloatingDock from '@/components/FloatingDock.vue'
import NavBar from '@/components/NavBar.vue'
import { computed } from 'vue'

const route = useRoute();

// Determine if the current route is the home page
const isHomePage = computed(() => {
  return route.path === '/';
});

// Determine if the current page is an auth page (login/register)
const isAuthPage = computed(() => {
  return ['/login', '/register'].includes(route.path);
});

// Compute if we should show the floating dock
const showFloatingDock = computed(() => {
  return !isHomePage.value && !isAuthPage.value;
});

// Compute if we should add top padding to account for fixed navbar
const shouldAddTopPadding = computed(() => {
  return !isHomePage.value;
});
</script>

<template>
  <div class="app-container" :class="{ 'with-padding': shouldAddTopPadding }">
    <!-- Don't show navbar on homepage as it has its own header -->
    <NavBar v-if="!isHomePage" />
    <RouterView />
    <FloatingDock v-if="showFloatingDock" />
  </div>
</template>

<style>
.app-container {
  min-height: 100vh;
}

.app-container.with-padding {
  padding-top: 64px; /* Height of the navbar */
}
</style>
