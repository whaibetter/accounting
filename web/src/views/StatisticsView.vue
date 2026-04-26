<template>
  <div class="page stats-page">
    <div class="page-header">
      <span class="page-title">统计</span>
      <div class="time-range-selector" @click="showTimeRangePicker = true">
        {{ currentTimeLabel }} ▾
      </div>
    </div>

    <div class="time-presets">
      <button
        v-for="preset in timePresets"
        :key="preset.value"
        class="preset-btn"
        :class="{ active: selectedPreset === preset.value }"
        @click="applyPreset(preset.value)"
      >
        {{ preset.label }}
      </button>
    </div>

    <div class="tab-bar">
      <div class="tab-item" :class="{ active: statsType === 1 }" @click="statsType = 1">支出</div>
      <div class="tab-item" :class="{ active: statsType === 2 }" @click="statsType = 2">收入</div>
      <div class="tab-item" :class="{ active: statsType === 3 }" @click="statsType = 3">余额趋势</div>
    </div>

    <template v-if="statsType === 3">
      <div class="card" style="padding: 16px">
        <div class="section-header">
          <span class="section-title">余额变化趋势</span>
          <button class="chart-toggle-btn" :class="{ active: chartType === 'bar' }" @click="toggleChartType">
            {{ chartType === 'line' ? '📈 折线' : '📊 柱状' }}
          </button>
        </div>
        <div class="chart-container" v-if="balanceData.length">
          <canvas ref="balanceCanvas"></canvas>
        </div>
        <div class="chart-empty" v-else>
          <span class="empty-icon">📈</span>
          <span class="empty-text">暂无余额数据</span>
          <span class="empty-hint">请先添加账户和账单记录</span>
        </div>
      </div>

      <div class="card" style="padding: 16px" v-if="balanceData.length">
        <div class="section-title">收支明细</div>
        <div class="chart-container" style="height: 200px">
          <canvas ref="balanceDetailCanvas"></canvas>
        </div>
        <div class="balance-stats" v-if="balanceSummary">
          <div class="bs-item">
            <span class="bs-label">期初余额</span>
            <span class="bs-value">¥{{ formatMoney(balanceSummary.startBalance) }}</span>
          </div>
          <div class="bs-item">
            <span class="bs-label">期末余额</span>
            <span class="bs-value">¥{{ formatMoney(balanceSummary.endBalance) }}</span>
          </div>
          <div class="bs-item">
            <span class="bs-label">总收入</span>
            <span class="bs-value income">¥{{ formatMoney(balanceSummary.totalIncome) }}</span>
          </div>
          <div class="bs-item">
            <span class="bs-label">总支出</span>
            <span class="bs-value expense">¥{{ formatMoney(balanceSummary.totalExpense) }}</span>
          </div>
        </div>
      </div>
    </template>

    <template v-else>
      <div class="card" style="padding: 20px; text-align: center">
        <div class="big-amount">¥ {{ formatMoney(totalAmount) }}</div>
        <div class="big-label">{{ currentTimeLabel }}总{{ statsType === 1 ? '支出' : '收入' }} | 日均 ¥ {{ formatMoney(dailyAvg) }}</div>
      </div>

      <div class="card" style="padding: 16px">
        <div class="section-title">{{ statsType === 1 ? '支出' : '收入' }}趋势</div>
        <div class="chart-container" v-if="hasTrendData">
          <canvas ref="trendCanvas"></canvas>
        </div>
        <div class="chart-empty" v-else>
          <span class="empty-icon">📈</span>
          <span class="empty-text">暂无趋势数据</span>
          <span class="empty-hint">该时间段还没有账单记录</span>
        </div>
      </div>

      <div class="card" style="padding: 16px">
        <div class="section-title">{{ statsType === 1 ? '支出' : '收入' }}占比</div>
        <template v-if="hasCategoryData">
          <div class="stats-donut-wrap">
            <div class="donut-wrap">
              <canvas ref="donutCanvas"></canvas>
            </div>
            <div class="legend-wrap">
              <div v-for="(stat, idx) in categoryStats" :key="stat.category_id" class="legend-item">
                <div class="legend-dot" :style="{ background: COLORS[idx % COLORS.length] }"></div>
                <span class="legend-name">{{ stat.category_name }}</span>
                <span class="legend-pct">{{ stat.percentage.toFixed(0) }}%</span>
              </div>
            </div>
          </div>
        </template>
        <div class="chart-empty" v-else>
          <span class="empty-icon">📊</span>
          <span class="empty-text">暂无分类数据</span>
          <span class="empty-hint">该时间段还没有{{ statsType === 1 ? '支出' : '收入' }}记录</span>
        </div>
      </div>
    </template>

    <MonthPicker
      :visible="showTimeRangePicker"
      v-model="selectedMonth"
      @select="onMonthSelect"
      @close="showTimeRangePicker = false"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { useStatisticsStore } from '@/stores/data'
