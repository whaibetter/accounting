<template>
  <div class="page stats">
    <div class="page-header">
      <h1>统计</h1>
      <button class="trend-btn" @click="$router.push('/balance-trend')">📈 余额趋势</button>
    </div>

    <div class="month-nav">
      <button class="nav-btn" @click="prevMonth">‹</button>
      <span class="month-text">{{ monthStr }}</span>
      <button class="nav-btn" @click="nextMonth">›</button>
    </div>

    <div class="overview-row" v-if="overview">
      <div class="stat-card card">
        <span class="stat-label">收入</span>
        <span class="stat-value income-text">¥{{ formatMoney(overview.total_income) }}</span>
      </div>
      <div class="stat-card card">
        <span class="stat-label">支出</span>
        <span class="stat-value expense-text">¥{{ formatMoney(overview.total_expense) }}</span>
      </div>
    </div>

    <div class="section-title" style="margin-top: 24px">支出分类</div>
    <div class="category-chart card" v-if="expenseStats.length">
      <div class="bar-list">
        <div class="bar-item" v-for="stat in expenseStats" :key="stat.category_id">
          <div class="bar-header">
            <span class="bar-name">{{ stat.category_name }}</span>
            <span class="bar-amount">¥{{ formatMoney(stat.amount) }}</span>
          </div>
          <div class="bar-track">
            <div class="bar-fill" :style="{ width: stat.percentage + '%', background: getBarColor(stat.percentage) }"></div>
          </div>
          <span class="bar-percent">{{ stat.percentage }}%</span>
        </div>
      </div>
    </div>

    <div class="section-title" style="margin-top: 24px">收支趋势</div>
    <div class="card trend-card" v-if="trendData.length">
      <v-chart :option="trendOption" autoresize style="height: 240px" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, LegendComponent } from 'echarts/components'
import { statisticsApi, type Overview, type CategoryStat, type TrendItem } from '@/api/types'

use([CanvasRenderer, LineChart, GridComponent, TooltipComponent, LegendComponent])

const overview = ref<Overview | null>(null)
const expenseStats = ref<CategoryStat[]>([])
const trendData = ref<TrendItem[]>([])
const currentYear = ref(new Date().getFullYear())
const currentMonth = ref(new Date().getMonth() + 1)

const monthStr = computed(() => `${currentYear.value}年${currentMonth.value}月`)

function formatMoney(n: number) {
  return Math.abs(n).toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

function getBarColor(pct: number) {
  const style = getComputedStyle(document.documentElement)
  if (pct > 40) return style.getPropertyValue('--bar-high').trim() || '#f87171'
  if (pct > 25) return style.getPropertyValue('--bar-medium').trim() || '#fb923c'
  if (pct > 15) return style.getPropertyValue('--bar-low').trim() || '#facc15'
  return style.getPropertyValue('--bar-default').trim() || '#6366f1'
}

function prevMonth() {
  if (currentMonth.value === 1) { currentMonth.value = 12; currentYear.value-- }
  else currentMonth.value--
}

function nextMonth() {
  if (currentMonth.value === 12) { currentMonth.value = 1; currentYear.value++ }
  else currentMonth.value++
}

const trendOption = computed(() => ({
  tooltip: {
    trigger: 'axis',
    backgroundColor: getComputedStyle(document.documentElement).getPropertyValue('--chart-bg').trim() || '#1a1a24',
    borderColor: getComputedStyle(document.documentElement).getPropertyValue('--chart-border').trim() || '#2a2a3a',
    textStyle: { color: getComputedStyle(document.documentElement).getPropertyValue('--chart-text').trim() || '#e8e8ed', fontSize: 12 },
  },
  legend: {
    data: ['收入', '支出'],
    textStyle: { color: getComputedStyle(document.documentElement).getPropertyValue('--chart-text-secondary').trim() || '#8888a0', fontSize: 11 },
    top: 0,
    right: 0,
  },
  grid: { left: 48, right: 16, top: 32, bottom: 24 },
  xAxis: {
    type: 'category',
    data: trendData.value.map((t) => t.period.slice(5)),
    axisLine: { lineStyle: { color: getComputedStyle(document.documentElement).getPropertyValue('--chart-axis').trim() || '#2a2a3a' } },
    axisLabel: { color: getComputedStyle(document.documentElement).getPropertyValue('--chart-text-secondary').trim() || '#8888a0', fontSize: 11 },
  },
  yAxis: {
    type: 'value',
    splitLine: { lineStyle: { color: getComputedStyle(document.documentElement).getPropertyValue('--chart-split').trim() || '#1e1e2e' } },
    axisLabel: { color: getComputedStyle(document.documentElement).getPropertyValue('--chart-text-secondary').trim() || '#8888a0', fontSize: 11 },
  },
  series: [
    {
      name: '收入',
      type: 'line',
      data: trendData.value.map((t) => t.income),
      smooth: true,
      lineStyle: { color: '#34d399', width: 2 },
      itemStyle: { color: '#34d399' },
      areaStyle: { color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: 'rgba(52,211,153,0.15)' }, { offset: 1, color: 'rgba(52,211,153,0)' }] } },
    },
    {
      name: '支出',
      type: 'line',
      data: trendData.value.map((t) => t.expense),
      smooth: true,
      lineStyle: { color: '#f87171', width: 2 },
      itemStyle: { color: '#f87171' },
      areaStyle: { color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: 'rgba(248,113,113,0.15)' }, { offset: 1, color: 'rgba(248,113,113,0)' }] } },
    },
  ],
}))

