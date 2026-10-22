<template>
  <div class="agent-workspace" :class="{ 'sidebar-collapsed': !isSidebarOpen }">
    <!-- 历史会话左侧边栏 -->
    <aside class="chat-sidebar" :class="{ collapsed: !isSidebarOpen }">
      <div class="sidebar-top">
        <div class="sidebar-header-row">
          <div class="sidebar-brand">
            <MessageSquare :size="16" class="sidebar-brand-icon" />
            <span class="sidebar-brand-text">历史会话</span>
          </div>
          <button
            type="button"
            class="sidebar-collapse-btn"
            title="收起侧边栏"
            @click="toggleSidebar"
          >
            <PanelLeftClose :size="16" />
          </button>
        </div>
        <button
          type="button"
          class="sidebar-new-chat-btn"
          @click="createNewSession"
        >
          <Plus :size="16" />
          <span>新建对话</span>
        </button>
      </div>

      <!-- 会话列表滚动区 -->
      <div class="session-list-scroll">
        <div
          v-for="s in sessions"
          :key="s.id"
          class="session-item"
          :class="{ active: s.id === currentSessionId }"
          @click="switchSession(s)"
        >
          <div class="session-item-icon">
            <MessageSquare :size="14" />
          </div>

          <div class="session-item-content">
            <!-- 编辑标题模式 -->
            <div
              v-if="editingSessionId === s.id"
              class="session-rename-wrap"
              @click.stop
            >
              <input
                ref="renameInputRef"
                v-model="editTitleInput"
                class="rename-input"
                @keydown.enter="confirmRename(s)"
                @keydown.esc="cancelRename"
                @blur="confirmRename(s)"
              />
            </div>
            <!-- 正常显示模式 -->
            <template v-else>
              <div class="session-item-title" :title="s.title">
                {{ s.title }}
              </div>
              <div class="session-item-meta">
                <span>{{ formatTimeAgo(s.updatedAt || s.createdAt) }}</span>
                <span v-if="s.messages && s.messages.length" class="meta-dot">·</span>
                <span v-if="s.messages && s.messages.length">{{ s.messages.length }}条</span>
              </div>
            </template>
          </div>

          <!-- 浮动操作按钮 -->
          <div
            v-if="editingSessionId !== s.id"
            class="session-item-actions"
            @click.stop
          >
            <button
              type="button"
              class="item-act-btn"
              title="重命名"
              @click="startRename(s)"
            >
              <Edit3 :size="12" />
            </button>
            <button
              type="button"
              class="item-act-btn delete"
              title="删除此会话"
              @click="confirmDeleteSession(s)"
            >
              <Trash2 :size="12" />
            </button>
          </div>
        </div>

        <div v-if="sessions.length === 0" class="session-empty">
          <span>暂无历史会话</span>
        </div>
      </div>

      <!-- 侧边栏底部 -->
      <div class="sidebar-bottom">
        <div class="book-tag">
          <span class="book-tag-dot"></span>
          <span>《{{ bookName }}》</span>
        </div>
        <button
          v-if="sessions.length > 1"
          type="button"
          class="sidebar-clear-btn"
          title="清空当前书籍的所有历史会话"
          @click="handleClearAllSessions"
        >
          <Trash :size="13" />
          <span>清空</span>
        </button>
      </div>
    </aside>

    <!-- 右侧主对话视口 -->
    <main class="chat-main">
      <!-- 顶部状态工具栏 -->
      <header class="assistant-bar">
        <div class="bar-left">
          <button
            v-if="!isSidebarOpen"
            type="button"
            class="sidebar-expand-btn"
            title="展开历史会话列表"
            @click="toggleSidebar"
          >
            <PanelLeftOpen :size="17" />
          </button>
          <div class="agent-avatar">
            <Sparkles :size="18" class="avatar-icon" />
          </div>
          <div class="agent-meta">
            <div class="agent-title-wrap">
              <span class="agent-title">{{ currentSession?.title || 'Aurora 智能研学导师' }}</span>
              <span class="status-indicator online" title="LangGraph 状态机在线">
                <span class="pulse-dot"></span> 运行时就绪
              </span>
            </div>
            <p class="agent-sub">
              已挂载《{{ bookName }}》本地知识库 · 支持查阅笔记、答辩升级与自动记日记
            </p>
          </div>
        </div>

        <div class="bar-right">
          <button
            type="button"
            class="subtle-btn"
            title="开启新话题"
            @click="createNewSession"
          >
            <Plus :size="14" />
            <span>新话题</span>
          </button>
          <button
            type="button"
            class="config-btn"
            :class="{ 'has-key': config.has_key }"
            title="配置大模型 API Key"
            @click="showConfigModal = true"
          >
            <Settings :size="15" />
            <span>{{ config.has_key ? '模型配置' : '配置 Key' }}</span>
          </button>
        </div>
      </header>

    <!-- 消息对话主视口 -->
    <div ref="chatScrollRef" class="chat-viewport">
      <!-- 空状态欢迎卡片 -->
      <div v-if="messages.length === 0" class="welcome-container">
        <div class="hero-box">
          <div class="hero-badge">
            <Bot :size="32" class="hero-icon" />
          </div>
          <h2 class="hero-title">你好！我是你的专属 AI 研学私教</h2>
          <p class="hero-desc">
            基于 <strong>LangGraph ReAct</strong> 架构编排，已接驳你的本地 Markdown
            知识库、知识框架大纲与日记流。
          </p>

          <div class="capabilities-grid">
            <div class="cap-card">
              <div class="cap-icon">📖</div>
              <div class="cap-name">查阅本地笔记</div>
              <div class="cap-desc">先看本地笔记再作答，拒绝幻觉胡说</div>
            </div>
            <div class="cap-card">
              <div class="cap-icon">🎙️</div>
              <div class="cap-name">苏格拉底答辩</div>
              <div class="cap-desc">用自测考题考查你，启发深层思考</div>
            </div>
            <div class="cap-card">
              <div class="cap-icon">🟢</div>
              <div class="cap-name">自动回写掌握度</div>
              <div class="cap-desc">答辩通过自动将知识点升级为理解/掌握</div>
            </div>
            <div class="cap-card">
              <div class="cap-icon">📝</div>
              <div class="cap-name">一键归整日记</div>
              <div class="cap-desc">提取精要内容自动追加进今日学习流水</div>
            </div>
          </div>

          <div class="suggestion-section">
            <p class="sug-title">试着对我说：</p>
            <div class="sug-chips">
              <button
                v-for="(sug, idx) in promptSuggestions"
                :key="idx"
                type="button"
                class="sug-chip"
                @click="sendPrompt(sug.text)"
              >
                <span class="chip-icon">{{ sug.icon }}</span>
                <span class="chip-text">{{ sug.label }}</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- 消息流列表 -->
      <div v-else class="messages-stream">
        <div
          v-for="(msg, mIdx) in messages"
          :key="mIdx"
          class="message-row"
          :class="msg.role"
        >
          <!-- 头像 -->
          <div class="avatar-cell">
            <div v-if="msg.role === 'user'" class="user-avatar">我</div>
            <div v-else class="bot-avatar">
              <Sparkles :size="14" />
            </div>
          </div>

          <!-- 气泡内容 -->
          <div class="bubble-cell">
            <div class="bubble-header">
              <span class="speaker-name">{{ msg.role === 'user' ? '我' : '研学导师' }}</span>
              <span class="speaker-time">{{ msg.time }}</span>
            </div>

            <!-- 工具调用折叠卡片列表 -->
            <div v-if="msg.tools && msg.tools.length" class="tool-calls-stack">
              <details
                v-for="(t, tIdx) in msg.tools"
                :key="tIdx"
                class="tool-card"
                :open="t.status === 'running'"
              >
                <summary class="tool-summary">
                  <div class="tool-sum-left">
                    <span
                      class="tool-status-badge"
                      :class="t.status"
                    >
                      <span v-if="t.status === 'running'" class="spinner"></span>
                      <span v-else>✓</span>
                    </span>
                    <span class="tool-name">
                      {{ formatToolTitle(t.name) }}
                    </span>
                  </div>
                  <span class="tool-state-tag">
                    {{ t.status === 'running' ? '正在执行...' : '调用完成' }}
                  </span>
                </summary>
                <div class="tool-body">
                  <div v-if="t.input" class="tool-section">
                    <div class="tool-label">入参契约：</div>
                    <pre><code>{{ formatJson(t.input) }}</code></pre>
                  </div>
                  <div v-if="t.output" class="tool-section">
                    <div class="tool-label">返回观察：</div>
                    <pre><code>{{ t.output }}</code></pre>
                  </div>
                </div>
              </details>
            </div>

            <!-- 消息正文 -->
            <!-- 流式等待首字节：气泡内显示思考点，避免空羊皮纸+光标掉到气泡外 -->
            <div
              v-if="msg.streaming && !msg.content"
              class="markdown-body thinking-bubble"
            >
              <span class="thinking-dot"></span>
              <span class="thinking-dot"></span>
              <span class="thinking-dot"></span>
            </div>
            <div
              v-else
              class="markdown-body"
              v-html="renderBubble(msg)"
            ></div>
          </div>
        </div>
      </div>
    </div>

    <!-- 底部输入操作栏 -->
    <footer class="assistant-input-area">
      <!-- 快捷灵感药丸条 -->
      <div v-if="messages.length > 0" class="floating-quick-chips">
        <button
          v-for="(sug, idx) in promptSuggestions"
          :key="idx"
          type="button"
          class="mini-chip"
          @click="sendPrompt(sug.text)"
        >
          {{ sug.icon }} {{ sug.label }}
        </button>
      </div>

      <div class="input-form">
        <textarea
          ref="textareaRef"
          v-model="inputQuery"
          class="chat-textarea"
          :placeholder="isStreaming ? '研学助手正在思考与调用工具中...' : '向研学助手提问、发起答辩或记录学习流水... (Enter 发送，Shift+Enter 换行)'"
          :disabled="isStreaming"
          rows="1"
          @keydown="handleKeydown"
          @input="autoResizeTextarea"
        ></textarea>
        <div class="form-actions">
          <button
            v-if="isStreaming"
            type="button"
            class="stop-btn"
            @click="stopGeneration"
          >
            <Square :size="14" />
            <span>停止</span>
          </button>
          <button
            v-else
            type="button"
            class="send-btn"
            :disabled="!inputQuery.trim()"
            @click="handleSubmit"
          >
            <Send :size="15" />
            <span>发送</span>
          </button>
        </div>
      </div>
    </footer>
    </main>

    <!-- 大模型配置弹窗 Modal -->
    <transition name="modal-fade">
      <div
        v-if="showConfigModal"
        class="modal-overlay"
        @click.self="showConfigModal = false"
      >
        <div class="config-modal">
          <div class="modal-header">
            <div class="m-title-wrap">
              <Settings :size="18" class="m-icon" />
              <h3>大模型与 API 配置</h3>
            </div>
            <button
              type="button"
              class="m-close"
              @click="showConfigModal = false"
            >
              ✕
            </button>
          </div>

          <form class="modal-body" @submit.prevent="handleSaveConfig">
            <div class="form-group">
              <label>快捷选择提供商</label>
              <div class="provider-presets">
                <button
                  type="button"
                  class="preset-btn"
                  :class="{ active: configForm.provider === 'deepseek' }"
                  @click="applyPreset('deepseek')"
                >
                  DeepSeek
                </button>
                <button
                  type="button"
                  class="preset-btn"
                  :class="{ active: configForm.provider === 'openai' }"
                  @click="applyPreset('openai')"
                >
                  OpenAI
                </button>
                <button
                  type="button"
                  class="preset-btn"
                  :class="{ active: configForm.provider === 'kimi' }"
                  @click="applyPreset('kimi')"
                >
                  Kimi (Moonshot)
                </button>
                <button
                  type="button"
                  class="preset-btn"
                  :class="{ active: configForm.provider === 'ollama' }"
                  @click="applyPreset('ollama')"
                >
                  本地 Ollama
                </button>
              </div>
            </div>

            <div class="form-group">
              <label for="cfg-base-url">API Base URL (接口地址)</label>
              <input
                id="cfg-base-url"
                v-model="configForm.base_url"
                type="text"
                class="cfg-input"
                placeholder="例如: https://api.deepseek.com/v1"
                required
              />
            </div>

            <div class="form-group">
              <label for="cfg-api-key">API Key (密钥)</label>
              <input
                id="cfg-api-key"
                v-model="configForm.api_key"
                type="password"
                class="cfg-input"
                :placeholder="config.has_key ? `已配置: ${config.api_key_masked}` : '填入 sk-xxx 密钥（仅保存在本地）'"
              />
              <span class="cfg-hint">
                🔒 密钥仅保存在本地 `agent_config.json`，不会上传任何外部服务器。
              </span>
            </div>

            <div class="form-row-2">
              <div class="form-group">
                <label for="cfg-model">模型名称 (Model)</label>
                <input
                  id="cfg-model"
                  v-model="configForm.model"
                  type="text"
                  class="cfg-input"
                  placeholder="例如: deepseek-chat"
                  required
                />
              </div>
              <div class="form-group">
                <label for="cfg-temp">采样温度 (Temperature: {{ configForm.temperature }})</label>
                <input
                  id="cfg-temp"
                  v-model.number="configForm.temperature"
                  type="range"
                  min="0"
                  max="1"
                  step="0.05"
                  class="cfg-range"
                />
              </div>
            </div>

            <div class="modal-footer">
              <button
                type="button"
                class="cancel-btn"
                @click="showConfigModal = false"
              >
                取消
              </button>
              <button type="submit" class="save-btn" :disabled="savingConfig">
                {{ savingConfig ? '保存中...' : '保存配置' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { computed, nextTick, onMounted, ref, watch } from 'vue';
import {
  Sparkles,
  Bot,
  Send,
  Square,
  Settings,
  Trash2,
  Trash,
  Plus,
  MessageSquare,
  PanelLeftClose,
  PanelLeftOpen,
  Edit3,
} from 'lucide-vue-next';
import { getCurrentBook, fetchAgentConfig, saveAgentConfig } from '../../api';
import { renderMarkdown } from '../../utils/markdown';

const props = defineProps({
  data: Object,
});

const emit = defineEmits(['open-note', 'update-level', 'toast']);

const currentBook = computed(() => getCurrentBook() || 'dl');
const bookName = computed(() => (currentBook.value === 'agent' ? 'Agent 学习' : '深度学习'));

const chatScrollRef = ref(null);
const textareaRef = ref(null);
const renameInputRef = ref(null);
const inputQuery = ref('');
const isStreaming = ref(false);
let abortController = null;

// 侧边栏展开状态（持久化）
const isSidebarOpen = ref(localStorage.getItem('aurora_chat_sidebar_open') !== 'false');
const toggleSidebar = () => {
  isSidebarOpen.value = !isSidebarOpen.value;
  localStorage.setItem('aurora_chat_sidebar_open', String(isSidebarOpen.value));
};

// 多会话管理状态
const sessions = ref([]);
const currentSessionId = ref('');
const editingSessionId = ref(null);
const editTitleInput = ref('');

const currentSession = computed(() => {
  return sessions.value.find((s) => s.id === currentSessionId.value) || null;
});

// 当前展示的消息列表
const messages = ref([]);

// 模型配置状态
const showConfigModal = ref(false);
const savingConfig = ref(false);
const config = ref({
  provider: 'deepseek',
  model: 'deepseek-chat',
  base_url: 'https://api.deepseek.com/v1',
  api_key_masked: '',
  has_key: false,
  temperature: 0.3,
});

const configForm = ref({
  provider: 'deepseek',
  model: 'deepseek-chat',
  base_url: 'https://api.deepseek.com/v1',
  api_key: '',
  temperature: 0.3,
});

// 动态灵感提示词
const promptSuggestions = computed(() => {
  if (currentBook.value === 'agent') {
    return [
      { icon: '🎙️', label: '考考我 ReAct 范式', text: '考考我《ReAct 范式》，用苏格拉底式提问看看我能不能升到理解（🔵）！' },
      { icon: '🔌', label: '大白话讲讲 MCP 协议', text: '用通俗大白话给我讲清 MCP 协议解决了什么痛点，并给我一个最小示例。' },
      { icon: '📝', label: '记一下今日学习', text: '记一下学习：今天深入理解了 Function Calling 的四步生命周期，搞懂了 JSON Schema 校验契约。' },
      { icon: '🗺️', label: '分析我目前的薄弱点', text: '请帮我梳理《Agent 学习》的知识大纲，看看我目前有哪些未学（⚪）和接触过（🟡）的概念需要攻坚？' },
    ];
  }
  return [
    { icon: '🎙️', label: '考考我反向传播', text: '考考我《反向传播》，看看我能不能讲清链式法则推导并升到理解（🔵）！' },
    { icon: '💡', label: '大白话解释 Dropout', text: '用直觉大白话解释一下 Dropout 为什么能抑制过拟合？' },
    { icon: '📝', label: '记一下今日所学', text: '记一下学习：今天手推了均方误差（MSE）在高斯分布先验下的对数似然损失推导。' },
    { icon: '🗺️', label: '查看大纲进度建议', text: '根据当前的深度学习学习路线，告诉我接下来最建议主攻哪个阶段里程碑？' },
  ];
});

const loadConfig = async () => {
  try {
    const res = await fetchAgentConfig();
    config.value = res;
    configForm.value = {
      provider: res.provider || 'deepseek',
      model: res.model || 'deepseek-chat',
      base_url: res.base_url || 'https://api.deepseek.com/v1',
      api_key: '',
      temperature: res.temperature ?? 0.3,
    };
  } catch (e) {
    console.error('加载大模型配置失败:', e);
  }
};

const applyPreset = (prov) => {
  configForm.value.provider = prov;
  if (prov === 'deepseek') {
    configForm.value.base_url = 'https://api.deepseek.com/v1';
    configForm.value.model = 'deepseek-chat';
  } else if (prov === 'openai') {
    configForm.value.base_url = 'https://api.openai.com/v1';
    configForm.value.model = 'gpt-4o-mini';
  } else if (prov === 'kimi') {
    configForm.value.base_url = 'https://api.moonshot.cn/v1';
    configForm.value.model = 'moonshot-v1-8k';
  } else if (prov === 'ollama') {
    configForm.value.base_url = 'http://localhost:11434/v1';
    configForm.value.model = 'qwen2.5:7b';
  }
};

const handleSaveConfig = async () => {
  savingConfig.value = true;
  try {
    const res = await saveAgentConfig(configForm.value);
    if (res.ok) {
      config.value = res.config;
      showConfigModal.value = false;
      emit('toast', '大模型配置已保存！');
    }
  } catch (e) {
    emit('toast', '保存配置失败: ' + e.message);
  } finally {
    savingConfig.value = false;
  }
};

const formatToolTitle = (name) => {
  const map = {
    read_knowledge_note: '查阅本地概念笔记',
    update_node_level: '同步回写掌握度',
    record_study_diary: '追加至今日学习日志',
    query_glossary: '检索速查词典',
    list_knowledge_framework: '扫描全书知识大纲',
    searxng_web_search: '联网搜索 (SearXNG)',
    web_url_read: '阅读网页正文',
    searxng_search_suggestions: '搜索联想词',
    searxng_instance_info: '搜索引擎状态',
  };
  return map[name] || `调用工具: ${name}`;
};

const formatJson = (val) => {
  if (typeof val === 'string') return val;
  try {
    return JSON.stringify(val, null, 2);
  } catch {
    return String(val);
  }
};

const renderContent = (content) => {
  return renderMarkdown(content || '');
};

// 渲染气泡正文：流式输出中把打字光标内联到最后一个块级元素末尾，
// 保证光标跟在文字后面（光标是气泡内容的兄弟节点时会掉到气泡外）
const renderBubble = (msg) => {
  const html = renderContent(msg.content);
  if (!msg.streaming) return html;
  const cursor = '<span class="typing-cursor"></span>';
  const tailBlock = /(<\/(?:p|li|h[1-6]|blockquote|td|th)>\s*)$/;
  if (tailBlock.test(html)) {
    return html.replace(tailBlock, `${cursor}$1`);
  }
  return html + cursor;
};

const scrollToBottom = async () => {
  await nextTick();
  if (chatScrollRef.value) {
    chatScrollRef.value.scrollTop = chatScrollRef.value.scrollHeight;
  }
};

const autoResizeTextarea = () => {
  const el = textareaRef.value;
  if (!el) return;
  el.style.height = 'auto';
  el.style.height = Math.min(el.scrollHeight, 160) + 'px';
};

const handleKeydown = (e) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    handleSubmit();
  }
};

