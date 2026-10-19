from bookkit.dsl import (box, code, defn, ex, fig, h, ol, p, quiz, table, ul)

CH = {
    "title": "Tableaux de données et listes longues",
    "subtitle": "Afficher, trier et filtrer des centaines de lignes sans perdre ni "
                "l'accessibilité ni la fluidité.",
    "duration": "3 h 00",
    "level": "Avancé",
    "prereq": "chapitres 8, 23 et 25",
    "objectives": [
        "Choisir entre tableau et liste.",
        "Rendre un tableau triable et accessible.",
        "Filtrer sans bloquer l'interface.",
        "Afficher un grand volume sans ralentir.",
        "Prévoir les états vides et les erreurs.",
    ],
    "blocks": [
        h(2, "Tableau ou liste ?"),
        p("Un tableau sert à comparer des valeurs sur plusieurs colonnes. Une liste sert à "
          "parcourir des objets. Utiliser un tableau pour trois champs et deux lignes "
          "alourdit la lecture sur mobile."),
        table(["Besoin", "Structure", "Raison"],
              [["Comparer des montants", "Tableau", "Alignement des colonnes"],
               ["Parcourir des articles", "Liste", "Lecture verticale"],
               ["Afficher des statuts", "Liste avec badges", "Hiérarchie visuelle"],
               ["Trier sur plusieurs colonnes", "Tableau", "En-têtes interactifs"]],
              widths=[5.0, 4.2, 4.8], first_col_bold=True,
              caption="Quatre besoins"),
        code("""<!-- Tableau de données avec légende et en-têtes explicites -->
<table>
  <caption>Commandes de la semaine</caption>
  <thead>
    <tr>
      <th scope="col">Numéro</th>
      <th scope="col">Client</th>
      <th scope="col" class="nombre">Montant</th>
      <th scope="col">Statut</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th scope="row">CMD-1042</th>
      <td>Awa Diallo</td>
      <td class="nombre">124,50 €</td>
      <td><span class="badge badge--payee">Payée</span></td>
    </tr>
  </tbody>
</table>""", "html", "Un tableau sémantique"),
        table(["Élément", "Rôle", "Erreur fréquente"],
              [["`<caption>`", "Titre du tableau", "Absent"],
               ["`scope=\"col\"`", "En-tête de colonne", "`<td>` en en-tête"],
               ["`scope=\"row\"`", "En-tête de ligne", "Confondu avec une donnée"],
               ["`class=\"nombre\"`", "Alignement à droite", "Chiffres non alignés"],
               ["`<tbody>`", "Corps du tableau", "Mélangé aux en-têtes"]],
              widths=[4.4, 4.8, 4.8], first_col_bold=True,
              caption="Cinq éléments"),
        box("attention", "Un tableau de mise en page reste un tableau pour un lecteur d'écran",
            "Utiliser un tableau pour disposer des blocs produit une lecture absurde. Pour "
            "la mise en page, utilisez CSS Grid ou Flexbox."),

        h(2, "Tri accessible"),
        p("Un tri interactif doit être annoncé et commandable au clavier. L'attribut "
          "`aria-sort` indique la colonne active et le sens."),
        code("""<th scope="col" aria-sort="ascending">
  <button type="button" data-tri="montant">
    Montant <span aria-hidden="true">▲</span>
  </button>
</th>""", "html", "Un en-tête triable"),
        code("""const boutons = document.querySelectorAll("[data-tri]");

boutons.forEach((bouton) => {
  bouton.addEventListener("click", () => {
    const cle = bouton.dataset.tri;
    const entete = bouton.closest("th");
    const sens = entete.getAttribute("aria-sort") === "ascending" ? "descending" : "ascending";

    document.querySelectorAll("th[aria-sort]").forEach((th) => {
      if (th !== entete) th.removeAttribute("aria-sort");
    });
    entete.setAttribute("aria-sort", sens);

    trierLignes(cle, sens);
  });
});

function trierLignes(cle, sens) {
  const corps = document.querySelector("tbody");
  const lignes = [...corps.rows];
  lignes.sort((a, b) => {
    const va = a.querySelector(`[data-cle="${cle}"]`).dataset.valeur;
    const vb = b.querySelector(`[data-cle="${cle}"]`).dataset.valeur;
    const cmp = Number(va) - Number(vb);
    return sens === "ascending" ? cmp : -cmp;
  });
  lignes.forEach((ligne) => corps.append(ligne));
}""", "js", "Un tri réel"),
        box("pratique", "Triez sur la valeur, pas sur le texte affiché",
            "« 9,50 € » se classe après « 124,50 € » en ordre alphabétique. Conservez la "
            "valeur brute dans un attribut et formatez seulement à l'affichage."),
        defn("`aria-sort`", "Attribut posé sur l'en-tête de la colonne triée, valant "
                            "`ascending`, `descending`, `none` ou `other`. Il évite de "
                            "deviner l'état à partir d'une icône."),

        h(2, "Filtrer"),
        p("Un filtre doit répondre vite, même sur plusieurs centaines d'éléments. Le "
          "retard (debounce) évite de recalculer à chaque frappe ; l'affichage du nombre "
          "de résultats évite l'incertitude."),
        code("""const champ = document.querySelector("#recherche");
const compteur = document.querySelector("#compteur");
const lignes = [...document.querySelectorAll("tbody tr")];

function filtrer(texte) {
  const requete = texte.trim().toLowerCase();
  let visibles = 0;

  lignes.forEach((ligne) => {
    const correspond = ligne.textContent.toLowerCase().includes(requete);
    ligne.hidden = !correspond;
    if (correspond) visibles += 1;
  });

  compteur.textContent = visibles === 1
    ? "1 résultat"
    : `${visibles} résultats`;

  document.querySelector("#vide").hidden = visibles !== 0;
}

let minuteur;
champ.addEventListener("input", (e) => {
  clearTimeout(minuteur);
  minuteur = setTimeout(() => filtrer(e.target.value), 150);
});""", "js", "Un filtre avec délai"),
        table(["Réglage", "Effet", "Valeur usuelle"],
              [["Délai de frappe", "Moins de calculs", "150 à 250 ms"],
               ["Nombre de résultats", "Repère pour l'utilisateur", "Toujours"],
               ["État vide", "Évite l'impression de panne", "Message et action"],
               ["Réinitialisation", "Sortie du filtre", "Bouton visible"]],
              widths=[4.6, 4.6, 4.8], first_col_bold=True,
              caption="Quatre réglages"),
        code("""<!-- Annonce discrète du nombre de résultats -->
<p id="compteur" role="status" aria-live="polite">24 résultats</p>

<!-- État vide utile -->
<div id="vide" hidden>
  <p>Aucune commande ne correspond à « <span id="terme"></span> ».</p>
  <button type="button" id="reinitialiser">Effacer le filtre</button>
</div>""", "html", "Deux éléments d'interface"),
        box("attention", "`aria-live` trop bavard fatigue",
            "Annoncer chaque frappe sature le lecteur d'écran. Annoncez uniquement le "
            "nombre final après le délai, et jamais les deux à la fois."),

        h(2, "Grands volumes"),
        p("Afficher dix mille lignes dans le DOM ralentit le navigateur. Deux approches "
          "existent : la pagination, plus simple, et la virtualisation, plus fluide mais "
          "plus complexe."),
        fig("compare", "Deux approches",
            ("PAGINATION", ["Simple à implémenter", "Repères stables",
                            "Changement de page"],
             "VIRTUALISATION", ["Défilement continu", "DOM constant",
                                "Complexité et repères instables"]),
            height=210),
        code("""<!-- Pagination accessible -->
<nav aria-label="Pagination des commandes">
  <button type="button" disabled aria-label="Page précédente">‹</button>
  <span>Page 2 sur 12</span>
  <button type="button" aria-label="Page suivante">›</button>
</nav>""", "html", "Une pagination lisible"),
        code("""// Rendu virtualisé simple : ne conserver que la fenêtre visible
const HAUTEUR = 44;

function rendreFenetre(conteneur, donnees, defilement) {
  const debut = Math.max(0, Math.floor(defilement / HAUTEUR) - 5);
  const fin = Math.min(donnees.length, debut + 30);

  conteneur.style.height = `${donnees.length * HAUTEUR}px`;
  conteneur.replaceChildren(
    ...donnees.slice(debut, fin).map((d, i) => creerLigne(d, (debut + i) * HAUTEUR))
  );
}""", "js", "Une fenêtre de rendu"),
        table(["Volume", "Approche", "Justification"],
              [["< 200 lignes", "Rendu complet", "Simple et rapide"],
               ["200 à 2 000", "Pagination", "Lisibilité et repères"],
               ["> 2 000", "Virtualisation", "DOM constant"],
               ["Défilement infini", "Chargement progressif", "Usage mobile"]],
              widths=[4.4, 4.8, 5.0], first_col_bold=True,
              caption="Quatre volumes"),
        box("pratique", "Le défilement infini complique la reprise",
            "Un utilisateur qui revient en arrière perd sa position et son contexte. La "
            "pagination reste plus prévisible, sauf pour un fil d'actualité."),

        h(2, "États et robustesse"),
        p("Une liste doit gérer quatre états, souvent oubliés : chargement, vide, erreur "
          "et résultat partiel. Les afficher explicitement évite les confusions."),
        table(["État", "Affichage", "Erreur évitée"],
              [["Chargement", "Squelette ou indicateur", "Page blanche"],
               ["Vide", "Message et action", "Impression de panne"],
               ["Erreur", "Message et réessai", "Silence"],
               ["Partiel", "Bandeau d'avertissement", "Données incomplètes"]],
              widths=[3.6, 5.2, 5.2], first_col_bold=True,
              caption="Quatre états"),
        code("""<!-- Squelette pendant le chargement, remplacé ensuite -->
<div id="liste" aria-busy="true" aria-live="polite">
  <div class="squelette" aria-hidden="true"></div>
  <div class="squelette" aria-hidden="true"></div>
</div>

<!-- Après chargement -->
<script>
  liste.setAttribute("aria-busy", "false");
</script>""", "html", "Un chargement annoncé"),
        box("methode", "Afficher des données tabulaires",
            items=["Choisir tableau ou liste selon la comparaison à faire.",
                   "Déclarer `caption`, `scope` et l'alignement des nombres.",
                   "Trier sur la valeur brute et annoncer avec `aria-sort`.",
                   "Filtrer avec un délai et afficher le nombre de résultats.",
                   "Prévoir chargement, vide, erreur et résultat partiel."]),
    ],
    "keypoints": [
        "Un tableau compare, une liste parcourt.",
        "`caption` et `scope` rendent un tableau compréhensible.",
        "Un tableau de mise en page est une erreur d'accessibilité.",
        "`aria-sort` annonce la colonne et le sens du tri.",
        "Le tri doit porter sur la valeur brute.",
        "Un filtre se temporise et affiche son nombre de résultats.",
        "Au-delà de deux mille lignes, la virtualisation devient nécessaire.",
        "Quatre états doivent être prévus : chargement, vide, erreur, partiel.",
    ],
    "bridge": "Vous savez présenter des données. Le volume se referme sur ses annexes.",
    "exercises": [
        ex("Rendre un tableau accessible",
           "Un tableau de factures n'a ni titre ni en-têtes déclarés.",
           ["Ajoutez une légende.",
            "Déclarez les en-têtes.",
            "Alignez les montants."],
           [("html", """<table>
  <caption>Factures de septembre 2026</caption>
  <thead>
    <tr>
      <th scope="col">Numéro</th>
      <th scope="col">Échéance</th>
      <th scope="col" class="nombre">Montant</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th scope="row">F-2026-091</th>
      <td>30 septembre 2026</td>
      <td class="nombre">1 240,00 €</td>
    </tr>
  </tbody>
</table>"""),
            "Le numéro de facture est un en-tête de ligne : il identifie la ligne.",
            "`class=\"nombre\"` avec `text-align: right` et `font-variant-numeric: "
            "tabular-nums` aligne les chiffres."]),
        ex("Trier sans casser l'accessibilité",
           "Le tri par montant classe mal les nombres.",
           ["Stockez la valeur brute.",
            "Triez numériquement.",
            "Mettez à jour `aria-sort`."],
           [("js", """// Chaque cellule porte la valeur brute
// <td class="nombre" data-cle="montant" data-valeur="1240">1 240,00 €</td>

function trier(cle, sens) {
  const corps = document.querySelector("tbody");
  [...corps.rows]
    .sort((a, b) => {
      const va = Number(a.querySelector(`[data-cle="${cle}"]`).dataset.valeur);
      const vb = Number(b.querySelector(`[data-cle="${cle}"]`).dataset.valeur);
      return sens === "ascending" ? va - vb : vb - va;
    })
    .forEach((r) => corps.append(r));
}"""),
            "Le texte affiché contient des espaces insécables et un symbole monétaire : "
            "le tri alphabétique échoue.",
            "Un seul en-tête porte `aria-sort` à la fois."],
           level="Accessibilité"),
        ex("Choisir une stratégie d'affichage",
           "Une page affiche 8 000 commandes.",
           ["Évaluez les volumes.",
            "Comparez les approches.",
            "Justifiez."],
           ["8 000 lignes en rendu complet : plusieurs secondes de blocage du fil principal.",
            "Pagination de 50 lignes : simple, prévisible, coût constant.",
            "Virtualisation : utile si le défilement continu est une exigence produit.",
            "Décision : pagination côté serveur avec filtre et tri également côté serveur."],
           level="Architecture"),
    ],
    "quiz": [
        quiz("Quand préférer une liste à un tableau ?",
             ["Pour comparer des montants", "Pour parcourir des objets",
              "Pour trier", "Pour paginer"],
             1,
             "Une liste se lit verticalement, sans colonnes à comparer."),
        quiz("Que déclare `scope=\"row\"` ?",
             ["Une colonne", "Un en-tête de ligne", "Une légende", "Un groupe"],
             1,
             "Il identifie la ligne pour les technologies d'assistance."),
        quiz("Que fait `aria-sort` ?",
             ["Trie réellement", "Annonce la colonne et le sens triés",
              "Masque la colonne", "Désactive le tri"],
             1,
             "Le tri doit être implémenté en JavaScript ou côté serveur."),
        quiz("Pourquoi temporiser un filtre ?",
             ["Pour la sécurité", "Pour éviter de recalculer à chaque frappe",
              "Pour le cache", "Pour l'accessibilité"],
             1,
             "Un délai de 150 à 250 ms suffit à réduire la charge."),
        quiz("Quel état est souvent oublié ?",
             ["Le chargement", "L'état vide", "Le résultat partiel", "La page d'accueil"],
             2,
             "Un résultat partiel affiché sans avertissement induit en erreur."),
    ],
}
