<template>
  <div class="page import-page">
    <div class="page-header">
      <span class="back-btn" @click="$router.back()">‹</span>
      <span class="page-title">数据导入</span>
      <span style="width: 24px"></span>
    </div>

    <div class="card">
      <div class="section-title">导入账单</div>
      <div class="form-field">
        <label>JSON数据</label>
        <textarea
          v-model="jsonInput"
          placeholder='{"bills": [{"account": "现金", "category": "午餐", "type": 1, "amount": 35.5, "date": "2026-04-17", "remark": "工作餐"}]}'
          class="form-textarea"
          rows="8"
        ></textarea>
      </div>
      <button class="btn-primary" @click="importBills" :disabled="importing" style="width: 100%">
        {{ importing ? '导入中...' : '导入账单' }}
      </button>
    </div>

    <div v-if="result" class="card">
      <div class="section-title">导入结果</div>
      <div class="result-item">
        <span class="result-label">成功导入</span>
        <span class="result-value success">{{ result.success || 0 }} 条</span>
      </div>
      <div v-if="result.skipped" class="result-item">
        <span class="result-label">跳过</span>
        <span class="result-value">{{ result.skipped }} 条</span>
      </div>
      <div v-if="result.errors && result.errors.length" class="error-list">
        <div class="section-title" style="color: var(--danger)">错误信息</div>
        <div v-for="(err, idx) in result.errors" :key="idx" class="error-item">{{ err }}</div>
      </div>
    </div>

    <div class="card">
      <div class="section-title">导入账户</div>
      <div class="form-field">
        <label>JSON数据</label>
        <textarea
          v-model="accountJsonInput"
          placeholder='{"accounts": [{"name": "建设银行储蓄卡", "type": 2, "initial_balance": 10000}]}'
          class="form-textarea"
          rows="4"
        ></textarea>
      </div>
      <button class="btn-primary" @click="importAccounts" :disabled="importing" style="width: 100%">
        {{ importing ? '导入中...' : '导入账户' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { importApi } from '@/services'

const jsonInput = ref('')
const accountJsonInput = ref('')
const importing = ref(false)
const result = ref(null)

async function importBills() {
  if (!jsonInput.value.trim()) {
    alert('请输入JSON数据')
    return
  }
  importing.value = true
  result.value = null
  try {
    const data = JSON.parse(jsonInput.value)
    const res = await importApi.bills(data)
    result.value = res.data.data
  } catch (e) {
    if (e instanceof SyntaxError) {
      alert('JSON格式错误，请检查输入')
    } else {
      alert(e.response?.data?.detail || '导入失败')
    }
  } finally {
    importing.value = false
  }
}

async function importAccounts() {
  if (!accountJsonInput.value.trim()) {
    alert('请输入JSON数据')
    return
  }
  importing.value = true
  try {
    const data = JSON.parse(accountJsonInput.value)
    const res = await importApi.accounts(data)
    result.value = res.data.data
  } catch (e) {
    if (e instanceof SyntaxError) {
      alert('JSON格式错误，请检查输入')
    } else {
      alert(e.response?.data?.detail || '导入失败')
    }
  } finally {
    importing.value = false
  }
}
</script>

<style scoped>
.back-btn {
  font-size: 22px;
  color: var(--text-primary);
  cursor: pointer;
  width: 24px;
}

.form-field {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-bottom: 12px;
}

.form-field label {
  font-size: 13px;
  color: #777;
}

.form-textarea {
  padding: 10px 14px;
  border: 1.5px solid var(--border);
  border-radius: 10px;
  font-size: 13px;
  color: var(--text-primary);
  background: var(--bg-primary);
  resize: vertical;
  font-family: 'Courier New', monospace;
}

.form-textarea:focus {
  border-color: var(--accent);
}

.result-item {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 0.5px solid #f0ece5;
}

.result-label {
  font-size: 14px;
  color: #777;
}

.result-value {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

.result-value.success {
  color: var(--success);
}

.error-list {
  margin-top: 12px;
}

.error-item {
  font-size: 12px;
  color: var(--danger);
  padding: 4px 0;
}
</style>
