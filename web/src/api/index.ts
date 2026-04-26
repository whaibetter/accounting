import axios from 'axios'
import { useAuthStore } from '@/stores/auth'
import router from '@/router'

const isDev = import.meta.env.DEV
const appEnv = import.meta.env.VITE_APP_ENV || 'development'
const apiTarget = import.meta.env.VITE_API_TARGET || ''

let baseURL: string
if (isDev && !apiTarget) {
  baseURL = '/api/v1'
} else if (apiTarget) {
  baseURL = `${apiTarget}/api/v1`
} else {
  baseURL = '/accountig/api/v1'
}

const api = axios.create({
  baseURL,
  timeout: 10000,
})

const llmApi = axios.create({
  baseURL,
  timeout: 120000,
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (res) => res.data,
  (err) => {
    if (err.response?.status === 401) {
      const auth = useAuthStore()
      auth.clearToken()
      router.push('/login')
      return Promise.reject(new Error('登录已过期，请重新登录'))
    }
    const msg = err.response?.data?.detail || err.message || '请求失败'
    return Promise.reject(new Error(msg))
  }
)

llmApi.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

llmApi.interceptors.response.use(
  (res) => res.data,
  (err) => {
    if (err.response?.status === 401) {
      const auth = useAuthStore()
      auth.clearToken()
      router.push('/login')
      return Promise.reject(new Error('登录已过期，请重新登录'))
    }
    const msg = err.response?.data?.detail || err.message || '请求失败'
    return Promise.reject(new Error(msg))
  }
)

export default api
export { llmApi }
