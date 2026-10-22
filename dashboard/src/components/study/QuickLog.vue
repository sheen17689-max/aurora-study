<template>
  <div class="quick-log-card">
    <div class="card-head">
      <div class="head-title-wrap">
        <PenLine :size="15" class="head-icon" />
        <span class="card-title">快速记录</span>
      </div>
      <span class="head-tip">随时沉淀灵感与卡点</span>
    </div>

    <!-- 标签切换 (全部换 Lucide 图标) -->
    <div class="log-tabs">
      <button
        v-for="t in logTypes"
        :key="t.key"
        :class="['tab-btn', currentType === t.key ? 'active' : '']"
        @click="switchType(t)"
      >
        <component :is="t.iconComp" :size="12" />
        <span>{{ t.name }}</span>
      </button>
    </div>

    <textarea
      v-model="logText"
      class="log-textarea"
      :placeholder="placeholderText"
      @keydown.enter.ctrl="submitLog"
    ></textarea>

    <!-- 底部操作区：右下角正常尺寸按钮 -->
    <div class="log-footer">
      <span class="shortcut-tip">Ctrl + Enter 快捷保存</span>
      <button class="btn btn-primary log-submit-btn" :disabled="submitting" @click="submitLog">
        <Save :size="13" />
        <span>{{ submitting ? '保存中...' : '保存' }}</span>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { PenLine, BookOpen, HelpCircle, Target, Save } from 'lucide-vue-next';
import { appendLog } from '../../api';

const emit = defineEmits(['logged', 'toast']);

const logTypes = [
  {
    key: 'learned',
    name: '今日所学',
    iconComp: BookOpen,
    ph: '例：今天搞懂了反向传播中的链式法则求导与矩阵维度对齐'
  },
  {
    key: 'questions',
    name: '疑问卡点',
    iconComp: HelpCircle,
    ph: '例：卡点：在 PyTorch 导出 ONNX 时 Dynamic Axes 维度不匹配'
  },
  {
    key: 'plan',
    name: '明日计划',
    iconComp: Target,
    ph: '例：明天主攻：用 NumPy 手写实现简单的多层感知机'
  }
];

const currentType = ref('learned');
const placeholderText = ref('例：今天搞懂了反向传播中的链式法则求导与矩阵维度对齐');
const logText = ref('');
const submitting = ref(false);

const switchType = (t) => {
  currentType.value = t.key;
  placeholderText.value = t.ph;
};

const submitLog = async () => {
  const text = logText.value.trim();
  if (!text) {
    emit('toast', '请先写点内容再提交');
    return;
  }
  submitting.value = true;
  try {
    const res = await appendLog(text, currentType.value);
    if (res.ok) {
      logText.value = '';
      emit('toast', '已记入今日日志 ✓');
      emit('logged');
    }
  } catch (e) {
    emit('toast', '写入失败');
  } finally {
    submitting.value = false;
  }
};
</script>

<style scoped>
.quick-log-card {
  background: var(--bg-card);
  border: 1px solid var(--border-card);
  border-radius: var(--radius-lg);
  padding: 16px 18px;
  box-shadow: var(--shadow-sm);
  display: flex;
  flex-direction: column;
  height: 100%;
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
.head-tip {
  font-size: 11.5px;
  color: var(--text-muted);
}

.log-tabs {
  display: flex;
  gap: 4px;
  margin-bottom: 8px;
  background: var(--bg-subtle);
  border-radius: 999px;
  padding: 2.5px;
}
.tab-btn {
  flex: 1;
  background: transparent;
  border: none;
  padding: 5px 6px;
  border-radius: 999px;
  font-size: 11.5px;
  color: var(--text-sub);
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  transition: all 0.15s;
}
.tab-btn:hover {
  color: var(--text-main);
}
.tab-btn.active {
  background: var(--bg-card);
  color: var(--accent-primary);
  font-weight: 600;
  box-shadow: var(--shadow-sm);
}

.log-textarea {
  flex: 1;
  min-height: 72px;
  background: var(--bg-subtle);
  border: 1px solid var(--border-card);
  border-radius: var(--radius-sm);
  padding: 10px 12px;
  font-family: inherit;
  font-size: 13px;
  line-height: 1.5;
  color: var(--text-main);
  outline: none;
  resize: vertical;
  transition: all 0.15s;
}
.log-textarea:focus {
  background: var(--bg-card);
  border-color: var(--accent-primary);
}

/* 底部操作行：正常右下角按钮 */
.log-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 10px;
}
.shortcut-tip {
  font-size: 11px;
  color: var(--text-muted);
}
.log-submit-btn {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 6px 16px;
  font-size: 12.5px;
  font-weight: 600;
  border-radius: var(--radius-sm);
}
</style>
