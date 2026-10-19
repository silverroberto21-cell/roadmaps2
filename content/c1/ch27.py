from bookkit.dsl import (box, code, defn, ex, fig, h, ol, p, quiz, table, ul)

CH = {
    "title": "Événements et interaction",
    "subtitle": "Réagir aux actions de l'utilisateur : clics, clavier, formulaires et "
                "événements personnalisés.",
    "duration": "2 h 45",
    "level": "Intermédiaire",
    "prereq": "chapitre 26",
    "objectives": [
        "Écouter et retirer des écouteurs d'événements.",
        "Comprendre la propagation et utiliser la délégation.",
        "Gérer le clavier et le focus dans les composants interactifs.",
        "Éviter les écouteurs en fuite et les manipulations coûteuses.",
        "Construire un menu déroulant accessible complet.",
    ],
    "blocks": [
        h(2, "Écouter un événement"),
        p("`addEventListener` associe une fonction à un type d'événement sur un "
          "élément. L'écouteur reçoit un objet `Event` qui décrit l'action : cible, "
          "coordonnées, touche pressée, état des modificateurs."),
        code("""const bouton = document.querySelector("#envoyer");

function gererClic(event) {
  event.preventDefault();       // annule le comportement par défaut
  console.log("Clic sur", event.currentTarget);
}

bouton.addEventListener("click", gererClic);

// Retirer l'écouteur : la fonction doit être nommée
bouton.removeEventListener("click", gererClic);

// Option : une seule exécution
bouton.addEventListener("click", gererClic, { once: true });""", "js",
             "Ajouter, retirer et limiter un écouteur"),
        table(["Événement", "Déclencheur", "Usage"],
              [["`click`", "Clic ou activation clavier", "Boutons, liens"],
               ["`input`", "Saisie dans un champ", "Validation en direct"],
               ["`change`", "Validation du champ", "Select, cases"],
               ["`submit`", "Envoi de formulaire", "Traitement"],
               ["`keydown`", "Touche pressée", "Raccourcis, Échap"],
               ["`focus` / `blur`", "Entrée/sortie de focus", "Aide contextuelle"],
               ["`scroll`", "Défilement", "En-tête collant"],
               ["`resize`", "Redimensionnement", "Recalculs"],
               ["`DOMContentLoaded`", "DOM analysé", "Initialisation"]],
              widths=[2.8, 4.2, 4.0], first_col_bold=True,
              caption="Neuf événements courants"),
        p("`DOMContentLoaded` se déclenche quand le DOM est construit, sans attendre "
          "les images. Un script chargé avec `defer` s'exécute après cet événement : "
          "l'écouteur n'est donc pas nécessaire dans ce cas."),

        h(2, "Propagation et délégation"),
        p("Un événement se propage de la cible vers la racine (bouillonnement). C'est "
          "ce qui permet d'écouter un seul parent au lieu de chaque enfant."),
        fig("flow", "Les trois phases de propagation",
            ["Capture : de la racine vers la cible",
             "Cible : l'élément déclencheur",
             "Bouillonnement : de la cible vers la racine",
             "`stopPropagation()` interrompt le parcours",
             "La délégation utilise le bouillonnement"],
            height=245),
        code("""// Sans délégation : un écouteur par élément
document.querySelectorAll(".onglet").forEach(onglet => {
  onglet.addEventListener("click", activer);
});

// Avec délégation : un seul écouteur
document.querySelector(".onglets").addEventListener("click", (event) => {
  const onglet = event.target.closest(".onglet");
  if (!onglet) return;              // clic hors d'un onglet
  activer(onglet);
});""", "js", "Deux approches, un coût très différent"),
        p("La délégation fonctionne aussi pour des éléments ajoutés après le chargement "
          "initial : c'est son second avantage. Un écouteur direct sur un élément "
          "inexistant ne sert à rien."),
        box("attention", "`stopPropagation` n'est pas un outil de correction",
            "Bloquer la propagation casse la délégation des autres scripts et les "
            "comportements natifs. Utilisez-la uniquement lorsqu'un composant doit "
            "isoler un événement interne."),

        h(2, "Clavier et focus"),
        p("Un composant interactif doit répondre au clavier. Pour un bouton natif, "
          "Entrée et Espace sont gérés par le navigateur ; pour un élément personnalisé, "
          "tout est à votre charge."),
        code("""document.addEventListener("keydown", (event) => {
  if (event.key === "Escape") {
    fermerMenu();
  }
  if (event.key === "/" && document.activeElement.tagName !== "INPUT") {
    event.preventDefault();
    champRecherche.focus();
  }
});

// Piège de focus dans une modale
function piegerFocus(conteneur, event) {
  const focusables = conteneur.querySelectorAll(
    'a[href], button:not([disabled]), input, select, textarea, [tabindex]:not([tabindex="-1"])'
  );
  const premier = focusables[0];
  const dernier = focusables[focusables.length - 1];
  if (event.key !== "Tab") return;
  if (event.shiftKey && document.activeElement === premier) {
    event.preventDefault();
    dernier.focus();
  } else if (!event.shiftKey && document.activeElement === dernier) {
    event.preventDefault();
    premier.focus();
  }
}""", "js", "Deux usages du clavier"),
        p("La propriété `event.key` renvoie le nom de la touche (« Escape », « Enter », "
          "« a »), contrairement à `event.code` qui renvoie la position physique. "
          "`key` est presque toujours le bon choix."),

        h(2, "Événements de formulaire"),
        p("L'événement `submit` est le point d'entrée naturel : il se déclenche au clic "
          "sur un bouton d'envoi comme à l'appui sur Entrée. L'écouter évite de traiter "
          "le clic et de perdre l'accessibilité."),
        code("""formulaire.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (!formulaire.reportValidity()) return;

  const donnees = new FormData(formulaire);
  const valeurs = Object.fromEntries(donnees);
  await envoyer(valeurs);
});""", "js", "Un envoi de formulaire maîtrisé"),
        table(["Événement", "Quand", "À privilégier pour"],
              [["`input`", "À chaque frappe", "Aperçu, compteur"],
               ["`change`", "À la validation", "Select, date"],
               ["`submit`", "À l'envoi", "Traitement principal"],
               ["`blur`", "À la sortie", "Validation de champ"],
               ["`invalid`", "Si un champ est invalide", "Messages personnalisés"]],
              widths=[2.6, 4.2, 4.2], first_col_bold=True,
              caption="Cinq événements de formulaire et leur usage"),

        h(2, "Événements personnalisés"),
        p("Un composant peut émettre ses propres événements pour communiquer avec le "
          "reste de la page, sans couplage direct."),
        code("""class Panneau extends HTMLElement {
  ouvrir() {
    this.hidden = false;
    this.dispatchEvent(new CustomEvent("panneau:ouvert", {
      bubbles: true,
      detail: { id: this.id },
    }));
  }
}
customElements.define("mon-panneau", Panneau);

document.addEventListener("panneau:ouvert", (event) => {
  console.log("Ouvert :", event.detail.id);
});""", "js", "Un composant qui annonce son état"),
        p("Les événements personnalisés suivent la même propagation que les événements "
          "natifs. Le champ `detail` transporte les données, ce qui évite d'inventer "
          "des propriétés globales."),

        h(2, "Fuites et performance"),
        p("Un écouteur conservé après la disparition de son élément empêche la "
          "libération de la mémoire. Les composants doivent retirer leurs écouteurs au "
          "démontage."),
        code("""// Écouteur coûteux sur scroll : à limiter
let planifie = false;
window.addEventListener("scroll", () => {
  if (planifie) return;
  planifie = true;
  requestAnimationFrame(() => {
    gererDefilement();
    planifie = false;
  });
}, { passive: true });""", "js", "Un écouteur de défilement maîtrisé"),
        box("pratique", "`{ passive: true }`",
            "Sur `scroll` et `touchmove`, l'option `passive` indique au navigateur que "
            "vous n'appellerez pas `preventDefault`, ce qui lui permet de faire défiler "
            "sans attendre votre code."),
        box("methode", "Contrôle d'un composant interactif",
            items=["S'active-t-il au clic **et** au clavier ?",
                   "L'état est-il annoncé (`aria-expanded`, `aria-selected`) ?",
                   "Échap ferme-t-il le composant ?",
                   "Le focus revient-il au déclencheur ?",
                   "Les écouteurs sont-ils retirés au démontage ?"]),
    ],
    "keypoints": [
        "`addEventListener` accepte `once` et `passive`.",
        "`DOMContentLoaded` est inutile avec un script `defer`.",
        "La délégation réduit le nombre d'écouteurs et gère les ajouts dynamiques.",
        "`event.key` décrit la touche, `event.code` sa position physique.",
        "`submit` est le point d'entrée correct d'un formulaire.",
        "Un composant doit annoncer ses changements d'état.",
        "Les écouteurs doivent être retirés lorsque le composant disparaît.",
    ],
    "bridge": "Les interactions sont en place. Le chapitre suivant les applique aux "
              "formulaires : validation, messages et retour utilisateur.",
    "exercises": [
        ex("Menu déroulant complet",
           "Un bouton ouvre une liste d'options. Implémentez le comportement complet.",
           ["Clic et clavier pour ouvrir.",
            "Échap pour fermer.",
            "Focus rendu au bouton."],
           [("code", """const bouton = document.querySelector("#menu-bouton");
const liste = document.querySelector("#menu-liste");

function ouvrir() {
  bouton.setAttribute("aria-expanded", "true");
  liste.hidden = false;
  liste.querySelector("a")?.focus();
}
function fermer() {
  bouton.setAttribute("aria-expanded", "false");
  liste.hidden = true;
  bouton.focus();
}

bouton.addEventListener("click", () => {
  bouton.getAttribute("aria-expanded") === "true" ? fermer() : ouvrir();
});

liste.addEventListener("keydown", (e) => {
  if (e.key === "Escape") fermer();
});

document.addEventListener("click", (e) => {
  if (!liste.hidden && !e.target.closest(".menu")) fermer();
});"""),
            "Le focus se déplace dans la liste à l'ouverture, ce qui permet la "
            "navigation au clavier sans Tab supplémentaire.",
            "Le clic à l'extérieur ferme le menu, comportement attendu par tous les "
            "utilisateurs."]),
        ex("Délégation sur une liste dynamique",
           "Une liste de tâches peut recevoir de nouveaux éléments. Gérez la "
           "suppression sans réattacher d'écouteurs.",
           ["Écoutez sur le conteneur.",
            "Utilisez `closest` pour trouver la tâche.",
            "Vérifiez que les éléments ajoutés fonctionnent aussi."],
           [("code", """liste.addEventListener("click", (event) => {
  const bouton = event.target.closest("[data-supprimer]");
  if (!bouton) return;
  bouton.closest("li").remove();
});

// Ajout ultérieur : fonctionne sans nouvel écouteur
const li = document.createElement("li");
li.innerHTML = '<span>Tâche</span> <button data-supprimer>Supprimer</button>';
liste.append(li);"""),
            "L'écouteur sur le parent reçoit les clics de tous les enfants, présents ou "
            "futurs.",
            "`closest` remonte depuis le bouton jusqu'à la tâche concernée, même si le "
            "clic porte sur une icône interne."]),
        ex("Optimiser un gestionnaire de défilement",
           "Un en-tête change d'apparence au défilement et saccade.",
           ["Limitez les appels avec `requestAnimationFrame`.",
            "Ajoutez `passive: true`.",
            "Mesurez avant et après dans l'onglet Performance."],
           [("code", """let enAttente = false;
window.addEventListener("scroll", () => {
  if (enAttente) return;
  enAttente = true;
  requestAnimationFrame(() => {
    document.body.classList.toggle("entete-compact", window.scrollY > 40);
    enAttente = false;
  });
}, { passive: true });"""),
            "Sans limitation, l'événement `scroll` se déclenche des dizaines de fois "
            "par seconde et chaque appel force un recalcul.",
            "`requestAnimationFrame` aligne le traitement sur le rafraîchissement de "
            "l'écran ; `passive` évite d'attendre le script pour défiler."],
           level="Performance"),
    ],
    "quiz": [
        quiz("Quelle option limite un écouteur à une seule exécution ?",
             ["`once: true`", "`single: true`", "`capture: true`", "`passive: true`"],
             0,
             "`once` retire automatiquement l'écouteur après le premier déclenchement."),
        quiz("Sur quelle phase repose la délégation d'événements ?",
             ["La capture", "Le bouillonnement", "La cible", "Aucune"],
             1,
             "L'événement remonte de la cible vers la racine, ce qui permet à un parent "
             "de l'intercepter."),
        quiz("Quel événement écouter pour intercepter l'envoi d'un formulaire ?",
             ["`click`", "`submit`", "`change`", "`input`"],
             1,
             "`submit` se déclenche quel que soit le moyen d'envoi, clic ou touche "
             "Entrée."),
        quiz("Que fait `{ passive: true }` ?",
             ["Empêche le déclenchement", "Indique qu'on n'appellera pas `preventDefault`",
              "Capture l'événement", "Limite la fréquence"],
             1,
             "Le navigateur peut alors traiter le défilement sans attendre le script."),
        quiz("Pourquoi retirer un écouteur lors du démontage ?",
             ["Pour accélérer le rendu", "Pour éviter une fuite mémoire",
              "Pour réinitialiser l'état", "Ce n'est pas nécessaire"],
             1,
             "Un écouteur qui référence un élément supprimé empêche sa libération et "
             "peut se déclencher sur des données obsolètes."),
    ],
}
