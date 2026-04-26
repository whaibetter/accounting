<template>
  <Transition name="confirm-fade">
    <div v-if="visible" class="confirm-overlay" @click="handleCancel">
      <div class="confirm-dialog" @click.stop>
        <div class="confirm-icon">{{ icon }}</div>
        <div class="confirm-title">{{ title }}</div>
        <div class="confirm-desc" v-if="description">{{ description }}</div>
        <div class="confirm-actions">
          <button class="confirm-btn cancel" @click="handleCancel">取消</button>
          <button class="confirm-btn danger" @click="handleConfirm">{{ confirmText }}</button>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  icon: { type: String, default: '⚠️' },
  title: { type: String, default: '确认操作' },
  description: { type: String, default: '' },
  confirmText: { type: String, default: '确认删除' },
})

const visible = ref(false)
let resolveFn = null

function show() {
  visible.value = true
  return new Promise((resolve) => {
    resolveFn = resolve
  })
}

function handleConfirm() {
  visible.value = false
  if (resolveFn) resolveFn(true)
  resolveFn = null
}

function handleCancel() {
  visible.value = false
  if (resolveFn) resolveFn(false)
  resolveFn = null
}

defineExpose({ show })
</script>

<style scoped>
.confirm-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.confirm-dialog {
  background: var(--bg-card);
  border-radius: 16px;
  padding: 28px 24px 24px;
  width: 85%;
  max-width: 320px;
  text-align: center;
  box-shadow: var(--shadow-lg);
}

.confirm-icon {
  font-size: 40px;
  margin-bottom: 12px;
}

.confirm-title {
  font-size: 17px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 6px;
}

.confirm-desc {
  font-size: 13px;
  color: var(--text-muted);
  margin-bottom: 20px;
  line-height: 1.5;
}

.confirm-actions {
  display: flex;
  gap: 12px;
}

.confirm-btn {
  flex: 1;
  padding: 12px;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s;
}

.confirm-btn.cancel {
  background: var(--bg-input);
  color: var(--text-secondary);
  border: 1.5px solid var(--border);
}

.confirm-btn.cancel:active {
  background: var(--bg-tab);
}

.confirm-btn.danger {
  background: var(--danger);
  color: white;
  border: none;
}

.confirm-btn.danger:active {
  opacity: 0.85;
}

.confirm-fade-enter-active {
  animation: confirmIn 0.2s ease;
}

.confirm-fade-leave-active {
  animation: confirmOut 0.15s ease;
}

@keyframes confirmIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes confirmOut {
  from { opacity: 1; }
  to { opacity: 0; }
}
</style>
