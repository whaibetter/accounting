import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '@/services'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || '')
  const isAuthenticated = computed(() => !!token.value)

  async function login(password) {
    const res = await authApi.login(password)
    if (res.data.code === 200) {
      token.value = res.data.data.access_token
      localStorage.setItem('token', token.value)
      return true
    }
    return false
  }

  function logout() {
    token.value = ''
    localStorage.removeItem('token')
  }

  return { token, isAuthenticated, login, logout }
})
