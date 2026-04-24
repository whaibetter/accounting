<template>
  <div class="page categories-page">
    <div class="page-header">
      <span class="back-btn" @click="$router.back()">‹</span>
      <span class="page-title">分类管理</span>
      <button class="add-btn" @click="showAddForm = true">新增</button>
    </div>

    <div class="tab-bar">
      <div class="tab-item" :class="{ active: currentType === 1 }" @click="currentType = 1">支出分类</div>
      <div class="tab-item" :class="{ active: currentType === 2 }" @click="currentType = 2">收入分类</div>
    </div>

    <div class="card" style="padding: 4px 16px">
      <div v-for="cat in displayCategories" :key="cat.id" class="cat-mgmt-item">
        <span class="cmi-icon">{{ cat.icon || '📝' }}</span>
        <div class="cmi-info">
          <span class="cmi-name">{{ cat.name }}</span>
          <div v-if="cat.children && cat.children.length" class="sub-cats">
            <span v-for="child in cat.children" :key="child.id" class="sub-cat-tag">
              {{ child.icon || '📝' }} {{ child.name }}
            </span>
          </div>
        </div>
        <div class="cmi-actions">
          <button class="action-btn edit" @click="editCategory(cat)">编辑</button>
          <button class="action-btn delete" @click="deleteCategory(cat.id)">删除</button>
        </div>
      </div>
    </div>

    <div v-if="showAddForm || editingCategory" class="modal-overlay" @click.self="closeForm">
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
          <div v-if="!editingCategory" class="form-field">
            <label>父分类</label>
            <select v-model="form.parent_id" class="form-input">
              <option :value="null">无（顶级分类）</option>
              <option v-for="cat in topLevelCategories" :key="cat.id" :value="cat.id">{{ cat.name }}</option>
            </select>
          </div>
          <button class="btn-primary save-btn" @click="saveCategory">保存</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useCategoryStore } from '@/stores/data'

const categoryStore = useCategoryStore()

const currentType = ref(1)
const showAddForm = ref(false)
const editingCategory = ref(null)
const form = ref({ name: '', icon: '', parent_id: null })

const displayCategories = computed(() => categoryStore.categories.filter(c => c.type === currentType.value))
const topLevelCategories = computed(() => displayCategories.value.filter(c => !c.parent_id))

function editCategory(cat) {
  editingCategory.value = cat
  form.value = { name: cat.name, icon: cat.icon, parent_id: cat.parent_id }
}

function closeForm() {
  showAddForm.value = false
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

async function deleteCategory(id) {
  if (!confirm('确定删除此分类？')) return
  try {
    await categoryStore.deleteCategory(id)
    categoryStore.fetchCategories(currentType.value)
  } catch (e) {
    alert(e.response?.data?.detail || '删除失败')
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

.cat-mgmt-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 0;
  border-bottom: 0.5px solid #f0ece5;
}

.cmi-icon {
  font-size: 24px;
}

.cmi-info {
  flex: 1;
  min-width: 0;
}

.cmi-name {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
}

.sub-cats {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 6px;
}

.sub-cat-tag {
  font-size: 11px;
  color: #888;
  background: var(--bg-tab);
  padding: 2px 8px;
  border-radius: 4px;
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

.form-field {
  display: flex;
  flex-direction: column;
  gap: 6px;
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

.form-input:focus {
  border-color: var(--accent);
}

.save-btn {
  width: 100%;
  margin-top: 8px;
}
</style>
