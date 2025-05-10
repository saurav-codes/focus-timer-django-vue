<script setup>

import { ref, computed } from 'vue'
import { useDark, useToggle } from "@vueuse/core";
import { useRouter, useRoute } from 'vue-router'
import { Layers, Layers2, SquareDashedKanban, Calendar, LayoutDashboard, Settings, Sun, Moon } from 'lucide-vue-next'

const isExpanded = ref(false)
const dockRef = ref(null)
const router = useRouter()
const route = useRoute()
const isDark = useDark()
const toggleDark = useToggle(isDark)
const closeTimeout = ref(null)

const handleMouseEnter = () => {
  // Clear any existing timeout when mouse enters
  if (closeTimeout.value) {
    clearTimeout(closeTimeout.value)
    closeTimeout.value = null
  }
  isExpanded.value = true
}

const handleMouseLeave = () => {
  // Set a timeout to close the dock after 1 second
  closeTimeout.value = setTimeout(() => {
    isExpanded.value = false
    closeTimeout.value = null
  }, 200) // 1000ms = 1 second delay
}

function handleDockItemClick(item) {
  if (item.action) {
    item.action();
  } else {
    router.push(item.path);
  }
}

const themeIcon = computed(() => isDark.value ? Sun : Moon)

const routes = [
  {
    id: 'theme-toggle',
    label: 'Toggle Theme',
    action: toggleDark
  },
  { path: '/settings', icon: Settings, label: 'Settings' },
  { path: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
  { path: '/cal-planner', icon: Calendar, label: 'Calendar' },
  { path: '/kanban-planner', icon: SquareDashedKanban, label: 'Kanban' },
]

const calculateMenuItemStyle = (index, isExpanded) => {
  return {
    transform: `translateY(${isExpanded ? -(index + 1.9) * 3.5 : 0}rem)`,
    opacity: isExpanded ? 1 : 0
  }
}
</script>

<template>
  <div
    ref="dockRef"
    class="dock"
    @mouseenter="handleMouseEnter"
    @mouseleave="handleMouseLeave">
    <div class="dock-container">
      <!-- Toggle Button -->
      <div
        class="dock-toggle"
        @click="handleMouseEnter">
        <div class="toggle-inner">
          <div class="icon-container">
            <Layers
              v-if="!isExpanded"
              class="icon" />
            <Layers2 v-else class="icon" />
          </div>
        </div>
      </div>

      <!-- Menu Items -->
      <div class="menu-container">
        <template
          v-for="(item, index) in routes"
          :key="item.path || item.id">
          <div
            class="menu-item"
            :title="item.label"
            :class="{ 'active': route.path === item.path }"
            :style="calculateMenuItemStyle(index, isExpanded)"
            @click="handleDockItemClick(item)">
            <div class="menu-item-inner">
              <component
                :is="item.id === 'theme-toggle' ? themeIcon: item.icon"
                class="menu-icon"
                :class="{ 'active': route.path === item.path }" />
            </div>
          </div>
        </template>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Base dock positioning */
.dock {
  position: fixed;
  bottom: 2rem;
  left: 2rem;
  z-index: 4;
}

.dock-container {
  position: relative;
  width: 3rem;
}

/* Toggle button styles */
.dock-toggle {
  position: relative;
  width: 3rem;
  height: 3rem;
  background-color: var(--dock-background);
  border-radius: 50%;
  cursor: pointer;
  box-shadow: var(--dock-shadow);
  transition: transform 0.2s cubic-bezier(0.34, 1.56, 0.64, 1); /* Improved easing for more natural feel */
}

.dock-toggle:hover {
  transform: scale(1.1);
}

.toggle-inner {
  position: relative;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* Icon styling */
.icon-container {
  position: relative;
  width: 1.5rem;
  height: 1.5rem;
}

.icon {
  position: absolute;
  inset: 0;
  transition: transform 0.2s cubic-bezier(0.34, 1.56, 0.64, 1), opacity 0.15s ease;
}

.dock-toggle:hover .icon {
  transform: scale(1.15);
}

/* Menu container and items */
.menu-container {
  position: relative;
  width: 3rem;
}

.menu-item {
  position: absolute;
  left: 0;
  width: 3rem;
  height: 3rem;
  background-color: var(--dock-background);
  border-radius: 50%;
  box-shadow: var(--dock-shadow);
  cursor: pointer;
  /* Separate transitions for different properties for better control */
  transition:
    transform 0.2s cubic-bezier(0.34, 1.56, 0.64, 1),
    opacity 0.3s ease,
    translate 0.3s cubic-bezier(0.25, 1, 0.5, 1);
}

/* Refined hover effect with slightly reduced scale for better usability */


.menu-item-inner {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
}

.menu-icon {
  width: 1.5rem;
  height: 1.5rem;
  color: var(--color-text-secondary);
  transition: transform 0.2s cubic-bezier(0.34, 1.56, 0.64, 1), color 0.2s ease;
}

/* Slightly increase icon size on hover but not as extreme */
.menu-item:hover .menu-icon {
  transform: scale(1.2);
}

/* Active state styling */
.menu-icon.active {
  color: var(--color-primary);
}

.menu-item.active {
  background-color: var(--color-background-tertiary);
}
</style>
