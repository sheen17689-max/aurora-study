<template>
  <LoginGate v-if="!vault" @unlock="onUnlock" />
  <CvWorkspace v-else-if="vault === 'cv'" @back="lockVault" />
  <div
    v-else
    class="app-shell"
    :class="{
      'sidebar-collapsed': sidebarCollapsed,
      'sidebar-resizing': sidebarResizing,
    }"
    :style="{ '--sidebar-width': sidebarWidth + 'px' }"
  >
    <!-- 应用级左侧边栏：知识框架文件导航（大纲地图视图常驻） -->
    <aside
      v-if="viewMode === 'tree'"
      class="app-sidebar"
      :class="{ collapsed: sidebarCollapsed }"
    >
      <div class="sidebar-brand">
        <div class="brand-badge">
          <span class="brand-icon">✦</span>
        </div>
        <div class="brand-meta">
          <div class="brand-text">{{ vault === 'agent' ? 'Agent 研学' : 'Aurora' }}</div>
          <div class="brand-subtitle">{{ vault === 'agent' ? '智能体与自主架构' : '学习笔记与知识库' }}</div>
        </div>
      </div>
      <KnowledgeTree
        bare
        :data="appData"
        :active-name="activeNoteName"
        @open-note="openDrawer"
        @toggle-sidebar="toggleSidebar"
      />
    </aside>

    <!-- 侧边栏 / 主区拖拽分隔条 -->
    <div
      v-if="viewMode === 'tree' && !sidebarCollapsed"
      class="sidebar-resizer"
      role="separator"
      aria-orientation="vertical"
      aria-label="拖动调整文档导航宽度"
      title="拖动调整宽度，双击恢复默认"
      tabindex="0"
      @pointerdown="startSidebarResize"
      @keydown="onResizerKeydown"
      @dblclick="resetSidebarWidth"
    ></div>
    <div v-if="sidebarResizing" class="resize-mask"></div>

    <!-- 侧边栏收起时的快捷拉出浮动触发条 -->
    <button
      v-if="viewMode === 'tree' && sidebarCollapsed"
      class="sidebar-edge-toggle"
      @click="toggleSidebar"
      title="展开文档导航 (Ctrl+B)"
      aria-label="展开文档导航"
    >
      <PanelLeftOpen :size="17" />
      <span class="edge-toggle-tip">展开导航</span>
    </button>

    <div class="app-main">
      <!-- 顶部导航 -->
      <Header
        :data="appData"
        v-model:viewMode="viewMode"
        :sidebar-collapsed="sidebarCollapsed"
        @toggle-sidebar="toggleSidebar"
        @toast="showToast"
        @back-to-shelf="lockVault"
      />

      <main class="main-content">
        <!-- 视图 1：笔记主区 + 右栏（艾宾浩斯自测 + 每日简报） -->
        <div v-if="viewMode === 'tree'" class="tree-layout">
          <section class="content-pane">
            <NoteDrawer
              v-if="noteOpen"
              inline
              :visible="noteOpen"
              :note-name="activeNoteName"
              :item-info="activeItemInfo"
              @close="closeNote"
              @open-note="openDrawer"
              @update-level="handleLevelUpdate"
              @saved="fetchData"
              @toast="showToast"
            />
            <div v-else class="workbench">
              <!-- 顶部：今日主攻路线 -->
              <div class="advice-card">
                <div class="card-head">
                  <div class="head-title-wrap">
                    <Compass :size="16" class="head-icon" />
                    <span class="card-title">今日主攻路线</span>
                  </div>
                  <span v-if="appData?.route?.current" class="current-stage-chip">
                    {{ appData.route.current }}
                  </span>
                </div>
                <ul class="clean-list">
                  <li
                    v-for="(item, idx) in (appData?.route?.next?.length ? appData.route.next : ['点击知识点查看概念并进行自测'])"
                    :key="idx"
                    v-html="renderInlineMarkdown(item)"
                  ></li>
                </ul>
              </div>

              <!-- 中间：40 / 60 栅格布局 (左 40% 学习进度 + 右 60% 快速记录) -->
              <div class="workbench-mid-grid">
                <div class="grid-col-40">
                  <TopStats :data="appData" />
                </div>
                <div class="grid-col-60">
                  <QuickLog
                    @logged="fetchData"
                    @toast="showToast"
                  />
                </div>
              </div>

              <!-- 底部：回顾与日记 -->
              <DiaryTimeline
                :diaries="appData?.diaries"
                :yesterday="appData?.yesterday"
              />
            </div>
          </section>

          <!-- 右栏：AI 学习助手（今日复习 + 每日简报） -->
          <aside class="rail-pane">
            <div class="rail-header">
              <Sparkles :size="14" class="rail-header-icon" />
              <span class="rail-header-title">学习助手</span>
            </div>

            <!-- 今日复习 -->
            <DailyQuizCard
              :quiz="appData?.quiz"
              @open-note="openDrawer"
              @update-level="handleLevelUpdate"
              @toast="showToast"
            />

            <!-- 今日简报 -->
            <div
              v-if="appData?.briefing?.sections?.length"
              class="briefing-panel"
              @click="handleBriefingClick"
            >
              <div class="brief-title">
                <Mail :size="14" class="brief-icon" />
                <span>今日简报 · {{ appData.briefing.date }}</span>
              </div>
              <details
                v-for="(sec, idx) in appData.briefing.sections"
                :key="idx"
                :open="isBriefSecOpen(sec.title)"
                class="brief-sec"
              >
                <summary>{{ sec.title || '简报' }}</summary>
                <div
                  v-for="(line, lidx) in sec.lines"
                  :key="lidx"
                  class="brief-line"
                  v-html="renderInlineMarkdown(line)"
                ></div>
              </details>
            </div>
          </aside>
        </div>

        <!-- 视图 2：全景知识星系力导向拓扑图 -->
        <div v-else-if="viewMode === 'graph'" class="graph-pane">
          <KnowledgeGraph
            :data="appData"
            @open-note="openDrawer"
          />
        </div>

        <!-- 视图 3：AI 研学 Agent 助手全功能工作台 -->
        <div v-else-if="viewMode === 'agent'" class="agent-pane">
          <ChatAssistant
            :data="appData"
            @open-note="openDrawer"
            @update-level="handleLevelUpdate"
            @toast="showToast"
          />
        </div>
      </main>
    </div>

    <!-- 侧边沉浸式笔记抽屉（星系视图用） -->
    <NoteDrawer
      :visible="drawerVisible"
      :note-name="activeNoteName"
      :item-info="activeItemInfo"
      @close="drawerVisible = false"
      @open-note="openDrawer"
      @update-level="handleLevelUpdate"
      @saved="fetchData"
      @toast="showToast"
    />

    <!-- 全局 Toast 提示 -->
    <div :class="['toast-notification', toastActive ? 'show' : '']">
      {{ toastMessage }}
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted } from 'vue';
import { PanelLeftOpen, Compass, Mail, Sparkles } from 'lucide-vue-next';
import { fetchData as loadAppData, updateLevel, setCurrentBook } from './api';
import { renderInlineMarkdown } from './utils/markdown';
import Header from './components/layout/Header.vue';
import LoginGate from './components/auth/LoginGate.vue';
import CvWorkspace from './components/auth/CvWorkspace.vue';
import TopStats from './components/study/TopStats.vue';
import DailyQuizCard from './components/study/DailyQuizCard.vue';
import KnowledgeTree from './components/knowledge/KnowledgeTree.vue';
import KnowledgeGraph from './components/knowledge/KnowledgeGraph.vue';
import NoteDrawer from './components/knowledge/NoteDrawer.vue';
import QuickLog from './components/study/QuickLog.vue';
import DiaryTimeline from './components/study/DiaryTimeline.vue';
import ChatAssistant from './components/agent/ChatAssistant.vue';

