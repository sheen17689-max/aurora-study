<template>
  <div class="mastery-card">
    <div class="card-head">
      <div class="head-title-wrap">
        <Activity :size="15" class="head-icon" />
        <span class="card-title">学习进度</span>
      </div>
      <span class="muted-text">共 {{ total }} 节点</span>
    </div>

    <!-- 双指标核心数据展示 -->
    <div class="dual-metrics-row">
      <div class="metric-pill">
        <span class="metric-label">知识覆盖度</span>
        <div class="metric-val-group">
          <span class="metric-num text-primary">{{ coveragePct }}%</span>
          <span class="metric-sub">{{ coveredCount }}/{{ total }}</span>
        </div>
        <div class="metric-bar-bg">
          <div class="metric-bar-fill coverage-fill" :style="{ width: coveragePct + '%' }"></div>
        </div>
      </div>

      <div class="metric-pill">
        <span class="metric-label">深度理解度</span>
        <div class="metric-val-group">
          <span class="metric-num text-success">{{ masteredPct }}%</span>
          <span class="metric-sub">{{ masteredCount }}/{{ total }}</span>
        </div>
        <div class="metric-bar-bg">
          <div class="metric-bar-fill mastery-fill" :style="{ width: masteredPct + '%' }"></div>
        </div>
      </div>
    </div>

    <!-- 掌握度分布明细 -->
    <div class="donut-legend">
      <div v-for="row in legendRows" :key="row.key" class="legend-row">
        <span class="legend-dot" :style="{ background: row.color }"></span>
        <span class="legend-label">{{ row.name }}</span>
        <span class="legend-bar"><i :style="{ width: row.pct + '%', background: row.color }"></i></span>
        <span class="legend-val">{{ row.count }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { Activity } from 'lucide-vue-next';

const props = defineProps({
  data: Object
});

const LV_DEF = [
  { key: '🟢', name: '掌握', color: '#059669' },
  { key: '🔵', name: '理解', color: '#2563eb' },
  { key: '🟡', name: '接触过', color: '#d97706' },
  { key: '⚪', name: '未学', color: '#a8a29e' }
];

const total = computed(() => props.data?.framework?.total || 0);

// 知识覆盖度（接触过 + 理解 + 掌握）
const coveredCount = computed(() => {
  const cnt = props.data?.framework?.counts || {};
  return (cnt['🟡'] || 0) + (cnt['🔵'] || 0) + (cnt['🟢'] || 0);
});

const coveragePct = computed(() => {
  if (!total.value) return 0;
  return Math.round((coveredCount.value / total.value) * 100);
});

// 深度掌握度（理解 + 掌握）
const masteredCount = computed(() => {
  const cnt = props.data?.framework?.counts || {};
  return (cnt['🔵'] || 0) + (cnt['🟢'] || 0);
});

const masteredPct = computed(() => {
  if (!total.value) return 0;
  return Math.round((masteredCount.value / total.value) * 100);
});

const legendRows = computed(() => {
  const cnt = props.data?.framework?.counts || {};
  const t = total.value || 1;
  return LV_DEF.map(({ key, name, color }) => ({
    key,
    name,
    color,
    count: cnt[key] || 0,
    pct: Math.round(((cnt[key] || 0) / t) * 100)
  }));
});
</script>

<style scoped>
.mastery-card {
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
  margin-bottom: 12px;
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
.muted-text {
  font-size: 11.5px;
  color: var(--text-muted);
}

/* 双指标卡片 */
.dual-metrics-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  margin-bottom: 14px;
}
.metric-pill {
  background: var(--bg-subtle);
  border: 1px solid var(--border-card);
  border-radius: var(--radius-md);
  padding: 10px 12px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.metric-label {
  font-size: 11px;
  font-weight: 600;
  color: var(--text-sub);
}
.metric-val-group {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 6px;
}
.metric-num {
  font-size: 18px;
  font-weight: 800;
  line-height: 1.1;
  font-variant-numeric: tabular-nums;
}
.text-primary {
  color: var(--accent-primary);
}
.text-success {
  color: #059669;
}
[data-theme="dark"] .text-success {
  color: #10b981;
}
.metric-sub {
  font-size: 11px;
  color: var(--text-muted);
  font-variant-numeric: tabular-nums;
}
.metric-bar-bg {
  height: 4px;
  background: rgba(0, 0, 0, 0.06);
  border-radius: 99px;
  overflow: hidden;
  margin-top: 2px;
}
[data-theme="dark"] .metric-bar-bg {
  background: rgba(255, 255, 255, 0.1);
}
.metric-bar-fill {
  height: 100%;
  border-radius: 99px;
  transition: width 0.3s ease;
}
.coverage-fill {
  background: var(--accent-primary);
}
.mastery-fill {
  background: #059669;
}

/* 分布图例 */
.donut-legend {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding-top: 10px;
  border-top: 1px solid var(--border-card);
  margin-top: auto;
}
.legend-row {
  display: grid;
  grid-template-columns: 8px 42px 1fr 22px;
  align-items: center;
  gap: 8px;
  font-size: 11.5px;
  color: var(--text-sub);
}
.legend-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
}
.legend-label {
  white-space: nowrap;
}
.legend-bar {
  height: 4px;
  background: var(--bg-subtle);
  border-radius: 99px;
  overflow: hidden;
}
.legend-bar i {
  display: block;
  height: 100%;
  border-radius: 99px;
}
.legend-val {
  text-align: right;
  font-weight: 600;
  color: var(--text-main);
  font-variant-numeric: tabular-nums;
}
</style>
