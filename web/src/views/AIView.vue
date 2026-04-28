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
      </div>
      <div class="config-actions">
        <button class="btn-test" @click="quickTest" :disabled="quickTesting" style="flex: 1">
          {{ quickTesting ? '测试中...' : '测试连接' }}
        </button>
        <button class="btn-outline" @click="openConfigForm" style="flex: 1">
          {{ config?.is_configured ? '修改配置' : '配置API' }}
        </button>
      </div>

      <div v-if="streamPhases.length > 0" class="test-result" style="margin-top: 12px">
        <div class="result-header" :class="finalSuccess === true ? 'success' : finalSuccess === false ? 'error' : 'pending'">
          <span v-if="finalSuccess === true">✅ 连接成功</span>
          <span v-else-if="finalSuccess === false">❌ 连接失败</span>
          <span v-else>⏳ 测试进行中...</span>
        </div>
        <div class="progress-timeline">
          <div v-for="(phase, idx) in streamPhases" :key="idx" class="timeline-item" :class="phaseClass(phase)">
            <div class="timeline-dot"></div>
            <div class="timeline-content">
              <div class="timeline-header">
                <span class="timeline-status">{{ phaseLabel(phase.phase) }}</span>
                <span v-if="phase.timing" class="timeline-time">{{ formatPhaseTime(phase) }}</span>
              </div>
              <div class="timeline-message">{{ phase.message }}</div>
            </div>
          </div>
          <div v-if="quickTesting" class="timeline-item active">
            <div class="timeline-dot pulsing"></div>
            <div class="timeline-content">
              <div class="timeline-header">
                <span class="timeline-status">等待响应</span>
              </div>
              <div class="timeline-message">正在等待服务器返回数据...</div>
            </div>
          </div>
        </div>
        <template v-if="streamRequest || streamResponse">
          <div v-if="streamRequest" class="result-section">
            <div class="section-title-row" @click="toggleQuickSection('request')">
              <span>请求信息 (Request)</span>
              <span class="toggle-icon">{{ quickExpanded.request ? '▼' : '▶' }}</span>
            </div>
            <div v-if="quickExpanded.request" class="result-detail">
              <div class="detail-item">
                <span class="detail-label">请求URL</span>
                <code class="detail-value">{{ streamRequest.url }}</code>
              </div>
              <div class="detail-item">
                <span class="detail-label">请求方法</span>
                <code class="detail-value">{{ streamRequest.method }}</code>
              </div>
              <div class="detail-item">
                <span class="detail-label">请求头</span>
                <pre class="detail-pre">{{ formatJson(streamRequest.headers) }}</pre>
              </div>
              <div class="detail-item">
                <span class="detail-label">请求参数</span>
                <pre class="detail-pre">{{ formatJson(streamRequest.body) }}</pre>
              </div>
            </div>
          </div>
          <div v-if="streamResponse" class="result-section">
            <div class="section-title-row" @click="toggleQuickSection('response')">
              <span>响应信息 (Response)</span>
              <span class="toggle-icon">{{ quickExpanded.response ? '▼' : '▶' }}</span>
            </div>
            <div v-if="quickExpanded.response" class="result-detail">
              <div v-if="streamResponse.status_code" class="detail-item">
                <span class="detail-label">状态码</span>
                <code class="detail-value" :class="streamResponse.status_code < 400 ? 'status-ok' : 'status-err'">
                  {{ streamResponse.status_code }}
                </code>
              </div>
              <div v-if="streamTiming" class="detail-item">
                <span class="detail-label">时间统计</span>
                <div class="timing-grid">
                  <div v-if="streamTiming.connect_elapsed_ms" class="timing-item">
                    <span class="timing-label">连接耗时</span>
                    <span class="timing-value">{{ streamTiming.connect_elapsed_ms }}ms</span>
                  </div>
                  <div v-if="streamTiming.transfer_elapsed_ms" class="timing-item">
                    <span class="timing-label">传输耗时</span>
                    <span class="timing-value">{{ streamTiming.transfer_elapsed_ms }}ms</span>
                  </div>
                  <div v-if="streamTiming.total_elapsed_ms" class="timing-item">
                    <span class="timing-label">总耗时</span>
                    <span class="timing-value highlight">{{ streamTiming.total_elapsed_ms }}ms</span>
                  </div>
                </div>
              </div>
              <div v-if="streamResponse.headers" class="detail-item">
                <span class="detail-label">响应头</span>
                <pre class="detail-pre">{{ formatJson(streamResponse.headers) }}</pre>
              </div>
              <div v-if="streamResponse.body" class="detail-item">
                <span class="detail-label">响应体</span>
                <pre class="detail-pre">{{ formatBody(streamResponse.body) }}</pre>
              </div>
              <div v-if="streamResponse.error" class="detail-item">
                <span class="detail-label">错误信息</span>
                <code class="detail-value status-err">{{ streamResponse.error }}</code>
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
        <textarea v-model="inputText" placeholder="例如：今天午饭花了35元，坐地铁6元" class="form-textarea" rows="3"></textarea>
      </div>
      <div class="action-row">
        <button class="btn-primary" @click="parseText" :disabled="parsing" style="flex: 1">
          {{ parsing ? '解析中...' : '解析' }}
        </button>
        <button class="btn-primary" @click="parseAndImport" :disabled="parsing" style="flex: 1; background: linear-gradient(135deg, var(--success), #5ca85c)">
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
            <label>已保存的配置</label>
            <div v-if="savedProviders.length" class="saved-providers">
              <div v-for="sp in savedProviders" :key="sp.name" class="saved-provider-chip" @click="loadSavedProvider(sp.name)">
                <span class="chip-name">{{ sp.name }}</span>
                <span class="chip-model">{{ sp.model || '-' }}</span>
                <span class="chip-delete" @click.stop="deleteSavedProvider(sp.name)">✕</span>
              </div>
            </div>
            <div v-else class="field-hint">暂无已保存的配置，配置后可保存以便快速切换</div>
          </div>

          <div class="form-field">
            <label>API协议</label>
            <CustomSelect v-model="configForm.protocol" :options="protocolOptions" placeholder="选择协议" class="form-input" />
            <div class="field-hint">OpenAI兼容格式适用于大多数提供商，Anthropic格式仅用于Claude</div>
          </div>

          <div class="form-field">
            <label>API Key</label>
            <div class="api-key-wrapper">
              <input v-model="configForm.api_key" :type="showApiKey ? 'text' : 'password'" :placeholder="configForm.has_api_key ? configForm.api_key_masked || '已配置，留空保持不变' : '输入API密钥'" class="form-input" />
              <span class="toggle-visibility" @click="showApiKey = !showApiKey">{{ showApiKey ? '🙈' : '👁' }}</span>
            </div>
            <div v-if="configForm.has_api_key && !configForm.api_key" class="field-hint">已配置API密钥，留空则保持不变</div>
          </div>

          <div class="form-field">
            <label>Base URL</label>
            <input v-model="configForm.base_url" type="text" placeholder="例如: https://api.openai.com/v1" class="form-input" />
            <div class="field-hint">OpenAI协议追加 /chat/completions，Anthropic协议追加 /v1/messages</div>
          </div>

          <div class="form-field">
            <label>模型名称</label>
            <input v-model="configForm.model" type="text" placeholder="例如: gpt-4o-mini" class="form-input" />
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
            <button class="btn-outline" @click="testConnectionInForm" :disabled="testing" style="flex: 1">
              {{ testing ? '测试中...' : '测试连接' }}
            </button>
            <button class="btn-primary" @click="saveConfig" style="flex: 1">保存</button>
          </div>

          <div class="form-field">
            <label>保存为预设配置</label>
            <div class="save-preset-row">
              <input v-model="presetName" type="text" placeholder="输入配置名称" class="form-input" style="flex: 1" />
              <button class="btn-small" @click="saveAsPreset" :disabled="!presetName.trim()">保存预设</button>
            </div>
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
                <div class="detail-item"><span class="detail-label">请求URL</span><code class="detail-value">{{ testResult.request.url }}</code></div>
                <div class="detail-item"><span class="detail-label">请求方法</span><code class="detail-value">{{ testResult.request.method }}</code></div>
                <div class="detail-item"><span class="detail-label">请求头</span><pre class="detail-pre">{{ formatJson(testResult.request.headers) }}</pre></div>
                <div class="detail-item"><span class="detail-label">请求参数</span><pre class="detail-pre">{{ formatJson(testResult.request.body) }}</pre></div>
              </div>
            </div>
            <div v-if="testResult.response" class="result-section">
              <div class="section-title-row" @click="toggleSection('response')">
                <span>响应信息 (Response)</span>
                <span class="toggle-icon">{{ expandedSections.response ? '▼' : '▶' }}</span>
              </div>
              <div v-if="expandedSections.response" class="result-detail">
                <div v-if="testResult.response.status_code" class="detail-item"><span class="detail-label">状态码</span><code class="detail-value" :class="testResult.response.status_code < 400 ? 'status-ok' : 'status-err'">{{ testResult.response.status_code }}</code></div>
                <div v-if="testResult.response.elapsed_ms" class="detail-item"><span class="detail-label">耗时</span><code class="detail-value">{{ testResult.response.elapsed_ms }}ms</code></div>
                <div v-if="testResult.response.headers" class="detail-item"><span class="detail-label">响应头</span><pre class="detail-pre">{{ formatJson(testResult.response.headers) }}</pre></div>
                <div v-if="testResult.response.body" class="detail-item"><span class="detail-label">响应体</span><pre class="detail-pre">{{ formatBody(testResult.response.body) }}</pre></div>
                <div v-if="testResult.response.error" class="detail-item"><span class="detail-label">错误信息</span><code class="detail-value status-err">{{ testResult.response.error }}</code></div>
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

