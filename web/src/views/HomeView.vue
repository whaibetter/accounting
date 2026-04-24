<template>
  <div class="page home-page">
    <div class="home-header">
      <div>
        <div class="home-greet">你好呀 👋</div>
        <div class="home-date">开始记录你的每一笔开销吧</div>
      </div>
      <span class="eye-btn" @click="toggleAmount">{{ showAmount ? '👁' : '👁‍🗨' }}</span>
    </div>

    <div class="card" style="margin-top: 8px">
      <div class="card-top-row">
        <span class="card-label">本月支出(元)</span>
        <span class="eye-btn" @click="toggleAmount">{{ showAmount ? '👁' : '👁‍🗨' }}</span>
      </div>
      <div class="amount-row">
        <span class="amount-val">{{ showAmount ? formatMoneyWithSymbol(monthExpense) : '¥ ****' }}</span>
      </div>
      <div class="sub-info">
        <span>本月收入 {{ showAmount ? formatMoneyWithSymbol(monthIncome) : '****' }}</span>
        <span>结余 {{ showAmount ? formatMoneyWithSymbol(monthBalance) : '****' }}</span>
      </div>

      <div style="margin-top: 18px">
        <div class="section-title">本月支出占比</div>
        <div class="donut-chart-wrap">
          <div class="donut-chart-container">
            <canvas ref="donutCanvas" width="130" height="130"></canvas>
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
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch, nextTick } from 'vue'
import { useStatisticsStore, useCategoryStore } from '@/stores/data'
import { formatMoney, formatMoneyWithSymbol, getMonthRange, CATEGORY_COLORS } from '@/utils/format'
import dayjs from 'dayjs'
import Chart from 'chart.js/auto'

const COLORS = CATEGORY_COLORS
const statsStore = useStatisticsStore()
const categoryStore = useCategoryStore()

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

  chartInstance = new Chart(donutCanvas.value, {
    type: 'doughnut',
    data: {
      labels: data.map(d => d.category_name),
      datasets: [{
        data: data.map(d => d.amount),
        backgroundColor: colors,
        borderWidth: 0,
        cutout: '72%',
      }],
    },
    options: {
      responsive: false,
      plugins: {
        legend: { display: false },
        tooltip: { enabled: false },
      },
      animation: { animateRotate: true, duration: 800 },
    },
  })
}

watch(categoryStats, () => {
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
.home-header {
  padding: 16px 20px 8px;
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
  margin-top: 2px;
}

.eye-btn {
  font-size: 16px;
  color: #c4b8a0;
  cursor: pointer;
}

.card-top-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
}

.card-label {
  font-size: 13px;
  color: var(--text-muted);
}

.amount-row {
  display: flex;
  align-items: baseline;
  gap: 4px;
  margin-top: 4px;
}

.amount-val {
  font-size: 38px;
  font-weight: 800;
  color: var(--text-primary);
  letter-spacing: -1px;
}

.sub-info {
  display: flex;
  gap: 16px;
  margin-top: 4px;
  font-size: 12px;
  color: var(--text-light);
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

.donut-center {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
  pointer-events: none;
}

.donut-amount {
  font-size: 17px;
  font-weight: 800;
  color: var(--text-primary);
}

.donut-label {
  font-size: 11px;
  color: var(--text-muted);
}

.legend-list {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
}

.legend-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
}

.legend-name {
  color: #666;
  flex: 1;
}

.legend-pct {
  font-weight: 700;
  color: #444;
}

.legend-amt {
  color: #999;
  font-size: 11px;
}
</style>
