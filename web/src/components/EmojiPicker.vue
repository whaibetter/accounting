<template>
  <div class="emoji-picker">
    <div class="ep-header">
      <div class="ep-preview">
        <span class="ep-preview-icon">{{ modelValue || '📝' }}</span>
      </div>
      <div class="ep-mode-toggle">
        <button
          class="ep-mode-btn"
          :class="{ active: mode === 'preset' }"
          @click="mode = 'preset'"
        >预设选择</button>
        <button
          class="ep-mode-btn"
          :class="{ active: mode === 'custom' }"
          @click="mode = 'custom'"
        >自定义图标</button>
      </div>
    </div>

    <div v-if="mode === 'preset'" class="ep-preset">
      <div class="ep-category-tabs">
        <button
          v-for="cat in presetCategories"
          :key="cat.key"
          class="ep-cat-tab"
          :class="{ active: activeCategory === cat.key }"
          @click="activeCategory = cat.key"
        >{{ cat.label }}</button>
      </div>
      <div class="ep-grid">
        <button
          v-for="emoji in currentEmojis"
          :key="emoji"
          class="ep-emoji-btn"
          :class="{ active: modelValue === emoji }"
          @click="selectEmoji(emoji)"
        >{{ emoji }}</button>
      </div>
    </div>

    <div v-else class="ep-custom">
      <input
        :value="modelValue"
        type="text"
        class="ep-custom-input"
        placeholder="输入自定义图标内容（如 emoji、文字、符号）"
        @input="$emit('update:modelValue', $event.target.value)"
      />
      <div class="ep-custom-hint">支持输入任意 emoji、文字或符号作为图标</div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  modelValue: { type: String, default: '' },
  category: { type: String, default: '' },
})

const emit = defineEmits(['update:modelValue'])

const mode = ref('preset')
const activeCategory = ref('common')

const presetCategories = [
  { key: 'common', label: '常用' },
  { key: 'food', label: '餐饮' },
  { key: 'transport', label: '交通' },
  { key: 'shopping', label: '购物' },
  { key: 'life', label: '生活' },
  { key: 'finance', label: '财务' },
  { key: 'nature', label: '自然' },
  { key: 'symbol', label: '符号' },
]

const presetEmojis = {
  common: ['📝', '📌', '🔖', '🏷️', '📂', '📋', '📊', '📈', '📉', '💡', '🔔', '⭐', '❤️', '🔥', '✅', '❌', '⏰', '🎯', '🎁', '🎉', '💰', '💳', '🏠', '👤', '🔒', '⚙️', '📱', '💻', '🛒', '📦'],
  food: ['🍜', '🍚', '🍛', '🍲', '🍱', '🥗', '🍞', '🥐', '🥩', '🍗', '🍔', '🍕', '🌮', '🍣', '🦐', '🍦', '🧁', '🍰', '🍩', '🍪', '☕', '🍵', '🧃', '🍺', '🥤', '🧋', '🍷', '🥛', '🫖', '🍶'],
  transport: ['🚗', '🚌', '🚕', '🚎', '🚇', '🚄', '✈️', '🚲', '🛵', '🚀', '🚢', '⛽', '🅿️', '🛣️', '🚥', '🚦', '🧭', '🗺️', '🚘', '🚃'],
  shopping: ['🛍️', '🛒', '👕', '👗', '👟', '👜', '💄', '💍', '🧴', '🪒', '🧸', '🎁', '🏷️', '🏪', '🏬', '🛒', '📦', '🧧', '🎀', '🛷'],
  life: ['🏠', '🏡', '🔑', '🛋️', '🛏️', '🚿', '🧹', '🧺', '💊', '🏥', '📚', '🎓', '🎬', '🎮', '⚽', '🏀', '🎵', '🎨', '✈️', '🏖️', '🎪', '🎭', '🎲', '🧩', '🎯', '🏋️', '🧘', '🏊', '🚴', '⛷️'],
  finance: ['💰', '💵', '💶', '💷', '💴', '💳', '🏦', '📈', '📉', '💹', '💼', '🧧', '🏧', '💰', '💎', '🏦', '📊', '🪙', '💲', '💱'],
  nature: ['☀️', '🌤️', '🌙', '⭐', '🌈', '🌸', '🌺', '🍀', '🌿', '🌾', '🌴', '🌵', '🍁', '🌊', '🔥', '💧', '❄️', '🍄', '🌻', '💐'],
  symbol: ['🔴', '🟠', '🟡', '🟢', '🔵', '🟣', '⚪', '⚫', '🔶', '🔷', '🔺', '🔻', '💠', '⬆️', '⬇️', '➡️', '⬅️', '↗️', '↘️', '↩️', '♻️', '🆕', '🆗', '🆒', '🆓', '✨', '💫', '🌟', '⚡', '💥'],
}

