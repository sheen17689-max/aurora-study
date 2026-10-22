# -*- coding: utf-8 -*-
"""桌面快捷方式入口（pythonw 无窗口运行）。

快捷方式：pythonw.exe "...\深度学习\app.py"
先启动后端，确认接口可访问后再打开网页。
失败时会在本目录写下「管家启动失败.log」，避免 pythonw 静默退出。
"""
import os
import sys
import traceback
from pathlib import Path

# 兼容 pythonw.exe 无控制台运行（stdout/stderr 为 None）
if sys.stdout is None:
    sys.stdout = open(os.devnull, "w", encoding="utf-8")
if sys.stderr is None:
    sys.stderr = open(os.devnull, "w", encoding="utf-8")

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

try:
    from server.main import main
    main()
except Exception:
    log = ROOT / "管家启动失败.log"
    log.write_text(traceback.format_exc(), encoding="utf-8")
    raise
