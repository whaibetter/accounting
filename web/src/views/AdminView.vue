<template>
  <div class="page admin-page">
    <div class="page-header">
      <h2 class="page-title">后台管理</h2>
    </div>

    <div class="tab-bar">
      <div class="tab-item" :class="{ active: activeTab === 'users' }" @click="activeTab = 'users'">用户管理</div>
      <div class="tab-item" :class="{ active: activeTab === 'logs' }" @click="activeTab = 'logs'">操作日志</div>
    </div>

    <div v-if="activeTab === 'users'" class="section">
      <div class="filter-bar">
        <input v-model="userKeyword" type="text" class="filter-input" placeholder="搜索用户名/昵称/邮箱" @keyup.enter="searchUsers" />
        <select v-model="userStatusFilter" class="filter-select" @change="searchUsers">
          <option :value="null">全部状态</option>
          <option :value="1">正常</option>
          <option :value="0">已禁用</option>
        </select>
        <button class="btn-search" @click="searchUsers">搜索</button>
      </div>

      <div v-if="userLoading" class="empty-state">加载中...</div>
      <div v-else-if="!users.length" class="empty-state">暂无数据</div>
      <div v-else class="user-cards">
        <div v-for="u in users" :key="u.id" class="user-card">
          <div class="user-card-top">
            <div class="user-info-left">
              <img v-if="u.avatar" :src="getAvatarUrl(u.avatar)" class="user-avatar" />
              <span v-else class="avatar-letter">{{ (u.nickname || u.username)?.charAt(0) }}</span>
              <div class="user-info-text">
                <div class="user-name-row">
                  <span class="user-name">{{ u.username }}</span>
                  <span class="role-tag" :class="{ admin: u.is_admin }">{{ u.is_admin ? '管理员' : '用户' }}</span>
                  <span class="status-tag" :class="u.status === 1 ? 'active' : 'disabled'">{{ u.status === 1 ? '正常' : '禁用' }}</span>
                </div>
                <div class="user-meta">{{ u.nickname || '-' }} · {{ u.email || '-' }}</div>
              </div>
            </div>
            <div class="user-actions">
              <button class="btn-action view" @click="viewUserBills(u)">账单</button>
              <button class="btn-action edit" @click="openEditUser(u)">编辑</button>
              <button v-if="u.status === 1 && u.id !== currentUserId" class="btn-action disable" @click="disableUser(u)">禁用</button>
            </div>
          </div>
          <div class="user-card-bottom">
            <span>ID: {{ u.id }}</span>
            <span>注册: {{ formatDate(u.created_at) }}</span>
          </div>
        </div>
      </div>

      <div class="pagination">
        <button class="page-btn" :disabled="userPage <= 1" @click="userPage--; fetchUsers()">上一页</button>
        <span class="page-info">{{ userPage }} / {{ totalUserPages }}</span>
        <button class="page-btn" :disabled="userPage >= totalUserPages" @click="userPage++; fetchUsers()">下一页</button>
      </div>
    </div>

    <div v-if="activeTab === 'logs'" class="section">
      <div class="filter-bar">
        <input v-model="logKeyword" type="text" class="filter-input" placeholder="搜索操作人" @keyup.enter="fetchLogs" />
        <select v-model="logActionFilter" class="filter-select" @change="fetchLogs">
          <option value="">全部操作</option>
          <option value="update_user">编辑用户</option>
          <option value="disable_user">禁用用户</option>
        </select>
        <button class="btn-search" @click="fetchLogs">搜索</button>
      </div>

      <div class="log-list">
        <div v-if="logLoading" class="empty-state">加载中...</div>
        <div v-else-if="!logs.length" class="empty-state">暂无日志</div>
        <div v-for="log in logs" :key="log.id" class="log-item">
          <div class="log-main">
            <span class="log-operator">{{ log.operator_name }}</span>
            <span class="log-action-tag">{{ actionLabel(log.action) }}</span>
            <span v-if="log.target_type" class="log-target">{{ log.target_type }}#{{ log.target_id }}</span>
          </div>
          <div class="log-detail">
            <span v-if="log.detail" class="log-desc">{{ log.detail }}</span>
            <span class="log-meta">{{ formatDate(log.created_at) }} · {{ log.ip_address || '-' }}</span>
          </div>
        </div>
      </div>

      <div class="pagination">
        <button class="page-btn" :disabled="logPage <= 1" @click="logPage--; fetchLogs()">上一页</button>
        <span class="page-info">{{ logPage }} / {{ totalLogPages }}</span>
        <button class="page-btn" :disabled="logPage >= totalLogPages" @click="logPage++; fetchLogs()">下一页</button>
      </div>
    </div>

    <div v-if="editingUser" class="modal-overlay" @click.self="editingUser = null">
      <div class="edit-modal">
        <div class="edit-header">
          <h3>编辑用户</h3>
          <span class="modal-close" @click="editingUser = null">✕</span>
        </div>
        <div class="edit-body">
          <div class="edit-field">
            <label>头像</label>
            <AvatarUploader :modelValue="editForm.avatar" :size="64" @uploaded="onEditAvatarUploaded" />
          </div>
          <div class="edit-field">
            <label>用户名</label>
            <input type="text" :value="editForm.username" disabled class="edit-input disabled" />
          </div>
          <div class="edit-field">
            <label>昵称</label>
            <input type="text" v-model="editForm.nickname" class="edit-input" />
          </div>
          <div class="edit-field">
            <label>邮箱</label>
            <input type="email" v-model="editForm.email" class="edit-input" />
          </div>
          <div class="edit-field">
            <label>手机号</label>
            <input type="tel" v-model="editForm.phone" class="edit-input" />
          </div>
          <div class="edit-field">
            <label>角色</label>
            <select v-model="editForm.is_admin" class="edit-input">
              <option :value="0">普通用户</option>
              <option :value="1">管理员</option>
            </select>
          </div>
          <div class="edit-field">
            <label>状态</label>
            <select v-model="editForm.status" class="edit-input">
              <option :value="1">正常</option>
              <option :value="0">禁用</option>
            </select>
          </div>
          <div class="edit-field">
            <label>重置密码</label>
            <input type="password" v-model="editForm.password" placeholder="留空则不修改" class="edit-input" />
          </div>
        </div>
        <div class="edit-footer">
          <button class="btn-cancel" @click="editingUser = null">取消</button>
          <button class="btn-primary" @click="saveEditUser" :disabled="savingUser">
            {{ savingUser ? '保存中...' : '保存' }}
          </button>
        </div>
      </div>
    </div>

    <div v-if="viewingBills" class="modal-overlay" @click.self="viewingBills = null">
      <div class="bills-modal">
        <div class="edit-header">
          <h3>{{ billUserName }} 的账单</h3>
          <span class="modal-close" @click="viewingBills = null">✕</span>
        </div>
        <div class="bills-filter">
          <input type="date" v-model="billStartDate" class="filter-input-sm" />
          <span class="filter-sep">至</span>
          <input type="date" v-model="billEndDate" class="filter-input-sm" />
          <select v-model="billTypeFilter" class="filter-select-sm">
            <option :value="null">全部</option>
            <option :value="1">支出</option>
            <option :value="2">收入</option>
          </select>
          <button class="btn-search-sm" @click="fetchUserBills">筛选</button>
          <button class="btn-export" @click="exportUserBills">导出</button>
        </div>
        <div class="bills-summary">
          <span class="summary-item">共 {{ billTotal }} 条</span>
          <span class="summary-item income">收入 ¥{{ billSummary.total_income.toFixed(2) }}</span>
          <span class="summary-item expense">支出 ¥{{ billSummary.total_expense.toFixed(2) }}</span>
        </div>
        <div class="bills-list">
          <div v-if="billLoading" class="empty-state">加载中...</div>
          <div v-else-if="!bills.length" class="empty-state">暂无账单</div>
          <div v-for="b in bills" :key="b.id" class="bill-item">
            <div class="bill-left">
              <span class="bill-icon">{{ b.category_icon || '📋' }}</span>
              <div class="bill-info">
                <span class="bill-category">{{ b.category_name }}</span>
                <span class="bill-meta">{{ b.account_name }} · {{ b.remark || '-' }}</span>
              </div>
            </div>
            <div class="bill-right">
              <span class="bill-amount" :class="b.type === 2 ? 'income' : 'expense'">
                {{ b.type === 2 ? '+' : '-' }}¥{{ b.amount.toFixed(2) }}
              </span>
              <span class="bill-date">{{ b.bill_date }}</span>
            </div>
          </div>
        </div>
        <div class="pagination">
          <button class="page-btn" :disabled="billPage <= 1" @click="billPage--; fetchUserBills()">上一页</button>
          <span class="page-info">{{ billPage }} / {{ totalBillPages }}</span>
          <button class="page-btn" :disabled="billPage >= totalBillPages" @click="billPage++; fetchUserBills()">下一页</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '@/services/api'
