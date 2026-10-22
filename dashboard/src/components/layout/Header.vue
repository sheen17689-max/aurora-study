<template>
  <header class="app-header" :class="{ 'farm-mode': viewMode === 'agent' }">
    <div class="header-left">
      <!-- 侧边栏展开/收起快捷触发器 -->
      <button
        v-if="viewMode === 'tree'"
        :class="['sidebar-nav-btn', sidebarCollapsed ? 'collapsed' : '']"
        @click="$emit('toggle-sidebar')"
        :title="sidebarCollapsed ? '展开文档导航 (Ctrl+B)' : '收起文档导航 (Ctrl+B)'"
      >
        <PanelLeftOpen v-if="sidebarCollapsed" :size="16" />
        <PanelLeftClose v-else :size="16" />
        <span class="btn-text">{{ sidebarCollapsed ? '展开文档导航' : '文档导航' }}</span>
      </button>

      <div v-if="viewMode !== 'tree' || sidebarCollapsed" class="logo">
        <Sparkles :size="18" class="logo-icon" />
        <span class="logo-text">Aurora</span>
      </div>

      <div class="header-tag book-tag" :class="data?.book === 'agent' ? 'agent-tag' : 'dl-tag'">
        <span class="book-badge-icon">📖</span>
        <span>{{ data?.book === 'agent' ? '卷三 · Agent 学习' : '卷一 · 深度学习' }}</span>
      </div>

      <div class="header-tag date-tag">
        {{ data?.today }} 周{{ data?.weekday }}
      </div>
      <div v-if="data?.streak > 0" class="header-tag streak-tag">
        <Flame :size="13" class="tag-icon" />
        <span>连续学习 {{ data?.streak }} 天</span>
      </div>
      <div v-else class="header-tag start-tag">
        <Sparkles :size="13" class="tag-icon" />
        <span>迈出第一步</span>
      </div>
    </div>

    <div class="header-right">
      <!-- 视图切换 -->
      <div class="view-switch">
        <button
          :class="['switch-btn', viewMode === 'tree' ? 'active' : '']"
          @click="$emit('update:viewMode', 'tree')"
        >
          <Map :size="13" class="switch-icon" />
          <span>大纲地图</span>
        </button>
        <button
          :class="['switch-btn', viewMode === 'graph' ? 'active' : '']"
          @click="$emit('update:viewMode', 'graph')"
        >
          <Network :size="13" class="switch-icon" />
          <span>知识星系</span>
        </button>
        <button
          :class="['switch-btn', viewMode === 'agent' ? 'active' : '']"
          @click="$emit('update:viewMode', 'agent')"
        >
          <Bot :size="13" class="switch-icon" />
          <span>Agent 助手</span>
        </button>
      </div>

      <!-- 主题切换 -->
      <button class="icon-btn" @click="toggleTheme" title="切换深色/浅色主题">
        <Sun v-if="isDark" :size="15" />
        <Moon v-else :size="15" />
      </button>

      <!-- 返回书架 -->
      <button class="quit-btn" @click="$emit('back-to-shelf')">
        返回书架
      </button>

      <!-- 退出 -->
      <button class="quit-btn" @click="quitApp">
        退出管家
      </button>
    </div>
  </header>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import {
  PanelLeftClose,
  PanelLeftOpen,
  Sparkles,
  Flame,
  Map,
  Network,
  Sun,
  Moon,
  Bot
} from 'lucide-vue-next';
import { shutdown } from '../../api';

const props = defineProps({
  data: Object,
  viewMode: String,
  sidebarCollapsed: Boolean
});

const emit = defineEmits(['update:viewMode', 'toast', 'toggle-sidebar', 'back-to-shelf']);

const isDark = ref(false);

const toggleTheme = () => {
  isDark.value = !isDark.value;
  if (isDark.value) {
    document.documentElement.setAttribute('data-theme', 'dark');
    localStorage.setItem('theme', 'dark');
  } else {
    document.documentElement.removeAttribute('data-theme');
    localStorage.setItem('theme', 'light');
  }
};

