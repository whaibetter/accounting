<template>
  <div class="page">
    <div class="page-header">
      <router-link to="/" class="back-btn">← 返回</router-link>
      <h1>设置</h1>
      <div style="width: 60px"></div>
    </div>

    <div class="section-title">外观设置</div>
    <div class="card theme-card">
      <div class="theme-title">主题模式</div>
      <div class="theme-desc">选择应用的外观主题</div>
      <div class="theme-options">
        <div
          v-for="option in themeOptions"
          :key="option.value"
          class="theme-option"
          :class="{ active: themeStore.themeMode === option.value }"
          @click="themeStore.setThemeMode(option.value)"
        >
          <div class="radio" :class="{ checked: themeStore.themeMode === option.value }"></div>
          <div>
            <div class="option-label">{{ option.label }}</div>
            <div class="option-desc">{{ option.desc }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useThemeStore } from '@/stores/theme'
import type { ThemeMode } from '@/stores/theme'

const themeStore = useThemeStore()

const themeOptions: { value: ThemeMode; label: string; desc: string }[] = [
  { value: 'system', label: '跟随系统', desc: '根据系统设置自动切换' },
  { value: 'light', label: '浅色模式', desc: '使用明亮的浅色界面' },
  { value: 'dark', label: '深色模式', desc: '使用暗色界面，减少视觉疲劳' },
]
</script>

<style scoped>
.back-btn {
  color: var(--primary-light);
  text-decoration: none;
  font-size: 14px;
}

.theme-card {
  margin-top: 12px;
}

.theme-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--text);
}

.theme-desc {
  font-size: 12px;
  color: var(--text-muted);
  margin-top: 4px;
}

.theme-options {
  margin-top: 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.theme-option {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px;
  border-radius: 12px;
  background: var(--bg-input);
  border: 1px solid var(--border);
  cursor: pointer;
  transition: all var(--transition);
}

.theme-option.active {
  background: var(--primary-bg);
  border-color: var(--primary);
}

.radio {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  border: 2px solid var(--text-muted);
  flex-shrink: 0;
  transition: all var(--transition);
  position: relative;
}

.radio.checked {
  border-color: var(--primary);
}

.radio.checked::after {
  content: '';
  position: absolute;
  top: 3px;
  left: 3px;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: var(--primary);
}

.option-label {
  font-size: 14px;
  font-weight: 500;
  color: var(--text);
}

.option-desc {
  font-size: 12px;
  color: var(--text-muted);
}
</style>
