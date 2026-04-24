<template>
  <div class="page balance-trend">
    <div class="page-header">
      <h1>余额趋势</h1>
    </div>

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
      <select v-model="selectedAccountId" class="account-select">
        <option :value="0">全部账户</option>
        <option v-for="acc in accounts" :key="acc.id" :value="acc.id">{{ acc.name }}</option>
      </select>
    </div>

    <div class="chart-container card" v-if="balanceData.length">
      <v-chart :option="chartOption" autoresize style="height: 300px" />
    </div>

    <div class="empty-state" v-else-if="!loading">
      <span class="empty-icon">📊</span>
      <span class="empty-text">暂无数据</span>
    </div>

    <div class="accounts-summary" v-if="accounts.length">
      <div class="section-title">账户余额</div>
      <div class="account-list">
        <div class="account-item card" v-for="acc in accounts" :key="acc.id" @click="selectedAccountId = acc.id">
          <div class="account-info">
            <span class="account-name">{{ acc.name }}</span>
            <span class="account-type">{{ getAccountType(acc.type) }}</span>
          </div>
          <span class="account-balance" :class="{ negative: acc.balance < 0 }">
            ¥{{ formatMoney(acc.balance) }}
          </span>
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
import { LineChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, LegendComponent, DataZoomComponent } from 'echarts/components'
import { statisticsApi, accountApi, type Account, type AccountBalanceTrend } from '@/api/types'

use([CanvasRenderer, LineChart, GridComponent, TooltipComponent, LegendComponent, DataZoomComponent])

const accounts = ref<Account[]>([])
const balanceData = ref<AccountBalanceTrend[]>([])
const selectedAccountId = ref(0)
const timeRange = ref('1m')
const loading = ref(false)

const timeFilters = [
  { label: '1周', value: '1w' },
  { label: '1月', value: '1m' },
  { label: '3月', value: '3m' },
  { label: '6月', value: '6m' },
  { label: '1年', value: '1y' },
]

const accountColors = ['#6366f1', '#34d399', '#f87171', '#facc15', '#fb923c', '#a78bfa']

function formatMoney(n: number) {
  return n.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

function getAccountType(type: number) {
  const types: Record<number, string> = {
    1: '现金', 2: '银行卡', 3: '信用卡', 4: '支付宝', 5: '微信', 6: '其他'
  }
  return types[type] || '其他'
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
  }
  
  return {
    start: start.toISOString().split('T')[0],
    end: end.toISOString().split('T')[0]
  }
}

const chartOption = computed(() => {
  const series = balanceData.value.map((account, index) => ({
    name: account.account_name,
    type: 'line' as const,
    data: account.data.map(d => d.balance),
    smooth: true,
    lineStyle: { color: accountColors[index % accountColors.length], width: 2 },
    itemStyle: { color: accountColors[index % accountColors.length] },
    areaStyle: {
      color: {
        type: 'linear' as const,
        x: 0, y: 0, x2: 0, y2: 1,
        colorStops: [
          { offset: 0, color: accountColors[index % accountColors.length] + '20' },
          { offset: 1, color: accountColors[index % accountColors.length] + '00' }
        ]
      }
    }
  }))

  const dates = balanceData.value[0]?.data.map(d => d.date.slice(5)) || []

  return {
    tooltip: {
      trigger: 'axis',
      backgroundColor: getComputedStyle(document.documentElement).getPropertyValue('--chart-bg').trim() || '#1a1a24',
      borderColor: getComputedStyle(document.documentElement).getPropertyValue('--chart-border').trim() || '#2a2a3a',
      textStyle: { color: getComputedStyle(document.documentElement).getPropertyValue('--chart-text').trim() || '#e8e8ed', fontSize: 12 },
      formatter: (params: any) => {
        let html = `<div style="font-weight:600;margin-bottom:8px">${params[0].axisValue}</div>`
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
      textStyle: { color: getComputedStyle(document.documentElement).getPropertyValue('--chart-text-secondary').trim() || '#8888a0', fontSize: 11 },
      top: 0,
      right: 0,
    },
    grid: { left: 56, right: 16, top: 40, bottom: 24 },
    xAxis: {
      type: 'category',
      data: dates,
      axisLine: { lineStyle: { color: getComputedStyle(document.documentElement).getPropertyValue('--chart-axis').trim() || '#2a2a3a' } },
      axisLabel: { color: getComputedStyle(document.documentElement).getPropertyValue('--chart-text-secondary').trim() || '#8888a0', fontSize: 10, interval: Math.floor(dates.length / 6) },
    },
    yAxis: {
      type: 'value',
      splitLine: { lineStyle: { color: getComputedStyle(document.documentElement).getPropertyValue('--chart-split').trim() || '#1e1e2e' } },
      axisLabel: { 
        color: getComputedStyle(document.documentElement).getPropertyValue('--chart-text-secondary').trim() || '#8888a0', 
        fontSize: 11,
        formatter: (v: number) => v >= 1000 ? (v / 1000).toFixed(1) + 'k' : v.toFixed(0)
      },
    },
    series
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
    
    const res = await statisticsApi.balanceTrend(params)
    balanceData.value = res.data || []
  } catch (e) {
    console.error(e)
    balanceData.value = []
  } finally {
    loading.value = false
  }
}

watch([timeRange, selectedAccountId], loadBalanceData)

onMounted(async () => {
  await loadAccounts()
  await loadBalanceData()
})
</script>

<style scoped>
.filter-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  gap: 12px;
}

.time-filter {
  display: flex;
  gap: 6px;
}

.filter-btn {
  padding: 6px 12px;
  border-radius: 16px;
  font-size: 12px;
  background: var(--bg-card);
  color: var(--text-secondary);
  border: 1px solid var(--border);
}

.filter-btn.active {
  background: var(--primary);
  color: #fff;
  border-color: var(--primary);
}

.account-select {
  padding: 8px 12px;
  border-radius: 8px;
  font-size: 13px;
  background: var(--bg-card);
  color: var(--text);
  border: 1px solid var(--border);
  min-width: 100px;
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
}

.accounts-summary {
  margin-top: 8px;
}

.account-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.account-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 16px;
  cursor: pointer;
}

.account-item:active {
  transform: scale(0.98);
}

.account-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.account-name {
  font-size: 15px;
  font-weight: 500;
}

.account-type {
  font-size: 11px;
  color: var(--text-muted);
}

.account-balance {
  font-size: 18px;
  font-weight: 700;
  font-variant-numeric: tabular-nums;
}

.account-balance.negative {
  color: var(--expense);
}
</style>