const VAULT_KEY = 'aurora_vault';
const SIDEBAR_WIDTH_KEY = 'aurora_sidebar_width';
const SIDEBAR_DEFAULT = 310;
const SIDEBAR_MIN = 220;
const SIDEBAR_MAX = 560;

const readStoredSidebarWidth = () => {
  const n = Number(localStorage.getItem(SIDEBAR_WIDTH_KEY));
  return Number.isFinite(n) ? n : SIDEBAR_DEFAULT;
};

const vault = ref(localStorage.getItem(VAULT_KEY) || '');
const appData = ref(null);
const viewMode = ref('tree'); // 'tree' | 'graph'
const sidebarCollapsed = ref(localStorage.getItem('aurora_sidebar_collapsed') === 'true');
const sidebarWidth = ref(
  Math.max(SIDEBAR_MIN, Math.min(SIDEBAR_MAX, readStoredSidebarWidth()))
);
const sidebarResizing = ref(false);
let stopSidebarResize = null;

const NOTE_OPEN_KEY = 'aurora_note_open';
const ACTIVE_NOTE_KEY = 'aurora_active_note';

const drawerVisible = ref(false);
const noteOpen = ref(localStorage.getItem(NOTE_OPEN_KEY) === 'true');
const activeNoteName = ref(localStorage.getItem(ACTIVE_NOTE_KEY) || '');
const activeItemInfo = ref(null);

