// main.js
import '@fontsource/inter/400.css'
import '@fontsource/inter/500.css'
import '@fontsource/inter/600.css'
import '@fontsource/inter/700.css'
import '@fontsource/jetbrains-mono/400.css'
import '@fontsource/jetbrains-mono/700.css'
import '@fontsource/press-start-2p/400.css'
import '@fontsource/shadows-into-light/400.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { autoAnimatePlugin } from '@formkit/auto-animate/vue'
import Popper from 'vue3-popper'
import { watch } from 'vue'
import { useUIStore } from './stores/uiStore'
import posthogPlugin from './plugins/posthog' //import the plugin.

import './assets/index.css'
import '@vueform/multiselect/themes/default.css'
import App from './App.vue'
import router from './router'
import { useAuthStore } from './stores/authStore'

import * as Sentry from '@sentry/vue'

const app = createApp(App)
const pinia = createPinia()

app.use(router)
app.use(pinia)
app.use(autoAnimatePlugin)

console.log('import.meta.env.PROD', import.meta.env.PROD)
if (import.meta.env.PROD) {
  Sentry.init({
    app,
    dsn: 'https://8e7633e4e6c341b176c2c416d0b5fde1@o4509411491577856.ingest.de.sentry.io/4509411497607248',
    // Setting this option to true will send default PII data to Sentry.
    // For example, automatic IP address collection on events
    sendDefaultPii: true,
  })
  console.log('Sentry initialized in production mode')
} else {
  console.log('Sentry not initialized in development mode')
}

app.component('Popper', Popper)

// Initialize auth state
const authStore = useAuthStore(pinia)
authStore.initAuth()

// Initialize and watch theme changes
const uiStore = useUIStore(pinia)
watch(
  () => uiStore.currentTheme,
  (theme) => {
    const root = document.documentElement
    // Remove all theme classes
    root.classList.remove('dark', 'theme-minecraft', 'theme-notion', 'theme-zed')
    if (theme === 'dark') {
      root.classList.add('dark')
    } else if (theme && theme !== 'light') {
      root.classList.add(`theme-${theme}`)
    }
  },
  { immediate: true }
)

app.use(posthogPlugin) //install the plugin
app.mount('#app')
