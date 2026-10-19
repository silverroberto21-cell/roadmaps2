from bookkit.dsl import (box, code, defn, ex, fig, h, ol, p, quiz, table, ul)

CH = {
    "title": "Design responsive",
    "subtitle": "Concevoir pour toutes les tailles d'écran, sans multiplier les versions "
                "du site.",
    "duration": "3 h 00",
    "level": "Intermédiaire",
    "prereq": "chapitre 20",
    "objectives": [
        "Écrire des media queries fondées sur le contenu, pas sur des appareils.",
        "Adopter une démarche mobile-first et la justifier.",
        "Utiliser les points de rupture avec parcimonie.",
        "Concevoir des images et des composants adaptatifs.",
        "Tester une interface dans des conditions réalistes.",
    ],
    "blocks": [
        h(2, "Pourquoi le responsive n'est pas une mode"),
        p("Plus de la moitié du trafic web mondial provient d'un téléphone. Les "
          "largeurs d'écran varient de 320 à 3840 pixels, et l'utilisateur peut redimensionner "
          "sa fenêtre à tout moment. Une mise en page figée casse dès que la largeur "
          "change."),
        fig("timeline", "Quatre décisions qui ont façonné le responsive",
            [("2001", "Mise en page fluide"),
             ("2010", "Media queries"),
             ("2015", "Mobile-first généralisé"),
             ("2023", "Container queries")],
            note="Chaque étape a ajouté un outil, sans remplacer les précédents.",
            height=205),
        defn("Responsive design", "Approche de conception où la mise en page s'adapte "
                                  "à l'espace disponible, plutôt que de présenter une "
                                  "version différente par appareil."),

        h(2, "Mobile-first"),
        p("La démarche mobile-first consiste à écrire les styles pour le plus petit "
          "écran, puis à les enrichir par des media queries ascendantes (`min-width`). "
          "Le navigateur applique peu de règles sur téléphone, ce qui économise du "
          "traitement et simplifie le CSS."),
        code("""/* Mobile-first : on part du plus simple */
.galerie { display: grid; gap: 1rem; grid-template-columns: 1fr; }

@media (min-width: 40rem) {
  .galerie { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}

@media (min-width: 64rem) {
  .galerie { grid-template-columns: repeat(3, minmax(0, 1fr)); }
}""", "css", "Trois paliers, une seule direction"),
        table(["Approche", "Sens", "Avantages", "Limites"],
              [["Mobile-first", "`min-width`", "CSS minimal, priorité au contenu", "Styles desktop en surcouche"],
               ["Desktop-first", "`max-width`", "Rapide si la maquette est desktop", "Surcharge mobile lourde"],
               ["Intrinsèque", "Sans media query", "Robuste, peu de code", "Moins de contrôle fin"]],
              widths=[2.6, 2.6, 4.0, 3.4], first_col_bold=True,
              caption="Trois approches de conception adaptative"),

        h(2, "Choisir ses points de rupture"),
        p("Un point de rupture se choisit là où **le contenu se casse**, pas là où un "
          "appareil particulier s'arrête. Les valeurs 320, 768 et 1024 sont des repères "
          "pratiques, pas des dogmes."),
        code("""/* Repères fréquents, à adapter au contenu */
@media (min-width: 30rem) { }   /* 480 px : téléphone large */
@media (min-width: 48rem) { }   /* 768 px : tablette */
@media (min-width: 64rem) { }   /* 1024 px : ordinateur portable */
@media (min-width: 80rem) { }   /* 1280 px : grand écran */""", "css",
             "Quatre points de rupture, rarement plus"),
        p("Multiplier les points de rupture produit un CSS difficile à maintenir. "
          "Deux ou trois suffisent généralement ; au-delà, c'est souvent le signe qu'un "
          "composant devrait s'adapter seul."),
        box("attention", "Ne ciblez pas les appareils",
            "`@media (max-width: 375px)` vise un iPhone précis, qui sera obsolète dans "
            "deux ans. Ciblez des comportements de mise en page : largeur disponible, "
            "orientation, préférences."),

        h(2, "Composants intrinsèquement adaptatifs"),
        p("De nombreux composants n'ont pas besoin de media query. Grid avec `auto-fit`, "
          "`clamp()` pour la typographie et `flex-wrap` suffisent à les rendre "
          "adaptatifs."),
        code(""".entete {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  align-items: center;
  padding-block: 1rem;
}
.entete__titre { flex: 1 1 16rem; font-size: clamp(1.5rem, 1rem + 2vw, 2.5rem); }
.entete__actions { flex: 0 0 auto; }""", "css",
             "Un en-tête qui se replie sans media query"),
        fig("compare", "Deux philosophies",
            ("MEDIA QUERIES", ["Points de rupture explicites", "Contrôle précis", "CSS plus long"],
             "INTRINSÈQUE", ["Composants autonomes", "Moins de code", "Résultat parfois moins fin"]),
            height=190),
        p("La container query pousse la logique plus loin : un composant s'adapte à la "
          "largeur de **son conteneur**, et non de la fenêtre. C'est décisif pour une "
          "carte placée tantôt dans une colonne étroite, tantôt dans une zone large."),
        code(""".conteneur { container-type: inline-size; }

@container (min-width: 30rem) {
  .carte { display: grid; grid-template-columns: 8rem 1fr; gap: 1rem; }
}""", "css", "Une carte qui s'adapte à son conteneur"),

        h(2, "Images et médias adaptatifs"),
        p("Une image doit rester nette et légère sur tous les écrans. `srcset`, "
          "`sizes` et `picture` (chapitre 6) couvrent les cas principaux ; le CSS "
          "complète avec `object-fit` et les ratios."),
        code(""".media {
  aspect-ratio: 16 / 9;
  width: 100%;
  object-fit: cover;
  border-radius: 12px;
}

video { max-width: 100%; height: auto; }

iframe { max-width: 100%; }""", "css", "Des médias qui ne débordent jamais"),
        p("`aspect-ratio` remplace les anciens conteneurs à `padding-top: 56.25 %`. Il "
          "réserve l'espace, évite les sauts de mise en page et rend le code lisible."),

        h(2, "Tester dans des conditions réelles"),
        p("L'émulation du navigateur est utile mais incomplète. Les différences de "
          "performance, de police et de densité d'écran ne s'y voient pas."),
        table(["Test", "Outil", "Ce qu'il révèle"],
              [["Largeurs extrêmes", "Redimensionnement manuel", "Débordements"],
               ["Téléphone réel", "Appareil physique", "Polices, densité, performance"],
               ["Zoom 200 %", "Navigateur", "Lisibilité, débordements"],
               ["Réseau lent", "Émulation 3G", "Ordre de chargement"],
               ["Orientation", "Rotation", "Hauteurs dynamiques"],
               ["Mode sombre", "Préférence système", "Contrastes, images"]],
              widths=[3.2, 3.6, 4.0], first_col_bold=True,
              caption="Six tests complémentaires"),
        code("""/* Attention aux unités de hauteur sur mobile */
.hero {
  min-height: 100svh;   /* small viewport : barre d'URL visible */
}

.panneau {
  max-height: 100dvh;   /* dynamic viewport : s'adapte aux barres */
}""", "css", "Choisir la bonne unité de hauteur"),
        box("methode", "Le test des 320 pixels",
            "Réduisez la fenêtre à 320 pixels de large et parcourez toute la page. "
            "Aucun contenu ne doit être tronqué, aucun défilement horizontal ne doit "
            "apparaître. C'est le test le plus révélateur, et le plus rapide."),
    ],
    "keypoints": [
        "Le responsive adapte la mise en page à l'espace, pas à un appareil.",
        "Mobile-first signifie `min-width` et styles enrichis progressivement.",
        "Les points de rupture se choisissent là où le contenu casse.",
        "Deux ou trois points de rupture suffisent souvent.",
        "Grid, `clamp()` et `flex-wrap` rendent des composants adaptatifs sans media query.",
        "Les container queries adaptent un composant à son conteneur.",
        "Le test à 320 pixels révèle la majorité des problèmes.",
    ],
    "bridge": "La mise en page s'adapte. Le chapitre suivant précise les unités "
              "fluides et les techniques de composition entre deux tailles d'écran.",
    "exercises": [
        ex("Convertir une page en mobile-first",
           "Cette feuille est écrite en desktop-first. Réécrivez-la en mobile-first.",
           ["`@media (max-width: 768px) { .grille { grid-template-columns: 1fr; } }`",
            "`.grille { grid-template-columns: repeat(3, 1fr); }`",
            "`.titre { font-size: 42px; }` puis `@media (max-width: 768px) { .titre { font-size: 28px; } }`"],
           [("code", """.grille { display: grid; gap: 1rem; grid-template-columns: 1fr; }
.titre { font-size: clamp(1.75rem, 1.2rem + 2.5vw, 2.625rem); }

@media (min-width: 48rem) {
  .grille { grid-template-columns: repeat(3, minmax(0, 1fr)); }
}"""),
            "Le mobile-first commence par une colonne unique ; la media query ajoute "
            "les colonnes à partir d'une largeur suffisante.",
            "`clamp()` remplace la double déclaration de taille de titre : une seule "
            "ligne, un rendu continu."]),
        ex("Carte adaptative avec container query",
           "Une carte doit s'afficher en colonne dans un espace étroit et en deux "
           "colonnes dans un espace large, quel que soit l'écran.",
           ["Déclarez un conteneur.",
            "Ajoutez la container query.",
            "Testez en plaçant la carte dans deux zones de largeurs différentes."],
           [("code", """.zone { container-type: inline-size; }

.carte { display: grid; gap: .75rem; }
.carte__image { width: 100%; aspect-ratio: 16/9; object-fit: cover; }

@container (min-width: 26rem) {
  .carte { grid-template-columns: 9rem 1fr; align-items: start; }
  .carte__image { aspect-ratio: 1; border-radius: 8px; }
}"""),
            "La taille du conteneur, et non celle de la fenêtre, décide de la "
            "disposition : la même carte s'adapte dans une barre latérale et dans une "
            "zone principale.",
            "Le `container-type: inline-size` doit être déclaré sur un ancêtre direct "
            "ou lointain, mais pas sur l'élément lui-même."]),
        ex("Auditer une page sur mobile",
           "Testez une page réelle à 320 pixels, en zoom 200 % et en réseau lent.",
           ["Notez trois défauts.",
            "Corrigez-les.",
            "Vérifiez qu'aucun défilement horizontal ne subsiste."],
           ["Défauts fréquents : un tableau qui déborde, un titre qui ne se coupe pas, "
            "une image sans `max-width`, un menu qui dépasse.",
            ("code", """html, body { max-width: 100%; overflow-x: clip; }
img, video, iframe { max-width: 100%; height: auto; }
h1, h2, h3 { overflow-wrap: break-word; }
.tableau { overflow-x: auto; }"""),
            "`overflow-x: clip` masque le symptôme sans corriger la cause : il ne "
            "remplace pas l'identification de l'élément fautif, mais évite un "
            "défilement catastrophique en attendant."],
           level="Audit"),
    ],
    "quiz": [
        quiz("Que signifie mobile-first ?",
             ["Créer une version mobile séparée",
              "Écrire d'abord les styles pour petit écran puis les enrichir",
              "Bloquer l'accès sur ordinateur",
              "Utiliser des media queries `max-width`"],
             1,
             "Les styles de base visent le petit écran ; les media queries `min-width` "
             "ajoutent des améliorations."),
        quiz("Où choisir un point de rupture ?",
             ["Sur la largeur d'un iPhone précis", "Là où la mise en page se casse",
              "Tous les 100 pixels", "À 1920 pixels"],
             1,
             "Le contenu dicte le seuil ; les appareils changent, les problèmes de "
             "composition restent."),
        quiz("Que fait une container query ?",
             ["Adapte selon la fenêtre", "Adapte selon la largeur du conteneur",
              "Adapte selon l'appareil", "Adapte selon la police"],
             1,
             "Elle permet à un composant de réagir à son propre espace, indépendamment "
             "de la fenêtre."),
        quiz("Quelle unité de hauteur s'adapte aux barres d'interface mobile ?",
             ["`vh`", "`dvh`", "`px`", "`%`"],
             1,
             "`dvh` suit la hauteur dynamique du viewport, contrairement à `vh` qui "
             "ignore les barres d'URL."),
        quiz("Quel test révèle le plus vite les problèmes de responsive ?",
             ["Une capture sur grand écran", "La fenêtre réduite à 320 pixels",
              "L'impression", "Le mode sombre"],
             1,
             "À 320 pixels, les débordements et les contenus insécables apparaissent "
             "immédiatement."),
    ],
}
