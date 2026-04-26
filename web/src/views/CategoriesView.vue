<template>
  <div class="page categories-page">
    <div class="page-header">
      <span class="back-btn" @click="$router.back()">‹</span>
      <span class="page-title">分类管理</span>
      <button class="add-btn" @click="openAddForm">新增</button>
    </div>

    <div class="tab-bar">
      <div class="tab-item" :class="{ active: currentType === 1 }" @click="currentType = 1">支出分类</div>
      <div class="tab-item" :class="{ active: currentType === 2 }" @click="currentType = 2">收入分类</div>
    </div>

    <div class="card" style="padding: 4px 16px">
      <div v-for="cat in displayCategories" :key="cat.id" class="cat-group">
        <div class="cat-mgmt-item parent" @click="toggleExpand(cat.id)">
          <span class="cmi-icon">{{ getCatIcon(cat.icon) }}</span>
          <div class="cmi-info">
            <span class="cmi-name">{{ cat.name }}</span>
            <span class="cmi-count" v-if="cat.children && cat.children.length">{{ cat.children.length }}个子分类</span>
          </div>
          <span class="expand-arrow" v-if="cat.children && cat.children.length" :class="{ collapsed: !expandedIds.has(cat.id) }">▾</span>
          <div class="cmi-actions" @click.stop>
            <button class="action-btn edit" @click="editCategory(cat)">编辑</button>
            <button class="action-btn delete" @click="handleDeleteCategory(cat)">删除</button>
          </div>
        </div>
        <Transition name="slide">
          <div v-if="cat.children && cat.children.length && expandedIds.has(cat.id)" class="sub-cat-list">
            <div v-for="child in cat.children" :key="child.id" class="cat-mgmt-item child">
              <span class="cmi-icon small">{{ child.icon || '📝' }}</span>
              <div class="cmi-info">
                <span class="cmi-name">{{ child.name }}</span>
              </div>
              <div class="cmi-actions">
                <button class="action-btn edit" @click="editCategory(child)">编辑</button>
                <button class="action-btn delete" @click="handleDeleteCategory(child)">删除</button>
              </div>
            </div>
          </div>
        </Transition>
      </div>
      <div v-if="!displayCategories.length" class="empty-state">
        <div class="icon">📂</div>
        <div class="text">暂无分类</div>
      </div>
    </div>

    <div v-if="showForm" class="modal-overlay" @click.self="closeForm">
      <div class="form-modal">
        <div class="form-header">
          <span class="close-btn" @click="closeForm">✕</span>
          <span class="form-title">{{ editingCategory ? '编辑分类' : '新增分类' }}</span>
          <span style="width: 20px"></span>
        </div>
        <div class="form-body">
          <div class="form-field">
            <label>分类名称</label>
            <input v-model="form.name" type="text" placeholder="请输入分类名称" class="form-input" />
          </div>
          <div class="form-field">
            <label>图标 (Emoji)</label>
            <input v-model="form.icon" type="text" placeholder="如 🍜 🛒 🚌" class="form-input" />
          </div>
          <div class="form-field">
            <label>父分类</label>
            <CustomSelect
              v-model="form.parent_id"
              :options="parentCategoryOptions"
              placeholder="无（顶级分类）"
              class="form-input"
            />
          </div>
          <button class="btn-primary save-btn" @click="saveCategory">保存</button>
        </div>
      </div>
    </div>

    <ConfirmDialog
      ref="confirmDialog"
      :icon="deleteConfirmIcon"
      :title="deleteConfirmTitle"
      :description="deleteConfirmDesc"
      confirmText="确认删除"
    />

    <Transition name="confirm-fade">
      <div v-if="showDeleteOptions" class="modal-overlay" @click="showDeleteOptions = false">
        <div class="delete-options-dialog" @click.stop>
          <div class="do-icon">⚠️</div>
          <div class="do-title">删除「{{ deletingCat?.name }}」</div>
          <div class="do-desc">该分类下有 {{ deletingCat?.children?.length || 0 }} 个子分类，请选择处理方式：</div>
          <div class="do-options">
            <button class="do-btn cascade" @click="doCascadeDelete">
              <span class="do-btn-icon">🗑️</span>
              <div class="do-btn-text">
                <span class="do-btn-title">级联删除</span>
                <span class="do-btn-desc">同时删除所有子分类</span>
              </div>
            </button>
            <button class="do-btn transfer" @click="openTransferDialog">
              <span class="do-btn-icon">↗️</span>
              <div class="do-btn-text">
                <span class="do-btn-title">转移子分类</span>
                <span class="do-btn-desc">将子分类移至其他父分类后删除</span>
              </div>
            </button>
            <button class="do-btn cancel" @click="showDeleteOptions = false">取消</button>
          </div>
        </div>
      </div>
    </Transition>

    <Transition name="confirm-fade">
      <div v-if="showTransferDialog" class="modal-overlay" @click="showTransferDialog = false">
        <div class="transfer-dialog" @click.stop>
          <div class="form-header">
            <span class="close-btn" @click="showTransferDialog = false">✕</span>
            <span class="form-title">转移子分类</span>
            <span style="width: 20px"></span>
          </div>
          <div class="transfer-body">
            <div class="transfer-info">
              将「{{ deletingCat?.name }}」下的 {{ deletingCat?.children?.length || 0 }} 个子分类转移到：
            </div>
            <div class="form-field">
              <label>目标父分类</label>
              <CustomSelect
                v-model="transferTargetId"
                :options="transferTargetOptions"
                placeholder="选择目标父分类"
                class="form-input"
              />
            </div>
            <button class="btn-primary save-btn" @click="doTransferAndDelete" :disabled="!transferTargetId">
              转移并删除
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useCategoryStore } from '@/stores/data'
import CustomSelect from '@/components/CustomSelect.vue'
import ConfirmDialog from '@/components/ConfirmDialog.vue'
import { getCategoryIcon } from '@/utils/format'
import { categoryApi } from '@/services'

