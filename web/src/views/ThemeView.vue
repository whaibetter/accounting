<template>
  <div class="page theme-page">
    <div class="page-header">
      <span class="back-btn" @click="$router.back()">‹</span>
      <span class="page-title">主题风格</span>
      <span style="width: 16px"></span>
    </div>

    <div class="theme-grid">
      <div
        v-for="theme in themeList"
        :key="theme.id"
        class="theme-card"
        :class="{ selected: currentThemeId === theme.id }"
        :style="cardStyle(theme)"
        @click="selectTheme(theme.id)"
      >
        <div class="theme-preview" :style="{ background: theme.colors['--theme-bg'] }">
          <div class="tp-bar" :style="{ background: theme.colors['--accent'] }"></div>
          <div class="tp-body" :style="{ background: theme.colors['--theme-body'] }"></div>
        </div>
        <div class="theme-name">{{ theme.icon }} {{ theme.name }}</div>
        <div v-if="currentThemeId === theme.id" class="theme-check" :style="checkStyle(theme)">✓</div>
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

function selectTheme(id) {
  themeStore.applyTheme(id)
}

function cardStyle(theme) {
  const isSelected = currentThemeId.value === theme.id
  return {
    background: theme.colors['--theme-bg'],
    border: isSelected
      ? `2px solid ${theme.colors['--accent']}`
      : '1px solid #e8e8e8',
  }
}

function checkStyle(theme) {
  return {
    background: theme.colors['--accent'],
    borderColor: theme.colors['--accent'],
  }
}
</script>

<style scoped>
.back-btn {
  font-size: 22px;
  color: var(--text-primary);
  cursor: pointer;
  width: 24px;
}

.theme-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  padding: 0 16px 90px;
}

.theme-card {
  border-radius: 16px;
  padding: 16px 12px;
  text-align: center;
  cursor: pointer;
  transition: transform 0.2s;
}

.theme-card:hover {
  transform: scale(1.03);
}

.theme-card:active {
  transform: scale(0.97);
}

.theme-preview {
  height: 60px;
  border-radius: 10px;
  margin-bottom: 8px;
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 8px;
}

.tp-bar {
  height: 6px;
  border-radius: 3px;
  width: 70%;
}

.tp-body {
  flex: 1;
  border-radius: 6px;
}

.theme-name {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-secondary);
}

.theme-check {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  border: 2px solid;
  margin: 4px auto 0;
  color: white;
  font-size: 12px;
  line-height: 20px;
  text-align: center;
}
</style>
