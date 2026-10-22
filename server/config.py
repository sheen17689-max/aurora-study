# -*- coding: utf-8 -*-
"""路径、常量和静态资源映射。改端口 / 知识库根目录时看这里。"""
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PORT = 8899

AGENT_CONFIG_FILE = ROOT / "agent_config.json"

DEFAULT_AGENT_CONFIG = {
    "provider": "deepseek",
    "model": "deepseek-chat",
    "base_url": "https://api.deepseek.com/v1",
    "api_key": "",
    "temperature": 0.3,
}


def load_agent_config() -> dict:
    """读取 Agent 大模型配置，优先支持环境变量与本地配置文件"""
    cfg = DEFAULT_AGENT_CONFIG.copy()
    if os.environ.get("OPENAI_API_KEY"):
        cfg["api_key"] = os.environ.get("OPENAI_API_KEY", "")
    if os.environ.get("OPENAI_BASE_URL"):
        cfg["base_url"] = os.environ.get("OPENAI_BASE_URL", "")
    if os.environ.get("OPENAI_MODEL"):
        cfg["model"] = os.environ.get("OPENAI_MODEL", "")

    if AGENT_CONFIG_FILE.exists():
        try:
            saved = json.loads(AGENT_CONFIG_FILE.read_text(encoding="utf-8"))
            if isinstance(saved, dict):
                cfg.update(saved)
        except Exception:
            pass
    return cfg


def save_agent_config(new_cfg: dict) -> dict:
    """保存 Agent 大模型配置到本地 agent_config.json"""
    cfg = load_agent_config()
    for k in ["provider", "model", "base_url", "api_key", "temperature", "mcp_servers"]:
        if k in new_cfg and new_cfg[k] is not None:
            cfg[k] = new_cfg[k]
    AGENT_CONFIG_FILE.write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")
    return cfg

LEVELS = ["⚪", "🟡", "🔵", "🟢"]
LEVEL_NAME = {"⚪": "未学", "🟡": "接触过", "🔵": "理解", "🟢": "掌握"}
CN_WEEK = "一二三四五六日"

DIARY_TEMPLATE = "# {date}（周{wd}）学习日志\n\n## 今日所学\n\n## 疑问 / 卡点\n- \n\n## 明日计划\n- \n"

BOOKS = {
    "dl": {
        "id": "dl",
        "name": "深度学习",
        "root": ROOT,
    },
    "agent": {
        "id": "agent",
        "name": "Agent 学习",
        "root": ROOT / "agent",
    },
}


def get_book_root(book: str = "dl") -> Path:
    """根据书籍 ID 获取对应知识库的根目录"""
    if book and book in BOOKS:
        return BOOKS[book]["root"]
    if book and (ROOT / book).is_dir() and (ROOT / book / "00-知识框架.md").exists():
        return ROOT / book
    return ROOT


DIST_DIR = ROOT / "dashboard" / "dist"

MIME_MAP = {
    ".html": "text/html; charset=utf-8",
    ".js": "application/javascript; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".json": "application/json; charset=utf-8",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".svg": "image/svg+xml",
    ".ico": "image/x-icon",
    ".woff": "font/woff",
    ".woff2": "font/woff2",
    ".ttf": "font/ttf",
}
