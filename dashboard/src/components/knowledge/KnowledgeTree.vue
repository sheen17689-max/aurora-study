<template>
  <div :class="['file-nav-card', bare ? 'bare' : '']">
    <!-- 标题与折叠按钮 -->
    <div class="nav-title-row">
      <div class="nav-title-text-group">
        <BookOpen :size="16" class="nav-brand-icon" />
        <h2 class="nav-title">知识目录</h2>
      </div>
      <button
        class="sidebar-toggle-btn"
        @click="$emit('toggle-sidebar')"
        title="收起侧边栏 (Ctrl+B)"
        aria-label="收起侧边栏"
      >
        <PanelLeftClose :size="16" />
      </button>
    </div>

    <!-- 搜索 -->
    <div class="search-box">
      <Search :size="13" class="search-icon" />
      <input
        type="text"
        v-model="searchQuery"
        class="search-input"
        placeholder="搜索知识点..."
      />
      <button v-if="searchQuery" class="clear-btn" @click="searchQuery = ''">✕</button>
    </div>

    <!-- 掌握度筛选 -->
    <div class="filter-row">
      <button
        :class="['f-btn', currentFilter === 'all' ? 'active' : '']"
        @click="currentFilter = 'all'"
      >
        全部
      </button>
      <button
        v-for="f in levelFilters"
        :key="f.lv"
        :class="['f-btn', currentFilter === f.lv ? 'active' : '']"
        @click="currentFilter = f.lv"
      >
        <span class="f-dot" :style="{ background: f.color, boxShadow: `0 0 6px ${f.color}88` }"></span>
        <span>{{ f.name }}</span>
      </button>
    </div>

    <!-- 下一步推荐卡片 (3D 凸起质感) -->
    <div
      v-if="nextRecommendation"
      class="next-step-bento"
      @click="handleNextClick"
      title="点击快速进入下一步主攻学习"
    >
      <div class="next-step-badge-icon">
        <Sparkles :size="14" />
      </div>
      <div class="next-step-info">
        <div class="next-step-tag">NEXT TARGET</div>
        <div class="next-step-text">{{ nextRecommendation.label }}</div>
      </div>
    </div>

    <!-- 3D 凸起卡片知识体系树 -->
    <div class="nav-tree-bento">
      <div
        v-for="sec in filteredSections"
        :key="sec.name"
        class="bento-section-group"
      >
        <!-- 章节头卡片 -->
        <div
          :class="['section-header-card', { 'is-active-section': sec.current }]"
          @click="toggleSection(sec.name)"
        >
          <div class="section-header-left">
            <span class="section-arrow-badge">
              <ChevronDown v-if="!isCollapsed(sec.name)" :size="13" />
              <ChevronRight v-else :size="13" />
            </span>
            <span class="section-name">{{ sec.name }}</span>
            <span v-if="sec.current" class="current-pulse-dot" title="当前主攻阶段"></span>
          </div>

          <div class="section-header-right">
            <span class="section-progress-pill">
              {{ (sec.counts?.['🔵'] || 0) + (sec.counts?.['🟢'] || 0) }}/{{ sec.total ?? sec.items?.length }}
            </span>
          </div>
        </div>

        <!-- 章节内卡片网格列表 -->
        <div v-show="!isCollapsed(sec.name)" class="section-cards-list">
          <!-- 章节核心导语 / 阶段闭环说明 -->
          <div v-if="sec.note" class="section-note-banner">
            <span class="section-note-icon">✦</span>
            <span class="section-note-text">{{ sec.note }}</span>
          </div>
          <template v-for="it in sec.filteredItems" :key="it.name">
            <!-- 分组折叠容器（下辖子项） -->
            <div v-if="it.children && it.children.length" class="bento-subgroup-box">
              <div
                class="bento-subgroup-header"
                @click="toggleGroup(sec.name + '/' + it.name)"
              >
                <div class="subgroup-header-left">
                  <Layers :size="12" class="subgroup-icon" />
                  <span class="subgroup-name">{{ it.name }}</span>
                </div>
                <span class="subgroup-arrow">
                  <ChevronDown v-if="!isGroupCollapsed(sec.name + '/' + it.name)" :size="11" />
                  <ChevronRight v-else :size="11" />
                </span>
              </div>

              <div
                v-show="!isGroupCollapsed(sec.name + '/' + it.name)"
                class="subgroup-cards-list"
              >
                <div
                  v-for="c in it.children"
                  :key="c.name"
                  :class="[
                    'bento-3d-card',
                    'bento-child-card',
                    {
                      'is-active': c.name === activeName || c.link === activeName,
                      'has-note': c.hasNote
                    }
                  ]"
                  :title="c.note || c.name"
                  @click="$emit('open-note', c.link || c.name, c)"
                >
                  <div class="card-inner">
                    <div class="card-main-row">
                      <span
                        class="status-gem"
                        :style="{
                          background: getLevelColor(c.level),
                          boxShadow: `0 0 6px ${getLevelColor(c.level)}99`
                        }"
                      ></span>
                      <span class="card-title">{{ c.name }}</span>
                      <FileText v-if="c.hasNote" :size="12" class="note-chip-icon" title="包含深度笔记" />
                    </div>
                    <div v-if="c.note" class="card-snippet">
                      {{ c.note }}
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- 独立 3D 凸起卡片 -->
            <div
              v-else
              :class="[
                'bento-3d-card',
                {
                  'is-active': it.name === activeName || it.link === activeName,
                  'has-note': it.hasNote
                }
              ]"
              :title="it.note || it.name"
              @click="$emit('open-note', it.link || it.name, it)"
            >
              <div class="card-inner">
                <div class="card-main-row">
                  <span
                    class="status-gem"
                    :style="{
                      background: getLevelColor(it.level),
                      boxShadow: `0 0 6px ${getLevelColor(it.level)}99`
                    }"
                  ></span>
                  <span class="card-title">{{ it.name }}</span>
                  <FileText v-if="it.hasNote" :size="12" class="note-chip-icon" title="包含深度笔记" />
                </div>
                <div v-if="it.note" class="card-snippet">
                  {{ it.note }}
                </div>
              </div>
            </div>
          </template>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import {
  BookOpen,
  Search,
  Sparkles,
  ChevronDown,
  ChevronRight,
  Layers,
  FileText,
  PanelLeftClose
} from 'lucide-vue-next';

