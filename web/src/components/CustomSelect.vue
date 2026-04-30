<template>
  <div class="custom-select" :class="{ open: isOpen, disabled: disabled }" v-click-outside="close">
    <div class="select-trigger" @click="!disabled && toggle()" :class="{ focused: isOpen, hasValue: !!selectedLabel }">
      <span class="select-value" :class="{ placeholder: !selectedLabel }">
        {{ selectedLabel || placeholder }}
      </span>
      <span class="select-arrow" :class="{ rotated: isOpen }">▾</span>
    </div>
    <Transition name="dropdown">
      <div v-if="isOpen" class="select-dropdown">
        <div
          v-for="option in options"
          :key="option.value"
          class="select-option"
          :class="{ active: option.value === modelValue }"
          @click.stop="selectOption(option)"
        >
          {{ option.label }}
        </div>
        <div v-if="!options || options.length === 0" class="select-empty">
          暂无选项
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  modelValue: { type: [String, Number, null, Boolean], default: null },
  options: { type: Array, default: () => [] },
  placeholder: { type: String, default: '请选择' },
  disabled: { type: Boolean, default: false },
})

const emit = defineEmits(['update:modelValue', 'change'])

const isOpen = ref(false)

const selectedLabel = computed(() => {
  if (props.modelValue === null || props.modelValue === undefined) return ''
  const found = props.options.find(o => o.value === props.modelValue)
  return found ? found.label : ''
})

function toggle() {
  if (props.disabled) return
  isOpen.value = !isOpen.value
}

function close() {
  isOpen.value = false
}

function selectOption(option) {
  if (props.modelValue !== option.value) {
    emit('update:modelValue', option.value)
    emit('change', option.value)
  }
  isOpen.value = false
}

const vClickOutside = {
  mounted(el, binding) {
    el._clickOutside = (e) => {
      if (e.target === document.documentElement || e.target === document.body) return
      if (!el.contains(e.target)) {
        binding.value()
      }
    }
    el._mouseDownOutside = (e) => {
      el._mouseDownWasOutside = !el.contains(e.target)
    }
    document.addEventListener('mousedown', el._mouseDownOutside, true)
    document.addEventListener('click', el._clickOutside)
  },
  unmounted(el) {
    document.removeEventListener('mousedown', el._mouseDownOutside, true)
    document.removeEventListener('click', el._clickOutside)
  },
}
</script>

<style scoped>
.custom-select {
  position: relative;
  width: 100%;
}

.custom-select.compact .select-trigger {
  padding: 6px 10px;
  border-radius: 8px;
}

.custom-select.compact .select-value {
  font-size: 12px;
}

.custom-select.compact .select-arrow {
  font-size: 11px;
}

.custom-select.compact .select-option {
  padding: 8px 10px;
  font-size: 12px;
}

.custom-select.compact .select-dropdown {
  max-height: 180px;
  border-radius: 10px;
}

.custom-select.disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.select-trigger {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 14px;
  background: var(--bg-input);
  border: 1.5px solid var(--border);
  border-radius: 10px;
  cursor: pointer;
  user-select: none;
  transition: all 0.2s;
}

.select-trigger:hover {
  border-color: var(--accent);
  box-shadow: 0 0 0 3px rgba(212, 165, 116, 0.08);
}

.select-trigger.focused {
  border-color: var(--accent);
  box-shadow: 0 0 0 3px rgba(212, 165, 116, 0.12);
  background: var(--bg-card);
}

.select-trigger.hasValue .select-value {
  color: var(--text-primary);
}

.select-value {
  font-size: 14px;
  color: var(--text-primary);
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-weight: 500;
}

.select-value.placeholder {
  color: var(--text-muted);
  font-weight: 400;
}

.select-arrow {
  font-size: 12px;
  color: var(--text-muted);
  transition: transform 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  flex-shrink: 0;
  margin-left: 8px;
}

.select-arrow.rotated {
  transform: rotate(180deg);
  color: var(--accent);
}

.select-dropdown {
  position: absolute;
  top: calc(100% + 4px);
  left: 0;
  right: 0;
  background: var(--bg-card);
  border: 1.5px solid var(--border);
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  z-index: 100;
  max-height: 220px;
  overflow-y: auto;
  overscroll-behavior: contain;
  backdrop-filter: blur(8px);
}

.select-dropdown::-webkit-scrollbar {
  width: 6px;
}

.select-dropdown::-webkit-scrollbar-track {
  background: transparent;
}

.select-dropdown::-webkit-scrollbar-thumb {
  background: var(--border);
  border-radius: 3px;
}

.select-dropdown::-webkit-scrollbar-thumb:hover {
  background: var(--text-muted);
}

.select-option {
  padding: 10px 14px;
  font-size: 14px;
  color: var(--text-primary);
  cursor: pointer;
  transition: all 0.15s;
  display: flex;
  align-items: center;
  gap: 8px;
}

.select-option:first-child {
  border-radius: 11px 11px 0 0;
}

.select-option:last-child {
  border-radius: 0 0 11px 11px;
}

.select-option:only-child {
  border-radius: 11px;
}

.select-option:hover {
  background: rgba(212, 165, 116, 0.06);
}

.select-option:active {
  background: rgba(212, 165, 116, 0.12);
}

.select-option.active {
  color: var(--accent);
  font-weight: 600;
  background: rgba(212, 165, 116, 0.1);
}

.select-option.active::before {
  content: '';
  width: 4px;
  height: 4px;
  border-radius: 50%;
  background: var(--accent);
  flex-shrink: 0;
}

.select-empty {
  padding: 16px;
  text-align: center;
  font-size: 13px;
  color: var(--text-muted);
}

.dropdown-enter-active {
  animation: dropdownIn 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.dropdown-leave-active {
  animation: dropdownOut 0.15s cubic-bezier(0.4, 0, 0.2, 1);
}

@keyframes dropdownIn {
  from { opacity: 0; transform: translateY(-8px) scale(0.98); }
  to { opacity: 1; transform: translateY(0) scale(1); }
}

@keyframes dropdownOut {
  from { opacity: 1; transform: translateY(0) scale(1); }
  to { opacity: 0; transform: translateY(-6px) scale(0.98); }
}
</style>
