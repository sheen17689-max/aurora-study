# -*- coding: utf-8 -*-
"""深度学习学习管家 —— 与 app.py 相同的启动入口（中文文件名）。"""
import runpy
from pathlib import Path

runpy.run_path(str(Path(__file__).with_name("app.py")), run_name="__main__")
