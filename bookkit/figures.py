"""Génération des visuels : couverture imprimable et schémas pédagogiques."""
from __future__ import annotations

import os
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle, Rectangle, Wedge
import numpy as np

from .units import NAVY, AMBER, GREY, MIST, WHITE, GREEN, PALE_BLUE, SAND, RED

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
FIGDIR = ROOT / "build" / "figures"


def _hex(c: str) -> str:
    return "#" + c


COL = dict(navy=_hex(NAVY), amber=_hex(AMBER), grey=_hex(GREY), mist=_hex(MIST),
           white="#FFFFFF", green=_hex(GREEN), pale=_hex(PALE_BLUE), sand=_hex(SAND),
           red=_hex(RED))


# --------------------------------------------------------------------------- #
# Couverture
# --------------------------------------------------------------------------- #
def _spaced(c, x, y, text, font, size, space):
    """Texte avec interlettrage, sans setCharSpace (API variable selon versions)."""
    c.setFont(font, size)
    cur = x
    for ch in text:
        c.drawString(cur, y, ch)
        cur += c.stringWidth(ch, font, size) + space
    return cur


def make_cover(path: str | Path, logo: str = "assets/logo_blanc.png",
               chapters: int = 0) -> str:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.colors import HexColor

    W, H = A4
    pdf = str(Path(str(path)).with_suffix(".pdf"))
    c = canvas.Canvas(pdf, pagesize=A4)
    navy = HexColor("#" + NAVY)
    amber = HexColor("#" + AMBER)
    white = HexColor("#FFFFFF")

    c.setFillColor(navy)
    c.rect(0, 0, W, H, fill=1, stroke=0)

    # décor : arcs concentriques en haut à droite
    c.saveState()
    c.setStrokeColor(amber)
    c.setStrokeAlpha(0.13)
    c.setLineWidth(1.1)
    for r in range(60, 420, 22):
        c.circle(W - 30, H - 40, r, stroke=1, fill=0)
    c.restoreState()

    # trame de points en bas à gauche
    c.saveState()
    c.setFillColor(white)
    c.setFillAlpha(0.07)
    for x in range(40, 260, 14):
        for y in range(40, 200, 14):
            c.circle(x, y, 1.0, stroke=0, fill=1)
    c.restoreState()

    # filet ambre vertical
    c.setFillColor(amber)
    c.rect(0, 0, 7, H, fill=1, stroke=0)

    # logo + éditeur
    try:
        c.drawImage(str(ROOT / logo), 58, H - 138, width=64, height=61,
                    mask="auto", preserveAspectRatio=True)
    except Exception:
        pass
    c.setFillColor(white)
    _spaced(c, 134, H - 106, "ESPRITROPIC", "Helvetica-Bold", 10, 2.6)
    _spaced(c, 134, H - 122, "COMMUNITY", "Helvetica-Bold", 10, 2.6)
    c.setFillColor(amber)
    c.setFont("Helvetica", 7.6)
    c.drawString(134, H - 138, "BIBLIOTHÈQUE TECHNIQUE")

    # surtitre
    c.setFillColor(amber)
    _spaced(c, 60, H - 300, "COLLECTION TECHNIQUE · ÉDITION 2026",
            "Helvetica-Bold", 8.6, 3.2)

    # titre
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 37)
    c.drawString(58, H - 356, "DÉVELOPPEMENT WEB")
    c.drawString(58, H - 400, "& DEVOPS")
    c.setFillColor(amber)
    c.rect(60, H - 424, 96, 4, fill=1, stroke=0)

    # sous-titre
    c.setFillColor(white)
    c.setFont("Helvetica", 13)
    c.drawString(60, H - 458, "HTML5, CSS3 et JavaScript")
    c.drawString(60, H - 478, "Linux, conteneurs, cloud et fiabilité")

    c.setFillColor(HexColor("#C9D6E2"))
    c.setFont("Helvetica", 10.2)
    for i, line in enumerate([
        "Deux cours complets, progressifs et autonomes réunis dans un seul volume :",
        "du premier navigateur au pipeline de production, avec exercices corrigés,",
        "schémas, tableaux de synthèse et projets guidés.",
    ]):
        c.drawString(60, H - 516 - i * 15, line)

    # bandeau de chiffres
    c.setFillColor(HexColor("#173D60"))
    c.roundRect(58, H - 640, 476, 62, 6, fill=1, stroke=0)
    c.setFillColor(amber)
    c.setFont("Helvetica-Bold", 18)
    c.drawString(76, H - 622, "2")
    c.drawString(212, H - 622, str(chapters or 0))
    c.drawString(342, H - 622, "350+")
    c.setFillColor(white)
    c.setFont("Helvetica", 7.6)
    c.drawString(76, H - 610, "COURS COMPLETS")
    c.drawString(212, H - 610, "CHAPITRES")
    c.drawString(342, H - 610, "PAGES PAR COURS")

    # bas de couverture
    c.setStrokeColor(HexColor("#3A5A78"))
    c.setLineWidth(0.8)
    c.line(58, 148, 534, 148)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(58, 122, "ICABOT")
    c.setFillColor(HexColor("#C9D6E2"))
    c.setFont("Helvetica", 8.6)
    c.drawString(58, 108, "ESPRITROPIC COMMUNITY")
    c.drawRightString(534, 122, "espritropic.rf.gd")
    c.drawRightString(534, 108, "Édition 2026 · Volume unique")

    c.showPage()
    c.save()

    import pymupdf
    doc = pymupdf.open(pdf)
    pix = doc[0].get_pixmap(dpi=300)
    pix.save(str(path))
    doc.close()
    os.remove(pdf)
    return str(path)


