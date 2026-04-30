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
        <CustomSelect v-model="userStatusFilter" :options="userStatusOptions" placeholder="全部状态" class="filter-select" @change="searchUsers" />
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
        <input v-model="logKeyword" type="text" class="filter-input" placeholder="搜索操作人/详情/路径" @keyup.enter="fetchLogs" />
        <CustomSelect v-model="logActionFilter" :options="logActionOptions" placeholder="全部操作" class="filter-select" @change="fetchLogs" />
        <CustomSelect v-model="logTargetFilter" :options="logTargetOptions" placeholder="全部对象" class="filter-select" @change="fetchLogs" />
        <CustomSelect v-model="logStatusFilter" :options="logStatusOptions" placeholder="全部状态" class="filter-select" @change="fetchLogs" />
        <input v-model="logStartDate" type="date" class="filter-date" @change="fetchLogs" />
        <span class="filter-sep">至</span>
        <input v-model="logEndDate" type="date" class="filter-date" @change="fetchLogs" />
        <button class="btn-search" @click="fetchLogs">搜索</button>
        <button class="btn-export" @click="exportLogs">导出Excel</button>
      </div>

      <div class="log-list">
        <div v-if="logLoading" class="empty-state">加载中...</div>
        <div v-else-if="!logs.length" class="empty-state">暂无日志</div>
        <div v-for="log in logs" :key="log.id" class="log-item" :class="{ 'log-failure': log.status === 'failure' }" @click="toggleLogExtra(log.id)">
          <div class="log-main">
            <span class="log-operator">{{ log.operator_name }}</span>
            <span class="log-action-tag" :class="actionClass(log.action)">{{ actionLabel(log.action) }}</span>
            <span v-if="log.method" class="log-method">{{ log.method }}</span>
            <span v-if="log.target_type" class="log-target">{{ log.target_type }}<span v-if="log.target_id">#{{ log.target_id }}</span></span>
            <span class="log-status" :class="log.status">{{ log.status === 'success' ? '✓' : '✕' }}</span>
            <span v-if="log.duration_ms" class="log-duration">{{ log.duration_ms }}ms</span>
            <span class="log-expand-icon" :class="{ open: expandedLogs[log.id] }">▶</span>
          </div>
          <div class="log-detail">
            <span v-if="log.detail" class="log-desc">{{ log.detail }}</span>
            <span v-if="log.path" class="log-path">{{ log.path }}</span>
          </div>
          <div class="log-meta-row">
            <span class="log-meta">{{ formatDate(log.created_at) }}</span>
            <span class="log-meta">IP: {{ log.ip_address || '-' }}</span>
          </div>

          <Transition name="log-expand">
            <div v-if="expandedLogs[log.id]" class="log-detail-panel" @click.stop>
              <div class="detail-grid">
                <div class="detail-field">
                  <span class="detail-label">操作ID</span>
                  <span class="detail-value">{{ log.id }}</span>
                </div>
                <div class="detail-field">
                  <span class="detail-label">操作用户</span>
                  <span class="detail-value">{{ log.operator_name }} <span class="detail-sub">(ID: {{ log.operator_id }})</span></span>
                </div>
                <div class="detail-field">
                  <span class="detail-label">操作类型</span>
                  <span class="detail-value"><span class="log-action-tag" :class="actionClass(log.action)">{{ actionLabel(log.action) }}</span></span>
                </div>
                <div class="detail-field">
                  <span class="detail-label">操作状态</span>
                  <span class="detail-value" :class="log.status === 'success' ? 'text-success' : 'text-danger'">{{ log.status === 'success' ? '成功' : '失败' }}</span>
                </div>
                <div class="detail-field">
                  <span class="detail-label">操作时间</span>
                  <span class="detail-value">{{ formatDate(log.created_at) }}</span>
                </div>
                <div class="detail-field">
                  <span class="detail-label">IP地址</span>
                  <span class="detail-value">{{ log.ip_address || '-' }}</span>
                </div>
                <div class="detail-field">
                  <span class="detail-label">请求方法</span>
                  <span class="detail-value"><span class="log-method">{{ log.method || '-' }}</span></span>
                </div>
                <div class="detail-field">
                  <span class="detail-label">请求路径</span>
                  <span class="detail-value"><code class="detail-code">{{ log.path || '-' }}</code></span>
                </div>
                <div class="detail-field">
                  <span class="detail-label">操作对象</span>
                  <span class="detail-value">{{ targetLabel(log.target_type) }}<span v-if="log.target_id" class="detail-sub"> #{{ log.target_id }}</span></span>
                </div>
                <div class="detail-field">
                  <span class="detail-label">耗时</span>
                  <span class="detail-value">{{ log.duration_ms ? log.duration_ms + 'ms' : '-' }}</span>
                </div>
              </div>

              <div v-if="log.detail" class="detail-section">
                <div class="detail-section-title">操作描述</div>
                <div class="detail-section-content">{{ log.detail }}</div>
              </div>

              <div v-if="log.extra_data" class="detail-section">
                <div class="detail-section-title" @click="toggleExtraRaw(log.id)">
                  <span>附加信息</span>
                  <span class="detail-section-toggle">{{ extraRawExpanded[log.id] ? '收起原始数据' : '查看原始数据' }}</span>
                </div>
                <div class="detail-section-content">
                  <template v-if="getExtraFields(log.extra_data).length">
                    <div class="extra-fields">
                      <div v-for="field in getExtraFields(log.extra_data)" :key="field.key" class="extra-field">
                        <span class="extra-key">{{ field.label }}</span>
                        <span class="extra-value" v-if="field.type === 'code'"><code>{{ field.value }}</code></span>
                        <span class="extra-value" v-else-if="field.type === 'tag'"><span class="log-action-tag" :class="field.class">{{ field.value }}</span></span>
                        <span class="extra-value" v-else-if="field.type === 'status'"><span :class="field.value === 'success' || field.value ? 'text-success' : 'text-danger'">{{ field.display || field.value }}</span></span>
                        <span class="extra-value" v-else>{{ field.value }}</span>
                      </div>
                    </div>
                  </template>
                </div>
                <div v-if="extraRawExpanded[log.id]" class="detail-raw">
                  <pre class="log-extra-pre">{{ formatExtraData(log.extra_data) }}</pre>
                </div>
              </div>
            </div>
          </Transition>
        </div>
      </div>

      <div class="pagination">
        <button class="page-btn" :disabled="logPage <= 1" @click="logPage--; fetchLogs()">上一页</button>
        <span class="page-info">{{ logPage }} / {{ totalLogPages }}</span>
        <button class="page-btn" :disabled="logPage >= totalLogPages" @click="logPage++; fetchLogs()">下一页</button>
      </div>
    </div>

    <div v-if="editingUser" class="modal-overlay" v-modal-overlay="() => editingUser = null">
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
            <CustomSelect v-model="editForm.is_admin" :options="roleOptions" class="edit-select" />
          </div>
          <div class="edit-field">
            <label>状态</label>
            <CustomSelect v-model="editForm.status" :options="statusOptions" class="edit-select" />
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

    <div v-if="viewingBills" class="modal-overlay" v-modal-overlay="() => viewingBills = null">
      <div class="bills-modal">
        <div class="edit-header">
          <h3>{{ billUserName }} 的账单</h3>
          <span class="modal-close" @click="viewingBills = null">✕</span>
        </div>
        <div class="bills-filter">
          <input type="date" v-model="billStartDate" class="filter-input-sm" />
          <span class="filter-sep">至</span>
          <input type="date" v-model="billEndDate" class="filter-input-sm" />
          <CustomSelect v-model="billTypeFilter" :options="billTypeOptions" class="filter-select-sm compact" />
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
  <ConfirmDialog ref="confirmRef" icon="⚠️" />
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '@/services/api'
import { useAuthStore } from '@/stores/auth'
import AvatarUploader from '@/components/AvatarUploader.vue'
import CustomSelect from '@/components/CustomSelect.vue'
import ConfirmDialog from '@/components/ConfirmDialog.vue'
import { toastSuccess, toastError } from '@/utils/toast'
import { vModalOverlay } from '@/directives/modalOverlay'

