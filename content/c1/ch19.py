from bookkit.dsl import (box, code, defn, ex, fig, h, ol, p, quiz, table, ul)

CH = {
    "title": "CSS Grid : structurer la page",
    "subtitle": "Déclarer une grille plutôt que d'empiler des marges : la mise en page "
                "devient lisible dans le code.",
    "duration": "3 h 15",
    "level": "Intermédiaire",
    "prereq": "chapitre 18",
    "objectives": [
        "Définir des colonnes et des lignes explicites ou implicites.",
        "Placer des éléments par ligne, par nom ou par zone.",
        "Utiliser `minmax()`, `auto-fit` et `repeat()` à bon escient.",
        "Construire une mise en page complète et responsive.",
        "Éviter les pièges de `fr`, de `auto` et des grilles imbriquées.",
    ],
    "blocks": [
        h(2, "Déclarer une grille"),
        p("Grid divise un conteneur en cellules selon deux axes. Contrairement à "
          "Flexbox, la structure est déclarée sur le conteneur, ce qui rend la mise en "
          "page lisible avant même de regarder les enfants."),
        code(""".page {
  display: grid;
  grid-template-columns: 16rem minmax(0, 1fr);
  grid-template-rows: auto 1fr auto;
  gap: 1.5rem;
  min-height: 100dvh;
}""", "css", "Une page en trois lignes et deux colonnes"),
        fig("columns", "Les trois notions de Grid",
            [("Pistes", ["colonnes", "lignes", "dimensions déclarées"]),
             ("Lignes", ["séparations numérotées", "1 à n+1", "placement"]),
             ("Cellules", ["intersections", "une ou plusieurs pistes", "contenu"])],
            height=195),
        table(["Propriété", "Rôle", "Exemple"],
              [["`grid-template-columns`", "Colonnes explicites", "`repeat(3, 1fr)`"],
               ["`grid-template-rows`", "Lignes explicites", "`auto 1fr auto`"],
               ["`grid-auto-rows`", "Hauteur des lignes implicites", "`minmax(6rem, auto)`"],
               ["`gap`", "Espacement", "`1rem 2rem`"],
               ["`grid-column`", "Placement en colonnes", "`1 / 3`"],
               ["`grid-row`", "Placement en lignes", "`2 / span 2`"],
               ["`grid-template-areas`", "Zones nommées", "`\"entete entete\"`"]],
              widths=[3.6, 3.8, 4.2], first_col_bold=True,
              caption="Sept propriétés de Grid"),
        defn("Piste", "Une colonne ou une ligne de la grille. Les pistes explicites sont "
                      "déclarées ; les pistes implicites sont créées automatiquement "
                      "pour accueillir les éléments supplémentaires."),

        h(2, "Unités et fonctions"),
        p("`fr` représente une fraction de l'espace **libre**, après déduction des "
          "tailles fixes et des espaces. `minmax()` borne une piste. `repeat()` évite "
          "les répétitions."),
        code(""".grille-1 { grid-template-columns: 1fr 2fr; }        /* 1/3 et 2/3 */
.grille-2 { grid-template-columns: 12rem minmax(0, 1fr); }
.grille-3 { grid-template-columns: repeat(3, minmax(0, 1fr)); }
.grille-4 { grid-template-columns: repeat(auto-fit, minmax(15rem, 1fr)); }
.grille-5 { grid-template-columns: subgrid; }             /* héritage de pistes */""",
             "css", "Cinq écritures de colonnes"),
        p("`minmax(0, 1fr)` est la forme la plus sûre de `1fr` : sans le `0`, une piste "
          "peut dépasser à cause d'un contenu insécable. `repeat(auto-fit, ...)` crée "
          "autant de colonnes que la largeur le permet, sans media query."),
        code("""/* Galerie responsive sans media query */
.galerie {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(15rem, 1fr));
  gap: 1.25rem;
}""", "css", "Une galerie qui s'adapte seule"),
        box("attention", "`auto-fit` ou `auto-fill` ?",
            "`auto-fit` étire les pistes existantes pour occuper la largeur ; "
            "`auto-fill` conserve des pistes vides. Pour une galerie de cartes, "
            "`auto-fit` évite les colonnes fantômes ; pour un alignement régulier, "
            "`auto-fill` garde la grille stable."),

        h(2, "Placer les éléments"),
        p("Un élément se place par ligne de grille (numérotée), par nom de zone, ou "
          "automatiquement dans l'ordre du document. Le placement explicite doit "
          "correspondre à l'ordre de lecture : sinon, l'accessibilité en souffre."),
        code(""".entete   { grid-column: 1 / -1; }       /* toute la largeur */
.contenu  { grid-column: 2; grid-row: 2; }
.lateral  { grid-column: 1; grid-row: 2; }
.pied     { grid-column: 1 / -1; grid-row: 3; }

/* Variante par zones nommées */
.page {
  grid-template-areas:
    "entete entete"
    "lateral contenu"
    "pied   pied";
}
.entete  { grid-area: entete; }
.lateral { grid-area: lateral; }
.contenu { grid-area: contenu; }
.pied    { grid-area: pied; }""", "css", "Deux façons de placer les mêmes blocs"),
        p("Les zones nommées rendent la structure lisible dans le CSS. Elles "
          "s'accompagnent naturellement d'un changement de disposition en media query :"),
        code("""@media (max-width: 48rem) {
  .page {
    grid-template-columns: 1fr;
    grid-template-areas:
      "entete"
      "contenu"
      "lateral"
      "pied";
  }
}""", "css", "Le même conteneur, une autre disposition"),

        h(2, "Construire une page complète"),
        p("Une mise en page classique combine une grille principale, des composants "
          "flex et des grilles secondaires. Chaque niveau utilise le modèle le plus "
          "simple."),
        code("""<body class="page">
  <header class="entete">...</header>
  <aside class="lateral">...</aside>
  <main class="contenu">...</main>
  <footer class="pied">...</footer>
</body>""", "html", "Quatre régions, une grille"),
        code(""".page {
  display: grid;
  grid-template-columns: minmax(0, 16rem) minmax(0, 1fr);
  grid-template-rows: auto 1fr auto;
  grid-template-areas:
    "entete  entete"
    "lateral contenu"
    "pied    pied";
  gap: 2rem;
  min-height: 100dvh;
  max-width: 78rem;
  margin-inline: auto;
  padding-inline: clamp(1rem, 4vw, 2.5rem);
}
.contenu > * + * { margin-block-start: 1.25rem; }""", "css",
             "Une mise en page complète, en dix lignes"),
        table(["Besoin", "Solution Grid", "Remarque"],
              [["Colonne de lecture centrée", "`minmax(0, 68ch)` + `margin: auto`", "Limite la mesure"],
               ["Trois colonnes égales", "`repeat(3, minmax(0, 1fr))`", "Évite le débordement"],
               ["Galerie fluide", "`auto-fit` + `minmax`", "Aucune media query"],
               ["Tableau de bord", "`grid-template-areas`", "Lisible"],
               ["Carte avec image", "Grid imbriquée", "Attention aux `1fr`"]],
              widths=[3.4, 4.4, 3.2], first_col_bold=True,
              caption="Cinq besoins et leur réponse Grid"),
        box("pratique", "Les grilles imbriquées",
            "Une grille placée dans une cellule peut déborder si elle contient un "
            "élément insécable. Appliquez `min-width: 0` aux cellules concernées : c'est "
            "la correction la plus fréquente des débordements en Grid."),

        h(2, "Pièges et diagnostics"),
        p("Grid est puissant mais punit les approximations. Quatre erreurs expliquent "
          "la majorité des mises en page cassées."),
        table(["Symptôme", "Cause", "Correction"],
              [["Colonne qui déborde", "`1fr` sans `minmax(0, …)`", "`minmax(0, 1fr)`"],
               ["Écart inattendu", "`gap` doublé par une marge", "Supprimer les marges"],
               ["Ordre visuel différent du DOM", "Placement explicite", "Réordonner le HTML"],
               ["Hauteur imprévisible", "Lignes implicites", "`grid-auto-rows`"],
               ["Grille qui ne se replie pas", "Colonnes fixes", "`auto-fit` ou media query"]],
              widths=[3.6, 3.8, 3.6], first_col_bold=True,
              caption="Cinq symptômes de Grid et leur remède"),
        code("""/* Vérifier la grille dans le navigateur */
/* Outils de développement → Éléments → badge « grid » à côté du conteneur */
/* Le panneau « Grid » affiche les lignes, les zones et les noms */""",
             "text", "L'inspecteur visualise la grille réellement calculée"),
        box("methode", "Trois vérifications avant de valider une grille",
            items=["Le contenu suit-il l'ordre du DOM à l'écran ?",
                   "La grille tient-elle à 320 pixels ?",
                   "Aucune piste ne déborde-t-elle à cause d'un `1fr` nu ?"]),
    ],
    "keypoints": [
        "Grid déclare la structure sur le conteneur, sur deux axes.",
        "`fr` désigne une fraction de l'espace libre, pas une proportion du total.",
        "`minmax(0, 1fr)` évite la plupart des débordements.",
        "`repeat(auto-fit, minmax(...))` adapte une galerie sans media query.",
        "Les zones nommées rendent la mise en page lisible.",
        "L'ordre visuel doit respecter l'ordre du DOM.",
        "Grid pour la page, Flexbox pour l'intérieur des composants.",
    ],
    "bridge": "La page se structure. Le chapitre suivant traite le positionnement "
              "précis et les couches d'interface : menus, modales, infobulles.",
    "exercises": [
        ex("Galerie auto-adaptative",
           "Créez une galerie d'images qui affiche une à quatre colonnes selon la "
           "largeur, sans media query.",
           ["Utilisez `auto-fit` et `minmax`.",
            "Ajoutez un espacement cohérent.",
            "Vérifiez le rendu à 320, 768 et 1440 pixels."],
           [("code", """.galerie {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 1rem;
}
.galerie img {
  display: block;
  width: 100%;
  height: 220px;
  object-fit: cover;
  border-radius: 8px;
}"""),
            "À 320 px, une seule colonne ; à 768, trois ; à 1440, quatre ou cinq selon "
            "la largeur maximale du conteneur.",
            "`object-fit: cover` conserve les proportions en remplissant la cellule ; "
            "sans lui, les images seraient déformées."]),
        ex("Mise en page à zones nommées",
           "Construisez une page : en-tête, barre latérale, contenu, pied, qui passe en "
           "une colonne sur mobile.",
           ["Déclarez les zones sur le conteneur.",
            "Placez chaque région par `grid-area`.",
            "Changez la disposition en media query."],
           [("code", """.page {
  display: grid;
  grid-template-columns: 15rem minmax(0, 1fr);
  grid-template-areas:
    "entete entete"
    "lateral contenu"
    "pied pied";
  gap: 1.5rem;
}
@media (max-width: 48rem) {
  .page {
    grid-template-columns: 1fr;
    grid-template-areas: "entete" "contenu" "lateral" "pied";
  }
}"""),
            "Les noms de zones doivent former un rectangle : une zone en L est "
            "invalide et la déclaration entière est ignorée.",
            "Sur mobile, l'ordre des zones place le contenu avant la barre latérale : "
            "l'information principale reste en tête."]),
        ex("Corriger une grille cassée",
           "Cette grille déborde sur mobile.",
           ["`.grille { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 2rem; }`",
            "`.carte { min-width: 320px; }`",
            "`.carte__titre { white-space: nowrap; }`"],
           ["Trois colonnes `1fr` sur un écran de 360 px donnent des cellules de "
            "120 px moins le `gap` : le contenu insécable déborde.",
            "`min-width: 320px` sur la carte est incompatible avec une cellule de "
            "120 px : la carte force la grille à s'élargir.",
            ("code", """.grille {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 1rem;
}
.carte { min-width: 0; }
.carte__titre { white-space: normal; overflow-wrap: anywhere; }""")],
           level="Diagnostic"),
    ],
    "quiz": [
        quiz("Que représente `1fr` ?",
             ["Un pixel", "Une fraction de l'espace libre", "Une ligne", "Une colonne fixe"],
             1,
             "Les fractions se partagent l'espace restant après déduction des tailles "
             "fixes et des `gap`."),
        quiz("Quelle fonction crée une galerie adaptative sans media query ?",
             ["`repeat(3, 1fr)`", "`repeat(auto-fit, minmax(15rem, 1fr))`", "`minmax(0, 1fr)` seul", "`subgrid`"],
             1,
             "`auto-fit` crée autant de pistes que possible selon la largeur, avec un "
             "minimum garanti par `minmax`."),
        quiz("Pourquoi préférer `minmax(0, 1fr)` à `1fr` ?",
             ["Pour avoir des colonnes plus larges",
              "Pour empêcher le contenu insécable de faire déborder la piste",
              "Pour centrer le contenu",
              "Pour activer `gap`"],
             1,
             "La valeur `auto` implicite de la taille minimale empêche la piste de "
             "rétrécir sous son contenu ; `0` lève cette contrainte."),
        quiz("Quel est l'effet de `grid-template-areas` ?",
             ["Créer des variables", "Définir des zones nommées pour placer les éléments",
              "Animer la grille", "Imbriquer des grilles"],
             1,
             "Les zones nommées décrivent la disposition et se placent avec "
             "`grid-area`."),
        quiz("Quel modèle pour l'intérieur d'une carte ?",
             ["Grid", "Flexbox", "Float", "Position absolue"],
             1,
             "Pour un composant à une dimension (empiler un titre, un texte, un pied), "
             "Flexbox reste le plus simple."),
    ],
}