# --------------------------------------------------------------------------- #
# Schémas
# --------------------------------------------------------------------------- #
def _canvas(w_pt: float, h_pt: float):
    fig = plt.figure(figsize=(w_pt / 72.0, h_pt / 72.0), dpi=220)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, w_pt)
    ax.set_ylim(0, h_pt)
    ax.axis("off")
    return fig, ax


def _rbox(ax, x, y, w, h, text, fc, ec=None, tc="#FFFFFF", fs=8.2, bold=True, r=5, lw=0.8):
    p = FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={r}",
                       linewidth=lw, edgecolor=ec or fc, facecolor=fc, zorder=2)
    ax.add_patch(p)
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center",
            fontsize=fs, color=tc, zorder=3,
            fontweight="bold" if bold else "normal", linespacing=1.25)


def _arrow(ax, x1, y1, x2, y2, color=None, lw=1.1):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="-|>", color=color or COL["amber"],
                                lw=lw, shrinkA=2, shrinkB=2, mutation_scale=9), zorder=1)


def _wrap(s: str, n: int = 26):
    import textwrap
    return "\n".join(textwrap.wrap(s, n))


def draw_flow(payload, path, w=440, h=250):
    steps = payload
    fig, ax = _canvas(w, h)
    n = len(steps)
    gap = 12
    bh = (h - (n - 1) * gap - 16) / n
    for i, s in enumerate(steps):
        y = h - 8 - (i + 1) * bh - i * gap
        fc = COL["navy"] if i % 2 == 0 else COL["navy"]
        _rbox(ax, 60, y, w - 128, bh, _wrap(s, 52), fc, fs=8.6)
        if i < n - 1:
            _arrow(ax, w / 2, y, w / 2, y - gap + 1)
    if n >= 2:
        ax.text(28, h / 2, "→", fontsize=1, color="white")
    fig.savefig(path, dpi=220, facecolor="white")
    plt.close(fig)


def draw_stack(payload, path, w=440, h=250):
    fig, ax = _canvas(w, h)
    n = len(payload)
    bh = (h - 16 - (n - 1) * 6) / n
    for i, item in enumerate(payload):
        label, sub = item if isinstance(item, (tuple, list)) else (item, "")
        y = 8 + i * (bh + 6)
        _rbox(ax, 70, y, w - 140, bh, "", COL["pale"], ec=COL["navy"], lw=0.9)
        ax.text(84, y + bh * 0.62, label, fontsize=8.8, color=COL["navy"], fontweight="bold", va="center")
        if sub:
            ax.text(84, y + bh * 0.28, _wrap(sub, 66), fontsize=7.4, color=COL["grey"], va="center")
    fig.savefig(path, dpi=220, facecolor="white")
    plt.close(fig)


