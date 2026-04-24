<template>
  <div class="login-page">
    <div class="splash-content">
      <div class="splash-logo">👛</div>
      <div class="splash-title">轻松记账</div>
      <div class="splash-subtitle">简单 · 纯粹 · 掌握生活</div>
      <div class="login-form">
        <div class="input-group">
          <input
            v-model="password"
            type="password"
            placeholder="请输入访问密码"
            class="login-input"
            @keyup.enter="handleLogin"
          />
        </div>
        <button class="btn-primary login-btn" @click="handleLogin" :disabled="loading">
          <span v-if="loading" class="loading-spinner"></span>
          <span v-else>登 录</span>
        </button>
        <div v-if="error" class="error-msg">{{ error }}</div>
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

const password = ref('')
const loading = ref(false)
const error = ref('')

async function handleLogin() {
  if (!password.value) {
    error.value = '请输入密码'
    return
  }
  loading.value = true
  error.value = ''
  try {
    const success = await authStore.login(password.value)
    if (success) {
      router.push('/')
    } else {
      error.value = '密码错误'
    }
  } catch (e) {
    error.value = e.response?.data?.detail || '登录失败'
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

.splash-content {
  text-align: center;
  width: 100%;
  max-width: 360px;
}

.splash-logo {
  width: 120px;
  height: 120px;
  background: linear-gradient(145deg, #f0d9b8, #e8c99a);
  border-radius: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 52px;
  box-shadow: 0 12px 40px rgba(200, 170, 120, 0.3);
  margin: 0 auto 28px;
}

.splash-title {
  font-size: 34px;
  font-weight: 800;
  color: var(--text-primary);
  letter-spacing: 4px;
  margin-bottom: 10px;
}

.splash-subtitle {
  font-size: 15px;
  color: var(--text-muted);
  letter-spacing: 6px;
  font-weight: 400;
  margin-bottom: 48px;
}

.login-form {
  width: 100%;
}

.input-group {
  margin-bottom: 16px;
}

.login-input {
  width: 100%;
  padding: 14px 20px;
  border: 1.5px solid var(--border);
  border-radius: 14px;
  font-size: 16px;
  background: var(--bg-card);
  color: var(--text-primary);
  transition: border-color 0.2s;
}

.login-input:focus {
  border-color: var(--accent);
}

.login-input::placeholder {
  color: var(--text-light);
}

.login-btn {
  width: 100%;
  padding: 14px;
  font-size: 17px;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 50px;
}

.error-msg {
  color: var(--danger);
  font-size: 13px;
  margin-top: 12px;
}
</style>
