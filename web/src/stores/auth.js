import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/services/api'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || '')
  const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))

  const isLoggedIn = computed(() => !!token.value)
  const username = computed(() => user.value?.username || '')
  const nickname = computed(() => user.value?.nickname || user.value?.username || '')
  const userId = computed(() => user.value?.id || null)

  async function login(usernameVal, password) {
    const res = await api.post('/auth/login', { username: usernameVal, password })
    const data = res.data?.data || res.data
    if (data.access_token) {
      token.value = data.access_token
      localStorage.setItem('token', data.access_token)
      await fetchProfile()
      return true
    }
    throw new Error(res.data?.message || '登录失败')
  }

  async function register(usernameVal, password) {
    const res = await api.post('/auth/register', { username: usernameVal, password })
    const data = res.data?.data || res.data
    if (data.access_token) {
      token.value = data.access_token
      localStorage.setItem('token', data.access_token)
      await fetchProfile()
      return true
    }
    throw new Error(res.data?.message || '注册失败')
  }

  async function fetchProfile() {
    try {
      const res = await api.get('/auth/profile')
      const profile = res.data?.data || res.data
      user.value = profile
      localStorage.setItem('user', JSON.stringify(profile))
    } catch {
      user.value = null
      localStorage.removeItem('user')
    }
  }

  async function updateProfile(updates) {
    const res = await api.put('/auth/profile', updates)
    const profile = res.data?.data || res.data
    user.value = profile
    localStorage.setItem('user', JSON.stringify(profile))
    return profile
  }

  async function changePassword(oldPassword, newPassword) {
    const res = await api.post('/auth/change-password', {
      old_password: oldPassword,
      new_password: newPassword,
    })
    return res.data
  }

  function logout() {
    token.value = ''
    user.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }

  return {
    token, user, isLoggedIn, username, nickname, userId,
    login, register, fetchProfile, updateProfile, changePassword, logout,
  }
})
