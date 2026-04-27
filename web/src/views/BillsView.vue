<template>
  <div class="page bills-page" ref="pageRef" @scroll="onScroll">
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

    <div v-if="loading && bills.length === 0" class="loading-center">
      <span class="loading-spinner"></span>
    </div>

    <div v-else-if="bills.length === 0" class="empty-state">
      <div class="icon">📋</div>
      <div class="text">暂无账单记录</div>
    </div>

    <div v-else class="bill-feed">
      <template v-for="group in groupedBills" :key="group.date">
        <div class="date-divider">
          <span class="divider-line"></span>
          <span class="divider-text">{{ group.label }}</span>
          <span class="divider-line"></span>
        </div>
        <div v-for="bill in group.bills" :key="bill.id" class="feed-item" @click="editBill(bill)">
          <div class="fi-icon" :style="{ background: getCatBgColor(bill.category_icon) }">
            {{ getCatIcon(bill.category_icon) }}
          </div>
          <div class="fi-content">
            <div class="fi-top">
              <span class="fi-name">{{ bill.remark || bill.category_name }}</span>
              <span class="fi-amt" :class="{ income: bill.type === 2, transfer: bill.type === 3 }">
                {{ bill.type === 2 ? '+' : bill.type === 3 ? '' : '-' }}¥{{ formatMoney(bill.amount) }}
              </span>
            </div>
            <div class="fi-bottom">
              <span class="fi-cat">{{ bill.category_name }}</span>
              <span class="fi-account">{{ bill.account_name }}</span>
            </div>
          </div>
        </div>
      </template>

      <div v-if="loadingMore" class="loading-more">
        <span class="loading-spinner small"></span>
        <span>加载中...</span>
      </div>
      <div v-else-if="noMore" class="no-more">— 没有更多了 —</div>
    </div>

    <MonthPicker
      :visible="showMonthPicker"
      v-model="currentMonth"
      @select="onMonthSelect"
      @close="showMonthPicker = false"
    />

    <div v-if="editingBill" class="modal-overlay" @click.self="editingBill = null">
      <div class="edit-modal">
        <div class="edit-header">
          <span class="close-btn" @click="editingBill = null">✕</span>
          <span class="edit-title">编辑账单</span>
          <span class="delete-btn" @click="handleDeleteBill">删除</span>
        </div>
        <div class="edit-body">
          <div class="edit-field">
            <label>金额</label>
            <input type="number" v-model="editForm.amount" step="0.01" class="edit-input-box" />
          </div>
          <div class="edit-field">
            <label>分类</label>
            <CustomSelect
              v-model="editForm.category_id"
              :options="categoryOptions"
              placeholder="选择分类"
              class="edit-select"
            />
          </div>
          <div class="edit-field">
            <label>账户</label>
            <CustomSelect
              v-model="editForm.account_id"
              :options="accountOptions"
              placeholder="选择账户"
              class="edit-select"
            />
          </div>
          <div class="edit-field">
            <label>备注</label>
            <input type="text" v-model="editForm.remark" placeholder="添加备注" class="edit-input-box" />
          </div>
          <div class="edit-field">
            <label>日期</label>
            <input type="date" v-model="editForm.bill_date" class="edit-input-box" />
          </div>
          <button class="btn-primary save-btn" @click="saveBill">保存</button>
        </div>
      </div>
    </div>

    <ConfirmDialog
      ref="confirmDialog"
      icon="🗑️"
      title="确定要删除此账单吗？"
      description="此操作不可撤销，删除后账单数据将永久丢失。"
      confirmText="确认删除"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { useBillStore, useCategoryStore, useAccountStore, useStatisticsStore } from '@/stores/data'
import { formatMoney, formatDateCN, getWeekday, getMonthRange, getCategoryIcon, getAccountIcon } from '@/utils/format'
import dayjs from 'dayjs'
import MonthPicker from '@/components/MonthPicker.vue'
import ConfirmDialog from '@/components/ConfirmDialog.vue'
import CustomSelect from '@/components/CustomSelect.vue'

const billStore = useBillStore()
const categoryStore = useCategoryStore()
const accountStore = useAccountStore()
const statsStore = useStatisticsStore()
const confirmDialog = ref(null)

const currentMonth = ref(dayjs())
const showMonthPicker = ref(false)
const editingBill = ref(null)
const editForm = ref({ amount: 0, remark: '', bill_date: '', category_id: null, account_id: null })
const pageRef = ref(null)
const loadingMore = ref(false)

const categoryOptions = computed(() =>
  categoryStore.flatCategories().map(cat => ({
    label: `${getCategoryIcon(cat.icon)} ${cat.name}`,
    value: cat.id,
  }))
)

const accountOptions = computed(() =>
  accountStore.accounts.filter(a => a.status === 1).map(acc => ({
    label: `${getAccountIcon(acc.icon)} ${acc.name}`,
    value: acc.id,
  }))
)