const props = defineProps({
  data: Object,
  bare: Boolean,
  activeName: String
});

const emit = defineEmits(['open-note', 'toggle-sidebar']);

const searchQuery = ref('');
const currentFilter = ref('all');
const collapsedSections = ref({});
const collapsedGroups = ref({});

const levelFilters = [
  { lv: '🟢', name: '掌握', color: '#059669' },
  { lv: '🔵', name: '理解', color: '#2563eb' },
  { lv: '🟡', name: '接触', color: '#d97706' },
  { lv: '⚪', name: '未学', color: '#94a3b8' }
];

const getLevelColor = (lv) => {
  const map = {
    '🟢': '#059669',
    '🔵': '#2563eb',
    '🟡': '#d97706',
    '⚪': '#94a3b8'
  };
  return map[lv] || '#94a3b8';
};

const isCollapsed = (secName) => {
  return !!collapsedSections.value[secName];
};

const toggleSection = (secName) => {
  collapsedSections.value[secName] = !collapsedSections.value[secName];
};

const isGroupCollapsed = (groupKey) => {
  return !!collapsedGroups.value[groupKey];
};

const toggleGroup = (groupKey) => {
  collapsedGroups.value[groupKey] = !collapsedGroups.value[groupKey];
};

// 提炼下一步主攻目标
const nextRecommendation = computed(() => {
  const route = props.data?.route;
  if (!route?.next || !route.next.length) return null;
  const firstItem = route.next[0];
  const match = firstItem.match(/\[\[(.*?)\]\]/);
  const targetNote = match ? match[1] : null;
  const label = firstItem.replace(/\[\[|\]\]/g, '').replace(/^[0-9.]+\s*/, '');
  return { label, targetNote };
});

const handleNextClick = () => {
  if (nextRecommendation.value?.targetNote) {
    emit('open-note', nextRecommendation.value.targetNote);
  }
};

const filteredSections = computed(() => {
  if (!props.data?.framework?.sections) return [];
  const q = searchQuery.value.trim().toLowerCase();
  const f = currentFilter.value;

  return props.data.framework.sections
    .map((sec) => {
      const items = sec.items || [];
      const filteredItems = items
        .map((it) => {
          if (it.children && it.children.length) {
            const filteredChildren = it.children.filter((c) => {
              const matchQ = !q || c.name.toLowerCase().includes(q) || (c.note && c.note.toLowerCase().includes(q));
              const matchF = f === 'all' || c.level === f;
              return matchQ && matchF;
            });
            if (filteredChildren.length > 0) {
              return { ...it, children: filteredChildren };
            }
            return null;
          } else {
            const matchQ = !q || it.name.toLowerCase().includes(q) || (it.note && it.note.toLowerCase().includes(q));
            const matchF = f === 'all' || it.level === f;
            return matchQ && matchF ? it : null;
          }
        })
        .filter(Boolean);

      return {
        ...sec,
        filteredItems
      };
    })
    .filter((sec) => sec.filteredItems.length > 0);
});
</script>

<style scoped>
.file-nav-card {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: var(--bg-card);
  overflow: hidden;
}

