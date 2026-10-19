from bookkit.dsl import (box, code, defn, ex, fig, h, ol, p, quiz, table, ul)

CH = {
    "title": "Unités fluides et rythme vertical",
    "subtitle": "Composer entre deux tailles d'écran : ni sauts brutaux, ni mesures "
                "arbitraires.",
    "duration": "2 h 15",
    "level": "Intermédiaire",
    "prereq": "chapitre 21",
    "objectives": [
        "Utiliser `clamp()`, `min()`, `max()` à bon escient.",
        "Construire une échelle fluide de tailles et d'espacements.",
        "Établir un rythme vertical cohérent.",
        "Éviter les pièges des unités relatives imbriquées.",
        "Vérifier les compositions intermédiaires, pas seulement les extrêmes.",
    ],
    "blocks": [
        h(2, "Trois fonctions de bornage"),
        p("`min()`, `max()` et `clamp()` comparent des valeurs et en choisissent une. "
          "Elles remplacent la plupart des media queries de typographie."),
        table(["Fonction", "Effet", "Exemple"],
              [["`min(a, b)`", "La plus petite", "`width: min(100%, 40rem)`"],
               ["`max(a, b)`", "La plus grande", "`padding: max(1rem, 2vw)`"],
               ["`clamp(min, idéal, max)`", "Bornée entre deux valeurs", "`font-size: clamp(1rem, 2vw, 1.5rem)`"]],
              widths=[3.4, 3.4, 5.0], first_col_bold=True,
              caption="Trois fonctions de comparaison"),
        code(""".conteneur { width: min(100% - 2rem, 68ch); margin-inline: auto; }
h1 { font-size: clamp(2rem, 1.2rem + 3.2vw, 3.75rem); line-height: 1.05; }
h2 { font-size: clamp(1.5rem, 1.1rem + 1.6vw, 2.25rem); line-height: 1.15; }
.section { padding-block: clamp(2rem, 5vw, 5rem); }""", "css",
             "Un ensemble fluide, sans media query"),
        p("La valeur idéale s'écrit sous la forme `base + pente × vw`. La pente "
          "détermine la vitesse de croissance ; la base ajuste le point de départ. Une "
          "pente de 3vw signifie que la taille augmente de 3 % de la largeur de la "
          "fenêtre."),
        fig("compare", "Deux façons de faire varier une taille",
            ("AVEC MEDIA QUERIES", ["Sauts visibles aux seuils", "Deux valeurs figées",
                                    "Code plus long"],
             "AVEC CLAMP", ["Croissance continue", "Bornée", "Une ligne"]),
            height=185),

        h(2, "Construire une échelle fluide"),
        p("Une échelle fluide se définit une fois, dans les jetons, puis se réutilise "
          "partout. Elle évite les tailles inventées au cas par cas."),
        code(""":root {
  --echelle-ratio: 1.2;
  --texte-min: 1rem;
  --texte-max: 1.125rem;

  --taille-0: clamp(1rem, .96rem + .2vw, 1.125rem);
  --taille-1: clamp(1.2rem, 1.1rem + .5vw, 1.45rem);
  --taille-2: clamp(1.44rem, 1.26rem + .9vw, 1.9rem);
  --taille-3: clamp(1.73rem, 1.44rem + 1.4vw, 2.5rem);
  --taille-4: clamp(2.07rem, 1.63rem + 2.2vw, 3.3rem);
}""", "css", "Une échelle de cinq niveaux, calculée"),
        p("Entre 320 et 1440 pixels, chaque niveau évolue continûment. Au-delà de "
          "1440, les tailles sont plafonnées : un écran de 4K n'a pas besoin de titres "
          "de 200 pixels."),
        box("attention", "Le piège du zoom",
            "Les unités `vw` ne réagissent pas au zoom du navigateur de la même façon "
            "que les `rem`. Utilisez `rem` dans la formule de `clamp()` (par exemple "
            "`1.2rem + 2vw`), jamais `vw` seul, pour préserver l'accessibilité."),

        h(2, "Rythme vertical"),
        p("Le rythme vertical est la régularité des espacements entre blocs. Il se "
          "construit à partir d'une unité de base — souvent la hauteur de ligne du "
          "corps — et de multiples de cette unité."),
        code("""body {
  --lh: 1.6;
  --unite: calc(1rem * var(--lh));   /* 25,6 px si la police fait 16 px */
  line-height: var(--lh);
}
h1 { margin-block: calc(var(--unite) * 2) var(--unite); }
h2 { margin-block: calc(var(--unite) * 1.5) calc(var(--unite) * .5); }
p  { margin-block: 0 var(--unite); }""", "css", "Un rythme fondé sur l'interligne"),
        table(["Espacement", "Usage", "Valeur type"],
              [["Intra-composant", "Entre titre et texte", "0,5 unité"],
               ["Inter-paragraphes", "Entre deux paragraphes", "1 unité"],
               ["Inter-sections", "Entre deux blocs distincts", "2 unités"],
               ["Marge de section", "Avant un titre de niveau 2", "3 unités"]],
              widths=[3.4, 4.4, 3.0], first_col_bold=True,
              caption="Quatre niveaux d'espacement vertical"),
        p("Le rythme ne se voit pas consciemment, mais son absence se remarque : des "
          "espacements irréguliers font paraître la page brouillonne, même avec une "
          "belle typographie."),

        h(2, "Unités imbriquées et pièges"),
        p("Les unités relatives dépendent de leur contexte. Une taille en `em` dans un "
          "élément dont la police est déjà en `em` se multiplie : c'est une source "
          "classique d'effet boule de neige."),
        code("""/* Effet boule de neige : chaque niveau réduit de 90 % */
.liste { font-size: .9em; }
.liste .liste { font-size: .9em; }   /* 81 % du parent */
.liste .liste .liste { font-size: .9em; }  /* 73 % */

/* Stable : rem partout */
.liste { font-size: .9rem; }
.liste .liste { font-size: .9rem; }  /* identique */""", "css",
             "`em` se compose, `rem` ne se compose pas"),
        defn("Unité relative", "Unité dont la valeur dépend d'un contexte : `em` dépend "
                               "de la police de l'élément, `rem` de la police racine, "
                               "`%` du parent, `vw` de la fenêtre."),
        p("Les `em` restent utiles pour un composant autonome : un bouton dont le "
          "rembourrage est en `em` s'agrandit proportionnellement si l'on augmente sa "
          "taille de police. Les `rem` conviennent mieux aux espacements globaux."),

        h(2, "Vérifier les états intermédiaires"),
        p("Tester à 320 et 1440 pixels ne suffit pas : les problèmes apparaissent "
          "souvent entre les deux, aux largeurs « moyennes » que personne ne teste."),
        code("""/* Un utilitaire de test temporaire */
* { outline: 1px solid rgb(255 0 0 / 25%); }

/* Dans l'inspecteur, redimensionner par pas de 40 px et observer :
   - les retours à la ligne
   - les éléments qui se chevauchent
   - les titres qui passent à trois lignes */""", "css",
             "Visualiser les boîtes pendant les tests de largeur"),
        table(["Largeur", "Ce qu'on teste", "Point d'attention"],
              [["320 px", "Lisibilité minimale", "Débordement, taille de police"],
               ["480 px", "Téléphone paysage", "Boutons trop larges"],
               ["768 px", "Tablette portrait", "Grilles à deux colonnes"],
               ["1024 px", "Ordinateur portable", "Mesure de lecture"],
               ["1440 px", "Grand écran", "Contenu trop étiré"],
               ["1920 px", "Écran large", "Marges excessives"]],
              widths=[2.6, 4.4, 4.0], first_col_bold=True,
              caption="Six largeurs de test et ce qu'elles révèlent"),
        box("methode", "La règle des quatre largeurs",
            "Testez toujours 320, 768, 1024 et la largeur de votre écran. Quatre "
            "captures suffisent à repérer 90 % des problèmes de composition."),
    ],
    "keypoints": [
        "`clamp()` remplace la plupart des media queries de typographie.",
        "La formule idéale s'écrit `base + pente × vw`, en `rem` pour la base.",
        "Une échelle fluide se définit une fois dans les jetons.",
        "Le rythme vertical se construit sur un multiple de l'interligne.",
        "`em` se compose, `rem` non : choisir selon le besoin.",
        "Tester les largeurs intermédiaires, pas seulement les extrêmes.",
        "Ne jamais utiliser `vw` seul pour une taille de texte.",
    ],
    "bridge": "La composition est fluide et régulière. Le chapitre suivant traite "
              "l'accessibilité de façon systématique, au-delà des bonnes intentions.",
    "exercises": [
        ex("Construire une échelle fluide",
           "Créez cinq tailles de titre fluides entre 360 et 1280 pixels.",
           ["Utilisez `clamp()` et des `rem`.",
            "Définissez des variables réutilisables.",
            "Vérifiez la croissance à 360, 600, 900 et 1280."],
           [("code", """:root {
  --t1: clamp(1.25rem, 1.16rem + .38vw, 1.5rem);
  --t2: clamp(1.5rem, 1.32rem + .78vw, 2rem);
  --t3: clamp(1.85rem, 1.55rem + 1.3vw, 2.75rem);
  --t4: clamp(2.3rem, 1.8rem + 2.2vw, 3.75rem);
  --t5: clamp(2.9rem, 2.1rem + 3.5vw, 5rem);
}"""),
            "Chaque niveau croît d'environ 20 % à chaque cran à 360 px, et les écarts "
            "s'ouvrent sur grand écran.",
            "Les bornes maximales évitent qu'un titre de niveau 1 occupe trois lignes "
            "sur un écran de 1440 pixels."]),
        ex("Établir un rythme vertical",
           "Un article enchaîne titre, sous-titre, paragraphes, citation et liste.",
           ["Définissez une unité de rythme.",
            "Appliquez des marges en multiples de cette unité.",
            "Vérifiez la régularité à deux tailles d'écran."],
           [("code", """article {
  --unite: 1.6rem;
  line-height: 1.6;
}
article h2 { margin-block: calc(var(--unite) * 2) var(--unite); }
article p { margin-block: 0 var(--unite); }
article blockquote {
  margin-block: calc(var(--unite) * 1.5);
  padding-inline-start: var(--unite);
  border-inline-start: 3px solid #e0a21b;
}"""),
            "Une unité unique et des multiples simples produisent une page régulière "
            "sans effort de calcul.",
            "Les marges fusionnent entre paragraphes : `margin-block: 0 var(--unite)` "
            "évite le doublement."]),
        ex("Diagnostiquer un effet boule de neige",
           "Les listes imbriquées deviennent illisibles au troisième niveau.",
           ["Identifiez la cause.",
            "Proposez une correction en `rem`.",
            "Indiquez dans quel cas `em` reste préférable."],
           ["Chaque niveau multiplie la taille par 0,9 : 0,9³ ≈ 0,73, ce qui rend le "
            "texte trop petit.",
            "Remplacer par `font-size: .95rem` à chaque niveau donne une taille "
            "stable, indépendante de la profondeur.",
            "`em` reste préférable pour un composant dont tous les espacements doivent "
            "suivre la taille de police locale, comme un bouton."],
           level="Diagnostic"),
    ],
    "quiz": [
        quiz("Que fait `clamp(1rem, 2vw, 1.5rem)` ?",
             ["Choisit toujours 1rem", "Borne une valeur fluide entre 1rem et 1,5rem",
              "Multiplie la taille par 2", "Désactive le zoom"],
             1,
             "La valeur idéale suit la largeur, mais reste comprise entre les deux "
             "bornes."),
        quiz("Pourquoi éviter `font-size: 2vw` seul ?",
             ["C'est trop grand", "Le texte ne respecte pas le zoom et devient illisible",
              "Ce n'est pas supporté", "Cela ralentit le rendu"],
             1,
             "Une taille uniquement liée à la fenêtre ignore les préférences de "
             "l'utilisateur et peut devenir minuscule."),
        quiz("Quelle unité reste stable quel que soit le niveau d'imbrication ?",
             ["`em`", "`rem`", "`%`", "`ex`"],
             1,
             "`rem` se rapporte toujours à la racine, contrairement à `em` qui dépend "
             "du parent."),
        quiz("Sur quoi se construit un rythme vertical ?",
             ["La taille des images", "Un multiple de l'interligne",
              "La largeur de la fenêtre", "La couleur de fond"],
             1,
             "L'unité de rythme dérive de la hauteur de ligne du corps de texte, ce "
             "qui aligne les blocs sur une grille invisible."),
        quiz("Quelles largeurs tester en priorité ?",
             ["Seulement 1920", "320, 768, 1024 et la largeur de l'écran",
              "Uniquement 375", "Toutes les largeurs possibles"],
             1,
             "Quatre largeurs couvrent l'essentiel des problèmes de composition."),
    ],
}
