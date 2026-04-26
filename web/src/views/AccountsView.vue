<template>
  <div class="page accounts-page">
    <div class="page-header">
      <span class="back-btn" @click="$router.back()">‹</span>
      <span class="page-title">资产</span>
      <span class="eye-btn" @click="showAmount = !showAmount">{{ showAmount ? '👁' : '👁‍🗨' }}</span>
    </div>

    <div class="card" style="text-align: center">
      <div class="asset-net">
        <div class="asset-label">净资产</div>
        <div class="asset-big">{{ showAmount ? '¥ ' + formatMoney(netWorth) : '¥ ****' }}</div>
        <div class="asset-split">
          <span>资产 <b style="color: var(--text-primary)">{{ showAmount ? '¥' + formatMoney(totalAssets) : '****' }}</b></span>
          <span>负债 <b style="color: var(--accent)">{{ showAmount ? '¥' + formatMoney(totalDebts) : '****' }}</b></span>
        </div>
      </div>
    </div>

    <div class="card">
      <div class="section-title">资产账户</div>
      <div class="account-list">
        <div v-for="acc in activeAccounts" :key="acc.id" class="acct-item">
          <div class="acct-dot" :style="{ background: getAccountTypeColor(acc.type) }"></div>
          <span class="acct-name">{{ acc.name }}</span>
          <span class="acct-amt">{{ showAmount ? '¥ ' + formatMoney(acc.balance) : '****' }}</span>
        </div>
      </div>
    </div>

    <div class="card">
      <div class="section-header">
        <span class="section-title" style="margin-bottom: 0">账户管理</span>
        <button class="add-btn" @click="showAddForm = true">+ 新增</button>
      </div>
      <div v-for="acc in accounts" :key="acc.id" class="acct-manage-item">
        <div class="acct-dot" :style="{ background: getAccountTypeColor(acc.type) }"></div>
        <div class="acct-info">
          <span class="acct-name">{{ acc.name }}</span>
          <span class="acct-type">{{ getAccountTypeName(acc.type) }}</span>
        </div>
        <div class="acct-actions">
          <button class="action-btn edit" @click="editAccount(acc)">编辑</button>
          <button class="action-btn delete" @click="handleDeleteAccount(acc)">删除</button>
        </div>
      </div>
    </div>

    <div v-if="showAddForm || editingAccount" class="modal-overlay" @click.self="closeForm">
      <div class="form-modal">
        <div class="form-header">
          <span class="close-btn" @click="closeForm">✕</span>
          <span class="form-title">{{ editingAccount ? '编辑账户' : '新增账户' }}</span>
          <span style="width: 20px"></span>
        </div>
        <div class="form-body">
          <div class="form-field">
            <label>账户名称</label>
            <input v-model="form.name" type="text" placeholder="请输入账户名称" class="form-input" />
          </div>
          <div class="form-field">
            <label>账户类型</label>
            <CustomSelect
              v-model="form.type"
              :options="accountTypeOptions"
              placeholder="选择账户类型"
              class="form-input"
            />
          </div>
          <div class="form-field">
            <label>初始余额</label>
            <input v-model.number="form.initial_balance" type="number" step="0.01" class="form-input" />
          </div>
          <div class="form-field">
            <label>设为默认</label>
            <input v-model="form.is_default" type="checkbox" class="form-checkbox" />
          </div>
          <button class="btn-primary save-btn" @click="saveAccount">保存</button>
        </div>
      </div>
    </div>

    <ConfirmDialog
      ref="confirmDialog"
      icon="🗑️"
      title="确定要删除此账户吗？"
      description="此操作不可撤销，删除后账户及其关联的账单数据将永久丢失。"
      confirmText="确认删除"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAccountStore } from '@/stores/data'
import { formatMoney, getAccountTypeName, getAccountTypeColor } from '@/utils/format'
import CustomSelect from '@/components/CustomSelect.vue'
import ConfirmDialog from '@/components/ConfirmDialog.vue'

const accountStore = useAccountStore()
const confirmDialog = ref(null)

const accountTypeOptions = [
  { label: '现金', value: 1 },
  { label: '银行卡', value: 2 },
  { label: '信用卡', value: 3 },
  { label: '支付宝', value: 4 },
  { label: '微信', value: 5 },
  { label: '其他', value: 6 },
]