const categoryStore = useCategoryStore()
const confirmDialog = ref(null)

const currentType = ref(1)
const showForm = ref(false)
const editingCategory = ref(null)
const form = ref({ name: '', icon: '', parent_id: null })
const expandedIds = ref(new Set())

function toggleExpand(id) {
  if (expandedIds.value.has(id)) {
    expandedIds.value.delete(id)
  } else {
    expandedIds.value.add(id)
  }
  expandedIds.value = new Set(expandedIds.value)
}

const showDeleteOptions = ref(false)
const showTransferDialog = ref(false)
const deletingCat = ref(null)
const transferTargetId = ref(null)

const deleteConfirmIcon = ref('🗑️')
const deleteConfirmTitle = ref('确定要删除此分类吗？')
const deleteConfirmDesc = ref('此操作不可撤销，删除后分类数据将永久丢失。')

const displayCategories = computed(() => categoryStore.categories.filter(c => c.type === currentType.value))
const topLevelCategories = computed(() => displayCategories.value.filter(c => !c.parent_id))

const parentCategoryOptions = computed(() => {
  const options = [{ label: '无（顶级分类）', value: null }]
  const cats = editingCategory.value ? topLevelCategories.value.filter(c => c.id !== editingCategory.value.id) : topLevelCategories.value
  cats.forEach(cat => {
    options.push({ label: cat.name, value: cat.id })
  })
  return options
})

const transferTargetOptions = computed(() => {
  if (!deletingCat.value) return []
  return topLevelCategories.value
    .filter(c => c.id !== deletingCat.value.id)
    .map(c => ({ label: c.name, value: c.id }))
})

function getCatIcon(icon) {
  return getCategoryIcon(icon)
}

function openAddForm() {
  editingCategory.value = null
  form.value = { name: '', icon: '', parent_id: null }
  showForm.value = true
}

