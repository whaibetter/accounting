<template>
  <div class="page bills">
    <div class="page-header">
      <h1>账单</h1>
      <div class="filter-tabs">
        <button
          v-for="f in filters"
          :key="f.value"
          class="filter-btn"
          :class="{ active: currentFilter === f.value }"
          @click="currentFilter = f.value"
        >{{ f.label }}</button>
      </div>
    </div>

    <div class="month-nav">
      <button class="nav-btn" @click="prevMonth">‹</button>
      <span class="month-text">{{ monthStr }}</span>
      <button class="nav-btn" @click="nextMonth">›</button>
    </div>

    <div class="bill-list" v-if="bills.length">
      <div
        class="bill-item card"
        v-for="bill in bills"
        :key="bill.id"
        @click="editBill(bill)"
      >
        <div class="bill-left">
          <span class="bill-icon">{{ getCategoryIcon(bill.category_id) }}</span>
          <div class="bill-info">
            <span class="bill-category">{{ bill.category_name }}</span>
            <span class="bill-meta">
              {{ bill.bill_date.slice(5) }}
              {{ bill.account_name }}
              <template v-if="bill.remark"> · {{ bill.remark }}</template>
            </span>
          </div>
        </div>
        <div class="bill-right">
          <span class="bill-amount" :class="bill.type === 2 ? 'income-text' : 'expense-text'">
            {{ bill.type === 2 ? '+' : '-' }}¥{{ formatMoney(bill.amount) }}
          </span>
          <div class="bill-tags" v-if="bill.tags?.length">
            <span class="mini-tag" v-for="t in bill.tags" :key="t.id" :style="{ background: t.color + '22', color: t.color }">{{ t.name }}</span>
          </div>
        </div>
      </div>
    </div>
    <div class="empty-state" v-else>
      <div class="icon">📭</div>
      <p>本月暂无账单</p>
    </div>

    <Teleport to="body">
      <div class="modal-overlay" v-if="showEdit" @click.self="showEdit = false">
        <div class="modal-content card scale-in">
          <h3>编辑账单</h3>
          <div class="edit-form">
            <div class="form-group">
              <label>金额</label>
              <input type="number" v-model="editForm.amount" step="0.01" />
            </div>
            <div class="form-group">
              <label>备注</label>
              <input type="text" v-model="editForm.remark" />
            </div>
            <div class="form-actions">
              <button class="btn-delete" @click="deleteBill">删除</button>
              <button class="btn-primary" @click="saveBill">保存</button>
            </div>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, computed } from 'vue'
import { billApi, type Bill } from '@/api/types'
import { useDataStore } from '@/stores/data'

const store = useDataStore()
const bills = ref<Bill[]>([])
const currentYear = ref(new Date().getFullYear())
const currentMonth = ref(new Date().getMonth() + 1)
const currentFilter = ref(0)
const showEdit = ref(false)
const editForm = ref({ id: 0, amount: 0, remark: '' })

const filters = [
  { label: '全部', value: 0 },
  { label: '支出', value: 1 },
  { label: '收入', value: 2 },
]

const monthStr = computed(() => `${currentYear.value}年${currentMonth.value}月`)