// 时间格式化辅助函数
const formatTimeAgo = (ts) => {
  if (!ts) return '';
  const now = Date.now();
  const diff = Math.max(0, now - ts);
  const minute = 60 * 1000;
  const hour = 60 * minute;
  const day = 24 * hour;

  if (diff < minute) return '刚刚';
  if (diff < hour) return `${Math.floor(diff / minute)} 分钟前`;
  if (diff < day) {
    const d = new Date(ts);
    return `${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`;
  }
  if (diff < 2 * day) return '昨天';
  const d = new Date(ts);
  return `${d.getMonth() + 1}月${d.getDate()}日`;
};

// 从 localStorage 加载某本书的多会话列表（含旧版单会话数据迁移）
const loadSessionsForBook = (book) => {
  const sKey = `aurora_chat_sessions_${book}`;
  const rawSessions = localStorage.getItem(sKey);
  let list = [];
  if (rawSessions) {
    try {
      list = JSON.parse(rawSessions);
    } catch (e) {
      console.error('解析历史会话失败:', e);
    }
  }

  // 兼容迁移：若无多会话列表，但有旧版单会话记录
  if (!list || list.length === 0) {
    const oldHistoryKey = `aurora_chat_history_${book}`;
    const oldThreadKey = `aurora_chat_thread_${book}`;
    const oldRaw = localStorage.getItem(oldHistoryKey);
    const oldTid = localStorage.getItem(oldThreadKey);

    if (oldRaw) {
      try {
        const oldMsgs = JSON.parse(oldRaw);
        if (Array.isArray(oldMsgs) && oldMsgs.length > 0) {
          const firstUser = oldMsgs.find((m) => m.role === 'user');
          let title = '历史对话';
          if (firstUser?.content) {
            const clean = firstUser.content.replace(/[\r\n\t]+/g, ' ').trim();
            title = clean.length > 20 ? clean.slice(0, 20) + '...' : clean;
          }
          list = [
            {
              id: oldTid || `session_${book}_${Date.now()}`,
              title,
              createdAt: Date.now() - 3600000,
              updatedAt: Date.now(),
              messages: oldMsgs.map((m) => ({
                ...m,
                streaming: false,
                tools: (m.tools || []).map((t) => ({ ...t, status: 'done' })),
              })),
            },
          ];
        }
      } catch (e) {
        console.error('迁移旧对话失败:', e);
      }
    }
  }

  // 若仍为空，创建一个默认新会话
  if (!list || list.length === 0) {
    const newSession = {
      id: `session_${book}_${Date.now()}`,
      title: '新对话',
      createdAt: Date.now(),
      updatedAt: Date.now(),
      messages: [],
    };
    list = [newSession];
  }

  // 状态清洗
  list.forEach((s) => {
    s.messages = (s.messages || []).map((m) => ({
      ...m,
      streaming: false,
      tools: (m.tools || []).map((t) => ({ ...t, status: 'done' })),
    }));
  });

  return list;
};

