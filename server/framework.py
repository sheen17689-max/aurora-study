# -*- coding: utf-8 -*-
"""解析 / 回写 00-知识框架.md，以及同步笔记里的掌握度。"""
import re
from datetime import datetime

from .config import LEVELS, LEVEL_NAME, ROOT, get_book_root
from .files import read_text, write_text

RE_ITEM = re.compile(r"^-\s+(.+?)\s*([⚪🟡🔵🟢])\s*(?:（\[\[(.+?)\]\]）)?\s*(.*)$")
RE_CHILD = re.compile(r"^\s+-\s+(.+?)\s*([⚪🟡🔵🟢])\s*(?:（\[\[(.+?)\]\]）)?\s*(.*)$")
RE_GROUP = re.compile(r"^-\s+(.+?)(?:\s*—\s*(.+))?$")


def _mk_item(m, section_name: str, root=None) -> dict:
    """由正则匹配构造知识点条目（顶层或缩进子项通用）"""
    base_dir = root or ROOT
    raw_title = m.group(1).strip()
    link = m.group(3) or ""
    note_file = base_dir / "知识点" / f"{link or raw_title}.md"
    return {
        "name": raw_title,
        "level": m.group(2),
        "link": link or raw_title,
        "hasNote": note_file.exists(),
        "note": (m.group(4) or "").strip(),
        "section": section_name,
        "children": [],
    }


def parse_framework(book: str = "dl"):
    root = get_book_root(book)
    path = root / "00-知识框架.md"
    text = read_text(path)
    sections, cur = [], None
    updated = ""
    m = re.search(r"最近更新[：:]\s*(\d{4}-\d{2}-\d{2})", text)
    if m:
        updated = m.group(1)

    for line in text.splitlines():
        h = re.match(r"^##\s+(.+)$", line)
        if h:
            raw_name = h.group(1).strip()
            is_cur = "⬅" in raw_name
            name = re.sub(r"\s*⬅.*$", "", raw_name).strip()
            cur = {"name": name, "current": is_cur, "note": "", "items": []}
            sections.append(cur)
            continue

        q = re.match(r"^>\s*(.+)$", line)
        if q and cur is not None and not cur["items"]:
            cur["note"] = q.group(1).strip()
            continue

        if cur is None:
            continue

        # 缩进的子项（如「  - 组合神经网络 …」）归入上一条目的 children
        mc = RE_CHILD.match(line)
        if mc and cur["items"]:
            cur["items"][-1]["children"].append(_mk_item(mc, cur["name"], root=root))
            continue

        # 普通知识点条目（行首 "- " 且带掌握度标记）
        mi = RE_ITEM.match(line)
        if mi:
            cur["items"].append(_mk_item(mi, cur["name"], root=root))
            continue

        # 分组节点（行首 "- " 但无掌握度标记，下辖缩进子项，不参与掌握度统计）
        mg = RE_GROUP.match(line)
        if mg:
            cur["items"].append({
                "name": mg.group(1).strip(),
                "level": "",
                "link": "",
                "hasNote": False,
                "note": (mg.group(2) or "").strip(),
                "section": cur["name"],
                "children": [],
                "isGroup": True,
            })

    counts = {lv: 0 for lv in LEVELS}
    for s in sections:
        c = {lv: 0 for lv in LEVELS}
        total_items = 0
        for it in s["items"]:
            for n in [it] + it.get("children", []):
                lv = n["level"]
                if lv in c:
                    counts[lv] += 1
                    c[lv] += 1
                    total_items += 1
        s["counts"] = c
        s["total"] = total_items  # 仅统计带掌握度的知识点（分组节点不计）

    total = sum(counts.values())
    return {
        "sections": sections,
        "counts": counts,
        "updated": updated or datetime.now().strftime("%Y-%m-%d"),
        "total": total,
    }


def update_framework_level(item_name: str, new_level: str, book: str = "dl") -> bool:
    if new_level not in LEVELS:
        return False
    root = get_book_root(book)
    path = root / "00-知识框架.md"
    text = read_text(path)
    if not text:
        return False

    today_str = datetime.now().strftime("%Y-%m-%d")
    lines = text.splitlines()
    changed = False

    new_lines = []
    for line in lines:
        if line.strip().startswith("- ") and item_name in line:
            for lv in LEVELS:
                if lv in line:
                    line = line.replace(lv, new_level, 1)
                    changed = True
                    break
        new_lines.append(line)

    if not changed:
        return False

    updated_text = "\n".join(new_lines)
    updated_text = re.sub(
        r"最近更新[：:]\s*\d{4}-\d{2}-\d{2}",
        f"最近更新：{today_str}",
        updated_text
    )

    counts = {lv: 0 for lv in LEVELS}
    for l in updated_text.splitlines():
        if l.strip().startswith("- "):
            for lv in LEVELS:
                if lv in l:
                    counts[lv] += 1
                    break

    total = sum(counts.values())
    stat_line = f"**统计**：🔵 {counts['🔵']} ｜ 🟢 {counts['🟢']} ｜ 🟡 {counts['🟡']} ｜ ⚪ {counts['⚪']} ｜ 共 {total} 个节点"
    updated_text = re.sub(r"\*\*统计\*\*：.*$", stat_line, updated_text, flags=re.MULTILINE)

    write_text(path, updated_text + ("\n" if not updated_text.endswith("\n") else ""))

    note_path = root / "知识点" / f"{item_name}.md"
    if note_path.exists():
        ntxt = read_text(note_path)
        if ntxt:
            ntxt = re.sub(
                r"> 掌握度[：:]\s*[⚪🟡🔵🟢]\s*([^\n|]*)",
                f"> 掌握度：{new_level} {LEVEL_NAME[new_level]}",
                ntxt
            )
            write_text(note_path, ntxt)

    return True
