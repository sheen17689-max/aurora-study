<template>
  <div v-if="quiz && quiz.questions && quiz.questions.length" class="quiz-flip-wrapper">
    <div :class="['flip-card', isFlipped ? 'flipped' : '']">
      <!-- 正面：问题 -->
      <div class="card-face card-front">
        <div class="quiz-top">
          <div class="quiz-badge">
            <Brain :size="15" class="badge-icon" />
            <span class="badge-title">今日复习</span>
            <span class="quiz-concept">· {{ quiz.name }} ({{ levelName }})</span>
          </div>
          <button class="btn btn-outline btn-xs" @click="$emit('open-note', quiz.name)">
            <BookOpen :size="12" />
            <span>查阅笔记</span>
          </button>
        </div>

        <div class="quiz-question">
          <HelpCircle :size="16" class="q-icon" />
          <span class="q-text" v-html="renderInlineMarkdown(quiz.questions[0])"></span>
        </div>

        <div class="quiz-footer">
          <span class="hint-text">先在脑海中回忆推导，再翻看解答</span>
          <button class="btn btn-primary btn-sm" @click="isFlipped = true">
            <RotateCw :size="13" />
            <span>开始自测 / 查看答案</span>
          </button>
        </div>
      </div>

      <!-- 背面：解析与升降级 -->
      <div class="card-face card-back">
        <div class="quiz-top">
          <div class="quiz-badge answer-badge">
            <Sparkles :size="15" class="badge-icon text-success" />
            <span class="badge-title text-success">思考要点与自测解析</span>
          </div>
          <button class="btn btn-outline btn-xs" @click="isFlipped = false">
            <RotateCw :size="12" />
            <span>翻回题目</span>
          </button>
        </div>

        <div class="quiz-answer">
          <p>建议结合该知识点的「一句话直觉」与「核心公式」进行费曼输出。</p>
          <div class="quick-feynman-hint">
            🎙️ 你也可以让 AI 考官对你深入提问，检验掌握度！
          </div>
        </div>

        <div class="quiz-footer">
          <button class="btn btn-outline btn-sm" @click="$emit('open-note', quiz.name)">
            <BookOpen :size="13" />
            <span>查阅笔记</span>
          </button>
          <button class="btn btn-primary btn-sm success-btn" @click="handleLevelUp">
            <CheckCircle2 :size="13" />
            <span>答对了，升一级 ({{ nextLevelName }})</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { Brain, BookOpen, RotateCw, CheckCircle2, HelpCircle, Sparkles } from 'lucide-vue-next';
import { renderInlineMarkdown } from '../../utils/markdown';

const props = defineProps({
  quiz: Object
});

const emit = defineEmits(['open-note', 'update-level', 'toast']);

const isFlipped = ref(false);

const LV_MAP = {
  "⚪": "未学", "🟡": "接触过", "🔵": "理解", "🟢": "掌握"
};

const levelName = computed(() => LV_MAP[props.quiz?.level] || "接触过");

const nextLevel = computed(() => {
  const lv = props.quiz?.level;
  if (lv === '⚪') return '🟡';
  if (lv === '🟡') return '🔵';
  return '🟢';
});

const nextLevelName = computed(() => LV_MAP[nextLevel.value] || "理解");

const handleLevelUp = async () => {
  if (!props.quiz?.name) return;
  emit('update-level', { name: props.quiz.name, level: nextLevel.value });
  emit('toast', `🎉 已将「${props.quiz.name}」升级为 ${nextLevelName.value}！`);
};
</script>

<style scoped>
.quiz-flip-wrapper {
  perspective: 1000px;
  min-height: 150px;
  margin-bottom: 16px;
}
.flip-card {
  display: grid;
  width: 100%;
  min-height: 150px;
  transition: transform 0.5s cubic-bezier(0.4, 0, 0.2, 1);
  transform-style: preserve-3d;
}
.flip-card.flipped {
  transform: rotateY(180deg);
}

.card-face {
  grid-area: 1 / 1;
  position: relative;
  -webkit-backface-visibility: hidden;
  backface-visibility: hidden;
  background: var(--bg-card);
  border: 1px solid var(--border-card);
  border-radius: var(--radius-lg);
  padding: 16px 18px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  gap: 12px;
  box-shadow: var(--shadow-sm);
}

.card-front {
  border-top: 3px solid var(--accent-primary);
}
.card-back {
  border-top: 3px solid #059669;
  transform: rotateY(180deg);
}

.quiz-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.quiz-badge {
  font-size: 13px;
  font-weight: 700;
  color: var(--text-main);
  display: flex;
  align-items: center;
  gap: 6px;
}
.badge-icon {
  color: var(--accent-primary);
}
.badge-icon.text-success {
  color: #059669;
}
.badge-title.text-success {
  color: #059669;
}
.quiz-concept {
  color: var(--text-sub);
  font-weight: 500;
  font-size: 12.5px;
}

.quiz-question {
  margin: 8px 0;
  font-size: 14px;
  font-weight: 600;
  color: var(--text-main);
  line-height: 1.6;
  display: flex;
  gap: 8px;
}
.q-icon {
  color: var(--accent-primary);
  flex-shrink: 0;
  margin-top: 2px;
}
.q-text {
  flex: 1;
}

.quiz-answer {
  margin: 6px 0;
  font-size: 13px;
  color: var(--text-sub);
  line-height: 1.6;
}
.quick-feynman-hint {
  font-size: 12px;
  color: var(--accent-primary);
  margin-top: 6px;
  background: var(--accent-light);
  padding: 6px 10px;
  border-radius: var(--radius-sm);
}

.quiz-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 6px;
}
.hint-text {
  font-size: 11.5px;
  color: var(--text-muted);
}
.btn-xs {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 3px 8px;
  font-size: 11.5px;
}
.btn-sm {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 5px 14px;
  font-size: 12.5px;
}
.success-btn {
  background: #059669;
}
.success-btn:hover {
  background: #047857;
}
</style>
