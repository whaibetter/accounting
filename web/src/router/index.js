import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/LoginView.vue'),
    meta: { public: true },
  },
  {
    path: '/',
    component: () => import('@/layouts/MainLayout.vue'),
    children: [
      { path: '', name: 'Home', component: () => import('@/views/HomeView.vue') },
      { path: 'bills', name: 'Bills', component: () => import('@/views/BillsView.vue') },
      { path: 'statistics', name: 'Statistics', component: () => import('@/views/StatisticsView.vue') },
      { path: 'profile', name: 'Profile', component: () => import('@/views/ProfileView.vue') },
    ],
  },
  {
    path: '/record',
    name: 'Record',
    component: () => import('@/views/RecordView.vue'),
  },
  {
    path: '/accounts',
    name: 'Accounts',
    component: () => import('@/views/AccountsView.vue'),
  },
  {
    path: '/categories',
    name: 'Categories',
    component: () => import('@/views/CategoriesView.vue'),
  },
  {
    path: '/tags',
    name: 'Tags',
    component: () => import('@/views/TagsView.vue'),
  },
  {
    path: '/export',
    name: 'Export',
    component: () => import('@/views/ExportView.vue'),
  },
  {
    path: '/import',
    name: 'Import',
    component: () => import('@/views/ImportView.vue'),
  },
  {
    path: '/ai',
    name: 'AI',
    component: () => import('@/views/AIView.vue'),
  },
  {
    path: '/theme',
    name: 'Theme',
    component: () => import('@/views/ThemeView.vue'),
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  if (!to.meta.public && !authStore.isAuthenticated) {
    next('/login')
  } else if (to.meta.public && authStore.isAuthenticated && to.name === 'Login') {
    next('/')
  } else {
    next()
  }
})

export default router
