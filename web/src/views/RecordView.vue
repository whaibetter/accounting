<template>
  <div class="page record-page">
    <div class="record-header">
      <span class="close-btn" @click="goBack">✕</span>
      <span class="record-title">记一笔</span>
      <span style="width: 20px"></span>
    </div>

    <div class="tab-bar">
      <div class="tab-item" :class="{ active: billType === 1 }" @click="switchType(1)">支出</div>
      <div class="tab-item" :class="{ active: billType === 2 }" @click="switchType(2)">收入</div>
      <div class="tab-item" :class="{ active: billType === 3 }" @click="switchType(3)">转账</div>
    </div>

    <div class="cat-grid">
      <div
        v-for="cat in displayCategories"
        :key="cat.id"
        class="cat-item"
        :class="{ active: selectedCategory?.id === cat.id }"
        @click="selectCategory(cat)"
      >
        <div class="cat-icon-box" :style="{ background: catBgColors[cat.id % catBgColors.length] }">
          {{ getCatIcon(cat.icon) }}
        </div>
        <span class="cat-name">{{ cat.name }}</span>
      </div>
    </div>

    <div class="form-section">
      <div class="form-row">
        <label>账户</label>
        <CustomSelect
          v-model="selectedAccountId"
          :options="accountOptions"
          placeholder="选择账户"
          class="form-select"
        />
      </div>
      <div v-if="billType === 3" class="form-row">
        <label>转入账户</label>
        <CustomSelect
          v-model="transferToAccountId"
          :options="accountOptions"
          placeholder="选择转入账户"
          class="form-select"
        />
      </div>
      <div class="form-row">
        <label>日期</label>
        <input type="date" v-model="billDate" class="form-input" />
      </div>
      <div class="form-row">
        <label>备注</label>
        <input type="text" v-model="remark" placeholder="添加备注..." class="form-input" />
      </div>
    </div>

    <div class="keypad-area">
      <div class="display-amount">¥ {{ displayAmount }}</div>
      <div class="keypad-grid">
        <button class="key-btn op" @click="clearAmount">清空</button>
        <button class="key-btn num" @click="inputKey('7')">7</button>
        <button class="key-btn num" @click="inputKey('8')">8</button>
        <button class="key-btn num" @click="inputKey('9')">9</button>

        <button class="key-btn op" @click="backspace">⌫</button>
        <button class="key-btn num" @click="inputKey('4')">4</button>
        <button class="key-btn num" @click="inputKey('5')">5</button>
        <button class="key-btn num" @click="inputKey('6')">6</button>

        <button class="key-btn op" @click="toggleSign">±</button>
        <button class="key-btn num" @click="inputKey('1')">1</button>
        <button class="key-btn num" @click="inputKey('2')">2</button>
        <button class="key-btn num" @click="inputKey('3')">3</button>

        <button class="key-btn op" @click="inputDot">.</button>
        <button class="key-btn num" @click="inputKey('0')">0</button>
        <button class="key-btn confirm" @click="submitBill">✓</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useBillStore, useAccountStore, useCategoryStore } from '@/stores/data'
import CustomSelect from '@/components/CustomSelect.vue'
import dayjs from 'dayjs'
import { getCategoryIcon } from '@/utils/format'

const router = useRouter()
const billStore = useBillStore()
const accountStore = useAccountStore()
const categoryStore = useCategoryStore()

const billType = ref(1)
const amountStr = ref('')
const isNegative = ref(false)
const selectedCategory = ref(null)
const selectedAccountId = ref(null)
const transferToAccountId = ref(null)
const billDate = ref(dayjs().format('YYYY-MM-DD'))
const remark = ref('')
const submitting = ref(false)

const catBgColors = ['#fef6ee', '#fef0e6', '#eef6fc', '#fceef6', '#f5f0ee', '#eff6ee', '#f0f0f4', '#f6f0ee', '#eeeef6', '#eefef6']

function getCatIcon(icon) {
  return getCategoryIcon(icon)
}

const accounts = computed(() => accountStore.accounts.filter(a => a.status === 1))

const accountOptions = computed(() =>
  accounts.value.map(acc => ({ label: acc.name, value: acc.id }))
)

const displayCategories = computed(() => {
  const typeMap = { 1: 1, 2: 2, 3: 1 }
  const catType = typeMap[billType.value]
  return categoryStore.flatCategories().filter(c => c.type === catType && !c.parent_id)
})

const displayAmount = computed(() => {
  if (!amountStr.value) return '0.00'
  const num = parseFloat(amountStr.value) || 0
  return (isNegative.value ? -num : num).toFixed(2)
})

function switchType(t) {
  billType.value = t
  selectedCategory.value = null
}

function selectCategory(cat) {
  selectedCategory.value = cat
}

function inputKey(key) {
  if (amountStr.value.includes('.') && amountStr.value.split('.')[1].length >= 2) return
  if (amountStr.value.length >= 12) return
  amountStr.value += key
}

function inputDot() {
  if (amountStr.value.includes('.')) return
  if (!amountStr.value) amountStr.value = '0'
  amountStr.value += '.'
}

