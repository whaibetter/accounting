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
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

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
</style>
