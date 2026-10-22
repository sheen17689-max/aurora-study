# Workflows 与 Agents 架构模式（Anthropic 权威指南）

> 掌握度：🟡 接触过

## 一句话直觉
Anthropic 在其经典工程指南《Building Effective Agents》中指出：不要一上来就搞黑盒完全自主的 Agent！**「能用简单 Workflow 解决的，绝不要用复杂 Agent」**。系统根据自主程度从低到高分为两大家族：
- **Workflows（确定性工作流）**：系统的主执行流程由明确的 Python 代码编排，模型只在其中担当高效算子；
- **Agents（自主智能体）**：系统的主循环由大模型自身动态驱动，大模型自发决策工具调用与终止时机。

---

## 📌 Anthropic 归纳的 5 大基础工程模式

```
1. Prompt Chaining (提示链)
   [Step 1] ──> [Gate / Parse] ──> [Step 2] ──> [Output]

2. Routing (路由分发)
                  ┌──> [专家 A (如代码助手)]
   [输入分发器] ────┼──> [专家 B (如文档专家)]
                  └──> [专家 C (如退款审批)]

3. Parallelization (并行化)
                  ┌──> [并行子任务 1] ──┐
   [输入] ────────┼──> [并行子任务 2] ──┼──> [聚合器]
                  └──> [并行子任务 3] ──┘

4. Orchestrator-Workers (编排者-工作者)
                  ┌──> [Worker 1] ──┐
   [Orchestrator] ┼──> [Worker 2] ──┼──> [Orchestrator 聚合评估]
                  └──> [Worker 3] ──┘

5. Evaluator-Optimizer (评估者-优化者双环)
   [Generator 生成] <──── 反馈修改 ────┐
          │                            │
          ▼                            │
   [Evaluator 评估打分] ── 未达标 ──────┘
          │
          ▼ 达标
       [最终产出]
```

---

## ⚖️ 选型决策准则

| 场景需求 | 推荐模式 | 核心收益 |
| :--- | :--- | :--- |
| **步骤固定，质量要求极高** | Prompt Chaining + Evaluator-Optimizer | 可测性强，避免模型天马行空 |
| **任务跨多个专业领域** | Routing（意图分类 + 专业提示） | 降低单个 Prompt 复杂度，提高准确率 |
| **长文档处理 / 多维度横评** | Parallelization（并行处理） | 吞吐量大，大幅降低整体 Wall-clock 延迟 |
| **子任务数量事先不可知（如复杂编程）** | Orchestrator-Workers 或 自主 Agent | 动态拆解，灵活性最高 |

---

## 思考与自测
- 为什么 Anthropic 建议在构建生产应用时，先从 Prompt Chaining 开始，而不是直接上多智能体（Multi-Agent）？
- 在 Evaluator-Optimizer 模式中，如何防止 Generator 与 Evaluator 陷入无限互掐（即评估器永远挑刺导致死循环）？
- 编排者-工作者架构中，中央 Orchestrator 的上下文 Token 很容易爆炸，有哪些典型的治理方法？
