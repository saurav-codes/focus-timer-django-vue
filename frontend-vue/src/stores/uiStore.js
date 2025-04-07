import { defineStore } from 'pinia';
import { useLocalStorage } from '@vueuse/core';
import { ref } from 'vue';

export const useUIStore = defineStore('ui', () => {
  // Use VueUse's useLocalStorage to persist state
  const isBrainDumpCollapsed = useLocalStorage('brain-dump-collapsed', false);
  const isIntegrationSidebarVisible = useLocalStorage('integration-sidebar-visible', false);
  const activeIntegration = useLocalStorage('active-integration', 'calendar');
  const isFilterSidebarVisible = useLocalStorage('filter-sidebar-visible', false);


  // Loading state for infinite scrolling
  const isLoadingMoreColumns = ref(false);

  // Toggle functions
  function toggleBrainDump() {
    isBrainDumpCollapsed.value = !isBrainDumpCollapsed.value;
  }

  function toggleFilterSidebar() {
    isFilterSidebarVisible.value = !isFilterSidebarVisible.value;
  }

  function toggleIntegrationSidebar() {
    isIntegrationSidebarVisible.value = !isIntegrationSidebarVisible.value;
  }

  function setActiveIntegration(integration) {
    activeIntegration.value = integration;
  }

  function setLoadingMoreColumns(isLoading) {
    isLoadingMoreColumns.value = isLoading;
  }

  return {
    isBrainDumpCollapsed,
    isIntegrationSidebarVisible,
    activeIntegration,
    isLoadingMoreColumns,
    isFilterSidebarVisible,
    toggleBrainDump,
    toggleIntegrationSidebar,
    setActiveIntegration,
    setLoadingMoreColumns,
    toggleFilterSidebar
  };
});