import { ref } from 'vue'

const toastRef = ref(null)

export function setToastRef(ref) {
  toastRef.value = ref
}

export function showToast(message, type = 'info', duration = 2500) {
  if (toastRef.value) {
    toastRef.value.show(message, type, duration)
  }
}

export function toastSuccess(message, duration) {
  showToast(message, 'success', duration)
}

export function toastError(message, duration) {
  showToast(message, 'error', duration)
}

export function toastWarning(message, duration) {
  showToast(message, 'warning', duration)
}

export function toastInfo(message, duration) {
  showToast(message, 'info', duration)
}

export default {
  install(app) {
    app.config.globalProperties.$toast = {
      show: showToast,
      success: toastSuccess,
      error: toastError,
      warning: toastWarning,
      info: toastInfo,
    }
  }
}