def draw_cycle(payload, path, w=440, h=250):
    fig, ax = _canvas(w, h)
    n = len(payload)
    cx, cy, rx, ry = w / 2, h / 2, w * 0.33, h * 0.32
    for i, s in enumerate(payload):
        ang = np.pi / 2 - i * 2 * np.pi / n
        x = cx + rx * np.cos(ang)
        y = cy + ry * np.sin(ang)
        _rbox(ax, x - 62, y - 17, 124, 34, _wrap(s, 22), COL["navy"], fs=7.6)
        ang2 = np.pi / 2 - (i + 0.55) * 2 * np.pi / n
        x2 = cx + rx * np.cos(ang2)
        y2 = cy + ry * np.sin(ang2)
        _arrow(ax, x2, y2, cx + rx * np.cos(ang2 - 0.35), cy + ry * np.sin(ang2 - 0.35))
    ax.text(cx, cy, "cycle", ha="center", va="center", fontsize=7.5, color=COL["grey"], style="italic")
    fig.savefig(path, dpi=220, facecolor="white")
    plt.close(fig)


def draw_hub(payload, path, w=440, h=250):
    fig, ax = _canvas(w, h)
    center, spokes = payload
    cx, cy = w / 2, h / 2
    _rbox(ax, cx - 72, cy - 22, 144, 44, _wrap(center, 20), COL["amber"], tc=COL["navy"], fs=8.4)
    n = len(spokes)
    for i, s in enumerate(spokes):
        ang = 2 * np.pi * i / n + np.pi / n
        x = cx + 0.36 * w * np.cos(ang)
        y = cy + 0.36 * h * np.sin(ang)
        _rbox(ax, x - 58, y - 15, 116, 30, s, COL["pale"], ec=COL["navy"], tc=COL["navy"], fs=7.6)
        _arrow(ax, cx + 76 * np.cos(ang), cy + 24 * np.sin(ang),
               x - 60 * np.cos(ang), y - 16 * np.sin(ang), color=COL["navy"], lw=0.8)
    fig.savefig(path, dpi=220, facecolor="white")
    plt.close(fig)


def draw_columns(payload, path, w=440, h=250):
    fig, ax = _canvas(w, h)
    n = len(payload)
    gap = 8
    bw = (w - 16 - (n - 1) * gap) / n
    for i, col in enumerate(payload):
        head, items = col
        x = 8 + i * (bw + gap)
        _rbox(ax, x, h - 40, bw, 26, head.upper(), COL["navy"], fs=7.8)
        ax.add_patch(Rectangle((x, 10), bw, h - 54, facecolor=COL["pale"],
                               edgecolor="#D5DEE6", lw=0.8, zorder=1))
        for j, it in enumerate(items):
            ax.text(x + 7, h - 56 - j * 13.5, "• " + _wrap(it, 26).replace("\n", "\n  "),
                    fontsize=7.0, color=COL["navy"], va="top")
    fig.savefig(path, dpi=220, facecolor="white")
    plt.close(fig)


def draw_matrix(payload, path, w=440, h=250):
    fig, ax = _canvas(w, h)
    xlab, ylab, cells = payload
    ax.add_patch(Rectangle((40, 24), w - 56, h - 58, facecolor="#FFFFFF",
                           edgecolor="#CBD5DE", lw=0.8))
    ax.plot([40 + (w - 56) / 2] * 2, [24, h - 34], color="#CBD5DE", lw=0.8)
    ax.plot([40, w - 16], [24 + (h - 58) / 2] * 2, color="#CBD5DE", lw=0.8)
    pos = [(40 + (w - 56) * 0.25, 24 + (h - 58) * 0.75),
           (40 + (w - 56) * 0.75, 24 + (h - 58) * 0.75),
           (40 + (w - 56) * 0.25, 24 + (h - 58) * 0.25),
           (40 + (w - 56) * 0.75, 24 + (h - 58) * 0.25)]
    cols = [COL["sand"], COL["pale"], COL["pale"], COL["sand"]]
    for i, (cx, cy) in enumerate(pos):
        ax.add_patch(Rectangle((cx - (w - 56) / 4, cy - (h - 58) / 4), (w - 56) / 2, (h - 58) / 2,
                               facecolor=cols[i], edgecolor="none", zorder=1))
        label = cells[i] if i < len(cells) else ""
        ax.text(cx, cy, _wrap(label, 30), ha="center", va="center", fontsize=7.6,
                color=COL["navy"], zorder=2)
    ax.text(w / 2, 8, xlab, ha="center", fontsize=7.4, color=COL["grey"], style="italic")
    ax.text(18, h / 2, ylab, ha="center", va="center", rotation=90, fontsize=7.4,
            color=COL["grey"], style="italic")
    fig.savefig(path, dpi=220, facecolor="white")
    plt.close(fig)


