<template>
  <div class="page ai-page">
    <div class="page-header">
      <span class="back-btn" @click="$router.back()">‹</span>
      <span class="page-title">AI智能记账</span>
      <span style="width: 24px"></span>
    </div>

    <div v-if="isAdmin" class="card">
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
          <span class="config-value">{{ providerLabel(config.provider) }}</span>
        </div>
        <div class="config-row">
          <span class="config-label">模型</span>
          <span class="config-value">{{ config.model || '-' }}</span>
        </div>
        <div class="config-row">
          <span class="config-label">API Key</span>
          <span class="config-value">{{ config.api_key_masked || '未设置' }}</span>
        </div>
        <div class="config-row">
          <span class="config-label">Temperature</span>
          <span class="config-value">{{ config.temperature ?? '-' }}</span>
        </div>
        <div class="config-row">
          <span class="config-label">Max Tokens</span>
          <span class="config-value">{{ config.max_tokens ?? '-' }}</span>
        </div>
        <div class="config-row">
          <span class="config-label">超时时间</span>
          <span class="config-value">{{ config.timeout ? config.timeout + '秒' : '-' }}</span>
        </div>
      </div>
      <div class="config-actions">
        <button class="btn-test" @click="quickTest" :disabled="quickTesting" style="flex: 1">
          {{ quickTesting ? '测试中...' : '测试连接' }}
        </button>
        <button class="btn-outline" @click="openConfigForm" style="flex: 1">
          {{ config?.is_configured ? '修改配置' : '配置API' }}
        </button>
      </div>

      <div v-if="quickTestResult" class="test-result" style="margin-top: 12px">
        <div class="result-header" :class="quickTestResult.success ? 'success' : 'error'">
          {{ quickTestResult.success ? '✅ 连接成功' : '❌ 连接失败' }}
        </div>
        <div class="result-message">{{ quickTestResult.message }}</div>
        <template v-if="quickTestResult.request || quickTestResult.response">
          <div v-if="quickTestResult.request" class="result-section">
            <div class="section-title-row" @click="toggleQuickSection('request')">
              <span>请求信息 (Request)</span>
              <span class="toggle-icon">{{ quickExpanded.request ? '▼' : '▶' }}</span>
            </div>
            <div v-if="quickExpanded.request" class="result-detail">
              <div class="detail-item">
                <span class="detail-label">请求URL</span>
                <code class="detail-value">{{ quickTestResult.request.url }}</code>
              </div>
              <div class="detail-item">
                <span class="detail-label">请求方法</span>
                <code class="detail-value">{{ quickTestResult.request.method }}</code>
              </div>
              <div class="detail-item">
                <span class="detail-label">请求头</span>
                <pre class="detail-pre">{{ formatJson(quickTestResult.request.headers) }}</pre>
              </div>
              <div class="detail-item">
                <span class="detail-label">请求参数</span>
                <pre class="detail-pre">{{ formatJson(quickTestResult.request.body) }}</pre>
              </div>
            </div>
          </div>
          <div v-if="quickTestResult.response" class="result-section">
            <div class="section-title-row" @click="toggleQuickSection('response')">
              <span>响应信息 (Response)</span>
              <span class="toggle-icon">{{ quickExpanded.response ? '▼' : '▶' }}</span>
            </div>
            <div v-if="quickExpanded.response" class="result-detail">
              <div v-if="quickTestResult.response.status_code" class="detail-item">
                <span class="detail-label">状态码</span>
                <code class="detail-value" :class="quickTestResult.response.status_code < 400 ? 'status-ok' : 'status-err'">
                  {{ quickTestResult.response.status_code }}
                </code>
              </div>
              <div v-if="quickTestResult.response.elapsed_ms" class="detail-item">
                <span class="detail-label">耗时</span>
                <code class="detail-value">{{ quickTestResult.response.elapsed_ms }}ms</code>
              </div>
              <div v-if="quickTestResult.response.headers" class="detail-item">
                <span class="detail-label">响应头</span>
                <pre class="detail-pre">{{ formatJson(quickTestResult.response.headers) }}</pre>
              </div>
              <div v-if="quickTestResult.response.body" class="detail-item">
                <span class="detail-label">响应体</span>
                <pre class="detail-pre">{{ formatBody(quickTestResult.response.body) }}</pre>
              </div>
              <div v-if="quickTestResult.response.error" class="detail-item">
                <span class="detail-label">错误信息</span>
                <code class="detail-value status-err">{{ quickTestResult.response.error }}</code>
              </div>
            </div>
          </div>
        </template>
      </div>
    </div>

    <div v-else-if="config" class="card">
      <div class="section-title">AI服务状态</div>
      <div class="config-info">
        <div class="config-row">
          <span class="config-label">状态</span>
          <span class="config-value" :class="{ active: config.is_configured }">
            {{ config.is_configured ? '✅ 可用' : '❌ 不可用' }}
          </span>
        </div>
      </div>
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

    <div v-if="showConfigForm" class="modal-overlay" @click.self="closeConfigForm">
      <div class="form-modal">
        <div class="form-header">
          <span class="close-btn" @click="closeConfigForm">✕</span>
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
          <div v-if="providerModels.length" class="form-field">
            <label>模型选择</label>
            <CustomSelect
              v-model="configForm.model"
              :options="providerModels"
              placeholder="选择模型"
              class="form-input"
            />
            <div class="field-hint">也可在下方手动输入模型名称</div>
          </div>
          <div class="form-field">
            <label>API Key</label>
            <div class="api-key-wrapper">
              <input
                v-model="configForm.api_key"
                :type="showApiKey ? 'text' : 'password'"
                :placeholder="configForm.has_api_key ? configForm.api_key_masked || '已配置，留空保持不变' : '输入API密钥'"
                class="form-input"
              />
              <span class="toggle-visibility" @click="showApiKey = !showApiKey">
                {{ showApiKey ? '🙈' : '👁' }}
              </span>
            </div>
            <div v-if="configForm.has_api_key && !configForm.api_key" class="field-hint">
              已配置API密钥，留空则保持不变
            </div>
          </div>
          <div class="form-field">
            <label>Base URL</label>
            <input v-model="configForm.base_url" type="text" placeholder="API基础URL" class="form-input" />
            <div class="field-hint">OpenAI兼容格式使用 /chat/completions，Anthropic格式使用 /v1/messages</div>
          </div>
          <div class="form-field">
            <label>模型名称</label>
            <input v-model="configForm.model" type="text" placeholder="模型名称" class="form-input" />
          </div>
          <div class="form-field">
            <label>Temperature (0-2)</label>
            <input v-model.number="configForm.temperature" type="number" min="0" max="2" step="0.1" class="form-input" />
          </div>
          <div class="form-field">
            <label>Max Tokens (1-32768)</label>
            <input v-model.number="configForm.max_tokens" type="number" min="1" max="32768" class="form-input" />
          </div>
          <div class="form-field">
            <label>超时时间/秒 (5-120)</label>
            <input v-model.number="configForm.timeout" type="number" min="5" max="120" class="form-input" />
          </div>
          <div class="action-row">
            <button class="btn-outline" @click="testConnection" :disabled="testing" style="flex: 1">
              {{ testing ? '测试中...' : '测试连接' }}
            </button>
            <button class="btn-primary" @click="saveConfig" style="flex: 1">保存</button>
          </div>

          <div v-if="testResult" class="test-result">
            <div class="result-header" :class="testResult.success ? 'success' : 'error'">
              {{ testResult.success ? '✅ 连接成功' : '❌ 连接失败' }}
            </div>
            <div class="result-message">{{ testResult.message }}</div>

            <div v-if="testResult.request" class="result-section">
              <div class="section-title-row" @click="toggleSection('request')">
                <span>请求信息 (Request)</span>
                <span class="toggle-icon">{{ expandedSections.request ? '▼' : '▶' }}</span>
              </div>
              <div v-if="expandedSections.request" class="result-detail">
                <div class="detail-item">
                  <span class="detail-label">请求URL</span>
                  <code class="detail-value">{{ testResult.request.url }}</code>
                </div>
                <div class="detail-item">
                  <span class="detail-label">请求方法</span>
                  <code class="detail-value">{{ testResult.request.method }}</code>
                </div>
                <div class="detail-item">
                  <span class="detail-label">请求头</span>
                  <pre class="detail-pre">{{ formatJson(testResult.request.headers) }}</pre>
                </div>
                <div class="detail-item">
                  <span class="detail-label">请求参数</span>
                  <pre class="detail-pre">{{ formatJson(testResult.request.body) }}</pre>
                </div>
              </div>
            </div>

            <div v-if="testResult.response" class="result-section">
              <div class="section-title-row" @click="toggleSection('response')">
                <span>响应信息 (Response)</span>
                <span class="toggle-icon">{{ expandedSections.response ? '▼' : '▶' }}</span>
              </div>
              <div v-if="expandedSections.response" class="result-detail">
                <div v-if="testResult.response.status_code" class="detail-item">
                  <span class="detail-label">状态码</span>
                  <code class="detail-value" :class="testResult.response.status_code < 400 ? 'status-ok' : 'status-err'">
                    {{ testResult.response.status_code }}
                  </code>
                </div>
                <div v-if="testResult.response.elapsed_ms" class="detail-item">
                  <span class="detail-label">耗时</span>
                  <code class="detail-value">{{ testResult.response.elapsed_ms }}ms</code>
                </div>
                <div v-if="testResult.response.headers" class="detail-item">
                  <span class="detail-label">响应头</span>
                  <pre class="detail-pre">{{ formatJson(testResult.response.headers) }}</pre>
                </div>
                <div v-if="testResult.response.body" class="detail-item">
                  <span class="detail-label">响应体</span>
                  <pre class="detail-pre">{{ formatBody(testResult.response.body) }}</pre>
                </div>
                <div v-if="testResult.response.error" class="detail-item">
                  <span class="detail-label">错误信息</span>
                  <code class="detail-value status-err">{{ testResult.response.error }}</code>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { llmApi } from '@/services'
