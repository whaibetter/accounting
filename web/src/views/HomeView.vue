<template>
  <div class="page home-page">
    <div class="home-header">
      <div>
        <div class="home-greet">你好呀 👋</div>
        <div class="home-date">开始记录你的每一笔开销吧</div>
      </div>
      <span class="eye-btn" @click="toggleAmount">{{ showAmount ? '👁' : '👁‍🗨' }}</span>
    </div>

    <div class="card summary-card">
      <div class="card-top-row">
        <span class="card-label">本月支出(元)</span>
      </div>
      <div class="amount-row">
        <span class="amount-val">{{ showAmount ? formatMoneyWithSymbol(monthExpense) : '¥ ****' }}</span>
      </div>
      <div class="sub-info">
        <span>本月收入 {{ showAmount ? formatMoneyWithSymbol(monthIncome) : '****' }}</span>
        <span>结余 {{ showAmount ? formatMoneyWithSymbol(monthBalance) : '****' }}</span>
      </div>

      <div style="margin-top: 20px">
        <div class="section-title">本月支出占比</div>
        <template v-if="categoryStats.length > 0">
          <div class="donut-chart-wrap">
            <div class="donut-chart-container">
              <canvas ref="donutCanvas"></canvas>
              <div class="donut-center">
                <div class="donut-amount">{{ showAmount ? formatMoney(monthExpense) : '****' }}</div>
                <div class="donut-label">总支出</div>
              </div>
            </div>
            <div class="legend-list">
              <div v-for="(stat, idx) in categoryStats" :key="stat.category_id" class="legend-item">
                <div class="legend-dot" :style="{ background: COLORS[idx % COLORS.length] }"></div>
                <span class="legend-name">{{ stat.category_name }}</span>
                <span class="legend-pct">{{ stat.percentage.toFixed(0) }}%</span>
                <span class="legend-amt">{{ showAmount ? '¥' + formatMoney(stat.amount) : '****' }}</span>
              </div>
            </div>
          </div>
        </template>
        <div class="chart-empty" v-else>
          <span class="empty-icon">📊</span>
          <span class="empty-text">暂无支出数据</span>
          <span class="empty-hint">本月还没有支出记录</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch, nextTick } from 'vue'
import { useStatisticsStore, useCategoryStore } from '@/stores/data'
import { useThemeStore, getThemeColor } from '@/stores/theme'
import { formatMoney, formatMoneyWithSymbol, getMonthRange, CATEGORY_COLORS } from '@/utils/format'
import dayjs from 'dayjs'
import Chart from 'chart.js/auto'

const COLORS = CATEGORY_COLORS
const statsStore = useStatisticsStore()
const categoryStore = useCategoryStore()
const themeStore = useThemeStore()

const showAmount = ref(true)
const donutCanvas = ref(null)
let chartInstance = null

const monthRange = computed(() => getMonthRange(dayjs()))
const monthExpense = computed(() => statsStore.overview?.total_expense || 0)
const monthIncome = computed(() => statsStore.overview?.total_income || 0)
const monthBalance = computed(() => statsStore.overview?.balance || 0)
const categoryStats = computed(() => statsStore.categoryStats)

function toggleAmount() {
  showAmount.value = !showAmount.value
}

function renderDonut() {
  if (!donutCanvas.value || !categoryStats.value.length) return

  if (chartInstance) {
    chartInstance.destroy()
  }

  const data = categoryStats.value
  const colors = data.map((_, i) => COLORS[i % COLORS.length])
  const borderColor = getThemeColor('--bg-card') || '#fff'

  const ctx = donutCanvas.value.getContext('2d')
  chartInstance = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: data.map(d => d.category_name),
      datasets: [{
        data: data.map(d => d.amount),
        backgroundColor: colors,
        borderWidth: 2,
        borderColor,
        cutout: '70%',
        hoverOffset: 4,
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          enabled: true,
          backgroundColor: getThemeColor('--bg-card') || '#fff',
          titleColor: getThemeColor('--text-primary') || '#333',
          bodyColor: getThemeColor('--text-secondary') || '#666',
          borderColor: getThemeColor('--border') || '#eee',
          borderWidth: 1,
          callbacks: {
            label: (ctx) => `${ctx.label}: ¥${formatMoney(ctx.parsed)}`
          }
        },
      },
      animation: { animateRotate: true, duration: 800 },
    },
  })
}

watch(categoryStats, () => {
  nextTick(renderDonut)
})

watch(() => themeStore.themeVersion, () => {
  nextTick(renderDonut)
})

onMounted(async () => {
  const range = monthRange.value
  await Promise.all([
    statsStore.fetchOverview(range),
    statsStore.fetchCategoryStats({ ...range, type: 1 }),
    categoryStore.fetchCategories(),
  ])
  nextTick(renderDonut)
})
</script>

<style scoped>
.home-page {
  padding-bottom: calc(var(--nav-height) + var(--safe-bottom) + 12px);
}

.home-header {
  padding: 18px 20px 12px;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.home-greet {
  font-size: 22px;
  font-weight: 800;
  color: var(--text-primary);
}

.home-date {
  font-size: 13px;
  color: var(--text-muted);
  margin-top: 3px;
}

.eye-btn {
  font-size: 17px;
  color: #c4b8a0;
  cursor: pointer;
}

.summary-card {
  margin: 8px 16px;
  padding: 20px;
}

.card-top-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}

.card-label {
  font-size: 13px;
  color: var(--text-muted);
}

.amount-row {
  display: flex;
  align-items: baseline;
  gap: 2px;
  margin-top: 4px;
}

.amount-val {
  font-size: 36px;
  font-weight: 800;
  color: var(--text-primary);
  letter-spacing: -1px;
}

.sub-info {
  display: flex;
  gap: 16px;
  margin-top: 6px;
  font-size: 12px;
  color: var(--text-light);
}

.section-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-secondary);
  margin-bottom: 14px;
}

.donut-chart-wrap {
  display: flex;
  align-items: center;
  gap: 20px;
}

.donut-chart-container {
  width: 130px;
  height: 130px;
  position: relative;
  flex-shrink: 0;
}

.donut-chart-container canvas {
  width: 100% !important;
  height: 100% !important;
}

.donut-center {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
  pointer-events: none;
}

.donut-amount {
  font-size: 16px;
  font-weight: 800;
  color: var(--text-primary);
}

.donut-label {
  font-size: 10px;
  color: var(--text-muted);
}

.legend-list {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 9px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
}

.legend-dot {
  width: 9px;
  height: 9px;
  border-radius: 50%;
  flex-shrink: 0;
}

.legend-name {
  color: var(--text-secondary);
  flex: 1;
}

.legend-pct {
  font-weight: 700;
  color: var(--text-primary);
  min-width: 28px;
  text-align: right;
}

.legend-amt {
  color: var(--text-muted);
  font-size: 11px;
  min-width: 56px;
  text-align: right;
}

.chart-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  color: var(--text-muted);
}

.chart-empty .empty-icon {
  font-size: 36px;
  margin-bottom: 8px;
}

.chart-empty .empty-text {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-secondary);
}

.chart-empty .empty-hint {
  font-size: 12px;
  margin-top: 4px;
}
</style>
