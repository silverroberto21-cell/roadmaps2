from bookkit.dsl import (box, code, defn, ex, fig, h, ol, p, quiz, table, ul)

CH = {
    "title": "Liens et navigation",
    "subtitle": "Le Web est un réseau de documents reliés. Savoir écrire une URL, "
                "c'est construire l'architecture du site.",
    "duration": "2 h 30",
    "level": "Débutant",
    "prereq": "chapitre 4",
    "objectives": [
        "Écrire des liens relatifs et absolus sans erreur de chemin.",
        "Concevoir une navigation accessible, cohérente et utilisable au clavier.",
        "Distinguer les liens internes, externes, de téléchargement et de contact.",
        "Maîtriser les ancres et les URL portant une requête.",
        "Éviter les pièges de sécurité des liens externes.",
    ],
    "blocks": [
        h(2, "L'anatomie d'un lien"),
        p("Un lien est un élément `a` doté de l'attribut `href`. Sa valeur est une "
          "URL : absolue si elle commence par un schéma, relative si elle décrit un "
          "chemin à partir du document courant. Le texte affiché — le **libellé** — "
          "est ce que l'utilisateur lit et ce que les moteurs indexent."),
        code("""<a href="https://developer.mozilla.org/">Documentation MDN</a>
<a href="/cours/html5">Cours HTML5</a>
<a href="../contact.html">Contact</a>
<a href="#sommaire">Aller au sommaire</a>
<a href="mailto:contact@exemple.fr">Écrire à l'équipe</a>
<a href="tel:+22901020304">Appeler</a>""", "html", "Six liens, six usages"),
        fig("stack", "Les parties d'une URL",
            [("Schéma", "https — protocole de transport"),
             ("Hôte et port", "exemple.fr:443 — la machine et le service"),
             ("Chemin", "/cours/html5 — la ressource"),
             ("Requête", "?page=2&tri=date — les paramètres"),
             ("Ancre", "#exercices — la position dans le document")],
            height=245),
        p("L'ancre n'est pas envoyée au serveur : elle est traitée localement. C'est "
          "pourquoi modifier une ancre ne provoque pas de nouvelle requête, alors "
          "que modifier la requête, oui."),

        h(2, "Chemins relatifs : la règle des dossiers"),
        p("Un chemin relatif se lit toujours depuis le fichier qui contient le lien. "
          "`./` désigne le dossier courant, `../` le dossier parent. Une erreur de "
          "chemin produit une 404 qui ne se voit pas en développement si le fichier "
          "existe par hasard ailleurs."),
        table(["Écriture", "Cible", "Depuis `blog/article.html`"],
              [["`contact.html`", "Même dossier", "`blog/contact.html`"],
               ["`/contact.html`", "Racine du site", "`contact.html`"],
               ["`../index.html`", "Dossier parent", "`index.html`"],
               ["`../images/logo.svg`", "Dossier parent puis `images`", "`images/logo.svg`"],
               ["`https://exemple.fr/a`", "URL absolue", "toujours identique"]],
              widths=[3.4, 4.2, 4.0], caption="Cinq écritures de chemin et leur résolution"),
        box("attention", "Un chemin absolu de serveur n'est pas un chemin local",
            "`/images/logo.png` désigne la racine du site **telle que servie**. Si "
            "vous ouvrez la page en `file://`, cette racine devient la racine du "
            "disque et l'image disparaît. C'est une raison supplémentaire de "
            "travailler avec un serveur local."),
        code("""mon-site/
├── index.html
├── contact.html
└── blog/
    ├── article.html
    └── images/
        └── schema.png""", "text", "Une arborescence pour vérifier les chemins"),
        p("Depuis `blog/article.html` : `../contact.html` mène à la page de contact, "
          "`images/schema.png` à l'image du dossier `blog`, et "
          "`../index.html` à l'accueil. Trois liens, trois chemins différents, tous "
          "corrects."),

        h(2, "Concevoir une navigation"),
        p("La navigation est la carte du site. Elle doit rester stable d'une page à "
          "l'autre, indiquer où l'on se trouve et rester utilisable au clavier comme "
          "au doigt. Elle repose sur un élément `nav` contenant une liste de liens."),
        code("""<nav aria-label="Navigation principale">
  <ul>
    <li><a href="/" aria-current="page">Accueil</a></li>
    <li><a href="/cours/">Cours</a></li>
    <li><a href="/ressources/">Ressources</a></li>
    <li><a href="/contact/">Contact</a></li>
  </ul>
</nav>""", "html", "Une navigation balisée, avec la page courante indiquée"),
        p("`aria-current=\"page\"` signale la page active. Les lecteurs d'écran "
          "l'annoncent, et le CSS peut la styler sans ajouter de classe :"),
        code("""[aria-current="page"] {
  font-weight: 700;
  text-decoration: none;
  border-bottom: 3px solid currentColor;
}""", "css", "Styler la page courante à partir de son état sémantique"),
        table(["Élément de navigation", "Rôle", "Bonne pratique"],
              [["Menu principal", "Accès aux grandes sections", "Cinq à sept entrées maximum"],
               ["Fil d'Ariane", "Situation dans la hiérarchie", "Liens, sauf le dernier"],
               ["Menu de pied de page", "Liens secondaires et légaux", "Organisé en colonnes titrées"],
               ["Lien d'évitement", "Sauter la navigation", "Premier élément focusable"],
               ["Pagination", "Parcours d'une liste", "Numéros et précédent/suivant"]],
              widths=[3.4, 4.2, 4.0], first_col_bold=True,
              caption="Cinq dispositifs de navigation complémentaires"),
        box("retenir", "Le lien d'évitement",
            "Un lien d'évitement permet à un utilisateur au clavier de sauter la "
            "navigation répétée sur chaque page. Il est invisible au repos, mais "
            "apparaît au premier appui sur Tab. C'est l'un des gains d'accessibilité "
            "les plus simples à mettre en œuvre."),
        code(""".skip-link {
  position: absolute;
  left: -9999px;
}
.skip-link:focus {
  left: 1rem;
  top: 1rem;
  padding: .75rem 1rem;
  background: #0f2e4c;
  color: #fff;
}""", "css", "Un lien d'évitement accessible et discret"),

        h(2, "Liens externes, téléchargements et contacts"),
        p("Un lien sortant mérite d'être signalé. Deux approches coexistent : ajouter "
          "une icône ou une mention textuelle, ou ouvrir dans un nouvel onglet. Cette "
          "seconde option doit rester rare : elle prive l'utilisateur du bouton "
          "« Retour » et perturbe la navigation."),
        code("""<a href="https://example.com/rapport.pdf"
   download="rapport-2026.pdf">
  Télécharger le rapport (PDF, 2,4 Mo)
</a>

<a href="https://example.com" target="_blank" rel="noopener noreferrer">
  Site partenaire <span class="visually-hidden">(nouvel onglet)</span>
</a>""", "html", "Téléchargement explicite et lien externe sécurisé"),
        p("L'attribut `download` suggère un téléchargement plutôt qu'une navigation ; "
          "il ne fonctionne que pour les ressources de même origine, par sécurité. "
          "`rel=\"noopener\"` empêche la page ouverte de manipuler la page d'origine "
          "via `window.opener`."),
        defn("Tabnabbing", "Attaque où une page ouverte dans un nouvel onglet "
                           "remplace le contenu de l'onglet d'origine par une fausse "
                           "page de connexion. `rel=\"noopener\"` la neutralise."),
        table(["Attribut", "Effet", "Recommandation"],
              [["`href`", "Destination", "Obligatoire"],
               ["`target=\"_blank\"`", "Nouvel onglet", "Toujours avec `rel=noopener`"],
               ["`rel=\"nofollow\"`", "Ne pas suivre pour le référencement", "Contenus sponsorisés"],
               ["`download`", "Télécharger au lieu de naviguer", "Même origine uniquement"],
               ["`hreflang`", "Langue de la cible", "Sites multilingues"],
               ["`aria-label`", "Nom accessible du lien", "Libellés ambigus"]],
              widths=[3.0, 4.4, 4.2], first_col_bold=True,
              caption="Six attributs de lien et leur usage"),
        p("Le libellé d'un lien doit être compréhensible hors contexte. « Cliquez ici » "
          "ne dit rien lorsqu'un lecteur d'écran liste les liens de la page. Préférez "
          "« Télécharger le rapport annuel 2026 »."),

        h(2, "Ancres, fragments et retour en haut"),
        p("Une ancre pointe vers un identifiant du document. Elle sert à construire "
          "un sommaire, à lier une section précise ou à revenir en haut de page."),
        code("""<nav aria-label="Sommaire">
  <a href="#structure">Structure</a> ·
  <a href="#semantique">Sémantique</a>
</nav>

<h2 id="structure">Structure</h2>
...
<h2 id="semantique">Sémantique</h2>
...
<a href="#top">Revenir en haut</a>""", "html", "Un sommaire interne et un retour en haut"),
        p("Le défilement vers l'ancre peut être adouci avec `scroll-behavior: smooth`, "
          "à condition de respecter la préférence de réduction des animations :"),
        code("""html { scroll-behavior: smooth; }

@media (prefers-reduced-motion: reduce) {
  html { scroll-behavior: auto; }
}""", "css", "Un défilement doux qui respecte les préférences système"),
        p("L'identifiant doit être unique, sans espace, et commencer par une lettre. "
          "Les accents sont autorisés en HTML5, mais évitez-les dans les ancres : ils "
          "compliquent les liens partagés et les copier-coller."),

        h(2, "Liens et référencement"),
        p("Les moteurs de recherche suivent les liens pour découvrir les pages. Trois "
          "principes gouvernent cette exploration : la **profondeur** (nombre de "
          "clics depuis l'accueil), la **stabilité** des URL et la **pertinence** des "
          "libellés."),
        ul("Une page importante ne devrait pas être à plus de trois clics de l'accueil.",
           "Une URL ne doit pas changer sans redirection 301 : sinon, le référencement "
           "acquis est perdu.",
           "Un lien doit décrire sa cible ; les libellés génériques diluent l'information.",
           "Un lien cassé est une impasse pour l'utilisateur comme pour le robot."),
        code("""# Vérifier les liens d'un site statique
$ npx linkinator ./public --recurse --skip "mailto:.*"

# Ou avec un outil plus ancien
$ wget --spider --recursive --no-parent https://exemple.fr""", "bash",
             "Détecter les liens cassés avant la mise en ligne"),
        box("methode", "Tester une navigation",
            items=["Parcourir tout le site au clavier, sans souris.",
                   "Vérifier que le focus est toujours visible.",
                   "Cliquer chaque lien du menu depuis au moins trois pages.",
                   "Tester avec la largeur d'un téléphone et le zoom à 200 %."]),
    ],
    "keypoints": [
        "Un lien se lit depuis le document qui le contient : `./`, puis `../`.",
        "Une navigation est une liste de liens dans un élément `nav` nommé.",
        "`aria-current=\"page\"` indique la page active et se style sans classe.",
        "Le lien d'évitement est la première amélioration d'accessibilité à ajouter.",
        "`target=\"_blank\"` exige `rel=\"noopener\"`.",
        "Le libellé d'un lien doit être compréhensible hors contexte.",
        "Les URL stables et les liens valides sont la base du référencement.",
    ],
    "bridge": "Les pages communiquent. Il reste à les habiller : images, vidéos et "
              "audio, avec les bonnes pratiques de poids et d'accessibilité.",
    "exercises": [
        ex("Résoudre des chemins relatifs",
           "Voici une arborescence. Écrivez les liens demandés depuis "
           "`blog/2026/article.html`.",
           ["Vers la page d'accueil `index.html`.",
            "Vers l'image `blog/2026/images/schema.png`.",
            "Vers la feuille `css/style.css` à la racine.",
            "Vers l'ancre `#conclusion` de la page courante."],
           ["`../../index.html` : deux remontées (2026, puis blog) avant d'atteindre "
            "la racine.",
            "`images/schema.png` : le dossier `images` est un enfant du dossier "
            "courant `2026`.",
            "`../../css/style.css` : deux remontées puis descente dans `css`.",
            "`#conclusion` : l'ancre seule suffit ; elle ne déclenche aucune requête."]),
        ex("Construire une navigation accessible",
           "Créez l'en-tête d'un site de trois pages : accueil, cours, contact.",
           ["Ajoutez un lien d'évitement en premier élément du body.",
            "Indiquez la page courante avec `aria-current`.",
            "Ajoutez un libellé au menu et testez au clavier."],
           [("code", """<body>
  <a class="skip-link" href="#contenu">Aller au contenu</a>
  <header>
    <nav aria-label="Navigation principale">
      <ul>
        <li><a href="index.html" aria-current="page">Accueil</a></li>
        <li><a href="cours.html">Cours</a></li>
        <li><a href="contact.html">Contact</a></li>
      </ul>
    </nav>
  </header>
  <main id="contenu">...</main>
</body>"""),
            "Le lien d'évitement doit être le premier élément focusable du document. "
            "Il pointe vers l'identifiant du contenu principal, qui doit exister.",
            "`aria-current=\"page\"` est annoncé par les lecteurs d'écran et ciblable "
            "en CSS. Au clavier, chaque lien reçoit un contour visible : ne supprimez "
            "jamais `outline` sans le remplacer."]),
        ex("Auditer les liens d'une page",
           "Prenez une page de votre projet et vérifiez tous ses liens.",
           ["Listez les liens internes, externes, d'ancre et de contact.",
            "Vérifiez chaque libellé hors contexte : est-il compréhensible seul ?",
            "Ajoutez `rel=\"noopener\"` aux liens en nouvel onglet.",
            "Corrigez au moins deux défauts."],
           ["Un tableau à quatre colonnes (type, cible, libellé, état) suffit pour "
            "l'audit. Les liens d'ancre doivent correspondre à un `id` existant.",
            "Un libellé comme « en savoir plus » est ambigu : il faut le compléter, "
            "par exemple « En savoir plus sur le cours HTML5 ».",
            "Les liens externes sans `noopener` exposent la page d'origine à une "
            "manipulation via `window.opener`. La correction est mécanique et sans "
            "effet visible."],
           level="Analyse"),
    ],
    "quiz": [
        quiz("Depuis `blog/article.html`, quel chemin mène à `index.html` situé à la racine ?",
             ["`index.html`", "`../index.html`", "`../../index.html`", "`/../index.html`"],
             1,
             "`article.html` est dans `blog/` : une seule remontée suffit pour "
             "atteindre la racine."),
        quiz("Que fait `rel=\"noopener\"` sur un lien en nouvel onglet ?",
             ["Il empêche le référencement du lien",
              "Il empêche la nouvelle page d'accéder à `window.opener`",
              "Il force le téléchargement",
              "Il ajoute une icône externe"],
             1,
             "`noopener` coupe la référence à la fenêtre d'origine, neutralisant les "
             "manipulations de type tabnabbing."),
        quiz("Quel attribut indique la page courante dans une navigation ?",
             ["`aria-selected`", "`aria-current=\"page\"`", "`class=\"active\"`", "`selected`"],
             1,
             "`aria-current` est l'attribut normalisé ; il porte l'état et peut être "
             "stylé sans classe supplémentaire."),
        quiz("Un lien `href=\"#section\"` déclenche-t-il une requête HTTP ?",
             ["Oui, toujours", "Non, il défile dans le document courant",
              "Oui, si la section est sur une autre page", "Seulement en HTTPS"],
             1,
             "L'ancre reste locale au document : aucune requête n'est envoyée au "
             "serveur, le navigateur déplace simplement la vue."),
        quiz("Pourquoi éviter le libellé « cliquez ici » ?",
             ["Il est trop long",
              "Il n'a pas de sens lorsqu'il est lu hors contexte",
              "Il empêche l'ouverture dans un nouvel onglet",
              "Il rend le HTML invalide"],
             1,
             "Les technologies d'assistance peuvent lister tous les liens : un "
             "libellé générique ne permet alors pas de savoir où mène chaque lien."),
    ],
}