import CustomSelect from '@/components/CustomSelect.vue'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const isAdmin = computed(() => !!authStore.user?.is_admin)

const providerOptions = [
  { label: 'OpenAI', value: 'openai' },
  { label: 'Anthropic', value: 'anthropic' },
  { label: 'OpenRouter', value: 'openrouter' },
  { label: 'DeepSeek', value: 'deepseek' },
  { label: '通义千问', value: 'qwen' },
  { label: '硅基流动', value: 'siliconflow' },
  { label: 'Groq', value: 'groq' },
  { label: '自定义', value: 'custom' },
]

const providerModelMap = {
  openai: [
    { label: 'GPT-4o', value: 'gpt-4o' },
    { label: 'GPT-4o Mini', value: 'gpt-4o-mini' },
    { label: 'GPT-4 Turbo', value: 'gpt-4-turbo' },
    { label: 'GPT-3.5 Turbo', value: 'gpt-3.5-turbo' },
    { label: 'O1 Mini', value: 'o1-mini' },
    { label: 'O3 Mini', value: 'o3-mini' },
  ],
  anthropic: [
    { label: 'Claude Sonnet 4', value: 'claude-sonnet-4-20250514' },
    { label: 'Claude 3.5 Sonnet', value: 'claude-3-5-sonnet-20241022' },
    { label: 'Claude 3 Haiku', value: 'claude-3-haiku-20240307' },
  ],
  openrouter: [
    { label: 'MiniMax M2.5 (Free)', value: 'minimax/minimax-m2.5:free' },
    { label: 'DeepSeek Chat V3 (Free)', value: 'deepseek/deepseek-chat-v3-0324:free' },
    { label: 'Gemma 3 27B (Free)', value: 'google/gemma-3-27b-it:free' },
    { label: 'Llama 4 Maverick (Free)', value: 'meta-llama/llama-4-maverick:free' },
    { label: 'Qwen3 32B (Free)', value: 'qwen/qwen3-32b:free' },
    { label: 'Tencent HY3 (Free)', value: 'tencent/hy3-preview:free' },
  ],
  deepseek: [
    { label: 'DeepSeek Chat', value: 'deepseek-chat' },
    { label: 'DeepSeek Reasoner', value: 'deepseek-reasoner' },
  ],
  qwen: [
    { label: 'Qwen Plus', value: 'qwen-plus' },
    { label: 'Qwen Turbo', value: 'qwen-turbo' },
    { label: 'Qwen Max', value: 'qwen-max' },
    { label: 'Qwen Long', value: 'qwen-long' },
  ],
  siliconflow: [
    { label: 'DeepSeek V3', value: 'deepseek-ai/DeepSeek-V3' },
    { label: 'DeepSeek R1', value: 'deepseek-ai/DeepSeek-R1' },
    { label: 'Qwen2.5 72B', value: 'Qwen/Qwen2.5-72B-Instruct' },
    { label: 'GLM-4 9B', value: 'THUDM/GLM-4-9B-0414' },
  ],
  groq: [
    { label: 'Llama 3.3 70B', value: 'llama-3.3-70b-versatile' },
    { label: 'Llama 3.1 8B', value: 'llama-3.1-8b-instant' },
    { label: 'Mixtral 8x7B', value: 'mixtral-8x7b-32768' },
  ],
  custom: [],
}

