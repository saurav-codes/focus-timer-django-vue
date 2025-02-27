import { createRouter, createWebHistory } from 'vue-router'
import KanbanPlannerView from '../views/KanbanPlanner.vue'
import CalendarPlannerView from '../views/CalendarPlanner.vue'
import DashboardView from '@/views/Dashboard.vue'
import SettingsView from '@/views/Settings.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '',
      redirect: '/kanban-planner'
    },
    {
      path: '/kanban-planner',
      name: 'kanban-planner-view',
      component: KanbanPlannerView,
    },
    {
      path: '/cal-planner',
      name: 'cal-planner-view',
      component: CalendarPlannerView,
    },
    {
      path: '/dashboard',
      name: 'dashboard-view',
      component: DashboardView
    },
    {
      path: '/settings',
      name: 'settings-view',
      component: SettingsView
    }
  ]
})

export default router
