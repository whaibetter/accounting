<template>
  <div class="page home">
    <div class="page-header">
      <h1>记账</h1>
      <span class="date-text">{{ todayStr }}</span>
    </div>

    <div class="overview-card card" v-if="overview">
      <div class="overview-balance">
        <span class="label">本月结余</span>
        <span class="amount" :class="overview.balance >= 0 ? 'positive' : 'negative'">
          ¥{{ formatMoney(overview.balance) }}
        </span>
      </div>
      <div class="overview-row">
        <div class="overview-item">
          <span class="dot income"></span>
          <span class="label">收入</span>
          <span class="value income-text">¥{{ formatMoney(overview.total_income) }}</span>
        </div>
        <div class="overview-item">
          <span class="dot expense"></span>
          <span class="label">支出</span>
          <span class="value expense-text">¥{{ formatMoney(overview.total_expense) }}</span>
        </div>
      </div>
    </div>

    <div class="section-title" style="margin-top: 28px">最近账单</div>
    <div class="bill-list" v-if="bills.length">
      <div
        class="bill-item card"
        v-for="bill in bills"
        :key="bill.id"
        @click="goToBills"
      >
        <div class="bill-left">
          <span class="bill-icon">{{ getCategoryIcon(bill.category_id) }}</span>
          <div class="bill-info">
            <span class="bill-category">{{ bill.category_name }}</span>
            <span class="bill-meta">{{ bill.account_name }}{{ bill.remark ? ' · ' + bill.remark : '' }}</span>
          </div>
        </div>
        <span class="bill-amount" :class="bill.type === 2 ? 'income-text' : 'expense-text'">
          {{ bill.type === 2 ? '+' : '-' }}¥{{ formatMoney(bill.amount) }}
        </span>
      </div>
    </div>
    <div class="empty-state" v-else>
      <div class="icon">📝</div>
      <p>暂无账单，点击下方记账开始</p>
    </div>

    <button class="fab" @click="$router.push('/add')">
      <span>+</span>
    </button>
    <button class="fab fab-ai" @click="$router.push('/ai-accounting')">
      <span>🤖</span>
    </button>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { statisticsApi, billApi, type Overview, type Bill } from '@/api/types'
import { useDataStore } from '@/stores/data'

const router = useRouter()
const store = useDataStore()
const overview = ref<Overview | null>(null)
const bills = ref<Bill[]>([])

const todayStr = new Date().toLocaleDateString('zh-CN', { month: 'long', day: 'numeric', weekday: 'short' })

function formatMoney(n: number) {
  return Math.abs(n).toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

const iconMap: Record<string, string> = {
  '1': '🍜', '2': '🚌', '3': '🛒', '4': '🏠', '5': '🎮',
  '6': '🏥', '7': '📚', '8': '📱', '9': '🎁', '10': '📌',
  '46': '💰', '47': '💼', '48': '📈', '49': '🧧', '50': '↩️', '51': '📌',
}

function getCategoryIcon(id: number) {
  const parentId = Math.floor(id / 10) * 10
  if (id <= 10 || (id >= 46 && id <= 51)) return iconMap[String(id)] || iconMap[String(parentId)] || '📌'
  return iconMap[String(parentId)] || '📌'
}

function goToBills() {
  router.push('/bills')
}

onMounted(async () => {
  await store.loadAll()
  const now = new Date()
  const start = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-01`
  const end = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}`

  try {
    const [overviewRes, billsRes] = await Promise.all([
      statisticsApi.overview({ start_date: start, end_date: end }),
      billApi.list({ page: 1, size: 5, start_date: start, end_date: end }),
    ])
    overview.value = overviewRes.data
    bills.value = billsRes.data?.items || []
  } catch (e) {
    console.error(e)
  }
})
</script>

<style scoped>
.overview-card {
  background: linear-gradient(135deg, #1e1e30 0%, #1a1a28 100%);
  border: 1px solid rgba(99, 102, 241, 0.15);
  overflow: hidden;
  position: relative;
}
.overview-card::before {
  content: '';
  position: absolute;
  top: -50%;
  right: -30%;
  width: 200px;
  height: 200px;
  background: radial-gradient(circle, rgba(99, 102, 241, 0.08) 0%, transparent 70%);
  pointer-events: none;
}

.overview-balance {
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin-bottom: 20px;
}
.overview-balance .label { font-size: 13px; color: var(--text-secondary); }
.overview-balance .amount {
  font-size: 36px;
  font-weight: 800;
  letter-spacing: -1px;
  font-variant-numeric: tabular-nums;
}
.positive { color: var(--income); }
.negative { color: var(--expense); }

.overview-row {
  display: flex;
  gap: 24px;
}
.overview-item {
  display: flex;
  align-items: center;
  gap: 8px;
}
.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}
.dot.income { background: var(--income); }
.dot.expense { background: var(--expense); }
.overview-item .label { font-size: 13px; color: var(--text-secondary); }
.income-text { color: var(--income); }
.expense-text { color: var(--expense); }
.overview-item .value { font-size: 15px; font-weight: 600; font-variant-numeric: tabular-nums; }

.bill-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.bill-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 16px;
  cursor: pointer;
}
.bill-item:active { transform: scale(0.98); }

.bill-left {
  display: flex;
  align-items: center;
  gap: 12px;
}
.bill-icon {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  background: var(--bg-input);
  border-radius: 12px;
}
.bill-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.bill-category { font-size: 15px; font-weight: 500; }
.bill-meta { font-size: 12px; color: var(--text-muted); }

.bill-amount {
  font-size: 16px;
  font-weight: 700;
  font-variant-numeric: tabular-nums;
}

.date-text { font-size: 13px; color: var(--text-secondary); }

.fab {
  position: fixed;
  bottom: 100px;
  right: calc(50% - 220px);
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: var(--primary);
  color: #fff;
  font-size: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 20px rgba(99, 102, 241, 0.4);
  z-index: 50;
  transition: all var(--transition);
}
.fab:active { transform: scale(0.9); }
.fab-ai {
  right: calc(50% - 220px + 70px);
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  font-size: 22px;
  box-shadow: 0 4px 20px rgba(139, 92, 246, 0.4);
}
@media (max-width: 480px) {
  .fab { right: 20px; }
  .fab-ai { right: 90px; }
}
</style>