import { useAuthStore } from '@/stores/auth'
import AvatarUploader from '@/components/AvatarUploader.vue'

const authStore = useAuthStore()
const currentUserId = computed(() => authStore.userId)

const activeTab = ref('users')

const userKeyword = ref('')
const userStatusFilter = ref(null)
const userPage = ref(1)
const userTotal = ref(0)
const userLoading = ref(false)
const users = ref([])

const logKeyword = ref('')
const logActionFilter = ref('')
const logPage = ref(1)
const logTotal = ref(0)
const logLoading = ref(false)
const logs = ref([])

const editingUser = ref(null)
const editForm = ref({})
const savingUser = ref(false)

const viewingBills = ref(null)
const billUserId = ref(null)
const billUserName = ref('')
const bills = ref([])
const billTotal = ref(0)
const billPage = ref(1)
const billLoading = ref(false)
const billStartDate = ref('')
const billEndDate = ref('')
const billTypeFilter = ref(null)
const billSummary = ref({ total_income: 0, total_expense: 0 })

const totalUserPages = computed(() => Math.max(1, Math.ceil(userTotal.value / 20)))
const totalLogPages = computed(() => Math.max(1, Math.ceil(logTotal.value / 20)))
const totalBillPages = computed(() => Math.max(1, Math.ceil(billTotal.value / 20)))

