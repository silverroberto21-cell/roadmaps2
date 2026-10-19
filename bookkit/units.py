"""Constantes physiques partagées par le rendu Word et le moteur de pagination."""
from __future__ import annotations

CM = 72.0 / 2.54

PAGE_W_CM = 21.0
PAGE_H_CM = 29.7
MARGIN_TOP_CM = 2.6
MARGIN_BOTTOM_CM = 2.4
MARGIN_LEFT_CM = 2.7
MARGIN_RIGHT_CM = 2.4
HEADER_CM = 1.25
FOOTER_CM = 1.15

TEXT_W_PT = (PAGE_W_CM - MARGIN_LEFT_CM - MARGIN_RIGHT_CM) * CM   # 462,05 pt
TEXT_H_PT = (PAGE_H_CM - MARGIN_TOP_CM - MARGIN_BOTTOM_CM) * CM   # 711,50 pt

# Palette (voir docs/DESIGN.md)
NAVY = "0F2E4C"
NAVY_LIGHT = "274B6D"
AMBER = "E0A21B"
SAND = "FBF3E2"
INK = "1F2933"
GREY = "5B6770"
MIST = "E8EDF1"
GREEN = "2F7D5B"
RED = "A63A32"
WHITE = "FFFFFF"
PALE_GREEN = "EAF3EE"
PALE_RED = "F7ECEA"
PALE_BLUE = "EFF4F8"

# Spécifications typographiques : (police Word, corps pt, interligne exact pt,
# espace avant pt, espace après pt)
S = {
    "body":      dict(font="Times New Roman", size=11.5, line=17.4, before=0.0,  after=7.5),
    "lead":      dict(font="Times New Roman", size=12.4, line=18.6, before=2.0,  after=10.0),
    "h1":        dict(font="Arial",           size=23.0, line=27.0, before=0.0,  after=14.0),
    "h2":        dict(font="Arial",           size=14.5, line=19.5, before=22.0, after=9.0),
    "h3":        dict(font="Arial",           size=11.8, line=16.0, before=15.0, after=7.0),
    "h4":        dict(font="Arial",           size=10.8, line=14.5, before=11.0, after=5.0),
    "bullet":    dict(font="Times New Roman", size=11.5, line=17.4, before=0.0,  after=4.0),
    "number":    dict(font="Times New Roman", size=11.5, line=17.4, before=0.0,  after=4.0),
    "code":      dict(font="Courier New",     size=9.2,  line=12.2, before=9.0,  after=12.0),
    "codecap":   dict(font="Arial",           size=8.0,  line=10.5, before=0.0,  after=4.0),
    "caption":   dict(font="Arial",           size=8.5,  line=11.0, before=3.0,  after=10.0),
    "quote":     dict(font="Times New Roman", size=11.0, line=16.4, before=7.0,  after=10.0),
    "boxtext":   dict(font="Times New Roman", size=10.8, line=15.8, before=0.0,  after=5.0),
    "boxitem":   dict(font="Times New Roman", size=10.8, line=15.8, before=0.0,  after=2.0),
    "boxtitle":  dict(font="Arial",           size=9.0,  line=12.5, before=0.0,  after=4.0),
    "table":     dict(font="Arial",           size=9.5,  line=13.0, before=0.0,  after=0.0),
    "tablehead": dict(font="Arial",           size=9.0,  line=12.5, before=0.0,  after=0.0),
    "toc1":      dict(font="Arial",           size=11.5, line=17.0, before=9.0,  after=1.0),
    "toc2":      dict(font="Arial",           size=10.5, line=15.5, before=1.0,  after=0.5),
    "toc3":      dict(font="Times New Roman", size=10.5, line=14.6, before=0.0,  after=0.0),
    "partnum":   dict(font="Arial",           size=44.0, line=50.0, before=0.0,  after=6.0),
    "parttitle": dict(font="Arial",           size=26.0, line=31.0, before=0.0,  after=14.0),
    "partdesc":  dict(font="Times New Roman", size=11.5, line=16.5, before=0.0,  after=6.0),
    "covertitle": dict(font="Arial",          size=34.0, line=40.0, before=0.0,  after=10.0),
    "chapeye":   dict(font="Arial",           size=9.0,  line=12.0, before=0.0,  after=6.0),
    "chapnum":   dict(font="Arial",           size=44.0, line=48.0, before=0.0,  after=2.0),
    "small":     dict(font="Arial",           size=8.5,  line=11.5, before=0.0,  after=4.0),
    "exhead":    dict(font="Arial",           size=10.5, line=15.0, before=14.0, after=4.0),
    "qhead":     dict(font="Arial",           size=9.5,  line=13.5, before=12.0, after=3.0),
    "corrhead":  dict(font="Arial",           size=10.5, line=15.0, before=12.0, after=4.0),
    "opt":       dict(font="Times New Roman", size=10.5, line=15.5, before=0.0,  after=1.5),
}

# Marges internes
CODE_PAD_V = 5.0          # bordure/ombrage : espace vertical, pt
CODE_INDENT_CM = 0.25
TABLE_CELL_PAD_V = 3.3    # pt
TABLE_CELL_PAD_H = 5.6    # pt
BOX_PAD_V = 7.0
BOX_PAD_H = 8.0
BULLET_INDENT_CM = 0.55
BULLET_HANG_CM = 0.45
QUOTE_INDENT_CM = 0.9