const quitApp = async () => {
  try {
    await shutdown();
    emit('toast', '管家服务已安全退出，可以关闭页面');
  } catch (e) {}
};

onMounted(() => {
  const saved = localStorage.getItem('theme');
  if (saved === 'dark' || (!saved && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
    isDark.value = true;
    document.documentElement.setAttribute('data-theme', 'dark');
  }
});
</script>

<style scoped>
.app-header {
  position: sticky;
  top: 0;
  z-index: 40;
  background: var(--bg-card);
  border-bottom: 1px solid var(--border-card);
  padding: 12px 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: var(--shadow-sm);
  backdrop-filter: blur(8px);
}
.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}
.sidebar-nav-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: var(--bg-subtle);
  border: 1px solid var(--border-card);
  border-radius: var(--radius-sm);
  padding: 5px 10px;
  font-size: 12.5px;
  font-weight: 600;
  color: var(--text-sub);
  cursor: pointer;
  transition: all .15s ease;
}
.sidebar-nav-btn:hover {
  background: var(--bg-card);
  border-color: var(--accent-primary);
  color: var(--accent-primary);
  box-shadow: var(--shadow-sm);
}
.sidebar-nav-btn.collapsed {
  background: var(--accent-light);
  border-color: var(--accent-primary);
  color: var(--accent-primary);
}
.sidebar-nav-btn .btn-text {
  font-size: 12px;
}
.logo {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 700;
  font-size: 16px;
  color: var(--text-main);
}
.logo-icon {
  font-size: 20px;
}
.header-tag {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-size: 12px;
  padding: 3px 10px;
  border-radius: 999px;
  font-weight: 500;
}
.date-tag {
  background: var(--bg-subtle);
  color: var(--text-sub);
}
.book-tag {
  font-weight: 600;
  border: 1px solid transparent;
}
.agent-tag {
  background: rgba(16, 185, 129, 0.12);
  color: #059669;
  border-color: rgba(16, 185, 129, 0.28);
}
.dl-tag {
  background: rgba(99, 102, 241, 0.12);
  color: #4f46e5;
  border-color: rgba(99, 102, 241, 0.28);
}
.streak-tag {
  background: rgba(245, 158, 11, 0.12);
  color: #d97706;
  border: 1px solid rgba(245, 158, 11, 0.25);
  font-weight: 600;
}
.start-tag {
  background: var(--accent-light);
  color: var(--accent-primary);
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}
.view-switch {
  display: flex;
  background: var(--bg-subtle);
  padding: 3px;
  border-radius: var(--radius-sm);
  gap: 2px;
}
.switch-btn {
  border: none;
  background: transparent;
  padding: 4px 10px;
  font-size: 12px;
  font-weight: 500;
  color: var(--text-sub);
  border-radius: 4px;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 5px;
  transition: all .15s ease;
}
.switch-btn:hover {
  color: var(--text-main);
}
.switch-btn.active {
  background: var(--bg-card);
  color: var(--accent-primary);
  font-weight: 600;
  box-shadow: var(--shadow-sm);
}

.icon-btn {
  background: var(--bg-subtle);
  border: 1px solid var(--border-card);
  border-radius: var(--radius-sm);
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-size: 14px;
  transition: all .15s;
}
.icon-btn:hover {
  background: var(--border-card);
}

.quit-btn {
  background: transparent;
  border: 1px solid var(--border-card);
  color: var(--text-muted);
  border-radius: var(--radius-sm);
  padding: 5px 12px;
  font-size: 12px;
  cursor: pointer;
  transition: all .15s;
}
.quit-btn:hover {
  color: var(--text-main);
  border-color: var(--border-subtle);
}

