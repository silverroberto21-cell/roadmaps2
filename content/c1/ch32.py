from bookkit.dsl import (box, code, defn, ex, fig, h, ol, p, quiz, table, ul)

CH = {
    "title": "Déboguer et tester",
    "subtitle": "Trouver la cause d'un défaut au lieu de deviner, puis empêcher son "
                "retour par des tests.",
    "duration": "3 h 00",
    "level": "Intermédiaire",
    "prereq": "chapitre 31",
    "objectives": [
        "Utiliser méthodiquement les outils de développement.",
        "Poser un point d'arrêt et inspecter l'état d'exécution.",
        "Lire une trace d'appels et interpréter les messages d'erreur.",
        "Écrire des tests unitaires et des tests de composant.",
        "Choisir ce qui mérite d'être testé.",
    ],
    "blocks": [
        h(2, "Une méthode, pas de l'intuition"),
        p("Déboguer consiste à réduire l'écart entre ce que le code fait et ce que "
          "l'on croit qu'il fait. La démarche est toujours la même : reproduire, "
          "isoler, comprendre, corriger, vérifier."),
        fig("flow", "Les cinq étapes du débogage",
            ["1. Reproduire de façon fiable",
             "2. Réduire le périmètre",
             "3. Observer l'état réel",
             "4. Corriger la cause",
             "5. Vérifier et prévenir le retour"],
            height=245),
        table(["Étape", "Question", "Outil"],
              [["Reproduire", "Dans quelles conditions ?", "Console, journal"],
               ["Isoler", "Quelle ligne ?", "Points d'arrêt"],
               ["Observer", "Quelles valeurs ?", "Panneau Sources"],
               ["Corriger", "Quelle cause racine ?", "Analyse du code"],
               ["Vérifier", "Le défaut est-il clos ?", "Test de régression"]],
              widths=[3.0, 4.8, 4.0], first_col_bold=True,
              caption="Cinq étapes et leurs outils"),
        box("attention", "Le piège de la correction au hasard",
            "Ajouter une condition jusqu'à ce que le symptôme disparaisse produit du "
            "code incompréhensible. Si vous ne pouvez pas expliquer *pourquoi* la "
            "correction fonctionne, vous n'avez pas trouvé la cause."),

        h(2, "La console et ses messages"),
        p("Le message d'une erreur contient trois informations : le type, le message "
          "et la pile d'appels. La pile se lit de haut en bas : la première ligne est "
          "l'endroit où l'erreur est survenue."),
        code("""TypeError: Cannot read properties of null (reading 'value')
    at validerFormulaire (app.js:42:18)
    at HTMLFormElement.<anonymous> (app.js:67:3)""", "text",
             "Une erreur typique, avec sa pile"),
        table(["Type", "Cause fréquente"],
              [["`ReferenceError`", "Variable non déclarée ou hors portée"],
               ["`TypeError`", "Appel sur `undefined` ou `null`"],
               ["`SyntaxError`", "Erreur de frappe, souvent un `}` manquant"],
               ["`RangeError`", "Récursion infinie ou index hors bornes"],
               ["`DOMException`", "API utilisée dans un contexte invalide"]],
              widths=[4.0, 8.0], first_col_bold=True,
              caption="Cinq familles d'erreurs et leur cause"),
        code("""// Localiser l'erreur au lieu de la masquer
console.error("Valeur de champ :", champ, "Formulaire :", formulaire);

// Grouper des mesures
console.group("Validation");
console.log("valeur", champ.value);
console.log("valide", champ.checkValidity());
console.groupEnd();""", "js", "Des traces utiles, pas un déluge"),

        h(2, "Points d'arrêt"),
        p("Un point d'arrêt suspend l'exécution à une ligne précise. On peut alors "
          "inspecter les variables, avancer pas à pas, entrer dans une fonction ou "
          "évaluer une expression."),
        table(["Action", "Raccourci usuel", "Effet"],
              [["Point d'arrêt", "Clic sur le numéro de ligne", "Suspend à cette ligne"],
               ["Reprendre", "F8", "Continue jusqu'au prochain arrêt"],
               ["Pas à pas", "F10", "Exécute la ligne suivante"],
               ["Entrer", "F11", "Entre dans la fonction appelée"],
               ["Sortir", "Maj+F11", "Termine la fonction courante"],
               ["Désactiver", "Ctrl+F8", "Ignore tous les arrêts"]],
              widths=[3.2, 3.6, 5.0], first_col_bold=True,
              caption="Six commandes de débogage"),
        code("""function calculerTotal(lignes) {
  debugger;                 // suspend ici si les outils sont ouverts
  return lignes.reduce((t, l) => t + l.prix * l.quantite, 0);
}""", "js", "Un point d'arrêt conditionnel minuscule"),
        p("Le point d'arrêt conditionnel s'active uniquement quand une expression est "
          "vraie, par exemple `lignes.length > 100`. Il évite de cliquer sur "
          "« Reprendre » pendant vingt minutes sur une boucle."),
        box("pratique", "Reproduire en isolation",
            "Si un défaut n'apparaît que dans une page complexe, extrayez la fonction "
            "fautive dans un fichier réduit avec les mêmes entrées. Le défaut qui "
            "persiste est alors beaucoup plus facile à localiser."),

        h(2, "Tests unitaires"),
        p("Un test unitaire vérifie une fonction isolée, avec une entrée connue et un "
          "résultat attendu. Il protège contre les régressions et documente le "
          "comportement attendu."),
        code("""// fonction testée
export function formaterPrix(centimes, devise = "EUR") {
  const valeur = (centimes / 100).toFixed(2).replace(".", ",");
  return `${valeur} ${devise}`;
}

// test
import { test, expect } from "vitest";

test("formate un prix en euros", () => {
  expect(formaterPrix(1234)).toBe("12,34 EUR");
});

test("accepte une autre devise", () => {
  expect(formaterPrix(500, "USD")).toBe("5,00 USD");
});

test("gère zéro", () => {
  expect(formaterPrix(0)).toBe("0,00 EUR");
});""", "js", "Trois cas, trois assertions"),
        table(["Niveau", "Portée", "Coût", "Rapidité"],
              [["Unitaire", "Une fonction", "Faible", "Millisecondes"],
               ["Composant", "Un composant rendu", "Moyen", "Millisecondes"],
               ["Intégration", "Plusieurs modules", "Moyen", "Secondes"],
               ["Bout en bout", "Parcours complet", "Élevé", "Minutes"],
               ["Manuel", "Vérification humaine", "Variable", "Minutes"]],
              widths=[3.0, 3.8, 3.0, 3.2], first_col_bold=True,
              caption="Cinq niveaux de test"),
        code("""// Un test de composant avec Testing Library
import { render, screen } from "@testing-library/dom";
import userEvent from "@testing-library/user-event";

test("le panneau s'ouvre au clic", async () => {
  document.body.innerHTML = `
    <button aria-expanded="false">Menu</button>
    <ul hidden><li>Accueil</li></ul>`;

  const bouton = screen.getByRole("button", { name: "Menu" });
  await userEvent.click(bouton);

  expect(bouton).toHaveAttribute("aria-expanded", "true");
  expect(screen.getByRole("list")).toBeVisible();
});""", "js", "Un test qui vérifie aussi l'accessibilité"),

        h(2, "Ce qui mérite un test"),
        p("Tester tout coûte cher et fige le code. Testez les décisions, les calculs, "
          "les cas limites et les parcours critiques."),
        table(["À tester", "Pourquoi", "Exemple"],
              [["Calculs", "Erreurs silencieuses", "Total, remise, TVA"],
               ["Cas limites", "Sources de bogues", "Vide, zéro, très long"],
               ["Parcours critique", "Impact commercial", "Paiement, connexion"],
               ["Correction de bogue", "Non-régression", "Test ajouté après un défaut"],
               ["Rendu conditionnel", "Cohérence", "État vide, erreur"]],
              widths=[3.2, 4.2, 4.4], first_col_bold=True,
              caption="Cinq priorités de test"),
        code("""// Couvrir les cas limites
test.each([
  [[], 0],
  [[{ prix: 10, quantite: 1 }], 10],
  [[{ prix: 10, quantite: 0 }], 0],
])("total de %j", (lignes, attendu) => {
  expect(calculerTotal(lignes)).toBe(attendu);
});""", "js", "Un test paramétré couvre plusieurs cas"),
        defn("Régression", "Défaut réapparu dans une version antérieurement correcte. "
                           "Un test de régression reproduit le défaut pour garantir "
                           "qu'il ne revient pas."),
        box("retenir", "Un test rouge vaut mieux qu'un test absent",
            "Un test qui échoue signale un problème réel. Un test qui passe sans rien "
            "vérifier donne une fausse assurance. Une assertion doit pouvoir échouer."),

        h(2, "Outillage minimal"),
        p("Un exécuteur de tests suffit pour commencer. Vitest ou Jest pour le code, "
          "Testing Library pour le DOM, et Playwright ou Cypress pour les parcours.")
        ,
        code("""# Installation et exécution
npm install -D vitest @testing-library/dom
npx vitest            # mode interactif
npx vitest run        # une seule exécution, intégration continue
npx vitest --coverage # rapport de couverture""", "bash",
             "Trois commandes pour démarrer"),
        p("La couverture indique le pourcentage de lignes exécutées par les tests. Ce "
          "n'est pas un objectif en soi : 100 % de couverture n'empêche pas un bogue "
          "de logique."),
        box("methode", "Après chaque bogue corrigé",
            items=["Écrire un test qui reproduit le défaut.",
                   "Vérifier qu'il échoue avant la correction.",
                   "Corriger.",
                   "Vérifier qu'il passe."]),
    ],
    "keypoints": [
        "Déboguer suit une méthode : reproduire, isoler, observer, corriger, vérifier.",
        "La pile d'appels indique l'origine exacte de l'erreur.",
        "Un point d'arrêt conditionnel cible un cas précis.",
        "Un test unitaire vérifie une fonction isolée.",
        "Les cas limites révèlent les bogues les plus fréquents.",
        "Chaque bogue corrigé mérite un test de régression.",
        "La couverture mesure l'exécution, pas la qualité.",
    ],
    "bridge": "Le code fonctionne et reste correct. Reste à savoir s'il est rapide : "
              "le chapitre suivant mesure et optimise les performances.",
    "exercises": [
        ex("Localiser un `TypeError`",
           "`Cannot read properties of null (reading 'value')` à la ligne 42.",
           ["Identifiez la variable nulle.",
            "Déterminez pourquoi la sélection échoue.",
            "Proposez une correction robuste."],
           [("code", """// Cause probable : le script s'exécute avant que l'élément existe
// ou le sélecteur ne correspond à rien

const champ = document.querySelector("#courriel");
if (!champ) {
  console.warn("Champ #courriel absent : le script ne s'applique pas à cette page.");
} else {
  champ.addEventListener("input", valider);
}"""),
            "`querySelector` renvoie `null` si aucun élément ne correspond ; appeler "
            "`.value` sur `null` produit l'erreur.",
            "Un script chargé sans `defer` s'exécute avant que le corps du document ne "
            "soit analysé : c'est la cause la plus fréquente."]),
        ex("Écrire trois tests utiles",
           "Testez une fonction de remise progressive.",
           ["Cas sans remise.",
            "Cas à la limite du seuil.",
            "Cas avec valeur invalide."],
           [("code", """export function remise(total) {
  if (!Number.isFinite(total) || total < 0) return 0;
  if (total >= 100) return total * 0.9;
  if (total >= 50) return total * 0.95;
  return total;
}

// tests
test("aucune remise sous 50", () => expect(remise(49.99)).toBe(49.99));
test("remise de 5 % à 50", () => expect(remise(50)).toBe(47.5));
test("remise de 10 % à 100", () => expect(remise(100)).toBe(90));
test("valeur invalide", () => expect(remise(-5)).toBe(0));"""),
            "Les seuils sont les endroits où les erreurs de comparaison (`<` contre "
            "`<=`) se produisent.",
            "Le cas invalide évite qu'une entrée inattendue propage `NaN` dans tout le "
            "calcul."]),
        ex("Reproduire un bogue en isolation",
           "Un total affiché est faux uniquement pour certaines commandes.",
           ["Extrayez la fonction de calcul.",
            "Testez avec les données réelles.",
            "Comparez avec le résultat attendu à la main."],
           [("code", """// Reproduction minimale
const lignes = [
  { prix: 19.99, quantite: 3 },
  { prix: 5.5, quantite: 2 },
];

const total = lignes.reduce((t, l) => t + l.prix * l.quantite, 0);
console.log(total);        // 70.97 (virgule flottante : 70.97000000000001)

// Correction : calculer en centimes
const totalCentimes = lignes.reduce(
  (t, l) => t + Math.round(l.prix * 100) * l.quantite, 0
);
console.log(totalCentimes / 100);   // 70.97"""),
            "L'addition de flottants binaires produit des décimales parasites, "
            "invisibles à l'affichage mais sensibles aux comparaisons.",
            "Calculer en centiers entiers supprime le problème à la racine."],
           level="Diagnostic"),
    ],
    "quiz": [
        quiz("Par où commence un débogage méthodique ?",
             ["Changer le code", "Reproduire le défaut de façon fiable",
              "Redémarrer le serveur", "Ajouter des `console.log` partout"],
             1,
             "Sans reproduction fiable, aucune correction ne peut être vérifiée."),
        quiz("Que contient une pile d'appels ?",
             ["Les variables", "La suite des fonctions appelées",
              "Les erreurs précédentes", "Le code source complet"],
             1,
             "Elle indique le chemin d'appel jusqu'à l'erreur, du plus récent au plus "
             "ancien."),
        quiz("À quoi sert un test de régression ?",
             ["À mesurer la vitesse", "À empêcher le retour d'un défaut corrigé",
              "À documenter l'API", "À remplacer les tests unitaires"],
             1,
             "Il reproduit le défaut d'origine pour garantir qu'il ne réapparaît pas."),
        quiz("Que mesure la couverture de code ?",
             ["La qualité du code", "Les lignes exécutées par les tests",
              "Le nombre de bogues", "La vitesse d'exécution"],
             1,
             "C'est un indicateur d'exécution, pas une preuve d'absence de défaut."),
        quiz("Quel point d'arrêt choisir dans une boucle de mille itérations ?",
             ["Un point normal", "Un point conditionnel",
              "Aucun", "Un `console.log`"],
             1,
             "La condition permet de suspendre uniquement sur l'itération "
             "problématique."),
    ],
}
