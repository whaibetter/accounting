const { getCategories, createCategory, updateCategory, deleteCategory } = require('../../utils/api');

Page({
  data: {
    expenseCats: [],
    incomeCats: [],
    activeTab: 'expense',
    showForm: false,
    isEdit: false,
    editId: null,
    form: { name: '', type: 1, icon: '', parent_id: null },
    parentOptions: [],
    submitting: false,
  },

  onShow() { this.loadData(); },
  onPullDownRefresh() { this.loadData().then(() => wx.stopPullDownRefresh()); },

  async loadData() {
    try {
      const res = await getCategories();
      if (res.code === 200) {
        const all = res.data || [];
        this.setData({
          expenseCats: all.filter(c => c.type === 1),
          incomeCats: all.filter(c => c.type === 2),
        });
      }
    } catch (_) {}
  },

  onTab(e) { this.setData({ activeTab: e.currentTarget.dataset.tab }); },

  onShowForm(e) {
    const { type } = e.currentTarget.dataset;
    const cats = type === 1 ? this.data.expenseCats : this.data.incomeCats;
    this.setData({
      showForm: true, isEdit: false, editId: null,
      form: { name: '', type: parseInt(type), icon: '', parent_id: null },
      parentOptions: cats,
    });
  },

  onEdit(e) {
    const cats = this.data.activeTab === 'expense' ? this.data.expenseCats : this.data.incomeCats;
    const cat = (function find(arr, id) {
      for (const c of arr) { if (c.id === id) return c; if (c.children) { const r = find(c.children, id); if (r) return r; } }
    })(cats, parseInt(e.currentTarget.dataset.id));

    if (cat) {
      const pOpts = cats.filter(c => c.id !== cat.id);
      this.setData({ showForm: true, isEdit: true, editId: cat.id,
        form: { name: cat.name, type: cat.type, icon: cat.icon || '', parent_id: cat.parent_id || null },
        parentOptions: pOpts,
      });
    }
  },

  onFormField(e) { const k = e.currentTarget.dataset.key; this.setData({ [`form.${k}`]: e.detail.value }); },
  onFormParent(e) { this.setData({ 'form.parent_id': parseInt(e.currentTarget.dataset.id) || null }); },

  async onSave() {
    const { form, isEdit, editId } = this.data;
    if (!form.name.trim()) { wx.showToast({ title: '请输入名称', icon: 'none' }); return; }

    const data = { name: form.name.trim(), type: form.type, icon: form.icon || '', parent_id: form.parent_id };
    this.setData({ submitting: true });
    try {
      if (isEdit) await updateCategory(editId, data);
      else await createCategory(data);
      wx.showToast({ title: isEdit ? '已更新' : '已创建', icon: 'success' });
      this.setData({ showForm: false, submitting: false });
      this.loadData();
    } catch (err) {
      wx.showToast({ title: err.message || '失败', icon: 'none' });
      this.setData({ submitting: false });
    }
  },

  async onDelete(e) {
    const r = await wx.showModal({ title: '确认删除', content: '删除后不可恢复' });
    if (r.confirm) {
      try { await deleteCategory(e.currentTarget.dataset.id); wx.showToast({ title: '已删除', icon: 'success' }); this.loadData(); }
      catch (_) { wx.showToast({ title: '删除失败', icon: 'none' }); }
    }
  },
});
