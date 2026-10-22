# -*- coding: utf-8 -*-
"""日记、简报、自测、词典、学习路线，以及看板聚合数据。"""
import random
import re
from datetime import datetime, timedelta

from .config import CN_WEEK, DIARY_TEMPLATE, LEVELS, ROOT, get_book_root
from .files import read_text, write_text
from .framework import parse_framework


def parse_route(book: str = "dl"):
    root = get_book_root(book)
    text = read_text(root / "学习路线.md")
    current = ""
    m = re.search(r"⬅\s*当前位置[：:]\s*(.+)", text)
    if m:
        current = m.group(1).strip()
    nxt = []
    sec = re.search(r"##\s*下一步建议[^\n]*\n(.*?)(?:\n##|\Z)", text, re.S)
    if sec:
        for line in sec.group(1).splitlines():
            b = re.match(r"^-\s+(.+)$", line.strip())
            if b:
                nxt.append(b.group(1).strip())
    return {"current": current, "next": nxt[:3]}


def parse_diary(p):
    text = read_text(p)

    def bullets(section):
        m = re.search(r"##\s*" + section + r"[^\n]*\n(.*?)(?:\n##|\Z)", text, re.S)
        if not m:
            return []
        out = []
        for line in m.group(1).splitlines():
            b = re.match(r"^-\s*(.*)$", line.strip())
            if b:
                t = b.group(1).strip()
                if not t or "尚未记录" in t or t.startswith("（由"):
                    continue
                out.append(t)
        return out

    return {
        "date": p.stem,
        "learned": bullets("今日所学"),
        "questions": bullets("疑问"),
        "plan": bullets("明日计划"),
    }


def parse_briefing(book: str = "dl"):
    root = get_book_root(book)
    bdir = root / "简报"
    if not bdir.is_dir():
        return None
    files = sorted(bdir.glob("2*.md"), reverse=True)
    if not files:
        return None
    p = files[0]
    out = []
    sections = []
    cur = None
    for line in read_text(p).splitlines():
        t = line.strip()
        if not t or t.startswith("# "):
            continue
        m = re.match(r"^##\s*(.+)$", t)
        if m:
            cur = {"title": m.group(1).strip(), "lines": []}
            sections.append(cur)
            continue
        t = re.sub(r"\*\*(.+?)\*\*", r"\1", t)
        if not t:
            continue
        out.append(t)
        if cur is None:
            cur = {"title": "", "lines": []}
            sections.append(cur)
        cur["lines"].append(t)
    return {"date": p.stem, "lines": out, "sections": sections}


def get_quiz_items(book: str = "dl"):
    root = get_book_root(book)
    kdir = root / "知识点"
    if not kdir.is_dir():
        return []
    quizzes = []
    for p in kdir.glob("*.md"):
        txt = read_text(p)
        if not txt:
            continue
        m = re.search(r"##\s*(?:思考与)?自测[^\n]*\n(.*?)(?:\n##|\Z)", txt, re.S)
        if m:
            questions = []
            for line in m.group(1).splitlines():
                line = line.strip()
                if line.startswith("-") and len(line) > 2:
                    q = line.lstrip("- ").strip()
                    if q:
                        questions.append(q)
            if questions:
                lv = "🟡"
                for l in LEVELS:
                    if f"掌握度：{l}" in txt or f"掌握度： {l}" in txt:
                        lv = l
                        break
                quizzes.append({
                    "name": p.stem,
                    "level": lv,
                    "questions": questions,
                })
    return quizzes


def parse_glossary(book: str = "dl"):
    root = get_book_root(book)
    path = root / "00-速查词典.md"
    text = read_text(path)
    if not text:
        return {"updated": "", "categories": [], "raw": "", "total": 0}

    categories = []
    current_cat = None
    updated = ""
    total = 0
    m = re.search(r"最近更新[：:]\s*(\d{4}-\d{2}-\d{2})", text)
    if m:
        updated = m.group(1)

    lines = text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith("## "):
            cat_name = line.replace("## ", "").strip()
            current_cat = {"name": cat_name, "items": []}
            categories.append(current_cat)
            i += 1
            continue

        if line.startswith("### "):
            term_name = line.replace("### ", "").strip()
            total += 1
            item = {"term": term_name, "category": "", "diff": "", "code": "", "raw": ""}
            if current_cat is not None:
                current_cat["items"].append(item)
            i += 1

            item_lines = []
            while i < len(lines) and not lines[i].strip().startswith("### ") and not lines[i].strip().startswith("## "):
                item_lines.append(lines[i])
                i += 1
            item["raw"] = "\n".join(item_lines).strip()
            continue
        i += 1

    return {"updated": updated, "categories": categories, "raw": text, "total": total}


