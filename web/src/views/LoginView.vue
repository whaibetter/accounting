<template>
  <div class="login-page">
    <div class="login-card">
      <div class="login-header">
        <div class="logo">💰</div>
        <h1 class="app-title">记账本</h1>
        <p class="app-subtitle">{{ isRegister ? '创建新账户' : '登录您的账户' }}</p>
      </div>

      <div class="login-form">
        <div class="form-field">
          <label>用户名</label>
          <input
            v-model="form.username"
            type="text"
            placeholder="请输入用户名"
            @keyup.enter="handleSubmit"
          />
        </div>
        <div class="form-field">
          <label>密码</label>
          <input
            v-model="form.password"
            type="password"
            :placeholder="isRegister ? '至少6位，需含字母和数字' : '请输入密码'"
            @keyup.enter="handleSubmit"
          />
        </div>
        <div v-if="isRegister" class="form-field">
          <label>确认密码</label>
          <input
            v-model="form.confirmPassword"
            type="password"
            placeholder="请再次输入密码"
            @keyup.enter="handleSubmit"
          />
        </div>

        <div v-if="errorMsg" class="error-msg">{{ errorMsg }}</div>

        <button class="btn-submit" @click="handleSubmit" :disabled="loading">
          {{ loading ? '处理中...' : (isRegister ? '注册' : '登录') }}
        </button>

        <div class="switch-mode">
          <span @click="toggleMode">
            {{ isRegister ? '已有账户？去登录' : '没有账户？去注册' }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const isRegister = ref(false)
const loading = ref(false)
const errorMsg = ref('')
const form = ref({
  username: '',
  password: '',
  confirmPassword: '',
})

function toggleMode() {
  isRegister.value = !isRegister.value
  errorMsg.value = ''
  form.value.confirmPassword = ''
}

async function handleSubmit() {
  errorMsg.value = ''

  if (!form.value.username.trim()) {
    errorMsg.value = '请输入用户名'
    return
  }
  if (!form.value.password) {
    errorMsg.value = '请输入密码'
    return
  }
  if (isRegister.value) {
    if (form.value.password !== form.value.confirmPassword) {
      errorMsg.value = '两次密码输入不一致'
      return
    }
  }

  loading.value = true
  try {
    if (isRegister.value) {
      await authStore.register(form.value.username.trim(), form.value.password)
    } else {
      await authStore.login(form.value.username.trim(), form.value.password)
    }
    router.replace('/')
  } catch (e) {
    const detail = e.response?.data?.detail || e.message
    errorMsg.value = detail || (isRegister.value ? '注册失败' : '用户名或密码错误')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-primary);
  padding: 20px;
}

.login-card {
  width: 100%;
  max-width: 380px;
  background: var(--bg-card);
  border-radius: 24px;
  padding: 40px 28px;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.06);
}

.login-header {
  text-align: center;
  margin-bottom: 32px;
}

.logo {
  font-size: 48px;
  margin-bottom: 12px;
}

.app-title {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 4px;
}

.app-subtitle {
  font-size: 14px;
  color: var(--text-secondary);
  margin: 0;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-field label {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-secondary);
}

.form-field input {
  padding: 12px 16px;
  border: 1.5px solid var(--border);
  border-radius: 12px;
  font-size: 15px;
  color: var(--text-primary);
  background: var(--bg-input);
  outline: none;
  transition: border-color 0.2s;
}

.form-field input:focus {
  border-color: var(--accent);
}

.form-field input::placeholder {
  color: var(--text-muted);
}

.error-msg {
  font-size: 13px;
  color: var(--danger);
  padding: 8px 12px;
  background: rgba(239, 68, 68, 0.08);
  border-radius: 8px;
}

.btn-submit {
  padding: 14px;
  border: none;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  color: white;
  background: var(--accent);
  cursor: pointer;
  transition: opacity 0.2s;
  margin-top: 4px;
}

.btn-submit:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-submit:not(:disabled):hover {
  opacity: 0.9;
}

.switch-mode {
  text-align: center;
  margin-top: 8px;
}

.switch-mode span {
  font-size: 14px;
  color: var(--accent);
  cursor: pointer;
}

.switch-mode span:hover {
  text-decoration: underline;
}
</style>