function getAvatarUrl(avatar) {
  if (!avatar) return ''
  if (avatar.startsWith('http')) return avatar
  const base = api.defaults?.baseURL ? api.defaults.baseURL.replace('/api/v1', '') : ''
  return base + avatar
}

function formatDate(dt) {
  if (!dt) return '-'
  return dt.slice(0, 10)
}

function actionLabel(action) {
  const map = { update_user: '编辑用户', disable_user: '禁用用户' }
  return map[action] || action
}

async function fetchUsers() {
  userLoading.value = true
  try {
    const params = { page: userPage.value, size: 20 }
    if (userKeyword.value) params.keyword = userKeyword.value
    if (userStatusFilter.value !== null) params.status = userStatusFilter.value
    const res = await api.get('/admin/users', { params })
    const data = res.data?.data || res.data
    users.value = data.items || []
    userTotal.value = data.total || 0
  } catch {
    users.value = []
  } finally {
    userLoading.value = false
  }
}

function searchUsers() {
  userPage.value = 1
  fetchUsers()
}

async function fetchLogs() {
  logLoading.value = true
  try {
    const params = { page: logPage.value, size: 20 }
    if (logKeyword.value) params.operator_name = logKeyword.value
    if (logActionFilter.value) params.action = logActionFilter.value
    const res = await api.get('/admin/logs', { params })
    const data = res.data?.data || res.data
    logs.value = data.items || []
    logTotal.value = data.total || 0
  } catch {
    logs.value = []
  } finally {
    logLoading.value = false
  }
}

