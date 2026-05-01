<template>
  <div class="avatar-uploader">
    <div class="avatar-preview" :class="{ readonly: !editable }" @click="triggerUpload">
      <img v-if="previewUrl" :src="previewUrl" class="avatar-img" />
      <div v-else class="avatar-placeholder">
        <span class="placeholder-icon">📷</span>
        <span class="placeholder-text">上传头像</span>
      </div>
      <div v-if="editable" class="avatar-overlay">
        <span>更换</span>
      </div>
    </div>
    <input
      ref="fileInput"
      type="file"
      accept=".jpg,.jpeg,.png,.webp"
      style="display: none"
      @change="handleFileSelect"
    />
    <div v-if="uploading" class="upload-progress">
      <div class="progress-bar">
        <div class="progress-fill" :style="{ width: progress + '%' }"></div>
      </div>
      <span class="progress-text">{{ progress }}%</span>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, computed, onMounted } from 'vue'
import api from '@/services/api'
import { toastError, toastSuccess } from '@/utils/toast'

const props = defineProps({
  modelValue: { type: String, default: '' },
  size: { type: Number, default: 80 },
  editable: { type: Boolean, default: true },
  userId: { type: Number, default: null },
})

const emit = defineEmits(['update:modelValue', 'uploaded'])

const fileInput = ref(null)
const previewUrl = ref('')
const uploading = ref(false)
const progress = ref(0)

function resolveUrl(url) {
  if (!url) return ''
  if (url.startsWith('http') || url.startsWith('data:')) return url
  const base = api.defaults?.baseURL ? api.defaults.baseURL.replace('/api/v1', '') : ''
  return base + url
}

watch(() => props.modelValue, (val) => {
  previewUrl.value = resolveUrl(val)
}, { immediate: true })

function triggerUpload() {
  if (uploading.value || !props.editable) return
  fileInput.value.click()
}

async function handleFileSelect(e) {
  const file = e.target.files?.[0]
  if (!file) return

  const allowedTypes = ['image/jpeg', 'image/png', 'image/webp']
  if (!allowedTypes.includes(file.type)) {
    toastError('仅支持 JPG、PNG、WebP 格式')
    fileInput.value.value = ''
    return
  }

  if (file.size > 2 * 1024 * 1024) {
    toastError('图片大小不能超过 2MB')
    fileInput.value.value = ''
    return
  }

  const reader = new FileReader()
  reader.onload = (ev) => {
    previewUrl.value = ev.target.result
  }
  reader.readAsDataURL(file)

  uploading.value = true
  progress.value = 0

  try {
    const formData = new FormData()
    formData.append('file', file)
    if (props.userId) {
      formData.append('target_user_id', props.userId)
    }

    const res = await api.post('/avatar/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: (ev) => {
        if (ev.total) progress.value = Math.round((ev.loaded / ev.total) * 100)
      },
    })

    const data = res.data?.data || res.data
    if (data.avatar) {
      previewUrl.value = resolveUrl(data.avatar)
      emit('update:modelValue', data.avatar)
      emit('uploaded', data.avatar)
    }
  } catch (err) {
    const detail = err.response?.data?.detail || err.message || '上传失败'
    toastError(detail)
    previewUrl.value = resolveUrl(props.modelValue)
  } finally {
    uploading.value = false
    fileInput.value.value = ''
  }
}
</script>

<style scoped>
.avatar-uploader {
  display: inline-flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
}

.avatar-preview {
  position: relative;
  width: v-bind(size + 'px');
  height: v-bind(size + 'px');
  border-radius: 50%;
  overflow: hidden;
  border: 2px solid var(--border);
  transition: border-color 0.2s;
}

.avatar-preview:not(.readonly) {
  cursor: pointer;
}

.avatar-preview:not(.readonly):hover {
  border-color: var(--accent);
}

.avatar-preview.readonly {
  cursor: default;
}

.avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: var(--bg-tab);
  color: var(--text-muted);
}

.placeholder-icon {
  font-size: 24px;
}

.placeholder-text {
  font-size: 11px;
  margin-top: 2px;
}

.avatar-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.2s;
}

.avatar-overlay span {
  color: white;
  font-size: 13px;
  font-weight: 600;
}

.avatar-preview:not(.readonly):hover .avatar-overlay {
  opacity: 1;
}

.upload-progress {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
}

.progress-bar {
  flex: 1;
  height: 4px;
  background: var(--bg-tab);
  border-radius: 2px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: var(--accent);
  border-radius: 2px;
  transition: width 0.3s;
}

.progress-text {
  font-size: 12px;
  color: var(--text-secondary);
  white-space: nowrap;
  min-width: 32px;
  text-align: right;
}
</style>
