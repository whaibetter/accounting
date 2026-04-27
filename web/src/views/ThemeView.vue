<template>
  <div class="page theme-page">
    <div class="page-header">
      <span class="back-btn" @click="$router.back()">‹</span>
      <span class="page-title">主题风格</span>
      <span style="width: 24px"></span>
    </div>

    <div class="mode-toggle-section">
      <div class="mode-toggle" @click="toggleMode">
        <div class="mode-option" :class="{ active: !isDark }">
          <span class="mode-icon">☀️</span>
          <span class="mode-label">浅色</span>
        </div>
        <div class="mode-option" :class="{ active: isDark }">
          <span class="mode-icon">🌙</span>
          <span class="mode-label">深色</span>
        </div>
        <div class="mode-slider" :class="{ dark: isDark }"></div>
      </div>
    </div>

    <div class="section-header">
      <span class="section-title">{{ isDark ? '深色主题' : '浅色主题' }}</span>
    </div>

    <div class="theme-list">
      <div
        v-for="theme in filteredThemes"
        :key="theme.id"
        class="theme-item"
        :class="{ selected: currentThemeId === theme.id }"
        @click="selectTheme(theme.id)"
      >
        <div class="theme-item-preview" :style="{ background: theme.colors['--bg-primary'] }">
          <div class="tip-bar" :style="{ background: theme.colors['--accent'] }"></div>
          <div class="tip-body" :style="{ background: theme.colors['--bg-tab'] }"></div>
        </div>
        <div class="theme-item-info">
          <span class="theme-item-name">{{ theme.icon }} {{ theme.name }}</span>
          <span v-if="currentThemeId === theme.id" class="theme-item-check" :style="{ color: theme.colors['--accent'] }">✓</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useThemeStore, THEMES } from '@/stores/theme'

const themeStore = useThemeStore()

const currentThemeId = computed(() => themeStore.currentThemeId)
const isDark = computed(() => themeStore.isDark)

const filteredThemes = computed(() => {
  const mode = isDark.value ? 'dark' : 'light'
  return Object.values(THEMES).filter(t => t.mode === mode)
})

function toggleMode() {
  themeStore.toggleDarkMode()
}

function selectTheme(id) {
  themeStore.applyTheme(id)
}
</script>

<style scoped>
.back-btn {
  font-size: 22px;
  color: var(--text-primary);
  cursor: pointer;
  width: 24px;
}

.mode-toggle-section {
  display: flex;
  justify-content: center;
  padding: 8px 16px 16px;
}

.mode-toggle {
  display: flex;
  position: relative;
  background: var(--bg-tab);
  border-radius: 12px;
  padding: 3px;
  cursor: pointer;
  width: 200px;
}

.mode-option {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 10px 0;
  z-index: 1;
  transition: color 0.25s;
  color: var(--text-muted);
}

.mode-option.active {
  color: var(--text-primary);
}

.mode-icon {
  font-size: 16px;
}

.mode-label {
  font-size: 13px;
  font-weight: 600;
}

.mode-slider {
  position: absolute;
  top: 3px;
  left: 3px;
  width: calc(50% - 3px);
  height: calc(100% - 6px);
  background: var(--bg-card);
  border-radius: 10px;
  box-shadow: var(--shadow);
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.mode-slider.dark {
  transform: translateX(100%);
}

.section-header {
  padding: 8px 20px 8px;
}

.section-title {
  font-size: 14px;
  font-weight: 700;
  color: var(--text-secondary);
  letter-spacing: 0.5px;
}

.theme-list {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  padding: 0 16px 90px;
}

.theme-item {
  border-radius: 16px;
  padding: 12px;
  text-align: center;
  cursor: pointer;
  transition: all 0.25s ease;
  background: var(--bg-card);
  border: 1.5px solid transparent;
  box-shadow: var(--shadow);
}

.theme-item.selected {
  border-color: var(--accent);
  box-shadow: var(--shadow-lg);
}

.theme-item:active {
  transform: scale(0.96);
}

.theme-item-preview {
  height: 52px;
  border-radius: 10px;
  margin-bottom: 8px;
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 6px;
}

.tip-bar {
  height: 5px;
  border-radius: 3px;
  width: 70%;
}

.tip-body {
  flex: 1;
  border-radius: 5px;
}

.theme-item-info {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
}

.theme-item-name {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-primary);
}

.theme-item-check {
  font-size: 11px;
  font-weight: 700;
}
</style>
