<template>
  <div class="page export-page">
    <div class="page-header">
      <span class="back-btn" @click="$router.back()">‹</span>
      <span class="page-title">数据导出</span>
      <span style="width: 24px"></span>
    </div>

    <div class="card">
      <div class="form-field">
        <label>开始日期</label>
        <input v-model="startDate" type="date" class="form-input" />
      </div>
      <div class="form-field">
        <label>结束日期</label>
        <input v-model="endDate" type="date" class="form-input" />
      </div>
    </div>

    <div class="export-options">
      <button class="export-btn" @click="exportExcel" :disabled="exporting">
        <span class="export-icon">📊</span>
        <div>
          <div class="export-name">导出 Excel</div>
          <div class="export-desc">导出为 .xlsx 格式文件</div>
        </div>
      </button>
      <button class="export-btn" @click="exportJson" :disabled="exporting">
        <span class="export-icon">📄</span>
        <div>
          <div class="export-name">导出 JSON</div>
          <div class="export-desc">导出为 .json 格式文件</div>
        </div>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { exportApi } from '@/services'
import dayjs from 'dayjs'

const startDate = ref(dayjs().startOf('month').format('YYYY-MM-DD'))
const endDate = ref(dayjs().endOf('month').format('YYYY-MM-DD'))
const exporting = ref(false)

function downloadBlob(blob, filename) {
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  a.click()
  URL.revokeObjectURL(url)
}

async function exportExcel() {
  exporting.value = true
  try {
    const res = await exportApi.excel({
      start_date: startDate.value || undefined,
      end_date: endDate.value || undefined,
    })
    downloadBlob(res.data, `accounting_${startDate.value}_${endDate.value}.xlsx`)
  } catch (e) {
    alert('导出失败')
  } finally {
    exporting.value = false
  }
}

async function exportJson() {
  exporting.value = true
  try {
    const res = await exportApi.json({
      start_date: startDate.value || undefined,
      end_date: endDate.value || undefined,
    })
    downloadBlob(res.data, `accounting_${startDate.value}_${endDate.value}.json`)
  } catch (e) {
    alert('导出失败')
  } finally {
    exporting.value = false
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

.form-input {
  padding: 10px 14px;
  border: 1.5px solid var(--border);
  border-radius: 10px;
  font-size: 14px;
  color: var(--text-primary);
  background: var(--bg-primary);
}

.export-options {
  padding: 0 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.export-btn {
  display: flex;
  align-items: center;
  gap: 16px;
  background: var(--bg-card);
  border-radius: var(--radius);
  padding: 20px;
  box-shadow: var(--shadow);
  cursor: pointer;
  transition: transform 0.15s;
  width: 100%;
  text-align: left;
}

.export-btn:active {
  transform: scale(0.98);
}

.export-btn:disabled {
  opacity: 0.6;
}

.export-icon {
  font-size: 32px;
}

.export-name {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

.export-desc {
  font-size: 12px;
  color: var(--text-light);
  margin-top: 2px;
}
</style>
