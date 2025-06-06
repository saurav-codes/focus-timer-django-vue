import { defineStore } from 'pinia'
import { useLocalStorage } from '@vueuse/core'
import { ref } from 'vue'

export const useUIStore = defineStore('ui', () => {
  // Use VueUse's useLocalStorage to persist state
  const isBrainDumpCollapsed = useLocalStorage('brain-dump-collapsed', false)
  const isIntegrationSidebarVisible = useLocalStorage('integration-sidebar-visible', false)
  const activeIntegration = useLocalStorage('active-integration', 'calendar')
  const isFilterSidebarVisible = useLocalStorage('filter-sidebar-visible', false)
  const isPointerOverIntegration = ref(false)
  // Multi-theme toggle state (light, dark, minecraft, notion, zed)
  const currentTheme = useLocalStorage('current-theme', 'light')

  // Loading state for infinite scrolling
  const isLoadingMoreColumns = ref(false)
  // Loading state for backward infinite scrolling
  const isLoadingEarlierColumns = ref(false)

  // Toggle functions
  function toggleBrainDump() {
    isBrainDumpCollapsed.value = !isBrainDumpCollapsed.value
  }

  function toggleFilterSidebar() {
    isFilterSidebarVisible.value = !isFilterSidebarVisible.value
  }

  function toggleIntegrationSidebar() {
    isIntegrationSidebarVisible.value = !isIntegrationSidebarVisible.value
  }

  function setActiveIntegration(integration) {
    activeIntegration.value = integration
  }

  // Cycle through themes on each toggle click
  function cycleTheme() {
    const order = ['light', 'dark', 'minecraft', 'notion', 'zed']
    const idx = order.indexOf(currentTheme.value)
    const next = order[(idx + 1) % order.length]
    currentTheme.value = next
  }

  function setLoadingMoreColumns(isLoading) {
    isLoadingMoreColumns.value = isLoading
  }

  function setLoadingEarlierColumns(isLoading) {
    isLoadingEarlierColumns.value = isLoading
  }

  function setPointerOverIntegration(isOver) {
    isPointerOverIntegration.value = isOver
  }

  return {
    isBrainDumpCollapsed,
    isIntegrationSidebarVisible,
    activeIntegration,
    isLoadingMoreColumns,
    isLoadingEarlierColumns,
    isFilterSidebarVisible,
    isPointerOverIntegration,
    toggleBrainDump,
    toggleIntegrationSidebar,
    setActiveIntegration,
    setLoadingMoreColumns,
    setLoadingEarlierColumns,
    toggleFilterSidebar,
    setPointerOverIntegration,
    // Export theme controls
    currentTheme,
    cycleTheme,
  }
})
