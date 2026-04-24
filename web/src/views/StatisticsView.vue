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
      <div class="chart-container" v-if="hasTrendData">
        <canvas ref="trendCanvas"></canvas>
      </div>
      <div class="chart-empty" v-else>
        <span class="empty-icon">📈</span>
        <span class="empty-text">暂无趋势数据</span>
        <span class="empty-hint">该月份还没有账单记录</span>
      </div>
    </div>

    <div class="card" style="padding: 16px">
      <div class="section-title">支出占比</div>
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
        <span class="empty-hint">该月份还没有{{ statsType === 1 ? '支出' : '收入' }}记录</span>
      </div>
    </div>

    <div class="card balance-trend-entry" @click="$router.push('/balance-trend')">
      <div class="entry-icon">📈</div>
      <div class="entry-info">
        <span class="entry-title">余额趋势</span>
        <span class="entry-desc">查看账户余额历史变化</span>
      </div>
      <span class="entry-arrow">›</span>
    </div>

    <div v-if="showMonthPicker" class="modal-overlay" @click.self="showMonthPicker = false">
      <div class="month-picker-modal">
        <div class="picker-header">
          <span class="picker-title">选择月份</span>
          <span class="picker-close" @click="showMonthPicker = false">✕</span>
        </div>
        <div class="year-list">
          <div v-for="year in yearList" :key="year" class="year-group">
            <div
              class="year-row"
              :class="{ active: expandedYear === year }"
              @click="toggleYear(year)"
            >
              <span class="year-label">{{ year }}年</span>
              <span class="year-arrow" :class="{ expanded: expandedYear === year }">›</span>
            </div>
            <transition name="slide">
              <div v-if="expandedYear === year" class="month-grid">
                <div
                  v-for="m in 12"
                  :key="m"
                  class="month-cell"
                  :class="{
                    selected: isSelected(year, m),
                    current: isCurrentMonth(year, m),
                    future: isFutureMonth(year, m),
                  }"
                  @click="selectMonth(year, m)"
                >
                  {{ m }}月
                </div>
              </div>
            </transition>
          </div>
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
const expandedYear = ref(dayjs().year())
const trendCanvas = ref(null)
const donutCanvas = ref(null)
let trendChart = null
let donutChart = null

const monthRange = computed(() => getMonthRange(currentMonth.value))
const currentMonthLabel = computed(() => currentMonth.value.format('YYYY年M月'))
const categoryStats = computed(() => statsStore.categoryStats)
const hasTrendData = computed(() => statsStore.trend && statsStore.trend.length > 0)
const hasCategoryData = computed(() => categoryStats.value && categoryStats.value.length > 0)
const totalAmount = computed(() => {
  if (statsType.value === 1) return statsStore.overview?.total_expense || 0
  return statsStore.overview?.total_income || 0
})
const dailyAvg = computed(() => {
  const days = currentMonth.value.daysInMonth()
  return totalAmount.value / days
})

const yearList = computed(() => {
  const now = dayjs()
  const years = []
  for (let y = now.year(); y >= now.year() - 5; y--) {
    years.push(y)
  }
  return years
})

function toggleYear(year) {
  expandedYear.value = expandedYear.value === year ? null : year
}

function isSelected(year, month) {
  return currentMonth.value.year() === year && currentMonth.value.month() + 1 === month
}

function isCurrentMonth(year, month) {
  const now = dayjs()
  return now.year() === year && now.month() + 1 === month
}

function isFutureMonth(year, month) {
  const now = dayjs()
  const target = dayjs(`${year}-${String(month).padStart(2, '0')}-01`)
  return target.isAfter(now, 'month')
}

function selectMonth(year, month) {
  if (isFutureMonth(year, month)) return
  currentMonth.value = dayjs(`${year}-${String(month).padStart(2, '0')}-01`)
  showMonthPicker.value = false
  fetchData()
}

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
  if (!trendCanvas.value || !hasTrendData.value) return
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
  if (!donutCanvas.value || !hasCategoryData.value) return
  if (donutChart) donutChart.destroy()

  const data = categoryStats.value
  const colors = data.map((_, i) => COLORS[i % COLORS.length])

  const ctx = donutCanvas.value.getContext('2d')
  donutChart = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: data.map(d => d.category_name),
      datasets: [{
        data: data.map(d => d.amount),
        backgroundColor: colors,
        borderWidth: 2,
        borderColor: '#fff',
        cutout: '68%',
        hoverOffset: 4,
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false }, tooltip: { enabled: false } },
    },
  })
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
  color: #666;
  flex: 1;
}

.legend-pct {
  font-weight: 700;
  color: #444;
}

.balance-trend-entry {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 16px 20px;
  cursor: pointer;
  transition: background 0.15s;
}

.balance-trend-entry:active {
  background: rgba(0, 0, 0, 0.03);
}

.entry-icon {
  font-size: 28px;
  width: 44px;
  height: 44px;
  border-radius: 12px;
  background: rgba(212, 165, 116, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
}

.entry-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.entry-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
}

.entry-desc {
  font-size: 12px;
  color: var(--text-muted);
}

.entry-arrow {
  font-size: 18px;
  color: var(--text-muted);
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: flex-end;
  justify-content: center;
  z-index: 200;
}

.month-picker-modal {
  background: var(--bg-card);
  border-radius: 20px 20px 0 0;
  padding: 20px 16px 32px;
  width: 100%;
  max-width: 480px;
  max-height: 70vh;
  overflow-y: auto;
}

.picker-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
  padding: 0 4px;
}

.picker-title {
  font-size: 17px;
  font-weight: 700;
  color: var(--text-primary);
}

.picker-close {
  font-size: 18px;
  color: var(--text-muted);
  cursor: pointer;
  padding: 4px 8px;
}

.year-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.year-group {
  border-radius: 12px;
  overflow: hidden;
}

.year-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 16px;
  cursor: pointer;
  transition: background 0.15s;
  border-radius: 12px;
}

.year-row:hover {
  background: rgba(0, 0, 0, 0.03);
}

.year-row.active {
  background: rgba(212, 165, 116, 0.08);
}

.year-label {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

.year-arrow {
  font-size: 18px;
  color: var(--text-muted);
  transition: transform 0.25s ease;
}

.year-arrow.expanded {
  transform: rotate(90deg);
}

.month-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 8px;
  padding: 4px 8px 12px;
}

.month-cell {
  text-align: center;
  padding: 10px 0;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
  cursor: pointer;
  transition: all 0.15s ease;
  background: rgba(0, 0, 0, 0.02);
}

.month-cell:hover {
  background: rgba(212, 165, 116, 0.12);
}

.month-cell.selected {
  background: var(--accent);
  color: white;
  font-weight: 700;
}

.month-cell.current:not(.selected) {
  border: 1.5px solid var(--accent);
  color: var(--accent);
  font-weight: 600;
}

.month-cell.future {
  color: var(--text-muted);
  opacity: 0.4;
  cursor: not-allowed;
}

.slide-enter-active,
.slide-leave-active {
  transition: all 0.25s ease;
  max-height: 200px;
  overflow: hidden;
}

.slide-enter-from,
.slide-leave-to {
  max-height: 0;
  opacity: 0;
  padding-top: 0;
  padding-bottom: 0;
}
</style>
