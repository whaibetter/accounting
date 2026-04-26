<template>
  <div class="page profile-page">
    <div class="profile-header">
      <div class="avatar-circle">👤</div>
      <div class="header-info">
        <div class="profile-name">记账用户</div>
        <div class="profile-desc">轻松管理你的财务</div>
      </div>
    </div>

    <div class="asset-overview card">
      <div class="asset-row">
        <div class="asset-item">
          <span class="asset-label">总资产</span>
          <span class="asset-value">{{ showAmount ? '¥' + formatMoney(totalAssets) : '****' }}</span>
        </div>
        <div class="asset-divider"></div>
        <div class="asset-item">
          <span class="asset-label">总负债</span>
          <span class="asset-value debt">{{ showAmount ? '¥' + formatMoney(totalDebts) : '****' }}</span>
        </div>
        <div class="asset-divider"></div>
        <div class="asset-item">
          <span class="asset-label">净资产</span>
          <span class="asset-value net">{{ showAmount ? '¥' + formatMoney(netAssets) : '****' }}</span>
        </div>
      </div>
      <div class="asset-eye" @click="showAmount = !showAmount">
        {{ showAmount ? '👁' : '👁‍🗨' }}
      </div>
    </div>

    <div class="menu-section">
      <div class="section-label">数据管理</div>
      <div class="menu-group card">
        <div class="menu-item" @click="$router.push('/accounts')">
          <div class="menu-icon" style="background: rgba(212, 165, 116, 0.12)">💳</div>
          <span class="menu-text">资产管理</span>
          <span class="menu-extra">{{ activeAccountCount }}个账户</span>
          <span class="menu-arrow">›</span>
        </div>
        <div class="menu-item" @click="$router.push('/categories')">
          <div class="menu-icon" style="background: rgba(124, 175, 212, 0.12)">🏷️</div>
          <span class="menu-text">分类管理</span>
          <span class="menu-arrow">›</span>
        </div>
        <div class="menu-item" @click="$router.push('/tags')">
          <div class="menu-icon" style="background: rgba(123, 201, 123, 0.12)">🔖</div>
          <span class="menu-text">标签管理</span>
          <span class="menu-arrow">›</span>
        </div>
        <div class="menu-item" @click="$router.push('/export')">
          <div class="menu-icon" style="background: rgba(160, 123, 212, 0.12)">📤</div>
          <span class="menu-text">数据导出</span>
          <span class="menu-arrow">›</span>
        </div>
        <div class="menu-item last" @click="$router.push('/import')">
          <div class="menu-icon" style="background: rgba(212, 200, 123, 0.12)">📥</div>
          <span class="menu-text">数据导入</span>
          <span class="menu-arrow">›</span>
        </div>
      </div>
    </div>

    <div class="menu-section">
      <div class="section-label">个性化</div>
      <div class="menu-group card">
        <div class="menu-item" @click="$router.push('/theme')">
          <div class="menu-icon" style="background: rgba(232, 201, 154, 0.2)">🎨</div>
          <span class="menu-text">主题风格</span>
          <span class="menu-extra">{{ currentThemeName }}</span>
          <span class="menu-arrow">›</span>
        </div>
        <div class="menu-item last" @click="$router.push('/ai')">
          <div class="menu-icon" style="background: rgba(123, 155, 212, 0.12)">🤖</div>
          <span class="menu-text">AI智能记账</span>
          <span class="menu-arrow">›</span>
        </div>
      </div>
    </div>

    <div class="menu-section">
      <div class="section-label">安全</div>
      <div class="menu-group card">
        <div class="menu-item last" @click="handleChangePassword">
          <div class="menu-icon" style="background: rgba(212, 123, 123, 0.12)">🔒</div>
          <span class="menu-text">修改密码</span>
          <span class="menu-arrow">›</span>
        </div>
      </div>
    </div>

    <div class="logout-section">
      <button class="logout-btn" @click="handleLogout">退出登录</button>
    </div>

    <div class="app-info">
      记账助手 v1.0.0
    </div>

    <div v-if="showChangePasswordModal" class="modal-overlay" @click="closeChangePasswordModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>修改密码</h3>
          <span class="modal-close" @click="closeChangePasswordModal">✕</span>
        </div>
        <div class="form-group">
          <label>旧密码</label>
          <input type="password" v-model="oldPassword" placeholder="请输入旧密码" />
        </div>
        <div class="form-group">
          <label>新密码</label>
          <input type="password" v-model="newPassword" placeholder="字母+数字，至少6位" />
          <div class="strength-bar" v-if="newPassword">
            <div class="strength-fill" :style="{ width: passwordStrength.percent + '%', background: passwordStrength.color }"></div>
          </div>
          <div class="strength-text" v-if="newPassword">{{ passwordStrength.text }}</div>
        </div>
        <div class="form-group">
          <label>确认新密码</label>
          <input type="password" v-model="confirmPassword" placeholder="请再次输入新密码" />
          <div class="error-hint" v-if="confirmPassword && newPassword !== confirmPassword">两次密码不一致</div>
        </div>
        <div class="modal-actions">
          <button class="btn-cancel" @click="closeChangePasswordModal">取消</button>
          <button
            class="btn-primary"
            @click="submitChangePassword"
            :disabled="isSubmitting || !canSubmit"
          >
            {{ isSubmitting ? '提交中...' : '确认修改' }}
          </button>
        </div>
      </div>
    </div>

    <div v-if="showLogoutConfirm" class="modal-overlay" @click="showLogoutConfirm = false">
      <div class="confirm-content" @click.stop>
        <div class="confirm-icon">🚪</div>
        <div class="confirm-title">确认退出登录？</div>
        <div class="confirm-desc">退出后需要重新输入密码登录</div>
        <div class="confirm-actions">
          <button class="btn-cancel" @click="showLogoutConfirm = false">取消</button>
          <button class="btn-danger" @click="confirmLogout">确认退出</button>
        </div>
      </div>
    </div>

    <Transition name="toast">
      <div v-if="toastMessage" class="toast" :class="toastType">
        {{ toastMessage }}
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useAccountStore } from '@/stores/data'
import { useThemeStore, THEMES } from '@/stores/theme'
import { authApi } from '@/services'

