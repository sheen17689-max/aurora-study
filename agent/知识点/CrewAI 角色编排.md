# CrewAI 角色编排

> 掌握度：🟡 接触过

## 一句话直觉
CrewAI 是多智能体开发领域的**“开箱即用轻量脚手架”**：它抽象出了一套非常符合人类企业协作习惯的三元组——**Agent（员工）、Task（工作单）、Crew（团队）**；哪怕没有深厚的分布式系统知识，你也能在 50 行代码内组建一支包含研究员与写手的全自动 AI 生产力小队。

---

## 📌 核心抽象三元组

```python
from crewai import Agent, Task, Crew, Process

# 1. 定义员工
researcher = Agent(
    role="资深技术研究员",
    goal="调研 2026 年最热门的开源 Agent 框架",
    backstory="你是一名在硅谷关注 AI 基础设施的技术极客。"
)

# 2. 定义任务
task1 = Task(
    description="搜集 LangGraph 与 AutoGen 的对比优势",
    expected_output="一份 500 字的优缺点对比报告",
    agent=researcher
)

# 3. 组建战队执行
crew = Crew(
    agents=[researcher],
    tasks=[task1],
    process=Process.sequential  # 顺序执行流程
)
# result = crew.kickoff()
```

---

## 思考与自测
- CrewAI 与 LangGraph 相比，各自适用的业务场景与开发门槛有何不同？
- CrewAI 中的 `Process.hierarchical`（层级流程）是如何通过管理者 Agent 实现子任务分发与审核的？
- 在 CrewAI 中如何给特定 Agent 绑定专属的自定义 Python 工具？\n