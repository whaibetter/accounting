import axios from 'axios'
import { useAuthStore } from '@/stores/auth'
import router from '@/router'

const isDev = import.meta.env.DEV
const apiTarget = import.meta.env.VITE_API_TARGET || ''

const api = axios.create({
  baseURL: isDev && apiTarget
    ? `${apiTarget}/api/v1`
    : '/accountig/api/v1',
  timeout: 10000,
})

const llmApi = axios.create({
  baseURL: isDev && apiTarget
    ? `${apiTarget}/api/v1`
    : '/accountig/api/v1',
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