import { useThemeStore, getThemeColor } from '@/stores/theme'
import { formatMoney, CATEGORY_COLORS } from '@/utils/format'
import dayjs from 'dayjs'
import Chart from 'chart.js/auto'
import MonthPicker from '@/components/MonthPicker.vue'

const COLORS = CATEGORY_COLORS
const statsStore = useStatisticsStore()
const themeStore = useThemeStore()

const statsType = ref(1)
const selectedPreset = ref('month')
const selectedMonth = ref(dayjs())
const showTimeRangePicker = ref(false)
const chartType = ref('line')

const trendCanvas = ref(null)
const donutCanvas = ref(null)
const balanceCanvas = ref(null)
const balanceDetailCanvas = ref(null)
let trendChart = null
let donutChart = null
let balanceChart = null
let balanceDetailChart = null

const balanceData = ref([])

const timePresets = [
  { label: '今日', value: 'today' },
  { label: '本周', value: 'week' },
  { label: '本月', value: 'month' },
  { label: '本季', value: 'quarter' },
  { label: '本年', value: 'year' },
]

const dateRange = computed(() => {
  const now = dayjs()
  let start
  switch (selectedPreset.value) {
    case 'today':
      start = now.startOf('day')
      break
    case 'week':
      start = now.startOf('week')
      break
    case 'month':
      start = now.startOf('month')
      break
    case 'quarter':
      const quarter = Math.floor(now.month() / 3)
      start = now.month(quarter * 3).startOf('month')
      break
    case 'year':
      start = now.startOf('year')
      break
    default:
      start = now.startOf('month')
  }
  return {
    start_date: start.format('YYYY-MM-DD'),
    end_date: now.format('YYYY-MM-DD'),
  }
})

const currentTimeLabel = computed(() => {
  const map = {
    today: '今日',
    week: '本周',
    month: selectedMonth.value.format('YYYY年M月'),
    quarter: '本季度',
    year: '本年度',
  }
  return map[selectedPreset.value] || selectedMonth.value.format('YYYY年M月')
})

const categoryStats = computed(() => statsStore.categoryStats)
const hasTrendData = computed(() => statsStore.trend && statsStore.trend.length > 0)
const hasCategoryData = computed(() => categoryStats.value && categoryStats.value.length > 0)
const totalAmount = computed(() => {
  if (statsType.value === 1) return statsStore.overview?.total_expense || 0
  return statsStore.overview?.total_income || 0
})
const dailyAvg = computed(() => {
  const range = dateRange.value
  const days = dayjs(range.end_date).diff(dayjs(range.start_date), 'day') + 1
  return totalAmount.value / Math.max(days, 1)
})

const balanceSummary = computed(() => {
  if (!balanceData.value.length) return null
  const first = balanceData.value[0]
  const data = first.data
  if (!data || !data.length) return null
  return {
    startBalance: data[0].balance,
    endBalance: data[data.length - 1].balance,
    totalIncome: data.reduce((s, d) => s + d.income, 0),
    totalExpense: data.reduce((s, d) => s + d.expense, 0),
  }
})

function applyPreset(value) {
  selectedPreset.value = value
  fetchData()
}

function onMonthSelect() {
  selectedPreset.value = 'month'
  fetchData()
}

function toggleChartType() {
  chartType.value = chartType.value === 'line' ? 'bar' : 'line'
  nextTick(renderBalanceChart)
}

async function fetchData() {
  const range = dateRange.value
  if (statsType.value === 3) {
    await loadBalanceData()
  } else {
    await Promise.all([
      statsStore.fetchOverview(range),
      statsStore.fetchCategoryStats({ ...range, type: statsType.value }),
      statsStore.fetchTrend({ ...range, granularity: selectedPreset.value === 'today' ? 'hour' : 'day' }),
    ])
    nextTick(renderCharts)
  }
}

async function loadBalanceData() {
  const range = dateRange.value
  try {
    const { statisticsApi } = await import('@/services')
    const res = await statisticsApi.balanceTrend(range)
    if (res.data.code === 200) {
      balanceData.value = res.data.data || []
    }
  } catch (e) {
    console.error(e)
    balanceData.value = []
  }
  nextTick(() => {
    renderBalanceChart()
    renderBalanceDetailChart()
  })
}

function renderCharts() {
  renderTrendChart()
  renderDonutChart()
}

