<template>
  <div class="page record-page">
    <div class="record-header">
      <span class="close-btn" @click="goBack">✕</span>
      <span class="record-title">记一笔</span>
      <span style="width: 20px"></span>
    </div>

    <div class="tab-bar">
      <div class="tab-item" :class="{ active: billType === 1 }" @click="billType = 1">支出</div>
      <div class="tab-item" :class="{ active: billType === 2 }" @click="billType = 2">收入</div>
      <div class="tab-item" :class="{ active: billType === 3 }" @click="billType = 3">转账</div>
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
          {{ cat.icon || '📝' }}
        </div>
        <span class="cat-name">{{ cat.name }}</span>
      </div>
    </div>

    <div class="form-section">
      <div class="form-row">
        <label>账户</label>
        <select v-model="selectedAccountId" class="form-select">
          <option v-for="acc in accounts" :key="acc.id" :value="acc.id">{{ acc.name }}</option>
        </select>
      </div>
      <div v-if="billType === 3" class="form-row">
        <label>转入账户</label>
        <select v-model="transferToAccountId" class="form-select">
          <option v-for="acc in accounts" :key="acc.id" :value="acc.id">{{ acc.name }}</option>
        </select>
      </div>
      <div class="form-row">
        <label>日期</label>
        <input type="date" v-model="billDate" class="form-input" />
      </div>
      <div class="form-row">
        <label>备注</label>
        <input type="text" v-model="remark" placeholder="添加备注" class="form-input" />
      </div>
    </div>

    <div class="keypad-area">
      <div class="display-amount">¥ {{ displayAmount }}</div>
      <div class="keypad-grid">
        <button class="key-btn op" @click="clearAmount">清空</button>
        <button class="key-btn" @click="inputKey('1')">1</button>
        <button class="key-btn" @click="inputKey('2')">2</button>
        <button class="key-btn" @click="inputKey('3')">3</button>
        <button class="key-btn op" @click="backspace">⌫</button>
        <button class="key-btn" @click="inputKey('4')">4</button>
        <button class="key-btn" @click="inputKey('5')">5</button>
        <button class="key-btn" @click="inputKey('6')">6</button>
        <button class="key-btn op" @click="toggleSign">±</button>
        <button class="key-btn" @click="inputKey('7')">7</button>
        <button class="key-btn" @click="inputKey('8')">8</button>
        <button class="key-btn" @click="inputKey('9')">9</button>
        <button class="key-btn op" @click="inputDot">.</button>
        <button class="key-btn zero-btn" @click="inputKey('0')">0</button>
        <button class="key-btn confirm" @click="submitBill">✓</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useBillStore, useAccountStore, useCategoryStore } from '@/stores/data'
import dayjs from 'dayjs'

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

const accounts = computed(() => accountStore.accounts.filter(a => a.status === 1))

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
  if (!selectedCategory.value) {
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
      category_id: selectedCategory.value.id,
      type: billType.value,
      amount: amount,
      bill_date: billDate.value,
      remark: remark.value,
    }
    if (billType.value === 3) {
      data.transfer_to_account_id = transferToAccountId.value
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
  min-height: 100vh;
  padding-bottom: 0;
}

.record-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 20px;
}

.close-btn {
  font-size: 20px;
  color: #bbb;
  cursor: pointer;
}

.record-title {
  font-size: 19px;
  font-weight: 800;
  color: var(--text-primary);
}

.cat-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  padding: 0 20px;
}

.cat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  transition: transform 0.15s;
}

.cat-item:active {
  transform: scale(0.94);
}

.cat-item.active .cat-icon-box {
  box-shadow: 0 0 0 2px var(--accent);
}

.cat-icon-box {
  width: 48px;
  height: 48px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  transition: box-shadow 0.2s;
}

.cat-name {
  font-size: 11px;
  color: #777;
}

.form-section {
  padding: 16px 20px 0;
}

.form-row {
  display: flex;
  align-items: center;
  padding: 10px 0;
  border-bottom: 0.5px solid #f0ece5;
}

.form-row label {
  width: 70px;
  font-size: 14px;
  color: #777;
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
  padding: 12px 20px 24px;
}

.display-amount {
  text-align: center;
  font-size: 42px;
  font-weight: 300;
  color: var(--text-primary);
  padding: 12px 0;
  letter-spacing: -1px;
}

.keypad-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 8px;
}

.key-btn {
  aspect-ratio: 1.3;
  border-radius: 14px;
  background: var(--bg-input);
  font-size: 20px;
  font-weight: 500;
  color: var(--text-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.1s;
}

.key-btn:active {
  transform: scale(0.94);
  background: #ede7dc;
}

.key-btn.op {
  background: #efe8dd;
  font-size: 16px;
  color: #888;
}

.key-btn.confirm {
  background: linear-gradient(135deg, var(--accent), var(--accent-dark));
  color: white;
  font-size: 18px;
  font-weight: 700;
}

.zero-btn {
  grid-column: span 2;
}
</style>
