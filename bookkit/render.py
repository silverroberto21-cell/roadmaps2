"""Rendu Word : document unique, styles natifs, champs automatiques."""
from __future__ import annotations

from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.enum.text import (WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT, WD_TAB_LEADER,
                            WD_BREAK)
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor, Emu

from . import figures
from .layout import code_lines, col_widths
from .metrics import segments
from .units import (
    S, TEXT_W_PT, NAVY, NAVY_LIGHT, AMBER, SAND, INK, GREY, MIST, WHITE,
    GREEN, RED, PALE_GREEN, PALE_RED, PALE_BLUE,
    MARGIN_TOP_CM, MARGIN_BOTTOM_CM, MARGIN_LEFT_CM, MARGIN_RIGHT_CM,
    PAGE_W_CM, PAGE_H_CM, HEADER_CM, FOOTER_CM, CM,
    TABLE_CELL_PAD_V, TABLE_CELL_PAD_H, BOX_PAD_V, BOX_PAD_H,
)

BOX_COLORS = {
    "objectifs": (SAND, AMBER),
    "retenir": (PALE_GREEN, GREEN),
    "attention": (PALE_RED, RED),
    "pratique": (PALE_BLUE, NAVY_LIGHT),
    "definition": (MIST, NAVY),
    "note": (MIST, GREY),
    "methode": (SAND, AMBER),
}


def _rgb(hexstr: str) -> RGBColor:
    return RGBColor.from_string(hexstr)


def _sub(tag: str, **attrs):
    el = OxmlElement(tag)
    for k, v in attrs.items():
        el.set(qn("w:" + k), str(v))
    return el


# --------------------------------------------------------------------------- #
# Styles
# --------------------------------------------------------------------------- #
def _set_fonts(style, family: str) -> None:
    rpr = style.element.get_or_add_rPr()
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = _sub("w:rFonts")
        rpr.append(rfonts)
    for a in ("ascii", "hAnsi", "cs", "eastAsia"):
        rfonts.set(qn("w:" + a), family)


def _set_lang(style, lang: str = "fr-FR") -> None:
    rpr = style.element.get_or_add_rPr()
    el = _sub("w:lang", val=lang, eastAsia=lang, bidi="ar-SA")
    rpr.append(el)


def _set_outline(style, level: int) -> None:
    ppr = style.element.get_or_add_pPr()
    el = ppr.find(qn("w:outlineLvl"))
    if el is None:
        el = _sub("w:outlineLvl")
        ppr.append(el)
    el.set(qn("w:val"), str(level))


def _style_id(style, sid: str) -> None:
    style.element.set(qn("w:styleId"), sid)