function editCategory(cat) {
  editingCategory.value = cat
  form.value = { name: cat.name, icon: cat.icon || '', parent_id: cat.parent_id }
  showForm.value = true
}

function closeForm() {
  showForm.value = false
  editingCategory.value = null
  form.value = { name: '', icon: '', parent_id: null }
}

async function saveCategory() {
  if (!form.value.name) {
    alert('请输入分类名称')
    return
  }
  try {
    if (editingCategory.value) {
      await categoryStore.updateCategory(editingCategory.value.id, {
        name: form.value.name,
        icon: form.value.icon,
        parent_id: form.value.parent_id,
      })
    } else {
      await categoryStore.createCategory({
        name: form.value.name,
        icon: form.value.icon,
        type: form.value.parent_id ? undefined : currentType.value,
        parent_id: form.value.parent_id,
      })
    }
    closeForm()
    categoryStore.fetchCategories(currentType.value)
  } catch (e) {
    alert(e.response?.data?.detail || '保存失败')
  }
}

async function handleDeleteCategory(cat) {
  deletingCat.value = cat

  if (cat.children && cat.children.length > 0) {
    showDeleteOptions.value = true
    return
  }

  deleteConfirmIcon.value = '🗑️'
  deleteConfirmTitle.value = `确定要删除「${cat.name}」吗？`
  deleteConfirmDesc.value = '此操作不可撤销，删除后分类数据将永久丢失。'
  const confirmed = await confirmDialog.value.show()
  if (!confirmed) return

  try {
    await categoryStore.deleteCategory(cat.id)
    categoryStore.fetchCategories(currentType.value)
  } catch (e) {
    alert(e.response?.data?.detail || '删除失败')
  }
}

async function doCascadeDelete() {
  showDeleteOptions.value = false
  const cat = deletingCat.value
  if (!cat) return

  deleteConfirmIcon.value = '⚠️'
  deleteConfirmTitle.value = `确定级联删除「${cat.name}」及其所有子分类吗？`
  deleteConfirmDesc.value = `此操作将同时删除「${cat.name}」及其 ${cat.children.length} 个子分类，此操作不可撤销！`
  const confirmed = await confirmDialog.value.show()
  if (!confirmed) return

  try {
    await categoryApi.delete(cat.id, true)
    categoryStore.fetchCategories(currentType.value)
  } catch (e) {
    alert(e.response?.data?.detail || '删除失败')
  }
}

function openTransferDialog() {
  showDeleteOptions.value = false
  transferTargetId.value = null
  showTransferDialog.value = true
}

async function doTransferAndDelete() {
  if (!transferTargetId.value || !deletingCat.value) return

  const cat = deletingCat.value
  try {
    for (const child of cat.children) {
      await categoryStore.updateCategory(child.id, {
        name: child.name,
        icon: child.icon,
        parent_id: transferTargetId.value,
      })
    }
    await categoryStore.deleteCategory(cat.id)
    showTransferDialog.value = false
    categoryStore.fetchCategories(currentType.value)
  } catch (e) {
    alert(e.response?.data?.detail || '操作失败')
  }
}

watch(currentType, () => categoryStore.fetchCategories(currentType.value))

onMounted(() => categoryStore.fetchCategories(currentType.value))
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

.tab-bar {
  display: flex;
  margin: 0 16px 12px;
  background: var(--bg-tab);
  border-radius: 10px;
  padding: 3px;
}

.tab-item {
  flex: 1;
  text-align: center;
  padding: 8px 0;
  font-size: 14px;
  font-weight: 600;
  color: var(--text-muted);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.tab-item.active {
  background: var(--bg-card);
  color: var(--accent);
  box-shadow: var(--shadow);
}

.cat-group {
  border-bottom: 0.5px solid var(--border);
}

.cat-group:last-child {
  border-bottom: none;
}

.cat-mgmt-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 0;
}

.cat-mgmt-item.parent {
  padding: 14px 0 8px;
}

.cat-mgmt-item.child {
  padding: 10px 0;
}

