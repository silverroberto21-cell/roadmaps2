#!/usr/bin/env python3
"""Contrôle de pagination du volume assemblé.

Deux mesures indépendantes sont produites pour chaque cours :

* ``modele``   — pagination déterministe du moteur interne (``bookkit.model``),
  qui simule Word bloc par bloc et surestime légèrement (blocs insécables) ;
* ``moteur``   — pagination réelle obtenue en composant les mêmes blocs avec
  ReportLab (``bookkit.preview``), moteur distinct de Word mais qui coupe les
  paragraphes comme lui.

L'encadrement obtenu donne une fourchette : la valeur Word se situe entre les
deux, plus près de ``moteur``. Le seuil exigé est de 350 pages par cours.

Usage :
    python tools/measure.py [--pdf build/controle.pdf] [--json build/pagination.json]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

SEUIL = 350


def _marques(pages: dict) -> dict:
    from bookkit.assemble import assemble
    from bookkit.model import paginate
    from content.annexes import build_annexes
    from content.c1.course import COURSE as C1
    from content.c2.course import COURSE as C2

    marks = dict(pages)
    pg = None
    blocks: list = []
    for _ in range(6):
        blocks, _ = assemble([C1, C2], marks, str(ROOT / "assets" / "logo_noir.png"),
                             build_annexes(marks))
        pg = paginate(blocks, page=2)
        if pg.marks == marks:
            break
        marks = pg.marks
    return marks, pg.pages, blocks


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pdf", default="build/controle.pdf")
    ap.add_argument("--json", default="build/pagination.json")
    args = ap.parse_args()

    from content.c1.course import COURSE as C1
    from content.c2.course import COURSE as C2

    marks, pages_modele, blocks = _marques({})
    c1, c2 = marks["course1"], marks["course2"]
    anx = marks.get("anx1", pages_modele + 1)
    modele = {"cours1": c2 - c1, "cours2": anx - c2}
    total_modele = pages_modele

    # Mesure par un moteur indépendant
    from bookkit.preview import PreviewBook

    pdf = ROOT / args.pdf
    pdf.parent.mkdir(parents=True, exist_ok=True)
    apercu = PreviewBook(blocks, str(pdf), "Contrôle de pagination")
    total_moteur = apercu.build()
    m = apercu.marks
    moteur = {"cours1": m["course2"] - m["course1"],
              "cours2": m["anx1"] - m["course2"]}

    resultat = {
        "seuil": SEUIL,
        "chapitres": {
            "cours1": sum(len(p["chapters"]) for p in C1["parts"]),
            "cours2": sum(len(p["chapters"]) for p in C2["parts"]),
        },
        "pages_modele": modele,
        "pages_moteur": moteur,
        "total_modele": total_modele,
        "total_moteur": total_moteur,
        "conforme": {k: moteur[k] >= SEUIL for k in moteur},
    }

    print(f"Seuil exigé : {SEUIL} pages par cours (hors liminaires)")
    for k in ("cours1", "cours2"):
        bas, haut = moteur[k], modele[k]
        etat = "conforme" if bas >= SEUIL else "INSUFFISANT"
        print(f"  {k} : {bas} à {haut} pages "
              f"(moteur {bas} / modèle {haut}) — {etat}")
    print(f"  volume complet : {total_moteur} à {total_modele} pages")

    out = ROOT / args.json
    out.write_text(json.dumps(resultat, ensure_ascii=False, indent=1))
    print(f"  rapport : {out.relative_to(ROOT)}")
    return 0 if all(resultat["conforme"].values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