/* 顶部标题行 */
.nav-title-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 18px 10px;
  border-bottom: 1px solid var(--border-card);
}
.nav-title-text-group {
  display: flex;
  align-items: center;
  gap: 8px;
}
.nav-brand-icon {
  color: var(--accent-primary);
}
.nav-title {
  font-size: 14.5px;
  font-weight: 700;
  color: var(--text-main);
}
.sidebar-toggle-btn {
  border: none;
  background: transparent;
  color: var(--text-muted);
  cursor: pointer;
  padding: 4px;
  border-radius: var(--radius-sm);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.15s ease;
}
.sidebar-toggle-btn:hover {
  background: var(--bg-subtle);
  color: var(--text-main);
}

/* 搜索框 */
.search-box {
  position: relative;
  margin: 10px 14px 6px;
  display: flex;
  align-items: center;
}
.search-icon {
  position: absolute;
  left: 10px;
  color: var(--text-muted);
  pointer-events: none;
}
.search-input {
  width: 100%;
  padding: 6px 28px 6px 30px;
  font-size: 12.5px;
  background: var(--bg-subtle);
  border: 1px solid var(--border-card);
  border-radius: var(--radius-sm);
  color: var(--text-main);
  outline: none;
  transition: all 0.15s ease;
}
.search-input:focus {
  border-color: var(--accent-primary);
  background: var(--bg-card);
  box-shadow: 0 0 0 3px var(--accent-light);
}
.clear-btn {
  position: absolute;
  right: 8px;
  border: none;
  background: transparent;
  font-size: 11px;
  color: var(--text-muted);
  cursor: pointer;
}

/* 筛选胶囊 */
.filter-row {
  display: flex;
  gap: 4px;
  padding: 4px 14px 8px;
  overflow-x: auto;
}
.f-btn {
  border: 1px solid var(--border-card);
  background: var(--bg-card);
  font-size: 11.5px;
  color: var(--text-sub);
  padding: 2px 8px;
  border-radius: 999px;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 4px;
  white-space: nowrap;
  transition: all 0.12s;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.02);
}
.f-btn:hover {
  background: var(--bg-subtle);
  color: var(--text-main);
}
.f-btn.active {
  background: var(--accent-light);
  border-color: rgba(79, 70, 229, 0.3);
  color: var(--accent-primary);
  font-weight: 600;
}
.f-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
}

/* 下一步推荐卡片 (3D 凸起质感) */
.next-step-bento {
  margin: 4px 14px 10px;
  padding: 8px 12px;
  background: linear-gradient(135deg, var(--accent-light) 0%, rgba(79, 70, 229, 0.04) 100%);
  border: 1px solid rgba(79, 70, 229, 0.22);
  border-radius: 12px;
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  box-shadow:
    0 1px 0 rgba(255, 255, 255, 0.95) inset,
    0 2px 5px rgba(79, 70, 229, 0.06),
    0 1px 2px rgba(0, 0, 0, 0.03);
  transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}
