<template>
  <div class="main-layout">
    <div class="layout-content">
      <router-view />
    </div>
    <nav class="bottom-nav">
      <router-link to="/" class="nav-item" :class="{ active: currentRoute === 'Home' }">
        <span class="nav-icon">🏠</span>
        <span>首页</span>
      </router-link>
      <router-link to="/bills" class="nav-item" :class="{ active: currentRoute === 'Bills' }">
        <span class="nav-icon">📋</span>
        <span>账单</span>
      </router-link>
      <router-link to="/record" class="nav-fab-link">
        <div class="nav-fab">+</div>
      </router-link>
      <router-link to="/statistics" class="nav-item" :class="{ active: currentRoute === 'Statistics' }">
        <span class="nav-icon">📊</span>
        <span>统计</span>
      </router-link>
      <router-link to="/profile" class="nav-item" :class="{ active: currentRoute === 'Profile' }">
        <span class="nav-icon">👤</span>
        <span>我的</span>
      </router-link>
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
  padding-bottom: 80px;
}

.bottom-nav {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  height: var(--nav-height);
  background: rgba(250, 247, 242, 0.95);
  backdrop-filter: blur(20px);
  display: flex;
  justify-content: space-around;
  align-items: flex-start;
  padding-top: 10px;
  border-top: 0.5px solid var(--border);
  z-index: 100;
}

.nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 3px;
  font-size: 10px;
  color: var(--text-light);
  transition: all 0.2s;
  text-decoration: none;
}

.nav-item.active {
  color: var(--accent);
}

.nav-icon {
  font-size: 22px;
  line-height: 1;
}

.nav-fab-link {
  text-decoration: none;
  display: flex;
  align-items: center;
  justify-content: center;
}

.nav-fab {
  width: 52px;
  height: 52px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--accent), var(--accent-dark));
  color: white;
  font-size: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-top: -22px;
  box-shadow: 0 4px 16px rgba(196, 148, 99, 0.4);
  cursor: pointer;
  transition: transform 0.2s;
}

.nav-fab:hover {
  transform: scale(1.05);
}

@media (min-width: 768px) {
  .bottom-nav {
    max-width: 480px;
    left: 50%;
    transform: translateX(-50%);
  }
}
</style>