// 持久化当前书籍的多会话数据
const persistSessions = () => {
  const book = currentBook.value;
  const sKey = `aurora_chat_sessions_${book}`;
  const aKey = `aurora_chat_active_session_${book}`;

  // 同步当前激活会话的消息与更新时间
  const cur = sessions.value.find((s) => s.id === currentSessionId.value);
  if (cur) {
    cur.messages = messages.value.map((m) => ({
      role: m.role,
      content: m.content,
      time: m.time,
      tools: m.tools || [],
    }));
    cur.updatedAt = Date.now();
  }

  try {
    localStorage.setItem(sKey, JSON.stringify(sessions.value));
    localStorage.setItem(aKey, currentSessionId.value);
  } catch (e) {
    console.error('保存会话列表失败:', e);
  }
};

// 切换会话
const switchSession = (targetSession) => {
  if (targetSession.id === currentSessionId.value) return;
  if (isStreaming.value) {
    emit('toast', '请等待当前回答生成完毕或点击停止后再切换会话');
    return;
  }
  persistSessions();
  currentSessionId.value = targetSession.id;
  messages.value = targetSession.messages || [];
  localStorage.setItem(`aurora_chat_active_session_${currentBook.value}`, targetSession.id);
  scrollToBottom();
};

// 新建对话
const createNewSession = () => {
  if (isStreaming.value) {
    emit('toast', '当前正在生成中，请稍候');
    return;
  }
  // 若当前会话本身就是空的，无需重复创建
  if (messages.value.length === 0 && currentSession.value) {
    if (textareaRef.value) textareaRef.value.focus();
    return;
  }

  persistSessions();

  const newId = `session_${currentBook.value}_${Date.now()}`;
  const newSession = {
    id: newId,
    title: '新对话',
    createdAt: Date.now(),
    updatedAt: Date.now(),
    messages: [],
  };

  sessions.value.unshift(newSession);
  currentSessionId.value = newId;
  messages.value = [];
  persistSessions();
  scrollToBottom();

  nextTick(() => {
    if (textareaRef.value) textareaRef.value.focus();
  });
  emit('toast', '已开启新话题！');
};

