# -*- coding: utf-8 -*-
"""Aurora 研学管家 LangGraph ReAct 智能体中枢。

管理大模型客户端初始化、状态图构建、内存检查点持久化以及事件流分发。
"""
import asyncio
import json
import logging
import os
import subprocess
import time
import urllib.request
from typing import AsyncGenerator, Dict, Any

from .config import load_agent_config
from .tools import AGENT_TOOLS

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """你是一个严谨、富有启发性且幽默风趣的【AI 研学管家兼私教导师】。
你的使命是辅助学员深度研学《深度学习》与《Agent 学习》两本经典知识库。

你的专属能力与行为守则：
1. 查阅本地知识库 (read_knowledge_note)：
   - 当学员提问某个概念、算法或代码时，必须【先调用 read_knowledge_note】获取本地标准笔记；
   - 基于本地笔记进行深入浅出的直觉化讲解，结合数学公式、代码与工程考点。
2. 费曼答辩与考查 (Exam & Socratic Dialogue)：
   - 当学员说「考考我 xxx」或想升级掌握度时，调取该知识点的自测考题，以苏格拉底式提问考查学员；
   - 绝不要一次性把答案全盘抛出，而是以提问启发其思考。
3. 动态升级掌握度 (update_node_level)：
   - 当学员回答深刻、讲清了原理、公式与边界时，给予充分肯定，并主动调用 update_node_level 将该概念升级为 🔵 (理解) 或 🟢 (掌握)！
4. 记录学习流水 (record_study_diary)：
   - 当学员说「记一下今天学了 xxx」或完成了某个里程碑时，主动提炼精要，调用 record_study_diary 归整入当天的学习日志。
5. 查阅速查词典 (query_glossary)：
   - 当学员问及常见易混淆 API 或对比时，调用词典快速检索。
6. 查阅全局框架 (list_knowledge_framework)：
   - 当学员询问全景进度或学习路线建议时，调用此工具分析掌握度薄弱项。
7. 联网搜索与网页阅读 (searxng_web_search / web_url_read，由 MCP 提供)：
   - 当学员询问最新资讯、库的版本变化、报错信息、或本地笔记未覆盖的内容时，调用 searxng_web_search 检索；
   - 需要深入阅读某个网页时，用 web_url_read 抓取正文；回答中附上来源链接；
   - 若调用失败（如本地搜索服务未启动），坦诚告知并基于已有知识回答。

回答风格：专业沉稳、亲切热忱、结构清晰，善用直觉比喻。数学公式使用 LaTeX 规范。"""

_cached_agent = None
_cached_cfg_hash = None
_memory_saver = None
_mcp_client = None
_mcp_tools = None
_mcp_cfg_hash = None


async def _load_mcp_tools(cfg: dict) -> list:
    """加载 agent_config.json 中 mcp_servers 声明的 MCP 外部工具。

    配置格式与 Claude Desktop 相同（stdio/sse 均可）。加载失败时优雅降级为仅本地工具，
    不影响主对话链路。客户端与工具按配置哈希缓存，避免每次对话都重启 MCP 进程。
    """
    global _mcp_client, _mcp_tools, _mcp_cfg_hash
    servers = cfg.get("mcp_servers") or {}
    if not servers:
        return []

    cfg_hash = json.dumps(servers, sort_keys=True, ensure_ascii=False)
    if _mcp_tools is not None and cfg_hash == _mcp_cfg_hash:
        return _mcp_tools

    try:
        from langchain_mcp_adapters.client import MultiServerMCPClient
    except ImportError:
        logger.warning("未安装 langchain-mcp-adapters，MCP 工具不可用: pip install langchain-mcp-adapters")
        return []

    # 配置变了：先关闭旧客户端（顺带停掉旧的 MCP 子进程）
    if _mcp_client is not None:
        try:
            close = getattr(_mcp_client, "close", None)
            if close:
                res = close()
                if asyncio.iscoroutine(res):
                    await res
        except Exception:
            pass
        _mcp_client = None
        _mcp_tools = None

    conns = {}
    for name, sc in servers.items():
        sc = dict(sc)
        cmd = sc.get("command", "")
        # Windows 上 npx/npm 需要 .cmd 后缀才能被 CreateProcess 拉起
        if os.name == "nt" and cmd in ("npx", "npm"):
            sc["command"] = cmd + ".cmd"
        # MCP stdio 的 env 是完全替换而非追加，必须并入父进程环境（PATH 等）
        sc["env"] = {**os.environ, **(sc.get("env") or {})}
        conns[name] = sc

    try:
        client = MultiServerMCPClient(conns)
        tools = await client.get_tools()
        _mcp_client = client
        _mcp_tools = tools
        _mcp_cfg_hash = cfg_hash
        logger.info(f"MCP 工具加载成功（{len(tools)} 个）: {[t.name for t in tools]}")
        return tools
    except Exception as e:
        logger.warning(f"MCP 工具加载失败，本轮对话仅使用本地知识库工具: {e}")
        return []