const showAmount = ref(true)
const showAddForm = ref(false)
const editingAccount = ref(null)
const form = ref({ name: '', type: 1, initial_balance: 0, is_default: false })

const accounts = computed(() => accountStore.accounts)
const activeAccounts = computed(() => accounts.value.filter(a => a.status === 1))
const totalAssets = computed(() => accountStore.totalAssets())
const totalDebts = computed(() => accountStore.totalDebts())
const netWorth = computed(() => totalAssets.value - totalDebts.value)

function editAccount(acc) {
  editingAccount.value = acc
  form.value = { name: acc.name, type: acc.type, initial_balance: acc.initial_balance, is_default: acc.is_default === 1 }
}

function closeForm() {
  showAddForm.value = false
  editingAccount.value = null
  form.value = { name: '', type: 1, initial_balance: 0, is_default: false }
}

async function saveAccount() {
  if (!form.value.name) {
    alert('请输入账户名称')
    return
  }
  try {
    if (editingAccount.value) {
      await accountStore.updateAccount(editingAccount.value.id, {
        name: form.value.name,
        type: form.value.type,
      })
    } else {
      await accountStore.createAccount(form.value)
    }
    closeForm()
    accountStore.fetchAccounts()
  } catch (e) {
    alert(e.response?.data?.detail || '保存失败')
  }
}

async function handleDeleteAccount(acc) {
  const confirmed = await confirmDialog.value.show()
  if (!confirmed) return
  try {
    await accountStore.deleteAccount(acc.id)
    accountStore.fetchAccounts()
  } catch (e) {
    alert(e.response?.data?.detail || '删除失败')
  }
}

onMounted(() => accountStore.fetchAccounts())
</script>

<style scoped>
.back-btn {
  font-size: 22px;
  color: var(--text-primary);
  cursor: pointer;
  width: 24px;
}

.eye-btn {
  font-size: 16px;
  color: #c4b8a0;
  cursor: pointer;
}

.asset-net {
  padding: 24px 0 16px;
}

.asset-label {
  font-size: 13px;
  color: var(--text-muted);
}

.asset-big {
  font-size: 36px;
  font-weight: 800;
  color: var(--text-primary);
  letter-spacing: -1px;
  margin-top: 4px;
}

.asset-split {
  display: flex;
  justify-content: center;
  gap: 24px;
  margin-top: 8px;
  font-size: 13px;
  color: var(--text-light);
}

.account-list {
  padding: 0;
}

.acct-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 0;
  border-bottom: 0.5px solid #f0ece5;
}

.acct-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
}

.acct-name {
  flex: 1;
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
}

.acct-amt {
  font-size: 15px;
  font-weight: 700;
  color: var(--text-primary);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.add-btn {
  font-size: 13px;
  color: var(--accent);
  font-weight: 600;
}

.acct-manage-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 0;
  border-bottom: 0.5px solid #f0ece5;
}

.acct-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.acct-type {
  font-size: 11px;
  color: #bbb;
}

.acct-actions {
  display: flex;
  gap: 8px;
}

.action-btn {
  font-size: 12px;
  padding: 4px 10px;
  border-radius: 6px;
  cursor: pointer;
}

.action-btn.edit {
  color: var(--accent);
  background: rgba(212, 165, 116, 0.1);
}

.action-btn.delete {
  color: var(--danger);
  background: rgba(212, 123, 123, 0.1);
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

.form-modal {
  background: var(--bg-card);
  border-radius: 20px;
  padding: 24px;
  width: 100%;
  max-width: 360px;
}

.form-header {
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

.form-title {
  font-size: 17px;
  font-weight: 700;
}

.form-body {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.form-field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-field label {
  font-size: 13px;
  color: #777;
}

.form-input {
  padding: 10px 14px;
  border: 1.5px solid var(--border);
  border-radius: 10px;
  font-size: 14px;
  color: var(--text-primary);
  background: var(--bg-primary);
}

.form-input:focus {
  border-color: var(--accent);
}

.form-checkbox {
  width: 18px;
  height: 18px;
  accent-color: var(--accent);
}

.save-btn {
  width: 100%;
  margin-top: 8px;
}
</style>
