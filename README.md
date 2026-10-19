# Développement web & DevOps — manuel complet

Volume unique de formation technique réunissant deux cours autonomes :

| Cours | Intitulé | Parties | Chapitres | Pages mesurées |
|---|---|---|---|---|
| 1 | Développement web front-end | 7 | 45 | 401 – 453 |
| 2 | DevOps, cloud et fiabilité | 7 | 48 | 402 – 453 |
| | **Volume** | **14** | **93** | **825 – 930** |

Le livrable est **un seul fichier Word** : `build/volume.docx` (couverture,
page de titre, mentions, mode d'emploi, plan, parcours, sommaire général
automatique, les deux cours, quatre annexes, registre de pagination).

## Sources éditoriales

- `devops.pdf` — feuille de route DevOps (roadmap.sh), plan du cours 2.
- `Apprenez_a_creer_votre_site_web_avec_HTM - Copie.pdf` — cours de référence
  HTML/CSS (249 p., 320 entrées de sommaire), référence pédagogique du cours 1.
- `Informations éditoriale.md` — éditeur, auteur, site.
- `assets/logo_noir.png`, `assets/logo_blanc.png` — identité visuelle.

## Structure du dépôt

```
bookkit/          moteur d'édition (unités, mise en page, figures, rendu Word)
content/          texte des chapitres, un fichier Python par chapitre
  front.py        pages liminaires, parcours calculés sur les plans réels
  c1/, c2/        cours 1 (ch01–ch45) et cours 2 (ch01–ch48) + course.py
  annexes.py      mémentos, glossaire, registre de pagination
tools/            check.py (import + pagination), lint.py, measure.py
docs/             AUDIT, DESIGN, PAGINATION, référence de sommaire HTML/CSS
build/            volume.docx (livrable) et fichiers de travail générés
build.py          fabrication complète du volume
```

Chaque chapitre est un module Python déclaratif (`CH = {...}`) composé de blocs
typés : titres, paragraphes, listes, tableaux, figures, encadrés, code,
exercices corrigés et quiz. Le rendu produit des styles Word natifs
(`Heading 1-4`, `Titre de cours`, `Titre de partie`, `Légende`, `Exercice`,
`toc 1/2`, code, encadrés) : le document reste éditable et son sommaire est un
champ automatique.

## Fabriquer le volume

```bash
python3 -m venv .venv
.venv/bin/pip install python-docx pillow lxml matplotlib reportlab pymupdf

.venv/bin/python build.py                 # → build/volume.docx
.venv/bin/python tools/check.py           # import des chapitres + pagination modèle
.venv/bin/python tools/measure.py         # mesure par moteur indépendant + seuil 350
```

`build.py` enchaîne : pagination du modèle, aperçu ReportLab, relevé des pages
réelles, recomposition du sommaire et du registre avec ces numéros, puis rendu
Word. Les numéros imprimés dans le sommaire général sont donc mesurés, et non
estimés.

## Contrôle du seuil de 350 pages par cours

`tools/measure.py` produit deux bornes par cours — modèle déterministe (haute)
et moteur ReportLab (basse) — et échoue si un cours passe sous 350 pages. Voir
`docs/PAGINATION.md` pour la méthode, les conditions de vérification dans Word
et la procédure de contrôle manuel.

Dernière mesure : **cours 1 = 401 à 453 p.**, **cours 2 = 402 à 453 p.**,
volume complet 825 à 930 p.

## Identité et convention

- Palette : navy `#0F2E4C`, ambre `#E0A21B`, sable `#FBF3E2`, encre `#1F2933`.
- Corps Times New Roman 11,5/17,4 pt ; titres Arial ; code Courier New 9,2 pt.
- A4, marges 2,6 / 2,4 / 2,7 / 2,4 cm ; zone de texte 15,9 × 24,7 cm.
- Auteur : IcaBot, agent d'Espritropic Community (graphie modifiable).
- Éditeur : ESPRITROPIC COMMUNITY — YKABAUTH, <https://espritropic.rf.gd>.

## État de production

Les 93 chapitres sont rédigés, importés sans erreur et paginés au-delà du
seuil. Les fichiers de travail (aperçus PDF, figures, captures) restent dans
`build/` et ne sont pas versionnés ; seul le volume final l'est.
