from bookkit.dsl import (box, code, defn, ex, fig, h, ol, p, quiz, table, ul)

CH = {
    "title": "Flexbox : aligner sur un axe",
    "subtitle": "Une dimension, deux axes, six propriétés : la mise en page du quotidien "
                "enfin maîtrisée.",
    "duration": "3 h 00",
    "level": "Intermédiaire",
    "prereq": "chapitre 17",
    "objectives": [
        "Distinguer axe principal et axe secondaire.",
        "Aligner et répartir des éléments sans marge ni positionnement.",
        "Contrôler le rétrécissement et l'expansion des enfants.",
        "Construire des barres, cartes, centrages et étiquettes.",
        "Reconnaître les cas où Flexbox n'est pas la bonne réponse.",
    ],
    "blocks": [
        h(2, "Le modèle mental"),
        p("Flexbox organise les enfants d'un conteneur le long d'un **axe principal**. "
          "Le sens de cet axe dépend de `flex-direction` : horizontale par défaut, "
          "verticale si l'on choisit `column`. L'axe perpendiculaire est l'axe "
          "secondaire."),
        fig("compare", "Deux axes, deux logiques",
            ("AXE PRINCIPAL", ["Sens de `flex-direction`", "`justify-content` répartit",
                               "Horizontal par défaut"],
             "AXE SECONDAIRE", ["Perpendiculaire au principal", "`align-items` aligne",
                                "Vertical par défaut"]),
            height=200),
        code(""".barre {
  display: flex;
  flex-direction: row;        /* axe principal horizontal */
  justify-content: space-between;  /* répartition sur l'axe principal */
  align-items: center;        /* alignement sur l'axe secondaire */
  gap: 1rem;
}""", "css", "Trois propriétés suffisent à une barre de navigation"),
        table(["Propriété", "Conteneur", "Effet"],
              [["`flex-direction`", "Oui", "Sens de l'axe principal"],
               ["`justify-content`", "Oui", "Répartition sur l'axe principal"],
               ["`align-items`", "Oui", "Alignement sur l'axe secondaire"],
               ["`align-content`", "Oui", "Lignes multiples"],
               ["`flex-wrap`", "Oui", "Passage à la ligne"],
               ["`gap`", "Oui", "Espace entre enfants"],
               ["`flex-grow`", "Non", "Capacité à occuper l'espace libre"],
               ["`flex-shrink`", "Non", "Capacité à rétrécir"],
               ["`flex-basis`", "Non", "Taille initiale"],
               ["`align-self`", "Non", "Exception d'alignement"]],
              widths=[3.0, 2.4, 5.2], first_col_bold=True,
              caption="Dix propriétés essentielles de Flexbox"),
        defn("`flex`", "Raccourci de `flex-grow`, `flex-shrink` et `flex-basis`. "
                       "`flex: 1` signifie « prends l'espace disponible, rétrécis si "
                       "nécessaire, base zéro »."),

        h(2, "Aligner : les combinaisons utiles"),
        p("`justify-content` accepte six valeurs principales. Chacune correspond à une "
          "intention de composition, pas à un réglage arbitraire."),
        table(["Valeur", "Effet", "Usage"],
              [["`flex-start`", "Alignés au début", "Par défaut, listes"],
               ["`flex-end`", "Alignés à la fin", "Actions secondaires"],
               ["`center`", "Groupés au centre", "Centrage d'un contenu"],
               ["`space-between`", "Écartés aux extrémités", "Barre de navigation"],
               ["`space-around`", "Espaces égaux autour", "Étiquettes"],
               ["`space-evenly`", "Espaces strictement égaux", "Menus courts"]],
              widths=[3.0, 4.2, 3.4], first_col_bold=True,
              caption="Six valeurs de `justify-content`"),
        code("""<nav class="barre">
  <a class="barre__marque" href="/">Espritropic</a>
  <ul class="barre__liens">
    <li><a href="/cours">Cours</a></li>
    <li><a href="/blog">Blog</a></li>
    <li><a href="/contact">Contact</a></li>
  </ul>
</nav>""", "html", "Une barre simple à structurer"),
        code(""".barre {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 2rem;
  padding-block: .75rem;
}
.barre__liens { display: flex; gap: 1.25rem; list-style: none; margin: 0; padding: 0; }""",
             "css", "Un conteneur flex dans un conteneur flex"),
        p("Le centrage vertical, longtemps difficile, devient trivial : "
          "`display: flex; align-items: center; justify-content: center;` sur le "
          "conteneur suffit. C'est la raison principale de l'adoption massive de "
          "Flexbox."),

        h(2, "Flexibilité et rétrécissement"),
        p("`flex: 1` sur tous les enfants produit des colonnes égales. `flex: 1 0 auto` "
          "conserve la taille naturelle et n'autorise pas le rétrécissement. Ces "
          "nuances décident du comportement sur petit écran."),
        code(""".cartes { display: flex; gap: 1rem; }
.carte { flex: 1 1 18rem; }   /* grandit, rétrécit, base 18rem */
.carte--fixe { flex: 0 0 20rem; }  /* largeur imposée */
.carte--large { flex: 2 1 24rem; } /* prend deux parts */""", "css",
             "Trois comportements de flexibilité"),
        p("Sur un téléphone, trois cartes à `flex: 1` deviennent trois colonnes de "
          "cent pixels : illisibles. `flex-wrap: wrap` les fait passer à la ligne, et "
          "`flex-basis` fixe la largeur minimale acceptable."),
        code(""".cartes {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
}
.carte { flex: 1 1 18rem; max-width: 100%; }""", "css",
             "Un passage à la ligne automatique"),
        box("attention", "L'élément qui refuse de rétrécir",
            "Un enfant flex a `min-width: auto` par défaut : il ne descend pas sous la "
            "largeur de son contenu. Un long mot, une URL ou une image empêchent donc "
            "la colonne de rétrécir. Solution : `min-width: 0` sur l'enfant."),
        code(""".colonne {
  flex: 1;
  min-width: 0;      /* autorise le rétrécissement sous la taille du contenu */
}
.colonne p { overflow-wrap: anywhere; }""", "css",
             "La correction du débordement le plus fréquent"),

        h(2, "Cas d'usage typiques"),
        p("Flexbox excelle pour les alignements en une dimension. Cinq motifs couvrent "
          "la majorité des besoins quotidiens."),
        table(["Motif", "Solution", "Piège"],
              [["Barre de navigation", "`space-between` + `align-items: center`", "Menu qui déborde"],
               ["Centrage parfait", "`center` sur les deux axes", "Hauteur nulle du parent"],
               ["Pied de carte collé en bas", "`flex-direction: column` + `margin-top: auto`", "Hauteur non définie"],
               ["Étiquettes qui se replient", "`flex-wrap: wrap` + `gap`", "Pas d'espacement"],
               ["Colonnes égales", "`flex: 1`", "Contenu long qui déborde"]],
              widths=[3.4, 4.8, 2.8], first_col_bold=True,
              caption="Cinq motifs et leurs pièges"),
        code("""/* Pied de carte aligné en bas, quelle que soit la hauteur */
.carte {
  display: flex;
  flex-direction: column;
  height: 100%;
}
.carte__pied { margin-top: auto; }

/* Étiquettes */
.etiquettes { display: flex; flex-wrap: wrap; gap: .5rem; }
.etiquette { padding: .2rem .6rem; border-radius: 999px; background: #e8edf1; }""",
             "css", "Deux motifs fréquents, résolus en trois lignes"),
        p("Le centrage vertical exige une hauteur sur le conteneur. Sur un élément dont "
          "la hauteur dépend du contenu, `align-items: center` n'a aucun effet visible : "
          "il n'y a rien à centrer."),

        h(2, "Flexbox ou Grid ?"),
        p("Les deux modèles se complètent. La règle pratique : **une dimension, "
          "Flexbox ; deux dimensions, Grid**. Cela dit, Flexbox reste excellent pour "
          "les composants internes, même dans une page construite en Grid."),
        fig("compare", "Deux modèles complémentaires",
            ("FLEXBOX", ["Un axe à la fois", "Répartition du contenu", "Composants, barres"],
             "GRID", ["Deux axes simultanés", "Structure déclarée", "Pages, galeries"]),
            height=190),
        code("""/* La page en Grid, les composants en Flex */
.page {
  display: grid;
  grid-template-columns: 16rem 1fr;
  gap: 2rem;
}
.barre { display: flex; justify-content: space-between; align-items: center; }""",
             "css", "Combiner les deux sans dogme"),
        box("methode", "Quatre questions avant de choisir",
            items=["Ai-je besoin d'aligner sur deux axes à la fois ?",
                   "Les éléments ont-ils une taille intrinsèque importante ?",
                   "La structure est-elle connue à l'avance ?",
                   "S'agit-il d'un composant interne ou d'une page entière ?"]),
    ],
    "keypoints": [
        "Flexbox organise un axe principal et un axe secondaire.",
        "`justify-content` agit sur l'axe principal, `align-items` sur l'autre.",
        "`flex: 1` répartit l'espace libre entre les enfants.",
        "`min-width: 0` corrige la plupart des débordements de colonnes flex.",
        "`flex-wrap` et `gap` gèrent le passage à la ligne proprement.",
        "`margin-top: auto` colle un pied de carte en bas.",
        "Grid pour la page, Flexbox pour les composants.",
    ],
    "bridge": "Une dimension est maîtrisée. Le chapitre suivant ajoute la seconde : "
              "CSS Grid et les mises en page complètes.",
    "exercises": [
        ex("Barre de navigation responsive",
           "Construisez une barre avec marque à gauche, liens au centre et bouton à "
           "droite, qui passe sur deux lignes en mobile.",
           ["Utilisez Flexbox et `gap`.",
            "Prévoyez le repli sur petit écran.",
            "Vérifiez l'alignement vertical."],
           [("code", """.barre {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 1rem;
}
.barre__liens {
  display: flex;
  gap: 1.25rem;
  list-style: none;
  margin: 0;
  padding: 0;
}
@media (max-width: 40rem) {
  .barre { justify-content: center; }
  .barre__liens { order: 3; flex-basis: 100%; justify-content: center; }
}"""),
            "`flex-wrap: wrap` permet le passage à la ligne ; `flex-basis: 100%` force "
            "les liens à occuper une ligne complète en mobile.",
            "`align-items: center` aligne la marque, les liens et le bouton sur l'axe "
            "secondaire. Sans hauteur fixe, chaque élément garde sa hauteur naturelle."]),
        ex("Galerie de cartes égales",
           "Alignez quatre cartes de hauteurs de texte différentes.",
           ["Les cartes doivent avoir la même hauteur.",
            "Le pied de chaque carte doit être aligné.",
            "Le passage à la ligne doit rester propre."],
           [("code", """.galerie { display: flex; flex-wrap: wrap; gap: 1.25rem; }
.carte {
  flex: 1 1 16rem;
  display: flex;
  flex-direction: column;
  padding: 1.25rem;
  border: 1px solid #e8edf1;
  border-radius: 12px;
}
.carte__pied { margin-top: auto; padding-top: 1rem; }"""),
            "La hauteur égale vient de `align-items: stretch`, valeur par défaut du "
            "conteneur flex.",
            "`margin-top: auto` absorbe l'espace libre restant et colle le pied en bas, "
            "ce qui aligne les pieds entre cartes."]),
        ex("Diagnostiquer un débordement flex",
           "Une colonne flex déborde sur mobile malgré `flex: 1`.",
           ["Identifiez la cause probable.",
            "Proposez deux corrections.",
            "Expliquez pourquoi `overflow: hidden` n'est pas une solution."],
           ["`min-width: auto` empêche la colonne de descendre sous la largeur de son "
            "contenu : un mot long ou une URL suffit à déborder.",
            "Corrections : `min-width: 0` sur la colonne, ou `overflow-wrap: anywhere` "
            "sur le texte longs, ou encore `word-break: break-word`.",
            "`overflow: hidden` masque le contenu au lieu de le rendre lisible : "
            "l'utilisateur perd une partie du texte."],
           level="Diagnostic"),
    ],
    "quiz": [
        quiz("Sur quel axe agit `justify-content` ?",
             ["L'axe secondaire", "L'axe principal", "Les deux", "Aucun"],
             1,
             "`justify-content` répartit sur l'axe principal, dont le sens dépend de "
             "`flex-direction`."),
        quiz("Que signifie `flex: 1` ?",
             ["Une largeur de 1 px", "Grandir, rétrécir, base zéro", "Un seul enfant", "Une colonne"],
             1,
             "`flex: 1` équivaut à `flex: 1 1 0%` : l'élément prend une part égale de "
             "l'espace disponible."),
        quiz("Pourquoi un enfant flex refuse-t-il de rétrécir sous son contenu ?",
             ["À cause de `flex-basis`", "À cause de `min-width: auto`", "À cause de `gap`", "À cause du padding"],
             1,
             "La valeur initiale `min-width: auto` impose la taille minimale du "
             "contenu ; `min-width: 0` lève cette contrainte."),
        quiz("Quel modèle choisir pour une mise en page de page complète ?",
             ["Flexbox", "Grid", "Float", "Table"],
             1,
             "Grid gère deux axes simultanément, ce qui correspond à la structure "
             "globale d'une page."),
        quiz("Comment coller un pied de carte en bas ?",
             ["`position: absolute`", "`margin-top: auto` dans un conteneur colonne", "`vertical-align: bottom`", "`padding-top: 100%`"],
             1,
             "Dans un conteneur flex en colonne, une marge automatique en haut absorbe "
             "l'espace libre."),
    ],
}
