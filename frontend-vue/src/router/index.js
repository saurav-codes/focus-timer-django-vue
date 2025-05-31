import { createRouter, createWebHistory } from 'vue-router'
import KanbanPlannerView from '../views/KanbanPlanner.vue'
import CalendarPlannerView from '../views/CalendarPlanner.vue'
import DashboardView from '../views/Dashboard.vue'
import SettingsView from '../views/Settings.vue'
import HomePage from '../views/HomePage.vue'
import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'
import PrivacyPolicyView from '../views/PrivacyPolicyView.vue'
import TermsConditionsView from '../views/TermsConditionsView.vue'
import { useAuthStore } from '../stores/authStore'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '',
      name: 'home',
      component: HomePage,
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView,
    },
    {
      path: '/register',
      name: 'register',
      component: RegisterView,
    },
    {
      path: '/privacy-policy',
      name: 'privacy-policy',
      component: PrivacyPolicyView,
    },
    {
      path: '/terms-and-conditions',
      name: 'terms-and-conditions',
      component: TermsConditionsView,
    },
    {
      path: '/kanban-planner',
      name: 'kanban-planner-view',
      component: KanbanPlannerView,
      meta: { requiresAuth: true },
    },
    {
      path: '/cal-planner',
      name: 'cal-planner-view',
      component: CalendarPlannerView,
      meta: { requiresAuth: true },
    },
    {
      path: '/dashboard',
      name: 'dashboard-view',
      component: DashboardView,
      meta: { requiresAuth: true },
    },
    {
      path: '/settings',
      name: 'settings-view',
      component: SettingsView,
      meta: { requiresAuth: true },
    },
  ],
})

// Navigation guard to check authentication for protected routes
router.beforeEach(async (to, from, next) => {
  // Check if the route requires authentication
  const requiresAuth = to.matched.some((record) => record.meta.requiresAuth)

  if (!requiresAuth) {
    // If the route doesn't require auth, allow navigation
    console.log('route does not require auth, proceeding to route', to.path)
    return next()
  }

  // For protected routes, check if user is authenticated
  const authStore = useAuthStore()

  // Initialize auth if needed
  if (authStore.isAuthenticated) {
    console.log('user is authenticated, proceeding to route', to.path)
  } else {
    console.log('user is not authenticated, initializing auth & redirecting to login')
    authStore.initAuth()
    // redirect to login page
    return next({ path: '/login' })
  }
  return next()
})

export default router
