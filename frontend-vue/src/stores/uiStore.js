import { defineStore } from 'pinia';
import { useLocalStorage } from '@vueuse/core';

export const useUIStore = defineStore('ui', () => {
  // Use VueUse's useLocalStorage to persist state
  const isBrainDumpCollapsed = useLocalStorage('brain-dump-collapsed', false);
  const isIntegrationSidebarVisible = useLocalStorage('integration-sidebar-visible', false);
  const activeIntegration = useLocalStorage('active-integration', 'calendar');

  // Toggle functions
  function toggleBrainDump() {
    isBrainDumpCollapsed.value = !isBrainDumpCollapsed.value;
  }

  function toggleIntegrationSidebar() {
    isIntegrationSidebarVisible.value = !isIntegrationSidebarVisible.value;
  }

  function setActiveIntegration(integration) {
    activeIntegration.value = integration;
  }

  return {
    isBrainDumpCollapsed,
    isIntegrationSidebarVisible,
    activeIntegration,
    toggleBrainDump,
    toggleIntegrationSidebar,
    setActiveIntegration
  };
});