<template>
  <div class="page llm-settings">
    <div class="page-header">
      <button class="back-btn" @click="$router.back()">‹</button>
      <h1>AI 模型设置</h1>
      <div style="width: 36px"></div>
    </div>

    <div class="config-status card" :class="config?.is_configured ? 'configured' : 'not-configured'">
      <span class="status-dot" :class="config?.is_configured ? 'active' : ''"></span>
      <span class="status-text">{{ config?.is_configured ? 'API已配置' : 'API未配置' }}</span>
    </div>

    <div class="form-section">
      <div class="form-group">
        <label>API 提供商</label>
        <div class="provider-grid">
          <button
            v-for="(info, key) in providers"
            :key="key"
            class="provider-btn"
            :class="{ active: form.provider === key }"
            @click="selectProvider(key)"
          >
            <span class="provider-name">{{ info.name }}</span>
          </button>
        </div>
      </div>

      <div class="form-group">
        <label>API 密钥</label>
        <div class="key-input-row">
          <input
            :type="showKey ? 'text' : 'password'"
            v-model="form.api_key"
            :placeholder="config.api_key_masked || '输入API密钥...'"
          />
          <button class="toggle-key" @click="showKey = !showKey">
            {{ showKey ? '🙈' : '👁' }}
          </button>
        </div>
        <div class="hint-text" v-if="form.provider === 'openai'">
          获取密钥: <a href="https://platform.openai.com/api-keys" target="_blank">OpenAI平台</a>
        </div>
        <div class="hint-text" v-else-if="form.provider === 'anthropic'">
          获取密钥: <a href="https://console.anthropic.com/" target="_blank">Anthropic控制台</a>
        </div>
        <div class="hint-text" v-else-if="form.provider === 'openrouter'">
          获取密钥: <a href="https://openrouter.ai/keys" target="_blank">OpenRouter</a> · 免费模型可用
        </div>
      </div>

      <div class="form-group">
        <label>API 地址</label>
        <input
          type="text"
          v-model="form.base_url"
          :placeholder="currentProvider?.default_base_url || '输入API地址...'"
        />
        <div class="hint-text">留空使用默认地址，支持自定义代理地址</div>
      </div>

      <div class="form-group">
        <label>模型</label>
        <div class="model-row" v-if="currentProvider?.models?.length">
          <select v-model="form.model" class="model-select">
            <option value="">自动选择</option>
            <option v-for="m in currentProvider.models" :key="m" :value="m">{{ m }}</option>
            <option value="__custom__">自定义模型...</option>
          </select>
        </div>
        <input
          v-else
          type="text"
          v-model="form.model"
          :placeholder="currentProvider?.default_model || '输入模型名称...'"
        />
        <input
          v-if="form.model === '__custom__'"
          type="text"
          v-model="customModel"
          placeholder="输入自定义模型名称..."
          class="custom-model-input"
        />
      </div>

      <div class="form-group">
        <label>参数配置</label>
        <div class="params-grid">
          <div class="param-item">
            <span class="param-label">Temperature</span>
            <div class="param-control">
              <input type="range" v-model.number="form.temperature" min="0" max="2" step="0.1" />
              <span class="param-value">{{ form.temperature }}</span>
            </div>
          </div>
          <div class="param-item">
            <span class="param-label">Max Tokens</span>
            <div class="param-control">
              <input type="number" v-model.number="form.max_tokens" min="1" max="32768" />
              <span class="param-value">{{ form.max_tokens }}</span>
            </div>
          </div>
          <div class="param-item">
            <span class="param-label">超时(秒)</span>
            <div class="param-control">
              <input type="number" v-model.number="form.timeout" min="5" max="120" />
              <span class="param-value">{{ form.timeout }}s</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="actions">
      <button class="btn-primary" @click="saveConfig" :disabled="saving">
        <span v-if="saving" class="loading-spinner"></span>
        <span v-else>保存配置</span>
      </button>
      <button class="btn-secondary" @click="testConnection" :disabled="testing || !config?.is_configured">
        <span v-if="testing" class="loading-spinner small"></span>
        <span v-else>🔗 测试连接</span>
      </button>
    </div>

    <div class="test-result card" v-if="testResult">
      <div class="test-status" :class="testResult.success ? 'success' : 'error'">
        {{ testResult.success ? '✓' : '✕' }} {{ testResult.message }}
      </div>
    </div>

    <div class="result-toast" v-if="toast.show" :class="toast.type">
      {{ toast.message }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { llmApi, type LlmConfig, type LlmProvider } from '@/api/types'

const config = ref<Partial<LlmConfig>>({
  provider: 'openrouter',
  api_key: '',
  base_url: 'https://openrouter.ai/api/v1',
  model: 'minimax/minimax-m2.5:free',
  temperature: 0.3,
  max_tokens: 1024,
  timeout: 60,
  is_configured: true,
})

const providers = ref<Record<string, LlmProvider>>({})
const showKey = ref(false)
const saving = ref(false)
const testing = ref(false)
const testResult = ref<{ success: boolean; message: string } | null>(null)
const customModel = ref('')
const toast = reactive({ show: false, message: '', type: 'success' })

const form = reactive({
  provider: 'openrouter',
  api_key: '',
  base_url: 'https://openrouter.ai/api/v1',
  model: 'minimax/minimax-m2.5:free',
  temperature: 0.3,
  max_tokens: 1024,
  timeout: 60,
})

const currentProvider = computed(() => providers.value[form.provider])

function showToast(message: string, type: string) {
  toast.message = message
  toast.type = type
  toast.show = true
  setTimeout(() => { toast.show = false }, 2500)
}

function selectProvider(key: string) {
  form.provider = key
  const info = providers.value[key]
  if (info && !form.base_url) {
    form.base_url = ''
  }
  if (info && !form.model) {
    form.model = ''
  }
}

async function loadConfig() {
  try {
    const [configRes, providersRes] = await Promise.all([
      llmApi.getConfig(),
      llmApi.getProviders(),
    ])

    const data = configRes.data || {}
    config.value = { ...config.value, ...data }
    providers.value = providersRes.data || {}

    form.provider = data.provider || 'openrouter'
    form.base_url = data.base_url || ''
    form.model = data.model || ''
    form.temperature = data.temperature ?? 0.3
    form.max_tokens = data.max_tokens ?? 1024
    form.timeout = data.timeout ?? 60
    form.api_key = ''
  } catch (e: any) {
    showToast('加载配置失败: ' + (e.message || ''), 'error')
  }
}

async function saveConfig() {
  saving.value = true
  testResult.value = null

  try {
    const updateData: any = {
      provider: form.provider,
      base_url: form.base_url || undefined,
      temperature: form.temperature,
      max_tokens: form.max_tokens,
      timeout: form.timeout,
    }

    if (form.api_key) {
      updateData.api_key = form.api_key
    }

    let modelValue = form.model
    if (modelValue === '__custom__') {
      modelValue = customModel.value
    }
    if (modelValue) {
      updateData.model = modelValue
    }

    const res = await llmApi.updateConfig(updateData)
    config.value = { ...config.value, ...(res.data || {}) }
    form.api_key = ''

    showToast('配置保存成功', 'success')
  } catch (e: any) {
    showToast('保存失败: ' + (e.message || ''), 'error')
  } finally {
    saving.value = false
  }
}

async function testConnection() {
  testing.value = true
  testResult.value = null

  try {
    const res = await llmApi.testConnection()
    testResult.value = res.data
  } catch (e: any) {
    testResult.value = { success: false, message: e.message || '测试失败' }
  } finally {
    testing.value = false
  }
}

onMounted(loadConfig)
</script>

<style scoped>
.back-btn {
  width: 36px; height: 36px; border-radius: 50%; background: var(--bg-card);
  color: var(--text); font-size: 20px; display: flex; align-items: center;
  justify-content: center; border: 1px solid var(--border);
}

.config-status {
  display: flex; align-items: center; gap: 10px; padding: 14px 16px;
  margin-bottom: 20px;
}
.config-status.configured { border-color: rgba(52, 211, 153, 0.3); }
.config-status.not-configured { border-color: rgba(248, 113, 113, 0.3); }
.status-dot {
  width: 8px; height: 8px; border-radius: 50%; background: var(--text-muted);
}
.status-dot.active { background: var(--income); box-shadow: 0 0 8px rgba(52, 211, 153, 0.5); }
.status-text { font-size: 14px; font-weight: 500; }

.form-section { display: flex; flex-direction: column; gap: 20px; margin-bottom: 24px; }
.form-group { display: flex; flex-direction: column; gap: 8px; }
.form-group label { font-size: 13px; color: var(--text-secondary); font-weight: 600; letter-spacing: 0.5px; }

.provider-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; }
.provider-btn {
  padding: 12px 8px; border-radius: var(--radius-sm); background: var(--bg-card);
  color: var(--text-secondary); border: 1px solid var(--border); text-align: center;
}
.provider-btn.active { background: var(--primary-bg); color: var(--primary-light); border-color: var(--primary); }
.provider-name { font-size: 13px; font-weight: 600; }

