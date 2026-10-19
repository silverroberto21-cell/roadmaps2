from bookkit.dsl import (box, code, defn, ex, fig, h, ol, p, quiz, table, ul)

CH = {
    "title": "Architecture CSS et conception",
    "subtitle": "Au-delà de quelques pages, une feuille de style sans architecture "
                "devient un passif. Voici comment la garder saine.",
    "duration": "2 h 45",
    "level": "Intermédiaire",
    "prereq": "chapitre 16",
    "objectives": [
        "Organiser les fichiers CSS d'un projet de taille moyenne.",
        "Choisir une convention de nommage et s'y tenir.",
        "Définir des jetons de conception (couleurs, espacements, typographie).",
        "Comprendre l'intérêt des couches et des composants isolés.",
        "Réduire le CSS mort et mesurer la croissance du projet.",
    ],
    "blocks": [
        h(2, "Pourquoi l'architecture compte"),
        p("Une feuille de style grossit toujours : nouveaux écrans, nouvelles "
          "variantes, corrections urgentes. Sans structure, chaque ajout augmente le "
          "risque de casser un écran existant. L'architecture CSS consiste à limiter "
          "ce risque par des règles d'organisation explicites."),
        fig("stack", "Une organisation en couches",
            [("Jetons", "variables : couleurs, espaces, typographie"),
             ("Base", "reset, éléments natifs, typographie globale"),
             ("Mise en page", "conteneurs, grilles, sections"),
             ("Composants", "boutons, cartes, formulaires, navigation"),
             ("Utilitaires", "rares, explicites, non dépendants du contexte")],
            height=250),
        table(["Couche", "Responsabilité", "Ne doit pas"],
              [["Jetons", "Valeurs de conception", "Contenir de sélecteurs"],
               ["Base", "Rendus par défaut des éléments", "Styler des classes"],
               ["Mise en page", "Structure des pages", "Définir l'apparence interne"],
               ["Composants", "Apparence autonome", "Dépendre du contexte parent"],
               ["Utilitaires", "Une seule propriété", "Contenir plusieurs règles"]],
              widths=[2.6, 4.6, 3.8], first_col_bold=True,
              caption="Cinq couches et leurs frontières"),
        p("La règle de dépendance est simple : une couche ne dépend que des couches "
          "inférieures. Un composant peut utiliser les jetons et la base, jamais un "
          "utilitaire défini plus haut."),

        h(2, "Organiser les fichiers"),
        p("Deux approches dominent : un fichier unique de plusieurs milliers de lignes, "
          "ou un découpage par rôle. Le découpage facilite la navigation et la revue "
          "de code ; il exige une convention de nommage claire."),
        code("""css/
├── main.css                  # importe tout, dans l'ordre
├── base/
│   ├── _reset.css
│   ├── _typographie.css
│   └── _formulaires.css
├── jetons/
│   ├── _couleurs.css
│   ├── _espacements.css
│   └── _typographie.css
├── mise-en-page/
│   ├── _conteneur.css
│   └── _sections.css
├── composants/
│   ├── _bouton.css
│   ├── _carte.css
│   └── _navigation.css
└── utilitaires/
    └── _aide.css""", "text", "Un découpage lisible, même sans préprocesseur"),
        code("""/* main.css : l'ordre est la documentation */
@layer reset, jetons, base, mise-en-page, composants, utilitaires;

@import url("base/_reset.css") layer(reset);
@import url("jetons/_couleurs.css") layer(jetons);
@import url("base/_typographie.css") layer(base);
@import url("mise-en-page/_conteneur.css") layer(mise-en-page);
@import url("composants/_bouton.css") layer(composants);
@import url("utilitaires/_aide.css") layer(utilitaires);""", "css",
             "Les couches rendent l'ordre explicite et vérifiable"),
        box("attention", "`@import` retarde le chargement",
            "Chaque `@import` déclenche une requête supplémentaire en cascade. En "
            "production, préférez un outil de construction qui fusionne les fichiers, "
            "ou un seul fichier généré. Les couches restent utiles après fusion."),

        h(2, "Conventions de nommage"),
        p("Une convention n'est bonne que si elle est appliquée partout. Trois "
          "familles coexistent : les préfixes de composant (BEM), les classes "
          "utilitaires (type Tailwind) et les modules CSS (nommage local généré)."),
        table(["Approche", "Exemple", "Force", "Faiblesse"],
              [["BEM", "`.carte__titre--large`", "Lisibilité, autonomie", "Noms longs"],
               ["Utilitaires", "`mt-4 text-sm`", "Composition rapide", "HTML verbeux"],
               ["Modules CSS", "`.carte_titre_ab12`", "Isolation stricte", "Outillage requis"],
               ["CSS-in-JS", "`styled(Carte)`", "Colocalisation", "Poids, complexité"]],
              widths=[2.2, 3.4, 3.2, 3.0], first_col_bold=True,
              caption="Quatre approches de nommage"),
        p("Quelle que soit l'approche, trois règles universelles s'appliquent : un nom "
          "décrit un rôle, jamais une apparence ni une position ; les classes se "
          "combinent par composition ; les identifiants ne servent pas au style."),
        code("""<!-- Mauvais : apparence et position -->
<div class="bleu colonne-gauche grand-texte">

<!-- Bon : rôle -->
<aside class="encart encart--mise-en-avant">""", "html",
             "Nommer par rôle rend le code résistant aux changements de charte"),

        h(2, "Jetons de conception"),
        p("Les jetons sont les valeurs de base du système : couleurs, espacements, "
          "rayons, ombres, durées, tailles de police. Centralisés, ils permettent de "
          "changer l'identité d'un site en quelques lignes."),
        code(""":root {
  /* Espacements, échelle de 4 px */
  --espace-1: .25rem;  --espace-2: .5rem;
  --espace-3: .75rem;  --espace-4: 1rem;
  --espace-6: 1.5rem;  --espace-8: 2rem;
  --espace-12: 3rem;   --espace-16: 4rem;

  /* Rayons */
  --rayon-s: 4px; --rayon-m: 8px; --rayon-l: 16px; --rayon-pilule: 999px;

  /* Typographie */
  --police-titre: "Arial", system-ui, sans-serif;
  --police-texte: "Times New Roman", Georgia, serif;
  --taille-s: .875rem; --taille-m: 1.0625rem; --taille-l: 1.5rem;

  /* Mouvement */
  --duree-rapide: 150ms; --duree-normale: 250ms;
}""", "css", "Un jeu de jetons complet, mais court"),
        p("Une échelle d'espacement de 4 pixels évite les valeurs arbitraires (13 px, "
          "27 px) et produit un rythme visuel régulier. Huit valeurs suffisent à "
          "couvrir l'essentiel d'un site."),

        h(2, "Isoler les composants"),
        p("Un composant ne doit pas être modifié par son contexte. Deux techniques "
          "l'en empêchent : les couches, qui figent l'ordre de priorité, et les "
          "contextes d'empilement locaux."),
        code("""@layer composants {
  .carte { padding: var(--espace-4); }
}

/* Le contexte ne modifie pas le composant */
.sidebar .carte { padding: var(--espace-2); }  /* à éviter */

/* Mieux : une variante explicite */
.carte--compacte { padding: var(--espace-2); }""", "css",
             "La variante explicite remplace la surcharge contextuelle"),
        p("Les variables CSS participent à l'isolation : un composant peut redéfinir "
          "ses propres jetons localement sans affecter le reste."),
        code(""".carte--sombre {
  --couleur-texte: #e8edf1;
  --couleur-fond: #16222e;
  background: var(--couleur-fond);
  color: var(--couleur-texte);
}
/* Tous les enfants héritent des nouvelles valeurs, sans règle supplémentaire */""",
             "css", "Un composant qui porte ses propres jetons"),

        h(2, "Mesurer et nettoyer"),
        p("Le CSS mort s'accumule : classes supprimées du HTML, règles remplacées, "
          "variantes oubliées. Un audit périodique maintient le poids et la lisibilité."),
        code("""# Compter les règles et la taille du fichier
$ wc -l css/**/*.css
$ npx cssnano css/main.css -o build/main.min.css

# Repérer les classes jamais utilisées (outil d'analyse)
$ npx purgecss --css css/main.css --content "**/*.html" --output build/""",
             "bash", "Deux mesures simples et un nettoyage"),
        table(["Indicateur", "Seuil d'alerte", "Action"],
              [["Taille du CSS (gzip)", "> 100 Ko", "Fusionner, purger"],
               ["Nombre de `!important`", "> 3", "Revoir la cascade"],
               ["Profondeur des sélecteurs", "> 3 niveaux", "Simplifier"],
               ["Classes orphelines", "> 10 %", "Purger"],
               ["Feuilles non utilisées", "> 0", "Supprimer"]],
              widths=[4.2, 3.0, 3.8], first_col_bold=True,
              caption="Cinq indicateurs de santé d'une feuille de style"),
        box("methode", "Revue trimestrielle du CSS",
            items=["Lister les fichiers et leur taille.",
                   "Supprimer les règles non utilisées (vérification dans le HTML).",
                   "Regrouper les valeurs en jetons.",
                   "Vérifier l'ordre des couches.",
                   "Documenter les conventions dans le README."]),
    ],
    "keypoints": [
        "Une architecture CSS limite le risque de régression.",
        "Cinq couches : jetons, base, mise en page, composants, utilitaires.",
        "Une couche ne dépend que des couches inférieures.",
        "Les `@layer` rendent l'ordre de priorité explicite.",
        "Un nom décrit un rôle, jamais une apparence.",
        "Les jetons centralisent les décisions de conception.",
        "Les variantes explicites remplacent les surcharges contextuelles.",
    ],
    "bridge": "L'architecture est posée. Place aux mises en page modernes, en "
              "commençant par Flexbox.",
    "exercises": [
        ex("Restructurer un projet",
           "Un projet contient un unique `style.css` de 2 400 lignes.",
           ["Proposez un découpage en cinq dossiers.",
            "Définissez l'ordre d'import et les couches.",
            "Listez trois risques de la migration."],
           ["Découpage : `base/`, `jetons/`, `mise-en-page/`, `composants/`, "
            "`utilitaires/`, avec un `main.css` qui importe dans l'ordre.",
            ("code", """@layer reset, jetons, base, mise-en-page, composants, utilitaires;
@import url("base/_reset.css") layer(reset);
@import url("jetons/_couleurs.css") layer(jetons);
/* ... */"""),
            "Trois risques : règles perdues lors du déplacement, ordre modifié qui "
            "change la cascade, et anciennes classes encore référencées dans le HTML. "
            "La migration doit être progressive et versionnée."],
           level="Organisation"),
        ex("Créer un jeu de jetons complet",
           "Définissez les jetons d'un site de formation : couleurs, espacements, "
           "typographie, rayons, ombres, durées.",
           ["Limitez-vous à huit espacements.",
            "Utilisez une échelle typographique.",
            "Documentez chaque famille en commentaire."],
           [("code", """:root {
  /* Couleurs : primaire, neutres, états */
  --primaire: #0f2e4c; --primaire-clair: #274b6d;
  --texte: #1f2933; --texte-doux: #52606d;
  --fond: #fff; --fond-alt: #f4f7f9;
  --succes: #2f7d5b; --alerte: #a63a32; --accent: #e0a21b;

  /* Espacements : échelle de 4 px */
  --e1: .25rem; --e2: .5rem; --e3: .75rem; --e4: 1rem;
  --e6: 1.5rem; --e8: 2rem; --e12: 3rem; --e16: 4rem;

  /* Typographie : rapport 1,25 */
  --t-s: .875rem; --t-m: 1.0625rem; --t-l: 1.5rem;
  --t-xl: 2rem; --t-xxl: 2.75rem;

  /* Rayons et ombres */
  --r-s: 4px; --r-m: 8px; --r-pilule: 999px;
  --ombre-1: 0 1px 2px rgb(15 46 76 / 8%);
  --ombre-2: 0 8px 24px rgb(15 46 76 / 12%);

  /* Mouvement */
  --d-rapide: 150ms; --d-normale: 250ms;
}"""),
            "Huit espacements couvrent les besoins courants ; au-delà, la valeur "
            "arbitraire revient.",
            "Une échelle typographique évite les tailles incohérentes et facilite les "
            "ajustements globaux."]),
        ex("Auditer une feuille de style",
           "Analysez la feuille d'un site existant.",
           ["Comptez les `!important` et les identifiants utilisés pour le style.",
            "Repérez les couleurs codées en dur.",
            "Proposez un plan de refonte en trois étapes."],
           ["Plus de trois `!important` indiquent un conflit de spécificité non "
            "résolu ; les identifiants de style empêchent la réutilisation.",
            "Les couleurs en dur (plus de dix teintes différentes) révèlent l'absence "
            "de palette : elles doivent devenir des jetons.",
            "Plan : 1) extraire les jetons sans rien changer visuellement ; 2) migrer "
            "les composants vers ces jetons ; 3) supprimer les règles obsolètes et "
            "réduire la spécificité."],
           level="Analyse"),
    ],
    "quiz": [
        quiz("Combien de couches propose l'architecture décrite dans ce chapitre ?",
             ["Trois", "Quatre", "Cinq", "Sept"],
             2,
             "Jetons, base, mise en page, composants, utilitaires : cinq couches aux "
             "frontières explicites."),
        quiz("Que fait `@layer reset, jetons, base;` ?",
             ["Il importe trois fichiers", "Il déclare l'ordre de priorité des couches",
              "Il crée trois variables", "Il active le mode sombre"],
             1,
             "L'ordre déclaré fixe la priorité : les couches suivantes l'emportent sur "
             "les précédentes, indépendamment du nombre de sélecteurs."),
        quiz("Quel nom de classe est le plus robuste ?",
             ["`.bleu`", "`.colonne-gauche`", "`.carte__titre`", "`.grand-texte`"],
             2,
             "Un nom de rôle (`carte__titre`) reste juste si la couleur, la position ou "
             "la taille changent."),
        quiz("Pourquoi éviter `.sidebar .carte { ... }` ?",
             ["C'est trop long",
              "Le composant devient dépendant de son contexte",
              "Cela empêche le responsive",
              "Cela casse la cascade"],
             1,
             "La surcharge contextuelle rend le composant imprévisible ; une variante "
             "explicite est préférable."),
        quiz("Quel outil repère les classes CSS non utilisées ?",
             ["Un minifieur", "PurgeCSS", "Un préprocesseur", "Un validateur HTML"],
             1,
             "PurgeCSS analyse le HTML et retire les règles dont les sélecteurs "
             "n'apparaissent nulle part."),
    ],
}