function renderTrendChart() {
  if (!trendCanvas.value || !hasTrendData.value) return
  if (trendChart) trendChart.destroy()

  const data = statsStore.trend
  const accent = getThemeColor('--accent') || '#d4a574'
  const textColor = getThemeColor('--text-muted') || '#ccc'

  const labels = data.map(d => {
    if (selectedPreset.value === 'today') return dayjs(d.period).format('H:00')
    return dayjs(d.period).format('M/D')
  })
  const values = data.map(d => statsType.value === 1 ? d.expense : d.income)

  trendChart = new Chart(trendCanvas.value, {
    type: 'line',
    data: {
      labels,
      datasets: [{
        data: values,
        borderColor: accent,
        backgroundColor: accent + '1a',
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
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: getThemeColor('--bg-card') || '#fff',
          titleColor: getThemeColor('--text-primary') || '#333',
          bodyColor: getThemeColor('--text-secondary') || '#666',
          borderColor: getThemeColor('--border') || '#eee',
          borderWidth: 1,
        },
      },
      scales: {
        x: { display: true, grid: { display: false }, ticks: { font: { size: 10 }, color: textColor, maxTicksLimit: 6 } },
        y: { display: false },
      },
    },
  })
}

function renderDonutChart() {
  if (!donutCanvas.value || !hasCategoryData.value) return
  if (donutChart) donutChart.destroy()

  const data = categoryStats.value
  const colors = data.map((_, i) => COLORS[i % COLORS.length])
  const borderColor = getThemeColor('--bg-card') || '#fff'

  const ctx = donutCanvas.value.getContext('2d')
  donutChart = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: data.map(d => d.category_name),
      datasets: [{
        data: data.map(d => d.amount),
        backgroundColor: colors,
        borderWidth: 2,
        borderColor,
        cutout: '68%',
        hoverOffset: 4,
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: getThemeColor('--bg-card') || '#fff',
          titleColor: getThemeColor('--text-primary') || '#333',
          bodyColor: getThemeColor('--text-secondary') || '#666',
          borderColor: getThemeColor('--border') || '#eee',
          borderWidth: 1,
        },
      },
    },
  })
}

function renderBalanceChart() {
  if (!balanceCanvas.value || !balanceData.value.length) return
  if (balanceChart) balanceChart.destroy()

  const isLine = chartType.value === 'line'
  const textColor = getThemeColor('--text-muted') || '#999'
  const gridColor = getThemeColor('--border') || '#f0f0f0'

  const datasets = balanceData.value.map((account) => {
    const base = {
      label: account.account_name,
      data: account.data.map(d => d.balance),
    }
    if (isLine) {
      base.borderColor = account.color
      base.backgroundColor = account.color + '18'
      base.borderWidth = 2
      base.fill = true
      base.tension = 0.4
      base.pointRadius = account.data.length < 60 ? 2 : 0
      base.pointHoverRadius = 4
    } else {
      base.backgroundColor = account.color + 'aa'
      base.borderRadius = 3
      base.barMaxWidth = 16
    }
    return base
  })

  const dates = balanceData.value[0]?.data.map(d => d.date.slice(5)) || []

  balanceChart = new Chart(balanceCanvas.value, {
    type: isLine ? 'line' : 'bar',
    data: { labels: dates, datasets },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { mode: 'index', intersect: false },
      plugins: {
        legend: { display: balanceData.value.length > 1, position: 'top', labels: { boxWidth: 12, font: { size: 11 }, color: textColor } },
        tooltip: {
          backgroundColor: getThemeColor('--bg-card') || '#fff',
          titleColor: getThemeColor('--text-primary') || '#333',
          bodyColor: getThemeColor('--text-secondary') || '#666',
          borderColor: getThemeColor('--border') || '#eee',
          borderWidth: 1,
          callbacks: {
            label: (ctx) => `${ctx.dataset.label}: ¥${formatMoney(ctx.parsed.y)}`
          }
        },
      },
      scales: {
        x: { grid: { display: false }, ticks: { font: { size: 10 }, color: textColor, maxTicksLimit: 8 } },
        y: {
          grid: { color: gridColor },
          ticks: {
            font: { size: 10 }, color: textColor,
            callback: (v) => {
              if (Math.abs(v) >= 10000) return (v / 10000).toFixed(1) + 'w'
              if (Math.abs(v) >= 1000) return (v / 1000).toFixed(1) + 'k'
              return v.toFixed(0)
            }
          },
        },
      },
    },
  })
}

