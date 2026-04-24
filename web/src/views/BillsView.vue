<template>
  <div class="page bills-page">
    <div class="page-header">
      <span class="page-title">账单</span>
      <div class="month-picker" @click="showMonthPicker = true">
        {{ currentMonthLabel }} ▾
      </div>
    </div>

    <div class="overview-cards">
      <div class="ov-card">
        <div class="ov-label">支出</div>
        <div class="ov-val" style="color: var(--accent)">¥ {{ formatMoney(monthExpense) }}</div>
      </div>
      <div class="ov-card">
        <div class="ov-label">收入</div>
        <div class="ov-val" style="color: var(--success)">¥ {{ formatMoney(monthIncome) }}</div>
      </div>
    </div>

    <div v-if="loading" class="loading-center">
      <span class="loading-spinner"></span>
    </div>

    <div v-else-if="groupedBills.length === 0" class="empty-state">
      <div class="icon">📋</div>
      <div class="text">暂无账单记录</div>
    </div>

    <div v-else>
      <div v-for="group in groupedBills" :key="group.date" class="bill-group">
        <div class="group-date">{{ group.label }}</div>
        <div v-for="bill in group.bills" :key="bill.id" class="bill-item" @click="editBill(bill)">
          <div class="bii-icon" :style="{ background: getCatBgColor(bill.category_icon) }">
            {{ bill.category_icon || '📝' }}
          </div>
          <div class="bii-info">
            <div class="bii-name">{{ bill.remark || bill.category_name }}</div>
            <div class="bii-cat">{{ bill.category_name }}</div>
          </div>
          <div class="bii-amt" :class="{ income: bill.type === 2, transfer: bill.type === 3 }">
            {{ bill.type === 2 ? '+' : '-' }}¥ {{ formatMoney(bill.amount) }}
          </div>
        </div>
      </div>

      <div v-if="hasMore" class="load-more" @click="loadMore">加载更多</div>
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

    <div v-if="editingBill" class="modal-overlay" @click.self="editingBill = null">
      <div class="edit-modal">
        <div class="edit-header">
          <span class="close-btn" @click="editingBill = null">✕</span>
          <span class="edit-title">编辑账单</span>
          <span class="delete-btn" @click="deleteBill">删除</span>
        </div>
        <div class="edit-body">
          <div class="edit-row">
            <label>金额</label>
            <input type="number" v-model="editForm.amount" step="0.01" class="edit-input" />
          </div>
          <div class="edit-row">
            <label>备注</label>
            <input type="text" v-model="editForm.remark" class="edit-input" />
          </div>
          <div class="edit-row">
            <label>日期</label>
            <input type="date" v-model="editForm.bill_date" class="edit-input" />
          </div>
          <button class="btn-primary save-btn" @click="saveBill">保存</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useBillStore, useStatisticsStore } from '@/stores/data'
import { formatMoney, formatDateCN, getWeekday, getMonthRange } from '@/utils/format'
import dayjs from 'dayjs'

const billStore = useBillStore()
const statsStore = useStatisticsStore()

const currentMonth = ref(dayjs())
const showMonthPicker = ref(false)
const pickerYear = ref(dayjs().year())
const pickerMonth = ref(dayjs().month() + 1)
const editingBill = ref(null)
const editForm = ref({ amount: 0, remark: '', bill_date: '' })

const loading = computed(() => billStore.loading)
const hasMore = computed(() => billStore.bills.length < billStore.total)

const monthRange = computed(() => getMonthRange(currentMonth.value))
const currentMonthLabel = computed(() => currentMonth.value.format('YYYY年M月'))
const monthExpense = computed(() => statsStore.overview?.total_expense || 0)
const monthIncome = computed(() => statsStore.overview?.total_income || 0)

const groupedBills = computed(() => {
  const groups = {}
  for (const bill of billStore.bills) {
    const date = bill.bill_date
    if (!groups[date]) {
      groups[date] = {
        date,
        label: `${formatDateCN(date)} ${getWeekday(date)}`,
        bills: [],
      }
    }
    groups[date].bills.push(bill)
  }
  return Object.values(groups).sort((a, b) => b.date.localeCompare(a.date))
})

const catBgColors = ['#fef6ee', '#fef0e6', '#eef6fc', '#fceef6', '#f5f0ee', '#eff6ee', '#f0f0f4', '#f6f0ee']

