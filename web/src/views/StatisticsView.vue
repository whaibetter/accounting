<template>
  <div class="page stats-page">
    <div class="page-header">
      <span class="page-title">统计</span>
      <div class="month-picker" @click="showMonthPicker = true">
        {{ currentMonthLabel }} ▾
      </div>
    </div>

    <div class="tab-bar">
      <div class="tab-item" :class="{ active: statsType === 1 }" @click="statsType = 1">支出</div>
      <div class="tab-item" :class="{ active: statsType === 2 }" @click="statsType = 2">收入</div>
    </div>

    <div class="card" style="padding: 20px; text-align: center">
      <div class="big-amount">¥ {{ formatMoney(totalAmount) }}</div>
      <div class="big-label">本月总{{ statsType === 1 ? '支出' : '收入' }} | 日均 ¥ {{ formatMoney(dailyAvg) }}</div>
    </div>

    <div class="card" style="padding: 16px">
      <div class="section-title">支出趋势</div>
      <div class="chart-container">
        <canvas ref="trendCanvas"></canvas>
      </div>
    </div>

    <div class="card" style="padding: 16px">
      <div class="section-title">支出占比</div>
      <div class="stats-donut-wrap">
        <div class="donut-wrap">
          <canvas ref="donutCanvas" width="120" height="120"></canvas>
        </div>
        <div class="legend-wrap">
          <div v-for="(stat, idx) in categoryStats" :key="stat.category_id" class="legend-item">
            <div class="legend-dot" :style="{ background: COLORS[idx % COLORS.length] }"></div>
            <span class="legend-name">{{ stat.category_name }}</span>
            <span class="legend-pct">{{ stat.percentage.toFixed(0) }}%</span>
          </div>
        </div>
      </div>
    </div>

    <div v-if="showMonthPicker" class="modal-overlay" @click.self="showMonthPicker = false">
      <div class="month-picker-modal">
        <div class="picker-header">
          <button @click="prevMonth">‹</button>
          <span>{{ pickerYear }}年{{ pickerMonth }}月</span>
          <button @click="nextMonth">›</button>
        </div>
        <div class="picker-actions">
          <button class="btn-primary" @click="confirmMonth">确定</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { useStatisticsStore } from '@/stores/data'
import { formatMoney, getMonthRange, CATEGORY_COLORS } from '@/utils/format'
import dayjs from 'dayjs'
import Chart from 'chart.js/auto'

const COLORS = CATEGORY_COLORS
const statsStore = useStatisticsStore()

const statsType = ref(1)
const currentMonth = ref(dayjs())
const showMonthPicker = ref(false)
const pickerYear = ref(dayjs().year())
const pickerMonth = ref(dayjs().month() + 1)
const trendCanvas = ref(null)
const donutCanvas = ref(null)
let trendChart = null
let donutChart = null

const monthRange = computed(() => getMonthRange(currentMonth.value))
const currentMonthLabel = computed(() => currentMonth.value.format('YYYY年M月'))
const categoryStats = computed(() => statsStore.categoryStats)
const totalAmount = computed(() => {
  if (statsType.value === 1) return statsStore.overview?.total_expense || 0
  return statsStore.overview?.total_income || 0
})
const dailyAvg = computed(() => {
  const days = currentMonth.value.daysInMonth()
  return totalAmount.value / days
})

async function fetchData() {
  const range = monthRange.value
  await Promise.all([
    statsStore.fetchOverview(range),
    statsStore.fetchCategoryStats({ ...range, type: statsType.value }),
    statsStore.fetchTrend({ ...range, granularity: 'day' }),
  ])
  nextTick(renderCharts)
}

function renderCharts() {
  renderTrendChart()
  renderDonutChart()
}

function renderTrendChart() {
  if (!trendCanvas.value) return
  if (trendChart) trendChart.destroy()

  const data = statsStore.trend
  const labels = data.map(d => dayjs(d.period).format('M/D'))
  const values = data.map(d => statsType.value === 1 ? d.expense : d.income)

  trendChart = new Chart(trendCanvas.value, {
    type: 'line',
    data: {
      labels,
      datasets: [{
        data: values,
        borderColor: '#d4a574',
        backgroundColor: 'rgba(212, 165, 116, 0.1)',
        borderWidth: 2.5,
        fill: true,
        tension: 0.4,
        pointRadius: 0,
        pointHoverRadius: 4,
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false }, tooltip: { enabled: true } },
      scales: {
        x: { display: true, grid: { display: false }, ticks: { font: { size: 10 }, color: '#ccc', maxTicksLimit: 6 } },
        y: { display: false },
      },
    },
  })
}

function renderDonutChart() {
  if (!donutCanvas.value || !categoryStats.value.length) return
  if (donutChart) donutChart.destroy()

  const data = categoryStats.value
  const colors = data.map((_, i) => COLORS[i % COLORS.length])

  donutChart = new Chart(donutCanvas.value, {
    type: 'doughnut',
    data: {
      labels: data.map(d => d.category_name),
      datasets: [{
        data: data.map(d => d.amount),
        backgroundColor: colors,
        borderWidth: 0,
        cutout: '68%',
      }],
    },
    options: {
      responsive: false,
      plugins: { legend: { display: false }, tooltip: { enabled: false } },
    },
  })
}

function prevMonth() {
  if (pickerMonth.value === 1) { pickerMonth.value = 12; pickerYear.value-- }
  else pickerMonth.value--
}

function nextMonth() {
  if (pickerMonth.value === 12) { pickerMonth.value = 1; pickerYear.value++ }
  else pickerMonth.value++
}

function confirmMonth() {
  currentMonth.value = dayjs(`${pickerYear.value}-${String(pickerMonth.value).padStart(2, '0')}-01`)
  showMonthPicker.value = false
  fetchData()
}

watch(statsType, fetchData)
watch(currentMonth, fetchData)

onMounted(fetchData)
</script>

<style scoped>
.big-amount {
  font-size: 26px;
  font-weight: 800;
  color: var(--text-primary);
}

.big-label {
  font-size: 12px;
  color: var(--text-muted);
  margin-top: 2px;
}

.chart-container {
  height: 180px;
  position: relative;
}

.stats-donut-wrap {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 12px 0;
}

.donut-wrap {
  flex-shrink: 0;
}

.legend-wrap {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
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

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 200;
  padding: 20px;
}

.month-picker-modal {
  background: var(--bg-card);
  border-radius: 20px;
  padding: 24px;
  width: 100%;
  max-width: 320px;
}

.picker-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 17px;
  font-weight: 600;
  margin-bottom: 20px;
}

.picker-header button {
  font-size: 22px;
  color: var(--accent);
  padding: 4px 12px;
}

.picker-actions {
  text-align: center;
}

.picker-actions .btn-primary {
  width: 100%;
}
</style>
