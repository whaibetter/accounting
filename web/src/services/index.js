import api from './api'

export const authApi = {
  login(password) {
    return api.post('/auth/login', { password })
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
  updateConfig(data) {
    return api.put('/llm/config', data)
  },
  getProviders() {
    return api.get('/llm/providers')
  },
  testConnection() {
    return api.post('/llm/test')
  },
  parse(text) {
    return api.post('/llm/parse', { text })
  },
  parseAndImport(data) {
    return api.post('/llm/parse-import', data)
  },
}
