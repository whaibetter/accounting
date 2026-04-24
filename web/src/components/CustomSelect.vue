<template>
  <div class="custom-select" ref="selectRef">
    <div
      class="select-trigger"
      :class="{ active: isOpen, disabled, 'has-error': error }"
      @click="toggle"
    >
      <span class="select-value" :class="{ placeholder: !selectedLabel }">
        {{ selectedLabel || placeholder }}
      </span>
      <span class="select-arrow" :class="{ open: isOpen }">‹</span>
    </div>
    <transition name="dropdown">
      <div v-if="isOpen" class="select-dropdown">
        <div class="dropdown-scroll">
          <div
            v-for="option in options"
            :key="option.value"
            class="dropdown-item"
            :class="{
              selected: modelValue === option.value,
              disabled: option.disabled,
            }"
            @click.stop="selectOption(option)"
          >
            <span class="item-label">{{ option.label }}</span>
            <span v-if="modelValue === option.value" class="item-check">✓</span>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue'

const props = defineProps({
  modelValue: {
    type: [String, Number, null],
    default: null,
  },
  options: {
    type: Array,
    default: () => [],
  },
  placeholder: {
    type: String,
    default: '请选择',
  },
  disabled: {
    type: Boolean,
    default: false,
  },
  error: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['update:modelValue', 'change'])

const isOpen = ref(false)
const selectRef = ref(null)

const selectedLabel = computed(() => {
  const opt = props.options.find(o => o.value === props.modelValue)
  return opt ? opt.label : ''
})

function toggle() {
  if (props.disabled) return
  isOpen.value = !isOpen.value
}

function selectOption(option) {
  if (option.disabled) return
  emit('update:modelValue', option.value)
  emit('change', option.value)
  isOpen.value = false
}

function handleClickOutside(e) {
  if (selectRef.value && !selectRef.value.contains(e.target)) {
    isOpen.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onBeforeUnmount(() => {
  document.removeEventListener('click', handleClickOutside)
})
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
  border: 1.5px solid var(--border);
  border-radius: 10px;
  background: var(--bg-primary);
  cursor: pointer;
  transition: all 0.2s ease;
  min-height: 42px;
}

.select-trigger:hover {
  border-color: var(--accent-light);
}

.select-trigger.active {
  border-color: var(--accent);
  box-shadow: 0 0 0 3px rgba(212, 165, 116, 0.12);
}

.select-trigger.disabled {
  opacity: 0.5;
  cursor: not-allowed;
  background: var(--bg-tab);
}

.select-trigger.has-error {
  border-color: var(--danger);
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
  font-size: 18px;
  color: var(--text-muted);
  transition: transform 0.25s ease;
  margin-left: 8px;
  flex-shrink: 0;
  transform: rotate(-90deg);
}

.select-arrow.open {
  transform: rotate(-90deg) rotate(180deg);
}

.select-dropdown {
  position: absolute;
  top: calc(100% + 4px);
  left: 0;
  right: 0;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(140, 120, 80, 0.12), 0 2px 8px rgba(140, 120, 80, 0.06);
  z-index: 300;
  overflow: hidden;
}

.dropdown-scroll {
  max-height: 220px;
  overflow-y: auto;
  padding: 4px;
}

.dropdown-scroll::-webkit-scrollbar {
  width: 4px;
}

.dropdown-scroll::-webkit-scrollbar-track {
  background: transparent;
}

.dropdown-scroll::-webkit-scrollbar-thumb {
  background: var(--accent-lighter);
  border-radius: 2px;
}

.dropdown-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.15s ease;
  font-size: 14px;
  color: var(--text-primary);
}

.dropdown-item:hover {
  background: rgba(212, 165, 116, 0.08);
}

.dropdown-item.selected {
  background: rgba(212, 165, 116, 0.12);
  color: var(--accent-dark);
  font-weight: 600;
}

.dropdown-item.disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.item-label {
  flex: 1;
}

.item-check {
  color: var(--accent);
  font-size: 14px;
  font-weight: 700;
  margin-left: 8px;
}

.dropdown-enter-active {
  transition: all 0.2s ease;
}

.dropdown-leave-active {
  transition: all 0.15s ease;
}

.dropdown-enter-from {
  opacity: 0;
  transform: translateY(-8px) scale(0.97);
}

.dropdown-leave-to {
  opacity: 0;
  transform: translateY(-4px) scale(0.99);
}
</style>
