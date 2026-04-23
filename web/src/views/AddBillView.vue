<template>
  <div class="page add-bill">
    <div class="page-header">
      <button class="back-btn" @click="$router.back()">✕</button>
      <h1>记一笔</h1>
      <div style="width: 36px"></div>
    </div>

    <div class="type-tabs">
      <button
        v-for="t in types"
        :key="t.value"
        class="type-btn"
        :class="{ active: form.type === t.value, expense: t.value === 1, income: t.value === 2 }"
        @click="form.type = t.value"
      >{{ t.label }}</button>
    </div>

    <div class="amount-section">
      <span class="currency">¥</span>
      <input
        type="number"
        class="amount-input"
        v-model="form.amount"
        placeholder="0.00"
        step="0.01"
        ref="amountRef"
      />
    </div>

    <div class="form-section">
      <div class="form-group">
        <label>分类</label>
        <div class="category-grid">
          <button
            v-for="cat in currentCategories"
            :key="cat.id"
            class="cat-btn"
            :class="{ active: form.category_id === cat.id }"
            @click="selectCategory(cat)"
          >
            <span class="cat-icon">{{ iconMap[String(cat.id)] || iconMap[String(Math.floor(cat.id / 10) * 10)] || '📌' }}</span>
            <span class="cat-name">{{ cat.name }}</span>
          </button>
        </div>
      </div>

      <div class="form-group" v-if="subCategories.length">
        <label>子分类</label>
        <div class="category-grid small">
          <button
            v-for="cat in subCategories"
            :key="cat.id"
            class="cat-btn"
            :class="{ active: form.category_id === cat.id }"
            @click="form.category_id = cat.id"
          >
            {{ cat.name }}
          </button>
        </div>
      </div>

      <div class="form-group">
        <label>账户</label>
        <div class="account-row">
          <button
            v-for="acc in store.accounts"
            :key="acc.id"
            class="acc-btn"
            :class="{ active: form.account_id === acc.id }"
            @click="form.account_id = acc.id"
          >{{ acc.name }}</button>
        </div>
      </div>

      <div class="form-group">
        <label>日期</label>
        <input type="date" v-model="form.bill_date" />
      </div>

      <div class="form-group">
        <label>备注</label>
        <input type="text" v-model="form.remark" placeholder="添加备注..." />
      </div>

      <div class="form-group" v-if="store.tags.length">
        <label>标签</label>
        <div class="tag-row">
          <button
            v-for="tag in store.tags"
            :key="tag.id"
            class="tag-btn"
            :class="{ active: form.tag_ids.includes(tag.id) }"
            :style="form.tag_ids.includes(tag.id) ? { background: tag.color + '22', color: tag.color, borderColor: tag.color } : {}"
            @click="toggleTag(tag.id)"
          >{{ tag.name }}</button>
        </div>
      </div>
    </div>

    <button class="btn-primary submit-btn" @click="submit" :disabled="!canSubmit">
      保存
    </button>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { billApi, type Category } from '@/api/types'
import { useDataStore } from '@/stores/data'

const router = useRouter()
const store = useDataStore()
const amountRef = ref<HTMLInputElement | null>(null)

const iconMap: Record<string, string> = {
  '1': '🍜', '2': '🚌', '3': '🛒', '4': '🏠', '5': '🎮',
  '6': '🏥', '7': '📚', '8': '📱', '9': '🎁', '10': '📌',
  '46': '💰', '47': '💼', '48': '📈', '49': '🧧', '50': '↩️', '51': '📌',
}

const types = [
  { label: '支出', value: 1 },
  { label: '收入', value: 2 },
]

const today = new Date().toISOString().slice(0, 10)
const form = ref({
  type: 1,
  amount: '' as any,
  category_id: 0,
  account_id: 0,
  bill_date: today,
  remark: '',
  tag_ids: [] as number[],
})

const currentCategories = computed(() => {
  return form.value.type === 1 ? store.expenseCategories : store.incomeCategories
})

const subCategories = computed(() => {
  const parent = currentCategories.value.find((c) => c.id === form.value.category_id)
  if (parent?.children?.length) return parent.children
  const parentId = Math.floor(form.value.category_id / 10) * 10
  const p = currentCategories.value.find((c) => c.id === parentId)
  return p?.children || []
})

