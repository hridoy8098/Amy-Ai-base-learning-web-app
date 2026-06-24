import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useThemeStore = defineStore('theme', () => {
  const isDark = ref(localStorage.getItem('amy_theme') === 'dark')

  function apply() {
    document.documentElement.setAttribute('data-theme', isDark.value ? 'dark' : 'light')
  }

  function toggle() {
    isDark.value = !isDark.value
    localStorage.setItem('amy_theme', isDark.value ? 'dark' : 'light')
    apply()
  }

  function init() {
    if (!localStorage.getItem('amy_theme')) {
      isDark.value = window.matchMedia('(prefers-color-scheme: dark)').matches
    }
    apply()
  }

  return { isDark, toggle, init }
})
