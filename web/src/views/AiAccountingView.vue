<template>
  <div class="page ai-accounting">
    <div class="page-header">
      <button class="back-btn" @click="$router.back()">‹</button>
      <h1>AI 智能记账</h1>
      <button class="settings-btn" @click="$router.push('/llm-settings')">⚙</button>
    </div>

    <div class="status-bar" v-if="!isConfigured" @click="$router.push('/llm-settings')">
      <span class="status-icon">⚠️</span>
      <span class="status-text">请先配置AI大模型API</span>
      <span class="status-arrow">›</span>
    </div>

    <div class="input-section">
      <div class="section-title">描述你的消费</div>
      <textarea
        class="text-input"
        v-model="inputText"
        placeholder="例如：今天买咖啡花了35元&#10;昨天午饭28块，打车回家15&#10;3月工资到账15000"
        :disabled="loading || !isConfigured"
        rows="4"
      ></textarea>
      <div class="input-footer">
        <span class="char-count">{{ inputText.length }}/2000</span>
        <div class="quick-actions">
          <button class="quick-btn" @click="inputText = '今天买咖啡花了35元'">☕ 示例1</button>
          <button class="quick-btn" @click="inputText = '昨天午饭28块，打车回家15'">🍜 示例2</button>
          <button class="quick-btn" @click="inputText = '3月工资到账15000'">💰 示例3</button>
        </div>
      </div>
    </div>

    <button
      class="btn-primary parse-btn"
      @click="parseText"
      :disabled="!inputText.trim() || loading || !isConfigured"
    >
      <span v-if="loading" class="loading-spinner"></span>
      <span v-else>🤖 AI 解析</span>
    </button>

    <div class="result-section" v-if="parseResult">
      <div class="result-header">
        <span class="section-title">解析结果</span>
        <span class="result-badge" :class="parseResult.success ? 'success' : 'error'">
          {{ parseResult.success ? `✓ 识别${parseResult.bills?.length || 0}笔` : '✕ 解析失败' }}
        </span>
      </div>

      <div class="error-msg card" v-if="parseResult.error">
        <span class="error-icon">❌</span>
        <span>{{ parseResult.error }}</span>
      </div>

      <div class="bill-list" v-if="parseResult.bills?.length">
        <div class="bill-item card" v-for="(bill, i) in parseResult.bills" :key="i">
          <div class="bill-top">
            <span class="bill-type" :class="bill.type === 1 ? 'expense' : 'income'">
              {{ bill.type === 1 ? '支出' : '收入' }}
            </span>
            <span class="bill-amount" :class="bill.type === 1 ? 'expense' : 'income'">
              {{ bill.type === 1 ? '-' : '+' }}¥{{ bill.amount.toFixed(2) }}
            </span>
          </div>
          <div class="bill-details">
            <div class="bill-row">
              <span class="bill-label">分类</span>
              <span class="bill-value">{{ bill.category }}</span>
            </div>
            <div class="bill-row">
              <span class="bill-label">日期</span>
              <span class="bill-value">{{ bill.date }}{{ bill.time ? ' ' + bill.time : '' }}</span>
            </div>
            <div class="bill-row" v-if="bill.remark">
              <span class="bill-label">备注</span>
              <span class="bill-value">{{ bill.remark }}</span>
            </div>
            <div class="bill-row" v-if="bill.account">
              <span class="bill-label">账户</span>
              <span class="bill-value">{{ bill.account }}</span>
            </div>
          </div>
        </div>
      </div>

      <div class="import-actions" v-if="parseResult.success && parseResult.bills?.length">
        <button class="btn-primary import-btn" @click="doImport" :disabled="importing">
          <span v-if="importing" class="loading-spinner"></span>
          <span v-else>✓ 确认导入</span>
        </button>
      </div>
    </div>

    <div class="import-result card" v-if="importResult">
      <div class="import-header">
        <span class="section-title">导入结果</span>
      </div>
      <div class="import-stats">
        <span class="stat success">✓ 成功 {{ importResult.success }}条</span>
        <span class="stat error" v-if="importResult.errors?.length">✕ 失败 {{ importResult.errors.length }}条</span>
      </div>
      <div class="error-list" v-if="importResult.errors?.length">
        <div class="error-item" v-for="(err, i) in importResult.errors" :key="i">
          <span class="error-idx">#{{ typeof err === 'object' ? err.index : i + 1 }}</span>
          <span class="error-msg">{{ typeof err === 'string' ? err : err.reason || JSON.stringify(err) }}</span>
        </div>
      </div>
    </div>

    <div class="result-toast" v-if="toast.show" :class="toast.type">
      {{ toast.message }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { llmApi, type ParseResult, type ImportResult } from '@/api/types'
import { useDataStore } from '@/stores/data'

const router = useRouter()
const store = useDataStore()

const inputText = ref('')
const loading = ref(false)
const importing = ref(false)
const isConfigured = ref(true)
const parseResult = ref<ParseResult | null>(null)
const importResult = ref<ImportResult | null>(null)
const toast = reactive({ show: false, message: '', type: 'success' })

function showToast(message: string, type: string) {
  toast.message = message
  toast.type = type
  toast.show = true
  setTimeout(() => { toast.show = false }, 2500)
}

async function checkConfig() {
  try {
    const res = await llmApi.getConfig()
    isConfigured.value = res.data?.is_configured || false
  } catch {
    isConfigured.value = false
  }
}

async function parseText() {
  if (!inputText.value.trim()) return

  loading.value = true
  parseResult.value = null
  importResult.value = null

  try {
    const res = await llmApi.parseText(inputText.value.trim())
    parseResult.value = res.data
    if (!res.data?.success) {
      showToast(res.data?.error || '解析失败', 'error')
    }
  } catch (e: any) {
    showToast(e.message || '解析请求失败', 'error')
    parseResult.value = { success: false, bills: [], error: e.message }
  } finally {
    loading.value = false
  }
}

async function doImport() {
  if (!parseResult.value?.bills?.length) return

  importing.value = true
  try {
    const defaultAccount = store.accounts.length > 0
      ? (store.accounts.find(a => a.is_default === 1)?.name || store.accounts[0]?.name)
      : undefined

    const res = await llmApi.parseAndImport(inputText.value.trim(), defaultAccount)
    const data = res.data

    if (data?.import_result) {
      importResult.value = data.import_result
      showToast(`成功导入 ${data.import_result.success} 条账单`, 'success')
      await store.refreshAccounts()
      if (data.import_result.success > 0) {
        setTimeout(() => router.push('/'), 2000)
      }
    } else {
      showToast(data?.parse_result?.error || '导入失败', 'error')
    }
  } catch (e: any) {
    showToast(e.message || '导入失败', 'error')
  } finally {
    importing.value = false
  }
}

onMounted(async () => {
  await store.loadAll()
  await checkConfig()
})
</script>

<style scoped>
.back-btn {
  width: 36px; height: 36px; border-radius: 50%; background: var(--bg-card);
  color: var(--text); font-size: 20px; display: flex; align-items: center;
  justify-content: center; border: 1px solid var(--border);
}

.settings-btn {
  width: 36px; height: 36px; border-radius: 50%; background: var(--bg-card);
  color: var(--text); font-size: 18px; display: flex; align-items: center;
  justify-content: center; border: 1px solid var(--border);
}

.status-bar {
  display: flex; align-items: center; gap: 10px; padding: 14px 16px;
  background: var(--expense-bg); border-radius: var(--radius-sm);
  margin-bottom: 20px; cursor: pointer; border: 1px solid rgba(248, 113, 113, 0.3);
}
.status-icon { font-size: 16px; }
.status-text { flex: 1; font-size: 14px; color: var(--expense); font-weight: 500; }
.status-arrow { color: var(--expense); font-size: 18px; }

.input-section { margin-bottom: 16px; }
.text-input {
  width: 100%; min-height: 120px; resize: vertical; font-size: 15px;
  line-height: 1.6; color: var(--text); background: var(--bg-input);
  border: 1px solid var(--border); border-radius: var(--radius-sm); padding: 14px;
  font-family: var(--font);
}
.text-input:disabled { opacity: 0.5; }

.input-footer {
  display: flex; align-items: center; justify-content: space-between;
  margin-top: 8px; gap: 8px;
}
.char-count { font-size: 12px; color: var(--text-muted); flex-shrink: 0; }
.quick-actions { display: flex; gap: 6px; flex-wrap: wrap; }
.quick-btn {
  padding: 4px 10px; border-radius: 14px; font-size: 11px;
  background: var(--bg-card); color: var(--text-secondary);
  border: 1px solid var(--border);
}
.quick-btn:active { transform: scale(0.95); }

.parse-btn { margin-bottom: 20px; display: flex; align-items: center; justify-content: center; gap: 8px; }
.parse-btn:disabled { opacity: 0.4; }

.loading-spinner {
  width: 18px; height: 18px; border: 2.5px solid var(--spinner-border);
  border-top-color: var(--spinner-top); border-radius: 50%; animation: spin 0.6s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

.result-section { animation: fadeUp 0.3s ease; }
.result-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px; }
.result-badge { font-size: 13px; font-weight: 600; padding: 4px 10px; border-radius: 14px; }
.result-badge.success { background: var(--income-bg); color: var(--income); }
.result-badge.error { background: var(--expense-bg); color: var(--expense); }

.error-msg {
  display: flex; align-items: center; gap: 8px; padding: 12px 16px;
  background: var(--expense-bg); border-color: rgba(248, 113, 113, 0.3);
  color: var(--expense); font-size: 14px; margin-bottom: 12px;
}
.error-icon { font-size: 16px; flex-shrink: 0; }

.bill-list { display: flex; flex-direction: column; gap: 10px; margin-bottom: 16px; }
.bill-item { padding: 14px; }
.bill-top { display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px; }
.bill-type {
  padding: 3px 10px; border-radius: 14px; font-size: 12px; font-weight: 600;
}
.bill-type.expense { background: var(--expense-bg); color: var(--expense); }
.bill-type.income { background: var(--income-bg); color: var(--income); }
.bill-amount { font-size: 22px; font-weight: 800; letter-spacing: -0.5px; }
.bill-amount.expense { color: var(--expense); }
.bill-amount.income { color: var(--income); }

.bill-details { display: flex; flex-direction: column; gap: 4px; }
.bill-row { display: flex; align-items: center; gap: 8px; }
.bill-label { font-size: 12px; color: var(--text-muted); min-width: 36px; }
.bill-value { font-size: 13px; color: var(--text-secondary); }

.import-actions { margin-top: 4px; }
.import-btn { display: flex; align-items: center; justify-content: center; gap: 8px; }
.import-btn:disabled { opacity: 0.4; }

.import-result { margin-top: 16px; animation: fadeUp 0.3s ease; }
.import-header { margin-bottom: 10px; }
.import-stats { display: flex; gap: 12px; font-size: 14px; margin-bottom: 8px; }
.stat.success { color: var(--income); font-weight: 600; }
.stat.error { color: var(--expense); font-weight: 600; }

.error-list { display: flex; flex-direction: column; gap: 6px; }
.error-item { display: flex; gap: 8px; padding: 8px 12px; background: var(--expense-bg); border-radius: var(--radius-xs); font-size: 12px; }
.error-idx { color: var(--expense); font-weight: 600; flex-shrink: 0; }
.error-msg { color: var(--text-secondary); word-break: break-all; }

.result-toast {
  position: fixed; bottom: 100px; left: 50%; transform: translateX(-50%);
  padding: 12px 24px; border-radius: 24px; font-size: 14px; font-weight: 500;
  z-index: 300; animation: slideUp 0.3s ease; white-space: nowrap;
}
.result-toast.success { background: var(--income); color: #000; }
.result-toast.error { background: var(--expense); color: #fff; }
</style>