const router = useRouter()
const authStore = useAuthStore()
const accountStore = useAccountStore()
const themeStore = useThemeStore()

const showAmount = ref(true)
const showChangePasswordModal = ref(false)
const showLogoutConfirm = ref(false)
const oldPassword = ref('')
const newPassword = ref('')
const confirmPassword = ref('')
const isSubmitting = ref(false)
const toastMessage = ref('')
const toastType = ref('success')

const totalAssets = computed(() => accountStore.totalAssets())
const totalDebts = computed(() => accountStore.totalDebts())
const netAssets = computed(() => totalAssets.value - totalDebts.value)
const activeAccountCount = computed(() => accountStore.accounts.filter(a => a.status === 1).length)

const currentThemeName = computed(() => {
  const theme = THEMES[themeStore.currentThemeId]
  return theme ? theme.name : ''
})

const passwordStrength = computed(() => {
  const pw = newPassword.value
  if (!pw) return { percent: 0, color: '#ddd', text: '' }
  let score = 0
  if (pw.length >= 6) score += 25
  if (pw.length >= 10) score += 25
  if (/[a-zA-Z]/.test(pw) && /\d/.test(pw)) score += 25
  if (/[!@#$%^&*()_+\-=[\]{}|;:',.<>?/`~]/.test(pw)) score += 25
  if (score <= 25) return { percent: 25, color: '#f87171', text: '弱' }
  if (score <= 50) return { percent: 50, color: '#fbbf24', text: '一般' }
  if (score <= 75) return { percent: 75, color: '#34d399', text: '较强' }
  return { percent: 100, color: '#22c55e', text: '强' }
})

const canSubmit = computed(() => {
  return oldPassword.value && newPassword.value && confirmPassword.value
    && newPassword.value === confirmPassword.value
    && newPassword.value.length >= 6
    && /[a-zA-Z]/.test(newPassword.value) && /\d/.test(newPassword.value)
})

function formatMoney(n) {
  return Number(n).toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

function showToast(msg, type = 'success') {
  toastMessage.value = msg
  toastType.value = type
  setTimeout(() => { toastMessage.value = '' }, 2500)
}

function handleChangePassword() {
  showChangePasswordModal.value = true
}

function closeChangePasswordModal() {
  showChangePasswordModal.value = false
  oldPassword.value = ''
  newPassword.value = ''
  confirmPassword.value = ''
}

async function submitChangePassword() {
  if (!canSubmit.value) return

  isSubmitting.value = true
  try {
    const response = await authApi.changePassword({
      old_password: oldPassword.value,
      new_password: newPassword.value
    })

    if (response.data.code === 200) {
      showToast('密码修改成功')
      closeChangePasswordModal()
    } else {
      showToast(response.data.message || '修改失败', 'error')
    }
  } catch (error) {
    const msg = error.response?.data?.detail || error.message || '网络错误'
    showToast(msg, 'error')
  } finally {
    isSubmitting.value = false
  }
}

function handleLogout() {
  showLogoutConfirm.value = true
}

function confirmLogout() {
  showLogoutConfirm.value = false
  authStore.logout()
  router.push('/login')
}

onMounted(() => {
  accountStore.fetchAccounts()
})
</script>

<style scoped>
.profile-page {
  padding-bottom: calc(var(--nav-height) + var(--safe-bottom) + 16px);
}

.profile-header {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 20px 20px 12px;
}

.avatar-circle {
  width: 54px;
  height: 54px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--accent-lighter), var(--accent-light));
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 26px;
  flex-shrink: 0;
}

.header-info {
  flex: 1;
}

.profile-name {
  font-size: 20px;
  font-weight: 800;
  color: var(--text-primary);
}

.profile-desc {
  font-size: 13px;
  color: var(--text-muted);
  margin-top: 2px;
}

.asset-overview {
  margin: 4px 16px 16px;
  padding: 16px 20px;
  position: relative;
}

.asset-row {
  display: flex;
  align-items: center;
}

.asset-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.asset-label {
  font-size: 11px;
  color: var(--text-muted);
}

.asset-value {
  font-size: 16px;
  font-weight: 700;
  font-variant-numeric: tabular-nums;
  color: var(--text-primary);
}

.asset-value.debt {
  color: var(--danger);
}

.asset-value.net {
  color: var(--accent);
}

.asset-divider {
  width: 1px;
  height: 28px;
  background: var(--border);
  flex-shrink: 0;
}

.asset-eye {
  position: absolute;
  top: 12px;
  right: 16px;
  font-size: 15px;
  color: var(--text-light);
  cursor: pointer;
  padding: 4px;
}

.menu-section {
  margin-bottom: 16px;
}

.section-label {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-muted);
  padding: 0 20px;
  margin-bottom: 6px;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.menu-group {
  margin: 0 16px;
  padding: 0 4px;
}

.menu-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 12px;
  border-bottom: 0.5px solid var(--border);
  cursor: pointer;
  transition: background 0.15s;
}