.key-input-row { display: flex; gap: 8px; }
.key-input-row input { flex: 1; }
.toggle-key {
  width: 44px; height: 44px; border-radius: var(--radius-sm); background: var(--bg-card);
  display: flex; align-items: center; justify-content: center; font-size: 18px;
  border: 1px solid var(--border); flex-shrink: 0;
}

.hint-text { font-size: 12px; color: var(--text-muted); }
.hint-text a { color: var(--primary-light); }

.model-row { display: flex; gap: 8px; }
.model-select {
  flex: 1; font-size: 14px; padding: 12px 16px;
  background: var(--bg-input); color: var(--text);
  border: 1px solid var(--border); border-radius: var(--radius-sm);
}
.custom-model-input { margin-top: 8px; }

.params-grid { display: flex; flex-direction: column; gap: 14px; }
.param-item { display: flex; flex-direction: column; gap: 4px; }
.param-label { font-size: 12px; color: var(--text-secondary); }
.param-control { display: flex; align-items: center; gap: 10px; }
.param-control input[type="range"] {
  flex: 1; height: 4px; -webkit-appearance: none; background: var(--border);
  border-radius: 2px; border: none; padding: 0;
}
.param-control input[type="range"]::-webkit-slider-thumb {
  -webkit-appearance: none; width: 18px; height: 18px; border-radius: 50%;
  background: var(--primary); cursor: pointer;
}
.param-control input[type="number"] {
  width: 80px; padding: 8px 10px; font-size: 13px;
}
.param-value { font-size: 13px; color: var(--text-secondary); min-width: 40px; text-align: right; }