/* ============ 星露谷像素风（仅 Agent 助手视图） ============ */
.app-header.farm-mode {
  background-color: #7a4a2b;
  background-image:
    repeating-linear-gradient(90deg, rgba(62, 36, 18, 0.3) 0 3px, transparent 3px 108px),
    linear-gradient(180deg, #855431 0%, #74462a 100%);
  border-bottom: 4px solid #3e2412;
  box-shadow:
    inset 0 2px 0 rgba(255, 235, 200, 0.12),
    0 3px 0 rgba(0, 0, 0, 0.18);
  backdrop-filter: none;
  font-family: 'ZCOOL KuaiLe', 'Microsoft YaHei', 'PingFang SC', sans-serif;
  letter-spacing: 0.03em;
}

.farm-mode .logo-text {
  color: #ffe9bd;
  text-shadow: 1px 1px 0 #3e2412;
}

.farm-mode .logo-icon {
  color: #a8d95b;
}

/* 木牌标签 */
.farm-mode .header-tag {
  border-radius: 6px;
  border: 2px solid #3e2412;
  box-shadow: 0 2px 0 #3e2412;
  padding: 4px 12px;
  font-family: inherit;
}

.farm-mode .date-tag {
  background: #edd9ae;
  color: #4a2e17;
}

.farm-mode .dl-tag,
.farm-mode .agent-tag {
  background: #3d8b37;
  border-color: #2d6b28;
  color: #fffbe8;
  text-shadow: 1px 1px 0 #2d6b28;
  box-shadow: inset 0 2px 0 #a8d95b, 0 2px 0 #3e2412;
}

.farm-mode .streak-tag {
  background: #e8a33d;
  border-color: #a86f1d;
  color: #fffbe8;
  text-shadow: 1px 1px 0 #a86f1d;
  box-shadow: inset 0 2px 0 #f7cd7f, 0 2px 0 #3e2412;
}

.farm-mode .start-tag {
  background: #b07fe8;
  border-color: #6b4a94;
  color: #fffbe8;
  text-shadow: 1px 1px 0 #6b4a94;
  box-shadow: inset 0 2px 0 #d4b3f5, 0 2px 0 #3e2412;
}

/* 视图切换 = 挂在栅栏上的木牌组 */
.farm-mode .view-switch {
  background: rgba(62, 36, 18, 0.45);
  border: 2px solid #3e2412;
  border-radius: 8px;
  padding: 4px;
  box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.35);
}

.farm-mode .switch-btn {
  color: #d9c49a;
  border-radius: 5px;
  font-family: inherit;
  letter-spacing: 0.04em;
  border: 2px solid transparent;
}

.farm-mode .switch-btn:hover {
  color: #ffe9bd;
}

.farm-mode .switch-btn.active {
  background: #3d8b37;
  border-color: #2d6b28;
  color: #fffbe8;
  text-shadow: 1px 1px 0 #2d6b28;
  box-shadow: inset 0 2px 0 #a8d95b, 0 2px 0 #3e2412;
  font-weight: 600;
}

/* 主题切换 + 退出按钮 = 米色小木牌 */
.farm-mode .icon-btn {
  background: #edd9ae;
  border: 2px solid #3e2412;
  border-radius: 6px;
  color: #4a2e17;
  box-shadow: 0 2px 0 #3e2412;
}

.farm-mode .icon-btn:hover {
  background: #f5e6c8;
}

.farm-mode .quit-btn {
  background: #edd9ae;
  border: 2px solid #3e2412;
  color: #4a2e17;
  border-radius: 6px;
  font-family: inherit;
  font-weight: 600;
  letter-spacing: 0.04em;
  box-shadow: 0 2px 0 #3e2412;
  transition: filter 0.15s, transform 0.1s;
}

.farm-mode .quit-btn:hover {
  filter: brightness(1.06);
  color: #4a2e17;
}

.farm-mode .quit-btn:active {
  transform: translateY(1px);
  box-shadow: 0 1px 0 #3e2412;
}
</style>
