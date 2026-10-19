"""Aperçu PDF : rendu indépendant des mêmes blocs, pour contrôler la mise en page.

Ce rendu utilise ReportLab/Platypus, dont la pagination est calculée par un moteur
distinct de celui du document Word. L'écart de pagination entre les deux moteurs
constitue un contrôle de cohérence.
"""
from __future__ import annotations

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.platypus import (BaseDocTemplate, Flowable, Frame, Image, KeepTogether,
                                PageBreak, PageTemplate, Paragraph, Spacer, Table,
                                TableStyle)
from xml.sax.saxutils import escape

from .figures import make_figure
from .layout import code_lines, col_widths
from .units import (S, TEXT_W_PT, TEXT_H_PT, NAVY, NAVY_LIGHT, AMBER, SAND, INK,
                    GREY, MIST, GREEN, RED, PALE_GREEN, PALE_RED, PALE_BLUE)

C = lambda h: colors.HexColor("#" + h)


class _Mark(Flowable):
    """Repère invisible qui note la page où il est composé."""

    def __init__(self, cle: str, sink: dict):
        super().__init__()
        self.cle = cle
        self.sink = sink
        self.width = 0
        self.height = 0

    def wrap(self, aw, ah):
        return (0, 0)

    def draw(self):
        self.sink[self.cle] = self.canv.getPageNumber()

BOX_COLORS = {
    "objectifs": (SAND, AMBER), "retenir": (PALE_GREEN, GREEN),
    "attention": (PALE_RED, RED), "pratique": (PALE_BLUE, NAVY_LIGHT),
    "definition": (MIST, NAVY), "note": (MIST, GREY), "methode": (SAND, AMBER),
}


def _runs(text: str) -> str:
    from .metrics import segments
    out = []
    for chunk, st in segments(text):
        t = escape(chunk)
        if st == "b":
            out.append(f"<b>{t}</b>")
        elif st == "i":
            out.append(f"<i>{t}</i>")
        elif st == "u":
            out.append(f"<u>{t}</u>")
        elif st == "c":
            out.append(f'<font name="Courier" size="9">{t}</font>')
        else:
            out.append(t)
    return "".join(out)


def _ps(name: str, spec: dict, squeeze: float = 1.0, color: str = INK,
        align: int = TA_LEFT, left: float = 0.0, first: float = 0.0) -> ParagraphStyle:
    return ParagraphStyle(
        name, fontName=__import__("bookkit.metrics", fromlist=["pdf_font"]).pdf_font(
            spec["font"], False, False),
        fontSize=spec["size"], leading=spec["line"],
        spaceBefore=spec["before"] * squeeze, spaceAfter=spec["after"] * squeeze,
        textColor=C(color), alignment=align, leftIndent=left,
        firstLineIndent=first, allowWidows=1, allowOrphans=1,
    )


STYLES = {
    "body": _ps("body", S["body"]),
    "lead": _ps("lead", S["lead"], color=NAVY_LIGHT),
    "small": _ps("small", S["small"], color=GREY),
    "h1": _ps("h1", S["h1"], color=NAVY),
    "h2": _ps("h2", S["h2"], color=NAVY),
    "h3": _ps("h3", S["h3"], color=NAVY_LIGHT),
    "h4": _ps("h4", S["h4"], color=NAVY_LIGHT),
    "quote": _ps("quote", S["quote"], color=NAVY_LIGHT, left=0.9 * cm),
    "caption": _ps("caption", S["caption"], color=GREY, align=TA_LEFT),
    "codecap": _ps("codecap", S["codecap"], color=NAVY_LIGHT),
    "table": _ps("table", S["table"]),
    "tablehead": _ps("tablehead", S["tablehead"], color="FFFFFF"),
}


def _header_footer(canvas, doc, left: str, right: str):
    canvas.saveState()
    canvas.setStrokeColor(C(AMBER))
    canvas.setLineWidth(0.7)
    y = A4[1] - 1.9 * cm
    canvas.line(2.5 * cm, y, A4[0] - 2.2 * cm, y)
    canvas.setFont("Helvetica", 7.4)
    canvas.setFillColor(C(GREY))
    canvas.drawString(2.5 * cm, y + 5, left.upper())
    canvas.drawRightString(A4[0] - 2.2 * cm, y + 5, right.upper())
    canvas.setFont("Helvetica", 7.2)
    canvas.drawString(2.5 * cm, 1.35 * cm, "ESPRITROPIC COMMUNITY · Bibliothèque technique")
    canvas.drawRightString(A4[0] - 2.2 * cm, 1.35 * cm, f"Page {doc.page}")
    canvas.restoreState()