async function loadData() {
  const m = String(currentMonth.value).padStart(2, '0')
  const start = `${currentYear.value}-${m}-01`
  const lastDay = new Date(currentYear.value, currentMonth.value, 0).getDate()
  const end = `${currentYear.value}-${m}-${lastDay}`

  try {
    const [overviewRes, statsRes, trendRes] = await Promise.all([
      statisticsApi.overview({ start_date: start, end_date: end }),
      statisticsApi.byCategory({ start_date: start, end_date: end, type: 1 }),
      statisticsApi.trend({ start_date: start, end_date: end, granularity: 'day' }),
    ])
    overview.value = overviewRes.data
    expenseStats.value = statsRes.data || []
    trendData.value = trendRes.data || []
  } catch (e) { console.error(e) }
}

watch([currentYear, currentMonth], loadData)
onMounted(loadData)
</script>

<style scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.trend-btn {
  padding: 6px 12px;
  border-radius: 16px;
  font-size: 12px;
  background: var(--bg-card);
  color: var(--text-secondary);
  border: 1px solid var(--border);
}

.overview-row { display: flex; gap: 12px; }
.stat-card { flex: 1; display: flex; flex-direction: column; gap: 4px; }
.stat-label { font-size: 12px; color: var(--text-secondary); }
.stat-value { font-size: 20px; font-weight: 700; font-variant-numeric: tabular-nums; }
.income-text { color: var(--income); }
.expense-text { color: var(--expense); }

.month-nav { display: flex; align-items: center; justify-content: center; gap: 20px; margin-bottom: 20px; }
.nav-btn {
  width: 36px; height: 36px; border-radius: 50%; background: var(--bg-card);
  color: var(--text); font-size: 20px; display: flex; align-items: center;
  justify-content: center; border: 1px solid var(--border);
}
.nav-btn:active { transform: scale(0.9); }
.month-text { font-size: 16px; font-weight: 600; }

.bar-list { display: flex; flex-direction: column; gap: 14px; }
.bar-item { display: flex; flex-direction: column; gap: 6px; }
.bar-header { display: flex; justify-content: space-between; align-items: center; }
.bar-name { font-size: 14px; font-weight: 500; }
.bar-amount { font-size: 14px; font-weight: 600; font-variant-numeric: tabular-nums; }
.bar-track { height: 6px; background: var(--bg-input); border-radius: 3px; overflow: hidden; }
.bar-fill { height: 100%; border-radius: 3px; transition: width 0.6s cubic-bezier(0.4, 0, 0.2, 1); }
.bar-percent { font-size: 11px; color: var(--text-muted); align-self: flex-end; }

.trend-card { padding: 16px; }
</style>

