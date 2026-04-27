import { defineStore } from 'pinia'
import { ref, watch } from 'vue'

function generateDarkVariant(lightColors, accentHue) {
  return {
    '--bg-primary': shiftToDark(lightColors['--bg-primary'], 0.12),
    '--bg-card': shiftToDark(lightColors['--bg-card'], 0.15),
    '--bg-input': shiftToDark(lightColors['--bg-input'], 0.18),
    '--bg-tab': shiftToDark(lightColors['--bg-tab'], 0.16),
    '--text-primary': '#e8e0d4',
    '--text-secondary': '#a09888',
    '--text-muted': '#706858',
    '--text-light': '#605848',
    '--accent': lightColors['--accent'],
    '--accent-dark': lightColors['--accent-dark'],
    '--accent-light': lightColors['--accent-light'],
    '--accent-lighter': lightColors['--accent-lighter'],
    '--success': '#6db86d',
    '--danger': '#d47b7b',
    '--border': 'rgba(255, 255, 255, 0.08)',
    '--shadow': '0 1px 4px rgba(0, 0, 0, 0.2)',
    '--shadow-lg': '0 4px 16px rgba(0, 0, 0, 0.3)',
    '--theme-bg': shiftToDark(lightColors['--theme-bg'], 0.13),
    '--theme-body': shiftToDark(lightColors['--theme-body'], 0.10),
  }
}

function shiftToDark(hex, factor) {
  if (!hex || hex.startsWith('rgba') || hex.startsWith('rgb')) return '#1a1a1a'
  const r = parseInt(hex.slice(1, 3), 16)
  const g = parseInt(hex.slice(3, 5), 16)
  const b = parseInt(hex.slice(5, 7), 16)
  const nr = Math.round(r * factor)
  const ng = Math.round(g * factor)
  const nb = Math.round(b * factor)
  return `#${nr.toString(16).padStart(2, '0')}${ng.toString(16).padStart(2, '0')}${nb.toString(16).padStart(2, '0')}`
}