const authStore = useAuthStore()
const currentUserId = computed(() => authStore.userId)
const confirmRef = ref(null)

const activeTab = ref('users')

const userStatusOptions = [
  { label: '全部状态', value: null },
  { label: '正常', value: 1 },
  { label: '已禁用', value: 0 },
]

const logActionOptions = [
  { label: '全部操作', value: '' },
  { label: '创建', value: 'create' },
  { label: '更新', value: 'update' },
  { label: '删除', value: 'delete' },
  { label: '读取', value: 'read' },
  { label: 'AI解析', value: 'ai_parse' },
  { label: 'AI导入', value: 'ai_import' },
  { label: 'AI测试', value: 'ai_test' },
  { label: '导出', value: 'export' },
  { label: '导入', value: 'import' },
  { label: '统计', value: 'statistics' },
  { label: '编辑用户', value: 'update_user' },
  { label: '禁用用户', value: 'disable_user' },
  { label: '登录', value: 'login' },
]

const logTargetOptions = [
  { label: '全部对象', value: '' },
  { label: '账单', value: 'bill' },
  { label: '账户', value: 'account' },
  { label: '分类', value: 'category' },
  { label: '标签', value: 'tag' },
  { label: '用户', value: 'user' },
  { label: 'AI服务', value: 'llm' },
  { label: '认证', value: 'auth' },
  { label: '系统', value: 'system' },
]

