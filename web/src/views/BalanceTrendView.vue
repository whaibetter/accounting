<template>
  <div class="page balance-trend">
    <div class="page-header">
      <h1>余额趋势</h1>
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
        <select v-model="selectedAccountType" class="filter-select">
          <option :value="0">全部类型</option>
          <option v-for="at in accountTypes" :key="at.value" :value="at.value">{{ at.label }}</option>
        </select>
        <select v-model="selectedAccountId" class="filter-select">
          <option :value="0">全部账户</option>
          <option v-for="acc in filteredAccounts" :key="acc.id" :value="acc.id">{{ acc.name }}</option>
        </select>
        <button class="chart-toggle" @click="chartType = chartType === 'line' ? 'bar' : 'line'">
          {{ chartType === 'line' ? '📈 折线' : '📊 柱状' }}
        </button>
      </div>
    </div>

    <div class="summary-row" v-if="balanceData.length">
      <div class="summary-card card" v-for="acc in balanceData" :key="acc.account_id"
           @click="selectedAccountId = acc.account_id"
           :class="{ selected: selectedAccountId === acc.account_id }">
        <div class="summary-dot" :style="{ background: acc.color }"></div>
        <div class="summary-info">
          <span class="summary-name">{{ acc.account_name }}</span>
          <span class="summary-type">{{ acc.account_type_name }}</span>
        </div>
        <span class="summary-balance" :class="{ negative: acc.current_balance < 0 }">
          ¥{{ formatMoney(acc.current_balance) }}
        </span>
      </div>
    </div>

    <div class="chart-container card" v-if="balanceData.length">
      <v-chart :option="chartOption" autoresize style="height: 320px" />
    </div>

    <div class="empty-state" v-else-if="!loading">
      <span class="empty-icon">📊</span>
      <span class="empty-text">暂无数据</span>
      <span class="empty-hint">请先添加账户和账单记录</span>
    </div>

    <div class="detail-section" v-if="selectedDetail">
      <div class="section-title">
        <span>{{ selectedDetail.account_name }} - 收支明细</span>
      </div>
      <div class="detail-chart card">
        <v-chart :option="detailChartOption" autoresize style="height: 220px" />
      </div>
      <div class="detail-stats">
        <div class="stat-item">
          <span class="stat-label">期初余额</span>
          <span class="stat-value">¥{{ formatMoney(selectedDetail.data[0]?.balance ?? 0) }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">期末余额</span>
          <span class="stat-value">¥{{ formatMoney(selectedDetail.data[selectedDetail.data.length - 1]?.balance ?? 0) }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">总收入</span>
          <span class="stat-value income">¥{{ formatMoney(totalIncome) }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">总支出</span>
          <span class="stat-value expense">¥{{ formatMoney(totalExpense) }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart, BarChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, LegendComponent, DataZoomComponent } from 'echarts/components'
import { statisticsApi, accountApi, type Account, type AccountBalanceTrend } from '@/api/types'

use([CanvasRenderer, LineChart, BarChart, GridComponent, TooltipComponent, LegendComponent, DataZoomComponent])

const accounts = ref<Account[]>([])
const balanceData = ref<AccountBalanceTrend[]>([])
const selectedAccountId = ref(0)
const selectedAccountType = ref(0)
const timeRange = ref('1m')
const chartType = ref<'line' | 'bar'>('line')
const loading = ref(false)

const timeFilters = [
  { label: '1周', value: '1w' },
  { label: '1月', value: '1m' },
  { label: '3月', value: '3m' },
  { label: '6月', value: '6m' },
  { label: '1年', value: '1y' },
  { label: '2年', value: '2y' },
]

const accountTypes = [
  { label: '现金', value: 1 },
  { label: '银行卡', value: 2 },
  { label: '信用卡', value: 3 },
  { label: '支付宝', value: 4 },
  { label: '微信', value: 5 },
  { label: '其他', value: 6 },
]

const filteredAccounts = computed(() => {
  if (selectedAccountType.value === 0) return accounts.value
  return accounts.value.filter(a => a.type === selectedAccountType.value)
})

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

function formatMoney(n: number) {
  return n.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

function getDateRange() {
  const end = new Date()
  let start = new Date()

  switch (timeRange.value) {
    case '1w': start.setDate(start.getDate() - 7); break
    case '1m': start.setMonth(start.getMonth() - 1); break
    case '3m': start.setMonth(start.getMonth() - 3); break
    case '6m': start.setMonth(start.getMonth() - 6); break
    case '1y': start.setFullYear(start.getFullYear() - 1); break
    case '2y': start.setFullYear(start.getFullYear() - 2); break
  }

  return {
    start: start.toISOString().split('T')[0],
    end: end.toISOString().split('T')[0]
  }
}

function getChartColors() {
  const style = getComputedStyle(document.documentElement)
  return {
    bg: style.getPropertyValue('--chart-bg').trim() || '#1a1a24',
    border: style.getPropertyValue('--chart-border').trim() || '#2a2a3a',
    text: style.getPropertyValue('--chart-text').trim() || '#e8e8ed',
    textSec: style.getPropertyValue('--chart-text-secondary').trim() || '#8888a0',
    axis: style.getPropertyValue('--chart-axis').trim() || '#2a2a3a',
    split: style.getPropertyValue('--chart-split').trim() || '#1e1e2e',
  }
}

const chartOption = computed(() => {
  const c = getChartColors()
  const isLine = chartType.value === 'line'

  const series = balanceData.value.map((account) => {
    const base: any = {
      name: account.account_name,
      type: isLine ? 'line' : 'bar',
      data: account.data.map(d => d.balance),
      smooth: isLine,
    }

    if (isLine) {
      base.lineStyle = { color: account.color, width: 2 }
      base.itemStyle = { color: account.color }
      base.areaStyle = {
        color: {
          type: 'linear',
          x: 0, y: 0, x2: 0, y2: 1,
          colorStops: [
            { offset: 0, color: account.color + '20' },
            { offset: 1, color: account.color + '00' }
          ]
        }
      }
      base.showSymbol = account.data.length < 60
    } else {
      base.itemStyle = { color: account.color + 'cc', borderRadius: [2, 2, 0, 0] }
      base.barMaxWidth = 20
    }

    return base
  })

  const dates = balanceData.value[0]?.data.map(d => {
    if (timeRange.value === '1w' || timeRange.value === '1m') return d.date.slice(5)
    return d.date.slice(2)
  }) || []

  const labelInterval = Math.max(Math.floor(dates.length / 7), 0)

  return {
    tooltip: {
      trigger: 'axis',
      backgroundColor: c.bg,
      borderColor: c.border,
      textStyle: { color: c.text, fontSize: 12 },
      formatter: (params: any) => {
        const dateStr = balanceData.value[0]?.data[params[0].dataIndex]?.date || params[0].axisValue
        let html = `<div style="font-weight:600;margin-bottom:8px">${dateStr}</div>`
        params.forEach((p: any) => {
          html += `<div style="display:flex;justify-content:space-between;gap:20px">
            <span>${p.marker} ${p.seriesName}</span>
            <span style="font-weight:600">¥${formatMoney(p.value)}</span>
          </div>`
        })
        return html
      }
    },
    legend: {
      data: balanceData.value.map(a => a.account_name),
      textStyle: { color: c.textSec, fontSize: 11 },
      top: 0,
      right: 0,
    },
    grid: { left: 56, right: 16, top: 40, bottom: 24 },
    xAxis: {
      type: 'category',
      data: dates,
      axisLine: { lineStyle: { color: c.axis } },
      axisLabel: { color: c.textSec, fontSize: 10, interval: labelInterval },
    },
    yAxis: {
      type: 'value',
      splitLine: { lineStyle: { color: c.split } },
      axisLabel: {
        color: c.textSec,
        fontSize: 11,
        formatter: (v: number) => {
          if (Math.abs(v) >= 10000) return (v / 10000).toFixed(1) + 'w'
          if (Math.abs(v) >= 1000) return (v / 1000).toFixed(1) + 'k'
          return v.toFixed(0)
        }
      },
    },
    dataZoom: dates.length > 30 ? [{
      type: 'inside',
      start: Math.max(0, 100 - (30 / dates.length) * 100),
      end: 100,
    }] : [],
    series
  }
})

const detailChartOption = computed(() => {
  if (!selectedDetail.value) return {}
  const c = getChartColors()
  const d = selectedDetail.value
  const dates = d.data.map(item => {
    if (timeRange.value === '1w' || timeRange.value === '1m') return item.date.slice(5)
    return item.date.slice(2)
  })
  const labelInterval = Math.max(Math.floor(dates.length / 7), 0)

  return {
    tooltip: {
      trigger: 'axis',
      backgroundColor: c.bg,
      borderColor: c.border,
      textStyle: { color: c.text, fontSize: 12 },
      formatter: (params: any) => {
        const dateStr = d.data[params[0].dataIndex]?.date || params[0].axisValue
        let html = `<div style="font-weight:600;margin-bottom:8px">${dateStr}</div>`
        params.forEach((p: any) => {
          html += `<div style="display:flex;justify-content:space-between;gap:20px">
            <span>${p.marker} ${p.seriesName}</span>
            <span style="font-weight:600">¥${formatMoney(p.value)}</span>
          </div>`
        })
        return html
      }
    },
    legend: {
      data: ['收入', '支出'],
      textStyle: { color: c.textSec, fontSize: 11 },
      top: 0,
      right: 0,
    },
    grid: { left: 48, right: 16, top: 36, bottom: 20 },
    xAxis: {
      type: 'category',
      data: dates,
      axisLine: { lineStyle: { color: c.axis } },
      axisLabel: { color: c.textSec, fontSize: 10, interval: labelInterval },
    },
    yAxis: {
      type: 'value',
      splitLine: { lineStyle: { color: c.split } },
      axisLabel: {
        color: c.textSec,
        fontSize: 11,
        formatter: (v: number) => {
          if (Math.abs(v) >= 10000) return (v / 10000).toFixed(1) + 'w'
          if (Math.abs(v) >= 1000) return (v / 1000).toFixed(1) + 'k'
          return v.toFixed(0)
        }
      },
    },
    series: [
      {
        name: '收入',
        type: 'bar',
        data: d.data.map(item => item.income),
        itemStyle: { color: '#34d399cc', borderRadius: [2, 2, 0, 0] },
        barMaxWidth: 16,
      },
      {
        name: '支出',
        type: 'bar',
        data: d.data.map(item => item.expense),
        itemStyle: { color: '#f87171cc', borderRadius: [2, 2, 0, 0] },
        barMaxWidth: 16,
      }
    ]
  }
})

async function loadAccounts() {
  try {
    const res = await accountApi.list()
    accounts.value = res.data || []
  } catch (e) {
    console.error(e)
  }
}

async function loadBalanceData() {
  loading.value = true
  const { start, end } = getDateRange()

  try {
    const params: any = { start_date: start, end_date: end }
    if (selectedAccountId.value > 0) {
      params.account_id = selectedAccountId.value
    }
    if (selectedAccountType.value > 0) {
      params.account_type = selectedAccountType.value
    }

    const res = await statisticsApi.balanceTrend(params)
    balanceData.value = res.data || []
  } catch (e) {
    console.error(e)
    balanceData.value = []
  } finally {
    loading.value = false
  }
}

watch([timeRange, selectedAccountId, selectedAccountType], loadBalanceData)

onMounted(async () => {
  await loadAccounts()
  await loadBalanceData()
})
</script>

<style scoped>
.filter-section {
  margin-bottom: 16px;
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
}

.filter-btn {
  padding: 6px 12px;
  border-radius: 16px;
  font-size: 12px;
  background: var(--bg-card);
  color: var(--text-secondary);
  border: 1px solid var(--border);
  white-space: nowrap;
}

.filter-btn.active {
  background: var(--primary);
  color: #fff;
  border-color: var(--primary);
}

.filter-select {
  padding: 8px 12px;
  border-radius: 8px;
  font-size: 13px;
  background: var(--bg-card);
  color: var(--text);
  border: 1px solid var(--border);
  flex: 1;
  min-width: 0;
}

.chart-toggle {
  padding: 8px 12px;
  border-radius: 8px;
  font-size: 12px;
  background: var(--bg-card);
  color: var(--text-secondary);
  border: 1px solid var(--border);
  white-space: nowrap;
}

.summary-row {
  display: flex;
  gap: 8px;
  overflow-x: auto;
  margin-bottom: 16px;
  padding-bottom: 4px;
}

.summary-card {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 14px;
  min-width: fit-content;
  cursor: pointer;
  transition: all 0.2s;
}

.summary-card.selected {
  border-color: var(--primary);
  background: var(--primary-bg, rgba(99, 102, 241, 0.1));
}

.summary-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.summary-info {
  display: flex;
  flex-direction: column;
  gap: 1px;
}

.summary-name {
  font-size: 13px;
  font-weight: 500;
}

.summary-type {
  font-size: 10px;
  color: var(--text-muted);
}

.summary-balance {
  font-size: 14px;
  font-weight: 700;
  font-variant-numeric: tabular-nums;
  margin-left: 8px;
}

.summary-balance.negative {
  color: var(--expense);
}

.chart-container {
  padding: 16px;
  margin-bottom: 20px;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: var(--text-muted);
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 12px;
}

.empty-text {
  font-size: 14px;
  margin-bottom: 4px;
}

.empty-hint {
  font-size: 12px;
  color: var(--text-muted);
}

.detail-section {
  margin-top: 8px;
}

.section-title {
  font-size: 15px;
  font-weight: 600;
  margin-bottom: 12px;
}

.detail-chart {
  padding: 16px;
  margin-bottom: 12px;
}

.detail-stats {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 12px;
  background: var(--bg-card);
  border-radius: 12px;
  border: 1px solid var(--border);
}

.stat-label {
  font-size: 11px;
  color: var(--text-muted);
}

.stat-value {
  font-size: 16px;
  font-weight: 700;
  font-variant-numeric: tabular-nums;
}

.stat-value.income {
  color: var(--income);
}

.stat-value.expense {
  color: var(--expense);
}
</style>