const canSubmit = computed(() => {
  return form.value.amount > 0 && form.value.category_id > 0 && form.value.account_id > 0
})

function selectCategory(cat: Category) {
  form.value.category_id = cat.id
  if (cat.children?.length) {
    form.value.category_id = cat.children[0].id
  }
}

function toggleTag(id: number) {
  const idx = form.value.tag_ids.indexOf(id)
  if (idx >= 0) form.value.tag_ids.splice(idx, 1)
  else form.value.tag_ids.push(id)
}

async function submit() {
  try {
    await billApi.create({
      account_id: form.value.account_id,
      category_id: form.value.category_id,
      type: form.value.type,
      amount: Number(form.value.amount),
      bill_date: form.value.bill_date,
      remark: form.value.remark,
      tag_ids: form.value.tag_ids,
    })
    await store.refreshAccounts()
    router.push('/')
  } catch (e: any) {
    alert(e.message || '保存失败')
  }
}

onMounted(async () => {
  await store.loadAll()
  if (store.accounts.length) form.value.account_id = store.accounts[0].id
  if (store.expenseCategories.length) {
    const first = store.expenseCategories[0]
    form.value.category_id = first.children?.[0]?.id || first.id
  }
  setTimeout(() => amountRef.value?.focus(), 300)
})
</script>

<style scoped>
.back-btn {
  width: 36px; height: 36px; border-radius: 50%; background: var(--bg-card);
  color: var(--text); font-size: 16px; display: flex; align-items: center;
  justify-content: center; border: 1px solid var(--border);
}

.type-tabs { display: flex; gap: 8px; margin-bottom: 24px; }
.type-btn {
  flex: 1; padding: 10px; border-radius: var(--radius-sm); font-weight: 600;
  background: var(--bg-card); color: var(--text-secondary); border: 1px solid var(--border);
}
.type-btn.active.expense { background: var(--expense-bg); color: var(--expense); border-color: var(--expense); }
.type-btn.active.income { background: var(--income-bg); color: var(--income); border-color: var(--income); }

.amount-section {
  display: flex; align-items: center; gap: 8px; margin-bottom: 28px;
  padding: 16px; background: var(--bg-card); border-radius: var(--radius);
  border: 1px solid var(--border);
}
.currency { font-size: 28px; font-weight: 700; color: var(--text-secondary); }
.amount-input {
  flex: 1; font-size: 36px; font-weight: 800; background: none; border: none;
  color: var(--text); letter-spacing: -1px; padding: 0;
  font-variant-numeric: tabular-nums;
}
.amount-input:focus { border: none; outline: none; }

.form-section { display: flex; flex-direction: column; gap: 20px; margin-bottom: 28px; }
.form-group { display: flex; flex-direction: column; gap: 8px; }
.form-group label { font-size: 13px; color: var(--text-secondary); font-weight: 600; letter-spacing: 0.5px; }

.category-grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 8px; }
.category-grid.small { grid-template-columns: repeat(4, 1fr); }
.cat-btn {
  display: flex; flex-direction: column; align-items: center; gap: 4px;
  padding: 10px 4px; border-radius: var(--radius-sm); background: var(--bg-card);
  color: var(--text-secondary); border: 1px solid var(--border); font-size: 12px;
}
.cat-btn.active { background: var(--primary-bg); color: var(--primary-light); border-color: var(--primary); }
.cat-icon { font-size: 22px; }
.cat-name { font-size: 11px; white-space: nowrap; }
.category-grid.small .cat-btn { padding: 8px 4px; }

.account-row { display: flex; gap: 8px; flex-wrap: wrap; }
.acc-btn {
  padding: 8px 16px; border-radius: 20px; background: var(--bg-card);
  color: var(--text-secondary); border: 1px solid var(--border); font-size: 13px;
}
.acc-btn.active { background: var(--primary-bg); color: var(--primary-light); border-color: var(--primary); }

.tag-row { display: flex; gap: 8px; flex-wrap: wrap; }
.tag-btn {
  padding: 6px 14px; border-radius: 20px; background: var(--bg-card);
  color: var(--text-secondary); border: 1px solid var(--border); font-size: 13px;
}

.submit-btn { margin-top: auto; }
.submit-btn:disabled { opacity: 0.4; }
</style>