function backspace() {
  amountStr.value = amountStr.value.slice(0, -1)
}

function clearAmount() {
  amountStr.value = ''
  isNegative.value = false
}

function toggleSign() {
  isNegative.value = !isNegative.value
}

function goBack() {
  router.back()
}

async function submitBill() {
  const amount = parseFloat(amountStr.value)
  if (!amount || amount <= 0) {
    alert('请输入金额')
    return
  }
  if (!selectedCategory.value && billType.value !== 3) {
    alert('请选择分类')
    return
  }
  if (!selectedAccountId.value) {
    alert('请选择账户')
    return
  }
  if (billType.value === 3 && !transferToAccountId.value) {
    alert('请选择转入账户')
    return
  }

  submitting.value = true
  try {
    const data = {
      account_id: selectedAccountId.value,
      type: billType.value,
      amount: amount,
      bill_date: billDate.value,
      remark: remark.value,
    }
    if (billType.value === 3) {
      data.transfer_to_account_id = transferToAccountId.value
    } else {
      data.category_id = selectedCategory.value.id
    }
    await billStore.createBill(data)
    router.back()
  } catch (e) {
    alert(e.response?.data?.detail || '创建失败')
  } finally {
    submitting.value = false
  }
}

onMounted(async () => {
  await Promise.all([
    accountStore.fetchAccounts(),
    categoryStore.fetchCategories(),
  ])
  if (accounts.value.length) {
    const defaultAcc = accounts.value.find(a => a.is_default === 1)
    selectedAccountId.value = defaultAcc?.id || accounts.value[0].id
  }
})
</script>

<style scoped>
.record-page {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: var(--bg-primary);
  padding-bottom: 0;
  padding-bottom: var(--safe-bottom);
}

.record-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 20px;
}

.close-btn {
  font-size: 18px;
  color: #bbb;
  cursor: pointer;
  width: 24px;
}

.record-title {
  font-size: 17px;
  font-weight: 700;
  color: var(--text-primary);
}

.tab-bar {
  display: flex;
  gap: 0;
  padding: 0 20px;
  margin-bottom: 16px;
}

.tab-item {
  flex: 1;
  text-align: center;
  padding: 10px 0;
  font-size: 14px;
  font-weight: 500;
  color: var(--text-muted);
  border-bottom: 2px solid transparent;
  cursor: pointer;
  transition: all 0.2s;
}

.tab-item.active {
  color: var(--text-primary);
  font-weight: 600;
  border-bottom-color: var(--accent);
}

.cat-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 8px 4px;
  padding: 0 16px;
  margin-bottom: 12px;
}

.cat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  cursor: pointer;
  padding: 6px 2px;
  border-radius: 10px;
  transition: all 0.15s;
}

.cat-item:active {
  transform: scale(0.94);
}

.cat-item.active .cat-icon-box {
  box-shadow: 0 0 0 2px var(--accent), 0 2px 8px rgba(212, 165, 116, 0.25);
}

.cat-item.active .cat-name {
  color: var(--accent-dark);
  font-weight: 600;
}

.cat-icon-box {
  width: 44px;
  height: 44px;
  border-radius: 13px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
  transition: all 0.2s;
}

.cat-name {
  font-size: 11px;
  color: #888;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 100%;
  text-align: center;
}

.form-section {
  padding: 4px 16px 0;
}

.form-row {
  display: flex;
  align-items: center;
  padding: 10px 4px;
  border-bottom: 0.5px solid #f0ece5;
}

.form-row label {
  width: 52px;
  font-size: 13px;
  color: #888;
  flex-shrink: 0;
}

.form-input,
.form-select {
  flex: 1;
  border: none;
  font-size: 14px;
  color: var(--text-primary);
  background: transparent;
  padding: 4px 0;
}

.keypad-area {
  margin-top: auto;
  padding: 8px 16px 28px;
  background: linear-gradient(to bottom, transparent 0%, rgba(255,255,255,0.6) 15%);
}

.display-amount {
  text-align: center;
  font-size: 40px;
  font-weight: 300;
  color: var(--text-primary);
  padding: 14px 0 16px;
  letter-spacing: -1px;
}

.keypad-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 8px;
}

.key-btn {
  height: 48px;
  border-radius: 12px;
  font-size: 20px;
  font-weight: 500;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.1s;
  border: none;
  cursor: pointer;
}

.key-btn:active {
  transform: scale(0.93);
}

.key-btn.num {
  background: #faf8f3;
  color: var(--text-primary);
}

.key-btn.num:active {
  background: #ede7dc;
}

.key-btn.op {
  background: #f2ebe0;
  color: #999;
  font-size: 15px;
}

.key-btn.op:active {
  background: #e8dfd0;
}

.key-btn.confirm {
  background: linear-gradient(135deg, var(--accent), var(--accent-dark));
  color: white;
  font-size: 20px;
  font-weight: 700;
  box-shadow: 0 3px 10px rgba(196, 148, 99, 0.35);
}

.key-btn.confirm:active {
  box-shadow: 0 1px 4px rgba(196, 148, 99, 0.3);
}
</style>