// 删除会话
const confirmDeleteSession = (session) => {
  if (isStreaming.value && session.id === currentSessionId.value) {
    emit('toast', '正在生成中，无法删除当前会话');
    return;
  }

  const idx = sessions.value.findIndex((s) => s.id === session.id);
  if (idx === -1) return;

  sessions.value.splice(idx, 1);

  if (sessions.value.length === 0) {
    const newSession = {
      id: `session_${currentBook.value}_${Date.now()}`,
      title: '新对话',
      createdAt: Date.now(),
      updatedAt: Date.now(),
      messages: [],
    };
    sessions.value = [newSession];
    currentSessionId.value = newSession.id;
    messages.value = [];
  } else if (session.id === currentSessionId.value) {
    const nextSession = sessions.value[0];
    currentSessionId.value = nextSession.id;
    messages.value = nextSession.messages || [];
  }

  persistSessions();
  emit('toast', '会话已删除');
};

// 重命名会话
const startRename = (session) => {
  editingSessionId.value = session.id;
  editTitleInput.value = session.title;
  nextTick(() => {
    if (renameInputRef.value) {
      const el = Array.isArray(renameInputRef.value)
        ? renameInputRef.value[0]
        : renameInputRef.value;
      el?.focus();
      el?.select();
    }
  });
};

const confirmRename = (session) => {
  if (editingSessionId.value !== session.id) return;
  const newTitle = editTitleInput.value.trim();
  if (newTitle) {
    session.title = newTitle;
    persistSessions();
  }
  editingSessionId.value = null;
};

const cancelRename = () => {
  editingSessionId.value = null;
};

// 清空当前书籍的所有会话
const handleClearAllSessions = () => {
  if (isStreaming.value) {
    emit('toast', '当前正在生成中，请稍候');
    return;
  }
  if (!confirm(`确定要清空《${bookName.value}》的所有历史会话吗？`)) {
    return;
  }
  const newSession = {
    id: `session_${currentBook.value}_${Date.now()}`,
    title: '新对话',
    createdAt: Date.now(),
    updatedAt: Date.now(),
    messages: [],
  };
  sessions.value = [newSession];
  currentSessionId.value = newSession.id;
  messages.value = [];
  persistSessions();
  emit('toast', '已清空所有历史会话！');
};

const sendPrompt = (text) => {
  inputQuery.value = text;
  handleSubmit();
};

const stopGeneration = () => {
  if (abortController) {
    abortController.abort();
    abortController = null;
  }
  isStreaming.value = false;
  persistSessions();
};

const handleSubmit = async () => {
  const q = inputQuery.value.trim();
  if (!q || isStreaming.value) return;

  const now = new Date();
  const timeStr = `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}`;

  // 如果当前是初始会话且未命名，自动从第一条问题提取标题
  if (currentSession.value) {
    if (
      currentSession.value.title === '新对话' ||
      currentSession.value.title === '新话题' ||
      !currentSession.value.title
    ) {
      const cleanTitle = q.replace(/[\r\n\t]+/g, ' ').trim();
      currentSession.value.title =
        cleanTitle.length > 20 ? cleanTitle.slice(0, 20) + '...' : cleanTitle;
    }
  }

  // 追加用户消息
  messages.value.push({
    role: 'user',
    content: q,
    time: timeStr,
  });

  inputQuery.value = '';
  if (textareaRef.value) textareaRef.value.style.height = 'auto';
  persistSessions();
  await scrollToBottom();

  // 创建助手消息占位
  const botMsg = {
    role: 'assistant',
    content: '',
    time: timeStr,
    streaming: true,
    tools: [],
  };
  messages.value.push(botMsg);
  isStreaming.value = true;
  await scrollToBottom();

  abortController = new AbortController();

  try {
    const threadId = currentSessionId.value;
    const res = await fetch('/api/agent/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message: q,
        book: currentBook.value,
        thread_id: threadId,
      }),
      signal: abortController.signal,
    });

    if (!res.ok) {
      throw new Error(`服务响应错误 (${res.status})`);
    }

    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n\n');
      buffer = lines.pop(); // 保留未闭合块

      for (const rawLine of lines) {
        const line = rawLine.trim();
        if (!line.startsWith('data:')) continue;
        const dataStr = line.replace(/^data:\s*/, '');

        if (dataStr === '[DONE]') {
          botMsg.streaming = false;
          isStreaming.value = false;
          break;
        }

        try {
          const payload = JSON.parse(dataStr);
          if (payload.type === 'content') {
            botMsg.content += payload.delta;
            scrollToBottom();
          } else if (payload.type === 'tool_start') {
            botMsg.tools.push({
              name: payload.name,
              input: payload.input,
              output: '',
              status: 'running',
            });
            scrollToBottom();
          } else if (payload.type === 'tool_end') {
            const runningTool = [...botMsg.tools].reverse().find((t) => t.name === payload.name && t.status === 'running');
            if (runningTool) {
              runningTool.status = 'done';
              runningTool.output = payload.output;
            } else {
              botMsg.tools.push({
                name: payload.name,
                output: payload.output,
                status: 'done',
              });
            }
            scrollToBottom();
          } else if (payload.type === 'error') {
            botMsg.content += `\n\n> ⚠️ **错误提醒**：${payload.message}\n`;
            scrollToBottom();
          }
        } catch {
          // 忽略非 JSON 帧
        }
      }
    }
  } catch (err) {
    if (err.name !== 'AbortError') {
      botMsg.content += `\n\n> ⚠️ **网络连接中断**：${err.message}`;
    }
  } finally {
    botMsg.streaming = false;
    isStreaming.value = false;
    abortController = null;
    persistSessions();
    scrollToBottom();
  }
};

// 初始化某本书的会话列表
const initBookSessions = (book) => {
  sessions.value = loadSessionsForBook(book);
  const activeId = localStorage.getItem(`aurora_chat_active_session_${book}`);
  const targetSession = sessions.value.find((s) => s.id === activeId) || sessions.value[0];
  if (targetSession) {
    currentSessionId.value = targetSession.id;
    messages.value = targetSession.messages || [];
  }
  scrollToBottom();
};

onMounted(() => {
  loadConfig();
  initBookSessions(currentBook.value);
});

watch(currentBook, (newBook, oldBook) => {
  if (oldBook) {
    persistSessions();
  }
  initBookSessions(newBook);
});
</script>

<style scoped>
@import url('https://fonts.loli.net/css2?family=ZCOOL+KuaiLe&display=swap');

