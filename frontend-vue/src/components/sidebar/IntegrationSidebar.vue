<script setup>
import { computed } from 'vue';
import CalendarIntegration from './integrations/CalendarIntegration.vue';
import GmailIntegration from './integrations/GmailIntegration.vue';
import GithubIntegration from './integrations/GithubIntegration.vue';
import AsanaIntegration from './integrations/AsanaIntegration.vue';
import BacklogIntegration from './integrations/BacklogIntegration.vue';
import ArchivedTasksIntegration from './integrations/ArchivedTasksIntegration.vue';
import { useUIStore } from '../../stores/uiStore'


// Icons from Lucide
import {
  Calendar,
  Mail,
  Github,
  CheckSquare,
  Archive,
  Clock,
  Plus,
  ChevronLeft,
  ChevronRight,
} from 'lucide-vue-next';

// Define available integrations
const integrations = [
  { id: 'calendar', name: 'Calendar', icon: Calendar, component: CalendarIntegration },
  { id: 'gmail', name: 'Gmail', icon: Mail, component: GmailIntegration },
  { id: 'github', name: 'GitHub', icon: Github, component: GithubIntegration },
  { id: 'asana', name: 'Asana', icon: CheckSquare, component: AsanaIntegration },
  { id: 'backlog', name: 'Backlog', icon: Clock, component: BacklogIntegration },
  { id: 'archived', name: 'Archived', icon: Archive, component: ArchivedTasksIntegration },
];

// Use the UI store for integration sidebar visibility and active integration
const uiStore = useUIStore();

const showIntegrationSidebar = computed(() => uiStore.isIntegrationSidebarVisible);

const activeIntegration = computed({
  get: () => uiStore.activeIntegration,
  set: (value) => uiStore.setActiveIntegration(value)
});

// Get current active component
const activeComponent = computed(() => {
  const integration = integrations.find(i => i.id === activeIntegration.value);
  return integration ? integration.component : null;
});

// Handle integration selection
const selectIntegration = (integrationId) => {
  activeIntegration.value = integrationId;
  // if sidebar is not visible, show it
  if (!showIntegrationSidebar.value) {
    uiStore.toggleIntegrationSidebar();
  }
};

const handleintegrationSidebarToggle = () => {
  uiStore.toggleIntegrationSidebar();
};

</script>

<template>
  <div
    class="integration-sidebar"
    @mouseenter="uiStore.setPointerOverIntegration(true)"
    @mouseleave="uiStore.setPointerOverIntegration(false)">
    <!-- Integration Content -->
    <transition name="slide">
      <div v-if="showIntegrationSidebar" class="integration-content">
        <component :is="activeComponent" />
      </div>
    </transition>

    <!-- Integration Icons -->
    <div class="integration-icons">
      <button class="toggle-button" @click="handleintegrationSidebarToggle">
        <component :is="showIntegrationSidebar? ChevronRight : ChevronLeft" size="20" class="toggle-icon" />
      </button>
      <button
        v-for="integration in integrations"
        :key="integration.id"
        class="integration-icon-btn"
        :class="{ 'active': activeIntegration === integration.id }"
        :title="integration.name"
        @click="selectIntegration(integration.id)">
        <component :is="integration.icon" size="20" />
      </button>

      <!-- Add new integration button -->
      <button class="integration-icon-btn add-integration" title="Add Integration">
        <Plus size="20" />
      </button>
    </div>
  </div>
</template>

<style scoped>
.integration-sidebar {
  display: flex;
  height: 100%;
  background-color: var(--color-background-secondary, #1e1e2e);
  box-shadow: var(--integration-sidebar-shadow);
}

.integration-icons {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 12px 0;
  border-left: 1px solid var(--color-border, #313244);
  width: 50px;
}

.toggle-button {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  margin-bottom: 8px;
  border-radius: 8px;
  background-color: var(--color-background-tertiary);
  border: 1px solid var(--color-border);
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all 0.2s ease;
}

.toggle-button:hover {
  background-color: var(--color-background-hover, #313244);
  color: var(--color-primary);
  transform: scale(1.05);
}

.toggle-icon {
  transition: transform 0.2s ease;
}

.integration-icon-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  margin: 4px 0;
  border-radius: 8px;
  background: transparent;
  border: none;
  color: var(--color-text-secondary, #a6adc8);
  cursor: pointer;
  transition: all 0.2s ease;
}

.integration-icon-btn:hover {
  background-color: var(--color-background-hover, #313244);
  color: var(--color-text, #cdd6f4);
}

.integration-icon-btn.active {
  /* High-contrast background and icon for selected state */
  background-color: var(--color-primary);
  color: var(--color-text-selected);
  /* Add a subtle ring to highlight selection */
  box-shadow: 0 0 0 2px var(--color-primary-light);
}

.add-integration {
  margin-top: 12px;
  border: 1px dashed var(--color-border, #313244);
}

/* Add transition styles */
.slide-enter-active,
.slide-leave-active {
  transition: transform 0.3s ease, opacity 0.3s ease;
}

.slide-enter-from,
.slide-leave-to {
  transform: translateX(20px);
  opacity: 0;
}

.integration-content {
  flex: 1;
  overflow-y: auto;
  width: 280px;
}
</style>
