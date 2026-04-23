<template>
  <div class="page accounts">
    <div class="page-header">
      <h1>账户</h1>
      <button class="import-btn" @click="$router.push('/import')">📥 导入</button>
    </div>

    <div class="total-card card">
      <span class="total-label">总资产</span>
      <span class="total-amount" :class="totalBalance >= 0 ? 'positive' : 'negative'">
        ¥{{ formatMoney(totalBalance) }}
      </span>
    </div>

    <div class="account-list" v-if="store.accounts.length">
      <div class="account-item card" v-for="acc in store.accounts" :key="acc.id">
        <div class="acc-left">
          <span class="acc-icon">{{ typeIcons[acc.type] || '💳' }}</span>
          <div class="acc-info">
            <span class="acc-name">{{ acc.name }}</span>
            <span class="acc-type">{{ typeLabels[acc.type] || '其他' }}</span>
          </div>
        </div>
        <span class="acc-balance" :class="acc.balance >= 0 ? 'positive' : 'negative'">
          ¥{{ formatMoney(acc.balance) }}
        </span>
      </div>
    </div>

    <div class="section-title" style="margin-top: 28px">添加账户</div>
    <div class="card add-form">
      <div class="form-group">
        <label>账户名称</label>
        <input type="text" v-model="newAccount.name" placeholder="如：招商银行储蓄卡" />
      </div>
      <div class="form-group">
        <label>账户类型</label>
        <div class="type-grid">
          <button
            v-for="(label, key) in typeLabels"
            :key="key"
            class="type-btn"
            :class="{ active: newAccount.type === Number(key) }"
            @click="newAccount.type = Number(key)"
          >
            {{ typeIcons[key] }} {{ label }}
          </button>
        </div>
      </div>
      <div class="form-group">
        <label>初始余额</label>
        <input type="number" v-model="newAccount.initial_balance" placeholder="0.00" step="0.01" />
      </div>
      <button class="btn-primary" @click="addAccount" :disabled="!newAccount.name">添加</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { accountApi } from '@/api/types'
import { useDataStore } from '@/stores/data'

const store = useDataStore()

const typeLabels: Record<number, string> = {
  1: '现金', 2: '银行卡', 3: '信用卡', 4: '支付宝', 5: '微信', 6: '其他',
}
const typeIcons: Record<number, string> = {
  1: '💵', 2: '🏦', 3: '💳', 4: '🔵', 5: '💚', 6: '📌',
}

const newAccount = ref({
  name: '',
  type: 1,
  initial_balance: 0,
})

const totalBalance = computed(() => store.accounts.reduce((sum, a) => sum + a.balance, 0))

function formatMoney(n: number) {
  return Math.abs(n).toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

async function addAccount() {
  if (!newAccount.value.name) return
  try {
    await accountApi.create({
      name: newAccount.value.name,
      type: newAccount.value.type,
      initial_balance: Number(newAccount.value.initial_balance) || 0,
    })
    newAccount.value = { name: '', type: 1, initial_balance: 0 }
    await store.refreshAccounts()
  } catch (e: any) {
    alert(e.message || '添加失败')
  }
}

onMounted(() => store.loadAll())
</script>

<style scoped>
.total-card {
  text-align: center;
  padding: 28px 20px;
  background: linear-gradient(135deg, #1e1e30 0%, #1a1a28 100%);
  border: 1px solid rgba(99, 102, 241, 0.15);
  margin-bottom: 20px;
}
.total-label { font-size: 13px; color: var(--text-secondary); display: block; margin-bottom: 4px; }
.total-amount { font-size: 32px; font-weight: 800; letter-spacing: -1px; font-variant-numeric: tabular-nums; }
.positive { color: var(--income); }
.negative { color: var(--expense); }

.account-list { display: flex; flex-direction: column; gap: 8px; }
.account-item { display: flex; align-items: center; justify-content: space-between; padding: 16px; }
.acc-left { display: flex; align-items: center; gap: 12px; }
.acc-icon {
  width: 44px; height: 44px; display: flex; align-items: center; justify-content: center;
  font-size: 22px; background: var(--bg-input); border-radius: 12px;
}
.acc-info { display: flex; flex-direction: column; gap: 2px; }
.acc-name { font-size: 15px; font-weight: 500; }
.acc-type { font-size: 12px; color: var(--text-muted); }
.acc-balance { font-size: 17px; font-weight: 700; font-variant-numeric: tabular-nums; }

.add-form { display: flex; flex-direction: column; gap: 16px; }
.form-group { display: flex; flex-direction: column; gap: 6px; }
.form-group label { font-size: 13px; color: var(--text-secondary); font-weight: 600; }

.type-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; }
.type-btn {
  padding: 10px; border-radius: var(--radius-sm); background: var(--bg-input);
  color: var(--text-secondary); border: 1px solid var(--border); font-size: 13px;
  text-align: center;
}
.type-btn.active { background: var(--primary-bg); color: var(--primary-light); border-color: var(--primary); }

.import-btn {
  font-size: 13px; padding: 6px 14px; border-radius: 20px;
  background: var(--primary-bg); color: var(--primary-light); border: 1px solid var(--primary);
}
</style>
