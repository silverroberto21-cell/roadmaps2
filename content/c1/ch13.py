from bookkit.dsl import (box, code, defn, ex, fig, h, ol, p, quiz, table, ul)

CH = {
    "title": "Le modèle de boîte",
    "subtitle": "Tout élément est un rectangle. Comprendre ce rectangle, c'est "
                "comprendre 80 % des problèmes de mise en page.",
    "duration": "3 h 00",
    "level": "Débutant",
    "prereq": "chapitre 12",
    "objectives": [
        "Décomposer un élément en contenu, remplissage, bordure et marge.",
        "Maîtriser `box-sizing` et anticiper les largeurs réelles.",
        "Comprendre la fusion des marges et l'éviter quand elle nuit.",
        "Utiliser les modes d'affichage à bon escient.",
        "Diagnostiquer un débordement ou un espacement inattendu.",
    ],
    "blocks": [
        h(2, "Quatre couches"),
        p("Chaque élément génère une boîte rectangulaire composée de quatre zones "
          "concentriques. De l'intérieur vers l'extérieur : le contenu, le remplissage "
          "(`padding`), la bordure et la marge."),
        fig("stack", "Les quatre couches d'une boîte",
            [("Marge (margin)", "espace extérieur, transparent, jamais cliquable"),
             ("Bordure (border)", "trait visible, épaisseur comprise dans la boîte"),
             ("Remplissage (padding)", "espace intérieur, prend la couleur de fond"),
             ("Contenu", "texte, image, enfant")],
            height=250),
        code(""".carte {
  width: 320px;
  padding: 1.5rem;          /* intérieur : 24 px de chaque côté */
  border: 2px solid #c9d6e2;
  margin: 2rem auto;        /* extérieur : 32 px, centrage horizontal */
}""", "css", "Une boîte complète"),
        table(["Zone", "Propriétés", "Couleur de fond", "Zone cliquable"],
              [["Contenu", "`width`, `height`", "Oui (via l'élément)", "Oui"],
               ["Padding", "`padding`, `padding-inline`", "Oui", "Oui"],
               ["Bordure", "`border`, `outline`", "Couleur de la bordure", "Oui"],
               ["Marge", "`margin`, `margin-block`", "Transparente", "Non"]],
              widths=[2.4, 4.4, 3.0, 2.6], first_col_bold=True,
              caption="Les quatre zones et leurs propriétés"),
        p("La marge est la seule zone qui n'appartient pas à l'élément : elle sépare, "
          "mais ne reçoit ni couleur ni clic. Confondre marge et remplissage produit "
          "des boutons dont la zone active est trop petite, ou des cartes dont le fond "
          "déborde."),
        defn("Modèle de boîte", "Règle de calcul qui détermine l'encombrement total "
                                "d'un élément à partir de son contenu, de son "
                                "remplissage, de ses bordures et de ses marges."),

        h(2, "box-sizing : la décision structurante"),
        p("Par défaut, `width` désigne la largeur du **contenu** : ajouter 24 pixels de "
          "remplissage de chaque côté fait une boîte de 48 pixels plus large. Cette "
          "règle surprend, et casse les grilles en pourcentage."),
        code("""/* Le comportement par défaut */
.boite {
  width: 300px;
  padding: 20px;
  border: 2px solid;
}
/* Largeur réelle : 300 + 40 + 4 = 344 px */

/* Le comportement attendu par presque tout le monde */
*, *::before, *::after {
  box-sizing: border-box;
}
.boite {
  width: 300px;
  padding: 20px;
  border: 2px solid;
}
/* Largeur réelle : 300 px, contenu = 256 px */""", "css",
             "La règle universelle qui simplifie tous les calculs"),
        box("retenir", "Toujours`border-box`",
            "Placez `box-sizing: border-box` sur tous les éléments dès le début du "
            "projet. Cette seule ligne évite la majorité des débordements de grille et "
            "des largeurs incohérentes."),
        fig("compare", "Deux modèles, deux résultats",
            ("content-box (défaut)", ["300 px de contenu", "+ 40 px de padding",
                                      "= 344 px au total"],
             "border-box", ["300 px au total", "padding inclus", "contenu = 256 px"]),
            height=195),

        h(2, "Marges, remplissages et raccourcis"),
        p("Les propriétés logiques (`margin-inline`, `padding-block`) remplacent "
          "progressivement les propriétés physiques (`margin-left`, `padding-top`). "
          "Elles s'adaptent au sens d'écriture : un site en arabe se met en page de "
          "droite à gauche sans feuille supplémentaire."),
        table(["Raccourci", "Signification", "Équivalent logique"],
              [["`margin: 1rem`", "4 côtés", "`margin: 1rem`"],
               ["`margin: 1rem 2rem`", "vertical / horizontal", "`margin-block` / `margin-inline`"],
               ["`margin: 1rem 2rem 3rem`", "haut / horiz. / bas", "—"],
               ["`margin: 1rem 2rem 3rem 4rem`", "haut, droite, bas, gauche", "—"],
               ["`padding-inline`", "gauche et droite logiques", "selon le sens d'écriture"],
               ["`margin-block`", "haut et bas logiques", "—"],
               ["`gap`", "espace entre éléments flex ou grid", "recommandé"]],
              widths=[4.0, 4.2, 3.6], first_col_bold=True,
              caption="Raccourcis de marges et propriétés logiques"),
        code(""".carte {
  padding-block: 1.5rem;
  padding-inline: 1.25rem;
  margin-block-end: 2rem;
  border-inline-start: 4px solid #e0a21b;
}""", "css", "Une boîte écrite en propriétés logiques"),
        p("Préférez `gap` aux marges entre éléments d'une grille ou d'un flex : il "
          "n'ajoute d'espace qu'entre les enfants, jamais sur les bords, ce qui évite "
          "les corrections au cas par cas."),

        h(2, "Fusion des marges"),
        p("Deux marges verticales adjacentes fusionnent en une seule, dont la taille "
          "est la plus grande des deux. Ce comportement, hérité de la typographie, "
          "surprend lorsqu'on attend une somme."),
        fig("flow", "La fusion des marges en action",
            ["Deux paragraphes : marge basse 24 px, marge haute 16 px",
             "Les marges fusionnent : un espace de 24 px, pas de 40 px",
             "Trois éléments ou plus : la plus grande marge l'emporte",
             "Un conteneur avec padding ou bordure bloque la fusion"],
            height=245),
        code("""/* Fusion : l'espace fait 24 px */
p { margin-block: 16px 24px; }

/* Pas de fusion à l'intérieur d'un conteneur bordé */
.conteneur { padding: 1px; }   /* artifice courant */
.conteneur { border: 1px solid transparent; }  /* plus propre */

/* Solution moderne : flow-root crée un contexte de formatage */
.conteneur { display: flow-root; }""", "css", "Trois façons de maîtriser la fusion"),
        box("attention", "La fusion ne s'applique pas partout",
            "Les marges ne fusionnent ni entre éléments flex ou grid, ni à travers un "
            "`padding` ou une bordure, ni lorsque `overflow` crée un contexte de "
            "formatage. C'est pourquoi un même code se comporte différemment selon le "
            "conteneur."),
        p("La marge d'un enfant peut aussi « s'échapper » de son parent et décaler "
          "tout le bloc. `display: flow-root` sur le parent supprime ce phénomène sans "
          "artifice."),

        h(2, "Modes d'affichage"),
        p("La propriété `display` détermine la façon dont une boîte se comporte : "
          "bloc, ligne, flex, grid, ou aucun rendu. Choisir le bon mode évite les "
          "contournements."),
        table(["Valeur", "Comportement", "Usage"],
              [["`block`", "Pleine largeur, sauts de ligne", "Sections, paragraphes"],
               ["`inline`", "Suit le flux du texte, marges verticales ignorées", "Liens, emphase"],
               ["`inline-block`", "En ligne, mais avec dimensions", "Puces, badges"],
               ["`flex`", "Aligne les enfants sur un axe", "Barres, cartes, centrage"],
               ["`grid`", "Aligne les enfants sur deux axes", "Mises en page"],
               ["`none`", "Retire du rendu et de l'arbre d'accessibilité", "Masquage"],
               ["`contents`", "Supprime la boîte, conserve les enfants", "Cas particuliers"]],
              widths=[2.6, 5.0, 3.8], first_col_bold=True,
              caption="Sept modes d'affichage et leur usage"),
        code(""".badge {
  display: inline-block;
  padding: .15rem .5rem;
  border-radius: 999px;
  background: #e8edf1;
}
/* Un inline pur ignorerait ce padding vertical : d'où inline-block */

[hidden] { display: none; }
/* ne pas confondre avec visibility: hidden, qui réserve l'espace */""", "css",
             "Le cas typique du badge"),
        p("`display: none` retire l'élément de la page et de l'arbre d'accessibilité : "
          "un lecteur d'écran ne l'annonce plus. `visibility: hidden` le rend invisible "
          "mais conserve l'espace — et le retire aussi de l'arbre. Pour masquer "
          "visuellement sans priver les lecteurs d'écran, on utilise une classe de "
          "masquage spécifique."),
        code(""".visually-hidden {
  position: absolute;
  width: 1px; height: 1px;
  margin: -1px; padding: 0;
  overflow: hidden;
  clip-path: inset(50%);
  white-space: nowrap;
  border: 0;
}""", "css", "Masquer visuellement, sans masquer aux technologies d'assistance"),

        h(2, "Débordements et dimensions"),
        p("Lorsqu'un contenu est plus large que sa boîte, il déborde. Quatre "
          "propriétés contrôlent ce comportement : `overflow-x`, `overflow-y`, "
          "`overflow` et `clip`."),
        code(""".extrait {
  max-height: 12rem;
  overflow: auto;              /* barres si nécessaire */
  overscroll-behavior: contain; /* évite le défilement en chaîne */
}

.chiffre {
  font-variant-numeric: tabular-nums;
  min-width: 4ch;              /* stabilité des colonnes */
}""", "css", "Contenir un débordement sans le subir"),
        table(["Symptôme", "Cause fréquente", "Correction"],
              [["Défilement horizontal de la page", "Enfant plus large que le parent", "`max-width: 100%`, `min-width: 0`"],
               ["Texte qui dépasse d'un bouton", "Largeur insuffisante", "`padding`, `white-space`"],
               ["Image qui casse la grille", "Largeur intrinsèque", "`max-width: 100%; height: auto`"],
               ["Colonne flex qui refuse de rétrécir", "`min-width: auto` par défaut", "`min-width: 0`"],
               ["Élément collé au bord", "Marge fusionnée", "`flow-root`, padding"]],
              widths=[3.8, 3.8, 3.6], first_col_bold=True,
              caption="Cinq débordements classiques et leur correction"),
        box("methode", "Le test du contour",
            "Ajoutez temporairement `outline: 1px solid red` à tous les éléments "
            "(`* { outline: 1px solid red }`) pour visualiser les boîtes réelles. "
            "Retirez-la ensuite : c'est un outil de diagnostic, pas un style."),
    ],
    "keypoints": [
        "Toute boîte se compose de contenu, padding, bordure et marge.",
        "`box-sizing: border-box` simplifie tous les calculs de largeur.",
        "La marge est extérieure et transparente ; le padding est intérieur et coloré.",
        "Les marges verticales fusionnent : ce n'est pas un bug.",
        "`display: flow-root` bloque la fusion sans artifice.",
        "`display: none` retire l'élément de l'arbre d'accessibilité.",
        "Un débordement se diagnostique en visualisant les contours.",
    ],
    "bridge": "La boîte est comprise. Le chapitre suivant l'habille : bordures, ombres "
              "et effets de profondeur.",
    "exercises": [
        ex("Calculer des largeurs",
           "Un conteneur mesure 900 px. Trois cartes ont `width: 33.33%`, "
           "`padding: 16px` et `border: 1px`. Tiennent-elles sur une ligne ?",
           ["Calculez avec le modèle par défaut.",
            "Calculez avec `border-box`.",
            "Proposez deux corrections."],
           ["Modèle par défaut : chaque carte occupe 300 px de contenu + 32 px de "
            "padding + 2 px de bordure = 334 px, soit 1002 px pour trois : débordement.",
            "Avec `border-box`, chaque carte occupe 300 px, soit 900 px au total : "
            "elles tiennent exactement.",
            "Deux corrections : activer `box-sizing: border-box` globalement, ou "
            "utiliser `display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem` "
            "en laissant la grille gérer les largeurs."]),
        ex("Reproduire une carte",
           "Reproduisez cette carte : 320 px de large, fond blanc, bordure de 1 px, "
           "coins arrondis, ombre douce, image en haut, texte avec marges internes.",
           ["Utilisez `border-box`.",
            "Ajoutez un espacement interne cohérent.",
            "Vérifiez la largeur réelle dans l'inspecteur."],
           [("code", """.carte {
  box-sizing: border-box;
  width: min(320px, 100%);
  background: #fff;
  border: 1px solid #e8edf1;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 6px 20px rgb(15 46 76 / 10%);
}
.carte__image { display: block; width: 100%; height: 180px; object-fit: cover; }
.carte__corps { padding: 1.25rem; }
.carte__titre { margin: 0 0 .5rem; font-size: 1.125rem; }"""),
            "`overflow: hidden` sur la carte empêche l'image de dépasser des coins "
            "arrondis.",
            "Dans l'inspecteur, la largeur de la boîte doit afficher 320 px, padding "
            "et bordure compris : c'est la preuve que `border-box` est actif."],
           level="Application"),
        ex("Diagnostiquer un débordement",
           "La page défile horizontalement sur mobile, sans qu'aucune image ne soit "
           "visiblement trop large.",
           ["Proposez trois causes possibles.",
            "Indiquez la commande CSS de diagnostic.",
            "Corrigez la cause la plus probable."],
           ["Causes : un élément en `width: 100vw` (dépasse de la largeur de la barre "
            "de défilement), une `grid` avec des colonnes `1fr` contenant un élément "
            "insécable, ou une marge négative.",
            "Ajoutez `* { outline: 1px solid red }` puis repérez l'élément qui sort "
            "de l'écran. L'inspecteur affiche aussi la largeur du document.",
            ("code", """html, body { overflow-x: hidden; }  /* masque le symptôme */
/* Correction réelle : */
.grille { grid-template-columns: minmax(0, 1fr); }
.large { width: 100%; max-width: 100%; }""")],
           level="Diagnostic"),
    ],
    "quiz": [
        quiz("Que comprend la largeur d'un élément avec `box-sizing: border-box` ?",
             ["Le contenu seul", "Contenu + padding + bordure", "Contenu + marge", "Tout, marge comprise"],
             1,
             "`border-box` inclut padding et bordure dans la largeur déclarée ; la "
             "marge reste extérieure."),
        quiz("Que devient l'espace entre deux marges verticales de 20 px et 30 px ?",
             ["50 px", "30 px", "20 px", "0 px"],
             1,
             "Les marges verticales adjacentes fusionnent : la plus grande l'emporte, "
             "soit 30 px."),
        quiz("Quelle valeur de `display` retire l'élément de l'arbre d'accessibilité ?",
             ["`none`", "`hidden`", "`contents`", "`inline-block`"],
             0,
             "`display: none` supprime l'élément du rendu et de l'arbre "
             "d'accessibilité ; `visibility: hidden` aussi, mais conserve l'espace."),
        quiz("Quel mode d'affichage empêche la fusion des marges avec l'extérieur ?",
             ["`display: block`", "`display: flow-root`", "`display: inline`", "`display: table`"],
             1,
             "`flow-root` crée un contexte de formatage de bloc qui confine les marges "
             "à l'intérieur du conteneur."),
        quiz("Quelle propriété espace les enfants d'un conteneur flex sans marge "
             "extérieure ?",
             ["`margin`", "`gap`", "`padding`", "`border-spacing`"],
             1,
             "`gap` n'ajoute de l'espace qu'entre les éléments, jamais sur les bords "
             "du conteneur."),
    ],
}
