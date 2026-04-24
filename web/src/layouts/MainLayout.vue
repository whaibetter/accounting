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
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--bg-primary);
}

.layout-content {
  flex: 1;
  padding-bottom: 88px;
}

.bottom-nav {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 100;
  padding: 0 12px 8px;
  pointer-events: none;
}

.nav-inner {
  max-width: 480px;
  margin: 0 auto;
  display: flex;
  justify-content: space-around;
  align-items: flex-end;
  background: rgba(255, 255, 255, 0.88);
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
  padding: 4px 12px;
  border-radius: 12px;
  min-width: 52px;
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
  width: 48px;
  height: 48px;
  border-radius: 16px;
  background: linear-gradient(135deg, var(--accent), var(--accent-dark));
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-top: -20px;
  box-shadow: 0 4px 16px rgba(196, 148, 99, 0.4);
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

@media (min-width: 768px) {
  .bottom-nav {
    padding: 0 20px 12px;
  }
}
</style>