function renderBalanceDetailChart() {
  if (!balanceDetailCanvas.value || !balanceData.value.length) return
  if (balanceDetailChart) balanceDetailChart.destroy()

  const first = balanceData.value[0]
  const data = first.data
  const dates = data.map(d => d.date.slice(5))
  const textColor = getThemeColor('--text-muted') || '#999'
  const gridColor = getThemeColor('--border') || '#f0f0f0'

  balanceDetailChart = new Chart(balanceDetailCanvas.value, {
    type: 'bar',
    data: {
      labels: dates,
      datasets: [
        {
          label: '收入',
          data: data.map(d => d.income),
          backgroundColor: getThemeColor('--success') + 'aa' || '#34d399aa',
          borderRadius: 3,
          barMaxWidth: 14,
        },
        {
          label: '支出',
          data: data.map(d => d.expense),
          backgroundColor: getThemeColor('--danger') + 'aa' || '#f87171aa',
          borderRadius: 3,
          barMaxWidth: 14,
        }
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { position: 'top', labels: { boxWidth: 12, font: { size: 11 }, color: textColor } },
        tooltip: {
          backgroundColor: getThemeColor('--bg-card') || '#fff',
          titleColor: getThemeColor('--text-primary') || '#333',
          bodyColor: getThemeColor('--text-secondary') || '#666',
          borderColor: getThemeColor('--border') || '#eee',
          borderWidth: 1,
          callbacks: {
            label: (ctx) => `${ctx.dataset.label}: ¥${formatMoney(ctx.parsed.y)}`
          }
        },
      },
      scales: {
        x: { grid: { display: false }, ticks: { font: { size: 10 }, color: textColor, maxTicksLimit: 8 } },
        y: {
          grid: { color: gridColor },
          ticks: {
            font: { size: 10 }, color: textColor,
            callback: (v) => {
              if (Math.abs(v) >= 10000) return (v / 10000).toFixed(1) + 'w'
              if (Math.abs(v) >= 1000) return (v / 1000).toFixed(1) + 'k'
              return v.toFixed(0)
            }
          },
        },
      },
    },
  })
}

watch(statsType, fetchData)
watch(() => themeStore.themeVersion, () => {
  nextTick(() => {
    if (statsType.value === 3) {
      renderBalanceChart()
      renderBalanceDetailChart()
    } else {
      renderCharts()
    }
  })
})

onMounted(fetchData)
</script>

<style scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px 8px;
}

.page-title {
  font-size: 20px;
  font-weight: 800;
  color: var(--text-primary);
}

.time-range-selector {
  font-size: 13px;
  color: var(--accent);
  cursor: pointer;
  font-weight: 600;
}

.time-presets {
  display: flex;
  gap: 6px;
  padding: 4px 16px 8px;
  overflow-x: auto;
  scrollbar-width: none;
}

.time-presets::-webkit-scrollbar {
  display: none;
}

.preset-btn {
  padding: 6px 14px;
  border-radius: 16px;
  font-size: 12px;
  background: var(--bg-card);
  color: var(--text-secondary);
  border: 1px solid var(--border, #eee);
  white-space: nowrap;
  cursor: pointer;
  transition: all 0.15s;
}

.preset-btn.active {
  background: var(--accent);
  color: white;
  border-color: var(--accent);
}

.tab-bar {
  display: flex;
  margin: 0 16px 12px;
  background: var(--bg-tab);
  border-radius: 10px;
  padding: 3px;
}

.tab-item {
  flex: 1;
  text-align: center;
  padding: 8px 0;
  font-size: 14px;
  font-weight: 600;
  color: var(--text-muted);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.tab-item.active {
  background: var(--bg-card);
  color: var(--accent);
  box-shadow: var(--shadow);
}

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

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.section-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-secondary);
  margin-bottom: 12px;
}

.section-header .section-title {
  margin-bottom: 0;
}

.chart-toggle-btn {
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 11px;
  background: var(--bg-input);
  color: var(--text-secondary);
  border: 1px solid var(--border, #eee);
  cursor: pointer;
  transition: all 0.2s;
}

.chart-toggle-btn.active {
  background: var(--accent);
  color: white;
  border-color: var(--accent);
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

.stats-donut-wrap {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 12px 0;
}

.donut-wrap {
  width: 120px;
  height: 120px;
  flex-shrink: 0;
}

.donut-wrap canvas {
  width: 100% !important;
  height: 100% !important;
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
  color: var(--text-secondary);
  flex: 1;
}

.legend-pct {
  font-weight: 700;
  color: var(--text-primary);
}

.balance-stats {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  margin-top: 16px;
}

.bs-item {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.bs-label {
  font-size: 11px;
  color: var(--text-muted);
}

.bs-value {
  font-size: 15px;
  font-weight: 700;
  font-variant-numeric: tabular-nums;
  color: var(--text-primary);
}

.bs-value.income {
  color: var(--success);
}

.bs-value.expense {
  color: var(--danger);
}

.stats-page {
  padding-bottom: calc(var(--nav-height) + var(--safe-bottom) + 12px);
}
</style>
