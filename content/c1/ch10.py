from bookkit.dsl import (box, code, defn, ex, fig, h, ol, p, quiz, table, ul)

CH = {
    "title": "Sélecteurs, variables et unités",
    "subtitle": "Écrire peu de CSS pour obtenir beaucoup : les outils qui rendent une "
                "feuille de style maintenable.",
    "duration": "2 h 45",
    "level": "Débutant",
    "prereq": "chapitre 9",
    "objectives": [
        "Utiliser les pseudo-classes et pseudo-éléments à bon escient.",
        "Structurer une feuille de style avec des variables CSS.",
        "Choisir la bonne unité de mesure selon le contexte.",
        "Créer des sélecteurs robustes et faciles à faire évoluer.",
        "Éviter les pièges de spécificité et de performance des sélecteurs.",
    ],
    "blocks": [
        h(2, "Pseudo-classes : décrire un état"),
        p("Une pseudo-classe cible un élément dans un état particulier : survolé, "
          "focalisé, coché, premier enfant, vide. Elle évite d'ajouter des classes "
          "que le JavaScript devrait maintenir."),
        table(["Pseudo-classe", "Cible", "Usage typique"],
              [["`:hover`", "Élément survolé", "Boutons, liens"],
               ["`:focus`", "Élément focalisé", "Champs, liens"],
               ["`:focus-visible`", "Focus visible au clavier", "Accessibilité"],
               ["`:active`", "Pendant l'appui", "Retour tactile"],
               ["`:visited`", "Lien déjà visité", "Navigation"],
               ["`:disabled`", "Champ désactivé", "Formulaires"],
               ["`:checked`", "Case ou radio cochée", "Styles personnalisés"],
               ["`:invalid`", "Champ invalide", "Signalement d'erreur"],
               ["`:placeholder-shown`", "Placeholder affiché", "Étiquette flottante"],
               ["`:first-child`", "Premier enfant", "Listes, tableaux"],
               ["`:nth-child(2n)`", "Enfants pairs", "Lignes alternées"],
               ["`:not(...)`", "Tout sauf", "Exceptions"],
               ["`:has(...)`", "Parent contenant", "Mise en page conditionnelle"]],
              widths=[3.2, 4.2, 3.2], first_col_bold=True,
              caption="Treize pseudo-classes parmi les plus utiles"),
        code("""a:hover { text-decoration-thickness: 2px; }
a:focus-visible {
  outline: 3px solid #e0a21b;
  outline-offset: 3px;
}
button:disabled { opacity: .5; cursor: not-allowed; }
tr:nth-child(even) { background: #f4f7f9; }
input:not(:placeholder-shown) + label { transform: translateY(-1.2rem); }""",
             "css", "Des états exprimés sans une seule classe supplémentaire"),
        box("attention", "Ne jamais supprimer le focus",
            "`outline: none` sans remplacement prive les utilisateurs au clavier de "
            "tout repère. Si le contour natif vous déplaît, remplacez-le par un "
            "`box-shadow` ou un `outline` personnalisé visible sur tous les fonds."),
        h(3, "`:has()`, le sélecteur de parent"),
        p("Longtemps impossible en CSS, `:has()` permet de styler un conteneur selon "
          "son contenu. Il est pris en charge par les navigateurs modernes depuis "
          "2023 environ."),
        code("""/* Une carte qui contient une image reçoit un autre rembourrage */
.carte:has(img) { padding-top: 0; }

/* Un formulaire contenant un champ invalide affiche un message */
form:has(input:invalid) .message-erreur { display: block; }

/* Une section sans titre reste sans marge */
section:not(:has(h2)) { margin-block: 0; }""", "css", "Trois usages de `:has()`"),

        h(2, "Pseudo-éléments : créer sans ajouter de balise"),
        p("Un pseudo-élément crée une partie d'élément qui n'existe pas dans le HTML. "
          "Il sert à la décoration, jamais à porter du contenu essentiel : ce contenu "
          "serait invisible pour une partie des outils."),
        table(["Pseudo-élément", "Cible", "Usage"],
              [["`::before`", "Contenu avant", "Icône décorative"],
               ["`::after`", "Contenu après", "Flèche, séparateur"],
               ["`::first-line`", "Première ligne", "Lettrine"],
               ["`::first-letter`", "Première lettre", "Lettrine"],
               ["`::selection`", "Texte sélectionné", "Couleur de surlignage"],
               ["`::placeholder`", "Texte indicatif", "Nuance de gris"],
               ["`::marker`", "Puce ou numéro", "Listes personnalisées"],
               ["`::backdrop`", "Arrière-plan de dialogue", "Modales"]],
              widths=[3.0, 4.0, 3.6], first_col_bold=True,
              caption="Huit pseudo-éléments et leur usage légitime"),
        code(""".titre-externe::after {
  content: " ↗";
  font-size: .8em;
}

.liste-propre { list-style: none; }
.liste-propre li::before {
  content: "";
  display: inline-block;
  width: .5rem; height: .5rem;
  margin-right: .6rem;
  border-radius: 50%;
  background: #e0a21b;
}""", "css", "Décoration générée par CSS"),
        p("`content` n'accepte que du texte ou une URL d'image, jamais du HTML. Un "
          "texte inséré par `content` peut être lu par certains lecteurs d'écran mais "
          "n'est ni sélectionnable ni traduisible : réservez-le à la décoration."),

        h(2, "Variables CSS : une source unique de vérité"),
        p("Une variable, appelée **propriété personnalisée**, se déclare avec deux "
          "tirets et se lit avec `var()`. Elle se propage par héritage : déclarée sur "
          "`:root`, elle est disponible partout."),
        code(""":root {
  --couleur-primaire: #0f2e4c;
  --couleur-accent: #e0a21b;
  --couleur-texte: #1f2933;
  --couleur-fond: #ffffff;
  --espace-xs: .5rem;
  --espace-s: 1rem;
  --espace-m: 2rem;
  --rayon: 6px;
  --ombre: 0 4px 12px rgb(15 46 76 / 12%);
  --police-titre: "Arial", system-ui, sans-serif;
}

.bouton {
  background: var(--couleur-primaire);
  color: var(--couleur-fond);
  padding: var(--espace-xs) var(--espace-s);
  border-radius: var(--rayon);
  box-shadow: var(--ombre);
}""", "css", "Un jeu de jetons de conception"),
        code("""/* Thème sombre : seules les variables changent */
@media (prefers-color-scheme: dark) {
  :root {
    --couleur-texte: #e8edf1;
    --couleur-fond: #101820;
    --couleur-primaire: #8fb6d9;
  }
}

/* Variante locale d'un composant */
.carte--alerte { --couleur-primaire: #a63a32; }""", "css",
             "Un thème sombre en dix lignes, sans dupliquer les règles"),
        p("Les variables acceptent une valeur de repli : `var(--couleur, #000)`. Elles "
          "peuvent aussi être modifiées par JavaScript (`element.style.setProperty`), "
          "ce qui permet des animations pilotées par le thème."),
        box("retenir", "Nommer les variables par leur rôle",
            "`--couleur-primaire` est meilleur que `--bleu-fonce` : le jour où la "
            "marque change de couleur, le nom reste juste. Nommez par fonction, pas "
            "par apparence."),

        h(2, "Unités : choisir la bonne échelle"),
        p("CSS propose une dizaine d'unités. Trois familles suffisent à structurer un "
          "projet : les unités relatives à la police, celles relatives à la fenêtre, "
          "et les unités fixes."),
        table(["Unité", "Référence", "Usage recommandé"],
              [["`px`", "Pixel CSS", "Bordures, ombres, traits"],
               ["`rem`", "Taille de police racine", "Typographie, espacements"],
               ["`em`", "Taille de police de l'élément", "Composant autonome"],
               ["`%`", "Élément parent", "Largeurs fluides"],
               ["`ch`", "Largeur du caractère 0", "Largeur de lecture"],
               ["`vw` / `vh`", "Fenêtre", "Bandeaux pleine page, à limiter"],
               ["`dvh`", "Fenêtre dynamique mobile", "Pleine hauteur fiable"],
               ["`fr`", "Fraction d'espace libre", "Grilles"],
               ["`lh`", "Hauteur de ligne", "Rythme vertical"]],
              widths=[2.2, 4.2, 4.2], first_col_bold=True,
              caption="Neuf unités et leur domaine"),
        code("""html { font-size: 100%; }        /* respecte la préférence */
body { font-size: 1.0625rem; }    /* 17 px par défaut */
h1   { font-size: 2.25rem; }      /* 38 px */
p    { max-width: 65ch; }         /* 65 caractères par ligne */
.carte { padding: 1.5rem; }       /* suit la taille racine */""", "css",
             "Une échelle typographique en `rem` et une largeur en `ch`"),
        p("La largeur en `ch` est la plus fidèle au confort de lecture : elle dépend "
          "de la police réellement utilisée et s'adapte si l'utilisateur change la "
          "taille de son texte."),
        box("attention", "Les pièges des unités de fenêtre",
            "`100vh` dépasse la hauteur visible sur mobile, à cause des barres "
            "d'interface. Utilisez `100dvh` (dynamic viewport height) ou "
            "`min-height: 100svh`. Et n'utilisez jamais `vw` pour la typographie sans "
            "`clamp()` : le texte deviendrait illisible sur écran étroit."),

        h(2, "Construire des sélecteurs robustes"),
        p("Un sélecteur robuste reste valide quand le HTML évolue. Il ne dépend ni de "
          "l'ordre des éléments, ni de la profondeur de l'arbre, ni d'un identifiant "
          "unique."),
        code("""/* Fragile : dépend de la structure */
div.contenu > div > div > p { ... }

/* Robuste : dépend du rôle */
.article__resume { ... }

/* Fragile : identifiant utilisé comme style */
#principal .bouton { ... }

/* Robuste : classe de composant */
.bouton--principal { ... }""", "css", "Deux sélecteurs fragiles, deux sélecteurs robustes"),
        p("La convention BEM (bloc, élément, modificateur) n'est qu'une des "
          "possibilités, mais elle illustre le principe : nommer par rôle, éviter les "
          "descriptions de position (`colonne-gauche`), préférer les classes aux "
          "identifiants."),
        code(""".carte { }
.carte__titre { }
.carte__image { }
.carte--mise-en-avant { }
.carte--compacte { }""", "css", "Une nomenclature qui se lit comme une arborescence"),
        p("Les sélecteurs très profonds coûtent plus cher au navigateur, mais le coût "
          "reste négligeable comparé au chargement des images. La vraie raison "
          "d'éviter `div > div > div` est la maintenabilité, pas la performance."),
        box("methode", "Trois questions avant d'écrire un sélecteur",
            items=["Puis-je le nommer par un rôle plutôt que par une position ?",
                   "Que se passera-t-il si un élément est ajouté ou déplacé ?",
                   "Ai-je besoin d'un identifiant, ou une classe suffit-elle ?"]),
    ],
    "keypoints": [
        "Les pseudo-classes évitent des classes d'état maintenues en JavaScript.",
        "Le focus doit rester visible : c'est une exigence d'accessibilité.",
        "Les pseudo-éléments décorent ; ils ne portent pas de contenu essentiel.",
        "Les variables CSS centralisent les décisions visuelles et permettent le thème.",
        "`rem` pour la typographie, `ch` pour la largeur de lecture, `px` pour les traits.",
        "Un sélecteur robuste survit aux modifications du HTML.",
        "Nommer par rôle, jamais par apparence ni par position.",
    ],
    "bridge": "Les règles sont structurées. Le chapitre suivant s'attaque au cœur de "
              "la lisibilité : la typographie.",
    "exercises": [
        ex("Créer un jeu de variables",
           "Créez un fichier `variables.css` définissant la palette et l'échelle "
           "typographique du cours.",
           ["Définissez six couleurs, quatre espacements et trois rayons.",
            "Ajoutez un thème sombre via `prefers-color-scheme`.",
            "Utilisez ces variables dans un composant bouton."],
           [("code", """:root {
  --couleur-primaire: #0f2e4c;
  --couleur-accent: #e0a21b;
  --couleur-texte: #1f2933;
  --couleur-fond: #ffffff;
  --couleur-bordure: #d5dee6;
  --couleur-erreur: #a63a32;
  --espace-1: .5rem;
  --espace-2: 1rem;
  --espace-3: 2rem;
  --espace-4: 3rem;
  --rayon-s: 4px;
  --rayon-m: 8px;
  --rayon-pilule: 999px;
}

@media (prefers-color-scheme: dark) {
  :root {
    --couleur-texte: #e8edf1;
    --couleur-fond: #0d1620;
    --couleur-primaire: #9dc2e4;
    --couleur-bordure: #2a3b4c;
  }
}

.bouton {
  padding: var(--espace-1) var(--espace-3);
  border-radius: var(--rayon-pilule);
  background: var(--couleur-primaire);
  color: var(--couleur-fond);
}"""),
            "Le thème sombre ne redéfinit que les variables : aucune règle de composant "
            "n'est dupliquée, donc aucun risque de divergence.",
            "Pour un contrôle manuel du thème, remplacez la media query par "
            "`[data-theme=\"dark\"]` sur l'élément `html` et basculez l'attribut en "
            "JavaScript."]),
        ex("Réécrire des sélecteurs fragiles",
           "Réécrivez ces sélecteurs pour les rendre robustes.",
           ["`div#contenu > div > p.intro`",
            "`ul li a:hover`",
            "`.colonne-gauche .boite .titre`"],
           ["Un composant nommé (`.intro` ou `.article__resume`) suffit ; "
            "l'identifiant et la profondeur sont inutiles.",
            "`a:hover` dans un contexte de liste est acceptable, mais mieux vaut "
            "`.menu a:hover` ou `.lien:hover` si le style doit être limité.",
            "`.boite__titre` remplace la chaîne de trois sélecteurs et reste valide "
            "quel que soit l'emplacement de la boîte."],
           level="Refactorisation"),
        ex("Construire une carte avec pseudo-éléments",
           "Créez une carte d'article dont l'icône de lien externe et la puce sont "
           "générées en CSS.",
           ["Ajoutez `::after` sur le titre pour la flèche.",
            "Remplacez les puces par des ronds ambre.",
            "Vérifiez que le contenu reste compréhensible si le CSS est désactivé."],
           [("code", """.carte__lien::after {
  content: " \\2197";
  margin-left: .35rem;
  font-size: .9em;
}
.carte__liste { list-style: none; padding-left: 0; }
.carte__liste li { position: relative; padding-left: 1.1rem; }
.carte__liste li::before {
  content: "";
  position: absolute;
  left: 0; top: .55em;
  width: .45rem; height: .45rem;
  border-radius: 50%;
  background: var(--couleur-accent);
}"""),
            "La flèche est décorative : elle est générée en CSS et n'apparaît pas "
            "dans le texte lu par les lecteurs d'écran.",
            "Sans CSS, la liste reste une liste à puces standard et le contenu "
            "demeure intégralement lisible : c'est le test de la décoration "
            "non essentielle."],
           level="Application"),
    ],
    "quiz": [
        quiz("Quelle pseudo-classe indique qu'un élément est focalisé au clavier ?",
             ["`:hover`", "`:active`", "`:focus-visible`", "`:target`"],
             2,
             "`:focus-visible` distingue le focus clavier du focus souris, ce qui "
             "permet de n'afficher le contour que lorsqu'il est utile."),
        quiz("Comment déclare-t-on une variable CSS ?",
             ["`$couleur: red;`", "`@couleur: red;`", "`--couleur: red;`", "`var couleur = red;`"],
             2,
             "Les propriétés personnalisées commencent par deux tirets et se lisent "
             "avec `var(--couleur)`."),
        quiz("Quelle unité est la plus adaptée à une largeur de lecture confortable ?",
             ["`px`", "`ch`", "`vw`", "`pt`"],
             1,
             "`ch` correspond à la largeur du caractère 0 dans la police utilisée, "
             "ce qui donne une mesure fidèle du nombre de caractères par ligne."),
        quiz("Que fait `var(--couleur, #000)` si la variable n'existe pas ?",
             ["Une erreur de rendu", "Elle applique `#000`", "Elle hérite du parent", "Elle ignore la déclaration"],
             1,
             "Le second argument est la valeur de repli utilisée lorsque la variable "
             "n'est pas définie."),
        quiz("Pourquoi éviter `div > div > div p` ?",
             ["Le navigateur ne le comprend pas",
              "Le sélecteur casse dès que la structure change",
              "Il est moins spécifique que `p`",
              "Il empêche l'héritage"],
             1,
             "Un sélecteur dépendant de la profondeur devient faux au moindre "
             "changement de structure ; un nom de rôle est plus durable."),
    ],
}