def draw_timeline(payload, path, w=440, h=250):
    fig, ax = _canvas(w, h)
    n = len(payload)
    ax.plot([28, w - 20], [h / 2, h / 2], color=COL["navy"], lw=1.0)
    step = (w - 48) / max(n - 1, 1)
    for i, (year, label) in enumerate(payload):
        x = 28 + i * step
        up = i % 2 == 0
        ax.add_patch(Circle((x, h / 2), 4.2, facecolor=COL["amber"], edgecolor="white", lw=1.2, zorder=3))
        ax.text(x, h / 2 + (14 if up else -14), year, ha="center", va="center",
                fontsize=8.4, color=COL["navy"], fontweight="bold")
        ax.text(x, h / 2 + (32 if up else -46), _wrap(label, 16), ha="center",
                va="center", fontsize=7.0, color=COL["grey"])
    fig.savefig(path, dpi=220, facecolor="white")
    plt.close(fig)


def draw_tree(payload, path, w=440, h=250):
    fig, ax = _canvas(w, h)
    root, branches = payload
    _rbox(ax, w / 2 - 72, h - 40, 144, 28, root, COL["navy"], fs=8.4)
    n = len(branches)
    bw = (w - 20 - (n - 1) * 8) / n
    for i, (b, leaves) in enumerate(branches):
        x = 10 + i * (bw + 8)
        _rbox(ax, x, h - 100, bw, 28, _wrap(b, 20), COL["amber"], tc=COL["navy"], fs=7.6)
        ax.plot([w / 2, x + bw / 2], [h - 40, h - 72], color="#B9C6D2", lw=0.8, zorder=0)
        ax.plot([x + bw / 2, x + bw / 2], [h - 100, h - 108], color="#B9C6D2", lw=0.8, zorder=0)
        for j, lf in enumerate(leaves[:5]):
            yy = h - 122 - j * 20
            ax.text(x + 4, yy, "– " + _wrap(lf, 24).replace("\n", "\n   "), fontsize=6.8,
                    color=COL["navy"], va="center")
    fig.savefig(path, dpi=220, facecolor="white")
    plt.close(fig)


def draw_compare(payload, path, w=440, h=250):
    fig, ax = _canvas(w, h)
    left_t, left_i, right_t, right_i = payload
    mid = w / 2
    for i, (t, items, x, fc) in enumerate([(left_t, left_i, 8, COL["pale"]),
                                           (right_t, right_i, mid + 6, COL["sand"])]):
        ax.add_patch(Rectangle((x, 12), mid - 14, h - 44, facecolor=fc, edgecolor="#D5DEE6", lw=0.8))
        ax.text(x + (mid - 14) / 2, h - 24, t.upper(), ha="center", fontsize=8.0,
                color=COL["navy"], fontweight="bold")
        for j, it in enumerate(items):
            ax.text(x + 10, h - 48 - j * 17, "• " + _wrap(it, 32).replace("\n", "\n  "),
                    fontsize=7.2, color=COL["navy"], va="top")
    fig.savefig(path, dpi=220, facecolor="white")
    plt.close(fig)


DRAWERS = {
    "flow": draw_flow, "stack": draw_stack, "cycle": draw_cycle, "hub": draw_hub,
    "columns": draw_columns, "matrix": draw_matrix, "timeline": draw_timeline,
    "tree": draw_tree, "compare": draw_compare,
}


def make_figure(block: dict, name: str) -> str:
    FIGDIR.mkdir(parents=True, exist_ok=True)
    path = FIGDIR / f"{name}.png"
    h = float(block.get("height", 250.0))
    DRAWERS[block["kind"]](block["payload"], str(path), w=439.0, h=h)
    return str(path)
