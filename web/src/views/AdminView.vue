<template>
  <div class="page admin-page">
    <div class="page-header">
      <h2 class="page-title">后台管理</h2>
    </div>

    <div class="stats-row">
      <div class="stat-card">
        <div class="stat-value">{{ stats.total_users || 0 }}</div>
        <div class="stat-label">总用户</div>
      </div>
      <div class="stat-card">
        <div class="stat-value active">{{ stats.active_users || 0 }}</div>
        <div class="stat-label">活跃用户</div>
      </div>
      <div class="stat-card">
        <div class="stat-value danger">{{ stats.disabled_users || 0 }}</div>
        <div class="stat-label">已禁用</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">{{ stats.total_bills || 0 }}</div>
        <div class="stat-label">总账单</div>
      </div>
    </div>

    <div class="tab-bar">
      <div class="tab-item" :class="{ active: activeTab === 'users' }" @click="activeTab = 'users'">用户管理</div>
      <div class="tab-item" :class="{ active: activeTab === 'logs' }" @click="activeTab = 'logs'">操作日志</div>
    </div>

    <div v-if="activeTab === 'users'" class="user-section">
      <div class="filter-bar">
        <input
          v-model="userKeyword"
          type="text"
          class="filter-input"
          placeholder="搜索用户名/昵称/邮箱"
          @keyup.enter="searchUsers"
        />
        <select v-model="userStatusFilter" class="filter-select" @change="searchUsers">
          <option :value="null">全部状态</option>
          <option :value="1">正常</option>
          <option :value="0">已禁用</option>
        </select>
        <button class="btn-search" @click="searchUsers">搜索</button>
      </div>

      <div class="user-table">
        <div class="table-header">
          <span class="col-id">ID</span>
          <span class="col-avatar">头像</span>
          <span class="col-name">用户名</span>
          <span class="col-nick">昵称</span>
          <span class="col-email">邮箱</span>
          <span class="col-role">角色</span>
          <span class="col-status">状态</span>
          <span class="col-date">注册时间</span>
          <span class="col-action">操作</span>
        </div>
        <div v-if="userLoading" class="table-empty">加载中...</div>
        <div v-else-if="!users.length" class="table-empty">暂无数据</div>
        <div v-for="u in users" :key="u.id" class="table-row">
          <span class="col-id">{{ u.id }}</span>
          <span class="col-avatar">
            <img v-if="u.avatar" :src="getAvatarUrl(u.avatar)" class="user-avatar" />
            <span v-else class="avatar-letter-sm">{{ (u.nickname || u.username)?.charAt(0) }}</span>
          </span>
          <span class="col-name">{{ u.username }}</span>
          <span class="col-nick">{{ u.nickname || '-' }}</span>
          <span class="col-email">{{ u.email || '-' }}</span>
          <span class="col-role">
            <span class="role-tag" :class="{ admin: u.is_admin }">{{ u.is_admin ? '管理员' : '用户' }}</span>
          </span>
          <span class="col-status">
            <span class="status-dot" :class="u.status === 1 ? 'active' : 'disabled'"></span>
            {{ u.status === 1 ? '正常' : '禁用' }}
          </span>
          <span class="col-date">{{ formatDate(u.created_at) }}</span>
          <span class="col-action">
            <button class="btn-action edit" @click="openEditUser(u)">编辑</button>
            <button v-if="u.status === 1 && u.id !== currentUserId" class="btn-action disable" @click="disableUser(u)">禁用</button>
          </span>
        </div>
      </div>

      <div class="pagination">
        <button class="page-btn" :disabled="userPage <= 1" @click="userPage--; fetchUsers()">上一页</button>
        <span class="page-info">{{ userPage }} / {{ totalUserPages }}</span>
        <button class="page-btn" :disabled="userPage >= totalUserPages" @click="userPage++; fetchUsers()">下一页</button>
      </div>
    </div>

    <div v-if="activeTab === 'logs'" class="log-section">
      <div class="filter-bar">
        <input
          v-model="logKeyword"
          type="text"
          class="filter-input"
          placeholder="搜索操作人"
          @keyup.enter="fetchLogs"
        />
        <select v-model="logActionFilter" class="filter-select" @change="fetchLogs">
          <option value="">全部操作</option>
          <option value="update_user">编辑用户</option>
          <option value="disable_user">禁用用户</option>
        </select>
        <button class="btn-search" @click="fetchLogs">搜索</button>
      </div>

      <div class="log-list">
        <div v-if="logLoading" class="table-empty">加载中...</div>
        <div v-else-if="!logs.length" class="table-empty">暂无日志</div>
        <div v-for="log in logs" :key="log.id" class="log-item">
          <div class="log-main">
            <span class="log-operator">{{ log.operator_name }}</span>
            <span class="log-action">{{ actionLabel(log.action) }}</span>
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
const stats = ref({})

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

