// src/main.js
import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import 'element-plus/theme-chalk/dark/css-vars.css'
import '@/assets/theme.css'
import reveal from '@/directives/reveal'

// 主题初始化：优先读取 localStorage，未设置时跟随系统偏好
const initTheme = () => {
  const saved = localStorage.getItem('theme')
  const prefersDark = window.matchMedia?.('(prefers-color-scheme: dark)').matches
  const isDark = saved ? saved === 'dark' : !!prefersDark
  document.documentElement.classList.toggle('dark', isDark)
}
initTheme()

const app = createApp(App)
app.use(router)
app.use(ElementPlus)
app.directive('reveal', reveal)
app.mount('#app')