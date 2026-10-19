from bookkit.dsl import (box, code, defn, ex, fig, h, ol, p, quiz, table, ul)

CH = {
    "title": "Introduction à JavaScript",
    "subtitle": "Le langage du navigateur : où l'exécuter, comment l'inclure et ce "
                "qu'il peut — ou ne peut pas — faire.",
    "duration": "2 h 30",
    "level": "Débutant",
    "prereq": "chapitre 23",
    "objectives": [
        "Exécuter du JavaScript dans le navigateur et dans Node.js.",
        "Inclure un script sans bloquer le rendu.",
        "Utiliser la console comme outil de travail.",
        "Comprendre la portée, le mode strict et les modules.",
        "Éviter les pièges de la conversion implicite.",
    ],
    "blocks": [
        h(2, "Où s'exécute JavaScript"),
        p("JavaScript est un langage standardisé (ECMAScript) exécuté par un moteur : "
          "V8 dans Chrome et Node.js, SpiderMonkey dans Firefox, JavaScriptCore dans "
          "Safari. Le langage est le même ; l'environnement diffère."),
        table(["Environnement", "Accès disponible", "Absent"],
              [["Navigateur", "DOM, fenêtre, stockage, réseau", "Système de fichiers direct"],
               ["Node.js", "Fichiers, processus, réseau", "DOM"],
               ["Service worker", "Cache, interception réseau", "DOM"],
               ["Deno / Bun", "Fichiers, réseau, permissions", "DOM"]],
              widths=[2.8, 4.6, 3.6], first_col_bold=True,
              caption="Quatre environnements et leurs capacités"),
        code("""// Dans la console du navigateur
2 + 3                        // 5
"Bonjour" + " " + "Web"      // "Bonjour Web"
document.title               // le titre de la page
localStorage.setItem("a", 1) // stockage local""", "js",
             "Premières manipulations dans la console"),
        p("La console est un espace d'expérimentation : elle exécute n'importe quelle "
          "expression et affiche les erreurs. C'est l'outil le plus utilisé au "
          "quotidien, bien avant le débogueur."),

        h(2, "Inclure un script dans une page"),
        p("Trois emplacements existent, mais un seul est recommandé : un fichier "
          "externe chargé avec `defer` ou déclaré comme module."),
        code("""<!-- Recommandé : différé, ordre préservé -->
<script src="js/app.js" defer></script>

<!-- Recommandé : module, différé par défaut -->
<script type="module" src="js/app.js"></script>

<!-- Déconseillé : bloque l'analyse du document -->
<script src="js/app.js"></script>

<!-- À proscrire : code mêlé au HTML -->
<button onclick="alert('clic')">Cliquer</button>""", "html",
             "Quatre façons de charger du JavaScript"),
        table(["Forme", "Exécution", "Portée", "Usage"],
              [["`<script>`", "Immédiate, bloquante", "Globale", "Particularités"],
               ["`<script defer>`", "Après l'analyse", "Globale", "Sites classiques"],
               ["`<script type=module>`", "Après l'analyse", "Module", "Code moderne"],
               ["`import` dynamique", "À la demande", "Module", "Chargement différé"]],
              widths=[3.2, 3.8, 2.6, 3.4], first_col_bold=True,
              caption="Quatre formes de chargement et leur portée"),
        p("Un module possède sa propre portée : les variables ne polluent pas l'objet "
          "global, et `import`/`export` structurent le code. C'est le mode à privilégier "
          "dès qu'un script dépasse quelques lignes."),
        code("""// js/math.js
export function additionner(a, b) { return a + b; }
export const PI = 3.14159;

// js/app.js
import { additionner, PI } from "./math.js";
console.log(additionner(2, 3), PI);""", "js", "Deux modules qui communiquent"),

        h(2, "La console, un outil de travail"),
        p("`console.log` n'est que la pointe de l'outil. Cinq méthodes couvrent des "
          "besoins distincts, et `console.table` transforme un tableau d'objets en "
          "tableau lisible."),
        code("""console.log("Valeur :", 42);
console.warn("Ceci est un avertissement");
console.error("Ceci est une erreur");
console.table([
  { nom: "Ada", annee: 1815 },
  { nom: "Grace", annee: 1906 },
]);
console.time("boucle");
for (let i = 0; i < 100000; i++) {}
console.timeEnd("boucle");   // boucle: 1.2ms""", "js", "Cinq méthodes de console"),
        box("pratique", "Déboguer sans `console.log`",
            "Un point d'arrêt dans le panneau Sources permet d'inspecter les variables "
            "à un instant précis, de rejouer une fonction et de suivre la pile "
            "d'appels. C'est plus efficace qu'une succession d'affichages."),

        h(2, "Variables et portée"),
        p("`let` et `const` remplacent `var` depuis 2015. `const` empêche la "
          "réaffectation de la liaison, pas la modification de l'objet référencé."),
        code("""const nom = "Ada";          // liaison constante
let compteur = 0;          // liaison réaffectable
compteur += 1;             // OK

const personne = { nom: "Ada" };
personne.nom = "Grace";   // OK : l'objet est modifié
// personne = {};         // Erreur : la liaison est constante

// var : portée de fonction, hissage — à éviter
if (true) { var x = 1; }
console.log(x);            // 1

// let : portée de bloc
if (true) { let y = 1; }
// console.log(y);         // ReferenceError""", "js",
             "`let`, `const`, `var` : trois comportements différents"),
        defn("Hissage (hoisting)", "Mécanisme qui remonte les déclarations en tête de "
                                   "leur portée. `var` est hissé et vaut `undefined` "
                                   "avant son affectation ; `let` et `const` sont dans "
                                   "une zone morte temporelle."),
        p("Règle pratique : `const` par défaut, `let` seulement si la valeur doit "
          "changer, `var` jamais dans du code neuf."),

        h(2, "Types et conversions"),
        p("JavaScript possède sept types primitifs et un type objet. La conversion "
          "implicite est la première source de bogues subtils."),
        table(["Type", "Exemple", "Piège"],
              [["`string`", "`\"texte\"`", "Concaténation avec `+`"],
               ["`number`", "`42`, `3.14`, `NaN`", "`0.1 + 0.2 !== 0.3`"],
               ["`bigint`", "`42n`", "Pas de mélange avec `number`"],
               ["`boolean`", "`true`, `false`", "Valeurs « fausses » nombreuses"],
               ["`null`", "`null`", "`typeof null === \"object\"`"],
               ["`undefined`", "`undefined`", "Différent de `null`"],
               ["`symbol`", "`Symbol()`", "Clés uniques"]],
              widths=[2.2, 4.2, 4.6], first_col_bold=True,
              caption="Sept types primitifs et leurs pièges"),
        code(""""5" + 3        // "53"   (concaténation)
"5" - 3        // 2      (soustraction numérique)
Number("5")    // 5
parseInt("42px", 10)  // 42
Number("42px") // NaN

Boolean("")    // false
Boolean("0")   // true  (chaîne non vide)
Boolean(0)     // false

0.1 + 0.2 === 0.3              // false
Math.abs(0.1 + 0.2 - 0.3) < 1e-9  // true""", "js",
             "Les conversions qui surprennent"),
        p("Utilisez `===` plutôt que `==` : l'égalité stricte évite les conversions "
          "implicites. `null == undefined` est le seul cas où `==` reste parfois "
          "toléré, et `??` couvre désormais ce besoin."),
        code("""const valeur = null;
const resultat = valeur ?? "défaut";   // "défaut" (null et undefined)
const autre = 0 || "défaut";           // "défaut" (0 est falsy) — piège
const juste = 0 ?? "défaut";           // 0""", "js",
             "`??` ne se déclenche que pour `null` et `undefined`"),

        h(2, "Mode strict"),
        p("`\"use strict\"` active un mode d'exécution plus rigoureux : variables non "
          "déclarées interdites, `this` non défini, affectations silencieuses "
          "transformées en erreurs. Les modules sont stricts par défaut."),
        code(""""use strict";

// Sans strict : crée une variable globale par accident
// avec strict : ReferenceError
fonctionInconnue = 10;""", "js", "Une erreur détectée tôt plutôt qu'un bogue tardif"),
        box("methode", "Trois réflexes de départ",
            items=["`const` par défaut, `let` si nécessaire.",
                   "`===` plutôt que `==`.",
                   "Un fichier par responsabilité, chargé en module."]),
    ],
    "keypoints": [
        "JavaScript s'exécute dans le navigateur, Node.js ou un service worker.",
        "`defer` et les modules évitent de bloquer l'analyse du document.",
        "Un module possède sa propre portée et s'organise en import/export.",
        "`const` empêche la réaffectation, pas la modification d'un objet.",
        "`let` et `const` ont une portée de bloc ; `var` non.",
        "Les conversions implicites produisent des bogues difficiles à voir.",
        "`===` et `??` remplacent `==` et `||` dans la plupart des cas.",
    ],
    "bridge": "Le langage est installé. Le chapitre suivant en explore les briques "
              "fondamentales : fonctions, tableaux et objets.",
    "exercises": [
        ex("Prédire des conversions",
           "Donnez le résultat de chaque expression, puis vérifiez dans la console.",
           ["`\"10\" + 5`", "`\"10\" - 5`", "`Number(\"3.5px\")`", "`Boolean([])`", "`[] + {}`"],
           ["`\"105\"` : le `+` privilégie la concaténation dès qu'une chaîne est "
            "présente.",
            "`5` : la soustraction force la conversion numérique.",
            "`NaN` : `Number` exige une chaîne entièrement numérique ; `parseFloat` "
            "aurait renvoyé 3.5.",
            "`true` : un tableau, même vide, est un objet donc vrai. `Boolean([])` est "
            "un piège classique.",
            "`\"[object Object]\"` : les deux opérandes sont convertis en chaînes puis "
            "concaténés."]),
        ex("Corriger un script global",
           "Ce script pollue l'espace global et échoue silencieusement.",
           ["`nom = \"Ada\"; function init(){ titre = nom; }`",
            "`var total = 0; for (var i=0;i<3;i++){ total += i; }`",
            "`if (total == \"3\") { init(); }`"],
           [("code", """"use strict";

const nom = "Ada";
let total = 0;
for (let i = 0; i < 3; i += 1) total += i;

function init() {
  const titre = nom;      // variable locale
  return titre;
}

if (total === 3) init();"""),
            "En mode strict, l'affectation à une variable non déclarée lève une "
            "erreur : le bogue devient visible immédiatement.",
            "`let i` limite la portée de la boucle, `===` évite la conversion de "
            "chaîne en nombre."]),
        ex("Créer un module",
           "Séparez le calcul et l'affichage dans deux modules.",
           ["Exportez une fonction de calcul.",
            "Importez-la dans le module principal.",
            "Vérifiez dans la console."],
           [("code", """// js/calcul.js
export function moyenne(notes) {
  if (!notes.length) return 0;
  return notes.reduce((a, b) => a + b, 0) / notes.length;
}

// js/app.js
import { moyenne } from "./calcul.js";
console.log(moyenne([12, 15, 9]));   // 12"""),
            "Le module de calcul ne dépend d'aucun élément de la page : il est "
            "testable isolément.",
            "L'import doit comporter l'extension `.js` dans le navigateur, contrairement "
            "à certains outils de construction."]),
    ],
    "quiz": [
        quiz("Quelle écriture charge un script sans bloquer l'analyse du document ?",
             ["`<script src=\"app.js\">`", "`<script defer src=\"app.js\">`",
              "`<script async src=\"app.js\">` et `defer` conviennent"] if False else
             ["`<script src=\"app.js\">`", "`<script defer src=\"app.js\">`",
              "`<script src=\"app.js\" blocking>`", "`<script nowait>`"],
             1,
             "`defer` télécharge en parallèle et exécute après l'analyse, dans l'ordre "
             "de déclaration."),
        quiz("Que signifie `const` ?",
             ["La valeur est immuable", "La liaison ne peut pas être réaffectée",
              "L'objet est gelé", "La variable est globale"],
             1,
             "`const` empêche la réaffectation de la liaison ; l'objet référencé reste "
             "modifiable (sauf `Object.freeze`)."),
        quiz("Quel opérateur évite les conversions implicites ?",
             ["`==`", "`===`", "`=`", "`!=`"],
             1,
             "L'égalité stricte compare sans convertir les types."),
        quiz("Que renvoie `Boolean([])` ?",
             ["`false`", "`true`", "`undefined`", "Une erreur"],
             1,
             "Un tableau vide est un objet, donc vrai en contexte booléen — un piège "
             "classique."),
        quiz("Quel est l'intérêt d'un module ?",
             ["Il s'exécute plus vite", "Il isole la portée et structure les dépendances",
              "Il remplace le HTML", "Il évite le CSS"],
             1,
             "Chaque module a sa portée et déclare ses exports, ce qui évite les "
             "collisions de variables globales."),
    ],
}
