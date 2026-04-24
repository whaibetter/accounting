import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export type ThemeMode = 'system' | 'dark' | 'light'

export const useThemeStore = defineStore('theme', () => {
  const savedTheme = localStorage.getItem('theme_mode') as ThemeMode | null
  const themeMode = ref<ThemeMode>(savedTheme || 'system')

  const isDark = computed(() => {
    if (themeMode.value === 'dark') return true
    if (themeMode.value === 'light') return false
    return window.matchMedia('(prefers-color-scheme: dark)').matches
  })

  function setThemeMode(mode: ThemeMode) {
    themeMode.value = mode
    localStorage.setItem('theme_mode', mode)
    applyTheme()
  }

  function applyTheme() {
    if (isDark.value) {
      document.documentElement.removeAttribute('data-theme')
    } else {
      document.documentElement.setAttribute('data-theme', 'light')
    }
  }

  function initTheme() {
    applyTheme()
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
      if (themeMode.value === 'system') applyTheme()
    })
  }

  return { themeMode, isDark, setThemeMode, initTheme }
})