.actions { display: flex; flex-direction: column; gap: 10px; margin-bottom: 16px; }
.btn-secondary {
  background: var(--bg-card); color: var(--text); padding: 14px 28px;
  border-radius: var(--radius-sm); font-weight: 600; font-size: 16px;
  width: 100%; border: 1px solid var(--border);
  display: flex; align-items: center; justify-content: center; gap: 8px;
}
.btn-secondary:disabled { opacity: 0.4; }
.btn-primary:disabled { opacity: 0.4; display: flex; align-items: center; justify-content: center; gap: 8px; }

.loading-spinner {
  width: 18px; height: 18px; border: 2.5px solid var(--spinner-border);
  border-top-color: var(--spinner-top); border-radius: 50%; animation: spin 0.6s linear infinite;
}
.loading-spinner.small {
  width: 14px; height: 14px; border-color: rgba(255,255,255,0.2);
  border-top-color: var(--text);
}
@keyframes spin { to { transform: rotate(360deg); } }

.test-result { margin-top: 8px; animation: fadeUp 0.3s ease; }
.test-status { font-size: 14px; font-weight: 500; }
.test-status.success { color: var(--income); }
.test-status.error { color: var(--expense); }

.result-toast {
  position: fixed; bottom: 100px; left: 50%; transform: translateX(-50%);
  padding: 12px 24px; border-radius: 24px; font-size: 14px; font-weight: 500;
  z-index: 300; animation: slideUp 0.3s ease; white-space: nowrap;
}
.result-toast.success { background: var(--income); color: #000; }
.result-toast.error { background: var(--expense); color: #fff; }
</style>

