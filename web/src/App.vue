<template>
  <router-view />
  <router-link to="/add" class="fab" v-if="showTabBar">
    <span class="fab-icon">+</span>
  </router-link>
  <nav class="tab-bar" v-if="showTabBar">
    <router-link
      v-for="tab in tabs"
      :key="tab.path"
      :to="tab.path"
      class="tab-item"
      :class="{ active: isActive(tab.path) }"
    >
      <span class="tab-icon" v-html="tab.icon"></span>
      <span class="tab-label">{{ tab.label }}</span>
    </router-link>
  </nav>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()

const tabs = [
  { path: '/', label: '首页', icon: '🏠' },
  { path: '/bills', label: '账单', icon: '📋' },
  { path: '/stats', label: '统计', icon: '📊' },
  { path: '/accounts', label: '账户', icon: '💳' },
]

const showTabBar = computed(() => {
  return !['add', 'login'].includes(route.name as string)
})

function isActive(path: string) {
  if (path === '/') return route.path === '/'
  return route.path.startsWith(path)
}
</script>

<style scoped>
.fab {
  position: fixed;
  right: 20px;
  bottom: calc(80px + env(safe-area-inset-bottom));
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 16px rgba(99, 102, 241, 0.4);
  z-index: 101;
  text-decoration: none;
  transition: transform 0.2s, box-shadow 0.2s;
}

.fab:active {
  transform: scale(0.9);
  box-shadow: 0 2px 8px rgba(99, 102, 241, 0.3);
}

.fab-icon {
  font-size: 28px;
  font-weight: 300;
  line-height: 1;
}

.tab-bar {
  position: fixed;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 100%;
  max-width: 480px;
  display: flex;
  background: rgba(15, 15, 19, 0.92);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-top: 1px solid var(--border);
  padding: 8px 0 calc(8px + env(safe-area-inset-bottom));
  z-index: 100;
}

.tab-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  padding: 6px 0;
  color: var(--text-muted);
  text-decoration: none;
  transition: all var(--transition);
  position: relative;
}

.tab-item.active {
  color: var(--primary-light);
}

.tab-icon {
  font-size: 22px;
  transition: transform var(--transition);
}

.tab-item.active .tab-icon {
  transform: scale(1.15);
}

.tab-label {
  font-size: 10px;
  font-weight: 500;
  letter-spacing: 0.3px;
}
</style>
