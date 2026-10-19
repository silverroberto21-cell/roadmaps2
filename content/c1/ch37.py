from bookkit.dsl import (box, code, defn, ex, fig, h, ol, p, quiz, table, ul)

CH = {
    "title": "CSS avancé : couches, `:has()` et requêtes de conteneur",
    "subtitle": "Les fonctionnalités récentes qui remplacent des habitudes anciennes et "
                "simplifient les feuilles de style volumineuses.",
    "duration": "3 h 00",
    "level": "Avancé",
    "prereq": "chapitre 36",
    "objectives": [
        "Organiser une feuille de style avec les couches de cascade.",
        "Écrire des sélecteurs relationnels avec `:has()`.",
        "Adapter un composant à son conteneur, non à l'écran.",
        "Utiliser `subgrid` pour aligner des sous-grilles.",
        "Écrire du CSS imbriqué sans reproduire les erreurs de Sass.",
    ],
    "blocks": [
        h(2, "Le problème des feuilles de style qui vieillissent"),
        p("Après quelques mois, une feuille de style accumule des correctifs : un "
          "`!important` pour passer devant un style antérieur, un sélecteur plus "
          "spécifique pour écraser le précédent, puis un second `!important` pour "
          "repasser devant. La cascade devient une négociation."),
        code("""/* La spirale de la spécificité */
.bouton { background: var(--navy); }
.carte .bouton { background: var(--amber); }
.carte .bouton.principal { background: var(--navy) !important; }
#app .carte .bouton.principal { background: var(--amber) !important; }""",
             "css", "Quatre règles pour une seule décision"),
        p("Les couches de cascade répondent à ce problème sans changer la spécificité "
          "individuelle des sélecteurs : elles établissent un ordre entre des ensembles "
          "de règles."),

        h(2, "Les couches de cascade"),
        p("`@layer` déclare des niveaux d'autorité. La dernière couche déclarée gagne, "
          "quelle que soit la spécificité des sélecteurs à l'intérieur."),
        code("""/* Déclaration de l'ordre : le dernier l'emporte */
@layer reset, base, composants, utilitaires, surcharges;

@layer reset {
  *, *::before, *::after { box-sizing: border-box; }
  body { margin: 0; }
}

@layer base {
  h1, h2, h3 { line-height: 1.15; }
  a { color: var(--lien); }
}

@layer composants {
  .carte { padding: var(--espace-2); border-radius: 8px; }
  .carte a { text-decoration: none; }
}

@layer utilitaires {
  .texte-centre { text-align: center; }
}""", "css", "Quatre couches, un ordre explicite"),
        table(["Couche", "Contenu", "Autorité"],
              [["`reset`", "Normalisation", "La plus faible"],
               ["`base`", "Éléments nus", "Faible"],
               ["`composants`", "Blocs réutilisables", "Moyenne"],
               ["`utilitaires`", "Classes ponctuelles", "Forte"],
               ["`surcharges`", "Exceptions documentées", "La plus forte"]],
              widths=[3.2, 5.2, 3.6], first_col_bold=True,
              caption="Cinq couches et leur autorité"),
        defn("Couche de cascade", "Niveau nommé qui s'insère dans l'ordre de calcul de la "
                                  "cascade, avant la spécificité. Une règle d'une couche "
                                  "supérieure gagne sur toute règle d'une couche "
                                  "inférieure, même moins spécifique."),
        code("""/* Importer une bibliothèque dans une couche dédiée */
@import url("librairie.css") layer(librairie);

/* L'ordre final : librairie < reset < base < composants < utilitaires */
@layer librairie, reset, base, composants, utilitaires;""", "css",
             "Une dépendance contenue dans sa couche"),
        p("Placer une bibliothèque dans une couche de faible autorité permet de la "
          "surcharger avec un simple sélecteur de classe, sans `!important` ni guerre "
          "de spécificité."),
        box("attention", "L'ordre se déclare une fois",
            "Deux déclarations `@layer a, b;` et `@layer b, a;` produisent l'ordre de la "
            "première. Déclarez l'ordre en tête de la feuille principale, avant toute "
            "règle."),

        h(2, "`:has()` : le sélecteur relationnel"),
        p("`:has()` sélectionne un élément selon ce qu'il contient. C'est la réponse CSS "
          "à de nombreux cas qui exigeaient auparavant du JavaScript."),
        code("""/* Une carte contenant une image passe en disposition horizontale */
.carte:has(img) { grid-template-columns: 12rem 1fr; }

/* Un champ suivi d'un message d'erreur visible */
.champ:has(.erreur:not(:empty)) input { border-color: var(--rouge); }

/* Un formulaire dont une case est cochée */
form:has(#consentement:checked) button[type=submit] { opacity: 1; }

/* Une section sans titre est masquée */
section:not(:has(h2)) { display: none; }""", "css", "Quatre usages concrets"),
        table(["Sélecteur", "Question posée", "Exemple"],
              [["`:has(> img)`", "Enfant direct image ?", "Disposition de carte"],
               ["`:has(+ p)`", "Frère suivant ?", "Espacement conditionnel"],
               ["`:has(:checked)`", "Contient un cochage ?", "État de formulaire"],
               ["`:not(:has(h2))`", "Aucun titre ?", "Masquage"],
               ["`:has(.vide)`", "Contient un état vide ?", "Mise en forme"]],
              widths=[3.4, 4.6, 4.0], first_col_bold=True,
              caption="Cinq formes de `:has()`"),
        p("`:has()` s'évalue en remontant depuis la cible : il peut donc coûter cher sur "
          "de très grands documents. Utilisez-le sur des conteneurs de composants, pas "
          "sur `body` avec des sélecteurs profonds."),

        h(2, "Requêtes de conteneur"),
        p("Une media query répond à la taille de la fenêtre. Une requête de conteneur "
          "répond à la taille du parent : un même composant peut être compact dans une "
          "barre latérale et large dans le contenu principal."),
        code("""/* Déclarer le conteneur */
.zone-contenu { container-type: inline-size; container-name: carte; }

/* Adapter selon la largeur du conteneur */
@container carte (min-width: 30rem) {
  .carte { grid-template-columns: 12rem 1fr; }
  .carte__image { height: 100%; }
}

@container carte (max-width: 20rem) {
  .carte__titre { font-size: 1rem; }
}""", "css", "Un composant qui s'adapte à sa place"),
        fig("compare", "Deux façons d'adapter un composant",
            ("MEDIA QUERY", ["Répond à la fenêtre", "Suppose une mise en page",
                             "Composant non réutilisable"],
             "CONTAINER QUERY", ["Répond au parent", "Indépendant du contexte",
                                 "Réutilisable partout"]),
            height=200),
        code("""/* Unités de conteneur */
.carte__titre {
  font-size: clamp(1rem, 4cqi, 1.6rem);   /* cqi = 1 % de la largeur du conteneur */
}

/* Requête sur le style, pas la taille */
@container style(--theme: sombre) {
  .carte { background: #1b2c3d; color: #e8edf1; }
}""", "css", "Unités et requêtes de style"),
        p("Les unités `cqi` et `cqb` remplacent `vw` et `vh` pour un composant : elles "
          "rendent la typographie proportionnelle à son espace réel, sans connaître la "
          "fenêtre."),

        h(2, "`subgrid`"),
        p("Une grille imbriquée peut hériter des pistes de sa grille parente. Sans "
          "`subgrid`, les cartes alignent leurs éléments indépendamment et les titres "
          "ne se répondent pas d'une carte à l'autre."),
        code(""".liste-cartes {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--espace-2);
}

.carte {
  display: grid;
  grid-template-rows: subgrid;   /* hérite des lignes du parent */
  grid-row: span 3;
}""", "css", "Trois cartes aux lignes alignées"),
        p("Le parent doit définir des pistes explicites, et l'enfant doit couvrir "
          "exactement le nombre de lignes héritées. C'est la solution propre pour "
          "aligner des en-têtes, des corps et des pieds de cartes sur plusieurs "
          "colonnes."),

        h(2, "Imbrication native"),
        p("Le CSS permet désormais d'imbriquer des règles avec `&`. La syntaxe évite "
          "deux pièges classiques de Sass : la concaténation de noms et les sélecteurs "
          "implicites."),
        code(""".carte {
  padding: 1rem;

  &__titre { font-size: 1.2rem; }   /* invalide : pas de concaténation */

  & .carte__titre { font-weight: 600; }
  &:hover { border-color: var(--amber); }
  &.est-active { outline: 2px solid var(--navy); }

  .contenu & { margin-block: 0; }  /* contexte externe explicite */
}""", "css", "Imbrication explicite"),
        box("retenir", "L'imbrication ne remplace pas la structure",
            "Imbriquer trois niveaux produit des sélecteurs longs et fragiles. Une "
            "bonne feuille de style reste majoritairement plate, avec des classes "
            "explicites héritées d'une convention de nommage."),
        box("methode", "Adopter une nouveauté CSS",
            items=["Vérifier l'usage réel dans les navigateurs ciblés.",
                   "Prévoir un repli acceptable sans la fonctionnalité.",
                   "Isoler l'essai dans une branche ou derrière un drapeau.",
                   "Mesurer le gain de lisibilité, pas seulement l'effet visuel."]),
    ],
    "keypoints": [
        "`@layer` règle les conflits sans augmenter la spécificité.",
        "L'ordre des couches se déclare une fois, en tête.",
        "`:has()` sélectionne un élément selon son contenu.",
        "Les requêtes de conteneur rendent un composant indépendant de la fenêtre.",
        "`cqi` exprime une taille relative au conteneur.",
        "`subgrid` aligne les éléments de plusieurs cartes.",
        "L'imbrication native ne concatène pas les noms.",
    ],
    "bridge": "Le CSS dispose désormais de tous les outils contemporains. Les deux "
              "chapitres suivants élargissent le propos : composants réutilisables, "
              "puis contenu multilingue.",
    "exercises": [
        ex("Réorganiser une feuille de style en couches",
           "La feuille contient trois `!important` et des sélecteurs à quatre niveaux.",
           ["Déclarez cinq couches.",
            "Placez la réinitialisation, la base, les composants.",
            "Supprimez les `!important`."],
           [("code", """@layer reset, base, composants, utilitaires, surcharges;

@layer reset {
  *, *::before, *::after { box-sizing: border-box; }
  body, h1, h2, p, ul { margin: 0; }
}

@layer base {
  body { font: 1rem/1.6 "Inter", system-ui, sans-serif; }
  a { color: #0f2e4c; }
}

@layer composants {
  .bouton { background: #e0a21b; color: #1f2933; }
  .bouton--secondaire { background: transparent; border: 1px solid currentColor; }
}

@layer utilitaires {
  .mt-2 { margin-block-start: 1rem; }
}"""),
            "Les conflits se règlent par l'ordre des couches, plus par des sélecteurs "
            "toujours plus longs.",
            "Un `!important` résiduel reste possible, mais son emplacement est "
            "identifié : la couche `surcharges`."],
           level="Refactorisation"),
        ex("Carte adaptative sans media query",
           "Une carte doit s'afficher en colonne dans une barre latérale et en ligne "
           "dans le contenu.",
           ["Déclarez le conteneur.",
            "Écrivez deux requêtes de conteneur.",
            "Testez en redimensionnant le conteneur, pas la fenêtre."],
           [("code", """.contenu, .aside { container-type: inline-size; }

.carte { display: grid; gap: 1rem; }

@container (min-width: 28rem) {
  .carte { grid-template-columns: 10rem 1fr; align-items: start; }
}

@container (max-width: 18rem) {
  .carte__titre { font-size: 1rem; }
  .carte__meta { display: none; }
}"""),
            "Le même composant s'adapte à deux contextes sans une seule règle "
            "supplémentaire.",
            "La requête porte sur le parent : renommer les conteneurs (`container-name`) "
            "évite les collisions."]),
        ex("Formulaire piloté par `:has()`",
           "Le bouton d'envoi reste grisé tant que les conditions ne sont pas remplies.",
           ["Cas de consentement obligatoire.",
            "Champ requis vide.",
            "Aucun JavaScript."],
           [("code", """form { }

form button[type=submit] {
  opacity: .55;
  pointer-events: none;
}

form:has(#consentement:checked)
    :has(#courriel:valid):has(#nom:not(:placeholder-shown))
    button[type=submit] {
  opacity: 1;
  pointer-events: auto;
}"""),
            "`:has()` combine trois conditions portant sur des champs différents.",
            "Le serveur doit toujours valider : cette règle améliore l'expérience, elle "
            "ne protège rien."],
           level="CSS"),
    ],
    "quiz": [
        quiz("Que règle `@layer` ?",
             ["La vitesse de rendu", "L'ordre d'autorité entre groupes de règles",
              "La taille des fichiers", "Le chargement des polices"],
             1,
             "La cascade consulte les couches avant la spécificité."),
        quiz("Que sélectionne `:has(img)` ?",
             ["Les images", "Les éléments contenant une image",
              "Les voisins d'une image", "Les parents d'images uniquement"],
             1,
             "C'est un sélecteur relationnel descendant : l'élément qui contient."),
        quiz("À quoi réagit une requête de conteneur ?",
             ["À la largeur de la fenêtre", "À la largeur du parent déclaré",
              "À la résolution de l'écran", "Au zoom"],
             1,
             "Elle s'appuie sur la taille d'un conteneur nommé, pas sur le viewport."),
        quiz("Que fait `grid-template-rows: subgrid` ?",
             ["Crée une nouvelle grille", "Hérite des lignes du parent",
              "Supprime les lignes", "Aligne uniquement le texte"],
             1,
             "L'élément participe aux pistes définies par la grille parente."),
        quiz("L'imbrication CSS permet-elle `&__titre` ?",
             ["Oui", "Non, il n'existe pas de concaténation", "Seulement avec Sass", "Uniquement en SCSS"],
             1,
             "`&` représente le sélecteur parent ; aucune concaténation de chaînes "
             "n'existe en CSS natif."),
    ],
}