function openEditUser(user) {
  editingUser.value = user
  editForm.value = {
    username: user.username,
    nickname: user.nickname || '',
    email: user.email || '',
    phone: user.phone || '',
    avatar: user.avatar || '',
    is_admin: user.is_admin,
    status: user.status,
    password: '',
  }
}

function onEditAvatarUploaded(url) {
  editForm.value.avatar = url
}

async function saveEditUser() {
  savingUser.value = true
  try {
    const data = {
      nickname: editForm.value.nickname || null,
      email: editForm.value.email || null,
      phone: editForm.value.phone || null,
      is_admin: editForm.value.is_admin,
      status: editForm.value.status,
    }
    if (editForm.value.password) data.password = editForm.value.password
    await api.put(`/admin/users/${editingUser.value.id}`, data)
    editingUser.value = null
    fetchUsers()
  } catch (e) {
    alert(e.response?.data?.detail || '保存失败')
  } finally {
    savingUser.value = false
  }
}

async function disableUser(user) {
  if (!confirm(`确定要禁用用户 "${user.username}" 吗？`)) return
  try {
    await api.delete(`/admin/users/${user.id}`)
    fetchUsers()
  } catch (e) {
    alert(e.response?.data?.detail || '操作失败')
  }
}

function viewUserBills(user) {
  billUserId.value = user.id
  billUserName.value = user.nickname || user.username
  billPage.value = 1
  billStartDate.value = ''
  billEndDate.value = ''
  billTypeFilter.value = null
  viewingBills.value = true
  fetchUserBills()
}

async function fetchUserBills() {
  billLoading.value = true
  try {
    const params = { page: billPage.value, size: 20 }
    if (billStartDate.value) params.start_date = billStartDate.value
    if (billEndDate.value) params.end_date = billEndDate.value
    if (billTypeFilter.value !== null) params.type = billTypeFilter.value
    const res = await api.get(`/admin/users/${billUserId.value}/bills`, { params })
    const data = res.data?.data || res.data
    bills.value = data.items || []
    billTotal.value = data.total || 0
    billSummary.value = {
      total_income: data.total_income || 0,
      total_expense: data.total_expense || 0,
    }
  } catch {
    bills.value = []
  } finally {
    billLoading.value = false
  }
}

function exportUserBills() {
  const params = new URLSearchParams()
  if (billStartDate.value) params.set('start_date', billStartDate.value)
  if (billEndDate.value) params.set('end_date', billEndDate.value)
  const base = api.defaults?.baseURL ? api.defaults.baseURL.replace('/api/v1', '') : ''
  const token = localStorage.getItem('token')
  const url = `${base}/api/v1/admin/users/${billUserId.value}/bills/export?${params.toString()}`
  const link = document.createElement('a')
  link.href = url
  link.setAttribute('download', `user_${billUserName.value}_bills.xlsx`)
  fetch(url, { headers: { Authorization: `Bearer ${token}` } })
    .then(r => r.blob())
    .then(blob => {
      const blobUrl = URL.createObjectURL(blob)
      link.href = blobUrl
      link.click()
      URL.revokeObjectURL(blobUrl)
    })
}

onMounted(() => {
  fetchUsers()
  fetchLogs()
})
</script>

<style scoped>
.admin-page {
  padding-bottom: 20px;
}

.page-header {
  padding: 16px 20px 8px;
}

.page-title {
  font-size: 20px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
}

.tab-bar {
  display: flex;
  margin: 0 16px 12px;
  background: var(--bg-tab);
  border-radius: 10px;
  padding: 3px;
}