def build_styles(doc: Document) -> None:
    st = doc.styles

    normal = st["Normal"]
    normal.font.name = "Times New Roman"
    normal.font.size = Pt(11.5)
    normal.font.color.rgb = _rgb(INK)
    _set_fonts(normal, "Times New Roman")
    _set_lang(normal)
    pf = normal.paragraph_format
    pf.line_spacing = Pt(S["body"]["line"])
    pf.space_before = Pt(0)
    pf.space_after = Pt(7.5)
    pf.widow_control = False
    pf.keep_together = False

    specs = {
        "Heading 1": ("h1", True, False),
        "Heading 2": ("h1", True, False),
        "Heading 3": ("h2", True, False),
        "Heading 4": ("h3", True, False),
    }
    for name, (key, bold, italic) in specs.items():
        style = st[name]
        spec = S[key]
        style.font.name = spec["font"]
        style.font.size = Pt(spec["size"])
        style.font.bold = bold
        style.font.italic = italic
        style.font.color.rgb = _rgb(NAVY if name != "Heading 3" else NAVY_LIGHT)
        _set_fonts(style, spec["font"])
        _set_lang(style)
        pf = style.paragraph_format
        pf.line_spacing = Pt(spec["line"])
        pf.space_before = Pt(spec["before"])
        pf.space_after = Pt(spec["after"])
        pf.keep_with_next = True
        pf.widow_control = False
        pf.keep_together = True


    # Sur-titres et titres hors sommaire
    def add(name, sid, size, color, bold=True, italic=False, before=0, after=6,
            font="Arial", keep=False, outline=None, base="Normal"):
        s = st.add_style(name, WD_STYLE_TYPE.PARAGRAPH)
        s.base_style = st[base]
        s.font.name = font
        s.font.size = Pt(size)
        s.font.bold = bold
        s.font.italic = italic
        s.font.color.rgb = _rgb(color)
        _set_fonts(s, font)
        _set_lang(s)
        pf = s.paragraph_format
        pf.space_before = Pt(before)
        pf.space_after = Pt(after)
        pf.line_spacing = Pt(round(size * 1.35, 1))
        pf.keep_with_next = keep
        if outline is not None:
            _set_outline(s, outline)
        _style_id(s, sid)
        return s

    add("Titre de cours", "TitreCours", 27, NAVY, before=0, after=10, font="Arial",
        keep=True, outline=0)
    add("Titre de partie", "TitrePartie", 26, WHITE, before=0, after=10, font="Arial",
        outline=0)
    add("Titre d'annexe", "TitreAnnexe", 24, NAVY, before=0, after=10, font="Arial",
        keep=True, outline=0)
    add("Titre hors sommaire", "TitreHorsSommaire", 18, NAVY, before=0, after=12,
        font="Arial", keep=True)
    add("Titre de rubrique", "TitreRubrique", 13, NAVY_LIGHT, before=18, after=7,
        font="Arial", keep=True, outline=3)
    add("Sur-titre", "SurTitre", 8.5, AMBER, before=0, after=4, font="Arial")
    add("Métadonnées", "Metadonnees", 8.5, GREY, before=0, after=6, font="Arial",
        bold=False)
    add("TOC cours", "TOCCours", 9.5, INK, before=0, after=1.5, font="Times New Roman",
        bold=False)
    add("TOC cours partie", "TOCCoursPartie", 9.5, NAVY, before=8, after=2,
        font="Arial", bold=True)
    add("Réponse quiz", "ReponseQuiz", 9.5, INK, before=0, after=4,
        font="Times New Roman", bold=False)

    code = st.add_style("Code", WD_STYLE_TYPE.PARAGRAPH)
    code.base_style = st["Normal"]
    code.font.name = "Courier New"
    code.font.size = Pt(S["code"]["size"])
    code.font.color.rgb = _rgb(INK)
    _set_fonts(code, "Courier New")
    _set_lang(code)
    pf = code.paragraph_format
    pf.line_spacing = Pt(S["code"]["line"])
    pf.space_before = Pt(S["code"]["before"])
    pf.space_after = Pt(S["code"]["after"])
    pf.left_indent = Cm(0.25)
    pf.right_indent = Cm(0.05)
    pf.keep_together = True
    pf.widow_control = False

    add("Exercice", "Exercice", 10.5, NAVY, before=14, after=4, font="Arial", keep=True)
    add("Question", "Question", 9.5, NAVY_LIGHT, before=12, after=3, font="Arial", keep=True)
    add("Corrigé", "Corrige", 10.5, AMBER, before=12, after=4, font="Arial", keep=True)
    add("Option", "Option", 10.5, INK, before=0, after=2, font="Times New Roman", bold=False)
    add("Légende", "Legende", 8.5, GREY, before=3, after=10, font="Arial",
        bold=False, italic=True)
    add("Légende de code", "LegendeCode", 8, NAVY_LIGHT, before=0, after=4,
        font="Arial", bold=True)
    add("Note de figure", "NoteFigure", 7.5, GREY, before=0, after=8, font="Arial",
        bold=False, italic=True)
    add("Source", "Source", 8, GREY, before=2, after=8, font="Arial", bold=False,
        italic=True)

    # Styles de table des matières (identifiants natifs Word TOC1..TOC3)
    for lvl in (1, 2, 3):
        name = f"toc {lvl}"
        s = st.add_style(name, WD_STYLE_TYPE.PARAGRAPH)
        s.base_style = st["Normal"]
        spec = S[f"toc{lvl}"]
        s.font.name = spec["font"]
        s.font.size = Pt(spec["size"])
        s.font.bold = lvl == 1
        s.font.color.rgb = _rgb(NAVY if lvl == 1 else INK)
        _set_fonts(s, spec["font"])
        _set_lang(s)
        pf = s.paragraph_format
        pf.line_spacing = Pt(spec["line"])
        pf.space_before = Pt(spec["before"])
        pf.space_after = Pt(spec["after"])
        pf.left_indent = Cm(0.0 if lvl == 1 else (0.5 if lvl == 2 else 1.1))
        pf.widow_control = False
        _style_id(s, f"TOC{lvl}")

    # Style de corps « Encadré »
    body = st["Normal"]
    return body


# --------------------------------------------------------------------------- #
# Helpers XML
# --------------------------------------------------------------------------- #
PPR_SEQ = ["w:pStyle","w:keepNext","w:keepLines","w:pageBreakBefore","w:framePr","w:widowControl",
           "w:numPr","w:suppressLineNumbers","w:pBdr","w:shd","w:tabs","w:suppressAutoHyphens",
           "w:kinsoku","w:wordWrap","w:overflowPunct","w:topLinePunct","w:autoSpaceDE",
           "w:autoSpaceDN","w:bidi","w:adjustRightInd","w:snapToGrid","w:spacing","w:ind",
           "w:contextualSpacing","w:mirrorIndents","w:suppressOverlap","w:jc","w:textDirection",
           "w:textAlignment","w:textboxTightWrap","w:outlineLvl","w:divId","w:cnfStyle",
           "w:rPr","w:sectPr","w:pPrChange"]
TCPR_SEQ = ["w:cnfStyle","w:tcW","w:gridSpan","w:hMerge","w:vMerge","w:tcBorders","w:shd",
            "w:noWrap","w:tcMar","w:textDirection","w:tcFitText","w:vAlign","w:hideMark",
            "w:headers","w:cellIns","w:cellDel","w:cellMerge","w:tcPrChange"]
TBLPR_SEQ = ["w:tblStyle","w:tblpPr","w:tblOverlap","w:bidiVisual","w:tblStyleRowBandSize",
             "w:tblStyleColBandSize","w:tblW","w:jc","w:tblCellSpacing","w:tblInd","w:tblBorders",
             "w:shd","w:tblLayout","w:tblCellMar","w:tblLook","w:tblCaption","w:tblDescription",
             "w:tblPrChange"]
TRPR_SEQ = ["w:cnfStyle","w:divId","w:gridBefore","w:gridAfter","w:wBefore","w:wAfter",
            "w:cantSplit","w:trHeight","w:tblHeader","w:tblCellSpacing","w:jc","w:hidden",
            "w:ins","w:del","w:trPrChange"]
PBDR_SEQ = ["w:top","w:left","w:bottom","w:right","w:between","w:bar"]


def insert_ordered(parent, el, seq):
    names = [qn(t) for t in seq]
    try:
        idx = names.index(el.tag)
    except ValueError:
        parent.append(el)
        return el
    for child in list(parent):
        if child.tag in names and names.index(child.tag) > idx:
            child.addprevious(el)
            return el
    parent.append(el)
    return el


