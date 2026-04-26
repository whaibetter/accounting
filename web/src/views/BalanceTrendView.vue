<template>
  <div class="page balance-trend-page">
    <div class="page-header">
      <span class="back-btn" @click="$router.back()">‹</span>
      <span class="page-title">余额趋势</span>
      <span class="export-btn" @click="handleExport">📤</span>
    </div>

    <div class="filter-section">
      <div class="filter-row">
        <div class="time-filter">
          <button
            v-for="tf in timeFilters"
            :key="tf.value"
            class="filter-btn"
            :class="{ active: timeRange === tf.value }"
            @click="timeRange = tf.value"
          >
            {{ tf.label }}
          </button>
        </div>
      </div>
      <div class="filter-row">
        <CustomSelect
          v-model="selectedAccountId"
          :options="accountFilterOptions"
          placeholder="全部账户"
          class="filter-select"
        />
        <button class="chart-toggle" :class="{ active: chartType === 'bar' }" @click="toggleChartType">
          {{ chartType === 'line' ? '📈 折线' : '📊 柱状' }}
        </button>
      </div>
    </div>

    <div class="account-list" v-if="balanceData.length">
      <div
        class="account-item"
        v-for="acc in balanceData"
        :key="acc.account_id"
        @click="selectedAccountId = acc.account_id"
        :class="{ selected: selectedAccountId === acc.account_id }"
      >
        <div class="ai-left">
          <div class="ai-dot" :style="{ background: acc.color }"></div>
          <div class="ai-info">
            <span class="ai-name">{{ acc.account_name }}</span>
            <span class="ai-type">{{ acc.account_type_name }}</span>
          </div>
        </div>
        <span class="ai-balance" :class="{ negative: acc.current_balance < 0 }">
          ¥{{ formatMoney(acc.current_balance) }}
        </span>
      </div>
    </div>

    <div class="card chart-card" v-if="balanceData.length">
      <canvas ref="mainChartCanvas"></canvas>
    </div>

    <div class="chart-empty card" v-else-if="!loading">
      <span class="empty-icon">📊</span>
      <span class="empty-text">暂无数据</span>
      <span class="empty-hint">请先添加账户和账单记录</span>
    </div>

    <div class="detail-section" v-if="selectedDetail">
      <div class="section-title">
        <span>{{ selectedDetail.account_name }} - 收支明细</span>
      </div>
      <div class="card detail-chart-card">
        <canvas ref="detailChartCanvas"></canvas>
      </div>
      <div class="detail-stats">
        <div class="stat-item card">
          <span class="stat-label">期初余额</span>
          <span class="stat-value">¥{{ formatMoney(selectedDetail.data[0]?.balance ?? 0) }}</span>
        </div>
        <div class="stat-item card">
          <span class="stat-label">期末余额</span>
          <span class="stat-value">¥{{ formatMoney(selectedDetail.data[selectedDetail.data.length - 1]?.balance ?? 0) }}</span>
        </div>
        <div class="stat-item card">
          <span class="stat-label">总收入</span>
          <span class="stat-value income">¥{{ formatMoney(totalIncome) }}</span>
        </div>
        <div class="stat-item card">
          <span class="stat-label">总支出</span>
          <span class="stat-value expense">¥{{ formatMoney(totalExpense) }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { statisticsApi, accountApi } from '@/services'
import { useThemeStore, getThemeColor } from '@/stores/theme'
import Chart from 'chart.js/auto'
import dayjs from 'dayjs'
import CustomSelect from '@/components/CustomSelect.vue'

const themeStore = useThemeStore()

const accounts = ref([])
const balanceData = ref([])
const selectedAccountId = ref(0)
const timeRange = ref('1m')
const chartType = ref('line')
const loading = ref(false)
const mainChartCanvas = ref(null)
const detailChartCanvas = ref(null)
let mainChart = null
let detailChart = null

const accountFilterOptions = computed(() => [
  { label: '全部账户', value: 0 },
  ...accounts.value.map(acc => ({ label: acc.name, value: acc.id })),
])

const timeFilters = [
  { label: '1周', value: '1w' },
  { label: '1月', value: '1m' },
  { label: '3月', value: '3m' },
  { label: '6月', value: '6m' },
  { label: '1年', value: '1y' },
  { label: '2年', value: '2y' },
]

const selectedDetail = computed(() => {
  if (selectedAccountId.value > 0) {
    return balanceData.value.find(d => d.account_id === selectedAccountId.value) || null
  }
  return balanceData.value.length === 1 ? balanceData.value[0] : null
})

const totalIncome = computed(() => {
  if (!selectedDetail.value) return 0
  return selectedDetail.value.data.reduce((sum, d) => sum + d.income, 0)
})

const totalExpense = computed(() => {
  if (!selectedDetail.value) return 0
  return selectedDetail.value.data.reduce((sum, d) => sum + d.expense, 0)
})

function formatMoney(n) {
  return Number(n).toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

function toggleChartType() {
  chartType.value = chartType.value === 'line' ? 'bar' : 'line'
  nextTick(() => {
    renderMainChart()
  })
}

function getDateRange() {
  const end = dayjs()
  let start = dayjs()
  switch (timeRange.value) {
    case '1w': start = start.subtract(7, 'day'); break
    case '1m': start = start.subtract(1, 'month'); break
    case '3m': start = start.subtract(3, 'month'); break
    case '6m': start = start.subtract(6, 'month'); break
    case '1y': start = start.subtract(1, 'year'); break
    case '2y': start = start.subtract(2, 'year'); break
  }
  return {
    start_date: start.format('YYYY-MM-DD'),
    end_date: end.format('YYYY-MM-DD'),
  }
}

function renderMainChart() {
  if (!mainChartCanvas.value || !balanceData.value.length) return
  if (mainChart) mainChart.destroy()

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

  const dates = balanceData.value[0]?.data.map(d => {
    if (timeRange.value === '1w' || timeRange.value === '1m') return d.date.slice(5)
    return d.date.slice(2)
  }) || []

  const labelInterval = Math.max(Math.floor(dates.length / 7), 0)

  mainChart = new Chart(mainChartCanvas.value, {
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
        x: {
          grid: { display: false },
          ticks: { font: { size: 10 }, color: textColor, maxTicksLimit: 8, interval: labelInterval },
        },
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

function renderDetailChart() {
  if (!detailChartCanvas.value || !selectedDetail.value) return
  if (detailChart) detailChart.destroy()

  const d = selectedDetail.value
  const dates = d.data.map(item => {
    if (timeRange.value === '1w' || timeRange.value === '1m') return item.date.slice(5)
    return item.date.slice(2)
  })
  const textColor = getThemeColor('--text-muted') || '#999'
  const gridColor = getThemeColor('--border') || '#f0f0f0'

  detailChart = new Chart(detailChartCanvas.value, {
    type: 'bar',
    data: {
      labels: dates,
      datasets: [
        {
          label: '收入',
          data: d.data.map(item => item.income),
          backgroundColor: getThemeColor('--success') + 'aa' || '#34d399aa',
          borderRadius: 3,
          barMaxWidth: 14,
        },
        {
          label: '支出',
          data: d.data.map(item => item.expense),
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

async function loadAccounts() {
  try {
    const res = await accountApi.list()
    if (res.data.code === 200) {
      accounts.value = res.data.data
    }
  } catch (e) {
    console.error(e)
  }
}

async function loadBalanceData() {
  loading.value = true
  const { start_date, end_date } = getDateRange()

  try {
    const params = { start_date, end_date }
    if (selectedAccountId.value > 0) {
      params.account_id = selectedAccountId.value
    }

    const res = await statisticsApi.balanceTrend(params)
    if (res.data.code === 200) {
      balanceData.value = res.data.data || []
    }
  } catch (e) {
    console.error(e)
    balanceData.value = []
  } finally {
    loading.value = false
  }

  nextTick(() => {
    renderMainChart()
    renderDetailChart()
  })
}

function handleExport() {
  if (!balanceData.value.length) return

  let csv = '\uFEFF日期,账户,余额,收入,支出\n'
  for (const acc of balanceData.value) {
    for (const d of acc.data) {
      csv += `${d.date},${acc.account_name},${d.balance},${d.income},${d.expense}\n`
    }
  }

  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `余额趋势_${dayjs().format('YYYYMMDD')}.csv`
  a.click()
  URL.revokeObjectURL(url)
}

watch([timeRange, selectedAccountId], loadBalanceData)

watch(() => themeStore.themeVersion, () => {
  nextTick(() => {
    renderMainChart()
    renderDetailChart()
  })
})

onMounted(async () => {
  await loadAccounts()
  await loadBalanceData()
})
</script>

<style scoped>
.back-btn {
  font-size: 22px;
  color: var(--text-primary);
  cursor: pointer;
  width: 24px;
}

.export-btn {
  font-size: 18px;
  cursor: pointer;
  padding: 4px;
}

.filter-section {
  margin-bottom: 12px;
  padding: 0 16px;
}

.filter-row {
  display: flex;
  gap: 8px;
  align-items: center;
  margin-bottom: 8px;
}

.time-filter {
  display: flex;
  gap: 6px;
  flex: 1;
  overflow-x: auto;
  scrollbar-width: none;
}

.time-filter::-webkit-scrollbar {
  display: none;
}

.filter-btn {
  padding: 6px 12px;
  border-radius: 16px;
  font-size: 12px;
  background: var(--bg-card);
  color: var(--text-secondary);
  border: 1px solid var(--border, #eee);
  white-space: nowrap;
  cursor: pointer;
  transition: all 0.15s;
}

.filter-btn.active {
  background: var(--accent);
  color: white;
  border-color: var(--accent);
}

.filter-select {
  padding: 8px 12px;
  border-radius: 8px;
  font-size: 13px;
  background: var(--bg-card);
  color: var(--text-primary);
  border: 1px solid var(--border, #eee);
  flex: 1;
  min-width: 0;
}

.chart-toggle {
  padding: 8px 12px;
  border-radius: 8px;
  font-size: 12px;
  background: var(--bg-card);
  color: var(--text-secondary);
  border: 1px solid var(--border, #eee);
  white-space: nowrap;
  cursor: pointer;
  transition: all 0.2s;
}

.chart-toggle.active {
  background: var(--accent);
  color: white;
  border-color: var(--accent);
}

.account-list {
  margin: 0 16px 12px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.account-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 14px;
  background: var(--bg-card);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: var(--shadow);
}

.account-item.selected {
  background: rgba(212, 165, 116, 0.08);
  border: 1.5px solid var(--accent);
}

.ai-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.ai-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
}

.ai-info {
  display: flex;
  flex-direction: column;
  gap: 1px;
}

.ai-name {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

.ai-type {
  font-size: 11px;
  color: var(--text-muted);
}

.ai-balance {
  font-size: 15px;
  font-weight: 700;
  font-variant-numeric: tabular-nums;
  color: var(--text-primary);
}

.ai-balance.negative {
  color: #f87171;
}

.chart-card {
  padding: 16px;
  margin: 0 16px 16px;
  height: 300px;
}

.chart-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  margin: 0 16px;
  color: var(--text-muted);
}

.chart-empty .empty-icon {
  font-size: 48px;
  margin-bottom: 12px;
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

.detail-section {
  margin: 0 16px 90px;
}

.section-title {
  font-size: 15px;
  font-weight: 600;
  margin-bottom: 12px;
  color: var(--text-primary);
}

.detail-chart-card {
  padding: 16px;
  margin-bottom: 12px;
  height: 220px;
}

.detail-stats {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.stat-item {
  padding: 12px;
}

.stat-label {
  display: block;
  font-size: 11px;
  color: var(--text-muted);
  margin-bottom: 4px;
}

.stat-value {
  font-size: 16px;
  font-weight: 700;
  font-variant-numeric: tabular-nums;
  color: var(--text-primary);
}

.stat-value.income {
  color: #34d399;
}

.stat-value.expense {
  color: #f87171;
}
</style>
