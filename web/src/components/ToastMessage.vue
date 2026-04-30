<template>
  <Transition name="toast-slide">
    <div v-if="visible" class="toast-container" :class="type">
      <div class="toast-icon">{{ iconMap[type] }}</div>
      <div class="toast-content">{{ message }}</div>
    </div>
  </Transition>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  type: { type: String, default: 'info' },
  message: { type: String, default: '' },
  duration: { type: Number, default: 2500 },
})

const visible = ref(false)
const iconMap = {
  success: '✓',
  error: '✕',
  warning: '!',
  info: 'i'
}

let timer = null

function show(msg, msgType, msgDuration) {
  if (timer) clearTimeout(timer)
  
  if (msg !== undefined) {
    message.value = msg
    type.value = msgType || 'info'
  }
  
  visible.value = true
  
  timer = setTimeout(() => {
    visible.value = false
    timer = null
  }, msgDuration || props.duration)
}

function hide() {
  if (timer) clearTimeout(timer)
  visible.value = false
}

const message = ref(props.message)
const type = ref(props.type)

defineExpose({ show, hide })
</script>

<style scoped>
.toast-container {
  position: fixed;
  top: 20px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px 20px;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
  z-index: 9999;
  max-width: 85%;
  min-width: 200px;
  backdrop-filter: blur(10px);
}

.toast-container.success {
  background: linear-gradient(135deg, #e8f5e9, #c8e6c9);
  border: 1px solid #81c784;
  color: #2e7d32;
}

.toast-container.error {
  background: linear-gradient(135deg, #ffebee, #ffcdd2);
  border: 1px solid #ef9a9a;
  color: #c62828;
}

.toast-container.warning {
  background: linear-gradient(135deg, #fff3e0, #ffe0b2);
  border: 1px solid #ffcc80;
  color: #e65100;
}

.toast-container.info {
  background: linear-gradient(135deg, #e3f2fd, #bbdefb);
  border: 1px solid #90caf9;
  color: #1565c0;
}

.toast-icon {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 700;
  flex-shrink: 0;
}

.toast-container.success .toast-icon {
  background: #4caf50;
  color: white;
}

.toast-container.error .toast-icon {
  background: #f44336;
  color: white;
}

.toast-container.warning .toast-icon {
  background: #ff9800;
  color: white;
}

.toast-container.info .toast-icon {
  background: #2196f3;
  color: white;
}

.toast-content {
  font-size: 14px;
  font-weight: 500;
  line-height: 1.4;
  word-break: break-word;
}

.toast-slide-enter-active {
  animation: toastIn 0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55);
}

.toast-slide-leave-active {
  animation: toastOut 0.2s ease-in;
}

@keyframes toastIn {
  from {
    opacity: 0;
    transform: translate(-50%, -20px) scale(0.9);
  }
  to {
    opacity: 1;
    transform: translate(-50%, 0) scale(1);
  }
}

@keyframes toastOut {
  from {
    opacity: 1;
    transform: translate(-50%, 0) scale(1);
  }
  to {
    opacity: 0;
    transform: translate(-50%, -10px) scale(0.95);
  }
}
</style>
