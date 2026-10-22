# 工具调用与函数调用（Function Calling）全景详解

> 掌握度：🔵 理解

## 一句话直觉
Function Calling 就像给大模型发了一张**“外卖点单表”**：开发者用 JSON Schema 写明菜单（工具名称、参数类型、哪些必填），大模型不直接替你炒菜（不直接执行底层代码），而是极其规范地在点单表上勾选**「我要叫 get_weather，参数是 city='上海'」**；宿主程序收到这张单子后替它去执行，再把结果打包送回给模型。

---

## 📌 函数调用的 4 步标准生命周期

```
┌────────┐               ┌─────────┐               ┌───────────────┐
│ 客户端 │ ── 1.Prompt+Tools定义 ──> │ 大模型  │               │ 外部工具环境  │
│ (宿主) │ <── 2.tool_calls JSON ─── │ (大脑)  │               │ (Python/API)  │
│        │                                                 │               │
│        │ ── 3. 解析参数并真正执行函数 ────────────────────────> │ (执行本地代码) │
│        │ <─── 获得函数返回值 output ─────────────────────────── │ (返回执行结果) │
│        │                                                 └───────────────┘
│        │ ── 4. 将 tool output 回传给模型 ─> │ 大模型  │
│        │ <── 5. 输出自然语言最终回答 ────── │ (合成答案)│
└────────┘                                     └─────────┘
```

1. **注册与定义（Declaration）**：宿主程序通过标准 JSON Schema，将本地工具的输入契约（函数名、描述、入参结构）注入到 API 请求的 `tools` 参数中；
2. **决策与参数提取（Tool Selection & Argument Generation）**：大模型判断当前问题是否需要工具协助。若需要，模型输出特殊标记结构 `tool_calls`，携带 `id`、`name` 和符合 JSON Schema 的序列化入参；
3. **宿主执行（Client Execution）**：宿主程序捕获该信号，暂停向用户输出，在本地沙箱或安全进程中调用实际 Python 函数；
4. **上下文回传与总结（Tool Message Response）**：将执行结果封装为 `role: "tool"` 消息追加到对话上下文中，触发大模型进行最终归纳。

---

## 🛠️ 标准 JSON Schema 结构规范

```json
{
  "type": "function",
  "function": {
    "name": "query_database",
    "description": "执行只读 SQL 查询以获取用户信息与订单记录",
    "parameters": {
      "type": "object",
      "properties": {
        "sql": {
          "type": "string",
          "description": "待执行的 SELECT 语句，禁止任何写操作"
        },
        "limit": {
          "type": "integer",
          "description": "返回的最大记录条数",
          "default": 10
        }
      },
      "required": ["sql"]
    }
  }
}
```

---

## 💻 最小原生代码示例（原生 Python + OpenAI / 兼容接口）

```python
import json

# 1. 本地真实函数定义
def get_current_stock(ticker: str) -> str:
    """获取股票当前价格"""
    mock_db = {"AAPL": "225.40 USD", "NVDA": "128.50 USD"}
    return mock_db.get(ticker.upper(), "Stock not found")

# 2. 模拟根据模型返回的 tool_call 执行分发
def dispatch_tool_call(tool_call):
    fn_name = tool_call["name"]
    fn_args = json.loads(tool_call["arguments"])
    
    if fn_name == "get_current_stock":
        result = get_current_stock(**fn_args)
        return {
            "role": "tool",
            "tool_call_id": tool_call["id"],
            "name": fn_name,
            "content": result
        }
    raise ValueError(f"Unknown tool: {fn_name}")
```

---

## 思考与自测
- 为什么大模型不直接生成可执行的 Python 代码并在大模型服务器上运行，而是由客户端（宿主）执行 Function Calling？
- 如果大模型输出的 JSON 参数缺失了必填字段（缺少 required 字段）或类型错误，客户端应当如何向模型优雅反馈？
- Function Calling 与早期基于纯文本正则匹配（例如在 Prompt 中要求模型输出 `Action: xxx`）相比，有哪些本质优势？