const toastMessage = ref('');
const toastActive = ref(false);

const toggleSidebar = () => {
  sidebarCollapsed.value = !sidebarCollapsed.value;
  localStorage.setItem('aurora_sidebar_collapsed', sidebarCollapsed.value);
};

const clampSidebarWidth = (w) => {
  const max = Math.min(SIDEBAR_MAX, Math.floor(window.innerWidth * 0.5));
  return Math.max(SIDEBAR_MIN, Math.min(max, Math.round(w)));
};

const persistSidebarWidth = () => {
  localStorage.setItem(SIDEBAR_WIDTH_KEY, String(sidebarWidth.value));
};

const resetSidebarWidth = () => {
  sidebarWidth.value = SIDEBAR_DEFAULT;
  persistSidebarWidth();
};

const startSidebarResize = (e) => {
  if (e.pointerType === 'mouse' && e.button !== 0) return;
  e.preventDefault();
  stopSidebarResize?.();
  sidebarResizing.value = true;
  const startX = e.clientX;
  const startW = sidebarWidth.value;

  const onMove = (ev) => {
    sidebarWidth.value = clampSidebarWidth(startW + (ev.clientX - startX));
  };
  const onUp = () => {
    stopSidebarResize?.();
  };
  stopSidebarResize = () => {
    sidebarResizing.value = false;
    persistSidebarWidth();
    window.removeEventListener('pointermove', onMove);
    window.removeEventListener('pointerup', onUp);
    window.removeEventListener('pointercancel', onUp);
    stopSidebarResize = null;
  };
  window.addEventListener('pointermove', onMove);
  window.addEventListener('pointerup', onUp);
  window.addEventListener('pointercancel', onUp);
};

const onResizerKeydown = (e) => {
  const step = e.shiftKey ? 32 : 16;
  if (e.key === 'ArrowLeft') {
    e.preventDefault();
    sidebarWidth.value = clampSidebarWidth(sidebarWidth.value - step);
    persistSidebarWidth();
  } else if (e.key === 'ArrowRight') {
    e.preventDefault();
    sidebarWidth.value = clampSidebarWidth(sidebarWidth.value + step);
    persistSidebarWidth();
  } else if (e.key === 'Home') {
    e.preventDefault();
    resetSidebarWidth();
  }
};

