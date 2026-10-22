# MCP 协议（Model Context Protocol）深度剖析

> 掌握度：🟡 接触过

## 一句话直觉
MCP 协议就像 AI 领域的 **USB-C 统一插口**：在过去，每个大模型客户端（Claude、Cursor、自定义 Agent）想要读 GitHub、查 SQLite 或发邮件，开发者都必须针对每个客户端重写一遍胶水代码；而有了 MCP，数据源与工具只需实现一次 **MCP Server** 标准协议，任何支持 MCP 的 **MCP Host / Client** 都能像插入 Type-C 外设一样即插即用！

---

## 📌 三层核心架构与传输协议

```
┌────────────────────────────────────────────────────────┐
│ MCP Host (如 Claude Desktop / IDE / 自研 Agent 运行时)  │
│ ┌────────────────────────────────────────────────────┐ │
│ │ MCP Client (负责协议协商与消息管道管理)            │ │
│ └─────────────────────────┬──────────────────────────┘ │
└───────────────────────────┼────────────────────────────┘
                            │ JSON-RPC 2.0 (stdio / SSE)
┌───────────────────────────▼────────────────────────────┐
│ MCP Server (如 SQLite Server / Git Server / Filesystem)│
│ • Resources (资源: 只读上下文，类比 GET)                │
│ • Prompts (提示模板: 预定义的上下文工程)               │
│ • Tools (工具: 带副作用的可调用函数，类比 POST)         │
└────────────────────────────────────────────────────────┘
```

1. **协议层**：基于成熟的 JSON-RPC 2.0 规范，保证跨语言、跨平台的高兼容性；
2. **传输层**：
   - **stdio（标准输入输出）**：本地进程间通信，速度极快，天然隔离与安全；
   - **SSE（Server-Sent Events）**：远程网络服务接入，适合跨机器服务暴露。
3. **三大能力基语**：
   - **Resources**：数据上下文（文件、表结构、API 日志）；
   - **Prompts**：标准化的交互提示模板与工作流预设；
   - **Tools**：带明确入参和返回签名的外部执行函数。

---

## 💻 最小 MCP Python Server 原生体验

```python
from mcp.server.fastmcp import FastMCP

# 初始化一个名为 'Demo Tools' 的极简 MCP Server
mcp = FastMCP("Demo Tools")

@mcp.tool()
def read_project_status(project_name: str) -> str:
    """读取本地项目的当前阶段与任务列表"""
    return f"项目 {project_name} 状态: 进行中，阶段 1 里程碑达成。"

if __name__ == "__main__":
    # 以 stdio 模式启动服务，等待 Host 客户端握手
    mcp.run(transport="stdio")
```

---

## 思考与自测
- 相比于传统把 API 包装成 OpenAI tools 字典，MCP 协议带来的最核心工程降本增效体现在哪里？
- MCP 协议定义的 Resources 与 Tools 之间，本质的设计哲学区别是什么？
- 在安全沙箱角度，MCP 的 stdio 本地进程隔离相比直接在 Host 进程里调用 Python 代码有哪些防御优势？
