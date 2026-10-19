from bookkit.dsl import (box, code, defn, ex, fig, h, ol, p, quiz, table, ul)

CH = {
    "title": "Projet final : d'un dossier vide à un site en ligne",
    "subtitle": "Mettre en pratique les trente-cinq chapitres précédents en construisant, "
                "testant et publiant un site complet.",
    "duration": "6 h 00",
    "level": "Intermédiaire",
    "prereq": "chapitres 1 à 35",
    "objectives": [
        "Planifier un projet web de bout en bout.",
        "Construire une page d'accueil, une page de contenu et un formulaire.",
        "Appliquer les règles d'accessibilité et de performance.",
        "Versionner, tester et publier le résultat.",
        "Rédiger la documentation d'un projet livré.",
    ],
    "blocks": [
        h(2, "Le projet"),
        p("Vous allez réaliser le site vitrine d'une association culturelle : trois "
          "pages, un formulaire d'inscription à une lettre d'information, un thème "
          "clair et sombre, et une publication en ligne. Le contenu est fourni ; "
          "l'objectif est la qualité d'exécution."),
        table(["Livrable", "Critère d'acceptation"],
              [["Page d'accueil", "En-tête, héros, programmes, pied de page"],
               ["Page « Programmes »", "Grille responsive, filtres accessibles"],
               ["Page « Contact »", "Formulaire validé, messages d'erreur annoncés"],
               ["Feuilles de style", "Trois fichiers, variables, aucun style en ligne"],
               ["JavaScript", "Modules, aucun script bloquant, aucun `innerHTML` de données"],
               ["Qualité", "Contrastes AA, navigation clavier complète, LCP < 2,5 s"],
               ["Versionnement", "Historique lisible, messages explicites"],
               ["Documentation", "`README.md` avec installation et décisions"]],
              widths=[3.6, 8.4], first_col_bold=True,
              caption="Huit livrables et leurs critères"),

        h(2, "Étape 1 : cadrer avant de coder"),
        p("Un projet qui commence par du code produit souvent une structure à refaire. "
          "Trente minutes de cadrage économisent plusieurs heures."),
        ol("**Public** : qui visite le site, avec quel appareil, dans quel contexte ?",
           "**Objectif** : quelle action unique doit être facilitée ?",
           "**Contenu** : quelles pages, quels textes, quelles images ?",
           "**Contraintes** : délai, hébergement, langue, accessibilité.",
           "**Mesure** : comment saura-t-on que le site fonctionne ?"),
        code("""# Cadrage — Association culturelle

Public      : habitants de 25 à 65 ans, 70 % sur mobile
Objectif    : inscription à la lettre d'information
Pages       : accueil, programmes, contact
Contrainte  : hébergement statique, budget nul
Mesure      : nombre d'inscriptions par semaine

# Arborescence
/            accueil
/programmes  liste filtrable
/contact     formulaire
/mentions    page légale""", "text", "Un cadrage en dix lignes"),
        box("methode", "Le contenu d'abord",
            "Écrivez les textes réels avant de dessiner les blocs. Une maquette remplie "
            "de faux texte masque les problèmes de longueur, de hiérarchie et de "
            "densité qui apparaissent avec le contenu vrai."),

        h(2, "Étape 2 : la structure HTML"),
        p("Chaque page partage le même squelette : en-tête, navigation, contenu "
          "principal, pied de page. Les repères ARIA sont implicites grâce aux "
          "éléments sémantiques."),
        code("""<!doctype html>
<html lang="fr">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Association culturelle — Programmes</title>
  <meta name="description" content="Ateliers, rencontres et spectacles de l'association.">
  <link rel="stylesheet" href="assets/styles/base.css">
  <link rel="stylesheet" href="assets/styles/composants.css">
  <link rel="stylesheet" href="assets/styles/pages.css">
  <script type="module" src="assets/scripts/app.js"></script>
</head>
<body>
  <a class="lien-evitement" href="#contenu">Aller au contenu</a>

  <header class="entete">
    <a href="/" class="entete__logo">
      <img src="assets/images/logo.svg" alt="Association culturelle" width="140" height="40">
    </a>
    <button class="menu__bouton" aria-expanded="false" aria-controls="menu-principal">
      Menu
    </button>
    <nav id="menu-principal" aria-label="Navigation principale">
      <ul>
        <li><a href="/" aria-current="page">Accueil</a></li>
        <li><a href="/programmes.html">Programmes</a></li>
        <li><a href="/contact.html">Contact</a></li>
      </ul>
    </nav>
    <button id="bascule-theme" type="button" aria-pressed="false">Thème sombre</button>
  </header>

  <main id="contenu">
    <h1>Nos programmes</h1>
    <!-- contenu -->
  </main>

  <footer class="pied">
    <p>© 2026 Association culturelle</p>
    <a href="/mentions.html">Mentions légales</a>
  </footer>
</body>
</html>""", "html", "Le squelette commun aux trois pages"),
        p("Trois détails font la différence : le lien d'évitement en première position, "
          "`aria-current=\"page\"` sur le lien actif, et un seul `h1` par page."),

        h(2, "Étape 3 : les styles"),
        p("Les styles s'organisent en trois couches : les fondations (variables, "
          "réinitialisation, typographie), les composants (boutons, cartes, formulaires) "
          "et les pages (dispositions spécifiques)."),
        code("""/* base.css — variables et fondations */
:root {
  --navy: #0f2e4c;
  --amber: #e0a21b;
  --ink: #1f2933;
  --mist: #e8edf1;
  --fond: #ffffff;
  --texte: var(--ink);

  --espace-1: .5rem;
  --espace-2: 1rem;
  --espace-3: 2rem;
  --espace-4: 4rem;

  --taille-0: clamp(1rem, .96rem + .2vw, 1.125rem);
  --taille-1: clamp(1.2rem, 1.1rem + .5vw, 1.45rem);
  --taille-2: clamp(1.44rem, 1.26rem + .9vw, 1.9rem);
  --taille-3: clamp(1.73rem, 1.44rem + 1.4vw, 2.5rem);

  --rayon: 8px;
  --duree: 160ms;
}

[data-theme="sombre"] {
  --fond: #0b1622;
  --texte: #e8edf1;
  --mist: #1b2c3d;
}

*, *::before, *::after { box-sizing: border-box; }

body {
  margin: 0;
  font-family: "Inter", system-ui, sans-serif;
  font-size: var(--taille-0);
  line-height: 1.6;
  color: var(--texte);
  background: var(--fond);
}

:focus-visible {
  outline: 3px solid var(--amber);
  outline-offset: 3px;
}""", "css", "Une couche de fondations"),
        code("""/* composants.css — la carte de programme */
.carte {
  display: grid;
  gap: var(--espace-1);
  padding: var(--espace-2);
  border: 1px solid var(--mist);
  border-radius: var(--rayon);
  background: var(--fond);
}

.carte__titre { font-size: var(--taille-1); margin: 0; }
.carte__meta { color: #5b6770; font-size: .9em; }

@media (prefers-reduced-motion: no-preference) {
  .carte { transition: transform var(--duree) ease; }
  .carte:hover { transform: translateY(-2px); }
}""", "css", "Un composant réutilisable"),
        code("""/* pages.css — la grille des programmes */
.grille-programmes {
  display: grid;
  gap: var(--espace-2);
  grid-template-columns: repeat(auto-fit, minmax(min(100%, 18rem), 1fr));
}

.conteneur {
  width: min(100% - 2 * var(--espace-2), 68rem);
  margin-inline: auto;
}

.section { padding-block: var(--espace-4); }""", "css", "Une mise en page qui s'adapte seule"),
        p("`min(100%, 18rem)` dans `minmax` empêche une carte de dépasser la largeur de "
          "l'écran sur mobile : c'est le détail qui distingue une grille robuste d'une "
          "grille qui déborde."),

        h(2, "Étape 4 : l'interactivité"),
        p("Trois comportements suffisent : le menu mobile, la bascule de thème et le "
          "filtre des programmes. Chacun est un module indépendant."),
        code("""// modules/menu.js
export function initialiserMenu() {
  const bouton = document.querySelector(".menu__bouton");
  const nav = document.querySelector("#menu-principal");
  if (!bouton || !nav) return;

  const basculer = (ouvrir) => {
    bouton.setAttribute("aria-expanded", String(ouvrir));
    nav.classList.toggle("est-ouvert", ouvrir);
  };

  bouton.addEventListener("click", () => {
    basculer(bouton.getAttribute("aria-expanded") !== "true");
  });

  nav.addEventListener("keydown", (e) => {
    if (e.key === "Escape") { basculer(false); bouton.focus(); }
  });
}""", "js", "Un module qui possède son état"),
        code("""// modules/theme.js
const CLE = "theme";
const VALEURS = ["clair", "sombre", "auto"];

function appliquer(valeur) {
  const theme = VALEURS.includes(valeur) ? valeur : "auto";
  document.documentElement.dataset.theme = theme === "auto"
    ? (matchMedia("(prefers-color-scheme: dark)").matches ? "sombre" : "clair")
    : theme;
  return theme;
}

export function initialiserTheme() {
  const bouton = document.querySelector("#bascule-theme");
  appliquer(localStorage.getItem(CLE));

  bouton.addEventListener("click", () => {
    const sombre = document.documentElement.dataset.theme === "sombre";
    const suivant = sombre ? "clair" : "sombre";
    localStorage.setItem(CLE, suivant);
    appliquer(suivant);
    bouton.setAttribute("aria-pressed", String(!sombre));
  });

  window.addEventListener("storage", (e) => {
    if (e.key === CLE) appliquer(e.newValue);
  });
}""", "js", "Un thème persistant et partagé entre onglets"),
        code("""// modules/filtres.js
export function initialiserFiltres() {
  const groupe = document.querySelector("[data-filtres]");
  const cartes = [...document.querySelectorAll("[data-theme-carte]")];
  if (!groupe) return;

  groupe.addEventListener("click", (e) => {
    const bouton = e.target.closest("[data-filtre]");
    if (!bouton) return;

    groupe.querySelectorAll("[data-filtre]").forEach((b) => {
      b.setAttribute("aria-pressed", String(b === bouton));
    });

    const filtre = bouton.dataset.filtre;
    cartes.forEach((carte) => {
      carte.hidden = filtre !== "tous" && carte.dataset.themeCarte !== filtre;
    });

    const visibles = cartes.filter((c) => !c.hidden).length;
    document.querySelector("[data-compteur]").textContent =
      `${visibles} programme${visibles > 1 ? "s" : ""}`;
  });
}""", "js", "Un filtre avec compteur annoncé"),
        box("pratique", "Un point d'entrée unique",
            "`app.js` importe les trois modules et les initialise. Chaque module gère "
            "ses intérêts et ne connaît pas les autres : l'ordre d'initialisation n'a "
            "pas d'importance."),

        h(2, "Étape 5 : le formulaire"),
        p("La page de contact comporte quatre champs et une case de consentement. La "
          "validation reprend exactement les principes du chapitre 28."),
        code("""<form id="inscription" novalidate>
  <div class="champ">
    <label for="nom">Nom complet</label>
    <input id="nom" name="nom" autocomplete="name" required minlength="2">
  </div>

  <div class="champ">
    <label for="courriel">Adresse électronique</label>
    <input id="courriel" name="courriel" type="email"
           autocomplete="email" required aria-describedby="courriel-aide">
    <p id="courriel-aide" class="aide">Nous ne partagerons jamais votre adresse.</p>
  </div>

  <div class="champ">
    <label for="motif">Motif du contact</label>
    <select id="motif" name="motif" required>
      <option value="">Choisir…</option>
      <option>Inscription</option>
      <option>Bénévolat</option>
      <option>Autre</option>
    </select>
  </div>

  <div class="champ">
    <label for="message">Message</label>
    <textarea id="message" name="message" rows="6" required minlength="20"></textarea>
  </div>

  <label class="consentement">
    <input type="checkbox" name="consentement" required>
    J'accepte de recevoir la lettre d'information.
  </label>

  <button type="submit">Envoyer</button>
</form>""", "html", "Un formulaire complet"),
        code("""// modules/formulaire.js
export function initialiserFormulaire() {
  const form = document.querySelector("#inscription");
  if (!form) return;

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    if (!form.checkValidity()) { form.reportValidity(); return; }

    const bouton = form.querySelector("button[type=submit]");
    bouton.disabled = true;
    bouton.setAttribute("aria-busy", "true");

    try {
      await envoyer(Object.fromEntries(new FormData(form)));
      afficherMessage("Merci, votre message est envoyé.", "succes");
      form.reset();
    } catch (erreur) {
      afficherMessage("L'envoi a échoué. Vos données sont conservées.", "erreur");
    } finally {
      bouton.disabled = false;
      bouton.removeAttribute("aria-busy");
    }
  });
}""", "js", "Un envoi qui préserve la saisie"),

        h(2, "Étape 6 : qualité avant publication"),
        p("Avant de publier, cinq contrôles systématiques évitent la majorité des "
          "désagréments. Aucun ne demande plus de dix minutes."),
        table(["Contrôle", "Outil", "Critère"],
              [["Validation HTML", "W3C Validator", "Aucune erreur"],
               ["Accessibilité", "Lighthouse + clavier", "Aucun blocage, contrastes AA"],
               ["Performance", "Lighthouse mobile", "LCP < 2,5 s, CLS < 0,1"],
               ["Responsive", "Outils de développement", "320 px à 1920 px"],
               ["Liens", "Vérificateur de liens", "Aucun 404"]],
              widths=[3.4, 4.6, 4.2], first_col_bold=True,
              caption="Cinq contrôles avant publication"),
        code("""# Parcours manuel de vérification
# 1. Tabuler sur chaque page : le focus est-il toujours visible ?
# 2. Zoomer à 200 % : le contenu reste-t-il lisible et complet ?
# 3. Naviguer avec le clavier seul : tous les composants fonctionnent-ils ?
# 4. Désactiver JavaScript : le contenu essentiel est-il présent ?
# 5. Simuler un réseau lent : un indicateur apparaît-il ?""", "bash",
             "Un parcours de dix minutes"),

        h(2, "Étape 7 : publication"),
        p("L'hébergement statique est gratuit et suffisant pour ce projet. Le principe "
          "est toujours le même : construire, puis envoyer le contenu du dossier "
          "produit."),
        code("""# Construction
npm run build

# Envoi par rsync vers un hébergement classique
rsync -avz --delete dist/ utilisateur@serveur:/var/www/mon-site/

# Ou publication sur une plateforme statique
npx vercel deploy --prod dist/
npx netlify deploy --prod --dir=dist""", "bash", "Trois façons de publier"),
        code("""# Vérifications après mise en ligne
curl -I https://exemple.fr                 # code 200, en-têtes de sécurité
curl -I https://exemple.fr/assets/index-3f2a91.css   # cache long
# Tester sur un appareil réel : téléphone, réseau mobile""", "bash",
             "Contrôler ce qui est réellement servi"),
        defn("Déploiement atomique", "Publication où la nouvelle version remplace "
                                     "l'ancienne d'un seul coup, sans état intermédiaire. "
                                     "En cas d'échec, l'ancienne version reste servi."),

        h(2, "Étape 8 : documenter"),
        p("Un projet sans documentation est un projet impossible à reprendre. Un "
          "`README.md` de vingt lignes suffit s'il contient les bonnes informations."),
        code("""# Site de l'association culturelle

Site vitrine statique : trois pages, thème clair et sombre,
formulaire d'inscription.

## Installation
    npm install
    npm run dev        # http://localhost:8080

## Construction
    npm run build      # produit dist/

## Structure
    src/               sources
    dist/              fichiers construits, non versionnés
    assets/styles/     trois couches : base, composants, pages

## Décisions
- Aucune bibliothèque d'interface : le CSS natif suffit.
- Thème mémorisé dans `localStorage`, synchronisé entre onglets.
- Validation native complétée par des messages explicites.

## Accessibilité
Contrastes AA vérifiés, navigation clavier complète,
lien d'évitement, formulaire annoncé.""", "markdown", "Une documentation suffisante"),
        box("retenir", "Ce qui distingue un projet professionnel",
            items=["Un historique Git lisible.",
                   "Une structure de fichiers prévisible.",
                   "Aucune dépendance inutile.",
                   "Des états d'erreur et de chargement prévus.",
                   "Une documentation à jour."]),

        h(2, "Pour aller plus loin"),
        p("Ce cours s'arrête à la publication d'un site statique. Trois pistes "
          "prolongent naturellement le parcours : un cadre applicatif pour les "
          "interfaces à état complexe, un back-end pour les données persistantes, et "
          "une chaîne d'intégration continue pour automatiser les contrôles."),
        table(["Piste", "Quand l'aborder", "Premier pas"],
              [["Cadre applicatif", "Interface à nombreux états", "Un composant, puis deux"],
               ["Back-end", "Données à stocker", "Une API minimale"],
               ["Intégration continue", "Plusieurs contributeurs", "Un test automatique"],
               ["Tests de bout en bout", "Parcours critiques", "Un scénario Playwright"]],
              widths=[3.6, 4.6, 4.0], first_col_bold=True,
              caption="Quatre prolongements naturels"),
        p("La partie suivante approfondit quatre de ces pistes avant de laisser la "
          "place au cours 2, consacré à l'infrastructure, au déploiement continu et à "
          "l'exploitation."),
    ],
    "keypoints": [
        "Le cadrage précède le code.",
        "Le contenu réel révèle les problèmes de mise en page.",
        "Une page possède un `h1` et des repères sémantiques.",
        "Les styles s'organisent en fondations, composants et pages.",
        "Chaque module JavaScript possède son état et son initialisation.",
        "Un formulaire conserve la saisie en cas d'échec.",
        "Cinq contrôles précèdent toute publication.",
        "Un `README.md` court et juste vaut mieux qu'aucune documentation.",
    ],
    "bridge": "Le site est livré. La dernière partie revient sur les outils qui le "
              "rendent durable : CSS contemporain, composants réutilisables, contenu "
              "multilingue et maintenance.",
    "exercises": [
        ex("Construire la page d'accueil",
           "Réalisez le squelette complet de la page d'accueil.",
           ["En-tête, héros, trois programmes, pied de page.",
            "Un seul `h1`, des `h2` pour les sections.",
            "Aucune image sans dimensions ni alternative."],
           [("code", """<main id="contenu">
  <section class="heros section">
    <div class="conteneur">
      <p class="surtitre">Saison 2026</p>
      <h1>La culture se partage</h1>
      <p class="lead">Ateliers, rencontres et spectacles ouverts à tous.</p>
      <a class="bouton" href="/programmes.html">Voir les programmes</a>
    </div>
  </section>

  <section class="section" aria-labelledby="titre-programmes">
    <div class="conteneur">
      <h2 id="titre-programmes">À venir</h2>
      <ul class="grille-programmes">
        <li><article class="carte">…</article></li>
      </ul>
    </div>
  </section>
</main>"""),
            "`aria-labelledby` relie la section à son titre, ce qui donne un nom "
            "exploitable par les technologies d'assistance.",
            "La liste de cartes est une liste : le nombre d'éléments est annoncé."]),
        ex("Écrire le module de filtres",
           "Les programmes se filtrent par catégorie, avec un compteur.",
           ["Un bouton par catégorie, avec `aria-pressed`.",
            "Masquez avec `hidden`, pas avec `display:none` en style.",
            "Annoncez le nombre de résultats."],
           [("code", """<div data-filtres role="group" aria-label="Filtrer les programmes">
  <button type="button" data-filtre="tous" aria-pressed="true">Tous</button>
  <button type="button" data-filtre="atelier" aria-pressed="false">Ateliers</button>
  <button type="button" data-filtre="scene" aria-pressed="false">Spectacles</button>
</div>
<p data-compteur aria-live="polite">3 programmes</p>"""),
            "`aria-pressed` indique l'état de chaque bouton ; un seul est actif.",
            "`aria-live=\"polite\"` fait annoncer le compteur sans interrompre la "
            "lecture en cours."]),
        ex("Préparer la livraison",
           "Produisez un dossier de livraison vérifié.",
           ["Construisez, contrôlez, versionnez.",
            "Rédigez le `README.md`.",
            "Préparez une capture de la page d'accueil."],
           [("bash", """npm run lint && npm run test && npm run build
du -sh dist
ls dist/assets

git add .
git commit -m "Livre la version 1.0 du site

Trois pages, thème clair et sombre, formulaire validé.
Accessibilité AA vérifiée, LCP mesuré à 1,8 s en 4G."
git tag v1.0.0
git push origin main --tags"""),
            "Le tag marque une version livrée : il permet de revenir exactement à cet "
            "état.",
            "Le message de commit résume ce qui est livré et les vérifications "
            "effectuées."],
           level="Mise en production"),
    ],
    "quiz": [
        quiz("Par quoi commence un projet web bien mené ?",
             ["Par le CSS", "Par le cadrage du besoin et du contenu",
              "Par le choix d'un cadre applicatif", "Par l'hébergement"],
             1,
             "Le périmètre, le public et les critères d'acceptation précèdent le code."),
        quiz("Combien de `h1` une page doit-elle contenir ?",
             ["Un seul", "Autant que de sections", "Aucun", "Au moins trois"],
             0,
             "Un `h1` unique décrit le sujet de la page ; les sections utilisent `h2`."),
        quiz("Comment masquer un élément filtré sans casser l'accessibilité ?",
             ["`display: none` en style en ligne", "L'attribut `hidden`",
              "`opacity: 0`", "`visibility: hidden`"],
             1,
             "`hidden` retire l'élément de l'arbre d'accessibilité de façon standard."),
        quiz("Que vérifier avant de publier ?",
             ["Uniquement le rendu visuel", "HTML, accessibilité, performance, responsive, liens",
              "Seulement la vitesse", "Rien, on corrige après"],
             1,
             "Cinq contrôles couvrent l'essentiel des défauts de mise en production."),
        quiz("À quoi sert un tag Git de version ?",
             ["À accélérer les commits", "À marquer un état livré et pouvoir y revenir",
              "À compresser le dépôt", "À signer les fichiers"],
             1,
             "Le tag identifie précisément la version publiée dans l'historique."),
    ],
}
