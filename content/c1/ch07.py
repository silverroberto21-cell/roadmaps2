from bookkit.dsl import (box, code, defn, ex, fig, h, ol, p, quiz, table, ul)

CH = {
    "title": "Tableaux de données",
    "subtitle": "Un tableau sert à croiser des données. Tout le reste n'est pas un "
                "tableau, et le confondre coûte cher.",
    "duration": "2 h 00",
    "level": "Débutant",
    "prereq": "chapitre 6",
    "objectives": [
        "Distinguer un tableau de données d'une mise en page tabulaire.",
        "Construire un tableau accessible avec titre, en-têtes et portées.",
        "Fusionner des cellules sans casser la lecture assistée.",
        "Adapter un tableau large aux petits écrans.",
        "Choisir entre tableau HTML, liste et composant CSS.",
    ],
    "blocks": [
        h(2, "Un tableau, c'est des données croisées"),
        p("Un tableau associe des valeurs à deux dimensions : des lignes et des "
          "colonnes. Un horaire de train, un comparatif de tarifs, un relevé de notes "
          "sont des tableaux. Une grille de cartes, une galerie, une mise en page à "
          "trois colonnes n'en sont pas."),
        p("Pendant vingt ans, les tableaux ont servi à mettre en page. Cette époque "
          "est révolue : CSS Grid et Flexbox font cela mieux, et un lecteur d'écran "
          "annonce désormais « tableau de 12 lignes, 3 colonnes » à chaque mise en "
          "page mal placée, ce qui désoriente profondément."),
        fig("compare", "Tableau ou grille ?",
            ("TABLEAU DE DONNÉES", ["Chaque cellule a un sens", "Les colonnes ont un en-tête",
                                    "Le lecteur compare des valeurs"],
             "GRILLE DE MISE EN PAGE", ["Disposition visuelle", "Aucune relation de données",
                                        "Le CSS suffit"]),
            height=205),
        h(3, "Ce qu'un lecteur d'écran annonce"),
        p("Face à un tableau, un lecteur d'écran peut annoncer la position et "
          "l'en-tête de la cellule courante : « ligne 3, colonne 2, tarif mensuel, "
          "19 euros ». Cette restitution dépend entièrement de la qualité du balisage."),
        code("""<!-- Annonce possible : « ligne 2, colonne 3, Prix, 19 € » -->
<table>
  <caption>Tarifs des offres 2026</caption>
  <thead>
    <tr>
      <th scope="col">Offre</th>
      <th scope="col">Stockage</th>
      <th scope="col">Prix</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th scope="row">Essentiel</th>
      <td>10 Go</td>
      <td>4 €</td>
    </tr>
    <tr>
      <th scope="row">Confort</th>
      <td>100 Go</td>
      <td>19 €</td>
    </tr>
  </tbody>
</table>""", "html", "Le tableau de référence : titre, en-têtes de colonnes et de lignes"),
        table(["Élément", "Rôle", "Obligatoire"],
              [["`caption`", "Titre du tableau", "Fortement recommandé"],
               ["`thead`", "Ligne(s) d'en-tête", "Oui pour les données"],
               ["`tbody`", "Corps du tableau", "Facultatif mais clair"],
               ["`tfoot`", "Pied, totaux", "Facultatif"],
               ["`tr`", "Ligne", "Oui"],
               ["`th`", "Cellule d'en-tête", "Oui pour les en-têtes"],
               ["`td`", "Cellule de données", "Oui"],
               ["`scope=\"col\"` / `\"row\"`", "Portée de l'en-tête", "Oui pour les en-têtes"]],
              widths=[3.6, 4.4, 4.0], first_col_bold=True,
              caption="Les éléments d'un tableau HTML et leur rôle"),

        h(2, "Construire un tableau lisible"),
        p("Un tableau de données doit rester compréhensible sans CSS. C'est le test "
          "décisif : sans styles, l'ordre de lecture doit être logique, les en-têtes "
          "identifiables et les unités présentes."),
        code("""<table>
  <caption>Consommation électrique mensuelle (kWh)</caption>
  <thead>
    <tr>
      <th scope="col">Mois</th>
      <th scope="col">2025</th>
      <th scope="col">2026</th>
      <th scope="col">Écart</th>
    </tr>
  </thead>
  <tbody>
    <tr><th scope="row">Janvier</th><td>412</td><td>398</td><td>−3,4 %</td></tr>
    <tr><th scope="row">Février</th><td>389</td><td>370</td><td>−4,9 %</td></tr>
  </tbody>
  <tfoot>
    <tr><th scope="row">Total</th><td>801</td><td>768</td><td>−4,1 %</td></tr>
  </tfoot>
</table>""", "html", "Un tableau complet, avec en-têtes de lignes et totaux"),
        p("Le signe moins typographique `−` (U+2212) se distingue du trait d'union ; "
          "il s'aligne mieux avec les chiffres. Les nombres restent alignés à droite "
          "en CSS, les textes à gauche : l'œil compare alors les ordres de grandeur."),
        code("""table {
  border-collapse: collapse;
  width: 100%;
  font-variant-numeric: tabular-nums;
}
caption { text-align: left; font-weight: 700; padding-bottom: .5rem; }
th, td { padding: .5rem .75rem; border-bottom: 1px solid #d5dee6; }
th { text-align: left; background: #e8edf1; }
td { text-align: right; }
td:first-child, th[scope="row"] { text-align: left; }""", "css",
             "Un tableau lisible, sans artifice"),
        box("attention", "Ne jamais utiliser de tableau pour la mise en page",
            "Si vous vous surprenez à écrire `<table>` pour aligner deux blocs, "
            "arrêtez-vous : utilisez `display: grid` ou `flex`. Le tableau restera "
            "annoncé comme tel par les technologies d'assistance, et la page "
            "deviendra incompréhensible sans CSS."),

        h(2, "Fusion de cellules"),
        p("`colspan` fusionne des cellules horizontalement, `rowspan` verticalement. "
          "Ces attributs compliquent la lecture assistée : à utiliser avec parcimonie "
          "et toujours avec des en-têtes explicites."),
        code("""<table>
  <caption>Horaires des ateliers</caption>
  <thead>
    <tr>
      <th scope="col">Jour</th>
      <th scope="col">Matin</th>
      <th scope="col">Après-midi</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th scope="row">Lundi</th>
      <td colspan="2">Journée d'intégration</td>
    </tr>
    <tr>
      <th scope="row">Mardi</th>
      <td>HTML</td>
      <td>CSS</td>
    </tr>
  </tbody>
</table>""", "html", "Une fusion horizontale lisible"),
        p("Une fusion verticale (`rowspan`) qui traverse plusieurs lignes est souvent "
          "le signe qu'un tableau plus simple serait possible. Si elle est "
          "indispensable, ajoutez des identifiants et `headers` sur les cellules "
          "concernées :"),
        code("""<tr>
  <th id="t1" scope="rowgroup" rowspan="2">Trimestre 1</th>
  <td headers="t1">Janvier</td>
</tr>
<tr>
  <td headers="t1">Février</td>
</tr>""", "html", "Un en-tête fusionné, relié explicitement aux cellules"),

        h(2, "Tableaux et petits écrans"),
        p("Un tableau de six colonnes ne tient pas sur un téléphone. Trois stratégies "
          "existent, à choisir selon la nature des données."),
        table(["Stratégie", "Principe", "Quand l'utiliser"],
              [["Défilement horizontal", "Le tableau garde sa structure, on fait défiler", "Peu de lignes, beaucoup de colonnes"],
               ["Empilement", "Chaque ligne devient une fiche", "Données hétérogènes"],
               ["Priorisation", "Certaines colonnes sont masquées", "Colonnes secondaires"]],
              widths=[3.2, 4.6, 4.2], first_col_bold=True,
              caption="Trois façons d'adapter un tableau au mobile"),
        code("""<div class="tableau-defilant" tabindex="0" role="region"
     aria-label="Consommation électrique mensuelle, tableau défilant">
  <table>...</table>
</div>""", "html", "Un conteneur défilant accessible au clavier"),
        code(""".tableau-defilant { overflow-x: auto; }
.tableau-defilant:focus-visible { outline: 3px solid #e0a21b; }

@media (max-width: 40rem) {
  .tableau-defilant table { min-width: 34rem; }
}""", "css", "Défilement horizontal, focus visible"),
        p("Le `tabindex=\"0\"` rend la zone défilante accessible au clavier : sans "
          "lui, un utilisateur qui ne peut pas utiliser la souris ne peut pas voir "
          "les colonnes cachées. C'est un détail que la plupart des sites oublient."),

        h(2, "Tableau, liste ou composant ?"),
        p("Avant d'écrire `<table>`, posez la question : les données ont-elles deux "
          "dimensions ? Si la réponse est non, un autre élément convient."),
        table(["Besoin", "Bonne solution", "Mauvaise solution"],
              [["Comparer des offres sur trois critères", "Tableau", "Cartes empilées"],
               ["Afficher une liste de courses", "`ul`", "Tableau à une colonne"],
               ["Présenter une fiche produit", "`article` + `dl`", "Tableau de mise en page"],
               ["Afficher un calendrier", "Grille CSS", "Tableau si les dates sont des données"],
               ["Aligner deux colonnes", "`grid`", "Tableau"]]),
        p("Le calendrier illustre le cas limite : s'il s'agit d'un sélecteur de dates, "
          "c'est une grille interactive ; s'il s'agit d'un planning consultable avec "
          "des ressources en lignes et des jours en colonnes, c'est un tableau."),
        box("methode", "Test des trois secondes",
            "Cachez le CSS. Si le contenu se lit encore dans l'ordre attendu et que "
            "les en-têtes restent compréhensibles, le tableau est correct. Sinon, "
            "c'est une mise en page déguisée."),
    ],
    "keypoints": [
        "Un tableau croise des données ; il ne met pas en page.",
        "`caption` donne un titre, `th` et `scope` donnent le sens.",
        "Les en-têtes de lignes sont aussi importants que ceux des colonnes.",
        "`colspan` et `rowspan` compliquent la lecture : à limiter.",
        "Sur mobile, préférer le défilement horizontal accessible au clavier.",
        "Sans CSS, un bon tableau reste compréhensible.",
    ],
    "bridge": "Les données sont structurées. Place à l'interaction : les formulaires, "
              "point de contact entre l'utilisateur et le système.",
    "exercises": [
        ex("Comparer trois offres",
           "Construisez un tableau comparant trois offres d'hébergement sur quatre "
           "critères : prix, stockage, bande passante, support.",
           ["Ajoutez un titre de tableau et des en-têtes de colonnes.",
            "Indiquez la meilleure offre par un moyen non visuel.",
            "Ajoutez un pied de tableau avec la mention des tarifs annuels."],
           [("code", """<table>
  <caption>Comparatif des offres d'hébergement (tarifs mensuels)</caption>
  <thead>
    <tr>
      <th scope="col">Critère</th>
      <th scope="col">Essentiel</th>
      <th scope="col">Pro</th>
      <th scope="col">Entreprise</th>
    </tr>
  </thead>
  <tbody>
    <tr><th scope="row">Prix</th><td>4 €</td><td>12 €</td><td>39 €</td></tr>
    <tr><th scope="row">Stockage</th><td>10 Go</td><td>100 Go</td><td>500 Go</td></tr>
    <tr><th scope="row">Bande passante</th><td>Illimitée</td><td>Illimitée</td><td>Illimitée</td></tr>
    <tr><th scope="row">Support</th><td>E-mail</td><td>E-mail 24 h</td><td>Téléphone 24/7</td></tr>
  </tbody>
  <tfoot>
    <tr><th scope="row" colspan="4">Tarifs annuels, hors taxes.</th></tr>
  </tfoot>
</table>"""),
            "La « meilleure » offre ne doit pas être signalée par la couleur seule : "
            "ajoutez un texte (« recommandé ») ou un symbole explicité, sinon "
            "l'information disparaît pour une partie des lecteurs.",
            "Le pied de tableau porte les mentions générales. Attention : une cellule "
            "fusionnée sur quatre colonnes doit rester lisible ; préférez parfois un "
            "paragraphe après le tableau."]),
        ex("Réparer un tableau inaccessible",
           "Ce tableau utilise des `td` partout et n'a ni titre ni en-tête.",
           ["Identifiez les cellules qui devraient être des `th`.",
            "Ajoutez un `caption` et les `scope` nécessaires.",
            "Proposez une version accessible au clavier sur mobile."],
           [("code", """<table>
  <caption>Résultats du contrôle technique</caption>
  <thead>
    <tr>
      <th scope="col">Véhicule</th>
      <th scope="col">Date</th>
      <th scope="col">Résultat</th>
    </tr>
  </thead>
  <tbody>
    <tr><th scope="row">AB-123-CD</th><td>12/03/2026</td><td>Favorable</td></tr>
    <tr><th scope="row">EF-456-GH</th><td>14/03/2026</td><td>Défavorable</td></tr>
  </tbody>
</table>"""),
            "Les cellules de la première colonne décrivent la ligne : ce sont des "
            "en-têtes de ligne, donc des `th` avec `scope=\"row\"`.",
            "Sur mobile, enveloppez le tableau dans une région défilante avec "
            "`tabindex=\"0\"` et un `aria-label` décrivant le contenu, puis "
            "autorisez le défilement horizontal en CSS."],
           level="Diagnostic"),
        ex("Choisir la bonne structure",
           "Pour chaque cas, indiquez la structure HTML appropriée et justifiez.",
           ["Une grille de tarifs à trois colonnes.",
            "Un planning de salles sur une semaine.",
            "Une fiche technique de produit.",
            "Une galerie de photos."],
           ["Une grille de tarifs compare des offres sur des critères : tableau, sauf "
            "si chaque offre contient beaucoup de texte, auquel cas des `article` "
            "comparés par une liste de définitions sont plus lisibles.",
            "Un planning croise des salles et des jours : tableau, avec en-têtes de "
            "colonnes (jours) et de lignes (salles).",
            "Une fiche technique est une suite de couples propriété/valeur : `dl`.",
            "Une galerie est une collection d'images autonomes : `ul` de `figure`, "
            "ou `div` si l'ordre n'a pas de sens."],
           level="Analyse"),
    ],
    "quiz": [
        quiz("Quel élément donne un titre à un tableau ?",
             ["`title`", "`caption`", "`thead`", "`h2`"],
             1,
             "`caption` est le titre natif du tableau ; il doit être le premier "
             "élément enfant de `table`."),
        quiz("À quoi sert `scope=\"col\"` sur une cellule `th` ?",
             ["À fusionner deux colonnes",
              "À indiquer que l'en-tête s'applique à la colonne",
              "À colorer la colonne",
              "À trier la colonne"],
             1,
             "`scope` déclare la portée de l'en-tête, ce qui permet aux lecteurs "
             "d'écran d'annoncer la bonne étiquette pour chaque cellule."),
        quiz("Pourquoi ne pas utiliser de tableau pour la mise en page ?",
             ["Le HTML devient invalide",
              "Les technologies d'assistance annoncent une structure de données inexistante",
              "Les tableaux sont obsolètes",
              "Cela empêche l'impression"],
             1,
             "Le tableau est un objet sémantique : l'utiliser pour la mise en page "
             "produit des annonces trompeuses et un ordre de lecture incohérent."),
        quiz("Quelle propriété CSS permet le défilement horizontal d'un tableau large ?",
             ["`overflow-x: auto`", "`display: block`", "`table-layout: fixed`", "`white-space: nowrap`"],
             0,
             "`overflow-x: auto` sur un conteneur permet le défilement ; ajoutez "
             "`tabindex=\"0\"` pour l'accès au clavier."),
        quiz("Combien de `caption` peut contenir un tableau ?",
             ["Aucun", "Un seul", "Un par section", "Autant que de colonnes"],
             1,
             "Un tableau possède au plus un `caption`, placé en premier."),
    ],
}