class PreviewBook:
    def __init__(self, blocks, path: str, title: str):
        self.blocks = blocks
        self.path = path
        self.title = title

    def story(self):
        flow = []
        self.marks: dict[str, int] = {}

        def add_break():
            if not flow or not isinstance(flow[-1], PageBreak):
                flow.append(PageBreak())
        chapter = 0
        fig_c: dict[int, int] = {}
        tab_c: dict[int, int] = {}

        def H(text, size, color=NAVY, before=0, after=8, gap=1.25):
            return Paragraph(escape(text), ParagraphStyle(
                "tmp", fontName="Helvetica-Bold", fontSize=size, leading=size * gap,
                textColor=C(color), spaceBefore=before, spaceAfter=after))

        for b in self.blocks:
            t = b["t"]
            if t == "section":
                add_break()
            elif t == "fullpage":
                add_break()
                inner = [Spacer(1, 2.0 * cm),
                         H(b["label"].upper(), 9, AMBER, 0, 10),
                         H(b["title"], 26, "FFFFFF", 0, 12, 1.2),
                         Spacer(1, 4),
                         Paragraph(escape(b["description"]),
                                   ParagraphStyle("pd", fontName="Times-Roman", fontSize=11.5,
                                                  leading=16.5, textColor=C("D6E1EB"))),
                         Spacer(1, 10),
                         Paragraph(escape(" · ".join(b.get("chapters", []))),
                                   ParagraphStyle("pc", fontName="Helvetica", fontSize=8.6,
                                                  leading=13.5, textColor=C("C9D6E2")))]
                tb = Table([[inner]], colWidths=[TEXT_W_PT], rowHeights=[20.4 * cm])
                tb.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), C(NAVY)),
                                        ("LEFTPADDING", (0, 0), (-1, -1), 34),
                                        ("RIGHTPADDING", (0, 0), (-1, -1), 34),
                                        ("VALIGN", (0, 0), (-1, -1), "MIDDLE")]))
                tb._cle = b.get("id")
                flow.append(tb)
            elif t == "logo":
                flow.append(Image(b["path"], width=b.get("width", 3.2) * cm,
                                  height=b.get("width", 3.2) * cm * 905 / 943))
                flow.append(Spacer(1, 10))
            elif t == "vspace":
                flow.append(Spacer(1, b.get("h", 12)))
            elif t == "bigtitle":
                for line in b["text"].split("\n"):
                    flow.append(H(line, 40, NAVY, 0, 0, 1.12))
            elif t == "smallcaps":
                flow.append(H(b["text"], 9.5, GREY, 2, 10))
            elif t == "rule":
                flow.append(Spacer(1, 6))
                tb = Table([[""]], colWidths=[TEXT_W_PT], rowHeights=[1])
                tb.setStyle(TableStyle([("LINEBELOW", (0, 0), (-1, -1), 1.5, C(AMBER))]))
                flow.append(tb)
                flow.append(Spacer(1, 10))
            elif t == "h":
                if b.get("page_break"):
                    add_break()
                import re as _re
                _m = _re.match(r"^ch(\d+)$", b.get("id") or "")
                if _m:
                    chapter = int(_m.group(1))
                if b.get("eyebrow"):
                    flow.append(H(b["eyebrow"], 9, AMBER, 0, 6))
                if b.get("style") == "Titre de cours":
                    titre = H(b["text"], 27, NAVY, 0, 12, 1.2)
                    titre._cle = b.get("id")
                    flow.append(titre)
                elif b["level"] == 2:
                    import re
                    m = re.match(r"(\d+)\.\s*(.*)", b["text"])
                    if m:
                        titre = H(f"{m.group(1)}. {m.group(2)}", 22, NAVY, 0, 12, 1.2)
                    else:
                        titre = H(b["text"], 22, NAVY, 0, 12, 1.2)
                    titre._cle = b.get("id")
                    flow.append(titre)
                else:
                    titre = H(b["text"], S[f"h{min(b['level'], 4)}"]["size"],
                              NAVY if b["level"] < 3 else NAVY_LIGHT,
                              S[f"h{min(b['level'], 4)}"]["before"], 7)
                    titre._cle = b.get("id")
                    flow.append(titre)
            elif t == "rubric":
                size = 18 if b.get("style") == "Titre hors sommaire" else 13
                flow.append(H(b["text"], size, NAVY_LIGHT, 16, 8))
            elif t == "p":
                st = STYLES.get(b.get("style", "body"), STYLES["body"])
                flow.append(Paragraph(_runs(b["text"]), st))
            elif t == "ul":
                for it in b["items"]:
                    flow.append(Paragraph("•\u00a0" + _runs(it), ParagraphStyle(
                        "li", parent=STYLES["body"], leftIndent=0.55 * cm,
                        firstLineIndent=-0.45 * cm, spaceAfter=3)))
            elif t == "ol":
                for i, it in enumerate(b["items"], 1):
                    flow.append(Paragraph(f"{i}.\u00a0" + _runs(it), ParagraphStyle(
                        "li2", parent=STYLES["body"], leftIndent=0.75 * cm,
                        firstLineIndent=-0.6 * cm, spaceAfter=3)))
            elif t == "exhead":
                flow.append(H(b["text"], 10.5, NAVY, 12, 4))
            elif t == "corrhead":
                flow.append(H(b["text"], 10.5, AMBER, 12, 4))
            elif t == "qhead":
                flow.append(H(b["text"], 9.5, NAVY_LIGHT, 10, 3))
            elif t == "opts":
                for letter, opt in zip("ABCDEFGH", b["items"]):
                    flow.append(Paragraph(f"<b>{letter})</b>\u00a0" + _runs(opt),
                                           ParagraphStyle("opt", parent=STYLES["body"],
                                                          leftIndent=0.8 * cm,
                                                          firstLineIndent=-0.5 * cm,
                                                          spaceAfter=1)))
            elif t == "code":
                if b.get("caption"):
                    flow.append(Paragraph(escape(b["caption"]), STYLES["codecap"]))
                txt = "<br/>".join(escape(x).replace(" ", "&nbsp;")
                                   for x in code_lines(b["text"]))
                flow.append(Paragraph(txt, ParagraphStyle(
                    "code", fontName="Courier", fontSize=9, leading=11.8,
                    textColor=C(INK), backColor=C(MIST), borderColor=C(AMBER),
                    borderWidth=0, leftIndent=0.25 * cm, spaceBefore=6, spaceAfter=10,
                    borderPadding=(5, 5, 5, 5))))
            elif t == "table":
                if b.get("caption"):
                    tab_c[chapter] = tab_c.get(chapter, 0) + 1
                    flow.append(Paragraph(escape(f"Tableau {chapter}.{tab_c[chapter]} — "
                                                 f"{b['caption']}"), STYLES["caption"]))
                ws = col_widths(b)
                data = [[Paragraph(_runs(str(h)), STYLES["tablehead"]) for h in b["headers"]]]
                for row in b["rows"]:
                    data.append([Paragraph(_runs(str(c)), STYLES["table"]) for c in row])
                tb = Table(data, colWidths=ws, repeatRows=1)
                style = [("BACKGROUND", (0, 0), (-1, 0), C(NAVY)),
                         ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                         ("TOPPADDING", (0, 0), (-1, -1), 3.3),
                         ("BOTTOMPADDING", (0, 0), (-1, -1), 3.3),
                         ("LEFTPADDING", (0, 0), (-1, -1), 5.6),
                         ("RIGHTPADDING", (0, 0), (-1, -1), 5.6),
                         ("LINEBELOW", (0, 1), (-1, -1), 0.5, C("D5DEE6"))]
                for r in range(1, len(data)):
                    if r % 2 == 0:
                        style.append(("BACKGROUND", (0, r), (-1, r), C("F4F7F9")))
                tb.setStyle(TableStyle(style))
                flow.append(tb)
                flow.append(Spacer(1, 6))
            elif t == "fig":
                fig_c[chapter] = fig_c.get(chapter, 0) + 1
                path = make_figure(b, f"prev_c{chapter}_{fig_c[chapter]}")
                flow.append(Spacer(1, 6))
                flow.append(Image(path, width=15.5 * cm, height=b.get("height", 250)))
                flow.append(Paragraph(escape(f"Figure {chapter}.{fig_c[chapter]} — "
                                             f"{b['title']}"), STYLES["caption"]))
            elif t == "box":
                fill, accent = BOX_COLORS.get(b["kind"], (MIST, NAVY))
                inner = [Paragraph(f"<b>{escape(b['title'].upper())}</b>",
                                   ParagraphStyle("bt", fontName="Helvetica", fontSize=9,
                                                  leading=12.5, textColor=C(accent),
                                                  spaceAfter=4))]
                if b.get("text"):
                    inner.append(Paragraph(_runs(b["text"]), ParagraphStyle(
                        "bx", parent=STYLES["body"], fontSize=10.5, leading=15.3,
                        spaceAfter=4)))
                for it in b.get("items") or []:
                    inner.append(Paragraph("•\u00a0" + _runs(it), ParagraphStyle(
                        "bi", parent=STYLES["body"], fontSize=10.5, leading=15.3,
                        leftIndent=0.5 * cm, firstLineIndent=-0.42 * cm, spaceAfter=2)))
                tb = Table([[inner]], colWidths=[TEXT_W_PT])
                tb.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), C(fill)),
                                        ("LINEBEFORE", (0, 0), (0, -1), 3, C(accent)),
                                        ("LEFTPADDING", (0, 0), (-1, -1), 8),
                                        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                                        ("TOPPADDING", (0, 0), (-1, -1), 7),
                                        ("BOTTOMPADDING", (0, 0), (-1, -1), 7)]))
                flow.append(tb)
                flow.append(Spacer(1, 7))
            elif t == "quote":
                flow.append(Paragraph(_runs(b["text"]), STYLES["quote"]))
            elif t == "toc_start":
                pass
            elif t == "toc_entry":
                st = ParagraphStyle("toc", fontName="Helvetica" if b["level"] == 1 else "Times-Roman",
                                    fontSize=11.5 if b["level"] == 1 else 10.5,
                                    leading=17 if b["level"] == 1 else 15.5,
                                    textColor=C(NAVY if b["level"] == 1 else INK),
                                    spaceBefore=9 if b["level"] == 1 else 1,
                                    leftIndent=0 if b["level"] == 1 else 0.5 * cm)
                tb = Table([[Paragraph(escape(b["text"]), st),
                             Paragraph(str(b["page"]), ParagraphStyle("pg", parent=st,
                                                                       alignment=2))]],
                           colWidths=[TEXT_W_PT - 50, 50])
                tb.setStyle(TableStyle([("LEFTPADDING", (0, 0), (-1, -1), 0),
                                        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                                        ("TOPPADDING", (0, 0), (-1, -1), 0),
                                        ("BOTTOMPADDING", (0, 0), (-1, -1), 0)]))
                flow.append(tb)
            elif t == "toc_course":
                st = ParagraphStyle("tocc", fontName="Times-Roman",
                                    fontSize=9.5 if not b.get("bold") else 10,
                                    leading=14, textColor=C(INK if not b.get("bold") else NAVY),
                                    leftIndent=b.get("indent", 0) * cm)
                tb = Table([[Paragraph(escape(b["text"]), st),
                             Paragraph(str(b.get("page", 0)), ParagraphStyle("pg2", parent=st,
                                                                              alignment=2))]],
                           colWidths=[TEXT_W_PT - 40, 40])
                tb.setStyle(TableStyle([("LEFTPADDING", (0, 0), (-1, -1), 0),
                                        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                                        ("TOPPADDING", (0, 0), (-1, -1), 0),
                                        ("BOTTOMPADDING", (0, 0), (-1, -1), 0)]))
                flow.append(tb)
            elif t in ("toc_end", "pb"):
                if t == "pb":
                    add_break()
        return flow

    def build(self):
        class _Doc(BaseDocTemplate):
            def afterFlowable(inner, flowable):      # noqa: N805
                cle = getattr(flowable, "_cle", None)
                if cle:
                    self.marks[cle] = inner.page

        doc = _Doc(self.path, pagesize=A4,
                              leftMargin=2.5 * cm, rightMargin=2.2 * cm,
                              topMargin=2.4 * cm, bottomMargin=2.2 * cm,
                              title=self.title)
        frame = Frame(2.5 * cm, 2.2 * cm, TEXT_W_PT, TEXT_H_PT, id="main",
                      leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
        doc.addPageTemplates([PageTemplate(id="p", frames=[frame],
                                           onPage=lambda c, d: _header_footer(c, d, "", ""))])
        doc.build(self.story())
        return doc.page


def index_marks(path: str, blocks: list[dict]) -> dict[str, int]:
    """Retrouve, dans un PDF d'aperçu, la page de départ de chaque repère.

    Le sommaire général répète les intitulés : la recherche est donc lancée
    après la dernière page du sommaire, puis avancée de façon monotone.
    """
    import re

    import pymupdf

    doc = pymupdf.open(path)
    pages = [re.sub(r"\s+", " ", doc[i].get_text()) for i in range(doc.page_count)]

    start = next(i for i, t in enumerate(pages) if "Sommaire général" in t)
    fin = start
    for i in range(start, min(start + 16, len(pages))):
        if "Annexe D" in pages[i]:
            fin = i

    marks: dict[str, int] = {}
    curseur = fin
    for b in blocks:
        bid = b.get("id")
        if not bid:
            continue
        if b["t"] == "h":
            aiguille = b["text"]
        elif b["t"] == "fullpage":
            aiguille = b.get("title", "")
        else:
            continue
        aiguille = re.sub(r"\s+", " ", aiguille).strip()
        if not aiguille:
            continue
        for i in range(curseur, len(pages)):
            if aiguille in pages[i]:
                marks[bid] = i + 1
                curseur = i
                break
    return marks
