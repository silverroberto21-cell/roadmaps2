#!/usr/bin/env python3
"""Fabrication du volume unique au format .docx.

Usage : python build.py [--output build/volume.docx]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from bookkit.assemble import assemble                       # noqa: E402
from bookkit.figures import make_cover                      # noqa: E402
from bookkit.model import paginate                          # noqa: E402
from bookkit.preview import PreviewBook                     # noqa: E402
from bookkit.render import Renderer                         # noqa: E402

META = {
    "title": "Développement web & DevOps — Manuel complet",
    "author": "IcaBot — ESPRITROPIC COMMUNITY",
    "subject": "HTML5, CSS3, JavaScript, Linux, conteneurs, cloud et fiabilité",
    "keywords": "HTML, CSS, JavaScript, DevOps, Linux, Docker, Kubernetes, Terraform, CI/CD, SRE",
    "comments": "Volume unique — Bibliothèque technique Espritropic, édition 2026",
}


def load_courses():
    from content.c1.course import COURSE as C1
    from content.c2.course import COURSE as C2
    return [C1, C2]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", default="build/volume.docx")
    ap.add_argument("--verbose", action="store_true")
    ap.add_argument("--no-preview", action="store_true",
                    help="ne pas recalculer les numéros de page par aperçu")
    args = ap.parse_args()

    out = ROOT / args.output
    out.parent.mkdir(parents=True, exist_ok=True)

    courses = load_courses()
    nb_chapitres = sum(len(pt["chapters"]) for c in courses for pt in c["parts"])

    cover = ROOT / "build" / "cover.png"
    make_cover(cover, "assets/logo_blanc.png", chapters=nb_chapitres)
    from content.annexes import build_annexes

    pages: dict = {}
    blocks: list = []
    entries: list = []
    for it in range(6):
        annex_blocks = build_annexes(pages)
        blocks, entries = assemble(courses, pages, str(ROOT / "assets/logo_noir.png"),
                                   annex_blocks)
        pg = paginate(blocks, page=2)
        new_pages = dict(pg.marks)
        total = pg.pages
        stable = all(new_pages.get(k) == pages.get(k) for k in new_pages) and pages
        if args.verbose:
            print(f"  passe {it + 1}: {total} pages, {len(pages)} repères")
        pages = new_pages
        if stable:
            break

    annex_blocks = build_annexes(pages)
    blocks, entries = assemble(courses, pages, str(ROOT / "assets/logo_noir.png"),
                               annex_blocks)
    pg = paginate(blocks, page=2)

    # Pagination réelle (moteur indépendant) : les numéros imprimés dans le
    # sommaire général et dans le registre d'annexe sont ceux mesurés ici.
    total_mesure = None
    if not args.no_preview:
        tmp = ROOT / "build" / "pagination-controle.pdf"
        apercu = PreviewBook(blocks, str(tmp), "Contrôle")
        total_mesure = apercu.build()
        mesures = dict(apercu.marks)
        if mesures:
            pages = dict(pages, **mesures)
            annex_blocks = build_annexes(pages)
            blocks, entries = assemble(courses, pages,
                                       str(ROOT / "assets/logo_noir.png"),
                                       annex_blocks)

    r = Renderer(META)
    r.cover(str(cover))
    r.new_section("Développement web & DevOps", "Pages liminaires", first_blank=True)
    for b in blocks:
        r.block(b)
    r.save(str(out))

    report = {
        "output": str(out),
        "pages_estimees": pg.pages,
        "pages_mesurees": total_mesure,
        "reperes": len(pages),
        "entrees_sommaire": len(entries),
        "cours": [],
    }
    for i, c in enumerate(courses, 1):
        start = pages.get(f"course{i}")
        nxt = pages.get(f"course{i + 1}") or pages.get("anx1") or pg.pages + 1
        report["cours"].append({
            "numero": i,
            "titre": c["title"],
            "debut": start,
            "fin_estimee": nxt - 1,
            "pages": (nxt - start) if start else None,
            "chapitres": sum(len(p["chapters"]) for p in c["parts"]),
        })
    (ROOT / "build" / "report.json").write_text(json.dumps(report, indent=2,
                                                          ensure_ascii=False),
                                               encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
