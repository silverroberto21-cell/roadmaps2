from bookkit.dsl import (box, code, defn, ex, fig, h, ol, p, quiz, table, ul)

CH = {
    "title": "Couleurs, fonds et contrastes",
    "subtitle": "La couleur n'est pas un décor : elle porte de l'information, crée une "
                "hiérarchie et conditionne l'accessibilité.",
    "duration": "2 h 30",
    "level": "Débutant",
    "prereq": "chapitre 11",
    "objectives": [
        "Écrire une couleur en hexadécimal, en RGB, en HSL et en couleurs modernes.",
        "Construire une palette cohérente et documentée.",
        "Mesurer et garantir un contraste conforme.",
        "Composer des dégradés et des arrière-plans maîtrisés.",
        "Ne jamais faire dépendre une information de la seule couleur.",
    ],
    "blocks": [
        h(2, "Quatre syntaxes pour une même couleur"),
        p("CSS accepte plusieurs notations. Chacune a ses usages : la notation "
          "hexadécimale est compacte, `rgb()` explicite, `hsl()` intuitive pour "
          "construire une palette, les notations modernes permettent la transparence "
          "et les espaces colorimétriques étendus."),
        code(""".exemple {
  color: #0f2e4c;                  /* hexadécimal */
  color: rgb(15 46 76);            /* rouge, vert, bleu */
  color: hsl(210 67% 18%);         /* teinte, saturation, luminosité */
  color: hsl(210 67% 18% / .85);   /* avec transparence */
  color: oklch(30% 0.06 250);      /* espace perceptuel moderne */
}""", "css", "Cinq écritures, une seule couleur"),
        table(["Notation", "Forces", "Limites"],
              [["Hexadécimal", "Compact, universel", "Peu intuitif à ajuster"],
               ["`rgb()`", "Lisible, alpha intégré", "Calcul mental difficile"],
               ["`hsl()`", "Variations intuitives de teinte", "Luminosité non perceptuelle"],
               ["`oklch()`", "Perceptuellement uniforme", "Support récent"],
               ["Variables nommées", "Cohérence du projet", "Nécessite une convention"]],
              widths=[2.8, 4.4, 3.8], first_col_bold=True,
              caption="Cinq notations et leur intérêt"),
        defn("Espace colorimétrique perceptuel", "Modèle où une variation numérique "
                                                 "correspond à une variation visuelle "
                                                 "constante. `oklch()` permet de générer "
                                                 "des palettes régulières."),

        h(2, "Construire une palette"),
        p("Une palette se compose de rôles, pas de couleurs. On définit d'abord la "
          "couleur primaire, puis les neutres, puis les couleurs d'état. Chaque rôle "
          "reçoit des variantes de luminosité pour les états et les surfaces."),
        fig("columns", "Les cinq familles d'une palette",
            [("Primaire", ["Marque", "Actions", "Liens"]),
             ("Neutres", ["Texte", "Fonds", "Bordures"]),
             ("États", ["Succès", "Alerte", "Information"]),
             ("Surfaces", ["Carte", "Bandeau", "Modale"]),
             ("Accents", ["Mise en avant", "Graphiques"])],
            height=210),
        code(""":root {
  /* Primaire */
  --primaire-900: #0b2138;
  --primaire-700: #0f2e4c;
  --primaire-500: #274b6d;
  --primaire-100: #e8edf1;

  /* Neutres */
  --neutre-900: #1f2933;
  --neutre-600: #5b6770;
  --neutre-300: #c9d6e2;
  --neutre-100: #f4f7f9;
  --blanc: #ffffff;

  /* États */
  --succes: #2f7d5b;
  --alerte: #a63a32;
  --info: #274b6d;
  --accent: #e0a21b;
}""", "css", "Une palette nommée par rôle et par intensité"),
        p("Nommer les nuances par un nombre (100 à 900) facilite les substitutions : "
          "`--primaire-700` peut changer de teinte sans que le nom devienne faux."),
        box("retenir", "Trois couleurs suffisent",
            "Une couleur de marque, un accent et une échelle de neutres couvrent la "
            "majorité des interfaces. Multiplier les couleurs dilue la hiérarchie et "
            "complique la maintenance."),

        h(2, "Contraste : la contrainte mesurable"),
        p("Le contraste se calcule à partir de la luminance relative des deux "
          "couleurs. Le rapport va de 1:1 (aucun contraste) à 21:1 (noir sur blanc). "
          "Les règles WCAG AA fixent des seuils selon la taille du texte."),
        table(["Élément", "AA", "AAA"],
              [["Texte courant", "4,5:1", "7:1"],
               ["Grand texte (≥ 24 px ou 18,66 px gras)", "3:1", "4,5:1"],
               ["Composants d'interface", "3:1", "—"],
               ["Indicateur de focus", "3:1", "—"],
               ["Graphiques informatifs", "3:1", "—"]],
              widths=[5.0, 2.4, 2.4], first_col_bold=True,
              caption="Seuils de contraste WCAG"),
        code("""/* Vérification rapide du contraste en JavaScript */
function luminance(hex) {
  const [r, g, b] = hex.match(/\\w\\w/g).map(h => {
    const v = parseInt(h, 16) / 255;
    return v <= 0.03928 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4;
  });
  return 0.2126 * r + 0.7152 * g + 0.0722 * b;
}
function contraste(a, b) {
  const [l1, l2] = [luminance(a), luminance(b)].sort((x, y) => y - x);
  return ((l1 + 0.05) / (l2 + 0.05)).toFixed(2);
}
contraste("1f2933", "ffffff"); // "14.36\"""", "js",
             "Calculer un contraste sans outil externe"),
        p("Un gris moyen sur blanc est le piège classique : `#777` sur `#fff` atteint "
          "4,48:1, juste sous le seuil. Le même gris sur un fond légèrement teinté "
          "passe sous 4:1. Testez toujours les combinaisons réelles, pas les couleurs "
          "théoriques."),
        box("attention", "Le contraste ne suffit pas",
            "Un texte blanc sur fond bleu peut respecter 4,5:1 et rester pénible pour "
            "les personnes astigmates. Évitez le blanc pur sur fond saturé et "
            "préférez un blanc cassé (`#f4f7f9`) sur un bleu très foncé."),

        h(2, "Arrière-plans et dégradés"),
        p("Une couleur de fond peut être unie, dégradée, répétée ou multiple. Les "
          "dégradés CSS sont des images générées : ils s'animent, se superposent et "
          "s'adaptent à la taille de l'élément."),
        code(""".bandeau {
  background: linear-gradient(135deg, #0f2e4c, #274b6d);
  color: #fff;
}

.hero {
  background:
    linear-gradient(to top, rgb(15 46 76 / .85), rgb(15 46 76 / .2)),
    url("images/atelier.webp") center / cover no-repeat;
}

.motif {
  background-image: radial-gradient(#c9d6e2 1px, transparent 1px);
  background-size: 16px 16px;
}""", "css", "Trois arrière-plans composés"),
        table(["Propriété", "Rôle", "Exemple"],
              [["`background-color`", "Couleur de fond", "`#f4f7f9`"],
               ["`background-image`", "Image ou dégradé", "`linear-gradient(...)`"],
               ["`background-size`", "Dimensionnement", "`cover`, `contain`"],
               ["`background-position`", "Position", "`center`, `50% 20%`"],
               ["`background-repeat`", "Répétition", "`no-repeat`"],
               ["`background-clip`", "Zone couverte", "`text` pour un titre en dégradé"]],
              widths=[3.4, 3.6, 4.2], first_col_bold=True,
              caption="Six propriétés d'arrière-plan"),
        code(""".titre-degrade {
  background: linear-gradient(90deg, #0f2e4c, #e0a21b);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}""", "css", "Un dégradé appliqué au texte"),
        p("Le texte en dégradé reste du texte : il demeure sélectionnable, lu par les "
          "lecteurs d'écran, indexé. Veillez toutefois à conserver un contraste "
          "suffisant sur toute la longueur du dégradé."),

        h(2, "La couleur comme information"),
        p("Environ 8 % des hommes présentent une forme de daltonisme. Une information "
          "portée uniquement par la couleur disparaît pour eux — et pour tous les "
          "utilisateurs en mode contraste élevé ou sur un écran mal calibré."),
        fig("compare", "Deux façons de signaler une erreur",
            ("COULEUR SEULE", ["Bordure rouge", "Invisible pour certains", "Ambigu à l'impression"],
             "COULEUR + FORME", ["Bordure rouge + icône", "Message texte", "Compréhensible par tous"]),
            height=200),
        code("""/* Ne jamais s'appuyer sur la couleur seule */
.champ-erreur {
  border: 2px solid #a63a32;
  background-image: url("icones/alerte.svg");
  background-position: right .6rem center;
  background-repeat: no-repeat;
}
/* Le message texte reste indispensable */
""", "css", "Une erreur signalée par plusieurs canaux"),
        ul("Un graphique : légender les séries, varier les motifs de trait, ne pas "
           "compter sur la seule teinte.",
           "Un état : ajouter une icône ou un texte (« En rupture »).",
           "Un lien dans un paragraphe : le souligner, pas seulement le colorer.",
           "Un formulaire : afficher un message explicite à côté du champ."),
        code("""/* Respecter le mode contraste élevé */
@media (forced-colors: active) {
  .bouton { border: 2px solid ButtonText; }
  .carte { border: 1px solid CanvasText; }
}""", "css", "Le mode contraste élevé remplace les couleurs système"),
        box("methode", "Auditer une palette",
            items=["Extraire toutes les couleurs employées (inspecteur ou script).",
                   "Calculer le contraste de chaque paire texte/fond.",
                   "Vérifier les états de focus, de survol et de désactivation.",
                   "Tester la page en niveaux de gris.",
                   "Simuler les principaux types de daltonisme."]),
    ],
    "keypoints": [
        "Une couleur s'écrit en hexadécimal, RGB, HSL ou OKLCH selon le besoin.",
        "Une palette se nomme par rôle et par intensité, pas par apparence.",
        "Le contraste se mesure : 4,5:1 pour le texte, 3:1 pour les interfaces.",
        "Le blanc pur sur fond saturé fatigue, même conforme.",
        "Les dégradés sont des images CSS, superposables et animables.",
        "La couleur ne doit jamais être le seul porteur d'une information.",
        "Le mode contraste élevé remplace la palette : prévoyez des bordures.",
    ],
    "bridge": "Couleurs et fonds sont posés. Le chapitre suivant entre dans le "
              "mécanisme central de CSS : le modèle de boîte.",
    "exercises": [
        ex("Construire une palette accessible",
           "Définissez une palette de six couleurs pour un site institutionnel.",
           ["Calculez le contraste de chaque paire texte/fond.",
            "Corrigez les combinaisons qui échouent.",
            "Nommez les variables par rôle."],
           [("code", """:root {
  --texte: #1f2933;        /* sur blanc : 14,4:1 */
  --texte-doux: #52606d;   /* sur blanc : 7,0:1 */
  --fond: #ffffff;
  --fond-alt: #f4f7f9;
  --primaire: #0f2e4c;     /* sur blanc : 13,4:1 */
  --primaire-clair: #274b6d;
  --accent: #e0a21b;       /* texte foncé obligatoire */
  --erreur: #a63a32;       /* sur blanc : 6,6:1 */
}"""),
            "L'accent ambre ne doit jamais porter du texte blanc : son contraste "
            "tombe sous 3:1. Il sert de fond avec un texte foncé, ou de trait.",
            "Le gris `#52606d` conserve 7:1 sur blanc et reste lisible sur "
            "`#f4f7f9`. C'est un bon compromis pour du texte secondaire."]),
        ex("Réparer une interface qui repose sur la couleur",
           "Un tableau de bord affiche les statuts en vert, orange et rouge, sans "
           "texte ni icône.",
           ["Proposez trois canaux d'information supplémentaires.",
            "Modifiez le HTML et le CSS en conséquence.",
            "Vérifiez le rendu en niveaux de gris."],
           [("code", """<ul class="statuts">
  <li class="statut statut--ok">
    <svg aria-hidden="true">…</svg> <strong>Opérationnel</strong>
    — dernier contrôle à 14 h 02
  </li>
  <li class="statut statut--ko">
    <svg aria-hidden="true">…</svg> <strong>Indisponible</strong>
    — depuis 13 h 47
  </li>
</ul>"""),
            "Trois canaux : le texte du statut, l'icône de forme différente, et la "
            "couleur. La couleur devient redondante au lieu d'être porteuse unique.",
            "En niveaux de gris, les icônes (coche, croix) et les textes restent "
            "distincts : l'information survit à la perte de couleur."],
           level="Accessibilité"),
        ex("Créer un bandeau avec dégradé et image",
           "Composez un bandeau de 40vh avec une image de fond, un voile sombre et un "
           "titre lisible.",
           ["Superposez un dégradé et une image.",
            "Garantissez le contraste du titre sur toutes les zones.",
            "Prévoyez un repli sans image."],
           [("code", """.bandeau {
  min-height: 40svh;
  display: grid;
  align-content: end;
  padding: 2rem;
  color: #fff;
  background:
    linear-gradient(to top, rgb(10 20 30 / .92) 0%, rgb(10 20 30 / .35) 60%),
    #0f2e4c url("images/bandeau.webp") center / cover no-repeat;
}
.bandeau h1 { font-size: clamp(2rem, 5vw, 3.5rem); line-height: 1.05; }"""),
            "Le dégradé vertical assombrit le bas, où se trouve le texte : le "
            "contraste reste supérieur à 7:1 quelle que soit l'image.",
            "La couleur de fond `#0f2e4c` sert de repli si l'image ne charge pas ; "
            "le texte reste lisible sur ce fond uni."],
           level="Application"),
    ],
    "quiz": [
        quiz("Quel contraste minimal pour du texte courant selon WCAG AA ?",
             ["2:1", "3:1", "4,5:1", "7:1"],
             2,
             "WCAG AA demande 4,5:1 pour le texte courant et 3:1 pour les grands "
             "textes."),
        quiz("Quelle notation permet d'ajuster intuitivement la luminosité d'une teinte ?",
             ["Hexadécimal", "`rgb()`", "`hsl()`", "`oklch()`"],
             2,
             "`hsl()` sépare teinte, saturation et luminosité : faire varier le "
             "troisième paramètre éclaircit ou assombrit la couleur."),
        quiz("Pourquoi ne pas coder une erreur uniquement par une bordure rouge ?",
             ["Le rouge est interdit en interface",
              "L'information disparaît pour les daltoniens et en niveaux de gris",
              "Cela ralentit le rendu",
              "Cela empêche la validation HTML"],
             1,
             "La couleur doit être doublée par un texte ou une icône pour rester "
             "perceptible par tous."),
        quiz("Que fait `background-clip: text` ?",
             ["Il découpe le texte", "Il applique l'arrière-plan à l'intérieur des lettres",
              "Il masque le texte", "Il ajoute une bordure"],
             1,
             "Combiné à `color: transparent`, il fait apparaître le dégradé à "
             "l'intérieur des glyphes."),
        quiz("Quel mode système remplace les couleurs par une palette imposée ?",
             ["`prefers-color-scheme`", "`forced-colors`", "`prefers-contrast`", "`color-gamut`"],
             1,
             "`forced-colors: active` signale le mode contraste élevé de Windows, qui "
             "remplace les couleurs par les couleurs système."),
    ],
}
