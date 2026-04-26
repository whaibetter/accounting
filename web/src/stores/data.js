import { defineStore } from 'pinia'
import { ref } from 'vue'
import { billApi, accountApi, categoryApi, tagApi, statisticsApi } from '@/services'
import dayjs from 'dayjs'

export const useBillStore = defineStore('bill', () => {
  const bills = ref([])
  const total = ref(0)
  const currentPage = ref(1)
  const pageSize = ref(20)
  const loading = ref(false)

  async function fetchBills(params = {}) {
    loading.value = true
    try {
      const res = await billApi.list({
        page: params.page || currentPage.value,
        size: params.size || pageSize.value,
        start_date: params.start_date,
        end_date: params.end_date,
        type: params.type,
        category_id: params.category_id,
        account_id: params.account_id,
        keyword: params.keyword,
      })
      if (res.data.code === 200) {
        if (params.append) {
          bills.value = [...bills.value, ...res.data.data.items]
        } else {
          bills.value = res.data.data.items
        }
        total.value = res.data.data.total
        currentPage.value = res.data.data.page
        pageSize.value = res.data.data.size
      }
    } finally {
      loading.value = false
    }
  }

  async function createBill(data) {
    const res = await billApi.create(data)
    return res.data
  }

  async function updateBill(id, data) {
    const res = await billApi.update(id, data)
    return res.data
  }

  async function deleteBill(id) {
    const res = await billApi.delete(id)
    return res.data
  }

  return { bills, total, currentPage, pageSize, loading, fetchBills, createBill, updateBill, deleteBill }
})

export const useAccountStore = defineStore('account', () => {
  const accounts = ref([])
  const loading = ref(false)

  async function fetchAccounts() {
    loading.value = true
    try {
      const res = await accountApi.list()
      if (res.data.code === 200) {
        accounts.value = res.data.data
      }
    } finally {
      loading.value = false
    }
  }

  async function createAccount(data) {
    const res = await accountApi.create(data)
    return res.data
  }

  async function updateAccount(id, data) {
    const res = await accountApi.update(id, data)
    return res.data
  }

  async function deleteAccount(id) {
    const res = await accountApi.delete(id)
    return res.data
  }

  const totalAssets = () => {
    return accounts.value
      .filter(a => a.status === 1 && a.type !== 3)
      .reduce((sum, a) => sum + a.balance, 0)
  }

  const totalDebts = () => {
    return accounts.value
      .filter(a => a.status === 1 && a.type === 3)
      .reduce((sum, a) => sum + Math.abs(a.balance), 0)
  }

  return { accounts, loading, fetchAccounts, createAccount, updateAccount, deleteAccount, totalAssets, totalDebts }
})

export const useCategoryStore = defineStore('category', () => {
  const categories = ref([])
  const loading = ref(false)

  async function fetchCategories(type) {
    loading.value = true
    try {
      const res = await categoryApi.list(type ? { type } : {})
      if (res.data.code === 200) {
        categories.value = res.data.data
      }
    } finally {
      loading.value = false
    }
  }

  async function createCategory(data) {
    const res = await categoryApi.create(data)
    return res.data
  }

  async function updateCategory(id, data) {
    const res = await categoryApi.update(id, data)
    return res.data
  }

  async function deleteCategory(id) {
    const res = await categoryApi.delete(id)
    return res.data
  }

  const flatCategories = () => {
    const result = []
    const flatten = (cats) => {
      for (const cat of cats) {
        result.push(cat)
        if (cat.children && cat.children.length) {
          flatten(cat.children)
        }
      }
    }
    flatten(categories.value)
    return result
  }

  return { categories, loading, fetchCategories, createCategory, updateCategory, deleteCategory, flatCategories }
})

export const useTagStore = defineStore('tag', () => {
  const tags = ref([])
  const loading = ref(false)

  async function fetchTags() {
    loading.value = true
    try {
      const res = await tagApi.list()
      if (res.data.code === 200) {
        tags.value = res.data.data
      }
    } finally {
      loading.value = false
    }
  }

  async function createTag(data) {
    const res = await tagApi.create(data)
    return res.data
  }

  async function updateTag(id, data) {
    const res = await tagApi.update(id, data)
    return res.data
  }

  async function deleteTag(id) {
    const res = await tagApi.delete(id)
    return res.data
  }

  return { tags, loading, fetchTags, createTag, updateTag, deleteTag }
})

export const useStatisticsStore = defineStore('statistics', () => {
  const overview = ref(null)
  const categoryStats = ref([])
  const trend = ref([])
  const balanceTrend = ref([])
  const loading = ref(false)

  async function fetchOverview(params = {}) {
    loading.value = true
    try {
      const res = await statisticsApi.overview(params)
      if (res.data.code === 200) {
        overview.value = res.data.data
      }
    } finally {
      loading.value = false
    }
  }

  async function fetchCategoryStats(params = {}) {
    try {
      const res = await statisticsApi.byCategory(params)
      if (res.data.code === 200) {
        categoryStats.value = res.data.data
      }
    } catch (e) {
      console.error(e)
    }
  }

  async function fetchTrend(params) {
    try {
      const res = await statisticsApi.trend(params)
      if (res.data.code === 200) {
        trend.value = res.data.data
      }
    } catch (e) {
      console.error(e)
    }
  }

  async function fetchBalanceTrend(params) {
    try {
      const res = await statisticsApi.balanceTrend(params)
      if (res.data.code === 200) {
        balanceTrend.value = res.data.data
      }
    } catch (e) {
      console.error(e)
    }
  }

  return {
    overview, categoryStats, trend, balanceTrend, loading,
    fetchOverview, fetchCategoryStats, fetchTrend, fetchBalanceTrend,
  }
})
