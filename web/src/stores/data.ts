import { defineStore } from 'pinia'
import { ref } from 'vue'
import { accountApi, categoryApi, tagApi, type Account, type Category, type Tag } from '@/api/types'

export const useDataStore = defineStore('data', () => {
  const accounts = ref<Account[]>([])
  const expenseCategories = ref<Category[]>([])
  const incomeCategories = ref<Category[]>([])
  const tags = ref<Tag[]>([])
  const loaded = ref(false)

  async function loadAll() {
    if (loaded.value) return
    try {
      const [accRes, expRes, incRes, tagRes] = await Promise.all([
        accountApi.list(),
        categoryApi.list(1),
        categoryApi.list(2),
        tagApi.list(),
      ])
      accounts.value = accRes.data || []
      expenseCategories.value = expRes.data || []
      incomeCategories.value = incRes.data || []
      tags.value = tagRes.data || []
      loaded.value = true
    } catch (e) {
      console.error('Failed to load data:', e)
    }
  }

  async function refreshAccounts() {
    try {
      const res = await accountApi.list()
      accounts.value = res.data || []
    } catch (e) {
      console.error('Failed to refresh accounts:', e)
    }
  }

  async function refreshTags() {
    try {
      const res = await tagApi.list()
      tags.value = res.data || []
    } catch (e) {
      console.error('Failed to refresh tags:', e)
    }
  }

  function getAccountName(id: number) {
    return accounts.value.find((a) => a.id === id)?.name || ''
  }

  function getCategoryName(id: number) {
    const find = (cats: Category[]) => {
      for (const c of cats) {
        if (c.id === id) return c.name
        if (c.children) {
          const found = find(c.children)
          if (found) return found
        }
      }
      return ''
    }
    return find(expenseCategories.value) || find(incomeCategories.value) || ''
  }

  return {
    accounts,
    expenseCategories,
    incomeCategories,
    tags,
    loaded,
    loadAll,
    refreshAccounts,
    refreshTags,
    getAccountName,
    getCategoryName,
  }
})
