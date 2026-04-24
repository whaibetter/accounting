<template>
  <div class="page ai-page">
    <div class="page-header">
      <span class="back-btn" @click="$router.back()">‹</span>
      <span class="page-title">AI智能记账</span>
      <span style="width: 24px"></span>
    </div>

    <div class="card">
      <div class="section-title">LLM配置</div>
      <div v-if="config" class="config-info">
        <div class="config-row">
          <span class="config-label">状态</span>
          <span class="config-value" :class="{ active: config.is_configured }">
            {{ config.is_configured ? '✅ 已配置' : '❌ 未配置' }}
          </span>
        </div>
        <div class="config-row">
          <span class="config-label">提供商</span>
          <span class="config-value">{{ config.provider || '-' }}</span>
        </div>
        <div class="config-row">
          <span class="config-label">模型</span>
          <span class="config-value">{{ config.model || '-' }}</span>
        </div>
      </div>
      <button class="btn-outline" @click="showConfigForm = true" style="width: 100%; margin-top: 12px">
        {{ config?.is_configured ? '修改配置' : '配置API' }}
      </button>
    </div>

    <div class="card">
      <div class="section-title">智能记账</div>
      <div class="form-field">
        <label>输入自然语言描述</label>
        <textarea
          v-model="inputText"
          placeholder="例如：今天午饭花了35元，坐地铁6元"
          class="form-textarea"
          rows="3"
        ></textarea>
      </div>
      <div class="action-row">
        <button class="btn-primary" @click="parseText" :disabled="parsing" style="flex: 1">
          {{ parsing ? '解析中...' : '解析' }}
        </button>
        <button
          class="btn-primary"
          @click="parseAndImport"
          :disabled="parsing"
          style="flex: 1; background: linear-gradient(135deg, var(--success), #5ca85c)"
        >
          解析并导入
        </button>
      </div>
    </div>

    <div v-if="parseResult" class="card">
      <div class="section-title">解析结果</div>
      <div v-if="parseResult.bills && parseResult.bills.length">
        <div v-for="(bill, idx) in parseResult.bills" :key="idx" class="parsed-bill">
          <span class="parsed-type">{{ bill.type === 2 ? '收入' : '支出' }}</span>
          <span class="parsed-category">{{ bill.category || '其他' }}</span>
          <span class="parsed-amount">¥{{ bill.amount }}</span>
          <span class="parsed-remark">{{ bill.remark || '' }}</span>
        </div>
      </div>
      <div v-else class="empty-state" style="padding: 20px">
        <div class="text">{{ parseResult.error || '未能解析出有效数据' }}</div>
      </div>
    </div>

    <div v-if="importResult" class="card">
      <div class="section-title">导入结果</div>
      <div class="result-item">
        <span class="result-label">成功导入</span>
        <span class="result-value success">{{ importResult.success || 0 }} 条</span>
      </div>
      <div v-if="importResult.errors && importResult.errors.length" class="error-list">
        <div v-for="(err, idx) in importResult.errors" :key="idx" class="error-item">{{ err }}</div>
      </div>
    </div>

    <div v-if="showConfigForm" class="modal-overlay" @click.self="showConfigForm = false">
      <div class="form-modal">
        <div class="form-header">
          <span class="close-btn" @click="showConfigForm = false">✕</span>
          <span class="form-title">配置LLM API</span>
          <span style="width: 20px"></span>
        </div>
        <div class="form-body">
          <div class="form-field">
            <label>提供商</label>
            <CustomSelect
              v-model="configForm.provider"
              :options="providerOptions"
              placeholder="选择提供商"
              class="form-input"
              @change="onProviderChange"
            />
          </div>
          <div class="form-field">
            <label>API Key</label>
            <input v-model="configForm.api_key" type="password" placeholder="输入API密钥" class="form-input" />
          </div>
          <div class="form-field">
            <label>Base URL</label>
            <input v-model="configForm.base_url" type="text" placeholder="API基础URL" class="form-input" />
          </div>
          <div class="form-field">
            <label>模型</label>
            <input v-model="configForm.model" type="text" placeholder="模型名称" class="form-input" />
          </div>
          <div class="action-row">
            <button class="btn-outline" @click="testConnection" :disabled="testing" style="flex: 1">
              {{ testing ? '测试中...' : '测试连接' }}
            </button>
            <button class="btn-primary" @click="saveConfig" style="flex: 1">保存</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { llmApi } from '@/services'
