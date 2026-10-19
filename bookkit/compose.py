"""Composition : transforme les chapitres rédigés en blocs typés prêts à paginer."""
from __future__ import annotations

import re

from .dsl import box, h, ol, p, pb, ul

def _solution_blocks(sol, num: int) -> list[dict]:
    if isinstance(sol, str):
        sol = [sol]
    out = []
    for item in sol:
        if isinstance(item, tuple):
            kind, text = item
            if kind == "code":
                out.append({"t": "code", "text": text, "lang": "", "caption": None})
            elif kind == "list":
                out.append(ul(*text))
            else:
                out.append(p(text))
        elif isinstance(item, dict):
            out.append(item)
        else:
            for para in str(item).split("\n\n"):
                if para.strip():
                    out.append(p(para.strip()))
    return out


def compose_chapter(ch: dict, num: int, part_label: str,
                    toc_sink: list | None = None, base: int = 0,
                    local: int = 0) -> list[dict]:
    blocks: list[dict] = []
    blocks.append({
        "t": "h", "level": 2, "text": f"{num}. {ch['title']}",
        "id": f"ch{num}", "page_break": True,
    })
    if ch.get("subtitle"):
        blocks.append(p(ch["subtitle"], "lead"))
    meta = []
    if ch.get("duration"):
        meta.append(f"Durée de travail : {ch['duration']}")
    if ch.get("level"):
        meta.append(f"Niveau : {ch['level']}")
    if local:
        # La progression est linéaire : le prérequis réel est le chapitre précédent.
        meta.append("Prérequis : aucun" if local <= 1 else
                    f"Prérequis : chapitre {num - 1}")
    if meta:
        blocks.append(p(" · ".join(meta), "small"))
    if ch.get("objectives"):
        blocks.append(box("objectifs", "À l'issue de ce chapitre, vous saurez",
                          items=ch["objectives"]))

    s2 = 0
    s3 = 0
    for b in ch["blocks"]:
        if b["t"] == "h" and b["level"] == 2:
            s2 += 1
            s3 = 0
            b = dict(b)
            b["text"] = f"{num}.{s2} {b['text']}"
            b["id"] = f"ch{num}_s{s2}"
            b["level"] = 3
            if toc_sink is not None:
                toc_sink.append((2, b["text"], b["id"]))
        elif b["t"] == "h" and b["level"] == 3:
            s3 += 1
            b = dict(b)
            b["text"] = f"{num}.{s2}.{s3} {b['text']}"
            b["level"] = 4
        elif b["t"] == "h" and b["level"] == 4:
            b = dict(b)
            b["level"] = 4
        blocks.append(b)

    if ch.get("keypoints"):
        blocks.append({"t": "rubric", "text": "L'essentiel du chapitre"})
        blocks.append(ul(*ch["keypoints"]))
    if ch.get("bridge"):
        blocks.append(p(ch["bridge"]))

    exercises = ch.get("exercises") or []
    if exercises:
        blocks.append({"t": "rubric", "text": "Exercices d'application",
                       "id": f"ch{num}_ex"})
        blocks.append(p(
            "Les exercices suivants se traitent avec un éditeur de texte et un navigateur "
            "récent. Les corrigés détaillés figurent immédiatement après, avec les "
            "explications de chaque décision technique."))
        for i, exo in enumerate(exercises, 1):
            tag = exo.get("level", "Application")
            blocks.append({"t": "exhead", "text": f"Exercice {num}.{i} — {exo['title']}",
                           "tag": tag, "id": f"ch{num}_ex{i}"})
            blocks.append(p(exo["prompt"]))
            if exo.get("tasks"):
                blocks.append(ol(*exo["tasks"]))
            if exo.get("hint"):
                blocks.append(p("**Indice.** " + exo["hint"]))
        blocks.append({"t": "rubric", "text": "Corrigés détaillés",
                       "id": f"ch{num}_cor"})
        blocks.append(p(
            "Chaque corrigé justifie les choix de structure, de style et de code. "
            "Plusieurs solutions restent valables : l'important est de comprendre "
            "la raison de chaque décision."))
        for i, exo in enumerate(exercises, 1):
            blocks.append({"t": "corrhead", "text": f"Corrigé {num}.{i}",
                           "id": f"ch{num}_cor{i}"})
            blocks.extend(_solution_blocks(exo["solution"], num))

    quizz = ch.get("quiz") or []
    if quizz:
        blocks.append({"t": "rubric", "text": "Quiz de vérification",
                       "id": f"ch{num}_quiz"})
        blocks.append(p(
            "Une seule réponse est exacte par question. Répondez sans revenir au texte, "
            "puis consultez les explications."))
        for i, q in enumerate(quizz, 1):
            blocks.append({"t": "qhead", "text": f"Question {i}"})
            blocks.append(p(q["question"]))
            blocks.append({"t": "opts", "items": q["options"]})
        blocks.append({"t": "rubric", "text": "Réponses et explications",
                       "id": f"ch{num}_ans"})
        for i, q in enumerate(quizz, 1):
            letter = "ABCDEFGH"[q["answer"]]
            blocks.append(p(f"**{i}. {letter}.** {q['explanation']}"))
    return blocks


