# LLM 与 Agent 基石

> 掌握度：🟡 接触过

## 一句话直觉
如果把 Agent 比作一台自动驾驶汽车，**大语言模型（LLM）就是那台超级中央计算大脑**：它本身没有手脚（无法直接联网、无法修改文件），本质上只是在计算 Token 的概率分布；但由于它吸收了海量人类知识与逻辑模式，只要给它外接感知器（环境观察）与执行机构（工具调用），它就能进行规划、推理与决策。

---

## 📌 认知底座：从概率预测到自主决策

传统大模型与 Agent 大脑的演化跃迁：
1. **Next-token Prediction（下一个词预测）**：
   $$\max_\theta \sum_{t=1}^T \log P(w_t \mid w_1, \dots, w_{t-1}; \theta)$$
   模型本质上是在高维语义空间中求解上下文条件概率。
2. **Context Window as Working Memory**：
   上下文窗口的容量与注意力机制决定了 Agent 在单次循环中能同时保留多少环境变量与前序观察。
3. **System Prompt 约束**：
   通过元指令（Meta-instruction）为大模型注入角色定位、可用工具说明以及禁止执行的高危红线。

---

## 💻 最小 Agent 调用契约（Python 原生）

```python
import os

def call_llm_engine(prompt: str, system_prompt: str = "You are an autonomous agent.") -> str:
    """原生模拟 Agent 与 LLM 底座的单步通讯"""
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt}
    ]
    # return client.chat.completions.create(model='gpt-4o', messages=messages).choices[0].message.content
    return "Decision: Need to check file system."
```

---

## ⚖️ 模型能力对 Agent 表现的关键影响

| 模型属性 | 对 Agent 的影响 | 典型卡点 |
| :--- | :--- | :--- |
| **推理能力 (Reasoning)** | 决定多步规划能否正确拆解目标 | 复杂任务容易中途遗忘主线 |
| **指令遵循度 (IF)** | 决定能否严格按 JSON Schema 输出工具入参 | 输出多余闲聊字符导致解析失败 |
| **上下文容量 (Context)** | 决定能容纳多少轮工具调用结果 | 长上下文注意力稀释 (Lost in the middle) |

---

## 思考与自测
- 为什么纯粹的自回归预测（Next-token Prediction）能够涌现出逻辑推理与工具调用能力？
- 为什么在 Agent 系统中，我们更倾向于选择指令遵循度（Instruction Following）高而非文采华丽的大模型？
- 什么是「Lost in the Middle」现象？它对需要长轮次工具调用的 Agent 会带来怎样的灾难？\n