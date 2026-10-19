from bookkit.dsl import (box, code, defn, ex, fig, h, ol, p, quiz, table, ul)

CH = {
    "title": "Polices web et typographie fine",
    "subtitle": "Charger les bonnes polices, éviter les décalages de mise en page et "
                "soigner le texte à l'écran.",
    "duration": "2 h 45",
    "level": "Intermédiaire",
    "prereq": "chapitre 11",
    "objectives": [
        "Choisir un format de police adapté au Web.",
        "Charger une police sans bloquer le rendu.",
        "Maîtriser les métriques de substitution.",
        "Utiliser `font-variation-settings` à bon escient.",
        "Éviter les décalages de contenu.",
    ],
    "blocks": [
        h(2, "Format et chargement"),
        p("Une police web se déclare avec `@font-face` : un nom de famille, une source et "
          "des descripteurs. Le format `woff2` est compressé et universellement pris en "
          "charge ; inutile de servir plusieurs formats sauf contrainte ancienne."),
        code("""@font-face {
  font-family: "Inter";
  src: url("/polices/inter-var.woff2") format("woff2");
  font-weight: 100 900;          /* police variable */
  font-style: normal;
  font-display: swap;
  unicode-range: U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC;
}""", "css", "Une déclaration complète"),
        table(["Descripteur", "Rôle", "Erreur fréquente"],
              [["`src`", "Fichier et format", "Format non déclaré"],
               ["`font-weight`", "Graisses couvertes", "Déclarer une seule graisse"],
               ["`font-display`", "Comportement de chargement", "Absent : texte invisible"],
               ["`unicode-range`", "Sous-ensemble", "Fichier trop lourd"],
               ["`size-adjust`", "Métriques de repli", "Aucun ajustement"]],
              widths=[4.2, 4.8, 4.6], first_col_bold=True,
              caption="Cinq descripteurs"),
        defn("`font-display`", "Stratégie d'affichage pendant le chargement du fichier : "
                               "`block` masque le texte, `swap` affiche immédiatement la "
                               "police de secours, `fallback` et `optional` arbitrent "
                               "différemment entre vitesse et fidélité."),
        code("""/* swap : le texte est lisible tout de suite */
@font-face { font-family: "Titre"; src: url("titre.woff2"); font-display: swap; }

/* optional : si la police n'arrive pas vite, elle n'est pas utilisée */
@font-face { font-family: "Corps"; src: url("corps.woff2"); font-display: optional; }""",
             "css", "Deux stratégies"),
        box("attention", "`font-display: block` masque le texte",
            "Pendant le chargement, le texte est invisible : pendant trois secondes, "
            "l'utilisateur voit des blocs vides. Réservez ce mode aux titres courts dont "
            "le fichier est local et rapide."),

        h(2, "Métriques et substitution"),
        p("Le passage de la police de secours à la police chargée provoque un décalage de "
          "mise en page si les métriques diffèrent. Deux réglages réduisent ce "
          "phénomène."),
        code("""/* Ajuster la police de repli aux métriques de la police cible */
@font-face {
  font-family: "Inter-fallback";
  src: local("Arial");
  size-adjust: 107%;
  ascent-override: 90%;
  descent-override: 22%;
  line-gap-override: 0%;
}

:root { --police-texte: "Inter", "Inter-fallback", system-ui, sans-serif; }""",
             "css", "Un repli ajusté"),
        table(["Réglage", "Effet", "Limite"],
              [["`size-adjust`", "Corrige la taille relative", "Ne règle pas l'interligne"],
               ["`ascent-override`", "Aligne la ligne de base", "Valeurs à mesurer"],
               ["`preload`", "Charge plus tôt", "Consomme de la bande passante"],
               ["`unicode-range`", "Charge par sous-ensemble", "Découpage à maintenir"]],
              widths=[4.6, 5.0, 4.4], first_col_bold=True,
              caption="Quatre réglages"),
        code("""<!-- Précharger uniquement la police du titre -->
<link rel="preload" href="/polices/titre.woff2" as="font" type="font/woff2"
      crossorigin>

<!-- Ne pas précharger plus de deux fichiers : la bande passante est partagée -->
<!-- La police doit être servie avec un cache long et une empreinte dans le nom -->""",
             "html", "Deux règles de préchargement"),
        defn("Décalage cumulé de mise en page", "Somme des déplacements visuels subis par "
                                                "le contenu pendant le chargement, mesurée "
                                                "par la métrique CLS. Une police à métriques "
                                                "différentes en est une cause fréquente."),

        h(2, "Polices variables"),
        p("Une police variable contient plusieurs graisses et largeurs dans un seul "
          "fichier. On l'utilise par `font-weight` et `font-stretch`, et par les axes "
          "personnalisés du dessinateur."),
        code("""@font-face {
  font-family: "Recia";
  src: url("/polices/recia-var.woff2") format("woff2");
  font-weight: 300 900;
  font-stretch: 75% 125%;
}

h2 {
  font-family: "Recia", serif;
  font-weight: 620;              /* valeur intermédiaire */
  font-stretch: 105%;
  font-optical-sizing: auto;     /* axe optique si disponible */
}

/* Axes personnalisés : à utiliser avec parcimonie */
.surtitre {
  font-variation-settings: "wght" 480, "slnt" -6;
}""", "css", "Une police variable"),
        table(["Usage", "Recommandation", "Raison"],
              [["Graisse", "`font-weight`", "Interpolation native"],
               ["Largeur", "`font-stretch`", "Interpolation native"],
               ["Style", "`font-style: oblique -6deg`", "Standard"],
               ["Axe propriétaire", "`font-variation-settings`", "Non interpolable"]],
              widths=[4.4, 5.0, 4.6], first_col_bold=True,
              caption="Quatre usages"),
        box("pratique", "Un fichier variable peut être plus lourd que deux statiques",
            "Une police variable complète pèse parfois 200 à 400 ko. Pour n'utiliser que "
            "deux graisses, deux fichiers statiques sous-ensemble peuvent être plus "
            "légers : mesurez."),

        h(2, "Typographie à l'écran"),
        p("La lisibilité d'un paragraphe dépend de trois réglages : la taille, "
          "l'interligne et la longueur de ligne. Un texte trop large fatigue, un texte "
          "trop étroit hache le rythme."),
        code(""":root {
  --mesure: 68ch;            /* longueur de ligne confortable */
  --corps: clamp(1rem, 0.95rem + 0.25vw, 1.125rem);
}

.article p {
  max-inline-size: var(--mesure);
  font-size: var(--corps);
  line-height: 1.6;
  text-wrap: pretty;         /* évite les lignes orphelines */
  hyphens: auto;
}

h1 { text-wrap: balance; }   /* équilibre les lignes d'un titre */""", "css",
             "Trois réglages"),
        table(["Réglage", "Valeur usuelle", "Effet"],
              [["Longueur de ligne", "45 à 75 caractères", "Confort de lecture"],
               ["Interligne", "1,4 à 1,7", "Respiration verticale"],
               ["Taille du corps", "16 à 19 px", "Lisibilité mobile"],
               ["Espacement des mots", "Par défaut", "À éviter de modifier"],
               ["Justification", "Non recommandée à l'écran", "Rivières blanches"]],
              widths=[4.6, 4.6, 4.8], first_col_bold=True,
              caption="Cinq réglages"),
        code("""/* Ne pas confondre espacement et justification */
.texte-justifie {
  text-align: justify;
  text-align-last: left;
  hyphens: auto;            /* indispensable pour éviter les trous */
}

/* Substituer des chiffres tabulaires dans un tableau */
.chiffres { font-variant-numeric: tabular-nums; }

/* Petites capitales réelles plutôt que simulées */
.petites-caps { font-variant-caps: all-small-caps; }""", "css",
             "Quatre détails typographiques"),
        box("methode", "Charger des polices sans casser la page",
            items=["Une police pour le texte, une pour les titres, pas plus.",
                   "Sous-ensembles et `unicode-range` pour alléger.",
                   "`font-display: swap` pour le corps, `optional` pour le décor.",
                   "Précharger au maximum deux fichiers.",
                   "Ajuster `size-adjust` pour limiter le décalage."]),
    ],
    "keypoints": [
        "`woff2` est le format de référence.",
        "`font-display` décide de la visibilité pendant le chargement.",
        "Une police de repli aux mauvaises métriques provoque un décalage.",
        "`size-adjust` et `ascent-override` corrigent ce décalage.",
        "Une police variable couvre plusieurs graisses en un fichier.",
        "Les axes propriétaires ne s'interpolent pas.",
        "Une ligne de 45 à 75 caractères reste confortable.",
        "La justification à l'écran exige la césure.",
    ],
    "bridge": "Le texte est soigné. Le chapitre suivant vérifie que l'interface fonctionne "
              "vraiment.",
    "exercises": [
        ex("Déclarer une police avec repli ajusté",
           "La police Inter doit remplacer Arial sans décalage visible.",
           ["Déclarez la police.",
            "Ajoutez une famille de repli.",
            "Ajustez la taille."],
           [("css", """@font-face {
  font-family: "Inter";
  src: url("/polices/inter-var.woff2") format("woff2");
  font-weight: 100 900;
  font-display: swap;
}

@font-face {
  font-family: "Inter-fallback";
  src: local("Arial");
  size-adjust: 107%;
  ascent-override: 90%;
  descent-override: 22%;
  line-gap-override: 0%;
}

body { font-family: "Inter", "Inter-fallback", system-ui, sans-serif; }"""),
            "La famille de repli doit être déclarée avant utilisation dans la pile.",
            "Les pourcentages se mesurent en comparant les hauteurs de ligne des deux "
            "polices."]),
        ex("Mesurer l'impact d'une police",
           "Le titre principal provoque un décalage visible au chargement.",
           ["Préchargez le fichier.",
            "Passez en `optional`.",
            "Comparez la métrique."],
           [("html", """<link rel="preload" href="/polices/titre.woff2" as="font"
      type="font/woff2" crossorigin>

<style>
@font-face {
  font-family: "Titre";
  src: url("/polices/titre.woff2") format("woff2");
  font-display: optional;   /* pas de bascule si le fichier est lent */
}
</style>"""),
            "`optional` évite complètement la bascule : la police est utilisée si elle "
            "arrive dans la fenêtre initiale.",
            "Le préchargement réduit fortement le risque de bascule."],
           level="Performance"),
        ex("Corriger une typographie d'article",
           "Les paragraphes sont trop larges et justifiés sans césure.",
           ["Limitez la mesure.",
            "Activez la césure.",
            "Équilibrez les titres."],
           [("css", """.article p {
  max-inline-size: 68ch;
  line-height: 1.6;
  text-align: justify;
  hyphens: auto;
  text-wrap: pretty;
}

.article h2 { text-wrap: balance; }

@media (max-width: 40rem) {
  .article p { text-align: left; }   /* la justification fatigue sur mobile */
}"""),
            "Sur petit écran, la justification crée des trous : revenez à l'alignement à "
            "gauche.",
            "`text-wrap: pretty` réduit les lignes orphelines en fin de paragraphe."]),
    ],
    "quiz": [
        quiz("Quel format de police est recommandé pour le Web ?",
             ["TTF", "WOFF2", "OTF", "EOT"],
             1,
             "Compressé et pris en charge partout."),
        quiz("Que fait `font-display: swap` ?",
             ["Masque le texte", "Affiche le repli immédiatement",
              "Bloque le rendu", "Charge en arrière-plan"],
             1,
             "Le texte est lisible tout de suite, puis la police remplace le repli."),
        quiz("À quoi sert `size-adjust` ?",
             ["Réduire le poids", "Aligner les métriques du repli",
              "Changer la graisse", "Précharger"],
             1,
             "Il limite le décalage lors de la substitution."),
        quiz("Quelle longueur de ligne est confortable ?",
             ["20 à 30 caractères", "45 à 75 caractères", "90 à 120 caractères",
              "Peu importe"],
             1,
             "Au-delà, l'œil perd le début de la ligne suivante."),
        quiz("Que ne permet pas `font-variation-settings` ?",
             ["Choisir un axe", "Interpoler une transition CSS",
              "Régler une graisse", "Régler une inclinaison"],
             1,
             "Les axes personnalisés ne s'interpolent pas en transition."),
    ],
}
