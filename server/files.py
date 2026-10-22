# -*- coding: utf-8 -*-
"""UTF-8 读写封装。"""
from pathlib import Path


def read_text(p: Path) -> str:
    if not p.is_file():
        return ""
    try:
        return p.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        try:
            return p.read_text(encoding="utf-8", errors="replace")
        except Exception:
            return ""
    except Exception:
        return ""


def write_text(p: Path, text: str):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
