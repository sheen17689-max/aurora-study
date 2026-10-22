# -*- coding: utf-8 -*-
"""Aurora 研学管家 FastAPI 接口与静态资源托管服务。"""
import os
import random
import re
import threading
import time
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, Response, StreamingResponse
from pydantic import BaseModel, Field

from .assistant import stream_agent_chat
from .config import DIST_DIR, LEVELS, ROOT, get_book_root, load_agent_config, save_agent_config
from .content import (
    append_glossary_term,
    append_log,
    collect_data,
    get_quiz_items,
    parse_glossary,
)
from .files import read_text, write_text
from .framework import update_framework_level

app = FastAPI(
    title="Aurora 研学管家 API",
    description="深度学习与 Agent 智能体工作台后端接口，支持知识树、笔记、自测与速查词典管理",
    version="1.0.0",
)

# 允许跨域（方便前端独立 Vite 开发时直接跨域请求）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_no_cache_headers(request, call_next):
    response = await call_next(request)
    path = request.url.path
    if path.startswith("/api/") or path in ["/", "/index.html"]:
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    return response

# dashboard/dist 未构建时的极简提示页
PAGE = (
    "<!DOCTYPE html><meta charset='utf-8'><title>研学管家</title>"
    "<p>看板尚未构建，请先执行 <code>cd dashboard && npm run build</code>，"
    "或使用 Vite 开发模式访问 <code>http://127.0.0.1:5173</code></p>"
)


class LogRecordRequest(BaseModel):
    text: str = Field(..., description="学习日记内容")
    type: str = Field("learned", description="日志类型：learned / question / plan 等")
    book: Optional[str] = Field("dl", description="书籍标识：dl / agent")


class GlossaryRequest(BaseModel):
    category: Optional[str] = Field("常见 API 与概念", description="分类")
    term: Optional[str] = Field("", description="术语名称")
    diff: Optional[str] = Field("", description="核心区别/解释")
    code: Optional[str] = Field("", description="代码示例")
    raw_full: Optional[str] = Field("", description="全量保存速查词典 Markdown 内容")
    book: Optional[str] = Field("dl", description="书籍标识：dl / agent")


class LevelUpdateRequest(BaseModel):
    name: str = Field(..., description="知识点名称")
    level: str = Field(..., description="掌握度等级：⚪ 🟡 🔵 🟢")
    book: Optional[str] = Field("dl", description="书籍标识：dl / agent")


class NoteSaveRequest(BaseModel):
    name: str = Field(..., description="知识点名称")
    content: str = Field("", description="Markdown 笔记内容")
    book: Optional[str] = Field("dl", description="书籍标识：dl / agent")


class AgentConfigRequest(BaseModel):
    provider: Optional[str] = Field("deepseek", description="模型提供商")
    model: Optional[str] = Field("deepseek-chat", description="模型名称")
    base_url: Optional[str] = Field("https://api.deepseek.com/v1", description="API 基础地址")
    api_key: Optional[str] = Field("", description="API Key")
    temperature: Optional[float] = Field(0.3, description="采样温度")


class AgentChatRequest(BaseModel):
    message: str = Field(..., description="用户对话消息")
    thread_id: Optional[str] = Field("default_thread", description="会话 ID")
    book: Optional[str] = Field("dl", description="当前所在书籍标识：dl / agent")


@app.get("/api/agent/config", summary="获取 Agent 大模型配置")
def get_agent_config():
    cfg = load_agent_config()
    raw_key = cfg.get("api_key", "")
    masked_key = ""
    if raw_key:
        masked_key = (raw_key[:3] + "..." + raw_key[-4:]) if len(raw_key) > 8 else "***"
    return {
        **cfg,
        "api_key_masked": masked_key,
        "has_key": bool(raw_key),
    }


@app.post("/api/agent/config", summary="保存 Agent 大模型配置")
def post_agent_config(payload: AgentConfigRequest):
    data = payload.dict(exclude_unset=True)
    cfg = save_agent_config(data)
    raw_key = cfg.get("api_key", "")
    masked_key = (raw_key[:3] + "..." + raw_key[-4:]) if len(raw_key) > 8 else "***"
    return {
        "ok": True,
        "config": {
            **cfg,
            "api_key_masked": masked_key,
            "has_key": bool(raw_key),
        },
    }


