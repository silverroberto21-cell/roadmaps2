"""Assemblage du volume : pages liminaires, cours, annexes, table des matières."""
from __future__ import annotations

import importlib

from .compose import compose_chapter, compose_course_front


def _load_chapter(module: str) -> dict | None:
    try:
        mod = importlib.import_module(module)
        importlib.reload(mod)
        return mod.CH
    except ModuleNotFoundError:
        return None


def course_parts(course: dict) -> list[dict]:
    parts = []
    for part in course["parts"]:
        chapters = []
        for name in part["chapters"]:
            ch = _load_chapter(name)
            if ch is not None:
                chapters.append(ch)
        parts.append({**part, "loaded": chapters})
    return parts


def _section(header_left: str, header_right: str, first_blank: bool = True) -> dict:
    return {"t": "section", "header_left": header_left, "header_right": header_right,
            "first_blank": first_blank}


def build_course(course: dict, number: int, offset: int, pages: dict):
    blocks: list[dict] = []
    general: list = []
    parts = course_parts(course)
    toc_sink: list = []
    chapters_blocks: list[list[dict]] = []
    num = offset
    for part in parts:
        for ch in part["loaded"]:
            num += 1
            chapters_blocks.append(
                compose_chapter(ch, num, part["label"], toc_sink,
                                base=offset, local=num - offset))

    course_toc: list = []
    num = offset
    for part in parts:
        course_toc.append(("part", f"{part['label']} — {part['title']}", part["id"]))
        for ch in part["loaded"]:
            num += 1
            course_toc.append(("chapter", f"{num}. {ch['title']}", f"ch{num}"))
            for lvl, text, bid in toc_sink:
                if bid.startswith(f"ch{num}_"):
                    course_toc.append(("section", text, bid))

    blocks.append(_section(f"Cours {number} · {course['short_header']}",
                           "Présentation du cours"))
    blocks += compose_course_front(course, number, pages, course_toc)

    num = offset
    idx = 0
    for part in parts:
        blocks.append(_section(f"Cours {number} · {course['short_header']}",
                               f"{part['label']} · {part['title']}"))
        blocks.append({"t": "fullpage", "kind": "part", "label": part["label"],
                       "title": part["title"], "description": part["description"],
                       "chapters": [f"{offset + j + 1}. {c['title']}"
                                    for j, c in enumerate(part["loaded"])],
                       "id": part["id"]})
        for ch in part["loaded"]:
            blocks += chapters_blocks[idx]
            idx += 1

    general.append((1, course["title"], f"course{number}"))
    num = offset
    for part in parts:
        general.append((1, f"{part['label']} — {part['title']}", part["id"]))
        for ch in part["loaded"]:
            num += 1
            general.append((2, f"{num}. {ch['title']}", f"ch{num}"))
    return blocks, course_toc, general


def assemble(course_modules: list[dict], pages: dict, logo: str,
             annex_blocks: list[dict]) -> tuple[list[dict], list]:
    from content.front import front_matter

    course_info = []
    for i, c in enumerate(course_modules, 1):
        course_info.append({
            "label": f"Cours {i}",
            "title": c["title"],
            "short": c["short"],
            "level": c["level"],
            "parts": [{"label": pt["label"], "title": pt["title"],
                       "chapters": pt["chapters"]} for pt in c["parts"]],
            "chapters": sum(len(pt["chapters"]) for pt in c["parts"]),
        })

    course_blocks = []
    general: list = []
    totals = [sum(len(pt["chapters"]) for pt in c["parts"]) for c in course_modules]
    for i, course in enumerate(course_modules, 1):
        cb, _, gen = build_course(course, i, sum(totals[: i - 1]), pages)
        course_blocks.append(cb)
        general += gen

    front = front_matter(course_info, pages, logo)
    entries: list = []
    idx = 0
    for b in front:
        if b["t"] == "h" and b.get("level") == 1:
            idx += 1
            if not b.get("id"):
                b["id"] = f"fm{idx}"
            entries.append((1, b["text"], b["id"]))
    entries += general
    annex_entries: list = []
    aidx = 0
    for b in annex_blocks:
        if b["t"] == "h" and b.get("level") == 1:
            aidx += 1
            if not b.get("id"):
                b["id"] = f"anx{aidx}"
            annex_entries.append((1, b["text"], b["id"]))
    entries += annex_entries

    blocks: list[dict] = []
    for b in front:
        if b["t"] == "__TOC__":
            blocks.append({"t": "toc_start"})
            for lvl, text, bid in entries:
                blocks.append({"t": "toc_entry", "level": lvl, "text": text,
                               "page": pages.get(bid, 0)})
            blocks.append({"t": "toc_end"})
        else:
            blocks.append(b)

    for cb in course_blocks:
        blocks += cb

    if annex_blocks:
        blocks.append(_section("Annexes", "Ressources et repères"))
        blocks += annex_blocks
    blocks = _cleanup(blocks)
    return blocks, entries


def _cleanup(blocks: list[dict]) -> list[dict]:
    """Normalise les sauts de page : un seul saut par frontière logique."""
    out: list[dict] = []
    for i, b in enumerate(blocks):
        nxt = blocks[i + 1] if i + 1 < len(blocks) else None
        if b["t"] == "pb":
            if nxt is None or nxt["t"] in ("pb", "section", "fullpage"):
                continue
            if nxt["t"] == "h" and nxt.get("level", 9) <= 2 and not nxt.get("page_break"):
                continue
        if b["t"] == "section" and out and out[-1]["t"] == "section":
            continue
        out.append(b)

    for i, b in enumerate(out):
        if b["t"] == "h" and b.get("level", 9) <= 2:
            prev = out[i - 1] if i else None
            b["page_break"] = not (prev and prev["t"] in ("section", "fullpage"))
    return out
