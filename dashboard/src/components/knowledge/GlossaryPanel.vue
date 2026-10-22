<template>
  <div class="glossary-container">
    <!-- 头部控制栏 -->
    <div class="glossary-header-card">
      <div class="header-top-row">
        <div class="title-box">
          <span class="g-icon">📖</span>
          <span class="g-title">专有名词 & API 速查词典</span>
          <span class="g-count">收录 {{ glossaryData?.total || 0 }} 条概念</span>
        </div>

        <button class="btn btn-primary" @click="showAddModal = true">
          + 随手记新术语 / API
        </button>
      </div>

      <!-- 搜索与分类过滤器 -->
      <div class="filter-controls">
        <div class="search-box">
          <span class="search-icon">🔍</span>
          <input
            type="text"
            v-model="searchQuery"
            class="search-input"
            placeholder="搜索 API 或术语（如：maximum、view、Logit、mAP、PTQ）..."
          />
          <button v-if="searchQuery" class="clear-btn" @click="searchQuery = ''">✕</button>
        </div>

        <div class="category-tabs">
          <button
            :class="['cat-tab', selectedCat === 'all' ? 'active' : '']"
            @click="selectedCat = 'all'"
          >
            全部 ({{ allItems.length }})
          </button>
          <button
            v-for="(cat, idx) in glossaryData?.categories"
            :key="idx"
            :class="['cat-tab', selectedCat === cat.name ? 'active' : '']"
            @click="selectedCat = cat.name"
          >
            {{ cat.name }} ({{ cat.items.length }})
          </button>
        </div>
      </div>
    </div>

    <!-- 术语卡片网格 -->
    <div class="terms-grid">
      <div
        v-for="(item, idx) in filteredItems"
        :key="idx"
        class="term-card"
      >
        <div class="term-head">
          <h3 class="term-name" v-html="renderInline(item.term)"></h3>
          <span class="term-cat-badge">{{ item.parentCat }}</span>
        </div>

        <!-- 详细解析 -->
        <div class="term-content" v-html="renderMarkdown(item.raw)"></div>
      </div>

      <div v-if="filteredItems.length === 0" class="empty-state">
        <span>🔍 没有找到匹配「{{ searchQuery }}」的术语</span>
      </div>
    </div>

    <!-- 新增术语 Modal -->
    <div v-if="showAddModal" class="modal-overlay" @click.self="showAddModal = false">
      <div class="modal-card">
        <div class="m-head">
          <h3>+ 记录新专有名词 / API 对比</h3>
          <button class="close-x" @click="showAddModal = false">✕</button>
        </div>

        <div class="m-body">
          <div class="form-group">
            <label>分类板块</label>
            <input
              type="text"
              v-model="newCat"
              placeholder="例：NumPy 与张量运算、模型评估指标、PyTorch 算子"
              class="form-input"
            />
          </div>

          <div class="form-group">
            <label>专有名词 / API 名称</label>
            <input
              type="text"
              v-model="newTerm"
              placeholder="例：np.maximum(a, b) vs np.max(a, axis=...)"
              class="form-input"
            />
          </div>

          <div class="form-group">
            <label>核心区别 / 概念解析</label>
            <textarea
              v-model="newDiff"
              placeholder="用通俗的语言写下两者的核心差异、作用与典型用法..."
              class="form-textarea"
              rows="4"
            ></textarea>
          </div>

          <div class="form-group">
            <label>示例代码（可选，支持 Python）</label>
            <textarea
              v-model="newCode"
              placeholder="import numpy as np&#10;# 示例验证代码..."
              class="form-textarea code-font"
              rows="4"
            ></textarea>
          </div>
        </div>

        <div class="m-foot">
          <button class="btn btn-outline" @click="showAddModal = false">取消</button>
          <button class="btn btn-primary" :disabled="submitting" @click="saveNewTerm">
            {{ submitting ? '保存中...' : '保存到速查词典' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue';
import { fetchGlossary as loadGlossary, saveGlossaryTerm } from '../../api';
import { renderMarkdown } from '../../utils/markdown';
import Prism from 'prismjs';

const emit = defineEmits(['toast']);

const glossaryData = ref(null);
const searchQuery = ref('');
const selectedCat = ref('all');
const showAddModal = ref(false);
const submitting = ref(false);

const newCat = ref('一、NumPy 与张量运算');
const newTerm = ref('');
const newDiff = ref('');
const newCode = ref('');

const fetchGlossary = async () => {
  try {
    glossaryData.value = await loadGlossary();
    nextTick(() => Prism.highlightAll());
  } catch (e) {
    console.error('获取词典失败:', e);
  }
};

const allItems = computed(() => {
  if (!glossaryData.value?.categories) return [];
  const items = [];
  glossaryData.value.categories.forEach(cat => {
    cat.items.forEach(it => {
      items.push({ ...it, parentCat: cat.name });
    });
  });
  return items;
});

const filteredItems = computed(() => {
  const q = searchQuery.value.trim().toLowerCase();
  const cat = selectedCat.value;

  return allItems.value.filter(it => {
    const matchCat = cat === 'all' || it.parentCat === cat;
    const matchSearch = !q || it.term.toLowerCase().includes(q) || it.raw.toLowerCase().includes(q);
    return matchCat && matchSearch;
  });
});

const renderInline = (str) => {
  if (!str) return '';
  return str.replace(/`([^`]+)`/g, '<code class="math-inline" style="color:var(--accent-primary); font-weight:700;">$1</code>');
};

const saveNewTerm = async () => {
  if (!newTerm.value.trim() || !newDiff.value.trim()) {
    emit('toast', '请填写词条名称和解析内容');
    return;
  }
  submitting.value = true;
  try {
    const res = await saveGlossaryTerm({
        category: newCat.value.trim() || '通用术语',
        term: newTerm.value.trim(),
        diff: newDiff.value.trim(),
        code: newCode.value.trim()
      });
    if (res.ok) {
      emit('toast', `已成功收录「${newTerm.value}」✓`);
      showAddModal.value = false;
      newTerm.value = '';
      newDiff.value = '';
      newCode.value = '';
      fetchGlossary();
    }
  } catch (e) {
    emit('toast', '保存失败');
  } finally {
    submitting.value = false;
  }
};

onMounted(() => {
  fetchGlossary();
});
</script>

<style scoped>
.glossary-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.glossary-header-card {
  background: var(--bg-card);
  border: 1px solid var(--border-card);
  border-radius: var(--radius-lg);
  padding: 18px 22px;
  box-shadow: var(--shadow-sm);
}

.header-top-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 14px;
}
.title-box {
  display: flex;
  align-items: center;
  gap: 8px;
}
.g-icon { font-size: 18px; }
.g-title { font-size: 16px; font-weight: 700; color: var(--text-main); }
.g-count { font-size: 12px; color: var(--text-muted); }

.filter-controls {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.search-box {
  position: relative;
  display: flex;
  align-items: center;
}
.search-icon {
  position: absolute;
  left: 12px;
  color: var(--text-muted);
  font-size: 13px;
}
.search-input {
  width: 100%;
  padding: 8px 30px 8px 34px;
  background: var(--bg-subtle);
  border: 1px solid var(--border-card);
  border-radius: var(--radius-sm);
  font-size: 13.5px;
  color: var(--text-main);
  outline: none;
}
.search-input:focus {
  border-color: var(--accent-primary);
  background: var(--bg-card);
}
.clear-btn {
  position: absolute;
  right: 10px;
  border: none;
  background: transparent;
  color: var(--text-muted);
  cursor: pointer;
}

.category-tabs {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}
.cat-tab {
  border: 1px solid var(--border-card);
  background: var(--bg-subtle);
  padding: 4px 10px;
  border-radius: var(--radius-sm);
  font-size: 12px;
  color: var(--text-sub);
  cursor: pointer;
  transition: all .15s;
}
.cat-tab:hover { color: var(--text-main); background: var(--border-card); }
.cat-tab.active {
  background: var(--accent-light);
  border-color: rgba(37,99,235,0.4);
  color: var(--accent-primary);
  font-weight: 600;
}

/* 术语卡片列表 */
.terms-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(480px, 1fr));
  gap: 16px;
}
@media(max-width: 768px) {
  .terms-grid { grid-template-columns: 1fr; }
}

.term-card {
  background: var(--bg-card);
  border: 1px solid var(--border-card);
  border-radius: var(--radius-md);
  padding: 18px 20px;
  box-shadow: var(--shadow-sm);
  display: flex;
  flex-direction: column;
  gap: 10px;
  transition: all .15s;
}
.term-card:hover {
  border-color: rgba(37,99,235,0.3);
  box-shadow: var(--shadow-md);
}

.term-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--border-card);
}
.term-name {
  font-size: 15px;
  font-weight: 700;
  color: var(--text-main);
}
.term-cat-badge {
  font-size: 11px;
  background: var(--bg-subtle);
  color: var(--text-muted);
  padding: 2px 8px;
  border-radius: 4px;
}

.term-content {
  font-size: 13.5px;
  line-height: 1.65;
  color: var(--text-sub);
}
.term-content :deep(pre) {
  background: #18181b;
  color: #f4f4f5;
  padding: 12px;
  border-radius: var(--radius-sm);
  font-family: var(--font-mono);
  font-size: 12.5px;
  margin: 8px 0;
  overflow-x: auto;
}
.term-content :deep(code) {
  background: var(--bg-subtle);
  color: #e11d48;
  padding: 2px 5px;
  border-radius: 4px;
  font-size: 12.5px;
  font-family: var(--font-mono);
}
.term-content :deep(pre code) {
  background: transparent;
  color: inherit;
  padding: 0;
}
.term-content :deep(ul) {
  padding-left: 18px;
  margin: 6px 0;
}
.term-content :deep(li) {
  margin-bottom: 4px;
}

/* Modal */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.6);
  backdrop-filter: blur(4px);
  z-index: 50;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}
.modal-card {
  background: var(--bg-card);
  border-radius: var(--radius-lg);
  width: min(600px, 94vw);
  box-shadow: var(--shadow-lg);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.m-head {
  padding: 16px 20px;
  border-bottom: 1px solid var(--border-card);
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.m-head h3 { font-size: 15.5px; font-weight: 700; color: var(--text-main); }
.close-x {
  border: none;
  background: transparent;
  font-size: 14px;
  color: var(--text-muted);
  cursor: pointer;
}
.m-body {
  padding: 18px 20px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-height: 70vh;
  overflow-y: auto;
}
.form-group {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.form-group label {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-sub);
}
.form-input, .form-textarea {
  width: 100%;
  padding: 8px 10px;
  background: var(--bg-subtle);
  border: 1px solid var(--border-card);
  border-radius: var(--radius-sm);
  font-size: 13px;
  color: var(--text-main);
  outline: none;
}
.form-input:focus, .form-textarea:focus {
  background: var(--bg-card);
  border-color: var(--accent-primary);
}
.code-font {
  font-family: var(--font-mono);
  font-size: 12.5px;
}
.m-foot {
  padding: 12px 20px;
  border-top: 1px solid var(--border-card);
  background: var(--bg-subtle);
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

.empty-state {
  grid-column: 1 / -1;
  padding: 48px 0;
  text-align: center;
  color: var(--text-muted);
  font-size: 14px;
}
</style>