def _get_or_make(parent, tag, seq):
    el = parent.find(qn(tag))
    if el is None:
        el = insert_ordered(parent, OxmlElement(tag), seq)
    return el


def shade_par(par, fill: str) -> None:
    ppr = par._p.get_or_add_pPr()
    shd = _get_or_make(ppr, "w:shd", PPR_SEQ)
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), fill)


def border_par(par, left=None, bottom=None, top=None, right=None, space=4) -> None:
    ppr = par._p.get_or_add_pPr()
    pbdr = _get_or_make(ppr, "w:pBdr", PPR_SEQ)
    for side, spec in (("top", top), ("left", left), ("bottom", bottom), ("right", right)):
        if spec:
            color, sz = spec
            el = pbdr.find(qn(f"w:{side}"))
            if el is None:
                el = insert_ordered(pbdr, OxmlElement(f"w:{side}"), PBDR_SEQ)
            el.set(qn("w:val"), "single")
            el.set(qn("w:sz"), str(int(sz * 8)))
            el.set(qn("w:space"), str(space))
            el.set(qn("w:color"), color)


def cell_shade(cell, fill: str) -> None:
    tcpr = cell._tc.get_or_add_tcPr()
    shd = _get_or_make(tcpr, "w:shd", TCPR_SEQ)
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), fill)


def cell_margins(cell, top=3.3, bottom=3.3, left=5.6, right=5.6) -> None:
    tcpr = cell._tc.get_or_add_tcPr()
    mar = _get_or_make(tcpr, "w:tcMar", TCPR_SEQ)
    for side, val in (("top", top), ("left", left), ("bottom", bottom), ("right", right)):
        el = mar.find(qn(f"w:{side}"))
        if el is None:
            el = OxmlElement(f"w:{side}")
            mar.append(el)
        el.set(qn("w:w"), str(int(val * 20)))
        el.set(qn("w:type"), "dxa")


def table_borders(table, color="D5DEE6", size=0.5, inside=True, outside=False) -> None:
    tblpr = table._tbl.tblPr
    borders = _get_or_make(tblpr, "w:tblBorders", TBLPR_SEQ)
    for child in list(borders):
        borders.remove(child)
    edges = ["top", "left", "bottom", "right"]
    for e in edges:
        borders.append(_sub(f"w:{e}", val="single" if outside else "nil",
                            sz=str(int(size * 8)), space="0", color=color))
    for e in ["insideH", "insideV"]:
        borders.append(_sub(f"w:{e}", val="single" if inside else "nil",
                            sz=str(int(size * 8)), space="0", color=color))


def row_cant_split(row) -> None:
    trpr = row._tr.get_or_add_trPr()
    el = _get_or_make(trpr, "w:cantSplit", TRPR_SEQ)
    el.set(qn("w:val"), "true")


def row_header(row) -> None:
    trpr = row._tr.get_or_add_trPr()
    el = _get_or_make(trpr, "w:tblHeader", TRPR_SEQ)
    el.set(qn("w:val"), "true")


def row_height(row, cm: float) -> None:
    row.height = Cm(cm)
    trpr = row._tr.get_or_add_trPr()
    tr = trpr.find(qn("w:trHeight"))
    if tr is not None:
        tr.set(qn("w:hRule"), "exact")


def anchor_picture(par, path: str, w_cm: float, h_cm: float) -> None:
    """Insère une image flottante pleine page, positionnée à l'origine de la page."""
    from docx.oxml import parse_xml
    from docx.oxml.ns import nsdecls
    run = par.add_run()
    run.add_picture(path, width=Cm(w_cm), height=Cm(h_cm))
    drawing = run._element.find(qn("w:drawing"))
    inline = drawing.find(qn("wp:inline"))
    cx, cy = int(Cm(w_cm)), int(Cm(h_cm))
    docpr_id = inline.find(qn("wp:docPr")).get("id")
    graphic = inline.find(qn("a:graphic"))
    anchor = parse_xml(
        '<wp:anchor %s distT="0" distB="0" distL="0" distR="0" simplePos="0" '
        'relativeHeight="0" behindDoc="1" locked="0" layoutInCell="1" allowOverlap="1">'
        '<wp:simplePos x="0" y="0"/>'
        '<wp:positionH relativeFrom="page"><wp:posOffset>0</wp:posOffset></wp:positionH>'
        '<wp:positionV relativeFrom="page"><wp:posOffset>0</wp:posOffset></wp:positionV>'
        '<wp:extent cx="%d" cy="%d"/>'
        '<wp:effectExtent l="0" t="0" r="0" b="0"/>'
        '<wp:wrapNone/>'
        '<wp:docPr id="%s" name="Couverture"/>'
        '</wp:anchor>' % (nsdecls("wp", "a"), cx, cy, docpr_id))
    anchor.append(graphic)
    drawing.remove(inline)
    drawing.append(anchor)


def char_spacing(run, twips: int) -> None:
    rpr = run._element.get_or_add_rPr()
    el = OxmlElement("w:spacing")
    el.set(qn("w:val"), str(twips))
    rpr.append(el)


def add_field(par, instr: str, cached: str = "") -> None:
    r1 = par.add_run()
    r1._element.append(_sub("w:fldChar", fldCharType="begin"))
    r2 = par.add_run()
    it = _sub("w:instrText", space="preserve")
    it.text = f" {instr} "
    r2._element.append(it)
    r3 = par.add_run()
    r3._element.append(_sub("w:fldChar", fldCharType="separate"))
    r4 = par.add_run(cached)
    r5 = par.add_run()
    r5._element.append(_sub("w:fldChar", fldCharType="end"))


