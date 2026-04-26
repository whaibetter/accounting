<template>
  <div class="custom-select" :class="{ open: isOpen }" v-click-outside="close">
    <div class="select-trigger" @click="toggle">
      <span class="select-value" :class="{ placeholder: !selectedLabel }">
        {{ selectedLabel || placeholder }}
      </span>
      <span class="select-arrow">▾</span>
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
  modelValue: { type: [String, Number, null], default: null },
  options: { type: Array, default: () => [] },
  placeholder: { type: String, default: '请选择' },
})

const emit = defineEmits(['update:modelValue'])

const isOpen = ref(false)

const selectedLabel = computed(() => {
  if (props.modelValue === null || props.modelValue === undefined) return ''
  const found = props.options.find(o => o.value === props.modelValue)
  return found ? found.label : ''
})

function toggle() {
  isOpen.value = !isOpen.value
}

function close() {
  isOpen.value = false
}

function selectOption(option) {
  emit('update:modelValue', option.value)
  isOpen.value = false
}

const vClickOutside = {
  mounted(el, binding) {
    el._clickOutside = (e) => {
      if (!el.contains(e.target)) {
        binding.value()
      }
    }
    document.addEventListener('click', el._clickOutside)
  },
  unmounted(el) {
    document.removeEventListener('click', el._clickOutside)
  },
}
</script>

<style scoped>
.custom-select {
  position: relative;
  width: 100%;
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
  transition: border-color 0.2s;
}

.select-trigger:active {
  border-color: var(--accent);
}

.custom-select.open .select-trigger {
  border-color: var(--accent);
}

.select-value {
  font-size: 14px;
  color: var(--text-primary);
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.select-value.placeholder {
  color: var(--text-muted);
}

.select-arrow {
  font-size: 12px;
  color: var(--text-muted);
  transition: transform 0.2s;
  flex-shrink: 0;
  margin-left: 8px;
}

.custom-select.open .select-arrow {
  transform: rotate(180deg);
}

.select-dropdown {
  position: absolute;
  top: calc(100% + 4px);
  left: 0;
  right: 0;
  background: var(--bg-card);
  border: 1.5px solid var(--border);
  border-radius: 10px;
  box-shadow: var(--shadow-lg);
  z-index: 100;
  max-height: 200px;
  overflow-y: auto;
  overscroll-behavior: contain;
}

.select-option {
  padding: 10px 14px;
  font-size: 14px;
  color: var(--text-primary);
  cursor: pointer;
  transition: background 0.15s;
}

.select-option:first-child {
  border-radius: 9px 9px 0 0;
}

.select-option:last-child {
  border-radius: 0 0 9px 9px;
}

.select-option:active {
  background: var(--bg-input);
}

.select-option.active {
  color: var(--accent);
  font-weight: 600;
  background: rgba(212, 165, 116, 0.08);
}

.select-empty {
  padding: 16px;
  text-align: center;
  font-size: 13px;
  color: var(--text-muted);
}

.dropdown-enter-active {
  animation: dropdownIn 0.2s ease;
}

.dropdown-leave-active {
  animation: dropdownOut 0.15s ease;
}

@keyframes dropdownIn {
  from { opacity: 0; transform: translateY(-6px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes dropdownOut {
  from { opacity: 1; transform: translateY(0); }
  to { opacity: 0; transform: translateY(-6px); }
}
</style>
