# LangGraph 状态机编排核心详解

> 掌握度：🟡 接触过

## 一句话直觉
LangGraph 就像把智能体放进了一张**“带红绿灯的高速公路网络”**：每个大模型或工具节点是一个服务区，路标是**“状态（State）”**；更关键的是，它彻底打破了传统链式（Chain）单向无法回头的问题，不仅支持**循环回滚（Cycles）**，还能在关键收费站亮起红灯等待**“人工交警签字审批（Human-in-the-loop）”**后才放行。

---

## 📌 三大核心要素

1. **State（统一状态契约）**：
   图在所有节点之间流转的唯一数据载荷（Payload），通常用 Python `TypedDict` 或 Pydantic 定义，支持使用 Reducer（如 `operator.add`）进行增量归并。
2. **Nodes（节点）**：
   普通的 Python 函数，入参是当前 `State`，返回值是一个包含要更新字段的字典。
3. **Edges（边与路由）**：
   - **普通边（Normal Edge）**：执行完节点 A 直接无条件转移到节点 B；
   - **条件边（Conditional Edge）**：根据函数的返回值动态决策下一站（如：需要调用工具则去 `tools` 节点，任务完成则去 `END` 终点）。

---

## 💻 最小 StateGraph 伪代码

```python
from typing import Annotated, TypedDict
import operator
from langgraph.graph import StateGraph, END

# 1. 定义状态
class AgentState(TypedDict):
    messages: Annotated[list, operator.add]

# 2. 定义节点
def agent_reasoner(state: AgentState):
    # 调用 LLM 思考
    return {"messages": ["Thought: I should check status"]}

def should_continue(state: AgentState) -> str:
    # 条件路由逻辑
    if "Error" in state["messages"][-1]:
        return "retry"
    return "end"

# 3. 编排状态图
workflow = StateGraph(AgentState)
workflow.add_node("agent", agent_reasoner)
workflow.set_entry_point("agent")
workflow.add_conditional_edges("agent", should_continue, {
    "retry": "agent",
    "end": END
})
app = workflow.compile()
```

---

## 思考与自测
- 为什么在复杂的长程任务中，LangChain 的传统线性 Chain 会逐渐失效，而必须引入基于图（Graph）的状态机？
- LangGraph 是如何利用 Checkpointer（检查点机制）实现人工审批（Human-in-the-loop）与时间旅行（Time Travel）回滚的？
- 在定义 State 时，Reducer 函数（例如 `operator.add`）起到了什么关键作用？
