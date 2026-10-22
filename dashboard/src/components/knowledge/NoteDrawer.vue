<template>
  <div v-if="visible" :class="['drawer-overlay', inline ? 'inline-mode' : '']" @click.self="close">
    <div :class="['drawer-panel', inline ? 'inline-panel' : '']">

      <!-- 1. 精简紧凑的现代 Header (第一优先级: 压缩 30%~40% 高度) -->
      <header class="note-header">
        <!-- 上层：返回所属章节面包屑 + 快捷状态/编辑 -->
        <div class="header-top-row">
          <button class="back-breadcrumb-btn" @click="close" title="返回工作台">
            <ArrowLeft :size="14" />
            <span>{{ cleanSectionName }}</span>
          </button>

          <div class="header-actions">
            <!-- 掌握度轻量交互状态徽章 (只展示当前状态，点击呼出选择菜单) -->
            <div class="level-dropdown-wrap">
              <button
                :class="['level-current-pill', 'level-' + getLevelClass(currentLevel)]"
                @click="levelMenuOpen = !levelMenuOpen"
                title="点击调整掌握度"
              >
                <span
                  class="status-gem"
                  :style="{ background: getLevelColor(currentLevel), boxShadow: `0 0 6px ${getLevelColor(currentLevel)}99` }"
                ></span>
                <span class="level-name">{{ getLevelName(currentLevel) }}</span>
                <ChevronDown :size="12" class="pill-arrow" />
              </button>

              <!-- 切换下拉浮层 -->
              <div v-if="levelMenuOpen" class="level-menu-popover" @click.stop>
                <button
                  v-for="lv in ['🟢', '🔵', '🟡', '⚪']"
                  :key="lv"
                  :class="['level-menu-item', currentLevel === lv ? 'selected' : '']"
                  @click="changeLevel(lv)"
                >
                  <span class="status-gem" :style="{ background: getLevelColor(lv) }"></span>
                  <span class="item-name">{{ getLevelName(lv) }}</span>
                  <Check v-if="currentLevel === lv" :size="13" class="check-icon" />
                </button>
              </div>
            </div>

            <!-- 轻量编辑文字按钮 (第八优先级: 按钮统一) -->
            <button class="btn-text-ghost edit-btn" @click="toggleEdit">
              <Pencil :size="13" />
              <span>{{ isEditing ? '退出编辑' : '编辑源码' }}</span>
            </button>
          </div>
        </div>

        <!-- 中层：标题与副标题 -->
        <div class="header-title-block">
          <h1 class="main-title">{{ displayTitle.main }}</h1>
          <p v-if="displayTitle.sub" class="sub-title">{{ displayTitle.sub }}</p>
        </div>

        <!-- 下层：轻量弱化 Metadata (第五优先级: 弱化掌握度元数据) -->
        <div v-if="displayTitle.date" class="header-meta-row">
          <span class="meta-item">更新于 {{ displayTitle.date }}</span>
        </div>
      </header>

      <!-- 2. 现代极简轻量 Tab 栏 (第四优先级: 无 Emoji，Lucide 图标 + 浅色交互) -->
      <nav class="tabs-nav-bar">
        <div class="tabs-container">
          <button
            v-for="tab in availableTabs"
            :key="tab.key"
            :class="['tab-item-btn', currentSectionTab === tab.key ? 'active' : '']"
            @click="switchTab(tab.key)"
          >
            <component :is="tab.iconComp" :size="14" class="tab-lucide-icon" />
            <span>{{ tab.name }}</span>
          </button>
        </div>
      </nav>

      <!-- 3. 关联术语轻量淡背景 Chip 栏 -->
      <div v-if="!isEditing && matchedTerms.length" class="terms-subtle-bar">
        <span class="terms-label">相关术语</span>
        <div class="terms-chips-group">
          <button
            v-for="(t, idx) in matchedTerms"
            :key="idx"
            :class="['term-chip', isCodeTerm(t.shortName) ? 'is-code-term' : 'is-concept-term']"
            @click="openTermPopover(t)"
            :title="`速查: ${t.shortName}`"
          >
            <span class="term-text">{{ t.shortName }}</span>
          </button>
        </div>
      </div>

      <!-- 4. 正文内容区 (第三优先级: 740px 黄金阅读视线宽度) -->
      <div class="drawer-body-viewport" @click="levelMenuOpen = false">
        <div class="reading-column">

          <!-- 模式 A：源码编辑 -->
          <div v-if="isEditing" class="editor-pane">
            <textarea v-model="editingContent" class="markdown-textarea"></textarea>
            <div class="editor-quick-tools">
              <button class="btn btn-outline btn-xs" @click="insertCodeTmpl">
                + 插入最小代码模版
              </button>
              <button class="btn btn-outline btn-xs" @click="insertQuizTmpl">
                + 插入自测考题模版
              </button>
              <button class="btn btn-primary btn-xs" @click="saveNote" style="margin-left: auto;">
                保存修改
              </button>
            </div>
          </div>

          <!-- 模式 B：分块结构化阅读 -->
          <div v-else class="structured-article">
            <!-- 加载中过渡状态 -->
            <div v-if="isLoading" class="loading-state">
              <div class="loading-spinner"></div>
              <p class="loading-text">正在加载笔记「{{ noteName }}」...</p>
            </div>

            <!-- 空笔记提示 -->
            <div v-else-if="!rawContent" class="empty-note-state">
              <p class="empty-title">📝 还没有「{{ noteName }}」的专属笔记</p>
              <p class="empty-desc">可以一键生成规范模版，包含直觉理解、核心公式、NumPy验证代码与自测题</p>
              <button class="btn btn-primary" @click="createTemplate">
                + 一键创建结构化笔记模版
              </button>
            </div>

            <!-- 分块 1：核心直觉 (第六优先级: 知识卡片一句话理解) -->
            <div v-else-if="currentSectionTab === 'intuition'" class="section-pane">
              <div v-if="parsedSections.intuition" class="intuition-highlight-card">
                <div class="card-eyebrow">
                  <Lightbulb :size="14" class="eyebrow-icon" />
                  <span>一句话理解</span>
                </div>
                <div
                  class="intuition-body rich-text-content"
                  v-html="renderMarkdown(parsedSections.intuition)"
                  @click="handleContentClick"
                ></div>
              </div>

              <!-- 关联知识节点 (第七优先级: 留白 32px 代替生硬分割线) -->
              <div v-if="parsedSections.related" class="related-knowledge-block">
                <h3 class="clean-section-title">相关知识</h3>
                <div
                  class="rich-text-content"
                  v-html="renderMarkdown(parsedSections.related)"
                  @click="handleContentClick"
                ></div>
              </div>
            </div>

            <!-- 分块 2：数学原理 -->
            <div v-else-if="currentSectionTab === 'math'" class="section-pane">
              <div
                v-if="parsedSections.math"
                class="rich-text-content"
                v-html="renderMarkdown(parsedSections.math)"
                @click="handleContentClick"
              ></div>
              <div v-else class="tab-empty-hint">本笔记暂无单独数学原理分块，可切换至「完整全文」查阅。</div>
            </div>

            <!-- 分块 3：代码实现 -->
            <div v-else-if="currentSectionTab === 'code'" class="section-pane">
              <div
                v-if="parsedSections.code"
                class="rich-text-content"
                v-html="renderMarkdown(parsedSections.code)"
                @click="handleContentClick"
              ></div>
              <div v-else class="tab-empty-hint">本笔记暂无单独代码验证分块，可切换至「完整全文」查阅。</div>
            </div>

            <!-- 分块 4：思考自测 -->
            <div v-else-if="currentSectionTab === 'quiz'" class="section-pane">
              <div class="quiz-top-action">
                <button class="btn btn-outline btn-xs feynman-copy-btn" @click="copyFeynmanPrompt">
                  <Copy :size="13" />
                  <span>复制 AI 考官答辩指令</span>
                </button>
              </div>
              <div
                v-if="parsedSections.quiz"
                class="rich-text-content"
                v-html="renderMarkdown(parsedSections.quiz)"
                @click="handleContentClick"
              ></div>
              <div v-else class="tab-empty-hint">本笔记暂无自测题目。</div>
            </div>

            <!-- 分块 5：完整全文 -->
            <div v-else class="section-pane">
              <div
                class="rich-text-content"
                v-html="cleanRenderedHtml"
                @click="handleContentClick"
              ></div>
            </div>

          </div>
        </div>
      </div>

      <!-- 5. 底部操作栏 -->
      <footer class="drawer-footer">
        <button class="btn btn-outline" @click="close">
          <ArrowLeft :size="14" />
          <span>{{ inline ? '返回工作台' : '关闭' }}</span>
        </button>
        <button v-if="isEditing" class="btn btn-primary" @click="saveNote">
          保存笔记
        </button>
      </footer>

      <!-- 🌟 专有名词 & API 悬浮窗弹窗 (Glossary Popover) 🌟 -->
      <div v-if="activeTerm" class="term-popover-overlay" @click.self="activeTerm = null">
        <div class="term-popover-card">
          <div class="popover-head">
            <div class="popover-title-row">
              <span class="popover-icon">💡</span>
              <span class="popover-term-name">{{ activeTerm.term }}</span>
            </div>
            <button class="popover-close-btn" @click="activeTerm = null">✕</button>
          </div>

          <div class="popover-body">
            <div class="popover-cat-badge">
              🏷️ {{ activeTerm.parentCat || '专有名词速查' }}
            </div>
            <div class="popover-content" v-html="renderMarkdown(activeTerm.raw)"></div>
          </div>

          <div class="popover-foot">
            <button class="btn btn-outline btn-xs" @click="activeTerm = null">关闭悬浮窗</button>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, nextTick } from 'vue';
