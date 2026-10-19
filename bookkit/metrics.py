"""Mesure typographique et découpe en lignes, calibrées sur les polices Word.

Les polices Times New Roman / Arial / Courier New sont métriquement identiques aux
métriques Adobe Times / Helvetica / Courier utilisées par ReportLab.
"""
from __future__ import annotations

import re
from typing import Iterable

from reportlab.pdfbase.pdfmetrics import stringWidth

_FONT_MAP = {
    ("Times New Roman", False, False): "Times-Roman",
    ("Times New Roman", True, False): "Times-Bold",
    ("Times New Roman", False, True): "Times-Italic",
    ("Times New Roman", True, True): "Times-BoldItalic",
    ("Arial", False, False): "Helvetica",
    ("Arial", True, False): "Helvetica-Bold",
    ("Arial", False, True): "Helvetica-Oblique",
    ("Arial", True, True): "Helvetica-BoldOblique",
    ("Courier New", False, False): "Courier",
    ("Courier New", True, False): "Courier-Bold",
    ("Courier New", False, True): "Courier-Oblique",
    ("Courier New", True, True): "Courier-BoldOblique",
}


def pdf_font(family: str, bold: bool, italic: bool) -> str:
    return _FONT_MAP.get((family, bold, italic)) or _FONT_MAP[(family, False, False)]


def width(text: str, family: str, size: float, bold: bool = False, italic: bool = False) -> float:
    if not text:
        return 0.0
    return stringWidth(text, pdf_font(family, bold, italic), size)


_TOKEN = re.compile(r"(\s+)")


def segments(text: str) -> list[tuple[str, str]]:
    """Découpe un texte à balisage léger en segments (texte, style).

    Balisage accepté : **gras**, *italique*, `code`, __souligné__.
    """
    out: list[tuple[str, str]] = []
    pattern = re.compile(r"(\*\*.+?\*\*|__.+?__|`.+?`|\*[^*\n]+?\*)", re.S)
    pos = 0
    for m in pattern.finditer(text):
        if m.start() > pos:
            out.append((text[pos:m.start()], "n"))
        tok = m.group(0)
        if tok.startswith("**"):
            out.append((tok[2:-2], "b"))
        elif tok.startswith("__"):
            out.append((tok[2:-2], "u"))
        elif tok.startswith("`"):
            out.append((tok[1:-1], "c"))
        elif tok.startswith("*"):
            out.append((tok[1:-1], "i"))
        pos = m.end()
    if pos < len(text):
        out.append((text[pos:], "n"))
    return out


def plain(text: str) -> str:
    return "".join(t for t, _ in segments(text))


def _style_font(base_family: str, size: float, style: str):
    if style == "c":
        return ("Courier New", size * 0.92, False, False)
    if style == "b":
        return (base_family, size, True, False)
    if style == "i":
        return (base_family, size, False, True)
    if style == "u":
        return (base_family, size, False, False)
    return (base_family, size, False, False)


def measure_markup(text: str, family: str, size: float, base_bold: bool = False) -> float:
    total = 0.0
    for chunk, st in segments(text):
        fam, sz, b, i = _style_font(family, size, st)
        total += width(chunk, fam, sz, bold=b or base_bold, italic=i)
    return total


def _split_words(text: str, family: str, size: float, bold: bool) -> list[list[tuple[str, float]]]:
    """Retourne une liste de mots ; chaque mot = liste de (texte, largeur)."""
    words: list[list[tuple[str, float]]] = []
    for chunk, st in segments(text):
        fam, sz, b, i = _style_font(family, size, st)
        for part in _TOKEN.split(chunk):
            if not part:
                continue
            if part.isspace():
                if words:
                    words[-1].append((part, width(part, family, size, bold, False)))
                else:
                    words.append([(part, width(part, family, size, bold, False))])
            else:
                words.append([(part, width(part, fam, sz, bold=b or bold, italic=i))])
    # fusionne les espaces isolés
    merged: list[list[tuple[str, float]]] = []
    for w in words:
        if merged and all(t.isspace() for t, _ in w):
            merged[-1].extend(w)
        else:
            merged.append(w)
    return merged


def count_lines(text: str, family: str, size: float, avail: float,
                bold: bool = False, first_indent: float = 0.0) -> int:
    if not text.strip():
        return 1
    words = _split_words(text, family, size, bold)
    lines = 1
    cur = 0.0
    limit = avail - first_indent
    for w in words:
        ww = sum(x[1] for x in w)
        trimmed = w[0][1] if w and w[0][0].isspace() else 0.0
        if cur > 0 and cur + ww - trimmed > limit:
            lines += 1
            cur = ww - trimmed
            limit = avail
        else:
            cur += ww
        # mot plus long que la ligne : césure dure
        while cur > limit and cur > 0:
            lines += 1
            cur -= limit
            limit = avail
    return lines


def wrap_text(text: str, family: str, size: float, avail: float,
              bold: bool = False) -> list[str]:
    """Découpe simple (sans balisage) pour les blocs de code : retourne les lignes."""
    out: list[str] = []
    for raw in text.split("\n"):
        if width(raw, family, size, bold=bold) <= avail:
            out.append(raw)
            continue
        cur = ""
        indent = len(raw) - len(raw.lstrip(" "))
        for word in raw.split(" "):
            candidate = (cur + " " + word) if cur else word
            if width(candidate, family, size, bold=bold) <= avail:
                cur = candidate
            else:
                if cur:
                    out.append(cur)
                cur = " " * min(indent + 2, 8) + word
        out.append(cur)
    return out