const bills = computed(() => billStore.bills)
const loading = computed(() => billStore.loading)
const hasMore = computed(() => bills.value.length < billStore.total)
const noMore = computed(() => !loading.value && !loadingMore.value && bills.value.length > 0 && !hasMore.value)

const monthRange = computed(() => getMonthRange(currentMonth.value))
const currentMonthLabel = computed(() => currentMonth.value.format('YYYY年M月'))
const monthExpense = computed(() => statsStore.overview?.total_expense || 0)
const monthIncome = computed(() => statsStore.overview?.total_income || 0)

const groupedBills = computed(() => {
  const groups = {}
  for (const bill of bills.value) {
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

function getCatIcon(icon) {
  return getCategoryIcon(icon)
}

async function fetchBills() {
  const range = monthRange.value
  await Promise.all([
    billStore.fetchBills({ ...range, page: 1 }),
    statsStore.fetchOverview(range),
  ])
  if (pageRef.value) {
    pageRef.value.scrollTop = 0
  }
}

async function loadMore() {
  if (loadingMore.value || !hasMore.value) return
  loadingMore.value = true
  try {
    const range = monthRange.value
    await billStore.fetchBills({
      ...range,
      page: billStore.currentPage + 1,
      append: true,
    })
  } finally {
    loadingMore.value = false
  }
}

function onScroll() {
  if (!pageRef.value) return
  const { scrollTop, scrollHeight, clientHeight } = pageRef.value
  if (scrollHeight - scrollTop - clientHeight < 100 && hasMore.value && !loadingMore.value) {
    loadMore()
  }
}

function onMonthSelect() {
  fetchBills()
}

function editBill(bill) {
  editingBill.value = bill
  editForm.value = {
    amount: bill.amount,
    remark: bill.remark,
    bill_date: bill.bill_date,
    category_id: bill.category_id,
    account_id: bill.account_id,
  }
  categoryStore.fetchCategories()
  accountStore.fetchAccounts()
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

async function handleDeleteBill() {
  if (!editingBill.value) return
  const confirmed = await confirmDialog.value.show()
  if (!confirmed) return
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
.bills-page {
  height: 100%;
  overflow-y: auto;
  -webkit-overflow-scrolling: touch;
  overscroll-behavior-y: contain;
}

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
  color: var(--text-muted);
  margin-bottom: 4px;
}

.ov-val {
  font-size: 18px;
  font-weight: 800;
  color: var(--text-primary);
}

.bill-feed {
  padding: 0 16px 90px;
}

.date-divider {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 0 8px;
}

.divider-line {
  flex: 1;
  height: 0.5px;
  background: var(--border);
}

.divider-text {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-muted);
  white-space: nowrap;
}

.feed-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 0;
  border-bottom: 0.5px solid var(--border);
  cursor: pointer;
  transition: background 0.15s;
}

.feed-item:active {
  background: var(--bg-input);
}

.feed-item:last-child {
  border-bottom: none;
}

.fi-icon {
  width: 42px;
  height: 42px;
  border-radius: 13px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  flex-shrink: 0;
}

.fi-content {
  flex: 1;
  min-width: 0;
}

.fi-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.fi-name {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.fi-amt {
  font-size: 15px;
  font-weight: 700;
  color: var(--text-primary);
  flex-shrink: 0;
  font-variant-numeric: tabular-nums;
}

.fi-amt.income {
  color: var(--success);
}

.fi-amt.transfer {
  color: #7b9bd4;
}

.fi-bottom {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 3px;
}

.fi-cat {
  font-size: 11px;
  color: var(--text-muted);
}

.fi-account {
  font-size: 11px;
  color: var(--text-light);
}

.loading-more {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 16px;
  color: var(--text-muted);
  font-size: 13px;
}

.no-more {
  text-align: center;
  padding: 20px;
  color: var(--text-muted);
  font-size: 12px;
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

.edit-modal {
  background: var(--bg-card);
  border-radius: 20px;
  padding: 24px;
  width: 100%;
  max-width: 360px;
  max-height: 85vh;
  overflow-y: auto;
  -webkit-overflow-scrolling: touch;
}

.edit-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}

.edit-body {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.close-btn {
  font-size: 18px;
  color: var(--text-muted);
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

.edit-field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.edit-field label {
  font-size: 13px;
  color: var(--text-secondary);
  font-weight: 600;
}

.edit-input-box {
  padding: 10px 14px;
  border: 1.5px solid var(--border);
  border-radius: 10px;
  font-size: 14px;
  color: var(--text-primary);
  background: var(--bg-input);
  outline: none;
  transition: border-color 0.2s;
}

.edit-input-box:focus {
  border-color: var(--accent);
}

.edit-select {
  width: 100%;
}

.save-btn {
  width: 100%;
  margin-top: 20px;
}
</style>