const providerModels = computed(() => {
  return providerModelMap[configForm.value.provider] || []
})

const config = ref(null)
const showConfigForm = ref(false)
const showApiKey = ref(false)
const configForm = ref({
  provider: 'openrouter',
  api_key: '',
  base_url: 'https://openrouter.ai/api/v1',
  model: 'minimax/minimax-m2.5:free',
  temperature: 0.3,
  max_tokens: 1024,
  timeout: 60,
  has_api_key: false,
  api_key_masked: '',
})
const inputText = ref('')
const parsing = ref(false)
const testing = ref(false)
const testResult = ref(null)
const parseResult = ref(null)
const importResult = ref(null)
const expandedSections = ref({ request: true, response: true })
const quickTesting = ref(false)
const quickTestResult = ref(null)
const quickExpanded = ref({ request: false, response: false })

function providerLabel(provider) {
  const map = {
    openai: 'OpenAI',
    anthropic: 'Anthropic',
    openrouter: 'OpenRouter',
    deepseek: 'DeepSeek',
    qwen: '通义千问',
    siliconflow: '硅基流动',
    groq: 'Groq',
    custom: '自定义',
  }
  return map[provider] || provider || '-'
}

async function fetchConfig() {
  try {
    const res = await llmApi.getConfig()
    config.value = res.data.data
  } catch (e) {
    console.error(e)
  }
}