# --------------------------------------------------------------------------- #
# Renderer
# --------------------------------------------------------------------------- #
class Renderer:
    def __init__(self, meta: dict):
        self.meta = meta
        self.doc = Document()
        self.fig_counters: dict[int, int] = {}
        self.tab_counters: dict[int, int] = {}
        self.lst_counters: dict[int, int] = {}
        self.chapter = 0
        self._setup_document()
        build_styles(self.doc)

    # ---------------- document ----------------
    def _setup_document(self) -> None:
        d = self.doc
        cp = d.core_properties
        cp.title = self.meta["title"]
        cp.author = self.meta["author"]
        cp.subject = self.meta["subject"]
        cp.category = "Manuel technique"
        cp.comments = self.meta["comments"]
        cp.keywords = self.meta["keywords"]
        cp.language = "fr-FR"
        cp.last_modified_by = self.meta["author"]

        s = d.sections[0]
        s.page_width = Cm(PAGE_W_CM)
        s.page_height = Cm(PAGE_H_CM)
        s.top_margin = Cm(0)
        s.bottom_margin = Cm(0)
        s.left_margin = Cm(0)
        s.right_margin = Cm(0)
        s.header_distance = Cm(0)
        s.footer_distance = Cm(0)
        s.different_first_page_header_footer = False

    def _margins(self, sec) -> None:
        sec.page_width = Cm(PAGE_W_CM)
        sec.page_height = Cm(PAGE_H_CM)
        sec.top_margin = Cm(MARGIN_TOP_CM)
        sec.bottom_margin = Cm(MARGIN_BOTTOM_CM)
        sec.left_margin = Cm(MARGIN_LEFT_CM)
        sec.right_margin = Cm(MARGIN_RIGHT_CM)
        sec.header_distance = Cm(HEADER_CM)
        sec.footer_distance = Cm(FOOTER_CM)

    def cover(self, image: str) -> None:
        p = self.doc.add_paragraph()
        pf = p.paragraph_format
        pf.space_before = Pt(0)
        pf.space_after = Pt(0)
        pf.line_spacing = Pt(12)
        pf.widow_control = False
        anchor_picture(p, image, 21.0, 29.7)

    def new_section(self, header_left: str, header_right: str, first_blank: bool = True,
                    footer: bool = True) -> None:
        sec = self.doc.add_section(WD_SECTION.NEW_PAGE)
        self._margins(sec)
        sec.different_first_page_header_footer = first_blank
        sec.header.is_linked_to_previous = False
        sec.footer.is_linked_to_previous = False

        hp = sec.header.paragraphs[0]
        hp.text = ""
        hp.paragraph_format.space_after = Pt(4)
        hp.paragraph_format.tab_stops.add_tab_stop(
            Cm(PAGE_W_CM - MARGIN_LEFT_CM - MARGIN_RIGHT_CM), WD_TAB_ALIGNMENT.RIGHT)
        r = hp.add_run(header_left)
        r.font.name = "Arial"; r.font.size = Pt(7.6); r.font.color.rgb = _rgb(GREY)
        r.font.all_caps = True
        r = hp.add_run("\t" + header_right)
        r.font.name = "Arial"; r.font.size = Pt(7.6); r.font.color.rgb = _rgb(GREY)
        border_par(hp, bottom=(AMBER, 0.75), space=3)

        fp = sec.footer.paragraphs[0]
        fp.text = ""
        fp.paragraph_format.tab_stops.add_tab_stop(
            Cm(PAGE_W_CM - MARGIN_LEFT_CM - MARGIN_RIGHT_CM), WD_TAB_ALIGNMENT.RIGHT)
        r = fp.add_run("ESPRITROPIC COMMUNITY · Bibliothèque technique")
        r.font.name = "Arial"; r.font.size = Pt(7.2); r.font.color.rgb = _rgb(GREY)
        r = fp.add_run("\tPage ")
        r.font.name = "Arial"; r.font.size = Pt(8); r.font.color.rgb = _rgb(GREY)
        add_field(fp, "PAGE", "1")
        for r in fp.runs:
            if r.font.size is None:
                r.font.name = "Arial"; r.font.size = Pt(8)
                r.font.color.rgb = _rgb(NAVY)

    # ---------------- runs ----------------
    def runs(self, par, text: str, family: str = "Times New Roman", size: float = 11,
             bold: bool = False, italic: bool = False, color: str = INK) -> None:
        for chunk, style in segments(text):
            r = par.add_run(chunk)
            if style == "c":
                r.font.name = "Courier New"
                r.font.size = Pt(size * 0.9)
                r.font.color.rgb = _rgb(NAVY_LIGHT)
            else:
                r.font.name = family
                r.font.size = Pt(size)
                r.font.color.rgb = _rgb(color)
                if style in ("b", "u"):
                    r.font.bold = True
                if style == "i":
                    r.font.italic = True
                if style == "u":
                    r.font.underline = True
                if bold:
                    r.font.bold = True
                if italic:
                    r.font.italic = True

    # ---------------- blocs ----------------
    def heading_runs(self, par, text: str) -> None:
        for chunk, style in segments(text):
            r = par.add_run(chunk)
            if style == "c":
                r.font.name = "Courier New"
                r.font.color.rgb = _rgb(NAVY_LIGHT)
            if style in ("b", "u"):
                r.font.bold = True
            if style == "i":
                r.font.italic = True

    def block(self, b: dict) -> None:
        t = b["t"]
        if t == "p":
            self.paragraph(b["text"], b.get("style", "body"))
        elif t == "h":
            if b.get("eyebrow"):
                eb = self.doc.add_paragraph(style="Sur-titre")
                r0 = eb.add_run(b["eyebrow"])
                r0.font.name = "Arial"; r0.font.size = Pt(9); r0.font.bold = True
                r0.font.color.rgb = _rgb(AMBER)
                char_spacing(r0, 60)
            par = self.doc.add_paragraph(style=b.get("style") or f"Heading {min(b['level'], 4)}")
            if b.get("page_break"):
                par.paragraph_format.page_break_before = True
            self.heading_runs(par, b["text"])
        elif t == "ul":
            for it in b["items"]:
                self.list_item(it, bullet=True)
        elif t == "ol":
            for i, it in enumerate(b["items"], 1):
                self.list_item(it, bullet=False, num=i)
        elif t == "code":
            self.code(b)
        elif t == "table":
            self.table(b)
        elif t == "fig":
            self.figure(b)
        elif t == "box":
            self.box(b)
        elif t == "quote":
            self.quote(b)
        elif t == "exhead":
            par = self.doc.add_paragraph(style="Exercice")
            self.runs(par, b["text"], family="Arial", size=10.5, bold=True, color=NAVY)
            if b.get("tag"):
                r = par.add_run("   " + b["tag"].upper())
                r.font.name = "Arial"; r.font.size = Pt(7.5); r.font.bold = True
                r.font.color.rgb = _rgb(AMBER)
        elif t == "corrhead":
            par = self.doc.add_paragraph(style="Corrigé")
            self.runs(par, b["text"], family="Arial", size=10.5, bold=True, color=AMBER)
        elif t == "qhead":
            par = self.doc.add_paragraph(style="Question")
            self.runs(par, b["text"], family="Arial", size=9.5, bold=True, color=NAVY_LIGHT)
        elif t == "opts":
            for letter, opt in zip("ABCDEFGH", b["items"]):
                par = self.doc.add_paragraph(style="Option")
                pf = par.paragraph_format
                pf.left_indent = Cm(0.8); pf.first_line_indent = Cm(-0.5)
                pf.space_before = Pt(0); pf.space_after = Pt(1)
                r = par.add_run(letter + ")\u00a0")
                r.font.name = "Arial"; r.font.size = Pt(9); r.font.bold = True
                r.font.color.rgb = _rgb(GREY)
                self.runs(par, opt, size=10.5)
        elif t == "toc_start":
            par = self.doc.add_paragraph()
            r = par.add_run()
            r._element.append(_sub("w:fldChar", fldCharType="begin"))
            it = _sub("w:instrText", space="preserve")
            it.text = ' TOC \\o "1-2" \\t "Titre de partie,1" \\z \\u '
            r._element.append(it)
            r = par.add_run()
            r._element.append(_sub("w:fldChar", fldCharType="separate"))
            par.paragraph_format.space_after = Pt(0)
            par.paragraph_format.line_spacing = Pt(1)
        elif t == "toc_entry":
            lvl = b["level"]
            par = self.doc.add_paragraph(style=f"toc {lvl}")
            par.paragraph_format.tab_stops.add_tab_stop(
                Cm(16.3), WD_TAB_ALIGNMENT.RIGHT, WD_TAB_LEADER.DOTS)
            self.runs(par, b["text"], family="Arial" if lvl == 1 else "Times New Roman",
                      size=S[f"toc{lvl}"]["size"], bold=(lvl == 1),
                      color=NAVY if lvl == 1 else INK)
            r = par.add_run("\t" + str(b["page"]))
            r.font.name = "Arial" if lvl == 1 else "Times New Roman"
            r.font.size = Pt(S[f"toc{lvl}"]["size"])
            r.font.color.rgb = _rgb(NAVY if lvl == 1 else GREY)
            self._last_toc = par
        elif t == "toc_end":
            par = getattr(self, "_last_toc", None)
            if par is not None:
                end = par.add_run()
                end._element.append(_sub("w:fldChar", fldCharType="end"))
        elif t == "logo":
            par = self.doc.add_paragraph()
            pf = par.paragraph_format
            pf.space_before = Pt(0); pf.space_after = Pt(10)
            pf.line_spacing = Pt(b.get("width", 3.2) * 28.35 * 905 / 943 + 4)
            if b.get("align") == "left":
                par.alignment = WD_ALIGN_PARAGRAPH.LEFT
            run = par.add_run()
            run.add_picture(b["path"], width=Cm(b.get("width", 3.2)))
        elif t == "vspace":
            par = self.doc.add_paragraph()
            pf = par.paragraph_format
            pf.space_before = Pt(0); pf.space_after = Pt(0)
            pf.line_spacing = Pt(max(b.get("h", 12), 1))
        elif t == "bigtitle":
            lines = b["text"].split("\n")
            for i, line in enumerate(lines):
                par = self.doc.add_paragraph()
                pf = par.paragraph_format
                pf.space_before = Pt(0); pf.space_after = Pt(0)
                pf.line_spacing = Pt(46)
                r0 = par.add_run(line)
                r0.font.name = "Arial"; r0.font.size = Pt(40); r0.font.bold = True
                r0.font.color.rgb = _rgb(NAVY)
        elif t == "smallcaps":
            par = self.doc.add_paragraph()
            par.paragraph_format.space_before = Pt(2)
            par.paragraph_format.space_after = Pt(10)
            r0 = par.add_run(b["text"])
            r0.font.name = "Arial"; r0.font.size = Pt(9.5); r0.font.bold = True
            r0.font.color.rgb = _rgb(GREY)
            char_spacing(r0, 60)
        elif t == "rule":
            par = self.doc.add_paragraph()
            par.paragraph_format.space_before = Pt(0)
            par.paragraph_format.space_after = Pt(8)
            border_par(par, bottom=(AMBER, 1.5), space=2)
        elif t == "rubric":
            style = b.get("style") or "Titre de rubrique"
            par = self.doc.add_paragraph(style=style)
            if style == "Titre hors sommaire":
                par.paragraph_format.space_after = Pt(12)
                self.runs(par, b["text"], family="Arial", size=18, bold=True, color=NAVY)
            else:
                self.runs(par, b["text"], family="Arial", size=13, bold=True,
                          color=NAVY_LIGHT)
        elif t == "toc_course":
            par = self.doc.add_paragraph(style="TOC cours")
            pf = par.paragraph_format
            pf.left_indent = Cm(b.get("indent", 0.0))
            pf.tab_stops.add_tab_stop(Cm(16.3), WD_TAB_ALIGNMENT.RIGHT, WD_TAB_LEADER.DOTS)
            self.runs(par, b["text"], size=9.5, bold=b.get("bold", False),
                      color=NAVY if b.get("bold") else INK)
            r = par.add_run("\t" + str(b.get("page", 0)))
            r.font.name = "Times New Roman"; r.font.size = Pt(9.5)
            r.font.color.rgb = _rgb(GREY)
        elif t == "section":
            self.new_section(b["header_left"], b["header_right"],
                             first_blank=b.get("first_blank", True))
        elif t == "pb":
            self.doc.add_page_break()
        elif t == "fullpage":
            self.part_page(b)
        else:
            raise ValueError(t)

    def paragraph(self, text: str, style: str = "body") -> None:
        spec = S.get(style, S["body"])
        par = self.doc.add_paragraph()
        pf = par.paragraph_format
        pf.space_before = Pt(spec["before"])
        pf.space_after = Pt(spec["after"])
        pf.line_spacing = Pt(spec["line"])
        pf.widow_control = False
        pf.keep_together = True
        if style == "lead":
            self.runs(par, text, size=12, italic=True, color=NAVY_LIGHT)
        elif style == "small":
            self.runs(par, text, family="Arial", size=8.5, color=GREY)
        else:
            self.runs(par, text)

    def heading(self, level: int, text: str, bid: str | None = None) -> None:
        if level == 2:
            import re
            m = re.match(r"(\d+)\.", text)
            if m:
                self.chapter = int(m.group(1))
        par = self.doc.add_paragraph(style=f"Heading {min(level, 4)}")
        if level == 2:
            # numéro de chapitre en ambre
            if ". " in text:
                num, rest = text.split(". ", 1)
                r = par.add_run(num + ".")
                r.font.name = "Arial"
                r.font.size = Pt(22)
                r.font.bold = True
                r.font.color.rgb = _rgb(AMBER)
                r = par.add_run("\u00a0" + rest)
                r.font.name = "Arial"
                r.font.size = Pt(22)
                r.font.bold = True
                r.font.color.rgb = _rgb(NAVY)
                return
        self.runs(par, text, family="Arial",
                  size=S["h1"]["size"] if level == 1 else S[f"h{level}"]["size"],
                  bold=True, color=NAVY if level < 3 else NAVY_LIGHT)

    def list_item(self, text: str, bullet: bool, num: int | None = None) -> None:
        par = self.doc.add_paragraph()
        pf = par.paragraph_format
        pf.left_indent = Cm(0.55 if bullet else 0.75)
        pf.first_line_indent = Cm(-0.45 if bullet else -0.6)
        pf.space_before = Pt(0)
        pf.space_after = Pt(3)
        pf.line_spacing = Pt(17.4)
        pf.widow_control = False
        pf.keep_together = True
        if bullet:
            r = par.add_run("\u2022\u00a0")
            r.font.name = "Times New Roman"
            r.font.size = Pt(11.5)
            r.font.color.rgb = _rgb(AMBER)
            r.font.bold = True
        else:
            r = par.add_run(f"{num}.\t")
            r.font.name = "Times New Roman"
            r.font.size = Pt(11.5)
            r.font.color.rgb = _rgb(NAVY)
            r.font.bold = True
            pf.tab_stops.add_tab_stop(Cm(0.75), WD_TAB_ALIGNMENT.LEFT)
        self.runs(par, text)

    def code(self, b: dict) -> None:
        if b.get("caption"):
            cap = self.doc.add_paragraph(style="Légende de code")
            cap.paragraph_format.keep_with_next = True
            lang = f" · {b['lang']}" if b.get("lang") else ""
            r = cap.add_run(b["caption"] + lang)
            r.font.name = "Arial"; r.font.size = Pt(8); r.font.bold = True
            r.font.color.rgb = _rgb(NAVY_LIGHT)
        par = self.doc.add_paragraph(style="Code")
        shade_par(par, MIST)
        border_par(par, left=(AMBER, 2.25), top=(MIST, 0.5), bottom=(MIST, 0.5),
                   right=(MIST, 0.5), space=5)
        text = "\n".join(code_lines(b["text"]))
        r = par.add_run(text)
        r.font.name = "Courier New"
        r.font.size = Pt(9.2)
        r.font.color.rgb = _rgb(INK)

    def table(self, b: dict) -> None:
        ch = self.chapter
        cap_txt = None
        if b.get("caption"):
            self.tab_counters[ch] = self.tab_counters.get(ch, 0) + 1
            cap_txt = f"Tableau {ch}.{self.tab_counters[ch]} — {b['caption']}"
            cap = self.doc.add_paragraph(style="Légende")
            cap.paragraph_format.keep_with_next = True
            self.runs(cap, cap_txt, family="Arial", size=8.5, italic=True, color=GREY)
        headers = b["headers"]
        rows = b["rows"]
        ws = col_widths(b)
        table = self.doc.add_table(rows=1, cols=len(headers))
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        table.autofit = False
        tblpr = table._tbl.tblPr
        layout = _sub("w:tblLayout", type="fixed")
        tblpr.append(layout)
        table_borders(table, color="D5DEE6", size=0.5, inside=True, outside=False)
        hdr = table.rows[0]
        row_header(hdr)
        row_cant_split(hdr)
        for i, htxt in enumerate(headers):
            cell = hdr.cells[i]
            cell.width = Emu(int(ws[i] * 12700))
            cell_shade(cell, NAVY)
            cell_margins(cell, TABLE_CELL_PAD_V, TABLE_CELL_PAD_V,
                         TABLE_CELL_PAD_H, TABLE_CELL_PAD_H)
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            par = cell.paragraphs[0]
            par.paragraph_format.space_before = Pt(0)
            par.paragraph_format.space_after = Pt(0)
            par.paragraph_format.line_spacing = Pt(12.5)
            self.runs(par, htxt, family="Arial", size=9, bold=True, color=WHITE)
        for ri, row in enumerate(rows):
            tr = table.add_row()
            row_cant_split(tr)
            for ci, val in enumerate(row):
                cell = tr.cells[ci]
                cell.width = Emu(int(ws[ci] * 12700))
                if ri % 2 == 1:
                    cell_shade(cell, "F4F7F9")
                cell_margins(cell, TABLE_CELL_PAD_V, TABLE_CELL_PAD_V,
                             TABLE_CELL_PAD_H, TABLE_CELL_PAD_H)
                cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
                par = cell.paragraphs[0]
                par.paragraph_format.space_before = Pt(0)
                par.paragraph_format.space_after = Pt(0)
                par.paragraph_format.line_spacing = Pt(13)
                bold = b.get("first_col_bold") and ci == 0
                self.runs(par, str(val), family="Arial", size=9.5, bold=bold,
                          color=NAVY if bold else INK)
        sp = self.doc.add_paragraph()
        sp.paragraph_format.space_before = Pt(0)
        sp.paragraph_format.space_after = Pt(0)
        sp.paragraph_format.line_spacing = Pt(4)

    def figure(self, b: dict) -> None:
        ch = self.chapter
        self.fig_counters[ch] = self.fig_counters.get(ch, 0) + 1
        num = self.fig_counters[ch]
        name = f"c{ch:02d}_f{num:02d}"
        path = figures.make_figure(b, name)
        par = self.doc.add_paragraph()
        par.alignment = WD_ALIGN_PARAGRAPH.CENTER
        pf = par.paragraph_format
        pf.space_before = Pt(6)
        pf.space_after = Pt(0)
        pf.line_spacing = Pt(1)
        pf.keep_with_next = True
        pf.keep_together = True
        run = par.add_run()
        run.add_picture(path, width=Cm(15.5), height=Pt(b.get("height", 250)))
        cap = self.doc.add_paragraph(style="Légende")
        self.runs(cap, f"Figure {ch}.{num} — {b['title']}", family="Arial",
                  size=8.5, italic=True, color=GREY)
        if b.get("note"):
            note = self.doc.add_paragraph(style="Note de figure")
            self.runs(note, b["note"], family="Arial", size=7.5, italic=True, color=GREY)

    def box(self, b: dict) -> None:
        fill, accent = BOX_COLORS.get(b["kind"], (MIST, NAVY))
        table = self.doc.add_table(rows=1, cols=1)
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        table.autofit = False
        cell = table.rows[0].cells[0]
        cell.width = Emu(int(462 * 12700))
        cell_shade(cell, fill)
        cell_margins(cell, BOX_PAD_V, BOX_PAD_V, BOX_PAD_H, BOX_PAD_H)
        tblpr = table._tbl.tblPr
        borders = _sub("w:tblBorders")
        borders.append(_sub("w:left", val="single", sz="24", space="0", color=accent))
        for side in ("top", "bottom", "right", "insideH", "insideV"):
            borders.append(_sub(f"w:{side}", val="nil", sz="0", space="0", color="auto"))
        tblpr.append(borders)
        p0 = cell.paragraphs[0]
        p0.paragraph_format.space_before = Pt(0)
        p0.paragraph_format.space_after = Pt(4)
        p0.paragraph_format.line_spacing = Pt(12.5)
        p0.paragraph_format.keep_with_next = True
        r = p0.add_run(b["title"].upper())
        r.font.name = "Arial"; r.font.size = Pt(9); r.font.bold = True
        r.font.color.rgb = _rgb(accent)
        char_spacing(r, 12)
        if b.get("text"):
            par = cell.add_paragraph()
            par.paragraph_format.space_before = Pt(0)
            par.paragraph_format.space_after = Pt(5)
            par.paragraph_format.line_spacing = Pt(15.8)
            self.runs(par, b["text"], size=10.5)
        for it in b.get("items") or []:
            par = cell.add_paragraph()
            par.paragraph_format.left_indent = Cm(0.5)
            par.paragraph_format.first_line_indent = Cm(-0.42)
            par.paragraph_format.space_before = Pt(0)
            par.paragraph_format.space_after = Pt(2)
            par.paragraph_format.line_spacing = Pt(15.8)
            r = par.add_run("\u2022\u00a0")
            r.font.name = "Times New Roman"; r.font.size = Pt(10.5)
            r.font.color.rgb = _rgb(accent); r.font.bold = True
            self.runs(par, it, size=10.5)
        sp = self.doc.add_paragraph()
        sp.paragraph_format.space_before = Pt(0)
        sp.paragraph_format.space_after = Pt(0)
        sp.paragraph_format.line_spacing = Pt(7)

    def quote(self, b: dict) -> None:
        par = self.doc.add_paragraph()
        pf = par.paragraph_format
        pf.left_indent = Cm(0.9)
        pf.right_indent = Cm(0.4)
        pf.space_before = Pt(6)
        pf.space_after = Pt(9)
        pf.line_spacing = Pt(15.5)
        pf.keep_together = True
        border_par(par, left=(AMBER, 2.0), space=7)
        self.runs(par, b["text"], size=10.5, italic=True, color=NAVY_LIGHT)
        if b.get("source"):
            r = par.add_run("  — " + b["source"])
            r.font.name = "Arial"; r.font.size = Pt(8)
            r.font.color.rgb = _rgb(GREY)

    def part_page(self, b: dict) -> None:
        table = self.doc.add_table(rows=1, cols=1)
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        cell = table.rows[0].cells[0]
        cell.width = Emu(int(462 * 12700))
        cell_shade(cell, NAVY)
        cell_margins(cell, 40, 40, 34, 34)
        row_height(table.rows[0], 20.6)
        cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        p0 = cell.paragraphs[0]
        p0.paragraph_format.space_before = Pt(0)
        p0.paragraph_format.space_after = Pt(6)
        r = p0.add_run(b["label"].upper())
        r.font.name = "Arial"; r.font.size = Pt(10); r.font.bold = True
        r.font.color.rgb = _rgb(AMBER)
        char_spacing(r, 60)
        p1 = cell.add_paragraph(style="Titre de partie")
        p1.paragraph_format.space_before = Pt(0)
        p1.paragraph_format.space_after = Pt(8)
        p1.paragraph_format.line_spacing = Pt(34)
        r = p1.add_run(b["title"])
        r.font.name = "Arial"; r.font.size = Pt(28); r.font.bold = True
        r.font.color.rgb = _rgb(WHITE)
        p2 = cell.add_paragraph()
        p2.paragraph_format.space_before = Pt(0)
        p2.paragraph_format.space_after = Pt(10)
        border_par(p2, bottom=(AMBER, 2.0), space=1)
        p3 = cell.add_paragraph()
        p3.paragraph_format.space_before = Pt(4)
        p3.paragraph_format.space_after = Pt(14)
        p3.paragraph_format.line_spacing = Pt(16.5)
        r = p3.add_run(b["description"])
        r.font.name = "Times New Roman"; r.font.size = Pt(11.5)
        r.font.color.rgb = _rgb("D6E1EB")
        if b.get("chapters"):
            p4 = cell.add_paragraph()
            p4.paragraph_format.space_before = Pt(0)
            p4.paragraph_format.space_after = Pt(6)
            p4.paragraph_format.line_spacing = Pt(12.5)
            r = p4.add_run("CHAPITRES")
            r.font.name = "Arial"; r.font.size = Pt(8); r.font.bold = True
            r.font.color.rgb = _rgb(AMBER)
            char_spacing(r, 40)
            par = cell.add_paragraph()
            par.paragraph_format.space_before = Pt(0)
            par.paragraph_format.line_spacing = Pt(13.5)
            r = par.add_run(" · ".join(b["chapters"]))
            r.font.name = "Arial"; r.font.size = Pt(8.6)
            r.font.color.rgb = _rgb("C9D6E2")
        brk = self.doc.add_paragraph()
        brk.paragraph_format.space_before = Pt(0)
        brk.paragraph_format.space_after = Pt(0)
        brk.add_run().add_break(WD_BREAK.PAGE)

    # ---------------- sommaire ----------------
    def toc(self, entries: list[tuple[int, str, int]]) -> None:
        first = self.doc.add_paragraph()
        r = first.add_run()
        r._element.append(_sub("w:fldChar", fldCharType="begin"))
        it = _sub("w:instrText", space="preserve")
        it.text = ' TOC \\o "1-2" \\z \\u '
        r._element.append(it)
        r = first.add_run()
        r._element.append(_sub("w:fldChar", fldCharType="separate"))
        first.paragraph_format.space_after = Pt(0)
        first.paragraph_format.line_spacing = Pt(1)

        last = first
        for lvl, text, page in entries:
            par = self.doc.add_paragraph(style=f"toc {lvl}")
            pf = par.paragraph_format
            pf.tab_stops.add_tab_stop(Cm(16.3), WD_TAB_ALIGNMENT.RIGHT,
                                      WD_TAB_LEADER.DOTS)
            self.runs(par, text, family="Arial" if lvl == 1 else "Times New Roman",
                      size=S[f"toc{lvl}"]["size"], bold=(lvl == 1),
                      color=NAVY if lvl == 1 else INK)
            r = par.add_run("\t" + str(page))
            r.font.name = "Arial" if lvl == 1 else "Times New Roman"
            r.font.size = Pt(S[f"toc{lvl}"]["size"])
            r.font.color.rgb = _rgb(NAVY if lvl == 1 else GREY)
            last = par
        end = last.add_run()
        end._element.append(_sub("w:fldChar", fldCharType="end"))

    def toc_line(self, text: str, page: int, family: str = "Times New Roman",
                 size: float = 9.5, bold: bool = False, indent: float = 0.0,
                 style: str = "TOC cours", color: str = INK) -> None:
        par = self.doc.add_paragraph(style=style)
        pf = par.paragraph_format
        pf.left_indent = Cm(indent)
        pf.tab_stops.add_tab_stop(Cm(16.3), WD_TAB_ALIGNMENT.RIGHT, WD_TAB_LEADER.DOTS)
        self.runs(par, text, family=family, size=size, bold=bold, color=color)
        r = par.add_run("\t" + str(page))
        r.font.name = family
        r.font.size = Pt(size)
        r.font.color.rgb = _rgb(GREY)

    def save(self, path: str) -> str:
        self.doc.save(path)
        return path