const protocolOptions = [
  { label: 'OpenAI 兼容格式', value: 'openai' },
  { label: 'Anthropic 格式', value: 'anthropic' },
]

const config = ref(null)
const showConfigForm = ref(false)
const showApiKey = ref(false)
const configForm = ref({
  provider: 'custom',
  protocol: 'openai',
  api_key: '',
  base_url: '',
  model: '',
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
const presetName = ref('')
const savedProviders = ref([])

const quickTesting = ref(false)
const streamPhases = ref([])
const streamRequest = ref(null)
const streamResponse = ref(null)
const streamTiming = ref(null)
const finalSuccess = ref(null)
const quickExpanded = ref({ request: false, response: false })

function providerLabel(provider) {
  const map = {
    openai: 'OpenAI', anthropic: 'Anthropic', openrouter: 'OpenRouter',
    deepseek: 'DeepSeek', qwen: '通义千问', siliconflow: '硅基流动',
    groq: 'Groq', nvidia: 'NVIDIA NIM', custom: '自定义',
  }
  return map[provider] || provider || '-'
}

function phaseLabel(phase) {
  const map = { init: '初始化', request_prepared: '请求已构建', connecting: '连接中', response_received: '已收到响应', completed: '已完成', error: '出错' }
  return map[phase] || phase
}

function phaseClass(phase) {
  if (phase.phase === 'error') return 'error'
  if (phase.phase === 'completed') return phase.success ? 'success' : 'error'
  return 'done'
}

function formatPhaseTime(phase) {
  const t = phase.timing
  if (!t) return ''
  if (t.total_elapsed_ms) return `${t.total_elapsed_ms}ms`
  if (t.connect_elapsed_ms) return `${t.connect_elapsed_ms}ms`
  return ''
}

async function fetchConfig() {
  try {
    const res = await llmApi.getConfig()
    config.value = res.data.data
  } catch (e) {
    console.error(e)
  }
}

async function fetchSavedProviders() {
  try {
    const res = await llmApi.getSavedProviders()
    savedProviders.value = res.data.data || []
  } catch (e) {
    savedProviders.value = []
  }
}

async function openConfigForm() {
  testResult.value = null
  showApiKey.value = false
  presetName.value = ''

  const currentConfig = config.value
  if (currentConfig) {
    configForm.value = {
      provider: currentConfig.provider || 'custom',
      protocol: currentConfig.protocol || 'openai',
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
      provider: data.provider || 'custom',
      protocol: data.protocol || 'openai',
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
    // already populated from currentConfig
  }

  fetchSavedProviders()
  showConfigForm.value = true
}

function closeConfigForm() {
  showConfigForm.value = false
  testResult.value = null
}

async function loadSavedProvider(name) {
  try {
    const res = await llmApi.loadProviderConfig(name)
    const data = res.data.data
    configForm.value = {
      provider: data.provider || 'custom',
      protocol: data.protocol || 'openai',
      api_key: data.api_key || '',
      base_url: data.base_url || '',
      model: data.model || '',
      temperature: data.temperature ?? 0.3,
      max_tokens: data.max_tokens ?? 1024,
      timeout: data.timeout ?? 60,
      has_api_key: data.has_api_key || false,
      api_key_masked: data.api_key_masked || '',
    }
    testResult.value = null
  } catch (e) {
    alert(e.response?.data?.detail || '加载配置失败')
  }
}

async function deleteSavedProvider(name) {
  if (!confirm(`确定删除配置 "${name}" 吗？`)) return
  try {
    await llmApi.deleteProviderConfig(name)
    fetchSavedProviders()
  } catch (e) {
    alert('删除失败')
  }
}

async function saveAsPreset() {
  if (!presetName.value.trim()) return
  try {
    await llmApi.saveProviderConfig({
      name: presetName.value.trim(),
      provider: configForm.value.provider || 'custom',
      protocol: configForm.value.protocol || 'openai',
      api_key: configForm.value.api_key || undefined,
      base_url: configForm.value.base_url,
      model: configForm.value.model,
      temperature: configForm.value.temperature,
      max_tokens: configForm.value.max_tokens,
      timeout: configForm.value.timeout,
    })
    presetName.value = ''
    fetchSavedProviders()
    alert('预设配置保存成功')
  } catch (e) {
    alert('保存失败')
  }
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

async function testConnectionInForm() {
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
  streamPhases.value = []
  streamRequest.value = null
  streamResponse.value = null
  streamTiming.value = null
  finalSuccess.value = null
  quickExpanded.value = { request: false, response: false }

  try {
    await llmApi.testConnectionStream((event) => {
      streamPhases.value = [...streamPhases.value, event]
      if (event.phase === 'request_prepared' && event.request) {
        streamRequest.value = event.request
      }
      if (event.phase === 'completed') {
        streamResponse.value = event.response
        streamTiming.value = event.timing
        finalSuccess.value = event.success
      }
      if (event.phase === 'error') {
        streamResponse.value = event.response
        streamTiming.value = event.timing
        finalSuccess.value = false
      }
    })
  } catch (e) {
    streamPhases.value = [...streamPhases.value, { phase: 'error', message: e.message || 'SSE连接失败' }]
    finalSuccess.value = false
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
  } catch { return String(obj) }
}

function formatBody(body) {
  if (!body) return ''
  try {
    const parsed = JSON.parse(body)
    return JSON.stringify(parsed, null, 2)
  } catch { return body }
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
.back-btn { font-size: 22px; color: var(--text-primary); cursor: pointer; width: 24px; }
.config-info { display: flex; flex-direction: column; gap: 8px; }
.config-row { display: flex; justify-content: space-between; align-items: center; padding: 4px 0; }
.config-label { font-size: 13px; color: var(--text-secondary); }
.config-value { font-size: 13px; font-weight: 600; color: var(--text-primary); word-break: break-all; text-align: right; max-width: 60%; }
.config-value.active { color: var(--success); }
.config-actions { display: flex; gap: 10px; margin-top: 12px; }

.btn-outline { padding: 10px 20px; border: 1.5px solid var(--accent); border-radius: 12px; color: var(--accent); font-size: 14px; font-weight: 600; background: transparent; cursor: pointer; transition: all 0.2s; }
.btn-outline:hover { background: rgba(212, 165, 116, 0.1); }
.btn-test { padding: 10px 20px; border: 1.5px solid var(--success); border-radius: 12px; color: var(--success); font-size: 14px; font-weight: 600; background: transparent; cursor: pointer; transition: all 0.2s; }
.btn-test:hover { background: rgba(76, 175, 80, 0.1); }
.btn-test:disabled { opacity: 0.6; cursor: not-allowed; }
.btn-small { padding: 8px 16px; border: none; border-radius: 8px; color: #fff; font-size: 13px; font-weight: 600; background: var(--accent); cursor: pointer; white-space: nowrap; }
.btn-small:disabled { opacity: 0.5; cursor: not-allowed; }

.form-field { display: flex; flex-direction: column; gap: 6px; margin-bottom: 12px; }
.form-field label { font-size: 13px; color: var(--text-secondary); font-weight: 500; }
.form-textarea { padding: 10px 14px; border: 1.5px solid var(--border); border-radius: 10px; font-size: 14px; color: var(--text-primary); background: var(--bg-primary); resize: vertical; }
.form-textarea:focus { border-color: var(--accent); }
.action-row { display: flex; gap: 10px; }

.saved-providers { display: flex; flex-wrap: wrap; gap: 8px; }
.saved-provider-chip { display: flex; align-items: center; gap: 6px; padding: 6px 12px; border-radius: 20px; background: rgba(212, 165, 116, 0.12); border: 1px solid rgba(212, 165, 116, 0.3); cursor: pointer; transition: all 0.2s; }
.saved-provider-chip:hover { background: rgba(212, 165, 116, 0.2); border-color: var(--accent); }
.chip-name { font-size: 13px; font-weight: 600; color: var(--accent); }
.chip-model { font-size: 11px; color: var(--text-muted); max-width: 100px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.chip-delete { font-size: 12px; color: var(--text-muted); cursor: pointer; padding: 0 2px; }
.chip-delete:hover { color: var(--danger); }

.save-preset-row { display: flex; gap: 8px; }

.parsed-bill { display: flex; align-items: center; gap: 10px; padding: 8px 0; border-bottom: 0.5px solid var(--border); font-size: 13px; }
.parsed-type { padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 600; background: rgba(212, 165, 116, 0.15); color: var(--accent); }
.parsed-category { color: var(--text-primary); font-weight: 500; }
.parsed-amount { font-weight: 700; color: var(--text-primary); }
.parsed-remark { color: var(--text-muted); font-size: 12px; }
.result-item { display: flex; justify-content: space-between; padding: 8px 0; }
.result-label { font-size: 14px; color: var(--text-secondary); }
.result-value { font-size: 14px; font-weight: 600; }
.result-value.success { color: var(--success); }
.error-list { margin-top: 8px; }
.error-item { font-size: 12px; color: var(--danger); padding: 4px 0; }

.modal-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0, 0, 0, 0.4); display: flex; align-items: center; justify-content: center; z-index: 200; padding: 20px; }
.form-modal { background: var(--bg-card); border-radius: 20px; padding: 24px; width: 100%; max-width: 440px; max-height: 85vh; overflow-y: auto; }
.form-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px; }
.close-btn { font-size: 18px; color: var(--text-muted); cursor: pointer; }
.form-title { font-size: 17px; font-weight: 700; }
.form-body { display: flex; flex-direction: column; gap: 4px; }

.form-input { padding: 10px 14px; border: 1.5px solid var(--border); border-radius: 10px; font-size: 14px; color: var(--text-primary); background: var(--bg-primary); width: 100%; box-sizing: border-box; }
.form-input:focus { border-color: var(--accent); outline: none; }

.api-key-wrapper { position: relative; display: flex; align-items: center; }
.api-key-wrapper .form-input { padding-right: 40px; }
.toggle-visibility { position: absolute; right: 12px; cursor: pointer; font-size: 16px; user-select: none; }
.field-hint { font-size: 11px; color: var(--text-muted); margin-top: 2px; }

.test-result { margin-top: 16px; border: 1.5px solid var(--border); border-radius: 12px; overflow: hidden; }
.result-header { padding: 12px 16px; font-size: 15px; font-weight: 700; }
.result-header.success { background: rgba(76, 175, 80, 0.1); color: var(--success); }
.result-header.error { background: rgba(244, 67, 54, 0.1); color: var(--danger); }
.result-header.pending { background: rgba(33, 150, 243, 0.1); color: #2196f3; }
.result-message { padding: 8px 16px; font-size: 13px; color: var(--text-secondary); border-bottom: 1px solid var(--border); }

.progress-timeline { padding: 12px 16px; border-bottom: 1px solid var(--border); }
.timeline-item { display: flex; gap: 12px; padding: 6px 0; position: relative; }
.timeline-item:not(:last-child)::after { content: ''; position: absolute; left: 5px; top: 22px; bottom: -6px; width: 2px; background: var(--border); }
.timeline-item.done .timeline-dot { background: var(--success); }
.timeline-item.success .timeline-dot { background: var(--success); }
.timeline-item.error .timeline-dot { background: var(--danger); }
.timeline-item.active .timeline-dot { background: #2196f3; }
.timeline-dot { width: 12px; height: 12px; border-radius: 50%; flex-shrink: 0; margin-top: 3px; background: var(--text-muted); }
.timeline-dot.pulsing { animation: pulse 1.5s infinite; }
@keyframes pulse { 0%, 100% { opacity: 1; transform: scale(1); } 50% { opacity: 0.5; transform: scale(1.3); } }
.timeline-content { flex: 1; min-width: 0; }
.timeline-header { display: flex; justify-content: space-between; align-items: center; gap: 8px; }
.timeline-status { font-size: 13px; font-weight: 600; color: var(--text-primary); }
.timeline-time { font-size: 11px; color: var(--text-muted); white-space: nowrap; }
.timeline-message { font-size: 12px; color: var(--text-secondary); margin-top: 2px; }

.timing-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: 8px; }
.timing-item { display: flex; flex-direction: column; padding: 6px 10px; border-radius: 8px; background: rgba(0, 0, 0, 0.03); }
.timing-label { font-size: 11px; color: var(--text-muted); }
.timing-value { font-size: 14px; font-weight: 700; color: var(--text-primary); }
.timing-value.highlight { color: var(--accent); }

.result-section { border-bottom: 1px solid var(--border); }
.result-section:last-child { border-bottom: none; }
.section-title-row { display: flex; justify-content: space-between; align-items: center; padding: 10px 16px; font-size: 13px; font-weight: 600; color: var(--text-primary); cursor: pointer; user-select: none; background: rgba(0, 0, 0, 0.02); }
.section-title-row:hover { background: rgba(0, 0, 0, 0.04); }
.toggle-icon { font-size: 11px; color: var(--text-muted); }
.result-detail { padding: 8px 16px 12px; }
.detail-item { margin-bottom: 8px; }
.detail-item:last-child { margin-bottom: 0; }
.detail-label { display: block; font-size: 11px; font-weight: 600; color: var(--text-muted); margin-bottom: 4px; text-transform: uppercase; letter-spacing: 0.5px; }
.detail-value { display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 13px; background: rgba(0, 0, 0, 0.04); word-break: break-all; }
.detail-value.status-ok { color: var(--success); background: rgba(76, 175, 80, 0.1); }
.detail-value.status-err { color: var(--danger); background: rgba(244, 67, 54, 0.1); }
.detail-pre { margin: 0; padding: 8px 12px; border-radius: 8px; font-size: 12px; line-height: 1.5; background: rgba(0, 0, 0, 0.04); color: var(--text-primary); overflow-x: auto; white-space: pre-wrap; word-break: break-all; max-height: 300px; overflow-y: auto; }
</style>
