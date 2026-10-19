from bookkit.dsl import (box, code, defn, ex, fig, h, ol, p, quiz, table, ul)

CH = {
    "title": "La structure d'un document HTML5",
    "subtitle": "Le squelette invisible d'une page : ce que le navigateur lit avant "
                "d'afficher le premier pixel.",
    "duration": "2 h 45",
    "level": "Débutant",
    "prereq": "chapitres 1 et 2",
    "objectives": [
        "Écrire un document HTML5 complet et valide.",
        "Comprendre le rôle de chaque métadonnée de l'en-tête.",
        "Organiser les ressources externes sans bloquer le rendu.",
        "Structurer le corps du document avec les éléments sémantiques.",
        "Contrôler l'encodage, la langue et l'aperçu social d'une page.",
    ],
    "blocks": [
        h(2, "Anatomie d'un document"),
        p("Un fichier HTML est un texte brut. Le navigateur le lit de haut en bas, "
          "construit progressivement une représentation en mémoire — le DOM — puis "
          "applique les styles et peint l'écran. Tout ce qui précède le contenu "
          "visible décrit **comment interpréter** ce contenu."),
        defn("DOM", "Document Object Model : représentation arborescente du document, "
                    "manipulable par les styles et les scripts. Chaque balise devient "
                    "un nœud, chaque attribut une propriété."),
        code("""<!doctype html>
<html lang="fr">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Le titre de ma page</title>
  <meta name="description" content="Résumé de la page en une phrase.">
  <link rel="stylesheet" href="css/style.css">
</head>
<body>
  <header>
    <h1>Le titre visible</h1>
  </header>
  <main>
    <p>Le contenu de la page.</p>
  </main>
  <footer>
    <p>© 2026 — Mon site</p>
  </footer>
  <script src="js/app.js" defer></script>
</body>
</html>""", "html", "Le document HTML5 complet, avec sa structure sémantique"),
        p("Ce modèle contient déjà l'essentiel : déclaration de type, langue, "
          "encodage, adaptation mobile, titre, description, feuille de style, "
          "structure sémantique et script non bloquant. Nous détaillons chaque ligne "
          "dans ce chapitre."),

        h(2, "Le doctype et le mode d'affichage"),
        p("La première ligne n'est pas une balise : c'est une déclaration. "
          "`<!doctype html>` indique au navigateur d'utiliser le **mode standard**, "
          "celui qui respecte les spécifications. Son absence déclenche le mode "
          "« quirks », hérité des années 1990, où le calcul des tailles et des "
          "marges diffère."),
        table(["Déclaration", "Mode", "Conséquences"],
              [["`<!doctype html>`", "Standard", "Modèle de boîte conforme, comportements prévisibles"],
               ["Doctype HTML 4 long", "Presque standard", "Quelques différences de rendu"],
               ["Aucun doctype", "Quirks", "Largeurs calculées différemment, styles imprévisibles"]],
              widths=[3.4, 2.4, 5.2], first_col_bold=True,
              caption="Trois modes d'affichage et leurs effets"),
        p("La déclaration HTML5 est volontairement courte et insensible à la casse. "
          "Gardez-la en minuscules, par cohérence avec le reste du document. "
          "N'essayez pas d'ajouter un numéro de version : HTML5 est un standard "
          "vivant, sans version figée."),

        h(2, "L'élément html et la langue"),
        p("L'élément `html` est la racine du document. Son attribut `lang` déclare la "
          "langue du contenu. Cette information, invisible, a des conséquences "
          "concrètes : prononciation par les lecteurs d'écran, césure, correction "
          "orthographique, traduction automatique, règles typographiques."),
        code("""<html lang="fr">          <!-- français -->
<html lang="fr-BE">       <!-- français de Belgique -->
<html lang="en">          <!-- anglais -->
<html lang="pt-BR">       <!-- portugais du Brésil -->""", "html",
             "Déclarer une langue imprécise est toujours mieux que ne rien déclarer"),
        p("Un document bilingue déclare la langue de chaque passage avec l'attribut "
          "`lang` sur l'élément concerné : `<span lang=\"en\">responsive design</span>`. "
          "Les lecteurs d'écran changeront alors de prononciation au milieu du texte."),

        h(2, "L'en-tête : ce que l'utilisateur ne voit pas"),
        p("L'élément `head` contient les métadonnées. Aucune de ses lignes ne "
          "s'affiche directement, mais chacune influence le rendu, le référencement "
          "ou le comportement du navigateur."),
        table(["Élément", "Rôle", "Obligatoire ?", "Recommandation"],
              [["`meta charset`", "Encodage des caractères", "De fait", "`utf-8`, en premier"],
               ["`meta viewport`", "Adaptation aux écrans mobiles", "De fait", "`width=device-width, initial-scale=1`"],
               ["`title`", "Titre de l'onglet et du résultat de recherche", "Oui", "Unique, 50 à 60 caractères"],
               ["`meta description`", "Résumé affiché par les moteurs", "Non", "120 à 155 caractères"],
               ["`link rel=stylesheet`", "Feuille de style", "Non", "Une feuille principale"],
               ["`link rel=icon`", "Favicon", "Non", "SVG + repli PNG"],
               ["`meta og:*`", "Aperçu sur les réseaux sociaux", "Non", "Titre, description, image"],
               ["`script`", "Comportement", "Non", "`defer` ou `type=module`"]],
              widths=[2.6, 3.8, 1.6, 3.2], first_col_bold=True,
              caption="Les métadonnées d'un en-tête de qualité"),
        h(3, "L'encodage des caractères"),
        p("`<meta charset=\"utf-8\">` doit apparaître dans les 1024 premiers octets du "
          "fichier. Le serveur peut aussi déclarer l'encodage dans l'en-tête HTTP "
          "`Content-Type` ; en cas de contradiction, c'est généralement l'en-tête "
          "HTTP qui gagne, d'où l'importance de configurer les deux."),
        p("Pourquoi UTF-8 ? Parce qu'il représente tous les caractères de tous les "
          "systèmes d'écriture, y compris les emojis, avec un octet par caractère "
          "ASCII. Un fichier enregistré en ISO-8859-1 affichera « Ã© » à la place de "
          "« é » : les octets sont corrects, l'interprétation ne l'est pas."),
        h(3, "L'adaptation mobile"),
        p("Sans la balise `viewport`, un téléphone suppose une largeur de page de "
          "980 pixels et dézoome pour tout faire tenir : le texte devient minuscule. "
          "`width=device-width` aligne la largeur du viewport sur celle de l'écran."),
        code("""<meta name="viewport" content="width=device-width, initial-scale=1">
<!-- Ne pas écrire : -->
<meta name="viewport" content="width=1024, maximum-scale=1, user-scalable=no">""",
             "html", "Une déclaration correcte, et trois erreurs fréquentes"),
        box("attention", "Bloquer le zoom est une faute d'accessibilité",
            "`user-scalable=no` et `maximum-scale=1` empêchent les personnes "
            "malvoyantes d'agrandir le texte. Cette pratique, encore répandue, est "
            "contraire aux règles d'accessibilité et pénalisée par les moteurs de "
            "recherche."),
        h(3, "Titre et description"),
        p("Le `title` est le texte affiché dans l'onglet, dans les favoris et comme "
          "lien dans les résultats de recherche. Il doit être unique par page, "
          "descriptif et placé avant tout contenu. La `meta description` n'influence "
          "pas directement le classement, mais elle détermine le texte de l'extrait : "
          "elle mérite une rédaction soignée."),
        code("""<title>Guide HTML5 : structure d'un document — Espritropic</title>
<meta name="description"
      content="Comprendre le doctype, l'encodage, le viewport et les métadonnées
              essentielles d'un document HTML5 valide.">""", "html",
             "Le titre décrit le contenu, la marque est placée en fin"),
        h(3, "L'aperçu social"),
        p("Les réseaux sociaux lisent des balises Open Graph pour construire l'aperçu "
          "d'un lien. Sans elles, ils devinent, souvent mal. Quatre propriétés "
          "suffisent :"),
        code("""<meta property="og:type" content="article">
<meta property="og:title" content="La structure d'un document HTML5">
<meta property="og:description" content="Doctype, encodage, viewport : ce que le
      navigateur lit avant d'afficher.">
<meta property="og:image" content="https://exemple.fr/img/apercu-html5.png">
<meta property="og:url" content="https://exemple.fr/html5/structure">""", "html",
             "Un aperçu social correct se prépare, il ne se devine pas"),
        p("L'image doit mesurer au moins 1200 × 630 pixels et rester lisible en "
          "vignette. Testez le résultat avec les validateurs de chaque plateforme "
          "avant de publier une page importante."),
        h(3, "La favicon"),
        p("La favicon apparaît dans l'onglet, les favoris et l'écran d'accueil "
          "mobile. Un fichier SVG s'adapte à toutes les tailles ; un PNG de 32 pixels "
          "sert de repli. Déclarez-les explicitement pour éviter une requête "
          "automatique vers `/favicon.ico`."),
        code("""<link rel="icon" href="favicon.svg" type="image/svg+xml">
<link rel="alternate icon" href="favicon.png" sizes="32x32">
<link rel="apple-touch-icon" href="apple-touch-icon.png">""", "html",
             "Trois déclarations pour couvrir navigateurs et mobiles"),

        h(2, "Charger les ressources sans bloquer"),
        p("Le navigateur construit le document en le parcourant. Une feuille de style "
          "rencontrée bloque le rendu : il doit connaître les styles avant de peindre, "
          "sinon l'utilisateur verrait un flash de contenu non stylé (FOUC). Un script "
          "classique bloque l'analyse du document : il peut modifier la page, il faut "
          "donc l'exécuter dans l'ordre."),
        fig("compare", "Deux façons de charger un script",
            ("SANS defer", ["Bloque l'analyse du HTML", "Exécution immédiate",
                            "Le contenu suivant attend"],
             "AVEC defer", ["Analyse HTML poursuivie", "Exécution après l'analyse",
                            "Ordre des scripts respecté"]),
            height=215),
        table(["Forme", "Quand le script s'exécute", "Usage"],
              [["`<script src>`", "Immédiatement, bloque l'analyse", "Rare, scripts critiques"],
               ["`<script defer src>`", "Après l'analyse, dans l'ordre", "Scripts d'interface"],
               ["`<script async src>`", "Dès qu'il est téléchargé", "Compteurs, publicités"],
               ["`<script type=module>`", "Différé par défaut", "Code moderne, imports"]],
              widths=[3.4, 4.2, 3.4], first_col_bold=True,
              caption="Quatre modes de chargement des scripts"),
        p("Pour les feuilles de style non critiques (polices, thèmes alternatifs), "
          "l'attribut `media` ou le chargement asynchrone évitent de retarder le "
          "premier rendu. Pour les polices, `font-display: swap` affiche "
          "immédiatement une police de substitution."),
        code("""<link rel="stylesheet" href="css/style.css">
<link rel="preload" href="fonts/inter-var.woff2" as="font"
      type="font/woff2" crossorigin>
<link rel="stylesheet" href="css/print.css" media="print">""", "html",
             "Ordonner les ressources : critique d'abord, le reste ensuite"),

        h(2, "Structurer le corps du document"),
        p("Le `body` contient le contenu visible. Depuis HTML5, des éléments "
          "sémantiques décrivent les grandes régions de la page. Ils n'apportent "
          "aucun style par défaut : leur intérêt est de fournir des **repères** aux "
          "lecteurs d'écran, aux moteurs de recherche et aux développeurs."),
        table(["Élément", "Région décrite", "Nombre par page"],
              [["`header`", "En-tête de page ou de section", "Un par contexte"],
               ["`nav`", "Ensemble de liens de navigation", "Un à trois"],
               ["`main`", "Contenu principal, unique", "Un seul"],
               ["`article`", "Contenu autonome, réutilisable", "Autant que nécessaire"],
               ["`section`", "Section thématique, toujours titrée", "Autant que nécessaire"],
               ["`aside`", "Contenu connexe", "Zéro à deux"],
               ["`footer`", "Pied de page ou de section", "Un par contexte"]],
              widths=[2.2, 5.6, 3.2], first_col_bold=True,
              caption="Sept éléments pour décrire une page sans une seule classe CSS"),
        code("""<body>
  <a class="skip-link" href="#contenu">Aller au contenu</a>
  <header>
    <nav aria-label="Navigation principale">
      <ul>
        <li><a href="/">Accueil</a></li>
        <li><a href="/cours">Cours</a></li>
      </ul>
    </nav>
  </header>
  <main id="contenu">
    <h1>Un titre unique</h1>
    <article>
      <h2>Un titre de section</h2>
      <p>Un paragraphe.</p>
    </article>
  </main>
  <footer><p>© 2026</p></footer>
</body>""", "html", "Une page complète, structurée sans une seule div"),
        box("retenir", "La règle du repère",
            "Chaque région sémantique doit être reconnaissable à l'œil nu. Si vous "
            "devez ajouter une classe pour expliquer à quoi sert une `<section>`, "
            "c'est probablement qu'elle n'a pas de rôle structurant : utilisez une "
            "`<div>` neutre."),
        h(3, "La hiérarchie des titres"),
        p("Les titres `h1` à `h6` forment le sommaire du document. Le niveau doit "
          "refléter la profondeur, jamais la taille souhaitée. Un `h3` ne doit pas "
          "apparaître sans `h2` parent, et une page possède en général un seul `h1`."),
        code("""<h1>Guide HTML5</h1>
  <h2>Structure</h2>
    <h3>Doctype</h3>
    <h3>En-tête</h3>
  <h2>Sémantique</h2>
    <h3>Régions</h3>""", "html", "Une hiérarchie correcte se lit comme un plan"),
        p("Les lecteurs d'écran permettent de naviguer de titre en titre : une "
          "hiérarchie cohérente transforme une page de 3 000 mots en document "
          "explorable en quelques secondes."),

        h(2, "Les commentaires et l'indentation"),
        p("Un commentaire HTML s'écrit `<!-- ... -->`. Il reste visible dans le code "
          "source envoyé au navigateur : n'y placez jamais d'information sensible, "
          "comme un mot de passe ou une adresse interne. Réservez-le aux repères de "
          "structure et aux notes de maintenance."),
        code("""<!-- Début de la zone de navigation principale -->
<nav aria-label="Navigation principale">...</nav>
<!-- Fin de la zone de navigation -->

<!-- Ne jamais écrire :
     mot de passe temporaire : ****
     serveur de préproduction : 10.0.0.12
-->""", "html", "Un commentaire utile, un commentaire dangereux"),
        p("L'indentation n'a aucun effet sur le rendu, mais un effet majeur sur la "
          "maintenance. Deux espaces par niveau, une balise par ligne pour les "
          "structures, et des lignes de moins de 100 caractères rendent les "
          "différences Git lisibles."),

        h(2, "Valider et diagnostiquer"),
        p("La validation signale les erreurs de grammaire. Certaines sont bloquantes, "
          "d'autres sont des avertissements à comprendre plutôt qu'à faire taire. "
          "Trois outils complètent la validation : l'inspecteur, l'audit "
          "d'accessibilité et le contrôle de rendu sans styles."),
        table(["Contrôle", "Outil", "Ce qu'il révèle"],
              [["Grammaire HTML", "Validateur W3C / vnu", "Balises mal fermées, attributs invalides"],
               ["Accessibilité", "axe DevTools, Lighthouse", "Contrastes, libellés, titres manquants"],
               ["Performance", "Lighthouse, PageSpeed", "Ressources bloquantes, images lourdes"],
               ["Rendu sans CSS", "Désactivation des styles", "Structure illisible, ordre incohérent"],
               ["Aperçu social", "Validateurs Open Graph", "Image absente, titre tronqué"]],
              widths=[2.4, 3.8, 4.8], first_col_bold=True,
              caption="Cinq contrôles à effectuer avant de publier une page"),
        box("methode", "Le protocole des cinq minutes",
            "Avant chaque commit : valider le HTML, vérifier la console, tester au "
            "clavier, réduire la fenêtre à 360 pixels, couper le CSS. Cinq minutes "
            "qui évitent des heures de correction."),
    ],
    "keypoints": [
        "`<!doctype html>` déclenche le mode standard ; sans lui, le rendu devient imprévisible.",
        "`lang` et `charset` sont des métadonnées invisibles aux effets majeurs.",
        "Le viewport ne doit jamais bloquer le zoom.",
        "Titre et description se rédigent page par page, avec soin.",
        "Les scripts se chargent avec `defer` ou en module pour ne pas bloquer l'analyse.",
        "Les régions sémantiques décrivent la page ; les titres forment son plan.",
        "Un document valide est un prérequis, pas une garantie de qualité.",
    ],
    "bridge": "La structure est posée. Le chapitre suivant entre dans le contenu : "
              "titres, paragraphes, listes, citations et tout l'art de choisir la "
              "balise juste.",
    "exercises": [
        ex("Écrire un en-tête complet",
           "Créez la page `article.html` d'un blog personnel.",
           ["Déclarez la langue française, l'encodage UTF-8 et le viewport.",
            "Rédigez un titre de 55 caractères et une description de 140 caractères.",
            "Ajoutez les balises Open Graph et une favicon SVG.",
            "Validez le document."],
           [("code", """<!doctype html>
<html lang="fr">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Cinq erreurs de débutant en HTML — Mon blog</title>
  <meta name="description" content="Les cinq erreurs de structure HTML les plus
        fréquentes, leurs conséquences concrètes et comment les corriger en une
        minute.">
  <meta property="og:type" content="article">
  <meta property="og:title" content="Cinq erreurs de débutant en HTML">
  <meta property="og:image" content="https://exemple.fr/img/erreurs-html.png">
  <link rel="icon" href="favicon.svg" type="image/svg+xml">
  <link rel="stylesheet" href="css/style.css">
</head>
<body>...</body>
</html>"""),
            "Les longueurs indiquées ne sont pas des règles absolues : ce sont des "
            "seuils d'affichage. Un titre de 55 caractères reste lisible dans "
            "l'onglet et dans les résultats de recherche.",
            "La validation doit être lancée après chaque modification importante. "
            "Corrigez d'abord les erreurs, puis examinez les avertissements : "
            "certains sont légitimes, comme l'usage de `aria-*` sur un rôle "
            "personnalisé."]),
        ex("Réparer une page non structurée",
           "Cette page fonctionne visuellement mais n'utilise que des `div`.",
           ["Réécrivez-la avec les éléments sémantiques appropriés.",
            "Corrigez la hiérarchie des titres.",
            "Justifiez chaque remplacement en une phrase."],
           [("code", """<body>
  <div class="top"><div class="logo">Mon site</div></div>
  <div class="menu"><a href="/">Accueil</a> <a href="/blog">Blog</a></div>
  <div class="content">
    <div class="title">Bienvenue</div>
    <div class="text">Un paragraphe.</div>
    <div class="title2">Derniers articles</div>
  </div>
  <div class="bottom">© 2026</div>
</body>"""),
            ("code", """<body>
  <header><p>Mon site</p></header>
  <nav aria-label="Navigation principale">
    <a href="/">Accueil</a> <a href="/blog">Blog</a>
  </nav>
  <main>
    <h1>Bienvenue</h1>
    <p>Un paragraphe.</p>
    <section>
      <h2>Derniers articles</h2>
    </section>
  </main>
  <footer><p>© 2026</p></footer>
</body>"""),
            "Chaque remplacement correspond à un rôle : `header` pour l'identité, "
            "`nav` pour les liens, `main` pour le contenu unique, `section` pour un "
            "bloc thématique titré, `footer` pour les mentions. Les `div` restantes "
            "seraient des conteneurs purement visuels, sans rôle documentaire."],
           level="Diagnostic"),
        ex("Contrôler le chargement des ressources",
           "Prenez une page contenant une feuille de style, une police et un script.",
           ["Chargez-la avec un réseau bridé (3G lente) dans les outils du navigateur.",
            "Notez l'ordre des requêtes et le moment du premier rendu.",
            "Ajoutez `defer` au script et `preload` à la police, puis comparez."],
           ["La feuille de style apparaît avant le script et bloque le rendu ; la "
            "police est demandée après l'analyse du CSS ; le script bloque l'analyse "
            "jusqu'à son exécution.",
            "Sans `defer`, le navigateur attend le téléchargement et l'exécution du "
            "script avant de poursuivre l'analyse du HTML. Le premier rendu est "
            "retardé d'autant.",
            "Avec `defer`, le script se télécharge en parallèle et s'exécute après "
            "l'analyse. Avec `preload` sur la police, la requête démarre plus tôt : "
            "le texte apparaît dans la bonne police plus rapidement, sans bloquer "
            "pour autant."]),
        ex("Auditer l'en-tête d'un site réel",
           "Choisissez trois sites de nature différente : institutionnel, média, "
           "commerce.",
           ["Relevez leurs balises `title`, `description`, Open Graph et favicon.",
            "Comparez la longueur des titres et la qualité des descriptions.",
            "Identifiez une bonne pratique à reprendre et une erreur à éviter."],
           ["Les titres varient de 25 à 90 caractères. Les plus longs sont tronqués "
            "dans les résultats de recherche ; les plus courts perdent l'occasion de "
            "préciser le sujet.",
            "Les sites médias privilégient le titre de l'article puis la marque ; "
            "les sites institutionnels placent souvent la marque en premier, ce qui "
            "est adapté à une recherche de notoriété.",
            "Bonne pratique fréquente : une description rédigée spécifiquement, "
            "différente du premier paragraphe. Erreur fréquente : la même description "
            "sur toutes les pages, ou l'absence d'image Open Graph."],
           level="Analyse"),
    ],
    "quiz": [
        quiz("Quel est l'effet de l'absence de `<!doctype html>` ?",
             ["Le navigateur refuse d'afficher la page",
              "Le mode quirks est activé et le calcul des tailles change",
              "Les styles CSS sont ignorés",
              "Le document devient invalide pour les moteurs de recherche"],
             1,
             "Sans doctype, les navigateurs basculent en mode quirks pour rester "
             "compatibles avec les pages anciennes : le modèle de boîte et certaines "
             "propriétés se comportent différemment."),
        quiz("Où doit apparaître `<meta charset=\"utf-8\">` ?",
             ["N'importe où dans le document",
              "Dans les 1024 premiers octets du fichier",
              "Après la balise `title`",
              "Dans le `body`, avant le contenu"],
             1,
             "Le navigateur doit connaître l'encodage avant d'analyser le texte : la "
             "déclaration doit figurer très tôt dans l'en-tête."),
        quiz("Quelle affirmation sur `defer` est exacte ?",
             ["Le script s'exécute avant l'analyse du HTML",
              "Le script s'exécute après l'analyse, dans l'ordre de déclaration",
              "Le script s'exécute dès son téléchargement",
              "Le script ne s'exécute jamais"],
             1,
             "`defer` diffère l'exécution jusqu'à la fin de l'analyse du document et "
             "conserve l'ordre des scripts, contrairement à `async`."),
        quiz("Combien d'éléments `main` une page peut-elle contenir ?",
             ["Un seul", "Deux au maximum", "Un par section", "Autant que nécessaire"],
             0,
             "`main` désigne le contenu principal unique du document. Plusieurs "
             "éléments `main` visibles rendraient la navigation par régions ambiguë."),
        quiz("Pourquoi `user-scalable=no` est-il déconseillé ?",
             ["Il ralentit le chargement",
              "Il empêche l'agrandissement du texte et nuit à l'accessibilité",
              "Il bloque les images",
              "Il rend le HTML invalide"],
             1,
             "Le zoom est un mécanisme d'accessibilité essentiel pour les personnes "
             "malvoyantes ; le désactiver est contraire aux bonnes pratiques et aux "
             "critères d'accessibilité."),
    ],
}
