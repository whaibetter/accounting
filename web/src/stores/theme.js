import { defineStore } from 'pinia'
import { ref, watch } from 'vue'

export const THEMES = {
  warmSun: {
    id: 'warmSun',
    name: '暖阳',
    icon: '☀️',
    colors: {
      '--bg-primary': '#FAF7F2',
      '--bg-card': '#ffffff',
      '--bg-input': '#f5f1ea',
      '--bg-tab': '#f0ebe3',
      '--text-primary': '#3d3325',
      '--text-secondary': '#777',
      '--text-muted': '#b8a488',
      '--text-light': '#a89a82',
      '--accent': '#d4a574',
      '--accent-dark': '#c49463',
      '--accent-light': '#e8c99a',
      '--accent-lighter': '#f0d9b8',
      '--success': '#7cb87c',
      '--danger': '#d47b7b',
      '--border': 'rgba(180, 165, 140, 0.25)',
      '--shadow': '0 1px 4px rgba(160, 140, 110, 0.06)',
      '--shadow-lg': '0 4px 16px rgba(196, 148, 99, 0.15)',
      '--theme-bg': '#fffaf4',
      '--theme-body': '#f5ede0',
    },
  },
  clearSky: {
    id: 'clearSky',
    name: '晴空',
    icon: '🌤️',
    colors: {
      '--bg-primary': '#f4fbff',
      '--bg-card': '#ffffff',
      '--bg-input': '#e8f2fa',
      '--bg-tab': '#e0ecf5',
      '--text-primary': '#253340',
      '--text-secondary': '#667',
      '--text-muted': '#8899aa',
      '--text-light': '#7b92a8',
      '--accent': '#7baed4',
      '--accent-dark': '#6a9dc3',
      '--accent-light': '#9ec5e0',
      '--accent-lighter': '#c0daf0',
      '--success': '#7cb87c',
      '--danger': '#d47b7b',
      '--border': 'rgba(123, 174, 212, 0.2)',
      '--shadow': '0 1px 4px rgba(100, 150, 200, 0.06)',
      '--shadow-lg': '0 4px 16px rgba(107, 157, 195, 0.15)',
      '--theme-bg': '#f4fbff',
      '--theme-body': '#e0ecf5',
    },
  },
  mint: {
    id: 'mint',
    name: '薄荷',
    icon: '🌿',
    colors: {
      '--bg-primary': '#f4fff4',
      '--bg-card': '#ffffff',
      '--bg-input': '#e8f5e8',
      '--bg-tab': '#e0f5e0',
      '--text-primary': '#253325',
      '--text-secondary': '#667766',
      '--text-muted': '#88aa88',
      '--text-light': '#7ba87b',
      '--accent': '#7bd47b',
      '--accent-dark': '#6ac36a',
      '--accent-light': '#9ee09e',
      '--accent-lighter': '#c0f0c0',
      '--success': '#5cb85c',
      '--danger': '#d47b7b',
      '--border': 'rgba(123, 212, 123, 0.2)',
      '--shadow': '0 1px 4px rgba(100, 200, 100, 0.06)',
      '--shadow-lg': '0 4px 16px rgba(106, 195, 106, 0.15)',
      '--theme-bg': '#f4fff4',
      '--theme-body': '#e0f5e0',
    },
  },
  lavender: {
    id: 'lavender',
    name: '薰衣',
    icon: '💜',
    colors: {
      '--bg-primary': '#f4f0ff',
      '--bg-card': '#ffffff',
      '--bg-input': '#ece6f8',
      '--bg-tab': '#ebe0f5',
      '--text-primary': '#302540',
      '--text-secondary': '#776688',
      '--text-muted': '#9988aa',
      '--text-light': '#8b7ba8',
      '--accent': '#a07bd4',
      '--accent-dark': '#8f6ac3',
      '--accent-light': '#b89ee0',
      '--accent-lighter': '#d0c0f0',
      '--success': '#7cb87c',
      '--danger': '#d47b7b',
      '--border': 'rgba(160, 123, 212, 0.2)',
      '--shadow': '0 1px 4px rgba(140, 100, 200, 0.06)',
      '--shadow-lg': '0 4px 16px rgba(143, 106, 195, 0.15)',
      '--theme-bg': '#f4f0ff',
      '--theme-body': '#ebe0f5',
    },
  },
  wheat: {
    id: 'wheat',
    name: '麦浪',
    icon: '🌾',
    colors: {
      '--bg-primary': '#fffff4',
      '--bg-card': '#ffffff',
      '--bg-input': '#f5f5e0',
      '--bg-tab': '#f0f0d8',
      '--text-primary': '#3d3d25',
      '--text-secondary': '#777766',
      '--text-muted': '#aaaa88',
      '--text-light': '#a8a87b',
      '--accent': '#d4c87b',
      '--accent-dark': '#c3b76a',
      '--accent-light': '#e0d89e',
      '--accent-lighter': '#f0ecc0',
      '--success': '#7cb87c',
      '--danger': '#d47b7b',
      '--border': 'rgba(212, 200, 123, 0.25)',
      '--shadow': '0 1px 4px rgba(200, 190, 100, 0.06)',
      '--shadow-lg': '0 4px 16px rgba(195, 183, 106, 0.15)',
      '--theme-bg': '#fffff4',
      '--theme-body': '#f5f5e0',
    },
  },
  berry: {
    id: 'berry',
    name: '莓果',
    icon: '🍓',
    colors: {
      '--bg-primary': '#fff4f4',
      '--bg-card': '#ffffff',
      '--bg-input': '#f5e0e0',
      '--bg-tab': '#f0d8d8',
      '--text-primary': '#402530',
      '--text-secondary': '#886677',
      '--text-muted': '#aa8899',
      '--text-light': '#a87b8b',
      '--accent': '#d47b7b',
      '--accent-dark': '#c36a6a',
      '--accent-light': '#e09e9e',
      '--accent-lighter': '#f0c0c0',
      '--success': '#7cb87c',
      '--danger': '#c36a6a',
      '--border': 'rgba(212, 123, 123, 0.2)',
      '--shadow': '0 1px 4px rgba(200, 100, 100, 0.06)',
      '--shadow-lg': '0 4px 16px rgba(195, 106, 106, 0.15)',
      '--theme-bg': '#fff4f4',
      '--theme-body': '#f5e0e0',
    },
  },
}

export const useThemeStore = defineStore('theme', () => {
  const currentThemeId = ref(localStorage.getItem('theme') || 'warmSun')

  function applyTheme(themeId) {
    const theme = THEMES[themeId]
    if (!theme) return
    const root = document.documentElement
    for (const [key, value] of Object.entries(theme.colors)) {
      root.style.setProperty(key, value)
    }
    currentThemeId.value = themeId
    localStorage.setItem('theme', themeId)
  }

  function initTheme() {
    applyTheme(currentThemeId.value)
  }

  watch(currentThemeId, (newId) => {
    applyTheme(newId)
  })

  return { currentThemeId, applyTheme, initTheme }
})
