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
import './assets/index.css'
import App from './App.vue'
import router from './router'

const app = createApp(App)

app.use(router)
app.use(createPinia())
app.use(Slicksort)

app.mount('#app')