const currentEmojis = computed(() => presetEmojis[activeCategory.value] || presetEmojis.common)

function selectEmoji(emoji) {
  emit('update:modelValue', emoji)
}
</script>

<style scoped>
.emoji-picker {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.ep-header {
  display: flex;
  align-items: center;
  gap: 12px;
}

.ep-preview {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  background: var(--bg-tab, #f5f1eb);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  border: 1.5px solid var(--border, #e8e4dc);
}

.ep-preview-icon {
  font-size: 22px;
}

.ep-mode-toggle {
  flex: 1;
  display: flex;
  background: var(--bg-tab, #f5f1eb);
  border-radius: 8px;
  padding: 2px;
  gap: 2px;
}

.ep-mode-btn {
  flex: 1;
  padding: 6px 0;
  font-size: 12px;
  font-weight: 600;
  border-radius: 6px;
  color: var(--text-muted, #a89a82);
  background: transparent;
  transition: all 0.2s;
  text-align: center;
}

.ep-mode-btn.active {
  background: var(--bg-card, #fff);
  color: var(--accent, #b8894e);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
}

.ep-preset {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.ep-category-tabs {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
}

.ep-cat-tab {
  padding: 4px 10px;
  font-size: 11px;
  font-weight: 600;
  border-radius: 6px;
  color: var(--text-muted, #a89a82);
  background: var(--bg-tab, #f5f1eb);
  white-space: nowrap;
  transition: all 0.2s;
}

.ep-cat-tab.active {
  background: var(--accent, #b8894e);
  color: #fff;
}

.ep-grid {
  display: grid;
  grid-template-columns: repeat(8, 1fr);
  gap: 4px;
  max-height: 160px;
  overflow-y: auto;
  padding: 4px;
  background: var(--bg-tab, #f5f1eb);
  border-radius: 10px;
  -webkit-overflow-scrolling: touch;
}

.ep-grid::-webkit-scrollbar {
  width: 3px;
}

.ep-grid::-webkit-scrollbar-thumb {
  background: rgba(0, 0, 0, 0.1);
  border-radius: 3px;
}

.ep-emoji-btn {
  width: 100%;
  aspect-ratio: 1;
  font-size: 18px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.15s;
  background: transparent;
}

.ep-emoji-btn:hover {
  background: rgba(0, 0, 0, 0.04);
  transform: scale(1.1);
}

.ep-emoji-btn:active {
  transform: scale(0.95);
}

.ep-emoji-btn.active {
  background: var(--accent, #b8894e);
  box-shadow: 0 2px 8px rgba(184, 137, 78, 0.3);
  transform: scale(1.05);
}

.ep-custom {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.ep-custom-input {
  padding: 10px 14px;
  border: 1.5px solid var(--border, #e8e4dc);
  border-radius: 10px;
  font-size: 14px;
  color: var(--text-primary, #333);
  background: var(--bg-input, #fff);
  transition: border-color 0.2s;
}

.ep-custom-input:focus {
  border-color: var(--accent, #b8894e);
  outline: none;
}

.ep-custom-hint {
  font-size: 11px;
  color: var(--text-muted, #a89a82);
  padding-left: 2px;
}
</style>