/* ================= 星露谷像素风 · 设计变量 ================= */
.agent-workspace {
  /* 木质色系 */
  --wood-dark: #3e2412;
  --wood-deep: #5c3a1e;
  --wood: #7a4a2b;
  --wood-mid: #a0653b;
  --wood-light: #c08b5c;
  /* 羊皮纸色系 */
  --paper: #f5e6c8;
  --paper-deep: #edd9ae;
  --paper-edge: #c9a96e;
  /* 文字 */
  --ink: #4a2e17;
  --ink-soft: #8a6d4f;
  /* 草绿按钮系 */
  --grass: #4caf50;
  --grass-dark: #3d8b37;
  --grass-deep: #2d6b28;
  --grass-light: #a8d95b;
  /* 点缀 */
  --plum: #9c6dd0;
  --plum-deep: #6b4a94;
  --berry: #c94f4f;
  --berry-deep: #8a3232;

  display: flex;
  flex-direction: row;
  height: 100%;
  color: var(--ink);
  overflow: hidden;
  position: relative;
  font-family: 'ZCOOL KuaiLe', 'Microsoft YaHei', 'PingFang SC', sans-serif;
  letter-spacing: 0.03em;
  /* 农场木板底：木板缝 + 横向木纹 + 纵向渐变 */
  background-color: #6b3f23;
  background-image:
    repeating-linear-gradient(90deg, rgba(62, 36, 18, 0.4) 0 3px, transparent 3px 118px),
    repeating-linear-gradient(0deg, rgba(255, 235, 200, 0.05) 0 2px, transparent 2px 7px),
    linear-gradient(180deg, #7d4e2d 0%, #6b3f23 100%);
}

/* ================= 历史会话左侧边栏（深木板） ================= */
.chat-sidebar {
  width: 260px;
  min-width: 260px;
  max-width: 260px;
  background-color: #5c3a1e;
  background-image:
    repeating-linear-gradient(90deg, rgba(0, 0, 0, 0.16) 0 2px, transparent 2px 44px),
    repeating-linear-gradient(0deg, rgba(255, 235, 200, 0.04) 0 2px, transparent 2px 8px);
  border-right: 4px solid var(--wood-dark);
  box-shadow: inset -3px 0 0 rgba(255, 235, 200, 0.08);
  display: flex;
  flex-direction: column;
  transition: width 0.22s ease, min-width 0.22s ease, max-width 0.22s ease, opacity 0.2s ease;
  height: 100%;
  overflow: hidden;
  position: relative;
  z-index: 10;
  color: #f0e0c0;
}

.chat-sidebar.collapsed {
  width: 0;
  min-width: 0;
  max-width: 0;
  border-right: none;
  opacity: 0;
  pointer-events: none;
}

/* 侧边栏头部 */
.sidebar-top {
  padding: 14px 14px 10px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  border-bottom: 3px solid var(--wood-dark);
  box-shadow: 0 2px 0 rgba(255, 235, 200, 0.06);
}

.sidebar-header-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.sidebar-brand {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 600;
  color: #ffe9bd;
  text-shadow: 1px 1px 0 var(--wood-dark);
}

.sidebar-brand-icon {
  color: var(--grass-light);
}

.sidebar-collapse-btn,
.sidebar-expand-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border-radius: 5px;
  background: rgba(62, 36, 18, 0.35);
  border: 2px solid rgba(255, 235, 200, 0.12);
  color: #d9c49a;
  cursor: pointer;
  transition: all 0.15s;
}

.sidebar-collapse-btn:hover,
.sidebar-expand-btn:hover {
  background: rgba(245, 230, 200, 0.15);
  color: #ffe9bd;
}

/* 绿色像素按钮（新建对话） */
.sidebar-new-chat-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  width: 100%;
  padding: 9px 12px;
  border-radius: 6px;
  background: var(--grass);
  border: 2px solid var(--grass-deep);
  box-shadow:
    inset 0 2px 0 var(--grass-light),
    inset 0 -3px 0 var(--grass-dark),
    0 3px 0 var(--wood-dark);
  color: #fffbe8;
  text-shadow: 1px 1px 0 var(--grass-deep);
  font-size: 13.5px;
  font-weight: 600;
  font-family: inherit;
  letter-spacing: 0.05em;
  cursor: pointer;
  transition: filter 0.15s;
}

.sidebar-new-chat-btn:hover {
  filter: brightness(1.08);
}

.sidebar-new-chat-btn:active {
  transform: translateY(2px);
  box-shadow:
    inset 0 2px 0 var(--grass-light),
    inset 0 -2px 0 var(--grass-dark),
    0 1px 0 var(--wood-dark);
}

/* 会话列表 */
.session-list-scroll {
  flex: 1;
  overflow-y: auto;
  padding: 10px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.session-list-scroll::-webkit-scrollbar {
  width: 6px;
}
.session-list-scroll::-webkit-scrollbar-track {
  background: rgba(62, 36, 18, 0.3);
}
.session-list-scroll::-webkit-scrollbar-thumb {
  background: var(--wood-mid);
  border: 1px solid var(--wood-dark);
  border-radius: 3px;
}

/* 会话卡片 = 小木牌 */
.session-item {
  display: flex;
  align-items: center;
  gap: 9px;
  padding: 9px 10px;
  border-radius: 6px;
  cursor: pointer;
  border: 2px solid rgba(255, 235, 200, 0.08);
  background: rgba(62, 36, 18, 0.25);
  transition: all 0.15s;
  color: #d9c49a;
  position: relative;
}

.session-item:hover {
  background: rgba(245, 230, 200, 0.1);
  border-color: rgba(255, 235, 200, 0.2);
  color: #ffe9bd;
}

.session-item.active {
  background: var(--grass-dark);
  border-color: var(--grass-light);
  color: #fffbe8;
  box-shadow:
    inset 0 2px 0 rgba(168, 217, 91, 0.45),
    0 2px 0 var(--wood-dark);
}

.session-item-icon {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #b89a70;
}

.session-item.active .session-item-icon {
  color: var(--grass-light);
}

.session-item-content {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.session-item-title {
  font-size: 13px;
  font-weight: 500;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  line-height: 1.3;
}

.session-item.active .session-item-title {
  font-weight: 600;
  color: #fffbe8;
}

.session-item-meta {
  font-size: 11px;
  color: #a98a5f;
  display: flex;
  align-items: center;
  gap: 4px;
}

.session-item.active .session-item-meta {
  color: #d3e8b0;
}

.meta-dot {
  opacity: 0.5;
}

/* 操作按钮 */
.session-item-actions {
  display: none;
  align-items: center;
  gap: 3px;
  flex-shrink: 0;
}

.session-item:hover .session-item-actions,
.session-item.active .session-item-actions {
  display: flex;
}

.item-act-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 22px;
  height: 22px;
  border-radius: 4px;
  background: rgba(62, 36, 18, 0.4);
  border: 1px solid rgba(255, 235, 200, 0.15);
  color: #d9c49a;
  cursor: pointer;
  transition: all 0.15s;
}

.item-act-btn:hover {
  background: rgba(245, 230, 200, 0.2);
  color: #fffbe8;
}

.item-act-btn.delete:hover {
  background: var(--berry);
  border-color: var(--berry-deep);
  color: #fff;
}

/* 重命名输入框 */
.session-rename-wrap {
  width: 100%;
}

.rename-input {
  width: 100%;
  background: #fff6de;
  border: 2px solid var(--grass-dark);
  border-radius: 4px;
  color: var(--ink);
  font-size: 12px;
  font-family: inherit;
  padding: 3px 6px;
  outline: none;
}

.session-empty {
  text-align: center;
  padding: 30px 10px;
  color: #a98a5f;
  font-size: 12px;
}

/* 侧栏底部 */
.sidebar-bottom {
  padding: 10px 14px;
  border-top: 3px solid var(--wood-dark);
  box-shadow: inset 0 2px 0 rgba(255, 235, 200, 0.06);
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 12px;
}

.book-tag {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #e8d3ae;
}

.book-tag-dot {
  width: 8px;
  height: 8px;
  border-radius: 2px;
  background: var(--grass-light);
  border: 1px solid var(--grass-deep);
  box-shadow: 1px 1px 0 var(--wood-dark);
}

.sidebar-clear-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  background: transparent;
  border: none;
  color: #a98a5f;
  cursor: pointer;
  font-size: 11.5px;
  font-family: inherit;
  padding: 3px 6px;
  border-radius: 4px;
  transition: all 0.15s;
}

.sidebar-clear-btn:hover {
  color: #ffb0b0;
  background: rgba(201, 79, 79, 0.2);
}

/* ================= 主对话视口主体 ================= */
.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  height: 100%;
  min-width: 0;
  position: relative;
}

/* 顶栏（木栅栏牌匾） */
.assistant-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 22px;
  background-color: #7a4a2b;
  background-image:
    repeating-linear-gradient(90deg, rgba(62, 36, 18, 0.3) 0 3px, transparent 3px 108px),
    linear-gradient(180deg, #855431 0%, #74462a 100%);
  border-bottom: 4px solid var(--wood-dark);
  box-shadow:
    inset 0 2px 0 rgba(255, 235, 200, 0.12),
    0 3px 0 rgba(0, 0, 0, 0.18);
}

.bar-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.agent-avatar {
  width: 38px;
  height: 38px;
  border-radius: 7px;
  background: var(--grass);
  border: 2px solid var(--grass-deep);
  box-shadow:
    inset 0 2px 0 var(--grass-light),
    inset 0 -3px 0 var(--grass-dark),
    0 3px 0 var(--wood-dark);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fffbe8;
}

