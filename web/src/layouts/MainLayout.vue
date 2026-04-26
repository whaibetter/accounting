<template>
  <div class="main-layout">
    <div class="layout-content">
      <router-view />
    </div>
    <nav class="bottom-nav">
      <div class="nav-inner">
        <router-link to="/" class="nav-item" :class="{ active: currentRoute === 'Home' }">
          <span class="nav-icon">🏠</span>
          <span class="nav-label">首页</span>
        </router-link>
        <router-link to="/bills" class="nav-item" :class="{ active: currentRoute === 'Bills' }">
          <span class="nav-icon">📋</span>
          <span class="nav-label">账单</span>
        </router-link>
        <router-link to="/record" class="nav-fab-link">
          <div class="nav-fab">
            <span class="fab-icon">✏</span>
          </div>
          <span class="nav-label fab-label">记账</span>
        </router-link>
        <router-link to="/statistics" class="nav-item" :class="{ active: currentRoute === 'Statistics' }">
          <span class="nav-icon">📊</span>
          <span class="nav-label">统计</span>
        </router-link>
        <router-link to="/profile" class="nav-item" :class="{ active: currentRoute === 'Profile' }">
          <span class="nav-icon">👤</span>
          <span class="nav-label">我的</span>
        </router-link>
      </div>
    </nav>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const currentRoute = computed(() => route.name)
</script>

<style scoped>
.main-layout {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: var(--bg-primary);
  position: relative;
}

.layout-content {
  flex: 1;
  overflow: hidden;
}

.bottom-nav {
  position: fixed;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 100%;
  max-width: 480px;
  z-index: 100;
  padding: 0 10px 8px;
  padding-bottom: calc(8px + var(--safe-bottom));
  pointer-events: none;
}

.nav-inner {
  display: flex;
  justify-content: space-around;
  align-items: flex-end;
  background: rgba(255, 255, 255, 0.92);
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  border-radius: 20px;
  padding: 8px 4px 10px;
  box-shadow:
    0 -2px 16px rgba(140, 120, 80, 0.08),
    0 4px 24px rgba(140, 120, 80, 0.06);
  border: 0.5px solid rgba(200, 180, 150, 0.15);
  pointer-events: auto;
}

.nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  font-size: 10px;
  color: var(--text-light);
  transition: all 0.25s ease;
  text-decoration: none;
  padding: 4px 10px;
  border-radius: 12px;
  min-width: 48px;
}

.nav-item.active {
  color: var(--accent);
}

.nav-item.active .nav-icon {
  transform: scale(1.15);
}

.nav-icon {
  font-size: 22px;
  line-height: 1;
  transition: transform 0.25s ease;
}

.nav-label {
  font-size: 10px;
  font-weight: 500;
  letter-spacing: 0.3px;
}

.nav-fab-link {
  text-decoration: none;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  padding: 0 8px;
}

.nav-fab {
  width: 46px;
  height: 46px;
  border-radius: 15px;
  background: linear-gradient(135deg, var(--accent), var(--accent-dark));
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-top: -18px;
  box-shadow: 0 4px 14px rgba(196, 148, 99, 0.4);
  cursor: pointer;
  transition: all 0.25s ease;
}

.nav-fab:active {
  transform: scale(0.92);
}

.fab-icon {
  font-size: 20px;
  font-weight: 700;
  line-height: 1;
}

.fab-label {
  font-size: 10px;
  font-weight: 600;
  color: var(--accent);
  letter-spacing: 0.3px;
}
</style>