import {
  Lightbulb,
  Sigma,
  Code2,
  Brain,
  BookOpen,
  Pencil,
  ArrowLeft,
  Check,
  Copy,
  ChevronDown
} from 'lucide-vue-next';
import {
  fetchGlossary as loadGlossary,
  fetchNote as loadNote,
  saveNote as persistNote
} from '../../api';
import { renderMarkdown } from '../../utils/markdown';
import Prism from 'prismjs';

const props = defineProps({
  visible: Boolean,
  noteName: String,
  itemInfo: Object,
  inline: Boolean
});

const emit = defineEmits(['close', 'open-note', 'update-level', 'toast', 'saved']);

const isLoading = ref(false);
const isEditing = ref(false);
const rawContent = ref('');
const editingContent = ref('');
const TAB_STORAGE_KEY = 'aurora_note_tab';
const currentSectionTab = ref(localStorage.getItem(TAB_STORAGE_KEY) || 'all'); // 'intuition' | 'math' | 'code' | 'quiz' | 'all'
const levelMenuOpen = ref(false);

// 专有名词与 API 词典数据
const glossaryData = ref(null);
const activeTerm = ref(null);

const availableTabs = [
  { key: 'intuition', name: '核心直觉', iconComp: Lightbulb },
  { key: 'math', name: '数学原理', iconComp: Sigma },
  { key: 'code', name: '代码实现', iconComp: Code2 },
  { key: 'quiz', name: '思考自测', iconComp: Brain },
  { key: 'all', name: '完整全文', iconComp: BookOpen }
];