const handleKeyDown = (e) => {
  if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'b') {
    e.preventDefault();
    toggleSidebar();
  }
};

const showToast = (msg) => {
  toastMessage.value = msg;
  toastActive.value = true;
  setTimeout(() => {
    toastActive.value = false;
  }, 2500);
};

const handleBriefingClick = (e) => {
  const target = e.target.closest('.wikilink-badge');
  if (target) {
    const noteName = target.getAttribute('data-note');
    if (noteName) {
      openDrawer(noteName);
    }
  }
};

// 简报分区默认展开规则：昨日回顾 / 今日建议展开，自测题与答案默认收起
const isBriefSecOpen = (title) => /建议|回顾/.test(title || '');

const fetchData = async () => {
  try {
    appData.value = await loadAppData();
  } catch (e) {
    console.error('获取学习管家数据失败:', e);
  }
};

const openDrawer = (name, itemInfo) => {
  activeNoteName.value = name;
  activeItemInfo.value = itemInfo || { name, level: '🟡', section: '知识点' };
  try {
    localStorage.setItem(ACTIVE_NOTE_KEY, name);
  } catch (e) {}
  if (viewMode.value === 'tree') {
    noteOpen.value = true;
    try {
      localStorage.setItem(NOTE_OPEN_KEY, 'true');
    } catch (e) {}
  } else {
    drawerVisible.value = true;
  }
};

const closeNote = () => {
  noteOpen.value = false;
  try {
    localStorage.removeItem(NOTE_OPEN_KEY);
    localStorage.removeItem(ACTIVE_NOTE_KEY);
  } catch (e) {}
};

watch(viewMode, () => {
  drawerVisible.value = false;
});

const handleLevelUpdate = async ({ name, level }) => {
  try {
    await updateLevel(name, level);
    fetchData();
  } catch (e) {
    showToast('更新掌握度失败');
  }
};

const onUnlock = (id) => {
  vault.value = id;
  localStorage.setItem(VAULT_KEY, id);
  if (id === 'dl' || id === 'agent') {
    setCurrentBook(id);
  }
};

const lockVault = () => {
  vault.value = '';
  localStorage.removeItem(VAULT_KEY);
};

let pollTimer = null;
watch(
  vault,
  (id) => {
    if (pollTimer) {
      clearInterval(pollTimer);
      pollTimer = null;
    }
    if (id === 'dl' || id === 'agent') {
      setCurrentBook(id);
      fetchData();
      pollTimer = setInterval(fetchData, 60000);
    }
  },
  { immediate: true }
);

onMounted(() => {
  window.addEventListener('keydown', handleKeyDown);
});

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeyDown);
  if (pollTimer) clearInterval(pollTimer);
  stopSidebarResize?.();
});
</script>

<style scoped>
.app-shell {
  display: flex;
  min-height: 100vh;
}
.app-shell.sidebar-resizing {
  cursor: col-resize;
  user-select: none;
}

/* 应用级左侧边栏 */
.app-sidebar {
  width: var(--sidebar-width, 310px);
  flex-shrink: 0;
  height: 100vh;
  position: sticky;
  top: 0;
  background: var(--bg-card);
  border-right: 1px solid var(--border-card);
  overflow-y: auto;
  overflow-x: hidden;
  display: flex;
  flex-direction: column;
  transition: width 0.24s cubic-bezier(0.4, 0, 0.2, 1),
              opacity 0.2s ease,
              border-color 0.2s ease;
  z-index: 30;
}
.app-shell.sidebar-resizing .app-sidebar {
  transition: none;
}
.app-sidebar.collapsed {
  width: 0 !important;
  min-width: 0 !important;
  opacity: 0;
  pointer-events: none;
  border-right-color: transparent;
  overflow: hidden;
}