const logStatusOptions = [
  { label: '全部状态', value: '' },
  { label: '成功', value: 'success' },
  { label: '失败', value: 'failure' },
]

const roleOptions = [
  { label: '普通用户', value: 0 },
  { label: '管理员', value: 1 },
]

const statusOptions = [
  { label: '正常', value: 1 },
  { label: '禁用', value: 0 },
]

const billTypeOptions = [
  { label: '全部', value: null },
  { label: '支出', value: 1 },
  { label: '收入', value: 2 },
]

const userKeyword = ref('')
const userStatusFilter = ref(null)
const userPage = ref(1)
const userTotal = ref(0)
const userLoading = ref(false)
const users = ref([])

const logKeyword = ref('')
const logActionFilter = ref('')
const logTargetFilter = ref('')
const logStatusFilter = ref('')
const logStartDate = ref('')
const logEndDate = ref('')
const logPage = ref(1)
const logTotal = ref(0)
const expandedLogs = ref({})
const extraRawExpanded = ref({})
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
  const map = {
    create: '创建', update: '更新', delete: '删除', read: '读取',
    ai_parse: 'AI解析', ai_import: 'AI导入', ai_test: 'AI测试',
    export: '导出', import: '导入', statistics: '统计',
    update_user: '编辑用户', disable_user: '禁用用户',
    login: '登录', read_config: '查看配置', read_logs: '查看日志',
    read_profile: '查看资料',
  }
  return map[action] || action
}

function targetLabel(type) {
  const map = {
    bill: '账单', account: '账户', category: '分类', tag: '标签',
    user: '用户', llm: 'AI服务', auth: '认证', system: '系统',
    admin: '后台', import: '导入', export: '导出', avatar: '头像',
    statistics: '统计',
  }
  return map[type] || type || '-'
}

function toggleExtraRaw(id) {
  extraRawExpanded.value[id] = !extraRawExpanded.value[id]
}