def _is_ollama_url(base_url: str) -> bool:
    """判断 base_url 是否指向本地 Ollama 服务"""
    return "11434" in (base_url or "")


def _ollama_root(base_url: str) -> str:
    return (base_url or "").split("/v1")[0].rstrip("/") or "http://localhost:11434"


def _ollama_healthy(root: str) -> bool:
    try:
        req = urllib.request.Request(root + "/api/tags")
        with urllib.request.urlopen(req, timeout=1.5) as r:
            return r.status == 200
    except Exception:
        return False


def ensure_ollama_service(base_url: str, timeout: float = 20.0) -> bool:
    """确保本地 Ollama 服务可用：先健康检查，未运行则后台拉起 `ollama serve`。

    服务以脱离终端的后台进程启动，即使本程序退出，Ollama 也会继续常驻。
    """
    root = _ollama_root(base_url)
    if _ollama_healthy(root):
        return True

    logger.info("未检测到 Ollama 服务，尝试后台启动 ollama serve ...")
    try:
        creationflags = 0
        if os.name == "nt":
            creationflags = subprocess.CREATE_NO_WINDOW | subprocess.DETACHED_PROCESS
        subprocess.Popen(
            ["ollama", "serve"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=creationflags,
        )
    except FileNotFoundError:
        logger.error("未找到 ollama 命令，请先安装 Ollama: https://ollama.com")
        return False

    deadline = time.time() + timeout
    while time.time() < deadline:
        if _ollama_healthy(root):
            return True
        time.sleep(0.5)
    return _ollama_healthy(root)


def ollama_has_model(base_url: str, model: str) -> bool:
    """检查本地 Ollama 是否已拉取指定模型"""
    try:
        req = urllib.request.Request(_ollama_root(base_url) + "/api/tags")
        with urllib.request.urlopen(req, timeout=2.0) as r:
            data = json.loads(r.read().decode("utf-8"))
        names = {m.get("name", "") for m in data.get("models", [])}
        names |= {n.split(":")[0] for n in names}
        return model in names
    except Exception:
        return False


def get_memory_saver():
    global _memory_saver
    if _memory_saver is None:
        try:
            from langgraph.checkpoint.memory import MemorySaver
            _memory_saver = MemorySaver()
        except ImportError:
            _memory_saver = None
    return _memory_saver


async def _repair_dangling_tool_calls(agent, config) -> int:
    """修复检查点历史里悬挂的 tool_calls，返回修补数量。

    工具执行被中断（前端点停止、外部服务如 SearXNG 崩溃、请求超时断连）时，
    带 tool_calls 的 AIMessage 已进入检查点却没有对应 ToolMessage；此后该线程的
    每次请求都会被 LangGraph 以 INVALID_CHAT_HISTORY 拒绝，整个会话卡死。
    这里把缺失的 ToolMessage 按原位（紧跟其 AIMessage）补写回历史。
    任何异常都吞掉，绝不阻断主对话链路。
    """
    try:
        state = await agent.aget_state(config)
        messages = list((state.values or {}).get("messages") or [])
        if not messages:
            return 0
        from langchain_core.messages import AIMessage, RemoveMessage, ToolMessage
        from langgraph.graph.message import REMOVE_ALL_MESSAGES

        answered = {m.tool_call_id for m in messages if isinstance(m, ToolMessage)}
        rebuilt = []
        fixes = 0
        for m in messages:
            rebuilt.append(m)
            if isinstance(m, AIMessage) and m.tool_calls:
                for tc in m.tool_calls:
                    tc_id = tc.get("id")
                    if tc_id and tc_id not in answered:
                        rebuilt.append(ToolMessage(
                            content="⚠️ 该工具调用被中断（外部服务异常或手动停止），未返回结果；请基于已有信息继续回答。",
                            tool_call_id=tc_id,
                            name=tc.get("name") or "tool",
                        ))
                        fixes += 1
        if not fixes:
            return 0
        # 全量重建以保持顺序（ToolMessage 必须紧跟其 AIMessage，严格校验的提供商要求）
        await agent.aupdate_state(
            config,
            {"messages": [RemoveMessage(id=REMOVE_ALL_MESSAGES), *rebuilt]},
            as_node="agent",
        )
        logger.warning(
            f"已修补 {fixes} 个悬挂的 tool_call（thread={config.get('configurable', {}).get('thread_id')}）"
        )
        return fixes
    except Exception:
        logger.exception("修补悬挂 tool_calls 失败（忽略，不阻断对话）")
        return 0


async def get_agent_executor():
    """获取或重新构建 LangGraph ReAct 智能体实例（本地工具 + MCP 外部工具）"""
    global _cached_agent, _cached_cfg_hash
    cfg = load_agent_config()
    mcp_hash = json.dumps(cfg.get("mcp_servers") or {}, sort_keys=True, ensure_ascii=False)
    current_hash = f"{cfg.get('provider')}:{cfg.get('model')}:{cfg.get('base_url')}:{cfg.get('api_key')}:{cfg.get('temperature')}:{mcp_hash}"

    if _cached_agent is not None and current_hash == _cached_cfg_hash:
        return _cached_agent, cfg

    api_key = cfg.get("api_key", "").strip()
    if not api_key:
        return None, cfg

    try:
        from langchain_openai import ChatOpenAI
        from langgraph.prebuilt import create_react_agent
    except ImportError as e:
        logger.error(f"缺少 LangGraph 或 LangChain 依赖: {e}")
        return None, cfg

    base_url = cfg.get("base_url", "").strip() or "https://api.deepseek.com/v1"
    model_name = cfg.get("model", "").strip() or "deepseek-chat"
    temperature = float(cfg.get("temperature", 0.3))

    llm = ChatOpenAI(
        model=model_name,
        api_key=api_key,
        base_url=base_url,
        temperature=temperature,
        streaming=True,
    )

    mcp_tools = await _load_mcp_tools(cfg)
    tools = AGENT_TOOLS + mcp_tools

    memory = get_memory_saver()
    agent = create_react_agent(
        model=llm,
        tools=tools,
        prompt=SYSTEM_PROMPT,
        checkpointer=memory,
    )

    _cached_agent = agent
    _cached_cfg_hash = current_hash
    return _cached_agent, cfg


async def stream_agent_chat(
    message: str,
    thread_id: str = "default_user",
    book: str = "dl"
) -> AsyncGenerator[str, None]:
    """与 Agent 异步对话，并以 SSE 格式实时推送事件。"""
    cfg = load_agent_config()

    # 本地 Ollama 模式：对话前确保服务已启动（懒启动，用户无感）
    if _is_ollama_url(cfg.get("base_url", "")):
        yield f"data: {json.dumps({'type': 'thought', 'content': '正在检查本地模型服务状态...'})}\n\n"
        # 同步检测放到线程池，避免冷启动 Ollama 时阻塞整个事件循环
        service_ok = await asyncio.to_thread(ensure_ollama_service, cfg["base_url"])
        if not service_ok:
            hint = (
                "⚠️ **未能连接到本地 Ollama 服务，自动启动也失败了。**\n\n"
                "请检查：\n"
                "1. 是否已安装 [Ollama](https://ollama.com)（命令行执行 `ollama --version` 应有输出）；\n"
                "2. 或手动在终端执行 `ollama serve` 启动服务后再试。"
            )
            for char in hint:
                yield f"data: {json.dumps({'type': 'content', 'delta': char})}\n\n"
            yield "data: [DONE]\n\n"
            return
        model_ok = await asyncio.to_thread(ollama_has_model, cfg["base_url"], cfg.get("model", ""))
        if not model_ok:
            hint = (
                f"⚠️ **本地 Ollama 中未找到模型 `{cfg.get('model')}`。**\n\n"
                f"请在终端执行：`ollama pull {cfg.get('model')}`，或在 ⚙️ 设置中切换为已安装的模型。"
            )
            for char in hint:
                yield f"data: {json.dumps({'type': 'content', 'delta': char})}\n\n"
            yield "data: [DONE]\n\n"
            return

    agent, cfg = await get_agent_executor()

    if not agent:
        # 未配置 API Key 时的贴心引导
        yield f"data: {json.dumps({'type': 'thought', 'content': '正在检查大模型配置...'})}\n\n"
        hint = (
            "👋 **你好！我是你的 Aurora AI 研学管家。**\n\n"
            "检测到当前尚未配置大模型的 **API Key**。\n\n"
            "你可以点击右上角的 **⚙️ 设置** 按钮进行配置：\n"
            "- **推荐提供商**：DeepSeek（模型 `deepseek-chat`，性价比极高）；\n"
            "- **同时也支持**：OpenAI、Kimi (Moonshot)、阿里通义千问、或本地通过 Ollama 部署的模型；\n"
            "- 填入对应的 API Key 和 Base URL 后点击保存，我就可以为你实时查阅笔记、答辩升级和记录日记啦！"
        )
        for char in hint:
            yield f"data: {json.dumps({'type': 'content', 'delta': char})}\n\n"
        yield "data: [DONE]\n\n"
        return

    config = {"configurable": {"thread_id": thread_id}}
    # 防御：上轮对话若被中断，检查点里可能留有悬挂的 tool_calls，
    # 不修复的话本线程之后每次请求都会报 INVALID_CHAT_HISTORY
    repaired = await _repair_dangling_tool_calls(agent, config)
    if repaired:
        yield f"data: {json.dumps({'type': 'thought', 'content': f'检测到上次有 {repaired} 次工具调用被中断，已自动修复对话历史'})}\n\n"
    # 附带当前正在研读的书籍上下文
    user_content = f"【当前所在书籍: {book}】\n{message}"
    inputs = {"messages": [("user", user_content)]}

    try:
        async for event in agent.astream_events(inputs, config=config, version="v2"):
            kind = event.get("event")

            # 1. 捕获模型流式输出片段
            if kind == "on_chat_model_stream":
                chunk = event.get("data", {}).get("chunk")
                if not chunk:
                    continue

                # 工具调用分块
                if hasattr(chunk, "tool_call_chunks") and chunk.tool_call_chunks:
                    for tc in chunk.tool_call_chunks:
                        name = tc.get("name")
                        args = tc.get("args")
                        yield f"data: {json.dumps({'type': 'tool_call', 'name': name or '', 'args': args or ''})}\n\n"
                elif hasattr(chunk, "content") and chunk.content:
                    # 纯文本增量
                    yield f"data: {json.dumps({'type': 'content', 'delta': chunk.content})}\n\n"

            # 2. 捕获工具调用开始
            elif kind == "on_tool_start":
                tool_name = event.get("name", "tool")
                tool_input = event.get("data", {}).get("input", {})
                yield f"data: {json.dumps({'type': 'tool_start', 'name': tool_name, 'input': tool_input})}\n\n"

            # 3. 捕获工具调用完成
            elif kind == "on_tool_end":
                tool_name = event.get("name", "tool")
                tool_output = event.get("data", {}).get("output", "")
                output_str = str(tool_output)
                if len(output_str) > 800:
                    output_str = output_str[:800] + "..."
                yield f"data: {json.dumps({'type': 'tool_end', 'name': tool_name, 'output': output_str})}\n\n"

    except Exception as e:
        logger.exception("Agent 对话执行异常")
        yield f"data: {json.dumps({'type': 'error', 'message': f'执行异常: {str(e)}'})}\n\n"

    yield "data: [DONE]\n\n"
