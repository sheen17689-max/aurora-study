# smolagents 轻量代码智能体（Hugging Face）

> 掌握度：🟡 接触过

## 一句话直觉
smolagents 是 Hugging Face 打造的**“崇尚代码优先（CodeAgent）的极简智能体利器”**：全框架仅有约 1000 行极度精简的代码！它的核心革命是：不要让模型在笨拙的 JSON 字典里绕弯子调用工具，直接让大模型输出一段真实的 Python 代码，在解释器里顺序调用函数、处理循环与条件分支，效率与灵活性翻倍！

---

## 📌 CodeAgent vs ToolCallingAgent

| 维度 | 传统 ToolCallingAgent | smolagents CodeAgent |
| :--- | :--- | :--- |
| **表达载体** | JSON Schema 对象 | 纯原生 Python 代码片段 |
| **复杂逻辑** | 无法处理临时变量与复杂循环 | 原生支持 `for`, `if`, 变量临时缓存 |
| **往返轮次** | 调用 3 次工具需与 LLM 网络交互 3 轮 | 1 轮代码执行全部 3 次调用并组合 |
| **代码量** | 框架极其庞大冗长 | 极简透明，源码一目了然 |

---

## 思考与自测
- 为什么 Hugging Face 极力推崇 CodeAgent（让模型直接写代码调用工具）而非传统的 JSON Function Calling？
- smolagents 是如何在不依赖完整 Docker 的情况下，安全受限地执行受约束的 Python AST 语法的？
- smolagents 与 Hugging Face Hub 上的海量模型和工具是如何即插即用结合的？\n