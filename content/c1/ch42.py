from bookkit.dsl import (box, code, defn, ex, fig, h, ol, p, quiz, table, ul)

CH = {
    "title": "SVG, canvas et visualisation",
    "subtitle": "Choisir le bon outil pour dessiner dans la page, sans sacrifier "
                "l'accessibilité ni la performance.",
    "duration": "3 h 00",
    "level": "Avancé",
    "prereq": "chapitres 9 à 12",
    "objectives": [
        "Distinguer SVG, canvas et CSS pour le dessin.",
        "Écrire un SVG lisible et accessible.",
        "Animer un SVG sans JavaScript.",
        "Dessiner sur un canvas avec un facteur d'échelle.",
        "Choisir l'outil adapté à un besoin de visualisation.",
    ],
    "blocks": [
        h(2, "Trois façons de dessiner"),
        p("Le navigateur propose trois modèles très différents : des éléments vectoriels "
          "dans le DOM (SVG), une surface de pixels pilotée par script (canvas), et des "
          "formes décoratives décrites en CSS. Chacun a un coût et un usage."),
        table(["Critère", "SVG", "Canvas", "CSS"],
              [["Nature", "DOM vectoriel", "Bitmap impératif", "Boîtes stylées"],
               ["Interaction", "Événements par forme", "Calcul manuel", "Sur les éléments"],
               ["Accessibilité", "Possible et fine", "Très limitée", "Bonne"],
               ["Milliers d'objets", "Coûteux", "Adapté", "Non"],
               ["Impression", "Nette", "Dépend de la résolution", "Nette"],
               ["Animation", "Déclarative", "Boucle de rendu", "Déclarative"]],
              widths=[3.8, 4.2, 4.2, 4.2], first_col_bold=True,
              caption="Six critères de choix"),
        defn("Canvas", "Surface bitmap dessinée par instructions JavaScript. Le contenu "
                       "n'existe pas dans le DOM : il n'est ni sélectionnable, ni "
                       "indexable, ni lisible par un lecteur d'écran."),
        fig("tree", "Quel outil pour quel besoin",
            ("Besoin de dessin", [
                ("Icônes, schémas", ["SVG"]),
                ("Graphiques interactifs", ["SVG ou canvas"]),
                ("Jeu, milliers de points", ["Canvas"]),
            ]),
            height=230),

        h(2, "Écrire du SVG"),
        p("Un SVG est un document XML : chaque forme est un élément, stylable en CSS et "
          "manipulable en JavaScript. Il s'intègre en ligne, en image ou en fichier "
          "référencé."),
        code("""<svg viewBox="0 0 120 80" role="img" aria-labelledby="titre-schema">
  <title id="titre-schema">Répartition du trafic par zone</title>
  <desc>Deux rectangles proportionnels : 70 % en Europe, 30 % en Afrique.</desc>

  <rect x="0"  y="0" width="84" height="40" rx="4" fill="#0F2E4C" />
  <rect x="0"  y="44" width="36" height="40" rx="4" fill="#E0A21B" />

  <text x="8" y="24" fill="#FFFFFF" font-size="11">Europe 70 %</text>
  <text x="8" y="68" fill="#0F2E4C" font-size="11">Afrique 30 %</text>
</svg>""", "html", "Un SVG accessible"),
        table(["Élément", "Rôle", "Remarque"],
              [["`viewBox`", "Système de coordonnées", "Indispensable pour l'échelle"],
               ["`<title>`", "Nom accessible", "Lu par les lecteurs d'écran"],
               ["`<desc>`", "Description longue", "Complète le titre"],
               ["`role=\"img\"`", "Rôle explicite", "Évite une lecture XML"],
               ["`preserveAspectRatio`", "Comportement au redimensionnement", "Par défaut, centré"]],
              widths=[4.6, 4.6, 4.4], first_col_bold=True,
              caption="Cinq éléments clés"),
        code("""/* Le SVG se style comme le reste de la page */
.schema { max-inline-size: 100%; block-size: auto; }

.schema .zone-europe  { fill: var(--navy); }
.schema .zone-afrique { fill: var(--amber); }

/* Les propriétés de forme se surchargent en CSS */
.schema rect { transition: fill 200ms ease; }
.schema rect:hover { fill: var(--navy-light); }""", "css", "Un SVG stylé"),
        box("attention", "`width` et `height` sans `viewBox` empêchent la mise à l'échelle",
            "Un SVG fixé à 300 × 200 pixels sera flou ou rogné sur mobile. Déclarez "
            "`viewBox` et laissez la taille venir du CSS."),
        code("""<!-- Icônes réutilisables avec <symbol> -->
<svg aria-hidden="true" style="display:none">
  <symbol id="icone-panier" viewBox="0 0 24 24">
    <path d="M3 4h2l2.5 10h9L19 7H6" fill="none" stroke="currentColor"
          stroke-width="2" stroke-linecap="round" />
    <circle cx="9" cy="19" r="1.6" fill="currentColor" />
    <circle cx="17" cy="19" r="1.6" fill="currentColor" />
  </symbol>
</svg>

<!-- Utilisation -->
<svg class="icone" aria-hidden="true"><use href="#icone-panier" /></svg>
<span class="sr-only">Panier</span>""", "html", "Des icônes sans répétition"),

        h(2, "Animer sans JavaScript"),
        p("Les animations SVG déclaratives suffisent pour la plupart des effets : tracé "
          "progressif, apparition, rotation. Elles respectent les préférences de mouvement "
          "si on les conditionne."),
        code("""/* Tracé progressif d'une courbe */
.courbe {
  stroke-dasharray: 600;
  stroke-dashoffset: 600;
  animation: tracer 1.2s ease-out forwards;
}

@keyframes tracer {
  to { stroke-dashoffset: 0; }
}

@media (prefers-reduced-motion: reduce) {
  .courbe { animation: none; stroke-dashoffset: 0; }
}""", "css", "Une animation de tracé"),
        table(["Technique", "Coût", "Usage"],
              [["Animation CSS sur attributs de présentation", "Faible", "Couleur, opacité"],
               ["`stroke-dashoffset`", "Faible", "Tracé progressif"],
               ["SMIL (`<animate>`)", "Moyen", "Sans CSS, support variable"],
               ["JavaScript (`requestAnimationFrame`)", "Élevé", "Interactions complexes"]],
              widths=[6.0, 3.0, 4.6], first_col_bold=True,
              caption="Quatre techniques d'animation"),
        box("pratique", "Préférez `transform` à la modification de géométrie",
            "Animer `width` ou `d` force un recalcul de la mise en page. `transform` et "
            "`opacity` sont composées par le GPU et restent fluides."),

        h(2, "Dessiner sur un canvas"),
        p("Le canvas exige de gérer soi-même la résolution, le redimensionnement et les "
          "interactions. En échange, il supporte des milliers d'objets sans alourdir le "
          "DOM."),
        code("""<canvas id="graphique" width="600" height="300"
        role="img"
        aria-label="Évolution mensuelle du trafic, de janvier à juin"></canvas>

<script>
const canvas = document.getElementById("graphique");
const ctx = canvas.getContext("2d");

// Adapte la résolution à l'écran (écran haute densité)
function ajuster() {
  const ratio = window.devicePixelRatio || 1;
  const rect = canvas.getBoundingClientRect();
  canvas.width  = rect.width  * ratio;
  canvas.height = rect.height * ratio;
  ctx.setTransform(ratio, 0, 0, ratio, 0, 0);
  dessiner();
}

function dessiner() {
  const { width: w, height: h } = canvas.getBoundingClientRect();
  ctx.clearRect(0, 0, w, h);

  const donnees = [12, 19, 15, 28, 34, 41];
  const max = Math.max(...donnees);
  const largeur = w / donnees.length;

  donnees.forEach((valeur, i) => {
    const hauteur = (valeur / max) * (h - 40);
    ctx.fillStyle = i === donnees.length - 1 ? "#E0A21B" : "#0F2E4C";
    ctx.fillRect(i * largeur + 8, h - hauteur - 20, largeur - 16, hauteur);
    ctx.fillStyle = "#1F2933";
    ctx.font = "12px Arial";
    ctx.fillText(valeur, i * largeur + 8, h - hauteur - 26);
  });
}

ajuster();
window.addEventListener("resize", ajuster);
</script>""", "html", "Un graphique en canvas"),
        table(["Problème", "Cause", "Correction"],
              [["Flou sur écran haute densité", "Canvas non redimensionné", "`devicePixelRatio`"],
               ["Dessin décalé", "Transform non réinitialisé", "`setTransform`"],
               ["Coordonnées fausses au clic", "Taille CSS ≠ taille interne", "Convertir par ratio"],
               ["Consommation élevée", "Boucle permanente", "Dessiner à la demande"],
               ["Texte illisible", "Pas de repli accessible", "`aria-label` + tableau"]],
              widths=[4.6, 4.6, 4.4], first_col_bold=True,
              caption="Cinq pièges du canvas"),
        box("attention", "Un canvas n'est pas accessible",
            "Placez toujours une alternative textuelle à proximité : tableau de données, "
            "description, ou la même information en HTML. Un `aria-label` seul ne remplace "
            "pas les valeurs."),

        h(2, "Choisir et vérifier"),
        p("Le choix se fait sur le volume d'objets, le besoin d'interaction et "
          "l'accessibilité. Une visualisation dense mais décorative peut être en canvas ; "
          "une figure porteuse d'information doit rester lisible par tous."),
        table(["Besoin", "Choix", "Justification"],
              [["Icônes et logos", "SVG en ligne", "Couleur héritée, netteté"],
               ["Schéma interactif", "SVG", "Événements par forme"],
               ["Nuage de 50 000 points", "Canvas ou WebGL", "Coût du DOM"],
               ["Graphique de rapport", "SVG ou bibliothèque", "Impression et accessibilité"],
               ["Effet décoratif", "CSS", "Aucun coût structurel"]],
              widths=[5.0, 4.6, 4.4], first_col_bold=True,
              caption="Cinq besoins"),
        code("""# Vérifications rapides
# 1. Le SVG a-t-il viewBox, title et role ?
grep -c "viewBox" figure.svg
grep -c "<title" figure.svg

# 2. Poids du SVG (nettoyer les métadonnées de l'éditeur)
svgo figure.svg --output figure.min.svg

# 3. Le canvas a-t-il une alternative textuelle dans la page ?""", "bash",
             "Deux contrôles"),
        box("methode", "Règles de dessin dans la page",
            items=["Une figure informative reste accessible.",
                   "`viewBox` sur tout SVG, taille pilotée par CSS.",
                   "Pas plus de quelques dizaines d'objets SVG animés.",
                   "Canvas réservé au volume ou au temps réel.",
                   "Animations conditionnées par `prefers-reduced-motion`."]),
    ],
    "keypoints": [
        "SVG décrit des formes dans le DOM, canvas peint des pixels.",
        "`viewBox` rend un SVG indépendant de sa taille d'affichage.",
        "`<title>` et `<desc>` rendent une figure compréhensible.",
        "Le canvas doit toujours avoir une alternative textuelle.",
        "Le facteur de densité évite un canvas flou.",
        "Animer `transform` et `opacity` coûte moins cher que la géométrie.",
        "Une animation se désactive avec `prefers-reduced-motion`.",
        "Le choix dépend du volume, de l'interaction et de l'accessibilité.",
    ],
    "bridge": "Le cours s'achève ici. Les annexes proposent un glossaire, des "
              "aide-mémoire et une grille d'auto-évaluation.",
    "exercises": [
        ex("Rendre un SVG accessible",
           "Un schéma est une image décorative pour l'auteur, informative pour le lecteur.",
           ["Ajoutez `role` et `title`.",
            "Décrivez les données.",
            "Vérifiez la mise à l'échelle."],
           [("html", """<svg viewBox="0 0 320 120" role="img" aria-labelledby="s1 d1">
  <title id="s1">Trafic par zone</title>
  <desc id="d1">Europe 70 %, Afrique 30 %, sur un total de 10 000 visites.</desc>
  <rect x="0" y="0" width="224" height="48" fill="#0F2E4C" />
  <rect x="0" y="56" width="96" height="48" fill="#E0A21B" />
</svg>"""),
            "Le `viewBox` seul suffit à rendre le dessin adaptatif ; il ne faut pas de "
            "`width` fixe.",
            "La description donne les valeurs, que le dessin ne permet pas de lire "
            "précisément."]),
        ex("Corriger un canvas flou",
           "Le graphique est net sur un écran, flou sur un autre.",
           ["Lisez le facteur de densité.",
            "Redimensionnez la surface.",
            "Réinitialisez la transformation."],
           [("js", """function ajuster(canvas) {
  const ratio = window.devicePixelRatio || 1;
  const rect = canvas.getBoundingClientRect();
  canvas.width = Math.round(rect.width * ratio);
  canvas.height = Math.round(rect.height * ratio);
  const ctx = canvas.getContext("2d");
  ctx.setTransform(ratio, 0, 0, ratio, 0, 0);
  return ctx;
}

// Sans setTransform, les coordonnées sont multipliées deux fois
// et le dessin sort du cadre."""),
            "La taille interne doit être la taille CSS multipliée par le ratio.",
            "`setTransform` remet l'échelle à 1 dans le repère utilisateur."]),
        ex("Choisir un outil",
           "Une page doit afficher 200 points reliés et permettre de cliquer sur chacun.",
           ["Comparez les coûts.",
            "Évaluez l'accessibilité.",
            "Justifiez le choix."],
           ["200 points avec clic : SVG reste raisonnable ; chaque point est un élément "
            "focusable et cliquable.",
            "Au-delà de quelques milliers d'objets, le DOM devient coûteux : canvas avec "
            "calcul de proximité au clic.",
            "Dans les deux cas, un tableau de données accompagne le graphique."],
           level="Architecture"),
    ],
    "quiz": [
        quiz("Quel outil conserve des éléments interactifs dans le DOM ?",
             ["Canvas", "SVG", "CSS", "WebGL"],
             1,
             "Chaque forme SVG est un élément avec ses événements."),
        quiz("Quel attribut rend un SVG redimensionnable ?",
             ["`width`", "`viewBox`", "`preserve`", "`role`"],
             1,
             "Il définit le repère indépendamment de la taille affichée."),
        quiz("Comment éviter un canvas flou ?",
             ["Augmenter la taille CSS", "Multiplier par `devicePixelRatio`",
              "Utiliser `image-rendering`", "Désactiver le zoom"],
             1,
             "La résolution interne doit suivre la densité de l'écran."),
        quiz("Que faut-il pour un graphique en canvas ?",
             ["Rien", "Une alternative textuelle", "Un `alt`", "Un titre HTML"],
             1,
             "Le contenu du canvas n'est pas accessible en soi."),
        quiz("Quelle propriété anime sans recalcul de mise en page ?",
             ["`width`", "`transform`", "`d`", "`height`"],
             1,
             "Elle est composée sans repasser par la mise en page."),
    ],
}