.sidebar-resizer {
  width: 8px;
  margin: 0 -4px;
  flex-shrink: 0;
  align-self: stretch;
  position: relative;
  z-index: 40;
  cursor: col-resize;
  touch-action: none;
  background: transparent;
}
.sidebar-resizer::after {
  content: "";
  position: absolute;
  top: 0;
  bottom: 0;
  left: 50%;
  width: 1px;
  transform: translateX(-50%);
  background: var(--border-card);
  transition: width 0.15s ease, background 0.15s ease;
}
.sidebar-resizer:hover::after,
.sidebar-resizer:focus-visible::after,
.app-shell.sidebar-resizing .sidebar-resizer::after {
  width: 3px;
  background: var(--accent-primary);
}
.sidebar-resizer:focus-visible {
  outline: none;
}
.resize-mask {
  position: fixed;
  inset: 0;
  z-index: 200;
  cursor: col-resize;
}

.sidebar-brand {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px 18px;
  border-bottom: 1px solid var(--border-card);
  position: sticky;
  top: 0;
  background: var(--bg-card);
  z-index: 5;
}
.brand-badge {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: linear-gradient(135deg, #a16207 0%, #ca8a04 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #ffffff;
  box-shadow: 0 2px 5px rgba(161, 98, 7, 0.25);
  flex-shrink: 0;
}
.brand-icon {
  font-size: 16px;
  line-height: 1;
}
.brand-meta {
  display: flex;
  flex-direction: column;
  min-width: 0;
}
.brand-text {
  font-size: 15px;
  font-weight: 800;
  color: var(--text-main);
  line-height: 1.2;
}
.brand-subtitle {
  font-size: 11px;
  color: var(--text-muted);
  line-height: 1.3;
  margin-top: 1px;
}

/* 悬浮边缘展开按钮 */
.sidebar-edge-toggle {
  position: fixed;
  left: 0;
  top: 76px;
  z-index: 50;
  background: var(--bg-card);
  border: 1px solid var(--border-card);
  border-left: none;
  border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
  padding: 7px 12px 7px 9px;
  display: flex;
  align-items: center;
  gap: 6px;
  box-shadow: var(--shadow-md);
  color: var(--text-sub);
  cursor: pointer;
  transition: all .2s cubic-bezier(0.16, 1, 0.3, 1);
}
.sidebar-edge-toggle:hover {
  background: var(--bg-subtle);
  color: var(--accent-primary);
  padding-left: 12px;
  transform: translateX(2px);
  box-shadow: var(--shadow-lg);
}
.edge-toggle-tip {
  font-size: 12px;
  font-weight: 600;
}

.app-main {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
}

.main-content {
  width: 100%;
  margin: 20px 0;
  padding: 0 20px;
  flex: 1;
}

/* Agent 工作台视图：去掉主区留白，让农场木板全出血铺满（否则会露出 body 白边） */
.main-content:has(.agent-pane) {
  margin: 0;
  padding: 0;
  min-height: 0;
}

/* Agent 视图下锁定整体高度为视口高，内部滚动，杜绝页面级滚动条/底部外露 */
.app-main:has(.agent-pane) {
  height: 100vh;
  overflow: hidden;
}

/* 三栏布局：笔记主区 + 右栏（自测 + 简报） */
.tree-layout {
  display: grid;
  grid-template-columns: 1fr 360px;
  gap: 16px;
  align-items: start;
}
.content-pane {
  min-width: 0;
}
.rail-pane {
  display: flex;
  flex-direction: column;
  gap: 16px;
  position: sticky;
  top: 78px;
  height: calc(100vh - 97px);
}

.rail-header {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 0 4px 2px;
}
.rail-header-icon {
  color: var(--accent-primary);
}
.rail-header-title {
  font-size: 13px;
  font-weight: 700;
  color: var(--text-main);
}

/* 右栏：每日简报面板 */
.briefing-panel {
  background: var(--bg-card);
  border: 1px solid var(--border-card);
  border-radius: var(--radius-lg);
  padding: 16px 18px;
  box-shadow: var(--shadow-sm);
  flex: 1;
  min-height: 0;
  overflow-y: auto;
}
.brief-title {
  display: flex;
  align-items: center;
  gap: 6px;
  font-weight: 700;
  color: var(--accent-primary);
  font-size: 13.5px;
  margin-bottom: 10px;
}
.brief-icon {
  color: var(--accent-primary);
}
.brief-sec {
  border-top: 1px dashed var(--border-card);
  padding: 8px 0;
}
.brief-sec:first-of-type {
  border-top: none;
  padding-top: 0;
}
.brief-sec summary {
  cursor: pointer;
  font-size: 12.5px;
  font-weight: 600;
  color: var(--text-main);
  list-style: none;
  user-select: none;
}
.brief-sec summary::-webkit-details-marker { display: none; }
.brief-sec summary:before { content: "▸ "; color: var(--accent-primary); }
.brief-sec[open] summary:before { content: "▾ "; }
.brief-line {
  font-size: 12.5px;
  color: var(--text-sub);
  line-height: 1.7;
  padding-left: 12px;
  margin-top: 4px;
}

/* 工作台（未选中笔记时的默认主区） */
.workbench {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* 中间 40/60 栅格 */
.workbench-mid-grid {
  display: grid;
  grid-template-columns: 4fr 6fr;
  gap: 16px;
  align-items: stretch;
}
.grid-col-40,
.grid-col-60 {
  min-width: 0;
  display: flex;
  flex-direction: column;
}

.advice-card {
  background: var(--bg-card);
  border: 1px solid var(--border-card);
  border-left: 3.5px solid var(--accent-primary);
  border-radius: var(--radius-lg);
  padding: 16px 20px;
  box-shadow: var(--shadow-sm);
}
.card-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 10px;
}
.head-title-wrap {
  display: flex;
  align-items: center;
  gap: 7px;
}
.head-icon {
  color: var(--accent-primary);
}
.card-title {
  font-size: 14px;
  font-weight: 700;
  color: var(--text-main);
}
.current-stage-chip {
  background: var(--accent-light);
  color: var(--accent-primary);
  font-size: 11px;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 999px;
  border: 1px solid rgba(79, 70, 229, 0.2);
}
.clean-list { list-style: none; }
.clean-list li {
  font-size: 13.5px;
  color: var(--text-sub);
  line-height: 1.65;
  padding-left: 16px;
  position: relative;
  margin-bottom: 4px;
}
.clean-list li:before {
  content: "";
  position: absolute;
  left: 2px;
  top: 9px;
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: var(--accent-primary);
}

.graph-pane {
  width: 100%;
}

.toast-notification {
  position: fixed;
  left: 50%;
  bottom: 28px;
  transform: translateX(-50%) translateY(20px);
  background: #1c1917;
  color: #ffffff;
  padding: 10px 24px;
  border-radius: 999px;
  font-size: 13px;
  font-weight: 500;
  box-shadow: var(--shadow-lg);
  opacity: 0;
  pointer-events: none;
  transition: all .25s cubic-bezier(0.16, 1, 0.3, 1);
  z-index: 999;
}
.toast-notification.show {
  opacity: 1;
  transform: translateX(-50%) translateY(0);
}

.agent-pane {
  flex: 1;
  display: flex;
  flex-direction: column;
  height: 100%;
  min-height: 0;
  overflow: hidden;
}

@media(max-width: 1000px) {
  .app-shell { flex-direction: column; }
  .sidebar-resizer,
  .resize-mask { display: none; }
  .app-sidebar {
    width: 100%;
    height: auto;
    position: static;
    border-right: none;
    border-bottom: 1px solid var(--border-card);
  }
  .tree-layout, .workbench {
    grid-template-columns: 1fr;
  }
  .rail-pane {
    position: static;
    height: auto;
  }
}
</style>
