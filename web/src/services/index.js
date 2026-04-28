import api from './api'
import { useAuthStore } from '@/stores/auth'

export const authApi = {
  login(username, password) {
    return api.post('/auth/login', { username, password })
  },
  register(username, password) {
    return api.post('/auth/register', { username, password })
  },
  getProfile() {
    return api.get('/auth/profile')
  },
  updateProfile(data) {
    return api.put('/auth/profile', data)
  },
  changePassword(data) {
    return api.post('/auth/change-password', data)
  },
}

export const billApi = {
  list(params) {
    return api.get('/bills', { params })
  },
  get(id) {
    return api.get(`/bills/${id}`)
  },
  create(data) {
    return api.post('/bills', data)
  },
  update(id, data) {
    return api.put(`/bills/${id}`, data)
  },
  delete(id) {
    return api.delete(`/bills/${id}`)
  },
}

export const accountApi = {
  list() {
    return api.get('/accounts')
  },
  get(id) {
    return api.get(`/accounts/${id}`)
  },
  create(data) {
    return api.post('/accounts', data)
  },
  update(id, data) {
    return api.put(`/accounts/${id}`, data)
  },
  delete(id) {
    return api.delete(`/accounts/${id}`)
  },
}

export const categoryApi = {
  list(params) {
    return api.get('/categories', { params })
  },
  create(data) {
    return api.post('/categories', data)
  },
  update(id, data) {
    return api.put(`/categories/${id}`, data)
  },
  delete(id, cascade = false) {
    return api.delete(`/categories/${id}`, { params: { cascade } })
  },
}

export const tagApi = {
  list() {
    return api.get('/tags')
  },
  create(data) {
    return api.post('/tags', data)
  },
  update(id, data) {
    return api.put(`/tags/${id}`, data)
  },
  delete(id) {
    return api.delete(`/tags/${id}`)
  },
}

export const statisticsApi = {
  overview(params) {
    return api.get('/statistics/overview', { params })
  },
  byCategory(params) {
    return api.get('/statistics/by-category', { params })
  },
  trend(params) {
    return api.get('/statistics/trend', { params })
  },
  balanceTrend(params) {
    return api.get('/statistics/balance-trend', { params })
  },
}

export const exportApi = {
  excel(params) {
    return api.get('/export/excel', { params, responseType: 'blob' })
  },
  json(params) {
    return api.get('/export/json', { params, responseType: 'blob' })
  },
}

export const importApi = {
  accounts(data) {
    return api.post('/import/accounts', data)
  },
  bills(data) {
    return api.post('/import/bills', data)
  },
}

export const llmApi = {
  getConfig() {
    return api.get('/llm/config')
  },
  getConfigForEdit() {
    return api.get('/llm/config/edit')
  },
  updateConfig(data) {
    return api.put('/llm/config', data)
  },
  getProviders() {
    return api.get('/llm/providers')
  },
  getSavedProviders() {
    return api.get('/llm/providers/saved')
  },
  saveProviderConfig(data) {
    return api.post('/llm/providers/save', data)
  },
  loadProviderConfig(name) {
    return api.post('/llm/providers/load', { name })
  },
  deleteProviderConfig(name) {
    return api.post('/llm/providers/delete', { name })
  },
  testConnection() {
    return api.post('/llm/test')
  },
  testConnectionStream(onEvent) {
    const authStore = useAuthStore()
    const token = authStore.token
    const baseUrl = api.defaults.baseURL || '/accounting/api/v1'
    const url = `${baseUrl}/llm/test/stream?token=${encodeURIComponent(token)}`

    return new Promise((resolve, reject) => {
      const evtSource = new EventSource(url)

      evtSource.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          onEvent(data)
          if (data.phase === 'completed' || data.phase === 'error') {
            evtSource.close()
            resolve(data)
          }
        } catch (e) {
          console.error('SSE parse error:', e)
        }
      }

      evtSource.onerror = () => {
        evtSource.close()
        reject(new Error('SSE连接失败，请检查网络或刷新页面重试'))
      }

      setTimeout(() => {
        evtSource.close()
        reject(new Error('SSE连接超时'))
      }, 120000)
    })
  },
  parse(text) {
    return api.post('/llm/parse', { text })
  },
  parseAndImport(data) {
    return api.post('/llm/parse-import', data)
  },
}
