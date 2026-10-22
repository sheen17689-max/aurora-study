# -*- coding: utf-8 -*-
"""深度学习研学管家 —— 桌面一键启动前后端脚本 (全功能开发模式)。

功能：
1. 检查并启动 Python 后端服务 (http://127.0.0.1:8899)
2. 检查并启动 Vue / Vite 前端开发服务 (http://127.0.0.1:5173)
3. 待前后端均就绪后，自动在浏览器打开前端页面 (http://127.0.0.1:5173)
4. 后台静默运行，无黑框控制台闪烁；若服务已在运行则直接唤起网页，避免重复启动
"""
import ctypes
import os
import shutil
import subprocess
import sys
import time
import traceback
import urllib.request
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DASHBOARD_DIR = ROOT / "dashboard"
VITE_BIN = DASHBOARD_DIR / "node_modules" / "vite" / "bin" / "vite.js"
PID_FILE = ROOT / ".vite_pid"

BACKEND_URL = "http://127.0.0.1:8899"
BACKEND_HEALTH = f"{BACKEND_URL}/api/data"
FRONTEND_URL = "http://127.0.0.1:5173"


def find_pythonw():
    """查找可用的 pythonw.exe 执行路径。"""
    candidates = [
        Path(sys.executable).with_name("pythonw.exe"),
        Path(r"D:\software\anaconda\pythonw.exe"),
        Path(os.environ.get("APPDATA", "")) / r"uv\python\cpython-3.11-windows-x86_64-none\pythonw.exe",
    ]
    for c in candidates:
        if c.exists():
            return str(c)
    which_pw = shutil.which("pythonw")
    if which_pw:
        return which_pw
    return sys.executable


def find_node():
    """查找 node.exe 路径。"""
    candidates = [
        Path(r"C:\Program Files\nodejs\node.exe"),
        Path(r"C:\Program Files (x86)\nodejs\node.exe"),
        Path(os.environ.get("LOCALAPPDATA", "")) / r"Programs\node\node.exe",
    ]
    for c in candidates:
        if c.exists():
            return str(c)
    which_node = shutil.which("node")
    if which_node:
        return which_node
    return "node"


def is_service_ready(url, timeout=0.8):
    """检测指定 URL 是否可正常响应。"""
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "AuroraLauncher"})
        with opener.open(req, timeout=timeout) as resp:
            return resp.status == 200
    except Exception:
        return False


def wait_until_ready(check_fn, timeout=10.0, interval=0.2):
    """循环等待服务就绪。"""
    deadline = time.time() + timeout
    while time.time() < deadline:
        if check_fn():
            return True
        time.sleep(interval)
    return False


def start_backend():
    """后台静默启动 Python 后端。"""
    if is_service_ready(BACKEND_HEALTH):
        return True

    pythonw = find_pythonw()
    env = os.environ.copy()
    env["DL_NO_BROWSER"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"

    creation_flags = 0
    if os.name == "nt":
        creation_flags = subprocess.CREATE_NO_WINDOW | subprocess.DETACHED_PROCESS

    subprocess.Popen(
        [pythonw, "-X", "utf8", str(ROOT / "app.py")],
        cwd=str(ROOT),
        env=env,
        creationflags=creation_flags,
    )
    return wait_until_ready(lambda: is_service_ready(BACKEND_HEALTH), timeout=25.0)


def get_pid_by_port(port):
    """根据端口号获取占用该端口的进程 PID。"""
    try:
        res = subprocess.run(
            ["netstat", "-ano"],
            capture_output=True,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
        )
        for line in res.stdout.splitlines():
            if f":{port}" in line and "LISTENING" in line:
                parts = line.strip().split()
                if parts:
                    return parts[-1]
    except Exception:
        pass
    return None


def start_frontend():
    """后台静默启动 Vite 前端开发服务。"""
    if is_service_ready(FRONTEND_URL):
        pid = get_pid_by_port(5173)
        if pid:
            try:
                PID_FILE.write_text(str(pid), encoding="utf-8")
            except Exception:
                pass
        return True

    if not VITE_BIN.exists():
        return False

    node_exe = find_node()
    creation_flags = 0
    if os.name == "nt":
        creation_flags = subprocess.CREATE_NO_WINDOW | subprocess.DETACHED_PROCESS

    proc = subprocess.Popen(
        [node_exe, str(VITE_BIN)],
        cwd=str(DASHBOARD_DIR),
        creationflags=creation_flags,
    )
    try:
        PID_FILE.write_text(str(proc.pid), encoding="utf-8")
    except Exception:
        pass

    return wait_until_ready(lambda: is_service_ready(FRONTEND_URL), timeout=15.0)


def open_browser(url):
    """唤起浏览器打开页面（优先 Edge，其次系统默认）。"""
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


def show_error(msg):
    """弹出 Windows 错误提示框。"""
    if os.name == "nt":
        ctypes.windll.user32.MessageBoxW(0, msg, "深度学习研学管家", 16)


def launch():
    try:
        # 1. 启动后端
        backend_ok = start_backend()

        # 2. 启动前端 Vite
        frontend_ok = start_frontend()

        # 3. 决定打开的页面
        if frontend_ok:
            open_browser(FRONTEND_URL)
        elif backend_ok:
            # 前端启动若异常，降级打开后端托管的静态看板
            open_browser(BACKEND_URL)
        else:
            show_error("管家服务启动超时，请检查后端是否报错。")

    except Exception:
        err = traceback.format_exc()
        try:
            (ROOT / "管家启动失败.log").write_text(err, encoding="utf-8")
        except Exception:
            pass
        show_error(f"启动过程发生异常：\n{err}")


if __name__ == "__main__":
    launch()
