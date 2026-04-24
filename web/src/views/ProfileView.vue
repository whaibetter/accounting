<template>
  <div class="page profile-page">
    <div class="profile-header">
      <div class="avatar-circle">👤</div>
      <div>
        <div class="profile-name">记账用户</div>
        <div class="profile-desc">轻松管理你的财务</div>
        <div class="badge-pill">记账达人 ✨</div>
      </div>
    </div>

    <div class="menu-list">
      <div class="menu-item" @click="handleChangePassword">
        <div class="menu-icon">🔒</div>
        <span class="menu-text">修改密码</span>
        <span class="menu-arrow">›</span>
      </div>
      <div class="menu-item" @click="$router.push('/accounts')">
        <div class="menu-icon">💳</div>
        <span class="menu-text">资产管理</span>
        <span class="menu-arrow">›</span>
      </div>
      <div class="menu-item" @click="$router.push('/categories')">
        <div class="menu-icon">🏷️</div>
        <span class="menu-text">分类管理</span>
        <span class="menu-arrow">›</span>
      </div>
      <div class="menu-item" @click="$router.push('/tags')">
        <div class="menu-icon">🔖</div>
        <span class="menu-text">标签管理</span>
        <span class="menu-arrow">›</span>
      </div>
      <div class="menu-item" @click="$router.push('/export')">
        <div class="menu-icon">📤</div>
        <span class="menu-text">数据导出</span>
        <span class="menu-arrow">›</span>
      </div>
      <div class="menu-item" @click="$router.push('/import')">
        <div class="menu-icon">📥</div>
        <span class="menu-text">数据导入</span>
        <span class="menu-arrow">›</span>
      </div>
      <div class="menu-item" @click="$router.push('/ai')">
        <div class="menu-icon">🤖</div>
        <span class="menu-text">AI智能记账</span>
        <span class="menu-arrow">›</span>
      </div>
      <div class="menu-item" @click="$router.push('/theme')">
        <div class="menu-icon">🎨</div>
        <span class="menu-text">主题风格</span>
        <span class="menu-arrow">›</span>
      </div>
      <div class="menu-item" @click="handleLogout">
        <div class="menu-icon">🚪</div>
        <span class="menu-text">退出登录</span>
        <span class="menu-arrow">›</span>
      </div>
    </div>

    <!-- 密码修改弹窗 -->
    <div v-if="showChangePasswordModal" class="modal-overlay" @click="closeChangePasswordModal">
      <div class="modal-content" @click.stop>
        <h3>修改密码</h3>
        <div class="form-group">
          <label>旧密码</label>
          <input type="password" v-model="oldPassword" placeholder="请输入旧密码" />
        </div>
        <div class="form-group">
          <label>新密码</label>
          <input type="password" v-model="newPassword" placeholder="请输入新密码" />
        </div>
        <div class="form-group">
          <label>确认新密码</label>
          <input type="password" v-model="confirmPassword" placeholder="请再次输入新密码" />
        </div>
        <div class="modal-actions">
          <button class="btn-cancel" @click="closeChangePasswordModal">取消</button>
          <button class="btn-primary" @click="submitChangePassword" :disabled="isSubmitting">
            {{ isSubmitting ? '提交中...' : '确认修改' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { authApi } from '@/services'

const router = useRouter()
const authStore = useAuthStore()

// 密码修改相关
const showChangePasswordModal = ref(false)
const oldPassword = ref('')
const newPassword = ref('')
const confirmPassword = ref('')
const isSubmitting = ref(false)

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
  if (!oldPassword.value || !newPassword.value || !confirmPassword.value) {
    alert('请填写所有字段')
    return
  }

  if (newPassword.value !== confirmPassword.value) {
    alert('两次输入的新密码不一致')
    return
  }

  isSubmitting.value = true
  try {
    const response = await authApi.changePassword({
      old_password: oldPassword.value,
      new_password: newPassword.value
    })
    
    if (response.data.code === 200) {
      alert('密码修改成功！')
      closeChangePasswordModal()
    } else {
      alert(response.data.message || '修改失败')
    }
  } catch (error) {
    alert('网络错误，请稍后重试')
  } finally {
    isSubmitting.value = false
  }
}

function handleLogout() {
  authStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.profile-header {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 20px;
}

.avatar-circle {
  width: 58px;
  height: 58px;
  border-radius: 50%;
  background: linear-gradient(135deg, #e8d4b8, #dccaa8);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
}

.profile-name {
  font-size: 19px;
  font-weight: 800;
  color: var(--text-primary);
}

.profile-desc {
  font-size: 12px;
  color: #bbb;
  margin-top: 2px;
}

.badge-pill {
  display: inline-block;
  background: linear-gradient(135deg, var(--accent), var(--accent-dark));
  color: white;
  font-size: 11px;
  padding: 3px 12px;
  border-radius: 10px;
  font-weight: 600;
  margin-top: 6px;
}

.menu-list {
  padding: 0 16px;
}

.menu-item {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 16px 0;
  border-bottom: 0.5px solid #f0ece5;
  cursor: pointer;
  transition: background 0.15s;
}

.menu-item:active {
  background: rgba(0, 0, 0, 0.02);
}

.menu-icon {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  background: #faf6ef;
}

.menu-text {
  flex: 1;
  font-size: 15px;
  font-weight: 500;
  color: var(--text-primary);
}

.menu-arrow {
  color: #ddd;
  font-size: 14px;
}

/* 弹窗样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 16px;
  padding: 24px;
  width: 90%;
  max-width: 400px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
}

.modal-content h3 {
  margin: 0 0 20px 0;
  font-size: 18px;
  font-weight: 700;
  color: var(--text-primary);
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.form-group input {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  font-size: 14px;
  outline: none;
  transition: border-color 0.2s;
}

.form-group input:focus {
  border-color: var(--accent);
}

.modal-actions {
  display: flex;
  gap: 12px;
  margin-top: 24px;
}

.btn-cancel {
  flex: 1;
  padding: 12px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  background: white;
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
  cursor: pointer;
  transition: all 0.2s;
}

.btn-cancel:hover {
  background: #f5f5f5;
}

.btn-primary {
  flex: 1;
  padding: 12px;
  border: none;
  border-radius: 8px;
  background: var(--accent);
  font-size: 14px;
  font-weight: 600;
  color: white;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary:hover {
  background: var(--accent-dark);
}

.btn-primary:disabled {
  background: #ccc;
  cursor: not-allowed;
}
</style>