import CustomSelect from '@/components/CustomSelect.vue'

const providerOptions = [
  { label: 'OpenAI', value: 'openai' },
  { label: 'Anthropic', value: 'anthropic' },
  { label: '自定义', value: 'custom' },
]

const config = ref(null)
const showConfigForm = ref(false)
const configForm = ref({ provider: 'openai', api_key: '', base_url: '', model: '' })
const inputText = ref('')
const parsing = ref(false)
const testing = ref(false)
const parseResult = ref(null)
const importResult = ref(null)

async function fetchConfig() {
  try {
    const res = await llmApi.getConfig()
    config.value = res.data.data
  } catch (e) {
    console.error(e)
  }
}

function onProviderChange() {
  const defaults = {
    openai: { base_url: 'https://api.openai.com/v1', model: 'gpt-4o-mini' },
    anthropic: { base_url: 'https://api.anthropic.com', model: 'claude-3-haiku-20240307' },
    custom: { base_url: '', model: '' },
  }
  const d = defaults[configForm.value.provider] || defaults.custom
  configForm.value.base_url = d.base_url
  configForm.value.model = d.model
}

async function saveConfig() {
  try {
    const data = {}
    for (const [k, v] of Object.entries(configForm.value)) {
      if (v) data[k] = v
    }
    await llmApi.updateConfig(data)
    showConfigForm.value = false
    fetchConfig()
    alert('配置保存成功')
  } catch (e) {
    alert(e.response?.data?.detail || '保存失败')
  }
}

async function testConnection() {
  testing.value = true
  try {
    const res = await llmApi.testConnection()
    const result = res.data.data
    alert(result.success ? '连接成功！' : `连接失败: ${result.message}`)
  } catch (e) {
    alert('测试失败')
  } finally {
    testing.value = false
  }
}

async function parseText() {
  if (!inputText.value.trim()) return
  parsing.value = true
  parseResult.value = null
  importResult.value = null
  try {
    const res = await llmApi.parse(inputText.value)
    parseResult.value = res.data.data
  } catch (e) {
    alert(e.response?.data?.detail || '解析失败')
  } finally {
    parsing.value = false
  }
}

async function parseAndImport() {
  if (!inputText.value.trim()) return
  parsing.value = true
  parseResult.value = null
  importResult.value = null
  try {
    const res = await llmApi.parseAndImport({ text: inputText.value })
    const data = res.data.data
    parseResult.value = data.parse_result
    importResult.value = data.import_result
  } catch (e) {
    alert(e.response?.data?.detail || '操作失败')
  } finally {
    parsing.value = false
  }
}

onMounted(fetchConfig)
</script>

<style scoped>
.back-btn {
  font-size: 22px;
  color: var(--text-primary);
  cursor: pointer;
  width: 24px;
}

.config-info {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.config-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 4px 0;
}

.config-label {
  font-size: 13px;
  color: #777;
}

.config-value {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
}

.config-value.active {
  color: var(--success);
}

.btn-outline {
  padding: 10px 20px;
  border: 1.5px solid var(--accent);
  border-radius: 12px;
  color: var(--accent);
  font-size: 14px;
  font-weight: 600;
  background: transparent;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-outline:hover {
  background: rgba(212, 165, 116, 0.1);
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
  font-size: 14px;
  color: var(--text-primary);
  background: var(--bg-primary);
  resize: vertical;
}

.form-textarea:focus {
  border-color: var(--accent);
}

.action-row {
  display: flex;
  gap: 10px;
}

.parsed-bill {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 0;
  border-bottom: 0.5px solid #f0ece5;
  font-size: 13px;
}

.parsed-type {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 600;
  background: rgba(212, 165, 116, 0.15);
  color: var(--accent);
}

.parsed-category {
  color: var(--text-primary);
  font-weight: 500;
}

.parsed-amount {
  font-weight: 700;
  color: var(--text-primary);
}

.parsed-remark {
  color: #999;
  font-size: 12px;
}

.result-item {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
}

.result-label {
  font-size: 14px;
  color: #777;
}

.result-value {
  font-size: 14px;
  font-weight: 600;
}

.result-value.success {
  color: var(--success);
}

.error-list {
  margin-top: 8px;
}

.error-item {
  font-size: 12px;
  color: var(--danger);
  padding: 4px 0;
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
  max-width: 380px;
  max-height: 80vh;
  overflow-y: auto;
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
</style>
