import { createApp } from 'vue'
import { createPinia } from 'pinia'
import Vue3Toastify from 'vue3-toastify'
import 'vue3-toastify/dist/index.css'
import router from './router'
import App from './App.vue'
import './assets/main.css'
import { useThemeStore } from './store/theme'

const pinia = createPinia()
const app = createApp(App)

app.use(pinia)
app.use(router)
app.use(Vue3Toastify, {
  autoClose: 3000,
  position: 'top-right',
  theme: 'auto',
  toastClassName: 'amy-toast',
})

const themeStore = useThemeStore(pinia)
themeStore.init()

app.mount('#app')
