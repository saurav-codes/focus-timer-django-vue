// main.js
import '@fontsource/inter/400.css';
import '@fontsource/inter/500.css';
import '@fontsource/inter/600.css';
import '@fontsource/inter/700.css';
import '@fontsource/jetbrains-mono/400.css';
import '@fontsource/jetbrains-mono/700.css';


import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { plugin as Slicksort } from 'vue-slicksort';
import { autoAnimatePlugin } from '@formkit/auto-animate/vue'

import './assets/index.css'
import '@vueform/multiselect/themes/default.css';
import App from './App.vue'
import router from './router'
import { useAuthStore } from './stores/authStore'

const app = createApp(App)
const pinia = createPinia()

app.use(router)
app.use(pinia)
app.use(Slicksort)
app.use(autoAnimatePlugin)

// Initialize auth state
const authStore = useAuthStore(pinia)
authStore.initAuth()

app.mount('#app')