.next-step-bento:hover {
  transform: translateY(-2px);
  border-color: var(--accent-primary);
  box-shadow:
    0 1px 0 rgba(255, 255, 255, 1) inset,
    0 5px 12px rgba(79, 70, 229, 0.16);
}
.next-step-badge-icon {
  width: 26px;
  height: 26px;
  border-radius: 8px;
  background: var(--accent-primary);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  box-shadow: 0 2px 5px rgba(79, 70, 229, 0.35);
}
.next-step-info {
  flex: 1;
  min-width: 0;
}
.next-step-tag {
  font-size: 9.5px;
  font-weight: 800;
  color: var(--accent-primary);
  letter-spacing: 0.06em;
}
.next-step-text {
  font-size: 12.5px;
  font-weight: 600;
  color: var(--text-main);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* 3D 知识树容器 */
.nav-tree-bento {
  flex: 1;
  overflow-y: auto;
  padding: 4px 12px 24px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

/* 章节 Bento 容器 */
.bento-section-group {
  background: var(--bg-subtle);
  border: 1px solid var(--border-card);
  border-radius: 13px;
  padding: 6px;
  transition: all 0.2s ease;
}

.section-header-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 7px 10px;
  border-radius: 8px;
  cursor: pointer;
  user-select: none;
  transition: all 0.15s ease;
}
.section-header-card:hover {
  background: rgba(0, 0, 0, 0.03);
}
[data-theme="dark"] .section-header-card:hover {
  background: rgba(255, 255, 255, 0.04);
}
.section-header-left {
  display: flex;
  align-items: center;
  gap: 7px;
  min-width: 0;
  flex: 1;
}
.section-arrow-badge {
  color: var(--text-muted);
  display: flex;
  align-items: center;
}
.section-name {
  font-size: 13px;
  font-weight: 700;
  color: var(--text-main);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.current-pulse-dot {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: var(--accent-primary);
  box-shadow: 0 0 0 2px var(--accent-light);
  flex-shrink: 0;
}
.section-progress-pill {
  font-size: 10.5px;
  font-weight: 600;
  color: var(--text-muted);
  background: var(--bg-card);
  border: 1px solid var(--border-card);
  padding: 2px 7px;
  border-radius: 999px;
}

.section-cards-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-top: 4px;
}

.section-note-banner {
  margin: 2px 2px 6px;
  padding: 7px 10px;
  background: linear-gradient(135deg, rgba(79, 70, 229, 0.05) 0%, rgba(79, 70, 229, 0.01) 100%);
  border: 1px dashed rgba(79, 70, 229, 0.25);
  border-radius: 9px;
  font-size: 11px;
  color: var(--text-muted);
  line-height: 1.45;
  display: flex;
  align-items: flex-start;
  gap: 6px;
}
.section-note-icon {
  color: var(--accent-primary);
  font-size: 11px;
  flex-shrink: 0;
  margin-top: 1px;
}
.section-note-text {
  flex: 1;
  word-break: break-word;
}

/* ====================================================
   3D 凸起质感卡片 (Tactile 3D Bento Card)
   ==================================================== */
.bento-3d-card {
  position: relative;
  background: var(--bg-card);
  border: 1px solid var(--border-card);
  border-radius: 10px;
  padding: 8px 11px;
  cursor: pointer;
  user-select: none;
  box-shadow:
    0 1px 0 rgba(255, 255, 255, 0.95) inset,
    0 1px 2px rgba(0, 0, 0, 0.04),
    0 3px 6px -1px rgba(0, 0, 0, 0.03);
  transition: all 0.18s cubic-bezier(0.16, 1, 0.3, 1);
}
[data-theme="dark"] .bento-3d-card {
  box-shadow:
    0 1px 0 rgba(255, 255, 255, 0.05) inset,
    0 2px 5px rgba(0, 0, 0, 0.35);
}

/* 3D 浮起悬停 */
.bento-3d-card:hover {
  transform: translateY(-2px);
  border-color: rgba(79, 70, 229, 0.35);
  box-shadow:
    0 1px 0 rgba(255, 255, 255, 1) inset,
    0 5px 12px -2px rgba(79, 70, 229, 0.14),
    0 2px 4px rgba(0, 0, 0, 0.04);
}
/* 物理下沉点击反馈 */
.bento-3d-card:active {
  transform: translateY(1px) scale(0.99);
  box-shadow:
    0 1px 2px rgba(0, 0, 0, 0.06),
    0 1px 0 rgba(255, 255, 255, 0.5) inset;
}

/* 选中高亮状态 */
.bento-3d-card.is-active {
  background: linear-gradient(180deg, var(--accent-light) 0%, var(--bg-card) 100%);
  border-color: var(--accent-primary);
  box-shadow:
    0 0 0 1.5px var(--accent-primary),
    0 4px 12px rgba(79, 70, 229, 0.18),
    0 1px 0 rgba(255, 255, 255, 0.9) inset;
}

.card-inner {
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.card-main-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.status-gem {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  flex-shrink: 0;
  transition: transform 0.2s ease;
}
.bento-3d-card:hover .status-gem {
  transform: scale(1.25);
}

.card-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-main);
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.bento-3d-card.is-active .card-title {
  color: var(--accent-primary);
  font-weight: 700;
}

.note-chip-icon {
  color: var(--text-muted);
  flex-shrink: 0;
}
.bento-3d-card.is-active .note-chip-icon {
  color: var(--accent-primary);
}

.card-snippet {
  font-size: 11px;
  color: var(--text-muted);
  line-height: 1.4;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  padding-left: 15px;
}

/* 分组折叠小节 */
.bento-subgroup-box {
  background: rgba(0, 0, 0, 0.02);
  border: 1px dashed var(--border-card);
  border-radius: 10px;
  padding: 4px;
}
[data-theme="dark"] .bento-subgroup-box {
  background: rgba(255, 255, 255, 0.02);
}
.bento-subgroup-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 5px 8px;
  font-size: 12px;
  font-weight: 600;
  color: var(--text-sub);
  cursor: pointer;
  border-radius: 6px;
}
.bento-subgroup-header:hover {
  background: var(--bg-card);
  color: var(--text-main);
}
.subgroup-header-left {
  display: flex;
  align-items: center;
  gap: 6px;
}
.subgroup-icon {
  color: var(--text-muted);
}
.subgroup-arrow {
  color: var(--text-muted);
  display: flex;
}

.subgroup-cards-list {
  display: flex;
  flex-direction: column;
  gap: 5px;
  margin-top: 4px;
  padding-left: 6px;
}
.bento-child-card {
  padding: 7px 10px;
  border-radius: 8px;
}
</style>