@app.post("/api/agent/chat", summary="与 Agent 助手对话 (SSE流式)")
async def post_agent_chat(payload: AgentChatRequest):
    text = payload.message.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    return StreamingResponse(
        stream_agent_chat(text, payload.thread_id or "default_thread", payload.book or "dl"),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@app.get("/api/data", summary="获取全量看板数据")
def get_data(book: Optional[str] = Query("dl")):
    return collect_data(book or "dl")


@app.get("/api/quiz", summary="随机获取自测题")
def get_quiz(book: Optional[str] = Query("dl")):
    quizzes = get_quiz_items(book or "dl")
    quiz = random.choice(quizzes) if quizzes else None
    return {"quiz": quiz}


@app.get("/api/glossary", summary="获取速查词典")
def get_glossary(book: Optional[str] = Query("dl")):
    return parse_glossary(book or "dl")


@app.get("/api/note", summary="读取单篇知识点笔记")
def get_note(name: str = Query("", description="知识点名称"), book: Optional[str] = Query("dl")):
    clean_name = re.sub(r"[^\w\u4e00-\u9fff（）()\-· ]", "", name.strip())
    root = get_book_root(book or "dl")
    txt = read_text(root / "知识点" / f"{clean_name}.md") if clean_name else ""
    return {"name": clean_name, "content": txt}


@app.post("/api/log", summary="追加学习日记")
def post_log(payload: LogRecordRequest):
    text = payload.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    append_log(text, payload.type, payload.book or "dl")
    return {"ok": True}


@app.post("/api/glossary", summary="追加或更新词典条目")
def post_glossary(payload: GlossaryRequest):
    root = get_book_root(payload.book or "dl")
    if payload.raw_full:
        write_text(root / "00-速查词典.md", payload.raw_full)
        return {"ok": True}
    term = (payload.term or "").strip()
    diff = (payload.diff or "").strip()
    category = (payload.category or "").strip() or "常见 API 与概念"
    code = (payload.code or "").strip()
    if term and diff:
        append_glossary_term(category, term, diff, code, payload.book or "dl")
        return {"ok": True}
    raise HTTPException(status_code=400, detail="Invalid glossary payload")


@app.post("/api/level", summary="更新知识点掌握度")
def post_level(payload: LevelUpdateRequest):
    name = payload.name.strip()
    level = payload.level.strip()
    if name and level in LEVELS:
        ok = update_framework_level(name, level, payload.book or "dl")
        return {"ok": ok}
    raise HTTPException(status_code=400, detail="Invalid name or level")


@app.post("/api/note", summary="保存知识点笔记")
def post_note(payload: NoteSaveRequest):
    name = payload.name.strip()
    if not name:
        raise HTTPException(status_code=400, detail="Name cannot be empty")
    clean_name = re.sub(r"[^\w\u4e00-\u9fff（）()\-· ]", "", name)
    root = get_book_root(payload.book or "dl")
    p = root / "知识点" / f"{clean_name}.md"
    p.parent.mkdir(parents=True, exist_ok=True)
    write_text(p, payload.content)
    return {"ok": True}


@app.post("/api/shutdown", summary="退出管家后台服务")
def post_shutdown():
    pid_file = ROOT / ".vite_pid"
    if pid_file.exists():
        try:
            vpid = pid_file.read_text(encoding="utf-8").strip()
            if vpid:
                import subprocess
                subprocess.run(
                    ["taskkill", "/F", "/T", "/PID", vpid],
                    capture_output=True,
                    creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
                )
            pid_file.unlink(missing_ok=True)
        except Exception:
            pass

    def do_shutdown():
        time.sleep(0.5)
        srv = getattr(app.state, "server", None)
        if srv:
            srv.should_exit = True
        else:
            os._exit(0)

    threading.Thread(target=do_shutdown, daemon=True).start()
    return {"ok": True}


# 静态文件托管与 SPA 页面路由支持
@app.get("/{full_path:path}", include_in_schema=False)
def serve_spa(full_path: str):
    # 针对 favicon 特殊处理
    if full_path == "favicon.ico":
        fav = DIST_DIR / "favicon.svg"
        if fav.exists():
            return FileResponse(fav)
        return Response(status_code=204)

    if DIST_DIR.exists():
        target = DIST_DIR / full_path
        if full_path and target.exists() and target.is_file():
            return FileResponse(target)
        index_file = DIST_DIR / "index.html"
        if index_file.exists():
            return FileResponse(index_file)

    if not full_path or full_path == "index.html":
        return HTMLResponse(PAGE)

    raise HTTPException(status_code=404, detail="Not Found")
