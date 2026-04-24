<template>
  <div class="page theme-page">
    <div class="page-header">
      <span class="back-btn" @click="$router.back()">‹</span>
      <span class="page-title">主题风格</span>
      <span style="width: 24px"></span>
    </div>

    <div class="current-theme-card" :style="currentThemeCardStyle">
      <div class="current-theme-preview" :style="{ background: currentTheme.colors['--theme-bg'] }">
        <div class="preview-nav" :style="{ background: currentTheme.colors['--accent'] }"></div>
        <div class="preview-body">
          <div class="preview-line" :style="{ background: currentTheme.colors['--theme-body'] }"></div>
          <div class="preview-line short" :style="{ background: currentTheme.colors['--theme-body'] }"></div>
          <div class="preview-line" :style="{ background: currentTheme.colors['--theme-body'] }"></div>
        </div>
        <div class="preview-fab" :style="{ background: currentTheme.colors['--accent'] }"></div>
      </div>
      <div class="current-theme-info">
        <div class="current-theme-name">{{ currentTheme.icon }} {{ currentTheme.name }}</div>
        <div class="current-theme-label">当前主题</div>
      </div>
    </div>

    <div class="section-header">
      <span class="section-title">选择主题</span>
    </div>

    <div class="theme-list">
      <div
        v-for="theme in themeList"
        :key="theme.id"
        class="theme-item"
        :class="{ selected: currentThemeId === theme.id }"
        @click="selectTheme(theme.id)"
      >
        <div class="theme-item-preview" :style="{ background: theme.colors['--theme-bg'] }">
          <div class="tip-bar" :style="{ background: theme.colors['--accent'] }"></div>
          <div class="tip-body" :style="{ background: theme.colors['--theme-body'] }"></div>
        </div>
        <div class="theme-item-info">
          <span class="theme-item-name">{{ theme.icon }} {{ theme.name }}</span>
          <span v-if="currentThemeId === theme.id" class="theme-item-check" :style="{ color: theme.colors['--accent'] }">✓ 使用中</span>
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
const themeList = Object.values(THEMES)
const currentTheme = computed(() => THEMES[currentThemeId.value] || THEMES.warmSun)

const currentThemeCardStyle = computed(() => ({
  background: currentTheme.value.colors['--bg-card'],
  borderColor: currentTheme.value.colors['--accent'],
}))

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

.current-theme-card {
  margin: 12px 16px;
  border-radius: 20px;
  padding: 20px;
  display: flex;
  gap: 16px;
  align-items: center;
  box-shadow: var(--shadow-lg);
  border: 1.5px solid var(--accent);
}

.current-theme-preview {
  width: 72px;
  height: 96px;
  border-radius: 12px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  padding: 6px;
  position: relative;
  overflow: hidden;
}

.preview-nav {
  height: 8px;
  border-radius: 4px;
  width: 80%;
  margin-bottom: 6px;
}

.preview-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.preview-line {
  height: 6px;
  border-radius: 3px;
  width: 100%;
}

.preview-line.short {
  width: 60%;
}

.preview-fab {
  position: absolute;
  bottom: 8px;
  right: 6px;
  width: 16px;
  height: 16px;
  border-radius: 5px;
}

.current-theme-info {
  flex: 1;
}

.current-theme-name {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-primary);
}

.current-theme-label {
  font-size: 12px;
  color: var(--accent);
  font-weight: 600;
  margin-top: 4px;
}

.section-header {
  padding: 16px 20px 8px;
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
  flex-direction: column;
  gap: 2px;
}

.theme-item-name {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-primary);
}

.theme-item-check {
  font-size: 10px;
  font-weight: 600;
}
</style>
