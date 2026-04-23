import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

const TOKEN_KEY = 'access_token'

export const useAuthStore = defineStore('auth', () => {
  const accessToken = ref(localStorage.getItem(TOKEN_KEY) || '')

  const isAuthenticated = computed(() => !!accessToken.value)

  function setToken(token: string) {
    accessToken.value = token
    localStorage.setItem(TOKEN_KEY, token)
  }

  function clearToken() {
    accessToken.value = ''
    localStorage.removeItem(TOKEN_KEY)
  }

  return {
    accessToken,
    isAuthenticated,
    setToken,
    clearToken,
  }
})