.cmi-icon {
  font-size: 24px;
  flex-shrink: 0;
}

.cmi-icon.small {
  font-size: 18px;
}

.cmi-info {
  flex: 1;
  min-width: 0;
  display: flex;
  align-items: center;
  gap: 8px;
}

.cmi-name {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
}

.cmi-count {
  font-size: 11px;
  color: var(--text-muted);
  background: var(--bg-tab);
  padding: 1px 6px;
  border-radius: 4px;
}

.expand-arrow {
  font-size: 14px;
  color: var(--text-muted);
  transition: transform 0.25s ease;
  flex-shrink: 0;
}

.expand-arrow.collapsed {
  transform: rotate(-90deg);
}

.sub-cat-list {
  padding-left: 36px;
  border-left: 2px solid var(--border);
  margin-left: 12px;
  overflow: hidden;
}

.slide-enter-active {
  animation: slideDown 0.25s ease;
}

.slide-leave-active {
  animation: slideUp 0.2s ease;
}

@keyframes slideDown {
  from { opacity: 0; max-height: 0; }
  to { opacity: 1; max-height: 500px; }
}

@keyframes slideUp {
  from { opacity: 1; max-height: 500px; }
  to { opacity: 0; max-height: 0; }
}

.cmi-actions {
  display: flex;
  gap: 8px;
  flex-shrink: 0;
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

.empty-state {
  text-align: center;
  padding: 40px 20px;
  color: var(--text-muted);
}

.empty-state .icon {
  font-size: 36px;
  margin-bottom: 8px;
}

.empty-state .text {
  font-size: 14px;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 200;
  padding: 20px;
}

.form-modal, .transfer-dialog {
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

.form-body, .transfer-body {
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
  font-weight: 600;
}

.form-input {
  padding: 10px 14px;
  border: 1.5px solid var(--border);
  border-radius: 10px;
  font-size: 14px;
  color: var(--text-primary);
  background: var(--bg-input);
}

.form-input:focus {
  border-color: var(--accent);
}

.save-btn {
  width: 100%;
  margin-top: 8px;
}

.transfer-info {
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.5;
  padding: 8px 0;
}

.delete-options-dialog {
  background: var(--bg-card);
  border-radius: 16px;
  padding: 28px 24px 24px;
  width: 90%;
  max-width: 360px;
  text-align: center;
}

.do-icon {
  font-size: 40px;
  margin-bottom: 12px;
}

.do-title {
  font-size: 17px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 6px;
}

.do-desc {
  font-size: 13px;
  color: var(--text-muted);
  margin-bottom: 20px;
  line-height: 1.5;
}

.do-options {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.do-btn {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 16px;
  border-radius: 12px;
  cursor: pointer;
  text-align: left;
  transition: all 0.15s;
  border: 1.5px solid var(--border);
  background: var(--bg-card);
}

.do-btn:active {
  transform: scale(0.98);
}

.do-btn.cascade {
  border-color: rgba(212, 123, 123, 0.3);
}

.do-btn.cascade:active {
  background: rgba(212, 123, 123, 0.08);
}

.do-btn.transfer {
  border-color: rgba(212, 165, 116, 0.3);
}

.do-btn.transfer:active {
  background: rgba(212, 165, 116, 0.08);
}

.do-btn.cancel {
  justify-content: center;
  color: var(--text-muted);
  font-size: 14px;
  border-color: transparent;
  background: transparent;
}

.do-btn-icon {
  font-size: 22px;
  flex-shrink: 0;
}

.do-btn-text {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.do-btn-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

.do-btn-desc {
  font-size: 11px;
  color: var(--text-muted);
}

.confirm-fade-enter-active {
  animation: confirmIn 0.2s ease;
}

.confirm-fade-leave-active {
  animation: confirmOut 0.15s ease;
}

@keyframes confirmIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes confirmOut {
  from { opacity: 1; }
  to { opacity: 0; }
}
</style>
