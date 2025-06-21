<script setup>
  import { RouterView, useRoute } from 'vue-router'
  import FloatingDock from '@/components/FloatingDock.vue'
  import { computed, ref, onMounted } from 'vue'
  import Snackbar from '@/components/Snackbar.vue'

  const route = useRoute()
  const snackbarRef = ref(null)

  onMounted(() => {
    if (snackbarRef.value && typeof snackbarRef.value.addSnackbarItem === 'function') {
      window.__addSnackbar = snackbarRef.value.addSnackbarItem
    }
  })

  // Determine if the current route is the home page
  const isHomePage = computed(() => {
    return route.path === '/'
  })

  // Determine if the current page is an auth page (login/register)
  const isAuthPage = computed(() => {
    return ['/login', '/register'].includes(route.path)
  })

  // Compute if we should show the floating dock
  const showFloatingDock = computed(() => {
    return !isHomePage.value && !isAuthPage.value
  })
</script>

<template>
  <RouterView />
  <Snackbar ref="snackbarRef" />
  <FloatingDock v-if="showFloatingDock" />
</template>