def compose_course_front(course: dict, num: int, chapter_pages: dict,
                         course_toc: list) -> list[dict]:
    """Couverture de cours + mode d'emploi + sommaire détaillé."""
    blocks: list[dict] = []
    blocks.append({"t": "h", "level": 1, "text": course["title"], "id": f"course{num}",
                   "style": "Titre de cours", "eyebrow": f"COURS {num}",
                   "page_break": True})
    blocks.append(p(course["subtitle"], "lead"))
    blocks.append({"t": "rule"})
    for para in course["description"]:
        blocks.append(p(para))
    blocks.append(box("pratique", "Ce que contient ce cours", items=course["contains"]))
    blocks.append(box("methode", "Comment travailler ce cours", items=course["method"]))
    blocks.append(pb())

    blocks.append({"t": "rubric", "text": "Sommaire détaillé du cours",
                   "style": "Titre hors sommaire", "id": None})
    blocks.append(p(
        "Les pages indiquées renvoient à la pagination continue du volume. "
        "Chaque chapitre peut être travaillé indépendamment, dans l'ordre proposé "
        "ou selon les besoins du lecteur."))
    for kind, text, bid in course_toc:
        if kind == "part":
            blocks.append({"t": "p", "text": text, "style": "small",
                           "id": None, "toc_course": True, "bold": True,
                           "page": chapter_pages.get(bid, 0)})
        elif kind == "chapter":
            blocks.append({"t": "toc_course", "text": text,
                           "page": chapter_pages.get(bid, 0), "indent": 0.0,
                           "bold": True})
        else:
            blocks.append({"t": "toc_course", "text": text,
                           "page": chapter_pages.get(bid, 0), "indent": 0.45,
                           "bold": False})
    blocks.append({"t": "pb"})
    return blocks


def part_block(part: dict, label: str, chapters: list[str], page_break: bool = True) -> dict:
    return {"t": "fullpage", "kind": "part", "label": label, "title": part["title"],
            "description": part["description"], "chapters": chapters,
            "id": part["id"]}


# --------------------------------------------------------------------------- #
# Renvois internes au cours
# --------------------------------------------------------------------------- #
import re as _re

_REF = _re.compile(r"chapitres?\s+(\d+)(?:\s*(?:à|et)\s*(\d+))?")


def _corps(ch: dict) -> list[str]:
    """Chaînes de texte libre d'un chapitre (hors champs de structure)."""
    out: list[str] = []
    for b in ch.get("blocks", []):
        t = b.get("t")
        if t in ("p", "quote"):
            out.append(b.get("text", ""))
        elif t in ("ul", "ol"):
            out.extend(b.get("items", []))
        elif t in ("box", "defn"):
            if b.get("title"):
                out.append(b["title"])
            if b.get("text"):
                out.append(b["text"])
            out.extend(b.get("items") or [])
        elif t == "table":
            out.extend(b.get("headers") or [])
            for row in b.get("rows") or []:
                out.extend(str(c) for c in row)
        elif t == "code":
            if b.get("caption"):
                out.append(b["caption"])
    return out


def renvois(ch: dict, base: int, local: int) -> list[int]:
    """Numéros absolus cités par le chapitre, triés et dédoublonnés."""
    trouves: set[int] = set()
    for texte in _corps(ch):
        for m in _REF.finditer(texte):
            for g in (m.group(1), m.group(2)):
                if g and 1 <= int(g) <= 99 and int(g) != local:
                    trouves.add(int(g) + base)
    return sorted(trouves)


def index_chapitres(parts: list[dict], base: int) -> dict[int, list[int]]:
    """Dictionnaire « chapitre absolu → chapitres absolus qui le citent ».

    ``parts`` est la liste des parties chargées (telle que produite par
    ``bookkit.assemble.course_parts``), ``base`` le nombre de chapitres qui
    précèdent ce cours dans le volume.
    """
    renverse: dict[int, set[int]] = {}
    local = 0
    for part in parts:
        for ch in part["loaded"]:
            local += 1
            absolu = base + local
            for cible in renvois(ch, base, local):
                renverse.setdefault(cible, set()).add(absolu)
    return {k: sorted(v) for k, v in sorted(renverse.items())}
