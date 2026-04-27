<template>
  <div class="avatar-uploader">
    <div class="avatar-preview" @click="triggerUpload">
      <img v-if="previewUrl" :src="previewUrl" class="avatar-img" />
      <div v-else class="avatar-placeholder">
        <span class="placeholder-icon">📷</span>
        <span class="placeholder-text">上传头像</span>
      </div>
      <div class="avatar-overlay">
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
      <span class="progress-text">上传中...</span>
    </div>
    <div v-if="errorMsg" class="upload-error">{{ errorMsg }}</div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import api from '@/services/api'

const props = defineProps({
  modelValue: { type: String, default: '' },
  size: { type: Number, default: 80 },
})

const emit = defineEmits(['update:modelValue', 'uploaded'])

const fileInput = ref(null)
const previewUrl = ref(props.modelValue || '')
const uploading = ref(false)
const progress = ref(0)
const errorMsg = ref('')

watch(() => props.modelValue, (val) => {
  if (val && !val.startsWith('data:')) {
    const base = api.defaults?.baseURL ? api.defaults.baseURL.replace('/api/v1', '') : ''
    previewUrl.value = val.startsWith('http') ? val : base + val
  } else {
    previewUrl.value = val
  }
})

function triggerUpload() {
  if (uploading.value) return
  fileInput.value.click()
}

async function handleFileSelect(e) {
  const file = e.target.files?.[0]
  if (!file) return

  errorMsg.value = ''

  const allowedTypes = ['image/jpeg', 'image/png', 'image/webp']
  if (!allowedTypes.includes(file.type)) {
    errorMsg.value = '仅支持 JPG、PNG、WebP 格式'
    fileInput.value.value = ''
    return
  }

  if (file.size > 2 * 1024 * 1024) {
    errorMsg.value = '图片大小不能超过 2MB'
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

    const res = await api.post('/avatar/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: (e) => {
        if (e.total) progress.value = Math.round((e.loaded / e.total) * 100)
      },
    })

    const data = res.data?.data || res.data
    if (data.avatar) {
      const base = api.defaults?.baseURL ? api.defaults.baseURL.replace('/api/v1', '') : ''
      previewUrl.value = data.avatar.startsWith('http') ? data.avatar : base + data.avatar
      emit('update:modelValue', data.avatar)
      emit('uploaded', data.avatar)
    }
  } catch (err) {
    const detail = err.response?.data?.detail || err.message || '上传失败'
    errorMsg.value = detail
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
  gap: 8px;
}

.avatar-preview {
  position: relative;
  width: v-bind(size + 'px');
  height: v-bind(size + 'px');
  border-radius: 50%;
  overflow: hidden;
  cursor: pointer;
  border: 2px solid var(--border);
  transition: border-color 0.2s;
}

.avatar-preview:hover {
  border-color: var(--accent);
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

.avatar-preview:hover .avatar-overlay {
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
}

.upload-error {
  font-size: 12px;
  color: var(--danger);
  text-align: center;
}
</style>
