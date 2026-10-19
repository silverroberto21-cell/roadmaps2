"""Calcul des hauteurs de blocs — source unique pour le modèle et le rendu."""
from __future__ import annotations

from .metrics import count_lines, wrap_text
from .units import (
    S, TEXT_W_PT, CODE_PAD_V, TABLE_CELL_PAD_V, TABLE_CELL_PAD_H,
    BOX_PAD_V, BOX_PAD_H, CM,
)

BODY_W = TEXT_W_PT
BULLET_W = TEXT_W_PT - 0.55 * CM
NUMBER_W = TEXT_W_PT - 0.75 * CM
CODE_W = TEXT_W_PT - 0.25 * CM - 2 * CODE_PAD_V - 2.0
BOX_W = TEXT_W_PT - 2 * BOX_PAD_H - 2.0
QUOTE_W = TEXT_W_PT - 0.9 * CM


def _lines(text: str, spec: dict, width: float, bold: bool = False) -> int:
    return count_lines(text, spec["font"], spec["size"], width, bold=bold)


def para_height(text: str, spec: dict, width: float = BODY_W, bold: bool = False) -> float:
    return _lines(text, spec, width, bold) * spec["line"] + spec["before"] + spec["after"]


def code_lines(text: str) -> list[str]:
    return wrap_text(text, "Courier New", S["code"]["size"], CODE_W)


def code_height(text: str, caption: str | None = None) -> float:
    n = len(code_lines(text))
    h = n * S["code"]["line"] + 2 * CODE_PAD_V + S["code"]["before"] + S["code"]["after"]
    if caption:
        h += S["codecap"]["line"] + S["codecap"]["after"]
    return h


def fig_height(block: dict) -> float:
    h = block.get("height", 250.0)
    h += S["caption"]["line"] + S["caption"]["before"] + S["caption"]["after"]
    return h


def box_height(block: dict) -> float:
    inner_w = BOX_W
    total = 2 * BOX_PAD_V + S["boxtitle"]["line"] + S["boxtitle"]["after"]
    if block.get("text"):
        total += _lines(block["text"], S["boxtext"], inner_w) * S["boxtext"]["line"]
        total += S["boxtext"]["after"]
    for it in block.get("items") or []:
        total += _lines(it, S["boxitem"], inner_w - 0.5 * CM) * S["boxitem"]["line"]
        total += S["boxitem"]["after"]
    total += 7.0  # espace avant
    return total


def col_widths(block: dict) -> list[float]:
    n = len(block["headers"])
    raw = block.get("widths") or [1.0] * n
    s = sum(raw)
    return [TEXT_W_PT * w / s for w in raw]


def table_row_heights(block: dict) -> list[float]:
    ws = col_widths(block)
    hs = []
    for row in [block["headers"]] + block["rows"]:
        lines = 1
        for cell, w in zip(row, ws):
            lines = max(lines, _lines(str(cell), S["table"], max(w - 2 * TABLE_CELL_PAD_H, 20)))
        hs.append(lines * S["table"]["line"] + 2 * TABLE_CELL_PAD_V)
    return hs


def table_height(block: dict) -> float:
    h = sum(table_row_heights(block))
    if block.get("caption"):
        h += S["caption"]["line"] + S["caption"]["before"] + S["caption"]["after"]
    return h


def block_height(block: dict) -> float:
    t = block["t"]
    if t == "p":
        spec = S.get(block.get("style", "body"), S["body"])
        return para_height(block["text"], spec)
    if t == "h":
        spec = S[f"h{block['level']}"]
        return _lines(block["text"], spec, BODY_W, bold=True) * spec["line"] + spec["before"] + spec["after"]
    if t in ("ul", "ol"):
        spec = S["bullet"] if t == "ul" else S["number"]
        width = BULLET_W if t == "ul" else NUMBER_W
        total = spec["before"]
        for it in block["items"]:
            total += _lines(it, spec, width) * spec["line"] + spec["after"]
        return total
    if t == "code":
        return code_height(block["text"], block.get("caption"))
    if t == "table":
        return table_height(block)
    if t == "fig":
        return fig_height(block)
    if t == "box":
        return box_height(block)
    if t == "quote":
        spec = S["quote"]
        return _lines(block["text"], spec, QUOTE_W) * spec["line"] + spec["before"] + spec["after"] + 4
    if t == "exhead":
        return para_height(block["text"], S["exhead"], BODY_W, bold=True)
    if t == "corrhead":
        return para_height(block["text"], S["corrhead"], BODY_W, bold=True)
    if t == "qhead":
        return para_height(block["text"], S["qhead"], BODY_W, bold=True)
    if t == "opts":
        return sum(para_height(o, S["opt"], BODY_W - 0.8 * CM) for o in block["items"])
    if t == "toc_entry":
        spec = S[f"toc{block['level']}"]
        n = _lines(block["text"] + "  000", spec, BODY_W - (0.0 if block["level"] == 1 else 0.5 * CM))
        return n * spec["line"] + spec["before"] + spec["after"]
    if t in ("toc_start", "toc_end"):
        return 1.0
    if t == "rule":
        return 16.0
    if t == "logo":
        return block.get("width", 3.2) * CM * 905 / 943 + 10 + 4
    if t == "vspace":
        return max(block.get("h", 12), 1)
    if t == "bigtitle":
        return len(block["text"].split("\n")) * 46
    if t == "smallcaps":
        return 14.5 + 12
    if t == "rubric":
        key = "h1" if block.get("style") == "Titre hors sommaire" else "h3"
        spec = dict(S[key])
        if block.get("style") == "Titre hors sommaire":
            spec.update(before=0.0, after=12.0, line=24.0, size=18.0)
        return _lines(block["text"], spec, BODY_W, bold=True) * spec["line"] + spec["before"] + spec["after"]
    if t == "toc_course":
        spec = S["toc3"]
        n = _lines(block["text"] + "  000", spec, BODY_W - block.get("indent", 0.0) * CM)
        return n * 14.0 + 2.0
    if t == "pb":
        return 0.0
    if t in ("fullpage",):
        return 1e9
    raise ValueError(f"bloc inconnu: {t}")
