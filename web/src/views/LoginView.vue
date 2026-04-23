<template>
  <div class="login-page">
    <div class="login-card">
      <div class="login-icon">🔐</div>
      <h1 class="login-title">记账助手</h1>
      <p class="login-desc">请输入访问密码以登录系统</p>

      <form @submit.prevent="handleLogin" class="login-form">
        <div class="input-group">
          <input
            v-model="password"
            :type="showPassword ? 'text' : 'password'"
            placeholder="请输入访问密码"
            autocomplete="current-password"
            class="login-input"
            ref="passwordInput"
          />
          <button type="button" class="toggle-pwd" @click="showPassword = !showPassword">
            {{ showPassword ? '🙈' : '👁️' }}
          </button>
        </div>

        <button type="submit" class="btn-primary login-btn" :disabled="loading || !password">
          <span v-if="loading" class="spinner"></span>
          <span v-else>登 录</span>
        </button>
      </form>

      <p class="login-hint" v-if="errorMsg">
        <span class="error-text">{{ errorMsg }}</span>
      </p>

      <div class="login-info">
        <p>登录后凭证有效期为 7 天</p>
        <p>期间内无需重复输入密码</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { authApi } from '@/api/types'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const auth = useAuthStore()
const password = ref('')
const showPassword = ref(false)
const loading = ref(false)
const errorMsg = ref('')
const passwordInput = ref<HTMLInputElement | null>(null)

onMounted(() => {
  passwordInput.value?.focus()
})

async function handleLogin() {
  if (!password.value) return
  loading.value = true
  errorMsg.value = ''
  try {
    const res = await authApi.login(password.value)
    const token = res.data?.access_token
    if (token) {
      auth.setToken(token)
      router.replace('/')
    } else {
      errorMsg.value = '登录返回数据异常'
    }
  } catch (e: any) {
    errorMsg.value = e.message || '登录失败，请重试'
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
  padding: 20px;
}

.login-card {
  width: 100%;
  max-width: 360px;
  text-align: center;
  animation: fadeUp 0.5s ease;
}

.login-icon {
  font-size: 64px;
  margin-bottom: 16px;
}

.login-title {
  font-size: 28px;
  font-weight: 800;
  letter-spacing: -0.5px;
  margin-bottom: 8px;
}

.login-desc {
  font-size: 14px;
  color: var(--text-secondary);
  margin-bottom: 32px;
  line-height: 1.5;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.input-group {
  position: relative;
  display: flex;
  align-items: center;
}

.login-input {
  padding-right: 48px;
}

.toggle-pwd {
  position: absolute;
  right: 12px;
  background: none;
  font-size: 18px;
  padding: 4px;
  line-height: 1;
  opacity: 0.6;
}

.toggle-pwd:active {
  opacity: 1;
}

.login-btn {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  height: 52px;
  font-size: 16px;
  letter-spacing: 4px;
}

.login-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.spinner {
  width: 22px;
  height: 22px;
  border: 2.5px solid rgba(255, 255, 255, 0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}

.error-text {
  color: var(--expense);
  font-size: 13px;
}

.login-hint {
  margin-top: 4px;
  min-height: 20px;
}

.login-info {
  margin-top: 32px;
  padding: 16px;
  background: var(--bg-card);
  border-radius: var(--radius-sm);
  border: 1px solid var(--border);
}

.login-info p {
  font-size: 12px;
  color: var(--text-muted);
  line-height: 1.8;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
