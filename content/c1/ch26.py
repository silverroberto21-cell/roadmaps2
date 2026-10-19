from bookkit.dsl import (box, code, defn, ex, fig, h, ol, p, quiz, table, ul)

CH = {
    "title": "Le DOM et la manipulation de la page",
    "subtitle": "Lire, créer et modifier le document depuis JavaScript, sans casser "
                "l'accessibilité ni les performances.",
    "duration": "3 h 00",
    "level": "Intermédiaire",
    "prereq": "chapitre 25",
    "objectives": [
        "Comprendre la différence entre HTML source et DOM vivant.",
        "Sélectionner efficacement des éléments.",
        "Créer, insérer, déplacer et supprimer des nœuds.",
        "Modifier les classes et les attributs sans écraser l'existant.",
        "Éviter les manipulations coûteuses et les fuites mémoire.",
    ],
    "blocks": [
        h(2, "Le DOM n'est pas votre HTML"),
        p("Le navigateur analyse le HTML et construit un arbre d'objets : le DOM. Cet "
          "arbre peut différer du source — une balise non fermée est corrigée, un "
          "`<tbody>` est ajouté, un script peut tout modifier."),
        fig("tree", "Du fichier au DOM",
            ("index.html", [("Analyse", ["tokenisation", "correction des erreurs"]),
                            ("DOM", ["nœuds", "attributs", "texte"]),
                            ("API", ["querySelector", "createElement", "append"])]),
            height=215),
        code("""<ul id="liste">
  <li>Un</li>
</ul>
<script>
  const ul = document.getElementById("liste");
  console.log(ul.children.length);   // 1
  ul.insertAdjacentHTML("beforeend", "<li>Deux</li>");
  console.log(ul.children.length);   // 2
  // Le fichier source n'a pas changé : seul le DOM a évolué.
</script>""", "js", "Le DOM évolue, le fichier reste intact"),
        defn("Nœud", "Élément de l'arbre DOM : élément HTML, texte, commentaire ou "
                     "document. Tous héritent de `Node`, mais seuls les éléments "
                     "héritent de `Element`."),

        h(2, "Sélectionner"),
        p("`querySelector` renvoie le premier élément correspondant à un sélecteur CSS, "
          "`querySelectorAll` une liste statique. Les méthodes plus anciennes restent "
          "utiles pour leur rapidité et leur clarté."),
        table(["Méthode", "Retour", "Remarque"],
              [["`querySelector`", "Premier élément ou `null`", "Sélecteur CSS complet"],
               ["`querySelectorAll`", "`NodeList` statique", "Non vivante"],
               ["`getElementById`", "Élément ou `null`", "Très rapide"],
               ["`getElementsByClassName`", "`HTMLCollection` vivante", "Se met à jour"],
               ["`closest`", "Ancêtre correspondant", "Idéal en délégation"],
               ["`matches`", "Booléen", "Test de sélecteur"]],
              widths=[3.6, 4.0, 3.4], first_col_bold=True,
              caption="Six méthodes de sélection"),
        code("""const bouton = document.querySelector(".bouton--principal");
const cartes = document.querySelectorAll(".carte");
const titre = document.getElementById("titre-page");

cartes.forEach(carte => carte.classList.add("carte--chargee"));

// `closest` remonte l'arbre depuis un enfant
const lien = document.querySelector("a");
const carteParente = lien.closest(".carte");""", "js", "Sélections courantes"),
        box("attention", "`querySelectorAll` n'est pas vivante",
            "Une `NodeList` renvoyée par `querySelectorAll` ne change pas quand le DOM "
            "évolue. `getElementsByClassName` renvoie au contraire une collection "
            "vivante, ce qui surprend dans une boucle."),

        h(2, "Créer et insérer"),
        p("Trois familles s'offrent à vous : `innerHTML`, `createElement` et "
          "`insertAdjacentHTML`. La première est rapide à écrire mais risque "
          "l'injection ; la deuxième est sûre mais verbeuse."),
        code("""// 1. innerHTML : lisible, mais interprète le HTML
liste.innerHTML += "<li>Trois</li>";

// 2. createElement : sûr, explicite
const li = document.createElement("li");
li.textContent = "Quatre";          // échappe le contenu
liste.append(li);

// 3. insertAdjacentHTML : compromis
liste.insertAdjacentHTML("beforeend", "<li>Cinq</li>");

// 4. Modèle : idéal pour les structures répétées
const modele = document.getElementById("modele-item");
const clone = modele.content.cloneNode(true);
clone.querySelector(".item__nom").textContent = "Six";
liste.append(clone);""", "js", "Quatre façons d'ajouter un élément"),
        table(["Méthode", "Position", "Sécurité"],
              [["`append`", "Dernier enfant", "Sûre (nœuds)"],
               ["`prepend`", "Premier enfant", "Sûre"],
               ["`before`", "Avant l'élément", "Sûre"],
               ["`after`", "Après l'élément", "Sûre"],
               ["`replaceWith`", "Remplace l'élément", "Sûre"],
               ["`insertAdjacentHTML`", "4 positions", "Interprète le HTML"]],
              widths=[3.6, 4.0, 3.4], first_col_bold=True,
              caption="Six méthodes d'insertion"),
        p("`textContent` écrit du texte, jamais du HTML : c'est la propriété à utiliser "
          "pour insérer une donnée utilisateur. `innerHTML` interprète les balises et "
          "ouvre la porte aux injections."),
        code("""const avis = "<img src=x onerror=alert('xss')>";

liste.textContent = avis;   // affiche le texte, inoffensif
// liste.innerHTML = avis;  // exécute le code : faille XSS""", "js",
             "La différence décisive entre `textContent` et `innerHTML`"),

        h(2, "Classes, attributs et styles"),
        p("`classList` gère les classes sans écraser les autres. Ne réaffectez jamais "
          "`className` sur un élément dont d'autres scripts ou composants dépendent."),
        code("""const panneau = document.querySelector(".panneau");

panneau.classList.add("ouvert");
panneau.classList.remove("ferme");
panneau.classList.toggle("ouvert", estOuvert);
panneau.classList.replace("ancien", "nouveau");
panneau.classList.contains("ouvert");     // booléen

panneau.dataset.etat = "ouvert";          // attribut data-etat
panneau.getAttribute("aria-expanded");    // lecture
panneau.setAttribute("aria-expanded", "true");
panneau.removeAttribute("hidden");""", "js", "Manipuler les classes et les attributs"),
        code("""// Préférer les classes aux styles en ligne
panneau.style.height = "0px";        // à éviter : écrase tout style en ligne
panneau.classList.add("est-ferme");  // à privilégier""", "js",
             "Les styles en ligne se combattent mal"),
        box("pratique", "`data-*` pour les valeurs, les classes pour l'apparence",
            "Un attribut `data-etat` peut porter une valeur lue par le CSS "
            "(`[data-etat=\"ouvert\"]`) et par le JavaScript. C'est un contrat clair "
            "entre les deux."),

        h(2, "Supprimer et déplacer"),
        p("Un élément retiré du DOM reste en mémoire tant qu'une variable le référence. "
          "Supprimez les écouteurs avant de retirer un nœud conservé, ou laissez le "
          "ramasse-miettes faire son travail en supprimant les références."),
        code("""const element = document.querySelector(".temporaire");
element.remove();          // moderne, simple
// parent.removeChild(element);   // équivalent plus ancien

// Déplacer un nœud existant le retire de sa position initiale
const dernier = document.querySelector(".liste li:last-child");
document.querySelector(".archive").append(dernier);""", "js",
             "Supprimer et déplacer un nœud"),
        fig("flow", "Cycle de vie d'un nœud",
            ["Création en mémoire (detached)",
             "Insertion dans le DOM (connected)",
             "Mise à jour des classes et attributs",
             "Retrait du DOM",
             "Libération mémoire si plus aucune référence"],
            height=245),

        h(2, "Performance des manipulations"),
        p("Chaque modification du DOM peut déclencher un recalcul de mise en page. "
          "Modifier mille éléments un par un produit mille recalculs. Trois techniques "
          "évitent ce coût."),
        code("""// 1. Construire hors du DOM, puis insérer une fois
const fragment = document.createDocumentFragment();
for (const item of items) {
  const li = document.createElement("li");
  li.textContent = item.nom;
  fragment.append(li);
}
liste.append(fragment);

// 2. Grouper les lectures et les écritures
const hauteur = element.offsetHeight;   // lecture
element.style.height = hauteur + "px"; // écriture
// Ne pas alterner lecture/écriture dans une boucle

// 3. Différer avec requestAnimationFrame
requestAnimationFrame(() => element.classList.add("visible"));""", "js",
             "Trois techniques de performance DOM"),
        table(["Pratique", "Coût", "Alternative"],
              [["`innerHTML +=` en boucle", "Élevé", "Fragment ou une seule chaîne"],
               ["Styles en ligne successifs", "Élevé", "Une classe"],
               ["Lecture/écriture alternées", "Très élevé", "Regrouper les phases"],
               ["Écouteurs sur mille éléments", "Élevé", "Délégation d'événements"]],
              widths=[4.2, 2.6, 4.2], first_col_bold=True,
              caption="Quatre pratiques coûteuses et leur alternative"),
        box("methode", "Trois vérifications après une manipulation",
            items=["L'ordre du DOM correspond-il à l'ordre visuel ?",
                   "Les attributs ARIA sont-ils à jour (`aria-expanded`, `aria-hidden`) ?",
                   "Le focus reste-t-il au bon endroit ?"]),
    ],
    "keypoints": [
        "Le DOM est un arbre vivant, distinct du fichier HTML.",
        "`querySelectorAll` renvoie une liste statique.",
        "`textContent` est sûr, `innerHTML` interprète le HTML.",
        "`classList` évite d'écraser les classes existantes.",
        "Les attributs `data-*` forment un contrat clair avec le CSS.",
        "Les modifications groupées évitent les recalculs de mise en page.",
        "Une manipulation visuelle doit préserver l'accessibilité.",
    ],
    "bridge": "La page peut être modifiée. Le chapitre suivant ajoute la réaction aux "
              "actions de l'utilisateur : les événements.",
    "exercises": [
        ex("Construire une liste depuis des données",
           "Affichez un tableau d'objets dans une liste, en toute sécurité.",
           ["Utilisez un fragment.",
            "Échappez les données utilisateur.",
            "Ajoutez une classe sur les éléments pairs."],
           [("code", """const contacts = [
  { nom: "Ada", email: "ada@exemple.fr" },
  { nom: "Grace", email: "grace@exemple.fr" },
];

const liste = document.querySelector("#contacts");
const fragment = document.createDocumentFragment();

contacts.forEach((contact, index) => {
  const li = document.createElement("li");
  li.className = "contact";
  if (index % 2 === 1) li.classList.add("contact--pair");

  const nom = document.createElement("strong");
  nom.textContent = contact.nom;

  const lien = document.createElement("a");
  lien.href = `mailto:${contact.email}`;
  lien.textContent = contact.email;

  li.append(nom, " ", lien);
  fragment.append(li);
});

liste.append(fragment);"""),
            "`textContent` empêche toute injection, même si le nom contient des "
            "balises.",
            "Le fragment n'est inséré qu'une fois : un seul recalcul de mise en page "
            "pour N éléments."]),
        ex("Basculer un panneau accessible",
           "Un bouton ouvre et ferme un panneau. L'état doit être annoncé.",
           ["Mettez à jour `aria-expanded`.",
            "Affichez ou masquez le panneau.",
            "Gardez le focus cohérent."],
           [("code", """const bouton = document.querySelector("#basculer");
const panneau = document.querySelector("#panneau");

bouton.addEventListener("click", () => {
  const ouvert = bouton.getAttribute("aria-expanded") === "true";
  bouton.setAttribute("aria-expanded", String(!ouvert));
  panneau.hidden = ouvert;
});"""),
            "`aria-expanded` reflète l'état ouvert/fermé, et l'attribut `hidden` "
            "supprime réellement le panneau de l'arbre d'accessibilité.",
            "Si le panneau contient un formulaire, veillez à ce que le focus ne reste "
            "pas dans un élément masqué."]),
        ex("Optimiser une liste de mille éléments",
           "Une liste est reconstruite à chaque frappe dans un champ de recherche.",
           ["Identifiez le coût actuel.",
            "Proposez une solution avec fragment.",
            "Ajoutez un anti-rebond (debounce)."],
           [("code", """function afficher(items) {
  const fragment = document.createDocumentFragment();
  for (const item of items) {
    const li = document.createElement("li");
    li.textContent = item.nom;
    fragment.append(li);
  }
  liste.replaceChildren(fragment);
}

let minuteur;
champ.addEventListener("input", (e) => {
  clearTimeout(minuteur);
  minuteur = setTimeout(() => {
    afficher(filtrer(e.target.value));
  }, 200);
});"""),
            "`replaceChildren` vide et remplit en une opération, au lieu d'une boucle de "
            "suppressions.",
            "L'anti-rebond évite de reconstruire la liste à chaque caractère : la "
            "recherche s'exécute 200 ms après la dernière frappe."],
           level="Performance"),
    ],
    "quiz": [
        quiz("Quelle propriété insère du texte sans interpréter le HTML ?",
             ["`innerHTML`", "`textContent`", "`outerHTML`", "`insertAdjacentHTML`"],
             1,
             "`textContent` traite la valeur comme du texte brut, ce qui empêche les "
             "injections."),
        quiz("`querySelectorAll` renvoie-t-il une liste vivante ?",
             ["Oui", "Non, elle est statique", "Seulement en mode strict", "Cela dépend du navigateur"],
             1,
             "La `NodeList` est figée au moment de l'appel ; `getElementsByClassName` "
             "renvoie au contraire une collection vivante."),
        quiz("Que fait `classList.toggle(\"ouvert\", true)` ?",
             ["Ajoute la classe", "Retire la classe", "Ajoute si absent, retire si présent",
              "Remplace toutes les classes"],
             0,
             "Le second argument force l'ajout (true) ou le retrait (false) ; sans lui, "
             "la méthode bascule."),
        quiz("Pourquoi utiliser un `DocumentFragment` ?",
             ["Pour sécuriser le HTML", "Pour éviter un recalcul par insertion",
              "Pour créer un fichier", "Pour trier les éléments"],
             1,
             "Les insertions se font hors du document, puis une seule opération "
             "raccorde l'ensemble."),
        quiz("Que devient un élément retiré du DOM mais référencé par une variable ?",
             ["Il est détruit immédiatement", "Il reste en mémoire",
              "Il revient dans le DOM", "Il provoque une erreur"],
             1,
             "Tant qu'une référence existe, l'élément n'est pas libéré : c'est une fuite "
             "mémoire potentielle."),
    ],
}