const totalUserPages = computed(() => Math.max(1, Math.ceil(userTotal.value / 20)))
const totalLogPages = computed(() => Math.max(1, Math.ceil(logTotal.value / 20)))

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

async function fetchStats() {
  try {
    const res = await api.get('/admin/stats')
    stats.value = res.data?.data || res.data || {}
  } catch {}
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
    fetchStats()
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
    fetchStats()
  } catch (e) {
    alert(e.response?.data?.detail || '操作失败')
  }
}

onMounted(() => {
  fetchStats()
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

.stats-row {
  display: flex;
  gap: 10px;
  padding: 0 16px 12px;
}

.stat-card {
  flex: 1;
  background: var(--bg-card);
  border-radius: 12px;
  padding: 12px;
  text-align: center;
}

.stat-value {
  font-size: 22px;
  font-weight: 700;
  color: var(--text-primary);
}

.stat-value.active { color: #34d399; }
.stat-value.danger { color: var(--danger); }

.stat-label {
  font-size: 12px;
  color: var(--text-secondary);
  margin-top: 2px;
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

.filter-bar {
  display: flex;
  gap: 8px;
  padding: 0 16px 12px;
  flex-wrap: wrap;
}

.filter-input {
  flex: 1;
  min-width: 160px;
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

.user-table {
  margin: 0 16px;
  background: var(--bg-card);
  border-radius: 12px;
  overflow: hidden;
}

.table-header {
  display: flex;
  align-items: center;
  padding: 10px 12px;
  background: var(--bg-tab);
  font-size: 12px;
  font-weight: 600;
  color: var(--text-secondary);
}

.table-row {
  display: flex;
  align-items: center;
  padding: 10px 12px;
  border-top: 0.5px solid var(--border);
  font-size: 13px;
  color: var(--text-primary);
}

.col-id { width: 36px; flex-shrink: 0; }
.col-avatar { width: 36px; flex-shrink: 0; }
.col-name { width: 80px; flex-shrink: 0; }
.col-nick { width: 70px; flex-shrink: 0; }
.col-email { flex: 1; min-width: 80px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.col-role { width: 60px; flex-shrink: 0; }
.col-status { width: 60px; flex-shrink: 0; }
.col-date { width: 80px; flex-shrink: 0; }
.col-action { width: 90px; flex-shrink: 0; }

.user-avatar {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  object-fit: cover;
}

.avatar-letter-sm {
  display: inline-flex;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: var(--accent-lighter);
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 600;
}

.role-tag {
  font-size: 11px;
  padding: 2px 6px;
  border-radius: 4px;
  background: var(--bg-tab);
  color: var(--text-secondary);
}

.role-tag.admin {
  background: rgba(212, 165, 116, 0.15);
  color: var(--accent);
}

.status-dot {
  display: inline-block;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  margin-right: 4px;
}

.status-dot.active { background: #34d399; }
.status-dot.disabled { background: var(--danger); }

.btn-action {
  padding: 3px 8px;
  border: none;
  border-radius: 4px;
  font-size: 12px;
  cursor: pointer;
  margin-right: 4px;
}

.btn-action.edit {
  background: var(--bg-tab);
  color: var(--text-secondary);
}

.btn-action.disable {
  background: rgba(239, 68, 68, 0.1);
  color: var(--danger);
}

.table-empty {
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
}

.log-operator {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
}

.log-action {
  font-size: 12px;
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
}

.edit-modal {
  background: var(--bg-card);
  border-radius: 20px;
  padding: 24px;
  width: 100%;
  max-width: 400px;
  max-height: 85vh;
  overflow-y: auto;
  -webkit-overflow-scrolling: touch;
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
</style>
