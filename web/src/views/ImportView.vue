<template>
  <div class="page import">
    <div class="page-header">
      <button class="back-btn" @click="$router.back()">‹</button>
      <h1>导入数据</h1>
      <div style="width: 36px"></div>
    </div>

    <div class="tabs">
      <button
        v-for="tab in tabs"
        :key="tab.key"
        class="tab"
        :class="{ active: activeTab === tab.key }"
        @click="activeTab = tab.key"
      >{{ tab.label }}</button>
    </div>

    <div class="format-hint card">
      <div class="hint-title">📋 JSON格式说明</div>
      <pre class="hint-code" v-if="activeTab === 'accounts'">{{ accountExample }}</pre>
      <pre class="hint-code" v-if="activeTab === 'bills'">{{ billExample }}</pre>
      <button class="copy-btn" @click="copyExample">复制示例</button>
    </div>

    <div class="input-section">
      <div class="section-title">{{ activeTab === 'accounts' ? '账户' : '账单' }}JSON数据</div>
      <textarea
        class="json-input"
        v-model="jsonInput"
        :placeholder="activeTab === 'accounts' ? accountPlaceholder : billPlaceholder"
        spellcheck="false"
      ></textarea>
    </div>

    <div class="actions">
      <button class="btn-primary" @click="parseAndPreview" :disabled="!jsonInput.trim()">
        预览解析
      </button>
    </div>

    <div class="preview-section" v-if="previewResult">
      <div class="preview-header">
        <span class="section-title">解析结果</span>
        <span class="preview-stats">
          <span class="stat success">✓ {{ previewResult.success }}条</span>
          <span class="stat skipped" v-if="previewResult.skipped !== undefined">跳过 {{ previewResult.skipped }}条</span>
          <span class="stat error" v-if="previewResult.errors?.length">✕ {{ previewResult.errors.length }}条失败</span>
        </span>
      </div>

      <div class="error-list" v-if="previewResult.errors?.length">
        <div class="error-item" v-for="(err, i) in previewResult.errors" :key="i">
          <span class="error-idx">#{{ typeof err === 'object' ? err.index : i + 1 }}</span>
          <span class="error-msg">{{ typeof err === 'string' ? err : err.reason || JSON.stringify(err) }}</span>
        </div>
      </div>

      <button class="btn-primary import-btn" @click="doImport" :disabled="previewResult.success === 0">
        确认导入
      </button>
    </div>

    <div class="result-toast" v-if="toast.show" :class="toast.type">
      {{ toast.message }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { importApi } from '@/api/types'
import { useDataStore } from '@/stores/data'
import { useRouter } from 'vue-router'

const router = useRouter()
const store = useDataStore()

const tabs = [
  { key: 'accounts', label: '导入账户' },
  { key: 'bills', label: '导入账单' },
]
const activeTab = ref('accounts')
const jsonInput = ref('')
const previewResult = ref<any>(null)
const toast = reactive({ show: false, message: '', type: 'success' })

const accountExample = `{
  "accounts": [
    {
      "name": "建设银行储蓄卡",
      "type": 2,
      "initial_balance": 10000
    },
    {
      "name": "支付宝",
      "type": 4,
      "initial_balance": 5000
    }
  ]
}`

const billExample = `{
  "bills": [
    {
      "account": "建设银行储蓄卡",
      "category": "午餐",
      "type": 1,
      "amount": 35.5,
      "date": "2026-04-17",
      "remark": "工作餐"
    },
    {
      "account": "支付宝",
      "category": "打车",
      "type": 1,
      "amount": 28.0,
      "date": "2026-04-17"
    },
    {
      "account": "建设银行储蓄卡",
      "category": "工资",
      "type": 2,
      "amount": 15000,
      "date": "2026-04-01"
    }
  ]
}`

const accountPlaceholder = `粘贴账户JSON，例如：
{
  "accounts": [
    {"name": "账户名称", "type": 1, "initial_balance": 0}
  ]
}`

const billPlaceholder = `粘贴账单JSON，例如：
{
  "bills": [
    {"account": "账户名称", "category": "分类", "type": 1, "amount": 100, "date": "2026-04-01", "remark": "备注"}
  ]
}`

function copyExample() {
  navigator.clipboard.writeText(activeTab.value === 'accounts' ? accountExample : billExample)
  showToast('已复制到剪贴板', 'success')
}

function showToast(message: string, type: string) {
  toast.message = message
  toast.type = type
  toast.show = true
  setTimeout(() => { toast.show = false }, 2500)
}

async function parseAndPreview() {
  previewResult.value = null
  let parsed: any
  try {
    parsed = JSON.parse(jsonInput.value)
  } catch (e) {
    showToast('JSON格式错误，请检查语法', 'error')
    return
  }

  if (activeTab.value === 'accounts') {
    if (!parsed.accounts || !Array.isArray(parsed.accounts)) {
      showToast('缺少 accounts 数组', 'error')
      return
    }
    previewResult.value = {
      success: parsed.accounts.length,
      skipped: 0,
      errors: [],
    }
  } else {
    if (!parsed.bills || !Array.isArray(parsed.bills)) {
      showToast('缺少 bills 数组', 'error')
      return
    }
    previewResult.value = {
      success: parsed.bills.length,
      errors: [],
    }
  }
}

async function doImport() {
  let parsed: any
  try {
    parsed = JSON.parse(jsonInput.value)
  } catch {
    showToast('JSON格式错误', 'error')
    return
  }

  try {
    if (activeTab.value === 'accounts') {
      const res = await importApi.importAccounts(parsed.accounts)
      previewResult.value = res.data
      showToast(`成功导入 ${res.data.success} 条账户`, 'success')
      await store.refreshAccounts()
    } else {
      const res = await importApi.importBills(parsed.bills)
      previewResult.value = res.data
      showToast(`成功导入 ${res.data.success} 条账单`, 'success')
      await store.refreshAccounts()
    }
    setTimeout(() => router.push('/'), 1500)
  } catch (e: any) {
    showToast(e.message || '导入失败', 'error')
  }
}
</script>

<style scoped>
.back-btn {
  width: 36px; height: 36px; border-radius: 50%; background: var(--bg-card);
  color: var(--text); font-size: 20px; display: flex; align-items: center;
  justify-content: center; border: 1px solid var(--border);
}

.tabs { display: flex; gap: 8px; margin-bottom: 20px; }
.tab {
  flex: 1; padding: 12px; border-radius: var(--radius-sm); font-weight: 600;
  background: var(--bg-card); color: var(--text-secondary); border: 1px solid var(--border);
}
.tab.active {
  background: var(--primary-bg); color: var(--primary-light); border-color: var(--primary);
}

.format-hint { margin-bottom: 20px; }
.hint-title { font-size: 14px; font-weight: 600; margin-bottom: 10px; }
.hint-code {
  font-size: 12px; background: var(--bg-input); padding: 12px;
  border-radius: var(--radius-sm); overflow-x: auto; white-space: pre;
  color: var(--text-secondary); line-height: 1.6; margin-bottom: 10px;
  font-family: 'SF Mono', 'Monaco', 'Consolas', monospace;
}
.copy-btn {
  font-size: 12px; padding: 6px 14px; border-radius: 6px;
  background: var(--bg-input); color: var(--primary-light); border: 1px solid var(--primary);
}

.input-section { margin-bottom: 20px; }
.json-input {
  width: 100%; min-height: 200px; resize: vertical; font-family: 'SF Mono', 'Monaco', 'Consolas', monospace;
  font-size: 13px; line-height: 1.6; color: var(--text); background: var(--bg-input);
  border: 1px solid var(--border); border-radius: var(--radius-sm); padding: 12px;
}

.actions { margin-bottom: 16px; }

.preview-section { animation: fadeUp 0.3s ease; }
.preview-header {
  display: flex; align-items: center; justify-content: space-between;
  margin-bottom: 12px;
}
.preview-stats { display: flex; gap: 10px; font-size: 13px; }
.stat.success { color: var(--income); }
.stat.skipped { color: var(--text-secondary); }
.stat.error { color: var(--expense); }

.error-list { display: flex; flex-direction: column; gap: 6px; margin-bottom: 16px; }
.error-item {
  display: flex; gap: 8px; padding: 8px 12px; background: var(--expense-bg);
  border-radius: var(--radius-xs); font-size: 12px;
}
.error-idx { color: var(--expense); font-weight: 600; flex-shrink: 0; }
.error-msg { color: var(--text-secondary); word-break: break-all; }

.import-btn { margin-top: 8px; }

.result-toast {
  position: fixed; bottom: 100px; left: 50%; transform: translateX(-50%);
  padding: 12px 24px; border-radius: 24px; font-size: 14px; font-weight: 500;
  z-index: 300; animation: slideUp 0.3s ease; white-space: nowrap;
}
.result-toast.success { background: var(--income); color: #000; }
.result-toast.error { background: var(--expense); color: #fff; }
</style>