function getExtraFields(extraData) {
  if (!extraData) return []
  let data = extraData
  if (typeof data === 'string') {
    try { data = JSON.parse(data) } catch { return [] }
  }
  if (typeof data !== 'object' || data === null) return []

  const fields = []
  const keyMap = {
    bills_count: { label: '解析账单数', type: 'text' },
    import_success: { label: '导入成功数', type: 'text' },
    import_errors: { label: '导入错误', type: 'text' },
    timing: { label: '耗时信息', type: 'code' },
  }

  for (const [key, value] of Object.entries(data)) {
    const config = keyMap[key] || { label: key, type: 'text' }
    if (key === 'request' || key === 'response') continue
    if (typeof value === 'object') {
      fields.push({ key, label: config.label, value: JSON.stringify(value, null, 2), type: 'code' })
    } else {
      fields.push({ key, label: config.label, value: String(value), type: config.type })
    }
  }

  if (data.request) {
    const req = data.request
    if (req.url) fields.push({ key: 'req_url', label: '请求URL', value: req.url, type: 'code' })
    if (req.method) fields.push({ key: 'req_method', label: '请求方法', value: req.method, type: 'tag' })
    if (req.body) {
      const bodyStr = typeof req.body === 'string' ? req.body : JSON.stringify(req.body, null, 2)
      if (bodyStr.length > 500) {
        fields.push({ key: 'req_body', label: '请求体', value: bodyStr.substring(0, 500) + '...', type: 'code' })
      } else {
        fields.push({ key: 'req_body', label: '请求体', value: bodyStr, type: 'code' })
      }
    }
  }

  if (data.response) {
    const resp = data.response
    if (resp.status_code) {
      const isOk = resp.status_code >= 200 && resp.status_code < 300
      fields.push({ key: 'resp_status', label: '响应状态码', value: resp.status_code, type: 'status', class: isOk ? 'action-create' : 'action-delete', display: `${resp.status_code} ${isOk ? '成功' : '失败'}` })
    }
    if (resp.body) {
      const bodyStr = typeof resp.body === 'string' ? resp.body : JSON.stringify(resp.body, null, 2)
      if (bodyStr.length > 500) {
        fields.push({ key: 'resp_body', label: '响应体', value: bodyStr.substring(0, 500) + '...', type: 'code' })
      } else {
        fields.push({ key: 'resp_body', label: '响应体', value: bodyStr, type: 'code' })
      }
    }
    if (resp.error) {
      fields.push({ key: 'resp_error', label: '错误信息', value: resp.error, type: 'code' })
    }
  }

  return fields
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
    if (logKeyword.value) params.keyword = logKeyword.value
    if (logActionFilter.value) params.action = logActionFilter.value
    if (logTargetFilter.value) params.target_type = logTargetFilter.value
    if (logStatusFilter.value) params.status = logStatusFilter.value
    if (logStartDate.value) params.start_date = logStartDate.value
    if (logEndDate.value) params.end_date = logEndDate.value
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

function toggleLogExtra(id) {
  expandedLogs.value[id] = !expandedLogs.value[id]
}

function formatExtraData(data) {
  if (typeof data === 'string') {
    try { return JSON.stringify(JSON.parse(data), null, 2) } catch { return data }
  }
  return JSON.stringify(data, null, 2)
}

function actionClass(action) {
  if (action?.startsWith('create') || action?.startsWith('ai_import')) return 'action-create'
  if (action?.startsWith('update')) return 'action-update'
  if (action?.startsWith('delete') || action?.startsWith('disable')) return 'action-delete'
  if (action?.startsWith('ai_')) return 'action-ai'
  if (action?.startsWith('export') || action?.startsWith('import')) return 'action-data'
  return ''
}

function exportLogs() {
  const params = new URLSearchParams()
  if (logKeyword.value) params.set('keyword', logKeyword.value)
  if (logActionFilter.value) params.set('action', logActionFilter.value)
  if (logTargetFilter.value) params.set('target_type', logTargetFilter.value)
  if (logStatusFilter.value) params.set('status', logStatusFilter.value)
  if (logStartDate.value) params.set('start_date', logStartDate.value)
  if (logEndDate.value) params.set('end_date', logEndDate.value)
  const base = api.defaults.baseURL || '/accounting/api/v1'
  const url = `${base}/admin/logs/export?${params.toString()}`
  window.open(url, '_blank')
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
    toastError(e.response?.data?.detail || '保存失败')
  } finally {
    savingUser.value = false
  }
}