.tab-item {
  flex: 1;
  text-align: center;
  padding: 8px 0;
  font-size: 14px;
  font-weight: 600;
  color: var(--text-muted);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.tab-item.active {
  background: var(--bg-card);
  color: var(--text-primary);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
}

.section {
  padding: 0;
}

.filter-bar {
  display: flex;
  gap: 8px;
  padding: 0 16px 12px;
  flex-wrap: wrap;
}

.filter-input {
  flex: 1;
  min-width: 140px;
  padding: 8px 12px;
  border: 1.5px solid var(--border);
  border-radius: 8px;
  font-size: 13px;
  color: var(--text-primary);
  background: var(--bg-input);
  outline: none;
}

.filter-input:focus { border-color: var(--accent); }

.filter-select {
  padding: 8px 12px;
  border: 1.5px solid var(--border);
  border-radius: 8px;
  font-size: 13px;
  color: var(--text-primary);
  background: var(--bg-input);
  outline: none;
  cursor: pointer;
}

.btn-search {
  padding: 8px 16px;
  border: none;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 600;
  color: white;
  background: var(--accent);
  cursor: pointer;
}

.user-cards {
  padding: 0 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.user-card {
  background: var(--bg-card);
  border-radius: 12px;
  padding: 12px 14px;
}

.user-card-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.user-info-left {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 0;
  flex: 1;
}

.user-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  object-fit: cover;
  flex-shrink: 0;
}

.avatar-letter {
  display: inline-flex;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: var(--accent-lighter);
  align-items: center;
  justify-content: center;
  font-size: 15px;
  font-weight: 600;
  flex-shrink: 0;
}

.user-info-text {
  min-width: 0;
  flex: 1;
}

.user-name-row {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
}

.user-name {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

.role-tag {
  font-size: 10px;
  padding: 1px 6px;
  border-radius: 4px;
  background: var(--bg-tab);
  color: var(--text-secondary);
}

.role-tag.admin {
  background: rgba(212, 165, 116, 0.15);
  color: var(--accent);
}

.status-tag {
  font-size: 10px;
  padding: 1px 6px;
  border-radius: 4px;
}

.status-tag.active {
  background: rgba(52, 211, 153, 0.12);
  color: #34d399;
}

.status-tag.disabled {
  background: rgba(239, 68, 68, 0.1);
  color: var(--danger);
}

.user-meta {
  font-size: 12px;
  color: var(--text-muted);
  margin-top: 2px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.user-actions {
  display: flex;
  gap: 6px;
  flex-shrink: 0;
}

.btn-action {
  padding: 4px 10px;
  border: none;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
}

.btn-action.view {
  background: rgba(99, 102, 241, 0.1);
  color: #6366f1;
}

.btn-action.edit {
  background: var(--bg-tab);
  color: var(--text-secondary);
}

.btn-action.disable {
  background: rgba(239, 68, 68, 0.1);
  color: var(--danger);
}

.user-card-bottom {
  display: flex;
  gap: 16px;
  margin-top: 6px;
  padding-top: 6px;
  border-top: 0.5px solid var(--border);
  font-size: 11px;
  color: var(--text-muted);
}

.empty-state {
  padding: 40px 20px;
  text-align: center;
  color: var(--text-muted);
  font-size: 14px;
}

.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 16px;
}

.page-btn {
  padding: 6px 14px;
  border: 1px solid var(--border);
  border-radius: 6px;
  font-size: 13px;
  color: var(--text-primary);
  background: var(--bg-card);
  cursor: pointer;
}

.page-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.page-info {
  font-size: 13px;
  color: var(--text-secondary);
}

.log-list {
  margin: 0 16px;
  background: var(--bg-card);
  border-radius: 12px;
  overflow: hidden;
}

.log-item {
  padding: 10px 14px;
  border-bottom: 0.5px solid var(--border);
}

.log-item:last-child { border-bottom: none; }

.log-main {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
  flex-wrap: wrap;
}

.log-operator {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
}

.log-action-tag {
  font-size: 11px;
  padding: 1px 6px;
  border-radius: 4px;
  background: var(--bg-tab);
  color: var(--text-secondary);
}

.log-target {
  font-size: 12px;
  color: var(--text-muted);
}

.log-detail {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.log-desc {
  font-size: 12px;
  color: var(--text-secondary);
}

.log-meta {
  font-size: 11px;
  color: var(--text-muted);
}

.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
  padding: 16px;
}

.edit-modal, .bills-modal {
  background: var(--bg-card);
  border-radius: 20px;
  padding: 24px;
  width: 100%;
  max-width: 400px;
  max-height: 85vh;
  overflow-y: auto;
  -webkit-overflow-scrolling: touch;
}

.bills-modal {
  max-width: 480px;
}

.edit-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.edit-header h3 {
  font-size: 16px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
}

.modal-close {
  font-size: 18px;
  color: var(--text-muted);
  cursor: pointer;
}

.edit-body {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.edit-field {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.edit-field label {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-secondary);
}

.edit-input {
  padding: 10px 12px;
  border: 1.5px solid var(--border);
  border-radius: 10px;
  font-size: 14px;
  color: var(--text-primary);
  background: var(--bg-input);
  outline: none;
  transition: border-color 0.2s;
}

.edit-input:focus { border-color: var(--accent); }
.edit-input.disabled { opacity: 0.5; cursor: not-allowed; }

.edit-footer {
  display: flex;
  gap: 10px;
  margin-top: 16px;
}

.btn-cancel {
  flex: 1;
  padding: 10px;
  border: 1.5px solid var(--border);
  border-radius: 10px;
  font-size: 14px;
  font-weight: 600;
  color: var(--text-secondary);
  background: transparent;
  cursor: pointer;
}

.btn-primary {
  flex: 1;
  padding: 10px;
  border: none;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 600;
  color: white;
  background: var(--accent);
  cursor: pointer;
}

.btn-primary:disabled { opacity: 0.6; cursor: not-allowed; }

.bills-filter {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
  margin-bottom: 12px;
}

.filter-input-sm {
  padding: 6px 8px;
  border: 1.5px solid var(--border);
  border-radius: 8px;
  font-size: 12px;
  color: var(--text-primary);
  background: var(--bg-input);
  outline: none;
  width: 120px;
}

.filter-sep {
  font-size: 12px;
  color: var(--text-muted);
}

.filter-select-sm {
  padding: 6px 8px;
  border: 1.5px solid var(--border);
  border-radius: 8px;
  font-size: 12px;
  color: var(--text-primary);
  background: var(--bg-input);
  outline: none;
  cursor: pointer;
}

.btn-search-sm {
  padding: 6px 12px;
  border: none;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 600;
  color: white;
  background: var(--accent);
  cursor: pointer;
}

.btn-export {
  padding: 6px 12px;
  border: 1.5px solid var(--accent);
  border-radius: 8px;
  font-size: 12px;
  font-weight: 600;
  color: var(--accent);
  background: transparent;
  cursor: pointer;
}

.bills-summary {
  display: flex;
  gap: 12px;
  padding: 8px 12px;
  background: var(--bg-tab);
  border-radius: 8px;
  margin-bottom: 12px;
  font-size: 12px;
  color: var(--text-secondary);
  flex-wrap: wrap;
}

.summary-item.income { color: #34d399; font-weight: 600; }
.summary-item.expense { color: var(--danger); font-weight: 600; }

.bills-list {
  display: flex;
  flex-direction: column;
  gap: 1px;
}

.bill-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 0.5px solid var(--border);
}

.bill-item:last-child { border-bottom: none; }

.bill-left {
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 0;
  flex: 1;
}

.bill-icon {
  font-size: 18px;
  flex-shrink: 0;
}

.bill-info {
  min-width: 0;
}

.bill-category {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-primary);
  display: block;
}

.bill-meta {
  font-size: 11px;
  color: var(--text-muted);
  display: block;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.bill-right {
  text-align: right;
  flex-shrink: 0;
  margin-left: 8px;
}

.bill-amount {
  font-size: 14px;
  font-weight: 600;
  display: block;
}

.bill-amount.income { color: #34d399; }
.bill-amount.expense { color: var(--danger); }

.bill-date {
  font-size: 11px;
  color: var(--text-muted);
  display: block;
}
</style>
