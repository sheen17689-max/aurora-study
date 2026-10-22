# -*- coding: utf-8 -*-
"""Aurora 研学管家专属 Agent 工具集。

将底层知识库、掌握度回写、日记追加与词典查询封装为标准 LangChain Tool。
"""
import re
from typing import Optional
from langchain_core.tools import tool

from .config import LEVELS, LEVEL_NAME, get_book_root
from .content import append_log, parse_glossary
from .files import read_text
from .framework import parse_framework, update_framework_level


@tool
def read_knowledge_note(note_name: str, book: str = "dl") -> str:
    """读取指定概念笔记的详细 Markdown 内容（包含原理、推导、实战代码与自测题）。

    :param note_name: 概念笔记名称，例如 '前向传播', '反向传播', 'ReAct 范式', 'MCP 协议'
    :param book: 所属书籍，'dl' 为深度学习，'agent' 为 Agent 学习
    """
    clean_name = re.sub(r"[^\w\u4e00-\u9fff（）()\-· ]", "", note_name.strip())
    root = get_book_root(book)
    note_path = root / "知识点" / f"{clean_name}.md"
    if not note_path.exists():
        # 模糊查找
        candidates = list((root / "知识点").glob(f"*{clean_name}*.md"))
        if candidates:
            return f"未直接找到《{clean_name}》，但找到了相似笔记《{candidates[0].stem}》：\n\n" + read_text(candidates[0])
        return f"未找到名为《{clean_name}》的笔记，请检查名称是否正确。"
    return read_text(note_path)


@tool
def update_node_level(item_name: str, new_level: str, book: str = "dl") -> str:
    """当用户通过你的答辩考核或主动要求升级掌握度时调用此工具。自动回写知识框架与笔记。

    :param item_name: 知识点名称，例如 '前向传播', 'ReAct 范式'
    :param new_level: 必须是以下 4 个符号之一：'⚪' (未学), '🟡' (接触过), '🔵' (理解), '🟢' (掌握)
    :param book: 所属书籍，'dl' 或 'agent'
    """
    clean_name = item_name.strip()
    if new_level not in LEVELS:
        return f"无效的掌握度等级 '{new_level}'。必须为 ⚪ (未学), 🟡 (接触过), 🔵 (理解), 🟢 (掌握) 之一。"
    ok = update_framework_level(clean_name, new_level, book)
    if ok:
        return f"✅ 成功将《{clean_name}》在《{book}》中的掌握度更新为 {new_level}（{LEVEL_NAME[new_level]}），已持久化同步回写！"
    return f"❌ 未能在《{book}》的知识框架中找到知识点 '{clean_name}'，更新失败。"


@tool
def record_study_diary(content: str, log_type: str = "learned", book: str = "dl") -> str:
    """向当天的学习日记追加记录（如今日所学、疑问卡点、明日计划）。

    :param content: 日记内容，例如 '搞懂了 ReAct 范式的状态转移方程式'
    :param log_type: 日志分类，必须为 'learned'(今日所学), 'questions'(疑问卡点), 'plan'(明日计划) 之一
    :param book: 所属书籍，'dl' 或 'agent'
    """
    clean_type = log_type.lower().strip()
    if clean_type not in ["learned", "questions", "plan"]:
        clean_type = "learned"
    append_log(content.strip(), clean_type, book)
    type_name = {"learned": "今日所学", "questions": "疑问/卡点", "plan": "明日计划"}.get(clean_type, "今日所学")
    return f"📝 已成功将内容归档至今日学习日志的【{type_name}】分区！"


@tool
def query_glossary(keyword: str = "", book: str = "dl") -> str:
    """查询速查词典中的概念、术语与 API 对比解析。

    :param keyword: 检索关键词，如 'maximum', 'Workflow', 'ReAct'。为空时返回词典概览。
    :param book: 所属书籍，'dl' 或 'agent'
    """
    data = parse_glossary(book)
    raw = data.get("raw", "")
    if not keyword:
        return f"词典总览（共 {data.get('total', 0)} 条）：\n" + raw[:1200] + "\n...(略)"
    # 查找关键词匹配块
    matches = []
    lines = raw.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("### ") and keyword.lower() in line.lower():
            chunk = [line]
            i += 1
            while i < len(lines) and not lines[i].startswith("### ") and not lines[i].startswith("## "):
                chunk.append(lines[i])
                i += 1
            matches.append("\n".join(chunk))
            continue
        i += 1
    if matches:
        return f"找到 {len(matches)} 条与 '{keyword}' 相关的词典释义：\n\n" + "\n\n---\n\n".join(matches)
    return f"词典中未找到包含 '{keyword}' 的术语条目。"


@tool
def list_knowledge_framework(book: str = "dl") -> str:
    """列出指定书籍当前的章节结构、全部知识节点及其当前掌握度状态。

    :param book: 所属书籍，'dl' 为深度学习，'agent' 为 Agent 学习
    """
    fw = parse_framework(book)
    output = [f"《{book}》全书大纲（共 {fw.get('total', 0)} 个节点，统计：🔵 {fw['counts']['🔵']} ｜ 🟢 {fw['counts']['🟢']} ｜ 🟡 {fw['counts']['🟡']} ｜ ⚪ {fw['counts']['⚪']}）："]
    for s in fw.get("sections", []):
        output.append(f"\n【{s['name']}】({s.get('total', 0)} 节点)")
        for it in s.get("items", []):
            lv = it.get("level") or "📁"
            output.append(f"  - [{lv}] {it['name']}")
            for ch in it.get("children", []):
                clv = ch.get("level") or "  "
                output.append(f"      [{clv}] {ch['name']}")
    return "\n".join(output)


AGENT_TOOLS = [
    read_knowledge_note,
    update_node_level,
    record_study_diary,
    query_glossary,
    list_knowledge_framework,
]
