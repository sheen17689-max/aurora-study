# -*- coding: utf-8 -*-
"""创建桌面快捷方式脚本。"""
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
ICO_PATH = ROOT / "sheen.ico"
LAUNCH_SCRIPT = ROOT / "launch_app.pyw"

# 查找 pythonw 路径
candidates = [
    Path(r"D:\software\anaconda\pythonw.exe"),
    Path(os.environ.get("APPDATA", "")) / r"uv\python\cpython-3.11-windows-x86_64-none\pythonw.exe",
    Path(sys.executable).with_name("pythonw.exe"),
]
pythonw = None
for c in candidates:
    if c.exists():
        pythonw = str(c)
        break
if not pythonw:
    pythonw = "pythonw.exe"

desktop = Path.home() / "Desktop"

ps_script = f"""
$WshShell = New-Object -ComObject WScript.Shell

$shortcutNames = @("Aurora研学管家.lnk", "sheen.lnk")

foreach ($name in $shortcutNames) {{
    $shortcutPath = Join-Path "{str(desktop)}" $name
    $shortcut = $WshShell.CreateShortcut($shortcutPath)
    $shortcut.TargetPath = "{pythonw}"
    $shortcut.Arguments = '"{str(LAUNCH_SCRIPT)}"'
    $shortcut.WorkingDirectory = "{str(ROOT)}"
    $shortcut.IconLocation = "{str(ICO_PATH)},0"
    $shortcut.Description = "Aurora 深度学习研学管家 (前后端联动)"
    $shortcut.Save()
    Write-Host "Created shortcut: $shortcutPath"
}}
"""

res = subprocess.run(["powershell", "-NoProfile", "-Command", ps_script], capture_output=True, text=True)
print(res.stdout)
if res.stderr:
    print(res.stderr, file=sys.stderr)
