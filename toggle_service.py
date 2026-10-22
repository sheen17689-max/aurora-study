# -*- coding: utf-8 -*-
"""深度学习研学管家 —— 桌面快捷方式启动脚本。

顺序：先启动后端，等 /api/data 通了，再打开网页。
已在运行时只打开网页，不重复拉起、也不关闭服务。
"""
import os
import sys
import time
import subprocess
import urllib.request
from pathlib import Path
import ctypes
import webbrowser

ROOT = Path(__file__).resolve().parent
APP_SCRIPT = ROOT / "app.py"
URL = "http://127.0.0.1:8899"
LAN_URL = "http://192.168.1.23:8899"


def is_running():
    try:
        req = urllib.request.Request(f"{URL}/api/data", headers={"User-Agent": "ToggleClient"})
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        with opener.open(req, timeout=1.0) as resp:
            return resp.getcode() == 200
    except Exception:
        return False


def show_msg(title, text, is_info=True):
    icon = 64 if is_info else 48
    ctypes.windll.user32.MessageBoxW(0, text, title, icon)


def open_page(url=URL):
    if os.name == "nt":
        candidates = [
            Path(os.environ.get("PROGRAMFILES(X86)", r"C:\Program Files (x86)"))
            / "Microsoft/Edge/Application/msedge.exe",
            Path(os.environ.get("PROGRAMFILES", r"C:\Program Files"))
            / "Microsoft/Edge/Application/msedge.exe",
        ]
        for edge in candidates:
            if edge.exists():
                subprocess.Popen([str(edge), url])
                return
    webbrowser.open(url)


def wait_until_running(timeout=8.0):
    deadline = time.time() + timeout
    while time.time() < deadline:
        if is_running():
            return True
        time.sleep(0.2)
    return False


def start_backend():
    python_exe = sys.executable
    pythonw = Path(python_exe).parent / "pythonw.exe"
    runner = str(pythonw) if pythonw.exists() else python_exe

    env = os.environ.copy()
    env["DL_NO_BROWSER"] = "1"

    subprocess.Popen(
        [runner, "-X", "utf8", str(APP_SCRIPT)],
        cwd=str(ROOT),
        env=env,
        creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
    )


def launch():
    if not is_running():
        start_backend()
        ready = wait_until_running()
        open_page()
        if ready:
            show_msg(
                "深度学习研学管家",
                f"后端已启动，正在打开网页。\n\n- 本机：{URL}\n- 局域网：{LAN_URL}",
                is_info=True,
            )
        else:
            show_msg(
                "深度学习研学管家",
                "后端还在启动，网页已打开。若打不开，稍等几秒后刷新。",
                is_info=False,
            )
        return

    open_page()


if __name__ == "__main__":
    launch()