.agent-meta {
  display: flex;
  flex-direction: column;
}

.agent-title-wrap {
  display: flex;
  align-items: center;
  gap: 10px;
}

.agent-title {
  font-weight: 700;
  font-size: 16px;
  letter-spacing: 0.06em;
  color: #ffe9bd;
  text-shadow: 1px 1px 0 var(--wood-dark);
}

.status-indicator {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-size: 11px;
  color: #fffbe8;
  background: var(--grass-dark);
  padding: 3px 10px;
  border-radius: 999px;
  border: 2px solid var(--grass-light);
  box-shadow: 0 2px 0 var(--wood-dark);
  text-shadow: 1px 1px 0 var(--grass-deep);
}

.pulse-dot {
  width: 7px;
  height: 7px;
  background: var(--grass-light);
  border-radius: 2px;
  box-shadow: 0 0 6px var(--grass-light);
  animation: blink 1.6s infinite;
}

.agent-sub {
  font-size: 12px;
  color: #e8d3ae;
  margin-top: 3px;
}

.bar-right {
  display: flex;
  align-items: center;
  gap: 10px;
}

/* 米色木牌按钮（新话题） */
.subtle-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 7px 14px;
  font-size: 12.5px;
  font-weight: 600;
  font-family: inherit;
  letter-spacing: 0.04em;
  border-radius: 6px;
  cursor: pointer;
  transition: filter 0.15s;
  background: var(--paper-deep);
  border: 2px solid var(--wood-dark);
  box-shadow:
    inset 0 2px 0 rgba(255, 255, 255, 0.5),
    0 3px 0 var(--wood-dark);
  color: var(--ink);
}

.subtle-btn:hover {
  filter: brightness(1.06);
}

.subtle-btn:active {
  transform: translateY(2px);
  box-shadow: inset 0 2px 0 rgba(255, 255, 255, 0.5), 0 1px 0 var(--wood-dark);
}

/* 绿色按钮（模型配置） */
.config-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 7px 14px;
  font-size: 12.5px;
  font-weight: 600;
  font-family: inherit;
  letter-spacing: 0.04em;
  border-radius: 6px;
  cursor: pointer;
  transition: filter 0.15s;
  background: var(--grass);
  border: 2px solid var(--grass-deep);
  box-shadow:
    inset 0 2px 0 var(--grass-light),
    inset 0 -3px 0 var(--grass-dark),
    0 3px 0 var(--wood-dark);
  color: #fffbe8;
  text-shadow: 1px 1px 0 var(--grass-deep);
}

.config-btn:hover {
  filter: brightness(1.08);
}

.config-btn:active {
  transform: translateY(2px);
  box-shadow:
    inset 0 2px 0 var(--grass-light),
    inset 0 -2px 0 var(--grass-dark),
    0 1px 0 var(--wood-dark);
}

.config-btn.has-key {
  background: var(--grass-dark);
}

/* 视口 */
.chat-viewport {
  flex: 1;
  overflow-y: auto;
  padding: 26px 20px;
  scroll-behavior: smooth;
}

.chat-viewport::-webkit-scrollbar {
  width: 10px;
}
.chat-viewport::-webkit-scrollbar-track {
  background: rgba(62, 36, 18, 0.4);
}
.chat-viewport::-webkit-scrollbar-thumb {
  background: var(--wood-mid);
  border: 2px solid var(--wood-dark);
  border-radius: 5px;
}
.chat-viewport::-webkit-scrollbar-thumb:hover {
  background: var(--wood-light);
}

/* ================= 欢迎卡片（羊皮纸告示） ================= */
.welcome-container {
  max-width: 820px;
  margin: 20px auto 40px;
}

