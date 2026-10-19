#!/usr/bin/env python3
"""Contrôles automatiques de qualité sur les chapitres."""
import importlib, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

EN_WORDS = [" the ", " and ", " with ", " methods ", " which ", " because ",
            " also ", " from the ", " of the ", " to the "]


def main():
    problems = []
    chapters = sorted(ROOT.glob("content/c*/ch*.py"))
    for path in chapters:
        mod = ".".join(path.relative_to(ROOT).with_suffix("").parts)
        try:
            m = importlib.import_module(mod)
            importlib.reload(m)
        except Exception as e:
            problems.append(f"{path.name}: IMPORT {e}")
            continue
        ch = m.CH
        text = path.read_text(encoding="utf-8")
        for w in EN_WORDS:
            if w in text:
                problems.append(f"{path.name}: anglicisme probable {w!r}")
        if len(ch["blocks"]) < 12:
            problems.append(f"{path.name}: seulement {len(ch['blocks'])} blocs")
        if not ch.get("exercises"):
            problems.append(f"{path.name}: aucun exercice")
        if len(ch.get("quiz", [])) < 4:
            problems.append(f"{path.name}: moins de 4 questions")
        def size(o):
            if isinstance(o, str):
                return len(o)
            if isinstance(o, dict):
                return sum(size(v) for v in o.values())
            if isinstance(o, (list, tuple)):
                return sum(size(v) for v in o)
            return 0
        chars = size(ch.get("blocks")) + size(ch.get("exercises")) + size(ch.get("quiz"))
        if chars < 8800:
            problems.append(f"{path.name}: contenu court ({chars} caractères)")
    print(f"{len(chapters)} chapitres analysés")
    for p in problems:
        print(" -", p)
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
