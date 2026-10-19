"""DSL de rédaction : les cours sont écrits comme des listes de blocs typés."""
from __future__ import annotations

import re


def p(text: str, style: str = "body") -> dict:
    return {"t": "p", "text": text.strip(), "style": style}


def lead(text: str) -> dict:
    return {"t": "p", "text": text.strip(), "style": "lead"}


def h(level: int, text: str) -> dict:
    return {"t": "h", "level": level, "text": text.strip()}


def ul(*items: str) -> dict:
    return {"t": "ul", "items": [i.strip() for i in items]}


def ol(*items: str) -> dict:
    return {"t": "ol", "items": [i.strip() for i in items]}


def code(text: str, lang: str = "", caption: str | None = None) -> dict:
    return {"t": "code", "text": text.strip("\n"), "lang": lang, "caption": caption}


def table(headers: list[str], rows: list[list[str]], widths: list[float] | None = None,
          caption: str | None = None, first_col_bold: bool = False) -> dict:
    return {"t": "table", "headers": headers, "rows": rows, "widths": widths,
            "caption": caption, "first_col_bold": first_col_bold}


def box(kind: str, title: str, text: str | None = None, items: list[str] | None = None) -> dict:
    return {"t": "box", "kind": kind, "title": title, "text": text, "items": items}


def defn(term: str, text: str) -> dict:
    return {"t": "box", "kind": "definition", "title": f"Définition — {term}", "text": text, "items": None}


def quote(text: str, source: str | None = None) -> dict:
    return {"t": "quote", "text": text.strip(), "source": source}


def fig(kind: str, title: str, payload, note: str | None = None, height: float = 250.0) -> dict:
    return {"t": "fig", "kind": kind, "title": title, "payload": payload,
            "note": note, "height": height}


def ex(title: str, prompt: str, tasks: list[str], solution, hint: str | None = None,
       level: str = "Application") -> dict:
    return {"t": "ex", "title": title, "prompt": prompt.strip(), "tasks": tasks,
            "solution": solution, "hint": hint, "level": level}


def quiz(question: str, options: list[str], answer: int, explanation: str) -> dict:
    return {"t": "quiz", "question": question.strip(), "options": options,
            "answer": answer, "explanation": explanation.strip()}


def pb() -> dict:
    return {"t": "pb"}


def parse_blocks(raw) -> list[dict]:
    if callable(raw):
        raw = raw()
    return raw