.menu-item.last {
  border-bottom: none;
}

.menu-item:active {
  background: var(--bg-input);
  border-radius: 8px;
}

.menu-icon {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  flex-shrink: 0;
}

.menu-text {
  flex: 1;
  font-size: 15px;
  font-weight: 500;
  color: var(--text-primary);
}

.menu-extra {
  font-size: 12px;
  color: var(--text-muted);
  max-width: 80px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.menu-arrow {
  color: var(--text-light);
  font-size: 14px;
}

.logout-section {
  padding: 8px 16px;
}

.logout-btn {
  width: 100%;
  padding: 14px;
  border: 1px solid var(--danger);
  border-radius: 12px;
  background: transparent;
  color: var(--danger);
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.logout-btn:active {
  background: var(--danger);
  color: white;
}

.app-info {
  text-align: center;
  font-size: 11px;
  color: var(--text-muted);
  padding: 16px 0 4px;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.2s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.modal-content {
  background: var(--bg-card);
  border-radius: 16px;
  padding: 24px;
  width: 90%;
  max-width: 400px;
  box-shadow: var(--shadow-lg);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.modal-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 700;
  color: var(--text-primary);
}

.modal-close {
  font-size: 18px;
  color: var(--text-muted);
  cursor: pointer;
  padding: 4px;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  font-size: 13px;
  font-weight: 600;
  color: var(--text-secondary);
  margin-bottom: 6px;
}

.form-group input {
  width: 100%;
  padding: 11px 14px;
  border: 1.5px solid var(--border);
  border-radius: 10px;
  font-size: 14px;
  background: var(--bg-input);
  color: var(--text-primary);
  outline: none;
  transition: border-color 0.2s;
  box-sizing: border-box;
}

.form-group input:focus {
  border-color: var(--accent);
}

.form-group input::placeholder {
  color: var(--text-muted);
}

.strength-bar {
  height: 3px;
  background: var(--bg-input);
  border-radius: 2px;
  margin-top: 8px;
  overflow: hidden;
}

.strength-fill {
  height: 100%;
  border-radius: 2px;
  transition: all 0.3s ease;
}

.strength-text {
  font-size: 11px;
  margin-top: 4px;
  color: var(--text-muted);
}

.error-hint {
  font-size: 12px;
  color: var(--danger);
  margin-top: 4px;
}

.modal-actions {
  display: flex;
  gap: 12px;
  margin-top: 24px;
}

.btn-cancel {
  flex: 1;
  padding: 12px;
  border: 1.5px solid var(--border);
  border-radius: 10px;
  background: transparent;
  font-size: 14px;
  font-weight: 500;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s;
}

.btn-cancel:active {
  background: var(--bg-input);
}

.btn-primary {
  flex: 1;
  padding: 12px;
  border: none;
  border-radius: 10px;
  background: var(--accent);
  font-size: 14px;
  font-weight: 600;
  color: white;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary:active {
  background: var(--accent-dark);
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.confirm-content {
  background: var(--bg-card);
  border-radius: 16px;
  padding: 32px 24px 24px;
  width: 85%;
  max-width: 340px;
  text-align: center;
  box-shadow: var(--shadow-lg);
}

.confirm-icon {
  font-size: 40px;
  margin-bottom: 12px;
}

.confirm-title {
  font-size: 17px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 6px;
}

.confirm-desc {
  font-size: 13px;
  color: var(--text-muted);
  margin-bottom: 24px;
}

.confirm-actions {
  display: flex;
  gap: 12px;
}

.btn-danger {
  flex: 1;
  padding: 12px;
  border: none;
  border-radius: 10px;
  background: var(--danger);
  font-size: 14px;
  font-weight: 600;
  color: white;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-danger:active {
  opacity: 0.8;
}

.toast {
  position: fixed;
  top: 60px;
  left: 50%;
  transform: translateX(-50%);
  padding: 10px 24px;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 500;
  z-index: 2000;
  box-shadow: var(--shadow-lg);
}

.toast.success {
  background: var(--success);
  color: white;
}

.toast.error {
  background: var(--danger);
  color: white;
}

.toast-enter-active {
  animation: toastIn 0.3s ease;
}

.toast-leave-active {
  animation: toastOut 0.3s ease;
}

@keyframes toastIn {
  from { opacity: 0; transform: translateX(-50%) translateY(-12px); }
  to { opacity: 1; transform: translateX(-50%) translateY(0); }
}

@keyframes toastOut {
  from { opacity: 1; transform: translateX(-50%) translateY(0); }
  to { opacity: 0; transform: translateX(-50%) translateY(-12px); }
}
</style>
