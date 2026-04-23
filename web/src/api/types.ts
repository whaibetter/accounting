import api, { llmApi as llmApiClient } from './index'

export interface Account {
  id: number
  name: string
  type: number
  icon: string
  color: string
  balance: number
  initial_balance: number
  is_default: number
  status: number
  created_at: string
  updated_at: string
}

export interface Category {
  id: number
  parent_id: number | null
  name: string
  type: number
  icon: string
  sort_order: number
  children: Category[]
}

export interface Tag {
  id: number
  name: string
  color: string
  created_at: string
}

export interface Bill {
  id: number
  account_id: number
  account_name: string
  category_id: number
  category_name: string
  category_icon: string
  type: number
  amount: number
  bill_date: string
  bill_time: string | null
  remark: string
  tags: { id: number; name: string; color: string }[]
  transfer_to_account_id: number | null
  created_at: string
  updated_at: string
}

export interface Overview {
  total_income: number
  total_expense: number
  balance: number
  bill_count: number
}

export interface CategoryStat {
  category_id: number
  category_name: string
  category_icon: string
  amount: number
  percentage: number
  bill_count: number
}

export interface TrendItem {
  period: string
  income: number
  expense: number
}

export interface BalanceTrendItem {
  date: string
  balance: number
}

export interface AccountBalanceTrend {
  account_id: number
  account_name: string
  data: BalanceTrendItem[]
}

export interface PagedData<T> {
  items: T[]
  total: number
  page: number
  size: number
}

export interface ApiResponse<T> {
  code: number
  message: string
  data: T
}

export const authApi = {
  login: (password: string) =>
    api.post<any, ApiResponse<{ access_token: string }>>('/auth/login', { password }),
}

export const accountApi = {
  list: () => api.get<any, ApiResponse<Account[]>>('/accounts'),
  get: (id: number) => api.get<any, ApiResponse<Account>>(`/accounts/${id}`),
  create: (data: any) => api.post<any, ApiResponse<Account>>('/accounts', data),
  update: (id: number, data: any) => api.put<any, ApiResponse<Account>>(`/accounts/${id}`, data),
  delete: (id: number) => api.delete<any, ApiResponse<null>>(`/accounts/${id}`),
}

export const categoryApi = {
  list: (type?: number) => api.get<any, ApiResponse<Category[]>>('/categories', { params: { type } }),
  create: (data: any) => api.post<any, ApiResponse<Category>>('/categories', data),
  update: (id: number, data: any) => api.put<any, ApiResponse<Category>>(`/categories/${id}`, data),
  delete: (id: number) => api.delete<any, ApiResponse<null>>(`/categories/${id}`),
}

export const tagApi = {
  list: () => api.get<any, ApiResponse<Tag[]>>('/tags'),
  create: (data: any) => api.post<any, ApiResponse<Tag>>('/tags', data),
  update: (id: number, data: any) => api.put<any, ApiResponse<Tag>>(`/tags/${id}`, data),
  delete: (id: number) => api.delete<any, ApiResponse<null>>(`/tags/${id}`),
}

export const billApi = {
  list: (params: any) => api.get<any, ApiResponse<PagedData<Bill>>>('/bills', { params }),
  get: (id: number) => api.get<any, ApiResponse<Bill>>(`/bills/${id}`),
  create: (data: any) => api.post<any, ApiResponse<Bill>>('/bills', data),
  update: (id: number, data: any) => api.put<any, ApiResponse<Bill>>(`/bills/${id}`, data),
  delete: (id: number) => api.delete<any, ApiResponse<null>>(`/bills/${id}`),
}

export const statisticsApi = {
  overview: (params?: any) => api.get<any, ApiResponse<Overview>>('/statistics/overview', { params }),
  byCategory: (params?: any) => api.get<any, ApiResponse<CategoryStat[]>>('/statistics/by-category', { params }),
  trend: (params: any) => api.get<any, ApiResponse<TrendItem[]>>('/statistics/trend', { params }),
  balanceTrend: (params: any) => api.get<any, ApiResponse<AccountBalanceTrend[]>>('/statistics/balance-trend', { params }),
}

export interface ImportResult {
  success: number
  skipped?: number
  errors: any[]
}

export const importApi = {
  importAccounts: (accounts: any[]) => api.post<any, ApiResponse<ImportResult>>('/import/accounts', { accounts }),
  importBills: (bills: any[]) => api.post<any, ApiResponse<ImportResult>>('/import/bills', { bills }),
}

export interface LlmConfig {
  provider: string
  api_key: string
  api_key_masked?: string
  base_url: string
  model: string
  temperature: number
  max_tokens: number
  timeout: number
  is_configured: boolean
}

export interface LlmProvider {
  name: string
  default_base_url: string
  default_model: string
  models: string[]
}

export interface ParseResult {
  success: boolean
  bills: ParsedBill[]
  raw_response?: string
  error?: string
}

export interface ParsedBill {
  type: number
  amount: number
  category: string
  date: string
  time: string | null
  remark: string
  account: string | null
  payment_method: string | null
}

export interface ParseAndImportResult {
  parse_result: ParseResult
  import_result: ImportResult | null
}

export const llmApi = {
  getConfig: () => api.get<any, ApiResponse<LlmConfig>>('/llm/config'),
  updateConfig: (data: Partial<LlmConfig>) => api.put<any, ApiResponse<LlmConfig>>('/llm/config', data),
  getProviders: () => api.get<any, ApiResponse<Record<string, LlmProvider>>>('/llm/providers'),
  testConnection: () => llmApiClient.post<any, ApiResponse<{ success: boolean; message: string; model?: string }>>('/llm/test'),
  parseText: (text: string) => llmApiClient.post<any, ApiResponse<ParseResult>>('/llm/parse', { text }),
  parseAndImport: (text: string, defaultAccount?: string) =>
    llmApiClient.post<any, ApiResponse<ParseAndImportResult>>('/llm/parse-import', { text, default_account: defaultAccount }),
}