async function disableUser(user) {
  const ok = await confirmRef.value.show({
    title: '禁用用户',
    description: `确定要禁用用户 "${user.username}" 吗？`,
    confirmText: '确认禁用',
  })
  if (!ok) return
  try {
    await api.delete(`/admin/users/${user.id}`)
    fetchUsers()
  } catch (e) {
    toastError(e.response?.data?.detail || '操作失败')
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
  width: 140px;
  flex-shrink: 0;
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
.log-action-tag.action-create { background: rgba(76, 175, 80, 0.12); color: #4caf50; }
.log-action-tag.action-update { background: rgba(33, 150, 243, 0.12); color: #2196f3; }
.log-action-tag.action-delete { background: rgba(244, 67, 54, 0.12); color: #f44336; }
.log-action-tag.action-ai { background: rgba(156, 39, 176, 0.12); color: #9c27b0; }
.log-action-tag.action-data { background: rgba(255, 152, 0, 0.12); color: #ff9800; }

.log-method {
  font-size: 10px;
  padding: 1px 5px;
  border-radius: 3px;
  background: rgba(0,0,0,0.06);
  color: var(--text-muted);
  font-weight: 600;
  font-family: monospace;
}

.log-target {
  font-size: 12px;
  color: var(--text-muted);
}

.log-status {
  font-size: 12px;
  font-weight: 700;
}
.log-status.success { color: #4caf50; }
.log-status.failure { color: #f44336; }

.log-duration {
  font-size: 11px;
  color: var(--accent);
  font-weight: 500;
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

.log-path {
  font-size: 11px;
  color: var(--text-muted);
  font-family: monospace;
  background: rgba(0,0,0,0.03);
  padding: 1px 5px;
  border-radius: 3px;
}

.log-meta-row {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.log-meta {
  font-size: 11px;
  color: var(--text-muted);
}

.log-extra-toggle {
  font-size: 11px;
  color: var(--accent);
  cursor: pointer;
}
.log-extra-toggle:hover { text-decoration: underline; }

.log-expand-icon {
  font-size: 9px;
  color: var(--text-muted);
  transition: transform 0.2s;
  margin-left: auto;
}
.log-expand-icon.open { transform: rotate(90deg); }

.log-detail-panel {
  margin-top: 10px;
  padding: 14px;
  background: rgba(0, 0, 0, 0.02);
  border-radius: 10px;
  border: 1px solid var(--border);
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 10px 16px;
  margin-bottom: 12px;
}

.detail-field {
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.detail-label {
  font-size: 11px;
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.3px;
}

.detail-value {
  font-size: 13px;
  color: var(--text-primary);
  word-break: break-all;
}

.detail-sub {
  font-size: 11px;
  color: var(--text-muted);
}

.detail-code {
  font-size: 12px;
  padding: 2px 6px;
  background: rgba(0,0,0,0.05);
  border-radius: 4px;
  font-family: 'Consolas', 'Monaco', monospace;
  word-break: break-all;
}

.text-success { color: #4caf50; font-weight: 600; }
.text-danger { color: #f44336; font-weight: 600; }

.detail-section {
  margin-top: 10px;
  border-top: 1px solid var(--border);
  padding-top: 10px;
}

.detail-section-title {
  font-size: 12px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 6px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  cursor: default;
}

.detail-section-toggle {
  font-size: 11px;
  font-weight: 400;
  color: var(--accent);
  cursor: pointer;
}
.detail-section-toggle:hover { text-decoration: underline; }

.detail-section-content {
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.5;
}

.extra-fields {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.extra-field {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  font-size: 12px;
}

.extra-key {
  min-width: 80px;
  color: var(--text-muted);
  font-weight: 500;
  flex-shrink: 0;
}

.extra-value {
  color: var(--text-primary);
  word-break: break-all;
}

.extra-value code {
  font-size: 11px;
  padding: 2px 5px;
  background: rgba(0,0,0,0.04);
  border-radius: 3px;
  font-family: 'Consolas', 'Monaco', monospace;
  white-space: pre-wrap;
  word-break: break-all;
}

.detail-raw {
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px dashed var(--border);
}

.log-expand-enter-active {
  animation: logExpandIn 0.2s ease-out;
}
.log-expand-leave-active {
  animation: logExpandOut 0.15s ease-in;
}

@keyframes logExpandIn {
  from { opacity: 0; max-height: 0; transform: translateY(-5px); }
  to { opacity: 1; max-height: 600px; transform: translateY(0); }
}
@keyframes logExpandOut {
  from { opacity: 1; max-height: 600px; transform: translateY(0); }
  to { opacity: 0; max-height: 0; transform: translateY(-5px); }
}

@media (max-width: 600px) {
  .detail-grid {
    grid-template-columns: 1fr 1fr;
  }
}

.log-failure {
  border-left: 3px solid #f44336;
}

.filter-date {
  padding: 6px 8px;
  border: 1px solid var(--border);
  border-radius: 6px;
  font-size: 13px;
  background: var(--bg-card);
  color: var(--text-primary);
}

.filter-sep {
  font-size: 12px;
  color: var(--text-muted);
}

.btn-export {
  padding: 6px 14px;
  border: none;
  border-radius: 6px;
  background: linear-gradient(135deg, #4caf50, #388e3c);
  color: white;
  font-size: 13px;
  cursor: pointer;
  font-weight: 500;
}
.btn-export:hover { opacity: 0.9; }

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