.hero-box {
  background-color: var(--paper);
  background-image:
    radial-gradient(circle 3px at 14px 14px, #b78d55 2.5px, transparent 3.5px),
    radial-gradient(circle 3px at calc(100% - 14px) 14px, #b78d55 2.5px, transparent 3.5px),
    radial-gradient(circle 3px at 14px calc(100% - 14px), #b78d55 2.5px, transparent 3.5px),
    radial-gradient(circle 3px at calc(100% - 14px) calc(100% - 14px), #b78d55 2.5px, transparent 3.5px),
    linear-gradient(180deg, #f7ebd0 0%, #f0dcb0 100%);
  border: 3px solid var(--wood-dark);
  box-shadow:
    inset 0 0 0 3px var(--paper-edge),
    0 6px 0 rgba(62, 36, 18, 0.55);
  border-radius: 10px;
  padding: 40px 36px;
  text-align: center;
}

.hero-badge {
  display: inline-flex;
  padding: 15px;
  background: var(--grass);
  border: 2px solid var(--grass-deep);
  box-shadow:
    inset 0 2px 0 var(--grass-light),
    inset 0 -3px 0 var(--grass-dark),
    0 4px 0 var(--wood-dark);
  border-radius: 10px;
  color: #fffbe8;
  margin-bottom: 18px;
}

.hero-title {
  font-size: 26px;
  letter-spacing: 0.08em;
  margin-bottom: 10px;
  color: #5c3a1e;
  text-shadow: 1px 1px 0 rgba(201, 169, 110, 0.6);
}

.hero-desc {
  font-size: 14px;
  color: #6b4a2b;
  max-width: 600px;
  margin: 0 auto 28px;
  line-height: 1.7;
}

.hero-desc strong {
  color: var(--grass-deep);
}

.capabilities-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 14px;
  margin-bottom: 32px;
}

.cap-card {
  background: var(--paper-deep);
  border: 2px solid var(--wood-mid);
  box-shadow:
    inset 0 2px 0 rgba(255, 255, 255, 0.4),
    0 3px 0 rgba(62, 36, 18, 0.4);
  border-radius: 7px;
  padding: 16px 14px;
  text-align: left;
  transition: transform 0.15s, border-color 0.15s;
}

.cap-card:hover {
  transform: translateY(-2px);
  border-color: var(--grass-dark);
}

.cap-icon {
  font-size: 22px;
  margin-bottom: 8px;
}

.cap-name {
  font-weight: 600;
  font-size: 13.5px;
  margin-bottom: 4px;
  color: var(--ink);
}

.cap-desc {
  font-size: 11.5px;
  color: #6b4a2b;
  line-height: 1.5;
}

.suggestion-section {
  border-top: 2px dashed var(--paper-edge);
  padding-top: 24px;
  text-align: left;
}

.sug-title {
  font-size: 12.5px;
  color: #6b4a2b;
  margin-bottom: 12px;
}

.sug-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

/* 胶囊 chips = 小羊皮纸标签 */
.sug-chip {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: #fff2d6;
  border: 2px solid var(--wood-mid);
  border-radius: 999px;
  padding: 8px 16px;
  color: var(--ink);
  font-size: 12.5px;
  font-family: inherit;
  cursor: pointer;
  box-shadow: 0 2px 0 rgba(62, 36, 18, 0.4);
  transition: all 0.15s;
}

.sug-chip:hover {
  background: #e2f0c4;
  border-color: var(--grass-dark);
  transform: translateY(-1px);
}

.sug-chip:active {
  transform: translateY(1px);
  box-shadow: none;
}

/* ================= 消息流 ================= */
.messages-stream {
  max-width: 900px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.message-row {
  display: flex;
  gap: 14px;
}

.message-row.user {
  flex-direction: row-reverse;
}

.avatar-cell {
  flex-shrink: 0;
}

/* 像素风方块头像 */
.user-avatar {
  width: 34px;
  height: 34px;
  border-radius: 6px;
  background: var(--plum);
  border: 2px solid var(--plum-deep);
  box-shadow:
    inset 0 2px 0 rgba(255, 255, 255, 0.35),
    0 3px 0 var(--wood-dark);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 700;
  color: #fffbe8;
  text-shadow: 1px 1px 0 var(--plum-deep);
}

.bot-avatar {
  width: 34px;
  height: 34px;
  border-radius: 6px;
  background: var(--grass);
  border: 2px solid var(--grass-deep);
  box-shadow:
    inset 0 2px 0 var(--grass-light),
    inset 0 -3px 0 var(--grass-dark),
    0 3px 0 var(--wood-dark);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fffbe8;
}

.bubble-cell {
  max-width: calc(100% - 60px);
  display: flex;
  flex-direction: column;
}

.message-row.user .bubble-cell {
  align-items: flex-end;
}

.bubble-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 11.5px;
  color: #e8d3ae;
  text-shadow: 1px 1px 0 rgba(62, 36, 18, 0.6);
  margin-bottom: 5px;
  padding: 0 4px;
}

/* 用户气泡 = 草地绿木牌 */
.message-row.user .markdown-body {
  background: linear-gradient(180deg, #57b356 0%, #43a047 100%);
  border: 3px solid var(--grass-deep);
  box-shadow:
    inset 0 2px 0 var(--grass-light),
    inset 0 -3px 0 var(--grass-dark),
    0 4px 0 rgba(62, 36, 18, 0.6);
  color: #fffbe8;
  text-shadow: 1px 1px 0 rgba(45, 107, 40, 0.45);
  border-radius: 10px 3px 10px 10px;
  padding: 12px 18px;
  font-size: 14.5px;
  line-height: 1.65;
}

/* 导师回复 = 四角钉装的羊皮纸信 */
.message-row.assistant .markdown-body {
  background-color: var(--paper);
  background-image:
    radial-gradient(circle 3px at 12px 12px, #b78d55 2.5px, transparent 3.5px),
    radial-gradient(circle 3px at calc(100% - 12px) 12px, #b78d55 2.5px, transparent 3.5px),
    radial-gradient(circle 3px at 12px calc(100% - 12px), #b78d55 2.5px, transparent 3.5px),
    radial-gradient(circle 3px at calc(100% - 12px) calc(100% - 12px), #b78d55 2.5px, transparent 3.5px),
    linear-gradient(180deg, #f7ebd0 0%, #f1dfb4 100%);
  border: 3px solid var(--wood-dark);
  box-shadow:
    inset 0 0 0 2px var(--paper-edge),
    0 4px 0 rgba(62, 36, 18, 0.6);
  border-radius: 3px 10px 10px 10px;
  padding: 16px 22px;
  font-size: 14.5px;
  line-height: 1.75;
  color: var(--ink);
}

/* ---- 羊皮纸上的 Markdown 排版 ---- */
.message-row.assistant .markdown-body :deep(h1),
.message-row.assistant .markdown-body :deep(h2),
.message-row.assistant .markdown-body :deep(h3),
.message-row.assistant .markdown-body :deep(h4) {
  color: #5c3a1e;
  text-shadow: 1px 1px 0 rgba(201, 169, 110, 0.5);
}

.message-row.assistant .markdown-body :deep(hr) {
  border: none;
  border-top: 2px dashed var(--paper-edge);
  margin: 14px 0;
}

.message-row.assistant .markdown-body :deep(code) {
  background: #e8d5a8;
  color: #7a4a2b;
  border: 1px solid var(--paper-edge);
  border-radius: 4px;
  padding: 1px 6px;
  font-size: 0.92em;
}

.message-row.assistant .markdown-body :deep(pre) {
  background: #5c3a1e;
  border: 2px solid var(--wood-dark);
  border-radius: 6px;
  padding: 12px 14px;
  overflow-x: auto;
}

.message-row.assistant .markdown-body :deep(pre code) {
  background: transparent;
  border: none;
  color: #f5e6c8;
  padding: 0;
}

.message-row.assistant .markdown-body :deep(a) {
  color: var(--grass-deep);
  text-decoration: underline;
  text-underline-offset: 3px;
}

.message-row.assistant .markdown-body :deep(blockquote) {
  border-left: 4px solid var(--paper-edge);
  background: rgba(201, 169, 110, 0.18);
  color: #6b4a2b;
  padding: 8px 14px;
  margin: 10px 0;
  border-radius: 0 6px 6px 0;
}

.message-row.assistant .markdown-body :deep(table) {
  border-collapse: collapse;
  margin: 10px 0;
  width: 100%;
}

.message-row.assistant .markdown-body :deep(th),
.message-row.assistant .markdown-body :deep(td) {
  border: 1.5px solid var(--paper-edge);
  padding: 6px 12px;
  font-size: 13.5px;
}

.message-row.assistant .markdown-body :deep(th) {
  background: rgba(201, 169, 110, 0.3);
  color: #5c3a1e;
}

.message-row.assistant .markdown-body :deep(strong) {
  color: #5c3a1e;
}

/* 用户气泡内的 Markdown 元素 */
.message-row.user .markdown-body :deep(code) {
  background: rgba(45, 107, 40, 0.55);
  color: #fffbe8;
  border: 1px solid rgba(168, 217, 91, 0.5);
  border-radius: 4px;
  padding: 1px 6px;
}

.message-row.user .markdown-body :deep(a) {
  color: #fffbe8;
  text-decoration: underline;
}

/* ================= 工具调用折叠卡片（小羊皮纸标签） ================= */
.tool-calls-stack {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 12px;
}

.tool-card {
  background: var(--paper-deep);
  border: 2px solid var(--wood-dark);
  box-shadow: 0 2px 0 rgba(62, 36, 18, 0.5);
  border-radius: 6px;
  overflow: hidden;
  font-size: 12px;
  color: var(--ink);
}

.tool-summary {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px;
  cursor: pointer;
  user-select: none;
  background: rgba(160, 101, 59, 0.2);
}

.tool-summary:hover {
  background: rgba(160, 101, 59, 0.3);
}

.tool-sum-left {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: var(--grass-deep);
}

/* 方形像素状态章 */
.tool-status-badge {
  width: 17px;
  height: 17px;
  border-radius: 3px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 10px;
  border: 1.5px solid transparent;
}

.tool-status-badge.done {
  background: var(--grass);
  border-color: var(--grass-deep);
  color: #fffbe8;
}

.tool-status-badge.running {
  background: #e8a33d;
  border-color: #a86f1d;
  color: #fff;
}

.tool-state-tag {
  font-size: 11px;
  color: var(--ink-soft);
}

.tool-body {
  padding: 10px 14px;
  background: #f1e0b8;
  border-top: 2px dashed var(--paper-edge);
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.tool-label {
  color: var(--ink-soft);
  font-weight: 600;
}

.tool-section pre {
  margin-top: 4px;
  background: #5c3a1e;
  border: 2px solid var(--wood-dark);
  color: #f5e6c8;
  padding: 8px 10px;
  border-radius: 6px;
  overflow-x: auto;
  font-family: 'JetBrains Mono', Consolas, monospace;
  font-size: 11px;
  letter-spacing: 0;
}

/* 打字机光标（像素方块，内联注入到正文末尾，需 deep 穿透 v-html） */
.markdown-body :deep(.typing-cursor) {
  display: inline-block;
  width: 9px;
  height: 16px;
  background: var(--grass-dark);
  box-shadow: 1px 1px 0 var(--grass-deep);
  margin-left: 5px;
  vertical-align: middle;
  animation: blink 0.9s infinite;
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0; }
}

/* 思考中加载点（显示在羊皮纸气泡内部） */
.thinking-bubble {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  min-width: 76px;
  min-height: 24px;
}

.thinking-dot {
  width: 8px;
  height: 8px;
  background: var(--grass-dark);
  box-shadow: 1px 1px 0 var(--grass-deep);
  animation: thinking-bounce 1.2s infinite;
}

.thinking-dot:nth-child(2) {
  animation-delay: 0.15s;
}

.thinking-dot:nth-child(3) {
  animation-delay: 0.3s;
}

@keyframes thinking-bounce {
  0%, 60%, 100% { transform: translateY(0); opacity: 0.45; }
  30% { transform: translateY(-5px); opacity: 1; }
}

/* ================= 底部输入操作栏 ================= */
.assistant-input-area {
  padding: 12px 22px 16px;
  background-color: #7a4a2b;
  background-image:
    repeating-linear-gradient(90deg, rgba(62, 36, 18, 0.3) 0 3px, transparent 3px 108px);
  border-top: 4px solid var(--wood-dark);
  box-shadow: inset 0 2px 0 rgba(255, 235, 200, 0.1);
  position: relative;
}

.floating-quick-chips {
  display: flex;
  gap: 8px;
  overflow-x: auto;
  padding-bottom: 10px;
  margin-bottom: 4px;
}

.floating-quick-chips::-webkit-scrollbar {
  height: 4px;
}
.floating-quick-chips::-webkit-scrollbar-thumb {
  background: var(--wood-mid);
  border-radius: 2px;
}

.mini-chip {
  flex-shrink: 0;
  background: #fff2d6;
  border: 2px solid var(--wood-mid);
  border-radius: 999px;
  padding: 5px 13px;
  font-size: 11.5px;
  font-family: inherit;
  color: var(--ink);
  cursor: pointer;
  box-shadow: 0 2px 0 rgba(62, 36, 18, 0.4);
  transition: all 0.15s;
}

.mini-chip:hover {
  background: #e2f0c4;
  border-color: var(--grass-dark);
  transform: translateY(-1px);
}

.mini-chip:active {
  transform: translateY(1px);
  box-shadow: none;
}

/* 输入框 = 嵌进木板的羊皮纸槽 */
.input-form {
  display: flex;
  align-items: flex-end;
  gap: 10px;
  background: var(--paper);
  border: 3px solid var(--wood-dark);
  box-shadow:
    inset 0 2px 4px rgba(62, 36, 18, 0.18),
    0 3px 0 rgba(0, 0, 0, 0.25);
  border-radius: 8px;
  padding: 8px 12px;
  transition: border-color 0.15s, box-shadow 0.15s;
}

.input-form:focus-within {
  border-color: var(--grass-deep);
  box-shadow:
    inset 0 2px 4px rgba(62, 36, 18, 0.18),
    0 0 0 3px var(--grass-light),
    0 3px 0 rgba(0, 0, 0, 0.25);
}

.chat-textarea {
  flex: 1;
  background: transparent;
  border: none;
  color: var(--ink);
  font-family: inherit;
  font-size: 14px;
  letter-spacing: 0.03em;
  line-height: 1.5;
  resize: none;
  max-height: 160px;
  outline: none;
  padding: 4px 0;
}

.chat-textarea::placeholder {
  color: #b08d5f;
}

.chat-textarea:disabled {
  color: var(--ink-soft);
}

.form-actions {
  display: flex;
  align-items: center;
}

/* 发送 = 绿色像素按钮 */
.send-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: var(--grass);
  color: #fffbe8;
  text-shadow: 1px 1px 0 var(--grass-deep);
  border: 2px solid var(--grass-deep);
  box-shadow:
    inset 0 2px 0 var(--grass-light),
    inset 0 -3px 0 var(--grass-dark),
    0 3px 0 var(--wood-dark);
  border-radius: 6px;
  padding: 8px 18px;
  font-size: 13px;
  font-weight: 600;
  font-family: inherit;
  letter-spacing: 0.05em;
  cursor: pointer;
  transition: filter 0.15s;
}

.send-btn:hover:not(:disabled) {
  filter: brightness(1.08);
}

.send-btn:active:not(:disabled) {
  transform: translateY(2px);
  box-shadow:
    inset 0 2px 0 var(--grass-light),
    inset 0 -2px 0 var(--grass-dark),
    0 1px 0 var(--wood-dark);
}

.send-btn:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

/* 停止 = 浆果红像素按钮 */
.stop-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: var(--berry);
  color: #fffbe8;
  text-shadow: 1px 1px 0 var(--berry-deep);
  border: 2px solid var(--berry-deep);
  box-shadow:
    inset 0 2px 0 #e88a7a,
    inset 0 -3px 0 #a83c3c,
    0 3px 0 var(--wood-dark);
  border-radius: 6px;
  padding: 8px 16px;
  font-size: 13px;
  font-weight: 600;
  font-family: inherit;
  cursor: pointer;
  transition: filter 0.15s;
}

.stop-btn:hover {
  filter: brightness(1.08);
}

.stop-btn:active {
  transform: translateY(2px);
  box-shadow: inset 0 2px 0 #e88a7a, inset 0 -2px 0 #a83c3c, 0 1px 0 var(--wood-dark);
}

/* ================= 设置 Modal（羊皮纸木板框） ================= */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(62, 36, 18, 0.6);
  backdrop-filter: blur(3px);
  z-index: 100;
  display: flex;
  align-items: center;
  justify-content: center;
}

.config-modal {
  width: min(560px, 92vw);
  background-color: var(--paper);
  background-image: linear-gradient(180deg, #f7ebd0 0%, #f0dcb0 100%);
  border: 3px solid var(--wood-dark);
  box-shadow:
    inset 0 0 0 3px var(--paper-edge),
    0 10px 0 rgba(0, 0, 0, 0.3);
  border-radius: 10px;
  padding: 24px;
  color: var(--ink);
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 2px dashed var(--paper-edge);
  padding-bottom: 14px;
  margin-bottom: 18px;
}

.m-title-wrap {
  display: flex;
  align-items: center;
  gap: 10px;
}

.m-icon {
  color: var(--grass-deep);
}

.modal-header h3 {
  font-size: 17px;
  font-weight: 700;
  color: #5c3a1e;
  letter-spacing: 0.05em;
}

.m-close {
  background: var(--paper-deep);
  border: 2px solid var(--wood-mid);
  border-radius: 5px;
  width: 28px;
  height: 28px;
  color: var(--ink-soft);
  font-size: 14px;
  cursor: pointer;
  box-shadow: 0 2px 0 rgba(62, 36, 18, 0.4);
  transition: all 0.15s;
}

.m-close:hover {
  background: var(--berry);
  border-color: var(--berry-deep);
  color: #fff;
}

.modal-body {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-group label {
  font-size: 12.5px;
  font-weight: 600;
  color: #6b4a2b;
}

.provider-presets {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.preset-btn {
  background: var(--paper-deep);
  border: 2px solid var(--wood-mid);
  border-radius: 6px;
  padding: 7px 14px;
  font-size: 12.5px;
  font-family: inherit;
  color: var(--ink);
  cursor: pointer;
  box-shadow: 0 2px 0 rgba(62, 36, 18, 0.35);
  transition: all 0.15s;
}

.preset-btn:hover {
  filter: brightness(1.04);
}

.preset-btn.active {
  background: var(--grass);
  border-color: var(--grass-deep);
  box-shadow:
    inset 0 2px 0 var(--grass-light),
    inset 0 -2px 0 var(--grass-dark),
    0 2px 0 var(--wood-dark);
  color: #fffbe8;
  text-shadow: 1px 1px 0 var(--grass-deep);
  font-weight: 600;
}

.cfg-input {
  background: #fff6de;
  border: 2px solid var(--wood-mid);
  border-radius: 6px;
  padding: 9px 12px;
  color: var(--ink);
  font-size: 13.5px;
  font-family: inherit;
  outline: none;
  box-shadow: inset 0 2px 3px rgba(62, 36, 18, 0.1);
  transition: border-color 0.15s;
}

.cfg-input:focus {
  border-color: var(--grass-dark);
}

.cfg-hint {
  font-size: 11px;
  color: var(--ink-soft);
}

.form-row-2 {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px;
}

.cfg-range {
  margin-top: 8px;
  accent-color: var(--grass-dark);
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 10px;
  border-top: 2px dashed var(--paper-edge);
  padding-top: 16px;
}

.cancel-btn {
  background: var(--paper-deep);
  border: 2px solid var(--wood-mid);
  box-shadow: 0 2px 0 rgba(62, 36, 18, 0.35);
  color: var(--ink);
  padding: 8px 18px;
  border-radius: 6px;
  font-size: 13px;
  font-family: inherit;
  cursor: pointer;
  transition: filter 0.15s;
}

.cancel-btn:hover {
  filter: brightness(1.04);
}

.save-btn {
  background: var(--grass);
  border: 2px solid var(--grass-deep);
  box-shadow:
    inset 0 2px 0 var(--grass-light),
    inset 0 -3px 0 var(--grass-dark),
    0 3px 0 var(--wood-dark);
  color: #fffbe8;
  text-shadow: 1px 1px 0 var(--grass-deep);
  padding: 8px 22px;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 600;
  font-family: inherit;
  letter-spacing: 0.05em;
  cursor: pointer;
  transition: filter 0.15s;
}

.save-btn:hover:not(:disabled) {
  filter: brightness(1.08);
}

.save-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 加载 spinner（像素方块旋转） */
.spinner {
  display: inline-block;
  width: 9px;
  height: 9px;
  background: #fff;
  border-radius: 2px;
  animation: pixel-spin 0.8s steps(8) infinite;
}

@keyframes pixel-spin {
  to { transform: rotate(360deg); }
}
</style>
