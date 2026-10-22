<template>
  <div class="diary-card">
    <div class="card-head">
      <div class="head-title-wrap">
        <History :size="15" class="head-icon" />
        <span class="card-title">回顾与日记</span>
      </div>
      <span class="head-tip">按时间沉淀学习轨迹</span>
    </div>

    <!-- 昨日打卡回顾 -->
    <div class="yest-block">
      <div class="yest-title">
        <Calendar :size="12" />
        <span>昨日打卡回顾</span>
      </div>
      <ul v-if="yesterday?.learned?.length" class="diary-bullets">
        <li v-for="(l, i) in yesterday.learned" :key="i" v-html="renderInlineMarkdown(l)"></li>
      </ul>
      <div v-else class="yest-empty">昨天暂无记录 — 今天从一条记录开始</div>
    </div>
    <div class="diary-divider"></div>

    <div v-if="diaries && diaries.length" class="timeline-container">
      <div v-for="(day, idx) in diaries.slice(0, 7)" :key="idx" class="timeline-day">
        <div class="timeline-dot"></div>
        <div class="day-date">{{ day.date }}</div>

        <!-- 今日所学 -->
        <div v-if="day.learned && day.learned.length" class="day-section">
          <ul class="diary-bullets">
            <li v-for="(l, lIdx) in day.learned" :key="lIdx" v-html="renderInlineMarkdown(l)">
            </li>
          </ul>
        </div>

        <!-- 疑问卡点 -->
        <div v-if="day.questions && day.questions.length" class="day-section questions">
          <div v-for="(q, qIdx) in day.questions" :key="qIdx" class="question-row">
            <HelpCircle :size="13" class="row-icon q-row-icon" />
            <span v-html="renderInlineMarkdown(q)"></span>
          </div>
        </div>

        <!-- 明日计划 -->
        <div v-if="day.plan && day.plan.length" class="day-section plans">
          <div v-for="(p, pIdx) in day.plan" :key="pIdx" class="plan-row">
            <Target :size="13" class="row-icon p-row-icon" />
            <span v-html="renderInlineMarkdown(p)"></span>
          </div>
        </div>
      </div>
    </div>

    <div v-else class="empty-diary">
      还没有学习打卡记录，从今天的第一条记录开始吧！
    </div>
  </div>
</template>

<script setup>
import { History, Calendar, HelpCircle, Target } from 'lucide-vue-next';
import { renderInlineMarkdown } from '../../utils/markdown';

defineProps({
  diaries: Array,
  yesterday: Object
});
</script>

<style scoped>
.diary-card {
  background: var(--bg-card);
  border: 1px solid var(--border-card);
  border-radius: var(--radius-lg);
  padding: 18px 20px;
  box-shadow: var(--shadow-sm);
}
.card-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 14px;
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
  font-size: 14.5px;
  font-weight: 700;
  color: var(--text-main);
}
.head-tip {
  font-size: 11.5px;
  color: var(--text-muted);
}

.timeline-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
  position: relative;
  padding-left: 14px;
  border-left: 2px solid var(--border-card);
  margin-left: 6px;
}

.timeline-day {
  position: relative;
}
.timeline-dot {
  position: absolute;
  left: -19px;
  top: 4px;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--accent-primary);
  border: 2px solid var(--bg-card);
}

.day-date {
  font-size: 12.5px;
  font-weight: 700;
  color: var(--text-sub);
  margin-bottom: 6px;
}

.diary-bullets {
  list-style: none;
}
.diary-bullets li {
  font-size: 13px;
  color: var(--text-sub);
  line-height: 1.6;
  padding-left: 12px;
  position: relative;
  margin-bottom: 4px;
}
.diary-bullets li:before {
  content: "•";
  position: absolute;
  left: 2px;
  top: 0;
  color: var(--accent-primary);
  font-size: 14px;
}

.question-row {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12.5px;
  color: #b45309;
  margin-top: 4px;
  line-height: 1.5;
}
.q-row-icon {
  color: #d97706;
  flex-shrink: 0;
}
.plan-row {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12.5px;
  color: #0284c7;
  margin-top: 4px;
  line-height: 1.5;
}
.p-row-icon {
  color: var(--accent-primary);
  flex-shrink: 0;
}

.yest-block {
  background: var(--bg-subtle);
  border: 1px solid var(--border-card);
  border-radius: var(--radius-sm);
  padding: 10px 14px;
}
.yest-title {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 11.5px;
  font-weight: 700;
  color: var(--text-muted);
  margin-bottom: 6px;
}
.yest-empty {
  font-size: 12.5px;
  color: var(--text-muted);
}
.diary-divider {
  border-top: 1px dashed var(--border-card);
  margin: 14px 0;
}

.empty-diary {
  font-size: 13px;
  color: var(--text-muted);
  padding: 12px 0;
}
</style>
