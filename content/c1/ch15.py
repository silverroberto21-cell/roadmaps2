from bookkit.dsl import (box, code, defn, ex, fig, h, ol, p, quiz, table, ul)

CH = {
    "title": "Composants d'interface et états",
    "subtitle": "Boutons, cartes, alertes, navigation : les briques réutilisables d'une "
                "interface cohérente.",
    "duration": "2 h 45",
    "level": "Intermédiaire",
    "prereq": "chapitre 14",
    "objectives": [
        "Concevoir des composants réutilisables et documentés.",
        "Gérer tous les états d'un composant interactif.",
        "Distinguer les composants par leur rôle et non par leur apparence.",
        "Construire des alertes et messages compréhensibles par tous.",
        "Organiser une bibliothèque de composants cohérente.",
    ],
    "blocks": [
        h(2, "Qu'est-ce qu'un composant ?"),
        p("Un composant est un ensemble autonome : une structure HTML, des styles et "
          "un comportement, réutilisables dans plusieurs contextes. Une carte "
          "d'article, un bouton, un champ de formulaire, une alerte sont des "
          "composants. Une `<div>` colorée n'en est pas un."),
        fig("tree", "Anatomie d'un composant",
            ("Carte", [("Structure", ["article", "image", "titre", "texte", "lien"]),
                       ("Styles", ["variables", "états", "variantes"]),
                       ("Documentation", ["usage", "limites", "exemples"])]),
            height=215),
        p("Un composant se définit par son **rôle**, pas par son apparence. Le même "
          "bouton peut être plein, contouré ou discret : ce sont des variantes, pas des "
          "composants différents."),

        h(2, "Les états d'un élément interactif"),
        p("Un composant interactif connaît au moins cinq états. Les oublier rend "
          "l'interface incomplète, souvent pour les utilisateurs les moins favorisés."),
        table(["État", "Déclencheur", "Traitement CSS"],
              [["Normal", "Repos", "Couleur de base"],
               ["Survol", "Souris au-dessus", "`:hover`"],
               ["Focus", "Sélection au clavier", "`:focus-visible`"],
               ["Actif", "Appui en cours", "`:active`"],
               ["Désactivé", "Action indisponible", "`:disabled`"],
               ["Chargement", "Traitement en cours", "`aria-busy`"],
               ["Erreur", "Validation échouée", "`aria-invalid`"]],
              widths=[2.4, 4.4, 3.6], first_col_bold=True,
              caption="Sept états et leur déclencheur"),
        code(""".bouton {
  display: inline-flex; align-items: center; gap: .45rem;
  padding: .7rem 1.2rem;
  border: 0; border-radius: 8px;
  background: var(--primaire-700); color: #fff;
  font: inherit; font-weight: 600;
  cursor: pointer;
  transition: background-color .18s ease, transform .18s ease;
}
.bouton:hover { background: var(--primaire-500); }
.bouton:active { transform: translateY(1px); }
.bouton:focus-visible { outline: 3px solid var(--accent); outline-offset: 3px; }
.bouton[disabled] { opacity: .55; cursor: not-allowed; }
.bouton[aria-busy="true"] { cursor: progress; }""", "css", "Un bouton complet"),
        box("attention", "Un bouton désactivé n'explique rien",
            "Préférez un bouton actif qui affiche un message d'erreur au clic, ou un "
            "texte expliquant pourquoi l'action est indisponible. Un bouton grisé sans "
            "explication laisse l'utilisateur sans recours."),

        h(2, "Variantes et modificateurs"),
        p("Une variante change une caractéristique d'un composant existant. Elle se "
          "nomme par son intention : `--principal`, `--discret`, `--danger`."),
        code(""".bouton--discret {
  background: transparent;
  color: var(--primaire-700);
  border: 1px solid var(--neutre-300);
}
.bouton--danger { background: var(--alerte); }
.bouton--petit { padding: .4rem .8rem; font-size: .875rem; }
.bouton--large { width: 100%; justify-content: center; }""", "css",
             "Quatre variantes, aucune duplication de structure"),
        p("Les tailles se combinent avec les variantes : `.bouton.bouton--danger.bouton--petit` "
          "reste cohérent parce que chaque classe ne touche qu'une dimension."),

        h(2, "Cartes et contenu"),
        p("Une carte regroupe un contenu autonome : article, produit, événement. Elle "
          "doit rester compréhensible hors contexte et ne pas dépendre d'une image pour "
          "être identifiée."),
        code("""<article class="carte">
  <img class="carte__image" src="images/atelier.webp" alt="" width="800" height="450">
  <div class="carte__corps">
    <p class="carte__etiquette">Atelier</p>
    <h2 class="carte__titre"><a href="/ateliers/html">HTML accessible</a></h2>
    <p class="carte__resume">Structurer une page pour tous les lecteurs.</p>
    <p class="carte__meta"><time datetime="2026-11-12">12 novembre</time> · 3 h</p>
  </div>
</article>""", "html", "Une carte dont le titre porte le lien"),
        p("Le lien est posé sur le titre, non sur toute la carte : cela donne un nom "
          "explicite au lien et permet de sélectionner le texte. Si vous rendez la "
          "carte entièrement cliquable, utilisez un pseudo-élément qui étend la zone "
          "sans masquer le contenu."),
        code(""".carte { position: relative; }
.carte__titre a::after {
  content: "";
  position: absolute;
  inset: 0;
}""", "css", "Étendre la zone cliquable sans masquer le texte"),
        p("L'image est décorative dans cet exemple : elle est déjà décrite par le "
          "titre, d'où l'attribut `alt` vide. Si elle apporte une information, elle "
          "doit être décrite."),

        h(2, "Alertes et messages"),
        p("Une alerte communique un état du système : succès, information, "
          "avertissement, erreur. Elle doit être annoncée par les lecteurs d'écran et "
          "rester visible sans être envahissante."),
        code("""<div class="alerte alerte--erreur" role="alert">
  <svg aria-hidden="true" class="alerte__icone">…</svg>
  <div>
    <p class="alerte__titre">Le paiement a échoué</p>
    <p>Votre carte a été refusée. Vérifiez les informations ou essayez un autre
       moyen de paiement.</p>
  </div>
</div>""", "html", "Une alerte structurée et annoncée"),
        table(["Rôle", "Attribut", "Usage"],
              [["Information", "`role=\"status\"`", "Message non urgent"],
               ["Succès", "`role=\"status\"`", "Confirmation d'action"],
               ["Erreur", "`role=\"alert\"`", "Interruption immédiate"],
               ["Avertissement", "`role=\"status\"` + icône", "Risque à venir"]],
              widths=[3.0, 3.6, 4.4], first_col_bold=True,
              caption="Quatre niveaux d'alerte et leur annonce"),
        code(""".alerte {
  display: flex;
  gap: .75rem;
  padding: 1rem;
  border-radius: 8px;
  border-inline-start: 4px solid;
}
.alerte--erreur { background: #f7ecea; border-color: #a63a32; color: #5c1f1a; }
.alerte--succes { background: #eaf3ee; border-color: #2f7d5b; color: #17432f; }
.alerte__titre { margin: 0 0 .25rem; font-weight: 700; }""", "css",
             "Une alerte lisible, avec un titre et un corps"),

        h(2, "Organiser une bibliothèque"),
        p("Une bibliothèque de composants documente ce qui existe pour éviter les "
          "réinventions. Trois éléments y figurent toujours : l'usage prévu, les "
          "exemples et les limites."),
        code("""/* ==========================================================================
   Bouton
   Usage : action ponctuelle. Jamais pour un lien de navigation.
   Variantes : --principal, --discret, --danger
   Tailles : --petit, (défaut), --large
   États : hover, focus-visible, active, disabled, aria-busy
   ========================================================================== */""", "css", "Une documentation intégrée au fichier"),
        code("""<!-- page composants.html : la bibliothèque vivante -->
<section id="boutons">
  <h2>Boutons</h2>
  <p><button class="bouton">Principal</button>
     <button class="bouton bouton--discret">Discret</button>
     <button class="bouton bouton--danger">Danger</button>
     <button class="bouton" disabled>Désactivé</button></p>
</section>""", "html", "Une page de démonstration versionnée avec le projet"),
        box("methode", "Un composant n'entre dans la bibliothèque que s'il est vérifié",
            items=["Il a été testé au clavier.",
                   "Il tient sur un écran de 320 pixels.",
                   "Il fonctionne en mode sombre.",
                   "Il ne dépend pas d'une image pour être compris.",
                   "Son code tient en moins de trente lignes."]),
    ],
    "keypoints": [
        "Un composant est un rôle réutilisable, pas une apparence.",
        "Sept états au minimum pour un élément interactif.",
        "Un bouton désactivé sans explication laisse l'utilisateur sans recours.",
        "Les variantes se nomment par intention, pas par couleur.",
        "Un composant doit rester compréhensible hors contexte.",
        "Les alertes portent un rôle ARIA adapté à leur niveau.",
        "Une bibliothèque documentée évite la réinvention.",
    ],
    "bridge": "Les composants sont en place. Le chapitre suivant leur donne du "
              "mouvement : transitions, animations et respect des préférences.",
    "exercises": [
        ex("Compléter une carte",
           "Une carte d'article n'a ni étiquette, ni date accessible, ni lien nommé.",
           ["Ajoutez une étiquette de catégorie.",
            "Balisez la date avec `time` et `datetime`.",
            "Donnez un nom explicite au lien du titre."],
           [("code", """<article class="carte">
  <img class="carte__image" src="images/css-grid.webp" alt="" width="800" height="450">
  <div class="carte__corps">
    <p class="carte__etiquette"><a href="/css">CSS</a></p>
    <h2 class="carte__titre"><a href="/articles/css-grid">Comprendre CSS Grid en pratique</a></h2>
    <p class="carte__resume">Sept exemples commentés pour remplacer les mises en page fragiles.</p>
    <p class="carte__meta">
      Publié le <time datetime="2026-11-12">12 novembre 2026</time>
    </p>
  </div>
</article>"""),
            "La date lisible peut différer de la valeur machine (`2026-11-12`) : "
            "l'attribut `datetime` fournit la forme normalisée.",
            "Le libellé du lien est le titre de l'article : il reste compréhensible "
            "lorsqu'il est extrait de la page et listé par un lecteur d'écran."]),
        ex("Concevoir une alerte de formulaire",
           "Le formulaire renvoie trois erreurs de champs. Concevez le message.",
           ["Le message est-il annoncé immédiatement ?",
            "Chaque erreur renvoie-t-elle au champ concerné ?",
            "Les données saisies sont-elles conservées ?"],
           [("code", """<div class="alerte alerte--erreur" role="alert" tabindex="-1">
  <h2 class="alerte__titre">3 champs nécessitent votre attention</h2>
  <ul>
    <li><a href="#email">L'adresse électronique est incomplète.</a></li>
    <li><a href="#mdp">Le mot de passe doit contenir au moins 12 caractères.</a></li>
    <li><a href="#cgv">Vous devez accepter les conditions.</a></li>
  </ul>
</div>"""),
            "`role=\"alert\"` déclenche une annonce immédiate. Le `tabindex=\"-1\"` "
            "permet de déplacer le focus sur le message après l'envoi.",
            "Chaque erreur est un lien vers le champ concerné : l'utilisateur corrige "
            "sans chercher. Les valeurs déjà saisies restent affichées pour éviter la "
            "double saisie."],
           level="Accessibilité"),
        ex("Auditer une bibliothèque",
           "Listez les composants de votre projet et vérifiez leur documentation.",
           ["Repérez les composants dupliqués.",
            "Vérifiez les états de chacun.",
            "Documentez trois composants manquants."],
           ["Les doublons typiques : deux styles de bouton secondaire, deux sortes "
            "d'alerte, deux cartes légèrement différentes. Fusionner réduit le code et "
            "les incohérences.",
            "Un composant sans état `focus-visible` ni `disabled` n'est pas prêt pour "
            "la production, même s'il est joli en démonstration.",
            "La documentation minimale tient en trois lignes par composant : rôle, "
            "variantes, accessible ou non au clavier."],
           level="Analyse"),
    ],
    "quiz": [
        quiz("Quel attribut ARIA pour une erreur qui doit être annoncée immédiatement ?",
             ["`role=\"status\"`", "`role=\"alert\"`", "`aria-live=\"off\"`", "`role=\"log\"`"],
             1,
             "`role=\"alert\"` correspond à `aria-live=\"assertive\"` : l'annonce "
             "interrompt le lecteur d'écran."),
        quiz("Quelle affirmation décrit une variante de composant ?",
             ["Un composant différent", "Une modification d'un composant existant par une classe",
              "Une duplication du HTML", "Un composant réservé au mobile"],
             1,
             "La variante modifie une dimension du composant (taille, intention) sans "
             "en changer le rôle."),
        quiz("Que doit faire un bouton désactivé pour rester compréhensible ?",
             ["Rien, il est grisé", "Expliquer pourquoi il est indisponible", "Disparaître", "Changer de couleur"],
             1,
             "Sans explication, l'utilisateur ne comprend pas ce qui manque pour "
             "activer l'action."),
        quiz("Où placer le lien d'une carte pour un nom accessible explicite ?",
             ["Sur toute la carte via un `div`", "Sur le titre", "Sur l'image", "Nulle part"],
             1,
             "Le lien sur le titre donne un nom explicite ; on peut étendre la zone "
             "cliquable avec un pseudo-élément."),
        quiz("Combien d'états minimum pour un bouton de qualité ?",
             ["Deux", "Trois", "Cinq (normal, survol, focus, actif, désactivé)", "Un"],
             2,
             "Les cinq états couvrent les usages souris, clavier et les indisponibilités."),
    ],
}
