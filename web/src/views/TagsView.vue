<template>
  <div class="page tags-page">
    <div class="page-header">
      <span class="back-btn" @click="$router.back()">‹</span>
      <span class="page-title">标签管理</span>
      <button class="add-btn" @click="showAddForm = true">新增</button>
    </div>

    <div class="card">
      <div v-if="tags.length === 0" class="empty-state">
        <div class="icon">🔖</div>
        <div class="text">暂无标签</div>
      </div>
      <div v-for="tag in tags" :key="tag.id" class="tag-item">
        <div class="tag-dot" :style="{ background: tag.color || '#d4a574' }"></div>
        <span class="tag-name">{{ tag.name }}</span>
        <div class="tag-actions">
          <button class="action-btn edit" @click="editTag(tag)">编辑</button>
          <button class="action-btn delete" @click="handleDeleteTag(tag)">删除</button>
        </div>
      </div>
    </div>

    <div v-if="showAddForm || editingTag" class="modal-overlay" @click.self="closeForm">
      <div class="form-modal">
        <div class="form-header">
          <span class="close-btn" @click="closeForm">✕</span>
          <span class="form-title">{{ editingTag ? '编辑标签' : '新增标签' }}</span>
          <span style="width: 20px"></span>
        </div>
        <div class="form-body">
          <div class="form-field">
            <label>标签名称</label>
            <input v-model="form.name" type="text" placeholder="请输入标签名称" class="form-input" />
          </div>
          <div class="form-field">
            <label>颜色</label>
            <div class="color-picker">
              <div
                v-for="color in colorOptions"
                :key="color"
                class="color-option"
                :class="{ active: form.color === color }"
                :style="{ background: color }"
                @click="form.color = color"
              ></div>
            </div>
          </div>
          <button class="btn-primary save-btn" @click="saveTag">保存</button>
        </div>
      </div>
    </div>

    <ConfirmDialog
      ref="confirmDialog"
      icon="🗑️"
      title="确定要删除此标签吗？"
      description="此操作不可撤销，删除后标签数据将永久丢失。"
      confirmText="确认删除"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useTagStore } from '@/stores/data'
import ConfirmDialog from '@/components/ConfirmDialog.vue'

const tagStore = useTagStore()
const confirmDialog = ref(null)

const showAddForm = ref(false)
const editingTag = ref(null)
const form = ref({ name: '', color: '#d4a574' })

const colorOptions = ['#d4a574', '#7cafd4', '#7bc97b', '#d47b7b', '#a07bd4', '#c4b896', '#7b9bd4', '#e8c99a']
const tags = computed(() => tagStore.tags)

function editTag(tag) {
  editingTag.value = tag
  form.value = { name: tag.name, color: tag.color || '#d4a574' }
}

function closeForm() {
  showAddForm.value = false
  editingTag.value = null
  form.value = { name: '', color: '#d4a574' }
}

async function saveTag() {
  if (!form.value.name) {
    alert('请输入标签名称')
    return
  }
  try {
    if (editingTag.value) {
      await tagStore.updateTag(editingTag.value.id, form.value)
    } else {
      await tagStore.createTag(form.value)
    }
    closeForm()
    tagStore.fetchTags()
  } catch (e) {
    alert(e.response?.data?.detail || '保存失败')
  }
}

async function handleDeleteTag(tag) {
  const confirmed = await confirmDialog.value.show()
  if (!confirmed) return
  try {
    await tagStore.deleteTag(tag.id)
    tagStore.fetchTags()
  } catch (e) {
    alert(e.response?.data?.detail || '删除失败')
  }
}

onMounted(() => tagStore.fetchTags())
</script>

<style scoped>
.back-btn {
  font-size: 22px;
  color: var(--text-primary);
  cursor: pointer;
  width: 24px;
}

.add-btn {
  font-size: 14px;
  color: var(--accent);
  font-weight: 600;
}

.tag-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 0;
  border-bottom: 0.5px solid var(--border);
}

.tag-item:last-child {
  border-bottom: none;
}

.tag-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  flex-shrink: 0;
}

.tag-name {
  flex: 1;
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
}

.tag-actions {
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

.color-picker {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.color-option {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  cursor: pointer;
  transition: transform 0.15s;
  border: 3px solid transparent;
}

.color-option.active {
  border-color: var(--text-primary);
  transform: scale(1.1);
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
  color: var(--text-muted);
  cursor: pointer;
}

.form-title {
  font-size: 17px;
  font-weight: 700;
  color: var(--text-primary);
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
  color: var(--text-secondary);
}

.form-input {
  padding: 10px 14px;
  border: 1.5px solid var(--border);
  border-radius: 10px;
  font-size: 14px;
  color: var(--text-primary);
  background: var(--bg-input);
}

.save-btn {
  width: 100%;
  margin-top: 8px;
}
</style>