function getCatBgColor(icon) {
  const idx = (icon || '').charCodeAt(0) % catBgColors.length
  return catBgColors[idx]
}

async function fetchBills() {
  const range = monthRange.value
  await Promise.all([
    billStore.fetchBills({ ...range, page: 1 }),
    statsStore.fetchOverview(range),
  ])
}

function loadMore() {
  billStore.fetchBills({ ...monthRange.value, page: billStore.currentPage + 1 })
}

function prevMonth() {
  if (pickerMonth.value === 1) {
    pickerMonth.value = 12
    pickerYear.value--
  } else {
    pickerMonth.value--
  }
}

function nextMonth() {
  if (pickerMonth.value === 12) {
    pickerMonth.value = 1
    pickerYear.value++
  } else {
    pickerMonth.value++
  }
}

function confirmMonth() {
  currentMonth.value = dayjs(`${pickerYear.value}-${String(pickerMonth.value).padStart(2, '0')}-01`)
  showMonthPicker.value = false
  fetchBills()
}

function editBill(bill) {
  editingBill.value = bill
  editForm.value = {
    amount: bill.amount,
    remark: bill.remark,
    bill_date: bill.bill_date,
  }
}

async function saveBill() {
  if (!editingBill.value) return
  try {
    await billStore.updateBill(editingBill.value.id, editForm.value)
    editingBill.value = null
    fetchBills()
  } catch (e) {
    alert(e.response?.data?.detail || '保存失败')
  }
}

async function deleteBill() {
  if (!editingBill.value) return
  if (!confirm('确定删除此账单？')) return
  try {
    await billStore.deleteBill(editingBill.value.id)
    editingBill.value = null
    fetchBills()
  } catch (e) {
    alert(e.response?.data?.detail || '删除失败')
  }
}

watch(currentMonth, fetchBills)

onMounted(fetchBills)
</script>

<style scoped>
.overview-cards {
  display: flex;
  gap: 10px;
  margin: 0 16px 12px;
}

.ov-card {
  flex: 1;
  background: var(--bg-card);
  border-radius: 14px;
  padding: 14px;
  box-shadow: var(--shadow);
}

.ov-label {
  font-size: 11px;
  color: #aaa;
  margin-bottom: 4px;
}

.ov-val {
  font-size: 18px;
  font-weight: 800;
  color: var(--text-primary);
}

.bill-group {
  padding: 8px 16px;
}

.group-date {
  font-size: 13px;
  font-weight: 700;
  color: #888;
  margin-bottom: 8px;
}

.bill-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 0;
  border-bottom: 0.5px solid #f0ece5;
  cursor: pointer;
  transition: background 0.15s;
}

.bill-item:active {
  background: rgba(0, 0, 0, 0.02);
}

.bii-icon {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  flex-shrink: 0;
}

.bii-info {
  flex: 1;
  min-width: 0;
}

.bii-name {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.bii-cat {
  font-size: 11px;
  color: #bbb;
  margin-top: 1px;
}

.bii-amt {
  font-size: 15px;
  font-weight: 700;
  color: var(--text-primary);
  flex-shrink: 0;
}

.bii-amt.income {
  color: var(--success);
}

.bii-amt.transfer {
  color: #7b9bd4;
}

.load-more {
  text-align: center;
  padding: 16px;
  color: var(--text-light);
  font-size: 13px;
  cursor: pointer;
}

.loading-center {
  display: flex;
  justify-content: center;
  padding: 40px;
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

.month-picker-modal,
.edit-modal {
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

.edit-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}

.close-btn {
  font-size: 18px;
  color: #bbb;
  cursor: pointer;
}

.edit-title {
  font-size: 17px;
  font-weight: 700;
}

.delete-btn {
  font-size: 14px;
  color: var(--danger);
  cursor: pointer;
}

.edit-row {
  display: flex;
  align-items: center;
  padding: 12px 0;
  border-bottom: 0.5px solid #f0ece5;
}

.edit-row label {
  width: 60px;
  font-size: 14px;
  color: #777;
  flex-shrink: 0;
}

.edit-input {
  flex: 1;
  border: none;
  font-size: 14px;
  color: var(--text-primary);
  background: transparent;
}

.save-btn {
  width: 100%;
  margin-top: 20px;
}
</style>
