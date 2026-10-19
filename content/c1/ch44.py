from bookkit.dsl import (box, code, defn, ex, fig, h, ol, p, quiz, table, ul)

CH = {
    "title": "Tester une interface : unité, intégration et bout en bout",
    "subtitle": "Écrire des tests qui échouent quand l'interface casse, et qui ne "
                "cassent pas quand elle évolue.",
    "duration": "3 h 15",
    "level": "Intermédiaire",
    "prereq": "chapitre 32",
    "objectives": [
        "Choisir le niveau de test adapté.",
        "Écrire un test unitaire utile.",
        "Tester un composant par son interface visible.",
        "Automatiser un parcours dans un navigateur.",
        "Éviter les tests fragiles.",
    ],
    "blocks": [
        h(2, "Trois niveaux"),
        p("Un test unitaire vérifie une fonction isolée ; un test d'intégration vérifie "
          "plusieurs unités ensemble ; un test de bout en bout traverse l'application dans "
          "un vrai navigateur. Le coût croît avec le niveau, la confiance aussi."),
        table(["Niveau", "Portée", "Vitesse", "Fragilité"],
              [["Unitaire", "Une fonction, un module", "Millisecondes", "Faible"],
               ["Intégration", "Composant et ses voisins", "Dizaines de ms", "Moyenne"],
               ["Bout en bout", "Parcours utilisateur complet", "Secondes", "Élevée"],
               ["Visuel", "Rendu comparé à une référence", "Secondes", "Très élevée"]],
              widths=[4.0, 4.6, 4.2, 4.2], first_col_bold=True,
              caption="Quatre niveaux"),
        defn("Pyramide des tests", "Répartition recommandée : beaucoup de tests unitaires, "
                                   "moins d'intégration, peu de bout en bout. Les tests "
                                   "lents et fragiles restent rares, mais couvrent les "
                                   "parcours critiques."),
        fig("stack", "Une répartition saine",
            ["Tests de bout en bout : parcours critiques",
             "Tests d'intégration : composants et API",
             "Tests unitaires : logique pure",
             "Base large, sommet étroit",
             "Un test de bout en bout remplace dix tests unitaires fragiles",
             "Un test unitaire ne remplace jamais un parcours critique"],
            height=250),
        code("""# Trois commandes, trois niveaux
npx vitest run                     # unitaires
npx vitest run --coverage          # avec couverture
npx playwright test                # bout en bout""", "bash", "Trois exécutions"),

        h(2, "Test unitaire"),
        p("Un bon test unitaire est court, déterministe et vérifie un comportement. Il "
          "n'utilise ni réseau, ni horloge réelle, ni base de données."),
        code("""// formater.js
export function formaterPrix(centimes, devise = "EUR") {
  if (!Number.isInteger(centimes) || centimes < 0) {
    throw new RangeError("montant invalide");
  }
  return new Intl.NumberFormat("fr-FR", {
    style: "currency", currency: devise,
  }).format(centimes / 100);
}

// formater.test.js
import { describe, it, expect } from "vitest";
import { formaterPrix } from "./formater.js";

describe("formaterPrix", () => {
  it("formate un montant en euros", () => {
    expect(formaterPrix(1234)).toBe("12,34 €");
  });

  it("formate une devise étrangère", () => {
    expect(formaterPrix(1234, "USD")).toContain("12,34");
  });

  it("refuse un montant négatif", () => {
    expect(() => formaterPrix(-1)).toThrow(RangeError);
  });
});""", "js", "Trois tests utiles"),
        table(["Bon test", "Mauvais test"],
              [["Vérifie un comportement", "Vérifie l'implémentation"],
               ["Un cas, une assertion claire", "Vingt assertions enchaînées"],
               ["Déterministe", "Dépend de l'heure ou du réseau"],
               ["Nomme le cas testé", "« fonctionne »"],
               ["Rapide", "Attend une seconde sans raison"]],
              widths=[6.0, 6.0], first_col_bold=True,
              caption="Deux colonnes"),
        box("attention", "Un test qui vérifie l'implémentation bloque le refactoring",
            "Si un test échoue à chaque changement interne sans modifier le comportement "
            "observable, il mesure la forme du code, pas son effet. Testez l'entrée et la "
            "sortie."),

        h(2, "Test d'interface"),
        p("Un composant se teste par ce que l'utilisateur voit : un rôle, un libellé, un "
          "texte. Chercher une classe CSS rend le test dépendant du style."),
        code("""import { render, screen } from "@testing-library/dom";
import userEvent from "@testing-library/user-event";
import { Panier } from "./panier.js";

it("ajoute un article et met à jour le total", async () => {
  render(Panier({ articles: [{ nom: "Livre", prix: 1200 }] }));

  await userEvent.click(screen.getByRole("button", { name: /ajouter/i }));

  expect(screen.getByText(/1 article/i)).toBeTruthy();
  expect(screen.getByText("12,00 €")).toBeTruthy();
});

it("signale un panier vide", () => {
  render(Panier({ articles: [] }));
  expect(screen.getByRole("status").textContent).toMatch(/panier vide/i);
});""", "js", "Deux tests par l'interface"),
        table(["Sélecteur", "Robustesse", "Usage"],
              [["Rôle + nom accessible", "Élevée", "Recommandé"],
               ["Libellé de champ", "Élevée", "Formulaires"],
               ["Texte visible", "Moyenne", "Contenu"],
               ["`data-testid`", "Moyenne", "Dernier recours"],
               ["Classe CSS", "Faible", "À éviter"]],
              widths=[4.8, 4.0, 5.2], first_col_bold=True,
              caption="Cinq sélecteurs"),
        code("""<!-- Un composant accessible est aussi plus facile à tester -->
<form>
  <label for="courriel">Adresse électronique</label>
  <input id="courriel" name="courriel" type="email" required
         aria-describedby="aide-courriel">
  <p id="aide-courriel">Nous ne partageons jamais votre adresse.</p>
  <button type="submit">S'inscrire</button>
</form>""", "html", "Un formulaire testable"),
        box("pratique", "L'accessibilité rend les tests plus simples",
            "Un bouton sans nom accessible est introuvable par rôle et libellé. Corriger "
            "l'accessibilité corrige souvent les difficultés de test."),

        h(2, "Bout en bout"),
        p("Un test de bout en bout traverse un vrai navigateur. Il couvre les parcours "
          "critiques : inscription, connexion, achat, paiement. Chaque parcours ajouté "
          "coûte en maintenance."),
        code("""// parcours.spec.js
import { test, expect } from "@playwright/test";

test("un visiteur peut rechercher puis ouvrir une fiche", async ({ page }) => {
  await page.goto("/");
  await page.getByRole("searchbox", { name: /rechercher/i }).fill("livre");
  await page.getByRole("button", { name: /lancer la recherche/i }).click();

  await expect(page.getByRole("heading", { name: /résultats/i })).toBeVisible();
  await page.getByRole("link", { name: /livre de cuisine/i }).click();

  await expect(page.getByRole("heading", { level: 1 })).toContainText("livre de cuisine");
  await expect(page.getByText(/en stock/i)).toBeVisible();
});""", "js", "Un parcours critique"),
        code("""// playwright.config.js
export default {
  use: {
    baseURL: "http://localhost:4173",
    trace: "on-first-retry",
    screenshot: "only-on-failure",
  },
  retries: process.env.CI ? 2 : 0,
  reporter: [["list"], ["html", { open: "never" }]],
};""", "js", "Une configuration prudente"),
        table(["Symptôme", "Cause", "Correction"],
              [["Test qui échoue au hasard", "Attente fixe (`sleep`)", "Attendre un état visible"],
               ["Test long", "Parcours trop large", "Découper en scénarios"],
               ["Sélecteur cassé", "Classe CSS", "Rôle et libellé"],
               ["Échec uniquement en CI", "Fenêtre trop petite", "Viewport explicite"],
               ["Capture inutilisable", "Aucune trace", "Activer la trace"]],
              widths=[4.6, 4.6, 4.8], first_col_bold=True,
              caption="Cinq symptômes"),
        box("attention", "Les réessais masquent l'instabilité",
            "Deux réessais automatiques sauvent un pipeline, mais un test qui échoue une "
            "fois sur cinq reste un test cassé. Corrigez la cause, ne l'ignorez pas."),
        defn("Trace", "Enregistrement détaillé d'une exécution de test : captures, réseau, "
                      "console. Elle permet de diagnostiquer un échec sans le reproduire."),

        h(2, "Couverture et discipline"),
        p("La couverture indique les lignes exécutées, pas les comportements vérifiés. Une "
          "couverture de 90 % peut coexister avec un calcul faux non testé."),
        code("""# Couverture ciblée : uniquement le code applicatif
npx vitest run --coverage \\
  --coverage.include='src/**' \\
  --coverage.exclude='**/*.test.js' \\
  --coverage.thresholds.lines=70""", "bash", "Une couverture honnête"),
        table(["Pratique", "Effet", "Piège"],
              [["Un test par défaut corrigé", "Non-régression", "Test trop précis"],
               ["Données de test explicites", "Lisibilité", "Duplication"],
               ["Horloge injectée", "Déterminisme", "Oubli dans un test"],
               ["Réseau simulé", "Rapidité", "Réalisme réduit"],
               ["Test de parcours unique", "Confiance", "Lenteur"]],
              widths=[4.8, 4.6, 4.6], first_col_bold=True,
              caption="Cinq pratiques"),
        box("methode", "Écrire des tests utiles",
            items=["Commencer par le comportement attendu.",
                   "Un test unitaire par cas limite identifié.",
                   "Tester les composants par rôle et libellé.",
                   "Réserver le bout en bout aux parcours critiques.",
                   "Corriger un test instable, ne pas le relancer."]),
    ],
    "keypoints": [
        "Trois niveaux de test, trois coûts et trois confiances.",
        "La pyramide réserve le bout en bout aux parcours critiques.",
        "Un test unitaire vérifie un comportement, pas une implémentation.",
        "Un test d'interface s'appuie sur les rôles et les libellés.",
        "Un composant accessible est plus facile à tester.",
        "Une attente fixe produit des tests instables.",
        "Deux réessais ne réparent pas un test cassé.",
        "La couverture mesure l'exécution, pas la vérification.",
    ],
    "bridge": "L'interface est testée. Le volume se referme sur ses annexes : glossaire, "
              "aide-mémoire et grille d'auto-évaluation.",
    "exercises": [
        ex("Écrire trois tests unitaires",
           "Une fonction calcule une remise selon le montant.",
           ["Testez le cas nominal.",
            "Testez la borne.",
            "Testez l'erreur."],
           [("js", """export function remise(montant) {
  if (montant < 0) throw new RangeError("montant négatif");
  if (montant >= 10000) return 0.15;
  if (montant >= 5000) return 0.10;
  return 0;
}

it("applique 10 % à partir de 50 €", () => {
  expect(remise(5000)).toBe(0.10);
});

it("applique 15 % à partir de 100 €", () => {
  expect(remise(10000)).toBe(0.15);
});

it("refuse un montant négatif", () => {
  expect(() => remise(-1)).toThrow(RangeError);
});"""),
            "Testez les bornes exactes : ce sont les cas où les erreurs se cachent.",
            "Un test d'erreur vérifie aussi que l'erreur est du bon type."]),
        ex("Tester un composant par son interface",
           "Un formulaire affiche un message d'erreur si le champ est vide.",
           ["Rendez le composant.",
            "Soumettez vide.",
            "Vérifiez le message."],
           [("js", """it("affiche une erreur quand le champ est vide", async () => {
  render(FormulaireInscription());

  await userEvent.click(screen.getByRole("button", { name: /s'inscrire/i }));

  expect(screen.getByRole("alert").textContent).toMatch(/adresse requise/i);
});

it("n'affiche pas d'erreur avec une adresse valide", async () => {
  render(FormulaireInscription());
  await userEvent.type(screen.getByLabelText(/adresse électronique/i),
                       "a@exemple.fr");
  await userEvent.click(screen.getByRole("button", { name: /s'inscrire/i }));

  expect(screen.queryByRole("alert")).toBeNull();
});"""),
            "`getByRole(\"alert\")` vérifie aussi que le message est annoncé aux lecteurs "
            "d'écran.",
            "`queryByRole` renvoie `null` au lieu d'échouer : utile pour vérifier une "
            "absence."],
           level="Qualité"),
        ex("Stabiliser un test de bout en bout",
           "Un test échoue une fois sur quatre en intégration continue.",
           ["Retirez les attentes fixes.",
            "Attendez un état visible.",
            "Activez la trace."],
           [("js", """// Fragile
await page.click("#valider");
await page.waitForTimeout(2000);

// Robuste
await page.getByRole("button", { name: /valider/i }).click();
await expect(page.getByRole("heading", { name: /confirmation/i })).toBeVisible();

// Et dans la configuration
// use: { trace: "on-first-retry", screenshot: "only-on-failure" }"""),
            "`waitForTimeout` attend une durée arbitraire : trop courte, le test échoue ; "
            "trop longue, il ralentit.",
            "Attendre un état visible est à la fois plus rapide et plus fiable."],
           level="Diagnostic"),
    ],
    "quiz": [
        quiz("Quel niveau de test coûte le plus cher à maintenir ?",
             ["Unitaire", "Intégration", "Bout en bout", "Aucun"],
             2,
             "Il traverse un vrai navigateur et dépend de l'ensemble du système."),
        quiz("Que doit vérifier un test unitaire ?",
             ["L'implémentation", "Le comportement observable",
              "Les classes CSS", "Le nombre de lignes"],
             1,
             "Un test lié à l'implémentation bloque le refactoring."),
        quiz("Quel sélecteur est le plus robuste ?",
             ["Classe CSS", "Identifiant généré", "Rôle et nom accessible", "Position"],
             2,
             "Il suit ce que l'utilisateur perçoit."),
        quiz("Pourquoi éviter `waitForTimeout` ?",
             ["Trop rapide", "Dépend d'une durée arbitraire", "Non supporté",
              "Trop précis"],
             1,
             "Il produit des échecs intermittents ou des tests lents."),
        quiz("Que mesure la couverture de code ?",
             ["La qualité des tests", "Les lignes exécutées", "Le nombre de bugs",
              "La vitesse"],
             1,
             "Elle ne dit rien de la pertinence des assertions."),
    ],
}
