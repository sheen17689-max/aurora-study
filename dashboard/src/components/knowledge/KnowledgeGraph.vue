<template>
  <div class="graph-card">
    <div class="graph-header">
      <div class="graph-title-group">
        <span class="graph-icon">🌌</span>
        <span class="graph-title">深度学习 · 知识星系图谱 (Graph View)</span>
      </div>
      <div class="graph-tips">
        <span>💡 滚轮缩放 ｜ 拖拽平移 ｜ 点击星球探索笔记</span>
      </div>
    </div>

    <!-- ECharts 容器 -->
    <div ref="chartRef" class="echarts-dom"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue';
import * as echarts from 'echarts';

const props = defineProps({
  data: Object
});

const emit = defineEmits(['open-note']);

const chartRef = ref(null);
let myChart = null;

const LV_COLORS = {
  '🟢': '#10b981',
  '🔵': '#3b82f6',
  '🟡': '#f59e0b',
  '⚪': '#94a3b8'
};

const buildGraphData = () => {
  if (!props.data?.framework?.sections) return { nodes: [], links: [], categories: [] };

  const nodes = [];
  const links = [];
  const categories = [];

  // 1. 板块枢纽节点
  props.data.framework.sections.forEach((sec, idx) => {
    categories.push({ name: sec.name });

    nodes.push({
      id: 'SEC_' + sec.name,
      name: sec.name,
      symbolSize: 42,
      category: idx,
      itemStyle: {
        color: '#6366f1',
        shadowBlur: 16,
        shadowColor: 'rgba(99, 102, 241, 0.5)'
      },
      label: {
        show: true,
        fontSize: 12,
        fontWeight: 'bold',
        color: '#ffffff'
      },
      isSection: true
    });

    // 2. 板块内知识点节点（含分组节点及其缩进子项）
    const pushItem = (it, srcId) => {
      const color = LV_COLORS[it.level] || '#94a3b8';
      nodes.push({
        id: it.name,
        name: it.name,
        symbolSize: it.hasNote ? 26 : 20,
        category: idx,
        itemStyle: {
          color: color,
          borderColor: it.hasNote ? '#ffffff' : 'transparent',
          borderWidth: 2,
          shadowBlur: 10,
          shadowColor: color
        },
        label: {
          show: true,
          position: 'right',
          fontSize: 11,
          color: '#cbd5e1'
        },
        rawItem: it
      });

      // 连线到上级（板块中心或分组节点）
      links.push({
        source: srcId,
        target: it.name,
        lineStyle: {
          color: 'rgba(255,255,255,0.15)',
          width: 1,
          curveness: 0.05
        }
      });

      // 3. 关联双链跨概念连线
      if (it.link && it.link !== it.name) {
        links.push({
          source: it.name,
          target: it.link,
          lineStyle: {
            color: '#38bdf8',
            width: 2,
            type: 'dashed',
            curveness: 0.2
          }
        });
      }
    };
    sec.items.forEach(it => {
      pushItem(it, 'SEC_' + sec.name);
      (it.children || []).forEach(c => pushItem(c, it.name));
    });
  });

  // 4. 手动增加经典跨板块知识链接
  const crossLinks = [
    { s: '反向传播', t: '梯度下降' },
    { s: '梯度下降', t: '过拟合' },
    { s: '损失函数（MSE / 交叉熵）', t: '前向传播' },
    { s: '激活函数（sigmoid / tanh / ReLU）', t: '反向传播' },
    { s: '卷积层 / 池化层', t: '目标检测（YOLO 系列）' },
    { s: '正则化（L2、Dropout）', t: '过拟合 / 欠拟合' },
    { s: '模型部署基础（ONNX / 量化）', t: '目标检测（YOLO 系列）' }
  ];

  crossLinks.forEach(cl => {
    links.push({
      source: cl.s,
      target: cl.t,
      lineStyle: {
        color: '#f43f5e',
        width: 1.5,
        type: 'dotted',
        curveness: 0.25
      }
    });
  });

  return { nodes, links, categories };
};

const renderChart = () => {
  if (!chartRef.value) return;
  if (!myChart) {
    myChart = echarts.init(chartRef.value);
    myChart.on('click', (params) => {
      if (params.dataType === 'node' && !params.data.isSection) {
        emit('open-note', params.data.name, params.data.rawItem);
      }
    });
  }

  const { nodes, links, categories } = buildGraphData();

  const option = {
    backgroundColor: '#090d16',
    tooltip: {
      formatter: (params) => {
        if (params.dataType === 'node') {
          if (params.data.isSection) return `<b>🌌 板块中心：${params.data.name}</b>`;
          const it = params.data.rawItem;
          return `<b>⭐ ${params.data.name}</b><br/>掌握度：${it?.level || '接触过'}<br/>${it?.hasNote ? '📝 包含结构化精讲笔记 (点击查阅)' : '⚪ 点击创建笔记'}`;
        }
        return '';
      }
    },
    series: [
      {
        type: 'graph',
        layout: 'force',
        data: nodes,
        links: links,
        categories: categories,
        roam: true,
        draggable: true,
        label: {
          show: true
        },
        force: {
          repulsion: 260,
          edgeLength: [50, 140],
          gravity: 0.12,
          friction: 0.6
        },
        emphasis: {
          focus: 'adjacency',
          lineStyle: {
            width: 3
          }
        }
      }
    ]
  };

  myChart.setOption(option);
};

onMounted(() => {
  renderChart();
  window.addEventListener('resize', () => myChart?.resize());
});

watch(() => props.data, () => renderChart(), { deep: true });

onUnmounted(() => {
  myChart?.dispose();
});
</script>

<style scoped>
.graph-card {
  background: #090d16;
  border: 1px solid #1f2937;
  border-radius: var(--radius-lg);
  overflow: hidden;
  box-shadow: var(--shadow-lg);
}
.graph-header {
  padding: 16px 22px;
  background: #111827;
  border-bottom: 1px solid #1f2937;
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.graph-title-group {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #f9fafb;
}
.graph-icon { font-size: 18px; }
.graph-title { font-size: 15px; font-weight: 700; }
.graph-tips {
  font-size: 12px;
  color: #9ca3af;
}

.echarts-dom {
  width: 100%;
  height: 640px;
}
</style>
