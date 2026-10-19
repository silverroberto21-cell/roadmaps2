# Pagination et contrôle du volume

Ce document décrit la mise en page du volume unique, la méthode employée pour
vérifier le nombre de pages de chaque cours et les conditions dans lesquelles ce
contrôle est valable. Il sert de référence en cas d'écart constaté à l'ouverture
du fichier dans Microsoft Word.

## 1. Exigence

Le seuil est de **350 pages minimum par cours**, mesuré dans le document Word
final, chaque cours compté séparément. Les liminaires (couverture, mentions,
mode d'emploi, sommaire général) et les annexes ne sont pas comptés dans le
volume d'un cours.

Le seuil n'est jamais atteint par gonflement : aucune page n'est ajoutée pour
elle-même. La longueur provient du contenu pédagogique (explications, tableaux,
listes de code commentées, exercices corrigés, quiz).

## 2. Mise en page de référence

| Paramètre | Valeur |
|---|---|
| Format | A4 portrait, 21 × 29,7 cm |
| Marges | haut 2,6 cm · bas 2,4 cm · gauche 2,7 cm · droite 2,4 cm |
| Zone de texte | 15,9 × 24,7 cm (≈ 461 × 705 pt) |
| Police du corps | Times New Roman 11,5 pt, interligne exact 17,4 pt |
| Titres | Arial (1 : 23 pt · 2 : 14,5 pt · 3 : 11,8 pt · 4 : 10,8 pt) |
| Code | Courier New 9,2 pt, interligne exact 12,2 pt |
| Tableaux | Arial 9,5 pt, interligne 13 pt |
| En-tête / pied | 1,25 cm / 1,15 cm ; pagination continue à droite |

Ces valeurs sont définies une seule fois dans `bookkit/units.py` et appliquées
aux deux moteurs (Word et aperçu). Toute modification de ce fichier change la
pagination : il faut alors relancer la mesure.

## 3. Méthode de mesure

Deux mesures indépendantes encadrent la pagination réelle :

1. **Modèle déterministe** (`bookkit/model.py::paginate`). Il simule Word bloc
   par bloc, en supposant les paragraphes insécables et les tableaux coupables
   entre deux lignes avec répétition d'en-tête. Il **surestime** légèrement,
   puisqu'un paragraphe long peut, dans Word, se poursuivre sur la page
   suivante.
2. **Moteur indépendant** (`bookkit/preview.py`, ReportLab). Les mêmes blocs sont
   composés par un moteur typographique distinct, avec les mêmes métriques de
   police et les mêmes marges ; les paragraphes s'y coupent comme dans Word. Il
   **sous-estime** légèrement, car il ne connaît ni les veuves et orphelines de
   Word ni les arrondis de ses tableaux.

La pagination Word se situe entre ces deux bornes, plus près de la seconde. La
commande `python tools/measure.py` produit les deux mesures, écrit
`build/pagination.json` et renvoie un code de sortie non nul si un cours passe
sous le seuil.

### Résultat de la dernière mesure

| Cours | Chapitres | Borne basse (moteur) | Borne haute (modèle) | Seuil |
|---|---|---|---|---|
| Cours 1 — Développement web front-end | 45 | 401 | 453 | 350 |
| Cours 2 — DevOps, cloud et fiabilité | 48 | 402 | 453 | 350 |
| Volume complet | 93 | 825 | 930 | — |

Les deux bornes basses dépassent le seuil de plus de 14 %, et la borne
haute de près de 30 %.

## 4. Conditions de vérification

La mesure n'est valable que si les conditions suivantes sont réunies :

- **Polices présentes.** Times New Roman, Arial et Courier New sont des polices
  fournies avec Microsoft Windows et Microsoft Office. Sur une machine où elles
  sont absentes (certaines installations Linux ou macOS), les métriques de
  substitution changent l'interligne et décalent la pagination de plusieurs
  pages. Les équivalents métriques (Liberation Serif, Liberation Sans,
  Liberation Mono) sont les seuls remplacements acceptables.
- **Mise en page inchangée.** Format, marges, interlignes exacts et styles
  natifs doivent rester ceux du document livré. L'ajout d'un en-tête plus haut
  ou d'un interligne multiple modifie le nombre de pages.
- **Champ de sommaire à jour.** À l'ouverture, Word peut demander la mise à jour
  des champs. Acceptez-la (ou `Ctrl+A` puis `F9`). Le sommaire occupe alors le
  même nombre de pages que lors de la mesure, car ses entrées sont déjà toutes
  présentes dans le cache du champ.
- **Aucune impression virtuelle intermédiaire.** Un export PDF produit par un
  pilote différent peut refléter une autre pagination ; il ne remplace pas la
  mesure faite dans Word.

## 5. Procédure de contrôle dans Word

1. Ouvrir `build/volume.docx` dans Microsoft Word (2016 ou ultérieur).
2. Mettre à jour les champs : `Ctrl+A`, puis `F9`, puis « Mettre à jour toute la
   table ».
3. Aller au début du cours 1 (page « Présentation du cours 1 ») : noter le
   numéro affiché dans la barre d'état.
4. Aller au début du cours 2 : noter le numéro. La différence donne le nombre de
   pages du cours 1.
5. Aller au début de l'annexe A : la différence avec l'étape 4 donne le nombre
   de pages du cours 2.
6. Comparer aux bornes du tableau ci-dessus. Un écart de quelques pages est
   normal ; un écart de plus de 5 % signale une différence de polices ou de
   mise en page.

L'annexe D du volume reproduit ce registre avec les pages de départ mesurées
lors de la fabrication.

## 6. Variabilité admise

La pagination d'un même fichier peut varier :

- de 1 à 3 pages selon la version de Word et le moteur de rendu ;
- de quelques pages selon les polices effectivement installées ;
- de 0 à 2 pages selon que les champs sont à jour ou non.

La marge observée (au moins 51 pages au-dessus du seuil sur le cours le plus
court, mesuré par le moteur indépendant) absorbe largement cette variabilité.

## 7. Si un cours passe sous le seuil

1. Vérifier les polices installées et la mise en page (section 4).
2. Relancer `python tools/measure.py` pour retrouver les deux bornes.
3. Si la borne basse est réellement sous 350, enrichir le cours concerné par du
   contenu pédagogique réel (section, exercice corrigé, étude de cas), jamais
   par des sauts de page ou des espaces.
4. Relancer la mesure et consigner le nouveau résultat dans ce document.
