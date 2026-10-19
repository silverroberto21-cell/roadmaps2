from bookkit.dsl import (box, code, defn, ex, fig, h, ol, p, quiz, table, ul)

CH = {
    "title": "Typographie web",
    "subtitle": "Quatre-vingt-dix pour cent du Web est du texte. Le soigner n'est pas "
                "un luxe, c'est la condition de la lecture.",
    "duration": "2 h 45",
    "level": "Débutant",
    "prereq": "chapitre 10",
    "objectives": [
        "Choisir des polices lisibles et performantes.",
        "Construire une échelle typographique cohérente.",
        "Régler interligne, mesure et espacement pour la lecture.",
        "Charger des polices personnalisées sans dégrader la performance.",
        "Adapter la typographie à l'impression et aux lecteurs d'écran.",
    ],
    "blocks": [
        h(2, "Choisir une police"),
        p("Trois options s'offrent à un projet web : les polices système, les polices "
          "auto-hébergées et les polices de services externes. Le choix engage la "
          "performance, la vie privée et l'identité visuelle."),
        table(["Option", "Avantages", "Inconvénients"],
              [["Polices système", "Aucun téléchargement, rendu immédiat", "Choix limité, rendu variable selon l'OS"],
               ["Auto-hébergement", "Contrôle total, respect de la vie privée", "Poids à optimiser soi-même"],
               ["Service externe", "Catalogue immense, mise en œuvre rapide", "Requête tierce, RGPD à vérifier"]],
              widths=[2.6, 4.4, 4.0], first_col_bold=True,
              caption="Trois stratégies de polices et leurs compromis"),
        code("""/* Pile système : aucun fichier à télécharger */
body {
  font-family: system-ui, -apple-system, "Segoe UI", Roboto,
               "Helvetica Neue", Arial, sans-serif;
}
h1, h2, h3 {
  font-family: "Iowan Old Style", "Palatino Linotype", Georgia, serif;
}""", "css", "Une pile système bien construite"),
        p("La pile liste des familles par ordre de préférence, et se termine toujours "
          "par une famille générique (`serif`, `sans-serif`, `monospace`). Sans cette "
          "dernière, le navigateur choisit lui-même, souvent mal."),
        defn("Police variable", "Fichier unique contenant plusieurs graisses et "
                                "largeurs, animables par l'axe `wght`. Il remplace "
                                "plusieurs fichiers statiques et allège le chargement."),

        h(2, "Charger une police correctement"),
        p("Une police personnalisée est un fichier lourd, souvent 100 à 400 "
          "kilo-octets par graisse. Trois décisions réduisent son coût : limiter les "
          "graisses, sous-ensembler les caractères, et contrôler l'affichage pendant "
          "le chargement."),
        code("""@font-face {
  font-family: "Inter";
  src: url("fonts/inter-var.woff2") format("woff2-variations");
  font-weight: 100 900;
  font-display: swap;
  unicode-range: U+0000-00FF, U+0131, U+0152-0153;
}""", "css", "Une déclaration de police complète"),
        table(["Descripteur", "Rôle", "Valeur recommandée"],
              [["`src`", "Fichier et format", "`woff2`, le plus léger"],
               ["`font-weight`", "Graisses couvertes", "Plage pour une variable"],
               ["`font-display`", "Affichage pendant le chargement", "`swap`"],
               ["`unicode-range`", "Sous-ensemble", "Latin de base"],
               ["`font-style`", "Styles couverts", "`normal`, `italic`"]],
              widths=[3.2, 4.4, 3.6], first_col_bold=True,
              caption="Cinq descripteurs de `@font-face`"),
        p("`font-display: swap` affiche immédiatement une police de substitution, "
          "puis remplace le texte une fois la police chargée. Le texte reste lisible "
          "dès la première seconde, au prix d'un léger décalage visuel."),
        code("""<link rel="preload" href="fonts/inter-var.woff2" as="font"
      type="font/woff2" crossorigin>""", "html",
             "Précharger la police principale, et elle seule"),
        box("attention", "Une police, un fichier, un coût",
            "Chaque graisse téléchargée retarde le premier rendu. Deux familles et "
            "trois graisses constituent déjà un maximum raisonnable. Une police "
            "variable couvre l'ensemble des graisses en un seul fichier."),
        fig("compare", "Deux stratégies de chargement",
            ("SANS font-display", ["Texte invisible jusqu'au chargement",
                                   "Jusqu'à 3 s de vide", "Meilleure fidélité visuelle"],
             "AVEC swap", ["Texte visible immédiatement", "Substitution visible",
                           "Aucune attente pour lire"]),
            height=200),

        h(2, "Construire une échelle typographique"),
        p("Une échelle est une suite de tailles reliées par un rapport constant. Elle "
          "évite les valeurs arbitraires (17 px, 23 px, 31 px) et donne un rythme "
          "visuel cohérent."),
        fig("tree", "Une échelle modulaire",
            ("Rapport 1,25", [("Titres", ["h1 : 2,44 rem", "h2 : 1,95 rem", "h3 : 1,56 rem"]),
                              ("Texte", ["Corps : 1,25 rem", "Petit : 1 rem", "Légende : 0,8 rem"])]),
            height=210),
        code(""":root {
  --ratio: 1.25;
  --taille-0: 1rem;
  --taille-1: calc(var(--taille-0) * var(--ratio));
  --taille-2: calc(var(--taille-1) * var(--ratio));
  --taille-3: calc(var(--taille-2) * var(--ratio));
  --taille--1: calc(var(--taille-0) / var(--ratio));
}

h1 { font-size: var(--taille-3); }
h2 { font-size: var(--taille-2); }
h3 { font-size: var(--taille-1); }
small { font-size: var(--taille--1); }""", "css", "Une échelle calculée à partir d'un seul rapport"),
        p("`clamp()` rend l'échelle fluide entre deux bornes, sans media query :"),
        code("""h1 {
  font-size: clamp(2rem, 1.4rem + 3vw, 3.5rem);
  line-height: 1.1;
}""", "css", "Une taille fluide, bornée dans les deux sens"),
        p("La borne minimale garantit la lisibilité sur petit écran ; la borne "
          "maximale évite les titres démesurés sur grand moniteur. Entre les deux, la "
          "taille suit la largeur de la fenêtre."),

        h(2, "Lisibilité : interligne, mesure, espacement"),
        p("Trois réglages déterminent le confort de lecture. Ils se règlent ensemble, "
          "car ils se compensent : une police large demande un interligne plus "
          "faible, une mesure courte supporte un interligne plus serré."),
        table(["Réglage", "Recommandation", "Effet"],
              [["`line-height`", "1,5 à 1,7 pour le corps", "Aération verticale"],
               ["`max-width`", "45 à 75 caractères", "Retour à la ligne naturel"],
               ["`letter-spacing`", "0 à 0,02 em", "Micro-aération"],
               ["`word-spacing`", "0 par défaut", "À ajuster rarement"],
               ["`text-align`", "`left` (ou `start`)", "Évite les rivières"],
               ["`hyphens`", "`auto` avec `lang`", "Césure correcte"],
               ["`text-wrap`", "`pretty` ou `balance`", "Évite les veuves"]],
              widths=[3.0, 4.2, 4.0], first_col_bold=True,
              caption="Sept réglages de lisibilité"),
        code("""body {
  font-size: 1.0625rem;      /* 17 px */
  line-height: 1.65;
  max-width: 68ch;
  margin-inline: auto;
  padding-inline: 1.25rem;
  text-align: left;
  hyphens: auto;
  overflow-wrap: break-word;
}

h1, h2, h3 {
  line-height: 1.15;
  text-wrap: balance;
  letter-spacing: -0.01em;
}""", "css", "Le réglage de base d'un texte long"),
        p("Le texte justifié (`text-align: justify`) est déconseillé sur le Web : sans "
          "césure fine, il crée des espaces irréguliers et des « rivières » blanches "
          "qui gênent la lecture, particulièrement pour les personnes dyslexiques."),
        box("pratique", "Le test des 60 caractères",
            "Comptez les caractères de trois lignes consécutives. Entre 55 et 75, la "
            "mesure est bonne. En dessous, l'œil change de ligne trop souvent ; "
            "au-dessus, il perd le début de la ligne suivante."),

        h(2, "Typographie française"),
        p("Les règles typographiques françaises diffèrent de l'anglais. Elles "
          "s'appliquent au contenu, pas seulement aux documents imprimés."),
        table(["Règle", "Correct", "Incorrect"],
              [["Espace avant les deux-points", "Exemple&nbsp;: ceci", "Exemple: ceci"],
               ["Guillemets français", "« texte »", "\"texte\""],
               ["Espace insécable dans les guillemets", "«&nbsp;texte&nbsp;»", "«texte»"],
               ["Tiret cadratin pour l'incise", "Le site — refondu — plaît.", "Le site - refondu - plaît."],
               ["Nombre et unité", "12&nbsp;kg", "12kg"],
               ["Pourcentage", "18&nbsp;%", "18%"],
               ["Heure", "14&nbsp;h&nbsp;30", "14h30"]],
              widths=[4.0, 4.0, 3.2], first_col_bold=True,
              caption="Sept règles typographiques françaises"),
        code("""/* Césure correcte : la langue doit être déclarée */
html { hyphens: auto; }

/* Ponctuation orpheline : éviter qu'un point seul passe à la ligne */
p { text-wrap: pretty; }""", "css", "Deux propriétés qui améliorent la composition"),

        h(2, "Typographie et accessibilité"),
        p("La lisibilité n'est pas qu'une affaire d'esthétique. Quatre facteurs "
          "conditionnent l'accès au texte pour les personnes malvoyantes, "
          "dyslexiques ou âgées."),
        ul("**Taille** : au moins 16 px pour le corps, et une mise à l'échelle qui "
           "respecte le zoom à 200 %.",
           "**Contraste** : 4,5:1 minimum pour le texte courant, 3:1 pour les grands "
           "textes.",
           "**Espacement** : un interligne de 1,5 minimum, un espacement des "
           "paragraphes visible.",
           "**Alignement** : à gauche, sans justification, avec des lignes courtes."),
        code("""/* Respecter les préférences de mouvement et de contraste */
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}

@media (prefers-contrast: more) {
  :root { --couleur-texte: #000; --couleur-fond: #fff; }
}""", "css", "Deux préférences système à honorer"),
        p("Le zoom navigateur ne doit jamais être bloqué. Testez votre page à 200 % : "
          "le texte doit rester lisible, les colonnes se réorganiser et aucun contenu "
          "ne doit être tronqué."),
        box("methode", "Contrôle typographique en cinq points",
            items=["Le corps fait-il au moins 16 px ?",
                   "La mesure reste-t-elle sous 75 caractères ?",
                   "L'interligne est-il au moins de 1,5 ?",
                   "Le contraste atteint-il 4,5:1 ?",
                   "La page reste-t-elle lisible à 200 % de zoom ?"]),
    ],
    "keypoints": [
        "La pile système évite tout téléchargement ; une police web se justifie.",
        "Une police variable remplace plusieurs fichiers statiques.",
        "`font-display: swap` rend le texte lisible immédiatement.",
        "Une échelle modulaire remplace les tailles arbitraires.",
        "`clamp()` produit une typographie fluide et bornée.",
        "Interligne, mesure et alignement se règlent ensemble.",
        "La typographie française exige espaces insécables et guillemets adaptés.",
    ],
    "bridge": "Le texte est lisible. Reste à lui donner de la couleur et du relief : "
              "le chapitre suivant traite couleurs, contrastes et arrière-plans.",
    "exercises": [
        ex("Construire une échelle fluide",
           "Créez une échelle typographique de cinq niveaux, fluide entre 360 et "
           "1440 pixels.",
           ["Utilisez `clamp()` et des variables.",
            "Définissez l'interligne pour chaque niveau.",
            "Vérifiez le rendu à 320, 768 et 1440 pixels."],
           [("code", """:root {
  --texte-s: clamp(0.875rem, 0.83rem + 0.2vw, 1rem);
  --texte-m: clamp(1rem, 0.95rem + 0.25vw, 1.125rem);
  --texte-l: clamp(1.25rem, 1.1rem + 0.7vw, 1.75rem);
  --texte-xl: clamp(1.6rem, 1.3rem + 1.5vw, 2.75rem);
  --texte-xxl: clamp(2rem, 1.5rem + 2.5vw, 4rem);
}

body { font-size: var(--texte-m); line-height: 1.65; }
h3 { font-size: var(--texte-l); line-height: 1.3; }
h2 { font-size: var(--texte-xl); line-height: 1.2; }
h1 { font-size: var(--texte-xxl); line-height: 1.05; letter-spacing: -0.02em; }"""),
            "Les tailles les plus grandes ont un interligne plus serré : à 64 px, un "
            "interligne de 1,65 créerait des lignes distantes et un titre disloqué.",
            "À 320 pixels, la borne minimale s'applique : le titre reste lisible sans "
            "déborder. À 1440, la borne maximale évite un titre qui occupe tout "
            "l'écran."]),
        ex("Optimiser une police personnalisée",
           "Vous disposez de la police Inter en quatre fichiers statiques de 180 Ko.",
           ["Remplacez-les par une police variable.",
            "Ajoutez `font-display`, `unicode-range` et le préchargement.",
            "Mesurez le gain dans l'onglet Réseau."],
           ["Un fichier variable `inter-var.woff2` couvre les graisses 100 à 900 en "
            "environ 100 Ko, contre 720 Ko pour quatre fichiers statiques.",
            "`unicode-range` limite les caractères téléchargés au latin de base ; "
            "`font-display: swap` évite le texte invisible ; le préchargement démarre "
            "la requête plus tôt.",
            "Le gain se mesure en kilo-octets transférés et en temps de premier "
            "rendu. Sur une connexion 3G, l'écart atteint souvent une seconde."]),
        ex("Corriger une page illisible",
           "Cette page fait fuir les lecteurs. Corrigez cinq problèmes de lisibilité.",
           ["`body { font-size: 12px; line-height: 1.1; text-align: justify; }`",
            "`p { width: 100%; }`",
            "Titres `h2` de la même taille que le corps",
            "`#333` sur `#444`",
            "`letter-spacing: -0.05em` sur le corps de texte"],
           ["Corps à 17 px minimum, interligne 1,6, alignement à gauche.",
            "Limiter la largeur à 68ch et centrer la colonne.",
            "Établir une hiérarchie : `h2` au moins 1,4 fois le corps.",
            "Contraste insuffisant (`#333` sur `#444` ≈ 1,2:1) : viser 4,5:1.",
            "Un espacement négatif serre les lettres et nuit à la dyslexie ; le "
            "réserver aux très grands titres."],
           level="Diagnostic"),
    ],
    "quiz": [
        quiz("Que fait `font-display: swap` ?",
             ["Il bloque l'affichage jusqu'au chargement",
              "Il affiche une police de substitution puis remplace",
              "Il empêche le téléchargement de la police",
              "Il désactive les italiques"],
             1,
             "Le texte est rendu immédiatement avec une police de secours, puis "
             "remplacé lorsque la police personnalisée est disponible."),
        quiz("Quelle est la mesure de ligne recommandée pour un texte long ?",
             ["20 à 30 caractères", "45 à 75 caractères", "90 à 120 caractères", "Illimitée"],
             1,
             "Entre 45 et 75 caractères, l'œil retrouve le début de la ligne "
             "suivante sans effort."),
        quiz("Quel rapport de contraste minimal pour du texte courant ?",
             ["2:1", "3:1", "4,5:1", "7:1"],
             2,
             "WCAG AA exige 4,5:1 pour le texte courant et 3:1 pour les grands "
             "textes."),
        quiz("Pourquoi éviter `text-align: justify` sur le Web ?",
             ["Il n'est pas supporté",
              "Il crée des espaces irréguliers sans césure fine",
              "Il ralentit le rendu",
              "Il empêche le zoom"],
             1,
             "La justification sans césure contrôlée produit des « rivières » et "
             "gêne la lecture, surtout pour les personnes dyslexiques."),
        quiz("Quelle unité pour une taille de police respectant les préférences ?",
             ["`px`", "`rem`", "`pt`", "`cm`"],
             1,
             "`rem` se rapporte à la taille racine, que l'utilisateur peut modifier "
             "dans son navigateur ; `px` ignore ce réglage."),
    ],
}
