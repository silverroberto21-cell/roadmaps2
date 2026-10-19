#!/usr/bin/env python3
"""Contrôle rapide : import des chapitres + pagination estimée."""
import importlib, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

def main():
    bad = []
    for path in sorted(ROOT.glob("content/c*/ch*.py")):
        mod = ".".join(path.relative_to(ROOT).with_suffix("").parts)
        try:
            importlib.import_module(mod)
        except Exception as e:
            bad.append(f"{path.name}: {type(e).__name__}: {e}")
    if bad:
        print("ERREURS:")
        for b in bad: print(" -", b)
        return 1
    from bookkit.assemble import assemble
    from bookkit.model import paginate
    from content.c1.course import COURSE as C1
    from content.c2.course import COURSE as C2
    from content.annexes import build_annexes
    pages = {}
    for _ in range(6):
        blocks, entries = assemble([C1, C2], pages, "assets/logo_noir.png", build_annexes(pages))
        pg = paginate(blocks, page=2)
        if pg.marks == pages: break
        pages = pg.marks
    c1 = pages.get("course1", 1)
    c2 = pages.get("course2", c1)
    anx = pages.get("anx1", pg.pages + 1)
    print(f"{len(list(ROOT.glob('content/c*/ch*.py')))} chapitres | "
          f"total {pg.pages} pages | cours1 {c2 - c1} pages | cours2 {anx - c2} pages")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