export const THEMES = {
  warmSun: {
    id: 'warmSun',
    name: '暖阳',
    icon: '☀️',
    mode: 'light',
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
  warmSunDark: {
    id: 'warmSunDark',
    name: '暖夜',
    icon: '🌙',
    mode: 'dark',
    colors: {
      '--bg-primary': '#1a1714',
      '--bg-card': '#252220',
      '--bg-input': '#2d2926',
      '--bg-tab': '#2a2623',
      '--text-primary': '#e8e0d4',
      '--text-secondary': '#a09888',
      '--text-muted': '#706858',
      '--text-light': '#605848',
      '--accent': '#d4a574',
      '--accent-dark': '#c49463',
      '--accent-light': '#e8c99a',
      '--accent-lighter': '#f0d9b8',
      '--success': '#6db86d',
      '--danger': '#d47b7b',
      '--border': 'rgba(255, 255, 255, 0.08)',
      '--shadow': '0 1px 4px rgba(0, 0, 0, 0.2)',
      '--shadow-lg': '0 4px 16px rgba(0, 0, 0, 0.3)',
      '--theme-bg': '#1e1b18',
      '--theme-body': '#2a2623',
    },
  },
  clearSky: {
    id: 'clearSky',
    name: '晴空',
    icon: '🌤️',
    mode: 'light',
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
  clearSkyDark: {
    id: 'clearSkyDark',
    name: '星夜',
    icon: '🌌',
    mode: 'dark',
    colors: {
      '--bg-primary': '#141a22',
      '--bg-card': '#1e2430',
      '--bg-input': '#252c38',
      '--bg-tab': '#222830',
      '--text-primary': '#d4e0ec',
      '--text-secondary': '#8899aa',
      '--text-muted': '#5a6a7a',
      '--text-light': '#4a5a6a',
      '--accent': '#7baed4',
      '--accent-dark': '#6a9dc3',
      '--accent-light': '#9ec5e0',
      '--accent-lighter': '#c0daf0',
      '--success': '#6db86d',
      '--danger': '#d47b7b',
      '--border': 'rgba(255, 255, 255, 0.08)',
      '--shadow': '0 1px 4px rgba(0, 0, 0, 0.25)',
      '--shadow-lg': '0 4px 16px rgba(0, 0, 0, 0.35)',
      '--theme-bg': '#161c26',
      '--theme-body': '#222830',
    },
  },
  mint: {
    id: 'mint',
    name: '薄荷',
    icon: '🌿',
    mode: 'light',
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
  mintDark: {
    id: 'mintDark',
    name: '深林',
    icon: '🌲',
    mode: 'dark',
    colors: {
      '--bg-primary': '#141e14',
      '--bg-card': '#1e281e',
      '--bg-input': '#253025',
      '--bg-tab': '#222c22',
      '--text-primary': '#d4e8d4',
      '--text-secondary': '#88aa88',
      '--text-muted': '#5a7a5a',
      '--text-light': '#4a6a4a',
      '--accent': '#7bd47b',
      '--accent-dark': '#6ac36a',
      '--accent-light': '#9ee09e',
      '--accent-lighter': '#c0f0c0',
      '--success': '#6db86d',
      '--danger': '#d47b7b',
      '--border': 'rgba(255, 255, 255, 0.08)',
      '--shadow': '0 1px 4px rgba(0, 0, 0, 0.25)',
      '--shadow-lg': '0 4px 16px rgba(0, 0, 0, 0.35)',
      '--theme-bg': '#161e16',
      '--theme-body': '#222c22',
    },
  },
  lavender: {
    id: 'lavender',
    name: '薰衣',
    icon: '💜',
    mode: 'light',
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
  lavenderDark: {
    id: 'lavenderDark',
    name: '紫夜',
    icon: '🔮',
    mode: 'dark',
    colors: {
      '--bg-primary': '#1a1422',
      '--bg-card': '#241e30',
      '--bg-input': '#2c2638',
      '--bg-tab': '#282230',
      '--text-primary': '#e0d4f0',
      '--text-secondary': '#9988aa',
      '--text-muted': '#6a5a7a',
      '--text-light': '#5a4a6a',
      '--accent': '#a07bd4',
      '--accent-dark': '#8f6ac3',
      '--accent-light': '#b89ee0',
      '--accent-lighter': '#d0c0f0',
      '--success': '#6db86d',
      '--danger': '#d47b7b',
      '--border': 'rgba(255, 255, 255, 0.08)',
      '--shadow': '0 1px 4px rgba(0, 0, 0, 0.25)',
      '--shadow-lg': '0 4px 16px rgba(0, 0, 0, 0.35)',
      '--theme-bg': '#1c1624',
      '--theme-body': '#282230',
    },
  },
  berry: {
    id: 'berry',
    name: '莓果',
    icon: '🍓',
    mode: 'light',
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
  berryDark: {
    id: 'berryDark',
    name: '暗莓',
    icon: '🫐',
    mode: 'dark',
    colors: {
      '--bg-primary': '#221418',
      '--bg-card': '#301e24',
      '--bg-input': '#38262c',
      '--bg-tab': '#302228',
      '--text-primary': '#f0d4dc',
      '--text-secondary': '#aa8899',
      '--text-muted': '#7a5a6a',
      '--text-light': '#6a4a5a',
      '--accent': '#d47b7b',
      '--accent-dark': '#c36a6a',
      '--accent-light': '#e09e9e',
      '--accent-lighter': '#f0c0c0',
      '--success': '#6db86d',
      '--danger': '#d47b7b',
      '--border': 'rgba(255, 255, 255, 0.08)',
      '--shadow': '0 1px 4px rgba(0, 0, 0, 0.25)',
      '--shadow-lg': '0 4px 16px rgba(0, 0, 0, 0.35)',
      '--theme-bg': '#24161a',
      '--theme-body': '#302228',
    },
  },
  wheat: {
    id: 'wheat',
    name: '麦浪',
    icon: '🌾',
    mode: 'light',
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
  wheatDark: {
    id: 'wheatDark',
    name: '金夜',
    icon: '✨',
    mode: 'dark',
    colors: {
      '--bg-primary': '#1a1a14',
      '--bg-card': '#26261e',
      '--bg-input': '#2e2e24',
      '--bg-tab': '#28281e',
      '--text-primary': '#e8e8d4',
      '--text-secondary': '#aaaa88',
      '--text-muted': '#7a7a5a',
      '--text-light': '#6a6a4a',
      '--accent': '#d4c87b',
      '--accent-dark': '#c3b76a',
      '--accent-light': '#e0d89e',
      '--accent-lighter': '#f0ecc0',
      '--success': '#6db86d',
      '--danger': '#d47b7b',
      '--border': 'rgba(255, 255, 255, 0.08)',
      '--shadow': '0 1px 4px rgba(0, 0, 0, 0.25)',
      '--shadow-lg': '0 4px 16px rgba(0, 0, 0, 0.35)',
      '--theme-bg': '#1c1c16',
      '--theme-body': '#28281e',
    },
  },
}

export function getThemeColor(varName) {
  return getComputedStyle(document.documentElement).getPropertyValue(varName).trim()
}

export function isDarkMode(themeId) {
  return THEMES[themeId]?.mode === 'dark'
}

export const useThemeStore = defineStore('theme', () => {
  const currentThemeId = ref(localStorage.getItem('theme') || 'warmSun')
  const themeVersion = ref(0)

  function applyTheme(themeId) {
    const theme = THEMES[themeId]
    if (!theme) return
    const root = document.documentElement
    for (const [key, value] of Object.entries(theme.colors)) {
      root.style.setProperty(key, value)
    }
    root.setAttribute('data-theme-mode', theme.mode)
    currentThemeId.value = themeId
    themeVersion.value++
    localStorage.setItem('theme', themeId)

    const metaThemeColor = document.querySelector('meta[name="theme-color"]')
    if (metaThemeColor) {
      metaThemeColor.setAttribute('content', theme.colors['--bg-primary'])
    }
  }

  function initTheme() {
    applyTheme(currentThemeId.value)
  }

  function toggleDarkMode() {
    const current = THEMES[currentThemeId.value]
    if (!current) return
    if (current.mode === 'light') {
      const darkId = currentThemeId.value + 'Dark'
      if (THEMES[darkId]) applyTheme(darkId)
    } else {
      const lightId = currentThemeId.value.replace('Dark', '')
      if (THEMES[lightId]) applyTheme(lightId)
    }
  }

  function setMode(mode) {
    const current = THEMES[currentThemeId.value]
    if (!current) return
    if (mode === 'dark' && current.mode === 'light') {
      const darkId = currentThemeId.value + 'Dark'
      if (THEMES[darkId]) applyTheme(darkId)
    } else if (mode === 'light' && current.mode === 'dark') {
      const lightId = currentThemeId.value.replace('Dark', '')
      if (THEMES[lightId]) applyTheme(lightId)
    }
  }

  const isDark = ref(THEMES[currentThemeId.value]?.mode === 'dark')

  watch(currentThemeId, (newId) => {
    isDark.value = THEMES[newId]?.mode === 'dark'
  })

  return { currentThemeId, themeVersion, isDark, applyTheme, initTheme, toggleDarkMode, setMode }
})
