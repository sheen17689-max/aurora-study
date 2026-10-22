# -*- coding: utf-8 -*-
"""启动本地服务：http://127.0.0.1:8899 (基于 FastAPI + Uvicorn)

先把后端拉起来并确认接口可访问，再打开网页。
"""
import os
import sys
import subprocess
import threading
import time
import urllib.request
import webbrowser
from pathlib import Path

# 兼容 pythonw.exe 无控制台运行（stdout/stderr 为 None）
if sys.stdout is None:
    sys.stdout = open(os.devnull, "w", encoding="utf-8")
if sys.stderr is None:
    sys.stderr = open(os.devnull, "w", encoding="utf-8")

try:
    import uvicorn
    from .api import app
except ImportError as e:
    raise RuntimeError(
        "缺少 FastAPI 或 Uvicorn 依赖，请在终端执行: pip install -r requirements.txt"
    ) from e

from .config import PORT


def dashboard_url():
    return f"http://127.0.0.1:{PORT}"


def backend_ready(timeout=1.2):
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    try:
        with opener.open(dashboard_url() + "/api/data", timeout=timeout) as resp:
            body = resp.read(4096)
            return resp.status == 200 and (b"framework" in body or body.startswith(b"{"))
    except Exception:
        return False


def wait_until_ready(timeout=8.0):
    deadline = time.time() + timeout
    while time.time() < deadline:
        if backend_ready(timeout=0.6):
            return True
        time.sleep(0.15)
    return False


def open_dashboard(url=None):
    url = url or dashboard_url()
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


def main():
    url = dashboard_url()
    open_browser = os.environ.get("DL_NO_BROWSER") != "1"

    # 若已在运行，直接唤起浏览器
    if backend_ready():
        if open_browser:
            open_dashboard(url)
        return

    config = uvicorn.Config(
        app,
        host="127.0.0.1",
        port=PORT,
        log_level="warning",
        access_log=False,
        use_colors=False,
    )
    server = uvicorn.Server(config)
    app.state.server = server

    server_thread = threading.Thread(target=server.run, daemon=True)
    server_thread.start()

    print("学习管家已启动 (FastAPI):")
    print(f" - 本机访问: {url}")
    print(f" - 接口文档: {url}/docs")
    print(" - 默认仅本机访问；请勿直接暴露到公网。")

    if open_browser:
        wait_until_ready()
        open_dashboard(url)

    try:
        server_thread.join()
    except KeyboardInterrupt:
        server.should_exit = True


if __name__ == "__main__":
    main()