async function openConfigForm() {
  testResult.value = null
  showApiKey.value = false

  const currentConfig = config.value
  if (currentConfig) {
    configForm.value = {
      provider: currentConfig.provider || 'openrouter',
      api_key: '',
      base_url: currentConfig.base_url || '',
      model: currentConfig.model || '',
      temperature: currentConfig.temperature ?? 0.3,
      max_tokens: currentConfig.max_tokens ?? 1024,
      timeout: currentConfig.timeout ?? 60,
      has_api_key: !!currentConfig.api_key_masked,
      api_key_masked: currentConfig.api_key_masked || '',
    }
  }

  try {
    const res = await llmApi.getConfigForEdit()
    const data = res.data.data
    configForm.value = {
      provider: data.provider || 'openrouter',
      api_key: '',
      base_url: data.base_url || '',
      model: data.model || '',
      temperature: data.temperature ?? 0.3,
      max_tokens: data.max_tokens ?? 1024,
      timeout: data.timeout ?? 60,
      has_api_key: data.has_api_key || false,
      api_key_masked: data.api_key_masked || '',
    }
  } catch (e) {
    // already populated from currentConfig above
  }

  showConfigForm.value = true
}

function closeConfigForm() {
  showConfigForm.value = false
  testResult.value = null
}

function onProviderChange() {
  const defaults = {
    openai: { base_url: 'https://api.openai.com/v1', model: 'gpt-4o-mini' },
    anthropic: { base_url: 'https://api.anthropic.com', model: 'claude-sonnet-4-20250514' },
    openrouter: { base_url: 'https://openrouter.ai/api/v1', model: 'minimax/minimax-m2.5:free' },
    deepseek: { base_url: 'https://api.deepseek.com', model: 'deepseek-chat' },
    qwen: { base_url: 'https://dashscope.aliyuncs.com/compatible-mode/v1', model: 'qwen-plus' },
    siliconflow: { base_url: 'https://api.siliconflow.cn/v1', model: 'deepseek-ai/DeepSeek-V3' },
    groq: { base_url: 'https://api.groq.com/openai/v1', model: 'llama-3.3-70b-versatile' },
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
      if (k === 'has_api_key' || k === 'api_key_masked') continue
      if (v !== '' && v !== null && v !== undefined) data[k] = v
    }
    await llmApi.updateConfig(data)
    showConfigForm.value = false
    testResult.value = null
    fetchConfig()
    alert('配置保存成功')
  } catch (e) {
    alert(e.response?.data?.detail || '保存失败')
  }
}

async function testConnection() {
  testing.value = true
  testResult.value = null
  expandedSections.value = { request: true, response: true }
  try {
    const res = await llmApi.testConnection()
    testResult.value = res.data.data
  } catch (e) {
    testResult.value = {
      success: false,
      message: e.response?.data?.detail || '测试请求失败',
      response: { error: e.message || '未知错误' },
    }
  } finally {
    testing.value = false
  }
}

