# ReAct 范式（Reasoning + Acting）核心详解

> 掌握度：🔵 理解

## 一句话直觉
ReAct 就像一位**严谨的侦探破案**：侦探不会凭空猜凶手，而是「先动脑推导当下线索（**Thought 思考**）」，决定去查某份通话记录（**Action 行动**），拿到证据（**Observation 观察**）之后，再基于新线索进行下一轮推导，步步为营，直到锁定真相（**Final Answer 最终答复**）。

---

## 📌 核心状态转移契约

在传统纯 LLM 中，生成是单向开环的：
$$\text{Input Prompt} \longrightarrow \text{LLM Output}$$

在 ReAct 范式中，系统演化为一个**人在环外、模型在环内的离散动态决策闭环**：
在时间步 $t$，智能体处于环境状态 $S_t$，其演进轨迹为：

$$\tau_t = (c_1, a_1, o_1, c_2, a_2, o_2, \dots, c_t)$$

- **$c_t = \text{Thought}_t$（思考）**：大模型利用自注意力生成自由文本推理，分解子目标或分析前序观察；
- **$a_t = \text{Action}_t$（行动）**：大模型输出格式化的工具调用指令 $a_t \in \mathcal{A}$，暂停文本生成并转让控制权；
- **$o_t = \text{Observation}_t$（观察）**：外部环境执行工具并返回观测结果 $o_t \sim \mathcal{E}(a_t)$，拼接入上下文馈送给模型；
- **直到 $a_t = \text{Finish}$**：模型判定线索完备，输出面向最终用户的答复。

---

## 💻 20 行极简纯 Python ReAct 闭环原型

不依赖 LangChain 或任何重量级框架，纯原生展现 ReAct 核心 Loop：

```python
import re

# 1. 模拟环境工具 (Environment Tool)
def calculator(expr: str) -> str:
    try:
        return str(eval(expr))
    except Exception as e:
        return f"Error: {e}"

TOOLS = {"calculator": calculator}

# 2. ReAct 运行时循环 (Runtime Loop)
def run_react_agent(query: str, mock_llm_step):
    history = f"Question: {query}\n"
    for step in range(5):  # 避免死循环的最大轮次
        # 大模型生成下一步 (思考 + 行动)
        thought_and_action = mock_llm_step(history)
        history += thought_and_action + "\n"
        print(f"[Step {step + 1}]\n{thought_and_action}")

        # 检查是否达成最终答复
        if "Final Answer:" in thought_and_action:
            break

        # 正则提取 Action: tool_name(param)
        match = re.search(r"Action:\s*(\w+)\((.*)\)", thought_and_action)
        if match:
            tool_name, param = match.group(1), match.group(2)
            obs = TOOLS.get(tool_name, lambda x: "Tool not found")(param)
            history += f"Observation: {obs}\n"
            print(f"Observation: {obs}\n")
    return history
```

---

## ⚖️ ReAct 的优势与现实工程挑战

| 维度 | ReAct 范式 | 纯思维链 (CoT) | 纯行动派 (Act-only) |
| :--- | :--- | :--- | :--- |
| **外部信息时效性** | ⭐⭐⭐ 动态调用搜索引擎检索 | ❌ 仅依赖训练时死记硬背 | ⭐⭐ 缺少推理常盲目调用 |
| **幻觉率** | ⭐⭐⭐ 强观察事实锚定，显著抑制幻觉 | ❌ 遇到未知知识易一本正经胡说 | ⭐ 容易陷入工具参数拼写错误 |
| **Token 与耗时** | 耗费较多 Token，需要多次往返网络 | 耗时短，单次直接吐出 | 中等 |
| **工程卡点** | 容易陷入死循环（Loop 死锁） | 无法纠偏已输出的错误前序 | 难以解决多步复合逻辑 |

---

## 思考与自测
- 为什么在 ReAct 中，把大模型的输出分成 Thought 和 Action 两个阶段能显著降低幻觉？
- 如果工具返回了严重的报错信息（如 404 Not Found 或语法异常），ReAct 机制是如何实现自我纠错的？
- 在实际工程中，当 Agent 陷入「搜索 A -> 结果不符 -> 再次搜索 A」的死循环时，有哪些兜底策略？
