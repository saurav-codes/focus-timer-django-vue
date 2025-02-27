<script setup>

import { ref, computed } from 'vue'
import { useDark, useToggle } from "@vueuse/core";
import { useRouter, useRoute } from 'vue-router'
import { Menu, X, SquareDashedKanban, Calendar, LayoutDashboard, Settings, Sun, Moon } from 'lucide-vue-next'

const isExpanded = ref(false)
const dockRef = ref(null)
const router = useRouter()
const x_icon = X
const route = useRoute()
const isDark = useDark()
const toggleDark = useToggle(isDark)

const handleMouseEnter = () => {
  isExpanded.value = true
}

const handleMouseLeave = () => {
  isExpanded.value = false
}

function handleDockItemClick(item) {
  if (item.action) {
    console.log("dock item clicked with action - ", item.action)
    item.action();
  } else {
    console.log("dock item clicked with path - ", item.path)
    router.push(item.path);
  }
}

const themeIcon = computed(() => isDark.value ? Sun : Moon)

const routes = [
  { path: '/kanban-planner', icon: SquareDashedKanban, label: 'Kanban' },
  { path: '/cal-planner', icon: Calendar, label: 'Calendar' },
  { path: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
  { path: '/settings', icon: Settings, label: 'Settings' },
  {
    id: 'theme-toggle',
    label: 'Toggle Theme',
    action: toggleDark
  }
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
            <Menu
              v-if="!isExpanded"
              class="icon" />
            <x_icon v-else class="icon" />
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
.dock {
  position: fixed;
  bottom: 2rem;
  left: 2rem;
  z-index: 50;
}

.dock-container {
  position: relative;
  width: 3rem;
}

.dock-toggle {
  position: relative;
  width: 3rem;
  height: 3rem;
  background-color: var(--dock-background);
  border-radius: 50px;
  cursor: pointer;
  box-shadow: var(--dock-shadow);
}

.toggle-inner {
  position: relative;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.icon-container {
  position: relative;
  width: 1.5rem;
  height: 1.5rem;
}

.icon {
  position: absolute;
  inset: 0;
}

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
  border-radius: 9999px;
  box-shadow: var(--dock-shadow);
  cursor: pointer;
  transition: all 300ms ease-in-out;
}

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
}

.menu-icon.active {
  color: var(--color-primary);
}
</style>