async function quickTest() {
  quickTesting.value = true
  quickTestResult.value = null
  quickExpanded.value = { request: false, response: false }
  try {
    const res = await llmApi.testConnection()
    quickTestResult.value = res.data.data
  } catch (e) {
    quickTestResult.value = {
      success: false,
      message: e.response?.data?.detail || '测试请求失败',
      response: { error: e.message || '未知错误' },
    }
  } finally {
    quickTesting.value = false
  }
}

function toggleSection(section) {
  expandedSections.value[section] = !expandedSections.value[section]
}

function toggleQuickSection(section) {
  quickExpanded.value[section] = !quickExpanded.value[section]
}

function formatJson(obj) {
  if (!obj) return ''
  try {
    if (typeof obj === 'string') return obj
    return JSON.stringify(obj, null, 2)
  } catch {
    return String(obj)
  }
}

function formatBody(body) {
  if (!body) return ''
  try {
    const parsed = JSON.parse(body)
    return JSON.stringify(parsed, null, 2)
  } catch {
    return body
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
  color: var(--text-secondary);
}

.config-value {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
  word-break: break-all;
  text-align: right;
  max-width: 60%;
}

.config-value.active {
  color: var(--success);
}

.config-actions {
  display: flex;
  gap: 10px;
  margin-top: 12px;
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

.btn-test {
  padding: 10px 20px;
  border: 1.5px solid var(--success);
  border-radius: 12px;
  color: var(--success);
  font-size: 14px;
  font-weight: 600;
  background: transparent;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-test:hover {
  background: rgba(76, 175, 80, 0.1);
}

.btn-test:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.form-field {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-bottom: 12px;
}

.form-field label {
  font-size: 13px;
  color: var(--text-secondary);
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
  border-bottom: 0.5px solid var(--border);
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
  color: var(--text-muted);
  font-size: 12px;
}

.result-item {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
}

.result-label {
  font-size: 14px;
  color: var(--text-secondary);
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
  max-width: 420px;
  max-height: 85vh;
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
  color: var(--text-muted);
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
  width: 100%;
  box-sizing: border-box;
}

.form-input:focus {
  border-color: var(--accent);
  outline: none;
}

.api-key-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.api-key-wrapper .form-input {
  padding-right: 40px;
}

.toggle-visibility {
  position: absolute;
  right: 12px;
  cursor: pointer;
  font-size: 16px;
  user-select: none;
}

.field-hint {
  font-size: 11px;
  color: var(--text-muted);
  margin-top: 2px;
}

.test-result {
  margin-top: 16px;
  border: 1.5px solid var(--border);
  border-radius: 12px;
  overflow: hidden;
}

.result-header {
  padding: 12px 16px;
  font-size: 15px;
  font-weight: 700;
}

.result-header.success {
  background: rgba(76, 175, 80, 0.1);
  color: var(--success);
}

.result-header.error {
  background: rgba(244, 67, 54, 0.1);
  color: var(--danger);
}

.result-message {
  padding: 8px 16px;
  font-size: 13px;
  color: var(--text-secondary);
  border-bottom: 1px solid var(--border);
}

.result-section {
  border-bottom: 1px solid var(--border);
}

.result-section:last-child {
  border-bottom: none;
}

.section-title-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 16px;
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
  cursor: pointer;
  user-select: none;
  background: rgba(0, 0, 0, 0.02);
}

.section-title-row:hover {
  background: rgba(0, 0, 0, 0.04);
}

.toggle-icon {
  font-size: 11px;
  color: var(--text-muted);
}

.result-detail {
  padding: 8px 16px 12px;
}

.detail-item {
  margin-bottom: 8px;
}

.detail-item:last-child {
  margin-bottom: 0;
}

.detail-label {
  display: block;
  font-size: 11px;
  font-weight: 600;
  color: var(--text-muted);
  margin-bottom: 4px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.detail-value {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 13px;
  background: rgba(0, 0, 0, 0.04);
  word-break: break-all;
}

.detail-value.status-ok {
  color: var(--success);
  background: rgba(76, 175, 80, 0.1);
}

.detail-value.status-err {
  color: var(--danger);
  background: rgba(244, 67, 54, 0.1);
}

.detail-pre {
  margin: 0;
  padding: 8px 12px;
  border-radius: 8px;
  font-size: 12px;
  line-height: 1.5;
  background: rgba(0, 0, 0, 0.04);
  color: var(--text-primary);
  overflow-x: auto;
  white-space: pre-wrap;
  word-break: break-all;
  max-height: 300px;
  overflow-y: auto;
}
</style>
