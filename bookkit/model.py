"""Moteur de pagination : simule la mise en pages Word bloc par bloc.

Tous les blocs sont insécables (réglages Word : « lignes solidaires » et
« paragraphes solidaires »), sauf les tableaux qui se coupent entre deux lignes
avec répétition de l'en-tête. La pagination est donc déterministe.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from .layout import block_height, table_row_heights
from .units import TEXT_H_PT


@dataclass
class Pagination:
    pages: int
    marks: dict[str, int] = field(default_factory=dict)


def paginate(blocks: list[dict], page: int = 1, y: float = TEXT_H_PT) -> Pagination:
    marks: dict[str, int] = {}
    for i, b in enumerate(blocks):
        t = b["t"]
        if b.get("id"):
            marks[b["id"]] = page

        if t == "section":
            if y < TEXT_H_PT - 0.5:
                page += 1
            y = TEXT_H_PT
            continue
        if t == "fullpage":
            if y < TEXT_H_PT - 0.5:
                page += 1
            y = TEXT_H_PT
            page += 1          # la page pleine est consommée
            y = TEXT_H_PT
            continue

        h = block_height(b)
        need_break = b.get("page_break", False)
        if need_break and y < TEXT_H_PT - 0.5:
            page += 1
            y = TEXT_H_PT

        if b.get("keep_next") or t in ("h", "rubric", "exhead", "qhead", "corrhead"):
            nxt = 0.0
            for nb in blocks[i + 1:i + 2]:
                try:
                    nxt = min(block_height(nb), 46.0)
                except Exception:
                    nxt = 0.0
            if h + nxt > y:
                page += 1
                y = TEXT_H_PT

        if t == "table":
            rows = table_row_heights(b)
            head = rows[0]
            if b.get("caption"):
                cap = 24.0
                if y - cap - head < 0:
                    page += 1
                    y = TEXT_H_PT
                y -= cap
            for i2, rh in enumerate(rows):
                if rh > y:
                    page += 1
                    y = TEXT_H_PT
                    if i2 > 0:
                        y -= min(head, y)
                y -= rh
            continue

        if h > y:
            page += 1
            y = TEXT_H_PT
        y -= h
    return Pagination(pages=page, marks=marks)
