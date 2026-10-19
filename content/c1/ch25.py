from bookkit.dsl import (box, code, defn, ex, fig, h, ol, p, quiz, table, ul)

CH = {
    "title": "Fonctions, tableaux et objets",
    "subtitle": "Les trois structures qui composent tout programme JavaScript, et les "
                "méthodes qui évitent les boucles inutiles.",
    "duration": "3 h 00",
    "level": "Intermédiaire",
    "prereq": "chapitre 24",
    "objectives": [
        "Écrire des fonctions claires, avec paramètres par défaut.",
        "Maîtriser les méthodes de tableau qui transforment des données.",
        "Structurer des objets et utiliser la déstructuration.",
        "Comprendre `this` et les différences entre fonction et flèche.",
        "Éviter les mutations involontaires.",
    ],
    "blocks": [
        h(2, "Fonctions : déclaration, expression, flèche"),
        p("Une fonction regroupe des instructions, reçoit des paramètres et renvoie une "
          "valeur. Trois syntaxes coexistent ; elles ne diffèrent pas seulement par "
          "l'apparence."),
        code("""// Déclaration : hissée, utilisable avant sa définition
function additionner(a, b) { return a + b; }

// Expression : affectée à une variable
const multiplier = function (a, b) { return a * b; };

// Flèche : syntaxe concise, pas de `this` propre
const diviser = (a, b) => a / b;
const carre = x => x * x;
const creer = () => ({ actif: true });   // parenthèses obligatoires pour un objet""",
             "js", "Trois syntaxes de fonction"),
        table(["Forme", "`this`", "Hissage", "Usage"],
              [["Déclaration", "Dynamique", "Oui", "Fonctions principales"],
               ["Expression", "Dynamique", "Non", "Callbacks nommés"],
               ["Flèche", "Celui du parent", "Non", "Callbacks courts"]],
              widths=[3.0, 3.4, 2.6, 4.0], first_col_bold=True,
              caption="Trois formes de fonction et leurs différences"),
        code("""function normaliser(texte, separateur = "-", bas = true) {
  const t = texte.trim().replace(/\\s+/g, separateur);
  return bas ? t.toLowerCase() : t;
}

normaliser("  Bonjour le Monde  ");          // "bonjour-le-monde"
normaliser("Salut", "_", false);             // "Salut"
normaliser("Test", undefined, true);         // "test\"""", "js",
             "Paramètres par défaut et chaînage de méthodes"),
        defn("Fonction pure", "Fonction dont le résultat ne dépend que de ses "
                              "paramètres, sans effet de bord. Elle est plus facile à "
                              "tester et à raisonner."),

        h(2, "Tableaux : transformer plutôt que boucler"),
        p("Les méthodes de tableau remplacent la plupart des boucles `for`. Elles "
          "expriment l'intention : filtrer, transformer, réduire, trier, chercher."),
        table(["Méthode", "Effet", "Retour"],
              [["`map`", "Transforme chaque élément", "Nouveau tableau de même taille"],
               ["`filter`", "Conserve ceux qui passent un test", "Nouveau tableau"],
               ["`reduce`", "Agrège en une valeur", "Valeur unique"],
               ["`find`", "Premier élément correspondant", "Élément ou `undefined`"],
               ["`some` / `every`", "Au moins un / tous", "Booléen"],
               ["`sort`", "Trie en place", "Tableau trié (mutation)"],
               ["`toSorted`", "Trie sans muter", "Nouveau tableau"],
               ["`flat`", "Aplati un niveau", "Nouveau tableau"],
               ["`includes`", "Contient une valeur", "Booléen"]],
              widths=[2.6, 4.6, 3.8], first_col_bold=True,
              caption="Neuf méthodes de tableau"),
        code("""const stagiaires = [
  { nom: "Ada", note: 18, present: true },
  { nom: "Grace", note: 15, present: false },
  { nom: "Linus", note: 12, present: true },
];

const noms = stagiaires.map(s => s.nom);
const admis = stagiaires.filter(s => s.note >= 15);
const moyenne = stagiaires.reduce((total, s) => total + s.note, 0) / stagiaires.length;
const tousPresents = stagiaires.every(s => s.present);
const premier = stagiaires.find(s => s.nom === "Grace");

const tries = stagiaires.toSorted((a, b) => b.note - a.note);""", "js",
             "Six opérations courantes sans une seule boucle"),
        box("attention", "`sort` modifie le tableau",
            "`sort` trie en place et renvoie le même tableau. Utilisez `toSorted` pour "
            "obtenir une copie, ou `[...tableau].sort(...)` si le support est ancien."),
        p("Le chaînage `filter(...).map(...)` est lisible tant qu'il reste court. "
          "Au-delà de trois étapes, extrayez des fonctions nommées : le code se lit "
          "alors comme une phrase."),
        code("""const resultat = commandes
  .filter(c => c.statut === "payee")
  .flatMap(c => c.lignes)
  .filter(l => l.quantite > 0)
  .reduce((total, l) => total + l.prix * l.quantite, 0);""", "js",
             "Un chaînage qui reste lisible"),

        h(2, "Objets et déstructuration"),
        p("Un objet associe des clés à des valeurs. La déstructuration extrait "
          "plusieurs valeurs en une ligne, avec des valeurs par défaut et des "
          "renommages."),
        code("""const article = {
  titre: "CSS Grid",
  auteur: { nom: "Ada", role: "éditrice" },
  tags: ["css", "mise en page"],
  publie: true,
};

const { titre, tags, publie = false } = article;
const { auteur: { nom } } = article;
const { titre: intitule } = article;

const nouvelArticle = {
  ...article,
  tags: [...article.tags, "reference"],   // copie superficielle
  publie: false,
};""", "js", "Déstructurer et copier sans muter"),
        table(["Opération", "Écriture", "Remarque"],
              [["Accès", "`article.titre`", "`undefined` si absent"],
               ["Accès sûr", "`article?.auteur?.nom`", "Chaînage optionnel"],
               ["Valeur par défaut", "`const { x = 1 } = obj`", "Seulement si `undefined`"],
               ["Copie", "`{ ...obj }`", "Superficielle"],
               ["Fusion", "`{ ...a, ...b }`", "`b` écrase `a`"],
               ["Clé dynamique", "`{ [cle]: valeur }`", "Calcul à l'exécution"]],
              widths=[2.8, 4.4, 3.6], first_col_bold=True,
              caption="Six opérations sur les objets"),

        h(2, "`this` et fonctions fléchées"),
        p("`this` désigne le contexte d'appel. Dans une méthode d'objet, c'est l'objet. "
          "Dans une fonction fléchée, c'est le `this` du contexte englobant — ce qui "
          "explique pourquoi une flèche ne convient pas comme méthode."),
        code("""const compteur = {
  valeur: 0,
  incrementer() {
    this.valeur += 1;          // this = compteur
  },
  // incrementerFleche: () => { this.valeur += 1 }, // this = contexte externe
};

const bouton = document.querySelector("button");
bouton.addEventListener("click", () => {
  this;   // dans une flèche, `this` n'est pas le bouton
});""", "js", "Deux contextes, deux comportements"),
        p("Dans la pratique moderne, les flèches servent aux callbacks et les méthodes "
          "aux objets. Confondre les deux produit des `undefined` difficiles à "
          "diagnostiquer."),

        h(2, "Immutabilité et effets de bord"),
        p("Une fonction qui modifie son argument surprend celui qui l'appelle. "
          "Préférez les fonctions qui renvoient une nouvelle valeur."),
        code("""// Mutation : l'appelant est surpris
function ajouterTag(tags, tag) {
  tags.push(tag);
  return tags;
}

// Sans mutation
function avecTag(tags, tag) {
  return [...tags, tag];
}

const base = ["css"];
const enrichi = avecTag(base, "html");
base;      // ["css"]
enrichi;   // ["css", "html"]""", "js", "Deux styles, deux conséquences"),
        box("retenir", "Copie superficielle n'est pas copie profonde",
            "`{ ...objet }` copie le premier niveau. Les objets imbriqués restent "
            "partagés : modifier `copie.auteur.nom` modifie aussi l'original. Pour une "
            "copie profonde, utilisez `structuredClone(objet)`."),
        code("""const original = { a: { b: 1 } };
const copie = structuredClone(original);
copie.a.b = 2;
original.a.b;   // 1""", "js", "Une copie réellement indépendante"),
        box("methode", "Trois questions avant d'écrire une boucle",
            items=["Puis-je exprimer l'intention avec `map`, `filter` ou `reduce` ?",
                   "Ma fonction modifie-t-elle son argument ?",
                   "Ai-je besoin de `this` dans ce callback ?"]),
    ],
    "keypoints": [
        "Déclaration, expression et flèche n'ont pas le même comportement.",
        "Les paramètres par défaut clarifient les signatures.",
        "`map`, `filter` et `reduce` remplacent la plupart des boucles.",
        "`sort` mute le tableau ; `toSorted` non.",
        "La déstructuration extrait plusieurs valeurs en une ligne.",
        "Une fonction fléchée ne possède pas son propre `this`.",
        "`structuredClone` réalise une copie profonde.",
    ],
    "bridge": "Les données se transforment. Il reste à les afficher : le chapitre "
              "suivant manipule le DOM.",
    "exercises": [
        ex("Transformer une liste d'élèves",
           "À partir d'un tableau d'objets `{nom, notes: []}`, calculez la moyenne de "
           "chacun et triez par moyenne décroissante.",
           ["Utilisez `map` puis `toSorted`.",
            "Ajoutez une mention selon la moyenne.",
            "Formatez le résultat en tableau HTML (sans le construire encore)."],
           [("code", """const eleves = [
  { nom: "Ada", notes: [16, 18, 15] },
  { nom: "Grace", notes: [12, 14, 11] },
  { nom: "Linus", notes: [9, 11, 13] },
];

const resultats = eleves
  .map(({ nom, notes }) => {
    const moyenne = notes.reduce((a, b) => a + b, 0) / notes.length;
    const mention = moyenne >= 16 ? "Très bien" : moyenne >= 14 ? "Bien" : "Passable";
    return { nom, moyenne: Math.round(moyenne * 10) / 10, mention };
  })
  .toSorted((a, b) => b.moyenne - a.moyenne);"""),
            "`toSorted` évite de modifier le tableau d'origine, ce qui rend la fonction "
            "prévisible.",
            "L'arrondi à une décimale évite les valeurs du type 14,666666 dans "
            "l'affichage."]),
        ex("Corriger une mutation involontaire",
           "Cette fonction modifie la configuration globale.",
           ["`function activer(config) { config.actif = true; return config; }`",
            "`const config = { actif: false, options: { theme: \"clair\" } }`"],
           [("code", """function activer(config) {
  return { ...config, actif: true };
}

const config = { actif: false, options: { theme: "clair" } };
const nouvelle = activer(config);
// config.actif === false
// nouvelle.actif === true"""),
            "La copie superficielle suffit ici car `actif` est une valeur primitive.",
            "Si l'on modifiait `options.theme`, il faudrait `structuredClone` ou une "
            "copie explicite du sous-objet."]),
        ex("Refactoriser une boucle",
           "Remplacez cette boucle par des méthodes de tableau.",
           ["`const noms = []; for (const u of users) { if (u.actif) noms.push(u.nom) }`",
            "`let total = 0; for (const c of commandes) { total += c.prix }`",
            "`const premier = users[0]` après un tri"],
           [("code", """const noms = users.filter(u => u.actif).map(u => u.nom);
const total = commandes.reduce((somme, c) => somme + c.prix, 0);
const premier = users.toSorted((a, b) => a.nom.localeCompare(b.nom))[0];"""),
            "Chaque méthode exprime une intention : filtrer, agréger, trier.",
            "`localeCompare` trie correctement les accents, contrairement à une "
            "comparaison `<` qui dépend des codes de caractères."],
           level="Refactorisation"),
    ],
    "quiz": [
        quiz("Quelle méthode transforme chaque élément d'un tableau ?",
             ["`filter`", "`map`", "`reduce`", "`find`"],
             1,
             "`map` renvoie un nouveau tableau de même longueur après transformation."),
        quiz("Quelle méthode agrège un tableau en une seule valeur ?",
             ["`map`", "`filter`", "`reduce`", "`some`"],
             2,
             "`reduce` applique un accumulateur à chaque élément et renvoie la valeur "
             "finale."),
        quiz("Que vaut `this` dans une fonction fléchée ?",
             ["L'objet appelant", "Le `this` du contexte englobant", "`window` toujours", "`undefined` toujours"],
             1,
             "Une flèche n'a pas de `this` propre : elle capture celui de la portée "
             "où elle est définie."),
        quiz("Quelle méthode trie sans modifier le tableau d'origine ?",
             ["`sort`", "`toSorted`", "`reverse`", "`splice`"],
             1,
             "`toSorted` renvoie une copie triée ; `sort` trie en place."),
        quiz("Que fait `structuredClone` ?",
             ["Une copie superficielle", "Une copie profonde", "Une sérialisation JSON", "Un tri"],
             1,
             "Il clone récursivement les objets imbriqués, contrairement au spread."),
    ],
}