const getLevelName = (lv) => {
  const map = { '⚪': '未学', '🟡': '接触过', '🔵': '理解', '🟢': '掌握' };
  return map[lv] || lv;
};

const getLevelColor = (lv) => {
  const map = { '🟢': '#059669', '🔵': '#2563eb', '🟡': '#d97706', '⚪': '#94a3b8' };
  return map[lv] || '#94a3b8';
};

const getLevelClass = (lv) => {
  const map = { '🟢': 'mastered', '🔵': 'understood', '🟡': 'touched', '⚪': 'unlearned' };
  return map[lv] || 'unlearned';
};

// 提炼并精简所属章节名称
const cleanSectionName = computed(() => {
  const raw = props.itemInfo?.section || '知识体系';
  return raw.replace(/^[一二三四五六七八九十0-9]+[、. ]\s*/, '').trim();
});

// 解析标题、副标题与更新日期
const displayTitle = computed(() => {
  const raw = rawContent.value || '';
  const lines = raw.split('\n');
  const firstHeader = lines.find((l) => l.startsWith('# ')) || '';

  let main = props.noteName || '';
  let sub = '';
  let date = '';

  if (firstHeader) {
    const text = firstHeader.replace(/^#\s*/, '').trim();
    const m = text.match(/^(.*?)[（(](.*?)[）)]$/);
    if (m) {
      main = m[1].trim();
      sub = m[2].trim();
    } else {
      main = text;
    }
  }

  const dateMatch = raw.match(/更新[：:]\s*([0-9\-]+)/);
  if (dateMatch) {
    date = dateMatch[1];
  }

  return { main, sub, date };
});

// 剥离顶部冗余标题和引用的纯净正文
const cleanContent = computed(() => {
  const raw = rawContent.value;
  if (!raw) return '';
  return raw
    .replace(/^#\s+.*?\n+/g, '')
    .replace(/^>\s*掌握度[：:].*?\n+/gm, '')
    .trim();
});

const cleanRenderedHtml = computed(() => {
  return renderMarkdown(cleanContent.value);
});

// 解析拆分各个二级标题分块
const parsedSections = computed(() => {
  const raw = cleanContent.value;
  if (!raw) return {};

  const text = raw.replace(/\r\n/g, '\n');
  const sections = {
    intuition: '',
    math: '',
    code: '',
    quiz: '',
    related: '',
    all: text
  };

  // 按 ## 切割
  const parts = text.split(/\n(?=##\s+)/);

  parts.forEach((part) => {
    const trimmed = part.trim();
    if (!trimmed) return;

    const firstLine = trimmed.split('\n')[0];

    // 非 ## 开头的（如导言、简介）
    if (!firstLine.startsWith('##')) {
      sections.intuition = (sections.intuition ? sections.intuition + '\n\n' : '') + trimmed;
      return;
    }

    // 1. 代码与工程落地
    if (/代码|工程|实战|映射|NumPy|PyTorch|实现|验证|部署|量化|缓存|Cache|算子/i.test(firstLine)) {
      sections.code = (sections.code ? sections.code + '\n\n' : '') + trimmed;
    }
    // 2. 自测与思考
    else if (/思考|自测|问答|考题|测试/i.test(firstLine)) {
      sections.quiz = (sections.quiz ? sections.quiz + '\n\n' : '') + trimmed;
    }
    // 3. 关联知识
    else if (/关联/i.test(firstLine)) {
      sections.related = (sections.related ? sections.related + '\n\n' : '') + trimmed;
    }
    // 4. 直觉比喻
    else if (/直觉|心智模型|比喻|概览/i.test(firstLine)) {
      // 剥离 ## 一句话直觉 标题本身，使卡片内容更纯粹
      const bodyOnly = trimmed.replace(/^##\s+.*?\n+/, '').trim();
      sections.intuition = (sections.intuition ? sections.intuition + '\n\n' : '') + bodyOnly;
    }
    // 5. 数学与推导手算
    else if (/数学|公式|推导|手算|符号|核心要点|计算图|定理|几何/i.test(firstLine)) {
      sections.math = (sections.math ? sections.math + '\n\n' : '') + trimmed;
    }
    // 6. 其他小节默认放入数学
    else {
      sections.math = (sections.math ? sections.math + '\n\n' : '') + trimmed;
    }
  });

  if (!sections.intuition && parts.length > 0) {
    sections.intuition = parts[0].replace(/^##\s+.*?\n+/, '').trim();
  }

  return sections;
});

// 获取所有词条扁平列表
const allGlossaryItems = computed(() => {
  if (!glossaryData.value?.categories) return [];
  const items = [];
  glossaryData.value.categories.forEach((cat) => {
    cat.items.forEach((it) => {
      const short = it.term.replace(/`/g, '').split(' vs ')[0].trim();
      items.push({
        ...it,
        shortName: short,
        parentCat: cat.name
      });
    });
  });
  return items;
});

// 计算当前笔记正文中包含的专有名词
const matchedTerms = computed(() => {
  if (!rawContent.value || !allGlossaryItems.value.length) return [];
  const txt = rawContent.value;
  return allGlossaryItems.value.filter((it) => {
    const key = it.shortName.split('(')[0].replace('np.', '').replace('torch.', '').trim();
    return key.length >= 3 && txt.includes(key);
  });
});

// 判断术语是否属于代码 API / 库函数（用于区分等宽字体与普通字体）
const isCodeTerm = (termStr) => {
  if (!termStr) return false;
  // 带有库命名空间或点号调用 (如 nn.CrossEntropyLoss, np.maximum, torch.matmul, tensor.view)
  if (/^(nn|np|torch|F|tf|cv2|plt)\./i.test(termStr) || termStr.includes('.')) return true;
  // 带有函数调用括号或下划线命名 (如 cross_entropy, lr_scheduler, adam_w)
  if (termStr.includes('(') || termStr.includes(')') || termStr.includes('_')) return true;
  // 常见 PyTorch/NumPy 纯代码 API 类名
  if (/^(DataLoader|Dataset|Module|Sequential|Tensor|Optimizer|Adam|SGD|Conv[123]d|Linear|Dropout|BatchNorm[123]d|LayerNorm|Embedding|CrossEntropyLoss|MSELoss|BCEWithLogitsLoss|Softmax|ReLU|Sigmoid|GELU|SiLU)$/.test(termStr)) return true;
  return false;
};

const switchTab = (tabKey) => {
  currentSectionTab.value = tabKey;
  try {
    localStorage.setItem(TAB_STORAGE_KEY, tabKey);
  } catch (e) {}
  isEditing.value = false;
  levelMenuOpen.value = false;
  nextTick(() => Prism.highlightAll());
};

const toggleEdit = () => {
  isEditing.value = !isEditing.value;
  levelMenuOpen.value = false;
  if (!isEditing.value) {
    nextTick(() => Prism.highlightAll());
  }
};

const fetchGlossary = async () => {
  try {
    glossaryData.value = await loadGlossary();
  } catch (e) {
    console.error('获取词典失败:', e);
  }
};

const fetchNote = async () => {
  if (!props.noteName) return;
  isLoading.value = true;
  currentLevel.value = props.itemInfo?.level || '🟡';
  // 保留当前选中的 Tab，避免被强制切回只有两句话的直觉卡片
  if (!currentSectionTab.value) {
    currentSectionTab.value = localStorage.getItem(TAB_STORAGE_KEY) || 'all';
  }
  isEditing.value = false;
  levelMenuOpen.value = false;
  try {
    const d = await loadNote(props.noteName);
    rawContent.value = d.content || '';
    editingContent.value = d.content || '';

    fetchGlossary();

    nextTick(() => {
      Prism.highlightAll();
    });
  } catch (e) {
    rawContent.value = '';
    editingContent.value = '';
  } finally {
    isLoading.value = false;
  }
};

onMounted(() => {
  fetchNote();
});

watch(() => props.noteName, () => {
  fetchNote();
});

watch(
  () => props.visible,
  (v) => {
    if (v) fetchNote();
  }
);

const changeLevel = (lv) => {
  currentLevel.value = lv;
  levelMenuOpen.value = false;
  emit('update-level', { name: props.noteName, level: lv });
  emit('toast', `已将掌握度更新为 ${getLevelName(lv)}`);
};

const copyFeynmanPrompt = () => {
  const prompt = `请扮演深度学习资深技术考官，针对「${props.noteName}」对我进行 1~2 道探究式提问，检验我是否真正达到深入理解（🔵/🟢）。`;
  navigator.clipboard.writeText(prompt);
  emit('toast', '已复制考官提问指令！可直接发给 AI 助手开始答辩 🎙️');
};

const openTermPopover = (termObj) => {
  activeTerm.value = termObj;
  nextTick(() => Prism.highlightAll());
};

const handleContentClick = (e) => {
  // 1. 双链跳转
  const wikiTarget = e.target.closest('.wikilink-badge');
  if (wikiTarget && wikiTarget.dataset.note) {
    emit('open-note', wikiTarget.dataset.note);
    return;
  }

  // 2. 点击代码匹配专有名词
  const codeTarget = e.target.closest('code');
  if (codeTarget) {
    const codeText = codeTarget.innerText.trim();
    const matched = allGlossaryItems.value.find(
      (it) => it.term.includes(codeText) || codeText.includes(it.shortName)
    );
    if (matched) {
      openTermPopover(matched);
    }
  }
};

const createTemplate = () => {
  const tmpl = `# ${props.noteName}\n\n> 掌握度：${currentLevel.value} ${getLevelName(currentLevel.value)} ｜ 所属：${props.itemInfo?.section || ''} ｜ 更新：${new Date().toISOString().slice(0, 10)}\n\n## 一句话直觉\n用最通俗的比喻或一句话讲清核心本质。\n\n## 核心要点与数学公式\n- 核心公式：$$ \\theta_{t+1} = \\theta_t - \\eta \\nabla L $$\n- 关键机制：\n\n## 最小验证代码（<20行纯 NumPy）\n\`\`\`python\nimport numpy as np\n\n# 极简前向/反向验证\n\`\`\`\n\n## 工程与业务映射\n- 关联项目：androidhub / YOLO / RKNN\n- 落地场景：\n\n## 思考与自测\n- **自测 1**：问题描述？\n  > *解析*：深入原因与机制。\n\n## 关联知识\n- \n`;
  editingContent.value = tmpl;
  isEditing.value = true;
};

const insertCodeTmpl = () => {
  editingContent.value +=
    '\n\n## 最小验证代码（<20行纯 NumPy）\n```python\nimport numpy as np\n\n# 极简验证\n```\n';
};

const insertQuizTmpl = () => {
  editingContent.value +=
    '\n\n## 思考与自测\n- **自测 1**：问题描述？\n  > *解析*：深入原因与机制。\n';
};

const saveNote = async () => {
  try {
    const res = await persistNote(props.noteName, editingContent.value);
    if (res.ok) {
      rawContent.value = editingContent.value;
      isEditing.value = false;
      emit('toast', '笔记保存成功 ✓');
      emit('saved');
      nextTick(() => Prism.highlightAll());
    }
  } catch (e) {
    emit('toast', '保存失败，请稍后再试');
  }
};

const close = () => emit('close');
</script>

<style scoped>
/* 内联面板模式（作为内容区而非悬浮抽屉） */
.drawer-overlay.inline-mode {
  position: static;
  inset: auto;
  background: none;
  backdrop-filter: none;
  z-index: auto;
  display: block;
  animation: none;
}
.drawer-panel.inline-panel {
  width: 100%;
  height: calc(100vh - 97px);
  min-height: 480px;
  border: 1px solid var(--border-card);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
  animation: none;
}

.drawer-overlay {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.6);
  backdrop-filter: blur(4px);
  z-index: 50;
  display: flex;
  justify-content: flex-end;
  animation: fadeIn 0.2s ease-out;
}
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.drawer-panel {
  position: relative;
  width: min(840px, 94vw);
  height: 100vh;
  background: var(--bg-card);
  box-shadow: var(--shadow-lg);
  display: flex;
  flex-direction: column;
  animation: slideLeft 0.25s cubic-bezier(0.16, 1, 0.3, 1);
  border-left: 1px solid var(--border-card);
}
@keyframes slideLeft {
  from { transform: translateX(100%); }
  to { transform: translateX(0); }
}

/* ====================================================
   1. 精简 Header (第一优先级)
   ==================================================== */
.note-header {
  padding: 16px 28px 14px;
  border-bottom: 1px solid var(--border-card);
  background: var(--bg-card);
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.header-top-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.back-breadcrumb-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  border: none;
  background: transparent;
  color: var(--text-sub);
  font-size: 12.5px;
  font-weight: 500;
  cursor: pointer;
  padding: 2px 4px;
  border-radius: 4px;
  transition: all 0.15s ease;
}
.back-breadcrumb-btn:hover {
  color: var(--accent-primary);
  background: var(--accent-light);
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

/* 掌握度胶囊按钮与浮层 */
.level-dropdown-wrap {
  position: relative;
}
.level-current-pill {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  border-radius: 999px;
  border: 1px solid var(--border-card);
  background: var(--bg-subtle);
  font-size: 12px;
  font-weight: 600;
  color: var(--text-main);
  cursor: pointer;
  transition: all 0.15s ease;
}
.level-current-pill:hover {
  background: var(--bg-card);
  border-color: var(--border-subtle);
  box-shadow: var(--shadow-sm);
}
.status-gem {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  flex-shrink: 0;
}
.pill-arrow {
  color: var(--text-muted);
}

.level-menu-popover {
  position: absolute;
  top: calc(100% + 6px);
  right: 0;
  background: var(--bg-card);
  border: 1px solid var(--border-card);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-md);
  padding: 4px;
  display: flex;
  flex-direction: column;
  gap: 2px;
  z-index: 60;
  min-width: 110px;
  animation: fadeIn 0.15s ease;
}
.level-menu-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 10px;
  border: none;
  background: transparent;
  border-radius: var(--radius-sm);
  font-size: 12px;
  color: var(--text-main);
  cursor: pointer;
  text-align: left;
  transition: background 0.12s;
}
.level-menu-item:hover {
  background: var(--bg-subtle);
}
.level-menu-item.selected {
  font-weight: 700;
  color: var(--accent-primary);
  background: var(--accent-light);
}
.check-icon {
  margin-left: auto;
  color: var(--accent-primary);
}

/* 统一文字按钮 (第八优先级) */
.btn-text-ghost {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  border: none;
  background: transparent;
  color: var(--text-sub);
  font-size: 12px;
  font-weight: 500;
  padding: 4px 8px;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all 0.15s ease;
}
.btn-text-ghost:hover {
  background: var(--bg-subtle);
  color: var(--text-main);
}

.header-title-block {
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.main-title {
  font-size: 22px;
  font-weight: 800;
  color: var(--text-main);
  line-height: 1.25;
}
.sub-title {
  font-size: 13.5px;
  color: var(--text-sub);
  margin: 0;
  line-height: 1.4;
}

.header-meta-row {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: var(--text-muted);
}

/* ====================================================
   2. 现代轻量 Tab 栏 (第四优先级)
   ==================================================== */
.tabs-nav-bar {
  padding: 0 28px;
  background: var(--bg-card);
  border-bottom: 1px solid var(--border-card);
}
.tabs-container {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 8px 0;
  overflow-x: auto;
}
.tab-item-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  border: none;
  background: transparent;
  padding: 6px 12px;
  font-size: 13px;
  font-weight: 500;
  color: var(--text-sub);
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all 0.15s ease;
  white-space: nowrap;
}
.tab-item-btn:hover {
  background: var(--bg-subtle);
  color: var(--text-main);
}
.tab-item-btn.active {
  background: var(--accent-light);
  color: var(--accent-primary);
  font-weight: 600;
}
.tab-lucide-icon {
  color: inherit;
}

/* ====================================================
   3. 涉及术语轻量淡背景 Chip 栏
   ==================================================== */
.terms-subtle-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 28px;
  background: var(--bg-card);
  border-bottom: 1px solid var(--border-card);
}

.terms-label {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-sub);
  flex-shrink: 0;
}

.terms-chips-group {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.term-chip {
  height: 28px;
  padding: 0 12px;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
  background: #f1f5f9;
  color: #334155;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  outline: none;
  transition: all 0.15s ease;
  user-select: none;
}

[data-theme="dark"] .term-chip {
  background: #1e293b;
  border-color: #334155;
  color: #cbd5e1;
}

.term-chip:hover {
  background: #e2e8f0;
  border-color: #cbd5e1;
  color: var(--accent-primary);
  transform: translateY(-1px);
}

[data-theme="dark"] .term-chip:hover {
  background: #334155;
  border-color: #475569;
  color: #818cf8;
}

.term-chip .term-text {
  line-height: 1;
}

/* 普通概念术语：普通 UI 字体，12.5px，干净现代 */
.term-chip.is-concept-term .term-text {
  font-family: var(--font-sans);
  font-size: 12.5px;
  font-weight: 500;
}

/* 真正的代码 API 术语：等宽代码字体，12px */
.term-chip.is-code-term .term-text {
  font-family: var(--font-mono);
  font-size: 12px;
  font-weight: 500;
  color: #4338ca;
}

[data-theme="dark"] .term-chip.is-code-term .term-text {
  color: #a5b4fc;
}

/* ====================================================
   4. 正文 740px 黄金阅读视线 (第三优先级)
   ==================================================== */
.drawer-body-viewport {
  flex: 1;
  overflow-y: auto;
  padding: 24px 28px 48px;
  background: var(--bg-app);
}
.reading-column {
  max-width: 740px;
  margin: 0 auto;
  width: 100%;
}

/* ====================================================
   5. 第六优先级:「一句话理解」知识卡片
   ==================================================== */
.intuition-highlight-card {
  background: var(--bg-card);
  border: 1px solid var(--border-card);
  border-radius: 16px;
  padding: 20px 24px;
  margin-bottom: 36px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03);
}
[data-theme="dark"] .intuition-highlight-card {
  background: #111827;
  border-color: #1f2937;
}
.card-eyebrow {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 11.5px;
  font-weight: 700;
  letter-spacing: 0.05em;
  color: var(--accent-primary);
  text-transform: uppercase;
  margin-bottom: 12px;
}
.eyebrow-icon {
  color: var(--accent-primary);
}
.intuition-body {
  font-size: 15px;
  line-height: 1.8;
  color: var(--text-main);
}

/* 留白与无分割线模块排版 (第七优先级) */
.related-knowledge-block {
  margin-top: 36px;
}
.clean-section-title {
  font-size: 16px;
  font-weight: 700;
  color: var(--text-main);
  margin-bottom: 14px;
}

.quiz-top-action {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 16px;
}
.feynman-copy-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.tab-empty-hint {
  padding: 48px 0;
  text-align: center;
  color: var(--text-muted);
  font-size: 13.5px;
}

/* ====================================================
   6. 结构化 Markdown 排版 (第七优先级: 移除横线，留白空间)
   ==================================================== */
.rich-text-content {
  font-size: 14.5px;
  line-height: 1.8;
  color: var(--text-main);
}
:deep(h1),
:deep(h2) {
  font-size: 17.5px;
  font-weight: 700;
  color: var(--text-main);
  margin: 36px 0 14px;
  border-bottom: none;
  padding-bottom: 0;
}
:deep(h2:first-child) {
  margin-top: 0;
}
:deep(h3) {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-main);
  margin: 24px 0 10px;
}
:deep(p) {
  margin-bottom: 16px;
}
:deep(img) {
  max-width: 100%;
  height: auto;
  display: block;
  margin: 18px auto;
  border-radius: var(--radius-md);
  border: 1px solid var(--border-card);
  box-shadow: var(--shadow-sm);
  background: #ffffff;
}
:deep(blockquote) {
  background: var(--bg-subtle);
  border-left: 3px solid var(--accent-primary);
  padding: 12px 18px;
  border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
  margin: 20px 0;
  color: var(--text-sub);
  font-size: 14px;
}
:deep(pre) {
  background: #18181b;
  color: #f4f4f5;
  padding: 16px 20px;
  border-radius: 12px;
  overflow-x: auto;
  font-family: var(--font-mono);
  font-size: 13px;
  margin: 20px 0;
}
:deep(code) {
  background: var(--bg-subtle);
  color: var(--accent-primary);
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 13px;
  font-family: var(--font-mono);
  cursor: pointer;
  transition: background 0.15s;
}
:deep(code:hover) {
  background: var(--accent-light);
}
:deep(pre code) {
  background: transparent;
  color: inherit;
  padding: 0;
  cursor: text;
}
:deep(pre code:hover) {
  background: transparent;
}
:deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin: 24px 0;
  font-size: 13.5px;
}
:deep(th),
:deep(td) {
  border: 1px solid var(--border-card);
  padding: 10px 14px;
  text-align: left;
}
:deep(th) {
  background: var(--bg-subtle);
  font-weight: 600;
}
:deep(ul),
:deep(ol) {
  padding-left: 22px;
  margin: 12px 0 20px;
}
:deep(li) {
  margin-bottom: 7px;
  color: var(--text-main);
}
:deep(.katex-block-wrapper) {
  background: var(--bg-subtle);
  border: 1px solid var(--border-card);
  border-radius: var(--radius-sm);
  padding: 14px;
  margin: 18px 0;
  text-align: center;
  overflow-x: auto;
}
:deep(.wikilink-badge) {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  background: var(--accent-light);
  color: var(--accent-primary);
  border: 1px solid rgba(79, 70, 229, 0.2);
  border-radius: 6px;
  padding: 2px 8px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  margin: 2px 4px;
  transition: all 0.15s;
}
:deep(.wikilink-badge:hover) {
  background: var(--accent-primary);
  color: #fff;
}

/* 编辑器容器 */
.markdown-textarea {
  width: 100%;
  min-height: 480px;
  background: var(--bg-card);
  border: 1px solid var(--border-card);
  border-radius: var(--radius-md);
  padding: 16px;
  font-family: var(--font-mono);
  font-size: 13px;
  line-height: 1.6;
  color: var(--text-main);
  outline: none;
  resize: vertical;
}
.editor-quick-tools {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 10px;
}

/* 加载中过渡动效 */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 0;
  gap: 14px;
}
.loading-spinner {
  width: 28px;
  height: 28px;
  border: 2.5px solid var(--border-card);
  border-top-color: var(--accent-primary);
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}
@keyframes spin {
  to { transform: rotate(360deg); }
}
.loading-text {
  font-size: 13px;
  color: var(--text-muted);
}

/* 空笔记引导 */
.empty-note-state {
  padding: 56px 0;
  text-align: center;
}
.empty-title {
  font-size: 16px;
  font-weight: 700;
  color: var(--text-main);
  margin-bottom: 8px;
}
.empty-desc {
  font-size: 13.5px;
  color: var(--text-muted);
  margin-bottom: 20px;
}

/* 底部操作栏 */
.drawer-footer {
  padding: 12px 28px;
  border-top: 1px solid var(--border-card);
  background: var(--bg-card);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

/* 专有名词浮层弹窗 */
.term-popover-overlay {
  position: absolute;
  inset: 0;
  background: rgba(15, 23, 42, 0.45);
  backdrop-filter: blur(2px);
  z-index: 100;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  animation: fadeIn 0.15s ease-out;
}
.term-popover-card {
  background: var(--bg-card);
  border: 1px solid var(--border-card);
  border-radius: var(--radius-lg);
  width: min(560px, 95%);
  box-shadow: var(--shadow-lg);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}
.popover-head {
  padding: 14px 18px;
  border-bottom: 1px solid var(--border-card);
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: var(--bg-subtle);
}
.popover-title-row {
  display: flex;
  align-items: center;
  gap: 8px;
}
.popover-icon { font-size: 16px; }
.popover-term-name {
  font-size: 14.5px;
  font-weight: 700;
  color: var(--text-main);
}
.popover-close-btn {
  border: none;
  background: transparent;
  font-size: 14px;
  color: var(--text-muted);
  cursor: pointer;
}
.popover-body {
  padding: 18px 20px;
  max-height: 60vh;
  overflow-y: auto;
}
.popover-cat-badge {
  font-size: 11.5px;
  color: var(--accent-primary);
  background: var(--accent-light);
  padding: 2px 8px;
  border-radius: 4px;
  display: inline-block;
  margin-bottom: 10px;
}
.popover-content {
  font-size: 13.5px;
  line-height: 1.65;
  color: var(--text-sub);
}
.popover-foot {
  padding: 10px 18px;
  background: var(--bg-subtle);
  border-top: 1px solid var(--border-card);
  display: flex;
  justify-content: flex-end;
}
</style>