function formatMoney(n: number) {
  return Math.abs(n).toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

const iconMap: Record<string, string> = {
  '1': '🍜', '2': '🚌', '3': '🛒', '4': '🏠', '5': '🎮',
  '6': '🏥', '7': '📚', '8': '📱', '9': '🎁', '10': '📌',
  '46': '💰', '47': '💼', '48': '📈', '49': '🧧', '50': '↩️', '51': '📌',
}

function getCategoryIcon(id: number) {
  const parentId = String(Math.floor(id / 10) * 10)
  return iconMap[String(id)] || iconMap[parentId] || '📌'
}

function prevMonth() {
  if (currentMonth.value === 1) { currentMonth.value = 12; currentYear.value-- }
  else currentMonth.value--
}

function nextMonth() {
  if (currentMonth.value === 12) { currentMonth.value = 1; currentYear.value++ }
  else currentMonth.value++
}

async function loadBills() {
  const m = String(currentMonth.value).padStart(2, '0')
  const start = `${currentYear.value}-${m}-01`
  const lastDay = new Date(currentYear.value, currentMonth.value, 0).getDate()
  const end = `${currentYear.value}-${m}-${lastDay}`
  const params: any = { page: 1, size: 100, start_date: start, end_date: end }
  if (currentFilter.value) params.type = currentFilter.value
  try {
    const res = await billApi.list(params)
    bills.value = res.data?.items || []
  } catch (e) { console.error(e) }
}

function editBill(bill: Bill) {
  editForm.value = { id: bill.id, amount: bill.amount, remark: bill.remark }
  showEdit.value = true
}

async function saveBill() {
  try {
    await billApi.update(editForm.value.id, {
      amount: editForm.value.amount,
      remark: editForm.value.remark,
    })
    showEdit.value = false
    await loadBills()
    await store.refreshAccounts()
  } catch (e) { console.error(e) }
}

async function deleteBill() {
  try {
    await billApi.delete(editForm.value.id)
    showEdit.value = false
    await loadBills()
    await store.refreshAccounts()
  } catch (e) { console.error(e) }
}

watch([currentYear, currentMonth, currentFilter], loadBills)
onMounted(() => { store.loadAll(); loadBills() })
</script>

<style scoped>
.filter-tabs { display: flex; gap: 6px; }
.filter-btn {
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 13px;
  background: var(--bg-card);
  color: var(--text-secondary);
  border: 1px solid var(--border);
}
.filter-btn.active {
  background: var(--primary-bg);
  color: var(--primary-light);
  border-color: var(--primary);
}

.month-nav {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 20px;
  margin-bottom: 20px;
}
.nav-btn {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: var(--bg-card);
  color: var(--text);
  font-size: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid var(--border);
}
.nav-btn:active { transform: scale(0.9); }
.month-text { font-size: 16px; font-weight: 600; }

.bill-list { display: flex; flex-direction: column; gap: 8px; }
.bill-item { display: flex; align-items: center; justify-content: space-between; padding: 14px 16px; cursor: pointer; }
.bill-item:active { transform: scale(0.98); }
.bill-left { display: flex; align-items: center; gap: 12px; flex: 1; min-width: 0; }
.bill-icon {
  width: 40px; height: 40px; display: flex; align-items: center; justify-content: center;
  font-size: 20px; background: var(--bg-input); border-radius: 12px; flex-shrink: 0;
}
.bill-info { display: flex; flex-direction: column; gap: 2px; min-width: 0; }
.bill-category { font-size: 15px; font-weight: 500; }
.bill-meta { font-size: 12px; color: var(--text-muted); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.bill-right { text-align: right; flex-shrink: 0; margin-left: 12px; }
.bill-amount { font-size: 16px; font-weight: 700; font-variant-numeric: tabular-nums; }
.income-text { color: var(--income); }
.expense-text { color: var(--expense); }
.bill-tags { display: flex; gap: 4px; margin-top: 4px; justify-content: flex-end; }
.mini-tag { font-size: 10px; padding: 2px 6px; border-radius: 4px; }

.modal-overlay {
  position: fixed; inset: 0; background: var(--bg-overlay); z-index: 200;
  display: flex; align-items: center; justify-content: center; padding: 20px;
  animation: fadeIn 0.2s ease;
}
.modal-content { width: 100%; max-width: 360px; }
.modal-content h3 { font-size: 18px; margin-bottom: 20px; }
.edit-form { display: flex; flex-direction: column; gap: 16px; }
.form-group { display: flex; flex-direction: column; gap: 6px; }
.form-group label { font-size: 13px; color: var(--text-secondary); font-weight: 500; }
.form-actions { display: flex; gap: 12px; margin-top: 8px; }
.btn-delete {
  flex: 1; padding: 14px; border-radius: var(--radius-sm);
  background: var(--expense-bg); color: var(--expense); font-weight: 600;
}
.btn-primary { flex: 2; }
</style>
