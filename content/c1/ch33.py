from bookkit.dsl import (box, code, defn, ex, fig, h, ol, p, quiz, table, ul)

CH = {
    "title": "Performance web",
    "subtitle": "Mesurer ce que l'utilisateur ressent, puis réduire le poids, le délai "
                "et le travail du navigateur.",
    "duration": "3 h 00",
    "level": "Intermédiaire",
    "prereq": "chapitre 32",
    "objectives": [
        "Interpréter les Core Web Vitals.",
        "Réduire le poids des images, polices et scripts.",
        "Optimiser le chemin critique de rendu.",
        "Mettre en cache et différer le non-critique.",
        "Mesurer avant et après chaque optimisation.",
    ],
    "blocks": [
        h(2, "Mesurer ce qui compte"),
        p("La performance perçue se mesure en jalons : quand le contenu apparaît, "
          "quand il devient lisible, quand il cesse de bouger. Trois indicateurs "
          "résument ces jalons."),
        table(["Indicateur", "Mesure", "Seuil correct"],
              [["LCP", "Affichage du plus grand élément", "≤ 2,5 s"],
               ["INP", "Réactivité aux interactions", "≤ 200 ms"],
               ["CLS", "Stabilité visuelle", "≤ 0,1"],
               ["TTFB", "Premier octet reçu", "≤ 800 ms"],
               ["FCP", "Premier contenu affiché", "≤ 1,8 s"]],
              widths=[2.6, 6.0, 3.4], first_col_bold=True,
              caption="Cinq jalons et leurs seuils"),
        defn("Core Web Vitals", "Trois indicateurs (LCP, INP, CLS) retenus par Google "
                                "pour décrire l'expérience réelle : rapidité "
                                "d'affichage, réactivité et stabilité."),
        fig("flow", "Le chargement d'une page",
            ["Requête DNS et connexion",
             "Premier octet (TTFB)",
             "HTML analysé, ressources découvertes",
             "CSS appliqué, premier rendu (FCP)",
             "Image principale chargée (LCP)",
             "Interactions disponibles, puis mesurées (INP)"],
            height=265),
        code("""// Mesurer dans le navigateur réel
const observateur = new PerformanceObserver((liste) => {
  for (const entree of liste.getEntries()) {
    console.log(entree.name, entree.startTime, entree.value);
  }
});
observateur.observe({ type: "largest-contentful-paint", buffered: true });
observateur.observe({ type: "layout-shift", buffered: true });""", "js",
             "Observer les jalons depuis la page"),
        code("""# Audit local avec Lighthouse
npx lighthouse https://exemple.fr --view
npx lighthouse http://localhost:8080 --preset=desktop --output=json""", "bash",
             "Un rapport complet en une commande"),

        h(2, "Le poids des images"),
        p("Les images représentent souvent plus de la moitié du poids d'une page. "
          "Quatre décisions réduisent ce poids sans perte visible."),
        table(["Décision", "Gain", "Effort"],
              [["Format moderne (WebP, AVIF)", "30 à 60 %", "Faible"],
               ["Dimension adaptée à l'affichage", "Jusqu'à 80 %", "Faible"],
               ["`srcset` et `sizes`", "Variable", "Moyen"],
               ["Chargement différé", "Élevé au premier écran", "Très faible"],
               ["Compression de qualité", "10 à 30 %", "Très faible"]],
              widths=[5.2, 3.4, 3.4], first_col_bold=True,
              caption="Cinq leviers sur les images"),
        code("""<img
  src="paysage-800.avif"
  srcset="paysage-400.avif 400w, paysage-800.avif 800w, paysage-1600.avif 1600w"
  sizes="(max-width: 600px) 100vw, 50vw"
  width="800" height="533"
  alt="Vallée brumeuse au lever du jour"
  loading="lazy"
  decoding="async">""", "html", "Une image adaptée à chaque écran"),
        p("Les attributs `width` et `height` réservent l'espace avant chargement et "
          "évitent un décalage de mise en page — l'une des causes principales de CLS."),
        box("attention", "Ne différez pas l'image principale",
            "`loading=\"lazy\"` sur l'image du premier écran retarde le LCP. Réservez "
            "le chargement différé aux images situées plus bas, et utilisez "
            "`fetchpriority=\"high\"` pour l'image principale."),

        h(2, "Polices"),
        p("Une police web déclenche un téléchargement qui peut bloquer l'affichage du "
          "texte. Trois réglages limitent l'attente."),
        code("""@font-face {
  font-family: "Inter";
  src: url("/polices/inter-latin.woff2") format("woff2");
  font-display: swap;              /* affiche un substitut immédiatement */
  unicode-range: U+0000-00FF;      /* sous-ensemble latin uniquement */
  font-weight: 400 700;            /* variable, un seul fichier */
}""", "css", "Une police qui n'attend pas"),
        code("""<!-- Précharger la police réellement utilisée au premier écran -->
<link rel="preload" href="/polices/inter-latin.woff2"
      as="font" type="font/woff2" crossorigin>""", "html",
             "Un préchargement ciblé"),
        p("Limitez-vous à deux familles et à trois graisses. `font-display: swap` "
          "affiche immédiatement un substitut, quitte à provoquer un léger changement "
          "d'aspect une fois la police chargée."),

        h(2, "Chemin critique de rendu"),
        p("Le navigateur doit analyser le HTML, télécharger les CSS, construire l'arbre "
          "de rendu, calculer la mise en page, puis peindre. Chaque ressource bloquante "
          "allonge ce chemin."),
        code("""<!-- Bloquant : à éviter -->
<link rel="stylesheet" href="tout.css">

<!-- Non bloquant : le CSS critique est en ligne, le reste différé -->
<style>/* règles du premier écran, quelques centaines d'octets */</style>
<link rel="stylesheet" href="tout.css" media="print" onload="this.media='all'">
<noscript><link rel="stylesheet" href="tout.css"></noscript>""", "html",
             "Différer ce qui n'est pas critique"),
        code("""<!-- Script : ne jamais bloquer l'analyse -->
<script src="app.js" defer></script>
<script src="analytics.js" async></script>
<script type="module" src="principal.js"></script>""", "html",
             "Trois façons de ne pas bloquer"),
        table(["Ressource", "Bloque l'analyse", "Bloque le rendu", "Traitement"],
              [["CSS classique", "Oui", "Oui", "En ligne pour le critique"],
               ["`<script>` sans attribut", "Oui", "Indirectement", "`defer` ou module"],
               ["`defer`", "Non", "Non", "Ordre préservé"],
               ["`async`", "Non", "Non", "Ordre libre"],
               ["Image", "Non", "Non", "Dimensions réservées"]],
              widths=[3.6, 3.0, 3.0, 3.6], first_col_bold=True,
              caption="Ce que chaque ressource bloque"),

        h(2, "Scripts et travail du navigateur"),
        p("Un fichier JavaScript coûte deux fois : il faut le télécharger puis "
          "l'exécuter. Le découpage en morceaux évite d'envoyer au navigateur du code "
          "qu'il n'utilisera peut-être jamais."),
        code("""// Chargement à la demande, au moment utile
boutonPartage.addEventListener("click", async () => {
  const { partager } = await import("./modules/partage.js");
  partager(document.title, location.href);
});""", "js", "Un module chargé à la demande"),
        code("""// Décharger un travail long pour garder l'interface réactive
function traiterParLots(elements, traiter, taille = 200) {
  let index = 0;
  function lot() {
    const fin = Math.min(index + taille, elements.length);
    for (; index < fin; index += 1) traiter(elements[index]);
    if (index < elements.length) requestAnimationFrame(lot);
  }
  lot();
}""", "js", "Découper un traitement long"),
        p("Les tâches longues de plus de 50 ms bloquent les interactions : l'utilisateur "
          "clique et rien ne se passe. Découper, différer ou déplacer vers un *worker* "
          "préserve la réactivité."),

        h(2, "Mise en cache"),
        p("Un second chargement doit être beaucoup plus rapide que le premier. La mise "
          "en cache est le levier le plus rentable, à condition de nommer les fichiers "
          "par leur empreinte."),
        code("""# Fichiers versionnés : cache long
Cache-Control: public, max-age=31536000, immutable

# HTML : revalidation systématique
Cache-Control: no-cache

# API : cache court et revalidation
Cache-Control: public, max-age=60, stale-while-revalidate=30""", "http",
             "Trois politiques de cache"),
        p("L'empreinte dans le nom (`app.3f2a91.js`) permet un cache d'un an : tout "
          "changement de contenu change le nom du fichier et force un nouveau "
          "téléchargement."),
        box("pratique", "Mesurer l'effet réel",
            "Comparer avant/après avec le même réseau simulé et le même appareil. Une "
            "optimisation non mesurée est une hypothèse, pas un résultat."),
        box("methode", "Cinq optimisations par ordre de rentabilité",
            items=["Compresser et dimensionner les images.",
                   "Différer les scripts non critiques.",
                   "Activer la compression et le cache HTTP.",
                   "Réduire le CSS bloquant au premier écran.",
                   "Supprimer les dépendances inutilisées."]),
    ],
    "keypoints": [
        "LCP, INP et CLS résument la performance perçue.",
        "Les images sont le premier levier de poids.",
        "`width` et `height` évitent les décalages de mise en page.",
        "`font-display: swap` évite un texte invisible.",
        "CSS et JavaScript peuvent bloquer le rendu.",
        "Le découpage de code évite de charger l'inutile.",
        "Un cache long exige des noms de fichiers versionnés.",
    ],
    "bridge": "La page est rapide. La dernière ligne droite concerne la sécurité, le "
              "versionnement et la mise en production.",
    "exercises": [
        ex("Réduire le poids d'une image",
           "Une image de 2,4 Mo s'affiche dans une vignette de 320 pixels.",
           ["Proposez un format et une dimension.",
            "Ajoutez `srcset` et `sizes`.",
            "Réservez l'espace."],
           [("code", """<img
  src="vignette-320.avif"
  srcset="vignette-320.avif 320w, vignette-640.avif 640w"
  sizes="(max-width: 700px) 90vw, 320px"
  width="320" height="320"
  alt="Portrait de l'autrice"
  loading="lazy"
  decoding="async">"""),
            "Une image affichée sur 320 pixels n'a pas besoin de 3000 pixels de large, "
            "même sur un écran dense : 640 pixels suffisent.",
            "`width` et `height` réservent la place et suppriment le décalage de mise "
            "en page."]),
        ex("Traiter une liste sans bloquer",
           "Un tri de 50 000 éléments fige l'interface deux secondes.",
           ["Mesurez avec `performance.now()`.",
            "Découpez le traitement.",
            "Comparez le ressenti."],
           [("code", """const debut = performance.now();
const resultat = traiterParLots(donnees, transformer, 500);
console.log(`Préparation : ${performance.now() - debut} ms`);

function traiterParLots(items, fn, taille) {
  return new Promise((resolve) => {
    const sortie = [];
    let i = 0;
    (function lot() {
      const fin = Math.min(i + taille, items.length);
      for (; i < fin; i += 1) sortie.push(fn(items[i]));
      if (i < items.length) requestAnimationFrame(lot);
      else resolve(sortie);
    })();
  });
}"""),
            "Le découpage ne réduit pas le temps total, mais rend la main entre chaque "
            "lot : l'interface reste réactive.",
            "`performance.now()` fournit une mesure haute résolution, plus précise que "
            "`Date.now()`."]),
        ex("Auditer une page",
           "Lancez Lighthouse sur votre projet et relevez trois problèmes.",
           ["Notez le LCP et le CLS.",
            "Identifiez la ressource la plus lourde.",
            "Corrigez, puis remesurez."],
           ["Un LCP élevé vient souvent d'une image non optimisée ou d'une police "
            "bloquante.",
            "Un CLS élevé vient d'images sans dimensions ou d'un contenu injecté en "
            "haut de page.",
            ("code", """# Comparer deux rapports
npx lighthouse http://localhost:8080 --output=json --output-path=avant.json
# ... optimisations ...
npx lighthouse http://localhost:8080 --output=json --output-path=apres.json""")],
           level="Mesure"),
    ],
    "quiz": [
        quiz("Que mesure le LCP ?",
             ["La réactivité", "L'affichage du plus grand élément",
              "La stabilité visuelle", "Le poids total"],
             1,
             "Largest Contentful Paint mesure quand le contenu principal est visible."),
        quiz("Quel attribut évite un décalage de mise en page sur une image ?",
             ["`alt`", "`width` et `height`", "`loading`", "`decoding`"],
             1,
             "Les dimensions réservent l'espace avant le chargement."),
        quiz("Que fait `font-display: swap` ?",
             ["Masque le texte", "Affiche un substitut immédiatement",
              "Bloque le rendu", "Télécharge deux polices"],
             1,
             "Le texte est visible tout de suite, puis remplacé par la police "
             "téléchargée."),
        quiz("Quel attribut exécute un script sans bloquer l'analyse, en préservant l'ordre ?",
             ["`async`", "`defer`", "`load`", "`type`"],
             1,
             "`defer` télécharge en parallèle et exécute après l'analyse, dans l'ordre."),
        quiz("Pourquoi versionner les noms de fichiers ?",
             ["Pour la sécurité", "Pour permettre un cache long",
              "Pour réduire le poids", "Pour le référencement"],
             1,
             "Un nom qui change à chaque modification permet de mettre en cache "
             "durablement sans risque de servir une ancienne version."),
    ],
}
