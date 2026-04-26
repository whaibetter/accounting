<template>
  <div v-if="visible" class="modal-overlay" @click.self="$emit('close')">
    <div class="month-picker-modal">
      <div class="picker-header">
        <span class="picker-title">选择月份</span>
        <span class="picker-close" @click="$emit('close')">✕</span>
      </div>
      <div class="quick-nav">
        <button class="quick-btn" @click="selectQuick('thisMonth')">本月</button>
        <button class="quick-btn" @click="selectQuick('lastMonth')">上月</button>
        <button class="quick-btn" @click="selectQuick('thisYear')">今年</button>
      </div>
      <div class="year-list">
        <div v-for="year in yearList" :key="year" class="year-group">
          <div
            class="year-row"
            :class="{ active: expandedYear === year }"
            @click="toggleYear(year)"
          >
            <span class="year-label">{{ year }}年</span>
            <span class="year-arrow" :class="{ expanded: expandedYear === year }">›</span>
          </div>
          <transition name="slide">
            <div v-if="expandedYear === year" class="month-grid">
              <div
                v-for="m in 12"
                :key="m"
                class="month-cell"
                :class="{
                  selected: isSelected(year, m),
                  current: isCurrentMonth(year, m),
                  future: isFutureMonth(year, m),
                }"
                @click="selectMonth(year, m)"
              >
                {{ m }}月
              </div>
            </div>
          </transition>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import dayjs from 'dayjs'

const props = defineProps({
  visible: { type: Boolean, default: false },
  modelValue: { type: Object, default: () => dayjs() },
})

const emit = defineEmits(['update:modelValue', 'close', 'select'])

const expandedYear = ref(dayjs().year())

watch(() => props.visible, (v) => {
  if (v) {
    expandedYear.value = props.modelValue.year()
  }
})

const yearList = computed(() => {
  const now = dayjs()
  const years = []
  for (let y = now.year(); y >= now.year() - 5; y--) {
    years.push(y)
  }
  return years
})

function toggleYear(year) {
  expandedYear.value = expandedYear.value === year ? null : year
}

function isSelected(year, month) {
  return props.modelValue.year() === year && props.modelValue.month() + 1 === month
}

function isCurrentMonth(year, month) {
  const now = dayjs()
  return now.year() === year && now.month() + 1 === month
}

function isFutureMonth(year, month) {
  const now = dayjs()
  const target = dayjs(`${year}-${String(month).padStart(2, '0')}-01`)
  return target.isAfter(now, 'month')
}

function selectMonth(year, month) {
  if (isFutureMonth(year, month)) return
  const d = dayjs(`${year}-${String(month).padStart(2, '0')}-01`)
  emit('update:modelValue', d)
  emit('select', d)
  emit('close')
}

function selectQuick(type) {
  const now = dayjs()
  let d
  switch (type) {
    case 'thisMonth': d = now.startOf('month'); break
    case 'lastMonth': d = now.subtract(1, 'month').startOf('month'); break
    case 'thisYear': d = now.startOf('year'); break
  }
  emit('update:modelValue', d)
  emit('select', d)
  emit('close')
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: flex-end;
  justify-content: center;
  z-index: 200;
}

.month-picker-modal {
  background: var(--bg-card);
  border-radius: 20px 20px 0 0;
  padding: 20px 16px 32px;
  width: 100%;
  max-width: 480px;
  max-height: 70vh;
  overflow-y: auto;
}

.picker-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
  padding: 0 4px;
}

.picker-title {
  font-size: 17px;
  font-weight: 700;
  color: var(--text-primary);
}

.picker-close {
  font-size: 18px;
  color: var(--text-muted);
  cursor: pointer;
  padding: 4px 8px;
}

.quick-nav {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
  padding: 0 4px;
}

.quick-btn {
  flex: 1;
  padding: 8px 0;
  border-radius: 10px;
  font-size: 13px;
  font-weight: 500;
  background: rgba(212, 165, 116, 0.08);
  color: var(--accent-dark);
  border: 1px solid rgba(212, 165, 116, 0.15);
  cursor: pointer;
  transition: all 0.15s;
}

.quick-btn:active {
  background: rgba(212, 165, 116, 0.18);
}

.year-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.year-group {
  border-radius: 12px;
  overflow: hidden;
}

.year-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 16px;
  cursor: pointer;
  transition: background 0.15s;
  border-radius: 12px;
}

.year-row:hover {
  background: rgba(0, 0, 0, 0.03);
}

.year-row.active {
  background: rgba(212, 165, 116, 0.08);
}

.year-label {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

.year-arrow {
  font-size: 18px;
  color: var(--text-muted);
  transition: transform 0.25s ease;
}

.year-arrow.expanded {
  transform: rotate(90deg);
}

.month-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 8px;
  padding: 4px 8px 12px;
}

.month-cell {
  text-align: center;
  padding: 10px 0;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
  cursor: pointer;
  transition: all 0.15s ease;
  background: rgba(0, 0, 0, 0.02);
}

.month-cell:hover {
  background: rgba(212, 165, 116, 0.12);
}

.month-cell.selected {
  background: var(--accent);
  color: white;
  font-weight: 700;
}

.month-cell.current:not(.selected) {
  border: 1.5px solid var(--accent);
  color: var(--accent);
  font-weight: 600;
}

.month-cell.future {
  color: var(--text-muted);
  opacity: 0.4;
  cursor: not-allowed;
}

.slide-enter-active,
.slide-leave-active {
  transition: all 0.25s ease;
  max-height: 200px;
  overflow: hidden;
}

.slide-enter-from,
.slide-leave-to {
  max-height: 0;
  opacity: 0;
  padding-top: 0;
  padding-bottom: 0;
}
</style>