def append_glossary_term(category: str, term: str, diff: str, code: str = "", book: str = "dl"):
    root = get_book_root(book)
    path = root / "00-速查词典.md"
    text = read_text(path)
    if not text:
        text = "# 📖 专有名词与 API 速查词典\n\n> 随手记录易混淆 API、关键数学概念与缩写术语\n\n"

    today_str = datetime.now().strftime("%Y-%m-%d")
    text = re.sub(r"最近更新[：:]\s*\d{4}-\d{2}-\d{2}", f"最近更新：{today_str}", text)

    entry = f"\n### `{term}`\n- **类别**：`{category}`\n- **核心区别/解析**：\n  {diff}\n"
    if code:
        entry += f"- **代码示例**：\n```python\n{code}\n```\n"

    cat_header = f"## {category}"
    if cat_header in text:
        text = text.replace(cat_header, f"{cat_header}\n{entry}")
    else:
        text += f"\n## {category}\n{entry}"

    write_text(path, text)
    return True


def append_log(text: str, log_type: str = "learned", book: str = "dl"):
    now = datetime.now()
    root = get_book_root(book)
    diary_dir = root / "日记"
    diary_dir.mkdir(parents=True, exist_ok=True)
    p = diary_dir / (now.date().isoformat() + ".md")
    if not p.exists():
        write_text(p, DIARY_TEMPLATE.format(date=now.date().isoformat(), wd=CN_WEEK[now.weekday()]))

    lines = read_text(p).splitlines()
    entry = f"- {now.strftime('%H:%M')} {text}"

    section_map = {
        "learned": "## 今日所学",
        "questions": "## 疑问 / 卡点",
        "plan": "## 明日计划",
    }
    sec_title = section_map.get(log_type, "## 今日所学")

    idx = next((i for i, l in enumerate(lines) if l.strip().startswith(sec_title)), None)
    if idx is None:
        lines += ["", sec_title, entry]
    else:
        j = idx + 1
        while j < len(lines) and not lines[j].startswith("## "):
            j += 1
        block = lines[idx + 1 : j]
        ph = next((k for k, l in enumerate(block) if "尚未记录" in l or "由明早" in l), None)
        if ph is not None:
            lines[idx + 1 + ph] = entry
        else:
            insert_at = idx + 1
            for k, l in enumerate(block):
                if l.strip().startswith("-") and l.strip() != "-":
                    insert_at = idx + 2 + k
            lines.insert(insert_at, entry)

    write_text(p, "\n".join(lines) + "\n")


def collect_data(book: str = "dl"):
    root = get_book_root(book)
    today = datetime.now().date()
    diaries = []
    diary_dir = root / "日记"
    if diary_dir.is_dir():
        for p in sorted(diary_dir.glob("2*.md"), reverse=True)[:14]:
            diaries.append(parse_diary(p))
    by_date = {d["date"]: d for d in diaries}
    ystr = (today - timedelta(days=1)).isoformat()

    streak = 0
    d = today
    if not by_date.get(d.isoformat(), {}).get("learned"):
        d -= timedelta(days=1)
    while by_date.get(d.isoformat(), {}).get("learned"):
        streak += 1
        d -= timedelta(days=1)

    all_quizzes = get_quiz_items(book)
    daily_quiz = random.choice(all_quizzes) if all_quizzes else None

    return {
        "book": book,
        "today": today.isoformat(),
        "weekday": CN_WEEK[today.weekday()],
        "framework": parse_framework(book),
        "route": parse_route(book),
        "yesterday": {"date": ystr, "learned": by_date.get(ystr, {}).get("learned", [])},
        "todayLog": by_date.get(today.isoformat(), {"date": today.isoformat(), "learned": [], "questions": [], "plan": []}),
        "diaries": [x for x in diaries if x["learned"] or x["questions"] or x["plan"]],
        "streak": streak,
        "briefing": parse_briefing(book),
        "quiz": daily_quiz,
        "glossaryCount": parse_glossary(book).get("total", 0),
    }
