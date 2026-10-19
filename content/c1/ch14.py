from bookkit.dsl import (box, code, defn, ex, fig, h, ol, p, quiz, table, ul)

CH = {
    "title": "Bordures, ombres et profondeur",
    "subtitle": "Donner du relief sans surcharger : les outils visuels qui séparent, "
                "hiérarchisent et guident le regard.",
    "duration": "2 h 15",
    "level": "Débutant",
    "prereq": "chapitre 13",
    "objectives": [
        "Composer des bordures cohérentes et accessibles au focus.",
        "Utiliser les rayons et les ombres avec discernement.",
        "Créer une hiérarchie visuelle par la profondeur.",
        "Éviter les effets qui nuisent à la lisibilité.",
        "Adapter les effets au mode sombre et au contraste élevé.",
    ],
    "blocks": [
        h(2, "Bordures : délimiter sans alourdir"),
        p("Une bordure sépare deux zones. Elle occupe de l'espace dans la boîte "
          "(contrairement à `outline`) et se compose d'une épaisseur, d'un style et "
          "d'une couleur. Le style `solid` suffit dans la majorité des cas."),
        code(""".carte   { border: 1px solid #e8edf1; }
.alerte  { border-inline-start: 4px solid #a63a32; }
.bouton  { border: 2px solid currentColor; }
.separe  { border-block-end: 1px solid #d5dee6; }

/* Bordure en pointillés pour une zone de dépôt */
.depot   { border: 2px dashed #c9d6e2; border-radius: 8px; }""", "css",
             "Quatre usages de la bordure"),
        table(["Propriété", "Rôle", "Remarque"],
              [["`border-width`", "Épaisseur", "1 px suffit pour séparer"],
               ["`border-style`", "Trait", "`solid`, `dashed`, `dotted`"],
               ["`border-color`", "Couleur", "Souvent une nuance de neutre"],
               ["`border-radius`", "Arrondi", "Un seul rayon crée une identité"],
               ["`outline`", "Contour de focus", "Hors du flux, ne décale rien"],
               ["`outline-offset`", "Écart du contour", "Améliore la visibilité"]],
              widths=[3.2, 3.4, 4.6], first_col_bold=True,
              caption="Six propriétés de contour"),
        code(""":focus-visible {
  outline: 3px solid #e0a21b;
  outline-offset: 3px;
  border-radius: 2px;
}""", "css", "Un focus visible sur tous les fonds"),
        box("attention", "`outline: none` sans remplacement",
            "Supprimer le contour de focus est l'une des erreurs d'accessibilité les "
            "plus fréquentes. Si le contour natif est inesthétique, remplacez-le par "
            "un `outline` personnalisé ou un `box-shadow`, jamais par rien."),
        p("Les rayons se déclarent de façon homogène (`border-radius: 8px`) ou "
          "asymétrique (`border-radius: 16px 16px 0 0`). Un rayon trop grand sur un "
          "petit élément produit une forme de pilule involontaire ; utilisez "
          "`border-radius: 999px` uniquement quand c'est l'effet recherché."),

        h(2, "Ombres : une illusion de profondeur"),
        p("Une ombre simule une source de lumière. Deux paramètres déterminent sa "
          "crédibilité : le décalage vertical (plus l'ombre est haute, plus l'objet "
          "semble proche du support) et le flou (plus il est grand, plus l'objet semble "
          "loin)."),
        code(""".niveau-1 { box-shadow: 0 1px 2px rgb(15 46 76 / 8%); }
.niveau-2 { box-shadow: 0 4px 8px rgb(15 46 76 / 10%); }
.niveau-3 { box-shadow: 0 12px 24px rgb(15 46 76 / 14%); }
.niveau-4 { box-shadow: 0 24px 48px rgb(15 46 76 / 18%); }""", "css",
             "Une échelle de profondeur à quatre niveaux"),
        fig("compare", "Deux façons de séparer deux surfaces",
            ("BORDURE", ["Précise, nette", "Poids visuel constant", "Idéale pour les tableaux"],
             "OMBRE", ["Douce, contextuelle", "Suggère une élévation", "Idéale pour les cartes"]),
            height=195),
        p("Une ombre se superpose à une bordure sans la remplacer. Sur un fond déjà "
          "teinté, une ombre seule devient invisible : ajoutez une bordure très fine "
          "(`1px solid rgb(0 0 0 / 6%)`) pour garantir la séparation en mode sombre."),
        code("""/* Ombre interne pour un champ enfoncé */
.champ { box-shadow: inset 0 1px 2px rgb(15 46 76 / 8%); }

/* Ombre colorée pour un bouton principal */
.bouton--principal {
  box-shadow: 0 6px 16px rgb(15 46 76 / 28%);
}

/* Aucune ombre en contraste élevé */
@media (forced-colors: active) {
  .carte { box-shadow: none; border: 1px solid CanvasText; }
}""", "css", "Trois variantes d'ombre"),

        h(2, "Hiérarchie visuelle"),
        p("La profondeur sert à indiquer ce qui est au-dessus de quoi : une boîte de "
          "dialogue au-dessus de la page, un menu déroulant au-dessus du contenu, une "
          "carte au-dessus du fond. Elle ne sert pas à décorer."),
        table(["Élément", "Niveau", "Traitement"],
              [["Page", "0", "Aucune ombre"],
               ["Carte", "1", "Ombre légère + bordure"],
               ["Menu déroulant", "2", "Ombre moyenne"],
               ["Panneau latéral", "3", "Ombre large + voile"],
               ["Boîte de dialogue", "4", "Ombre très large + fond assombri"]],
              widths=[3.4, 2.0, 5.6], first_col_bold=True,
              caption="Cinq niveaux de profondeur et leur usage"),
        p("`z-index` ne crée pas de profondeur visuelle : il ordonne les couches. Une "
          "ombre sans `z-index` cohérent produit des superpositions incohérentes. Nous "
          "traiterons le positionnement au chapitre 20."),
        code(""":root {
  --ombre-1: 0 1px 2px rgb(15 46 76 / 8%);
  --ombre-2: 0 4px 8px rgb(15 46 76 / 10%);
  --ombre-3: 0 12px 24px rgb(15 46 76 / 14%);
}

.carte { box-shadow: var(--ombre-1); }
.menu  { box-shadow: var(--ombre-2); }
.dialogue { box-shadow: var(--ombre-3); }""", "css",
             "Des ombres nommées, cohérentes dans tout le projet"),

        h(2, "Effets et sobriété"),
        p("Les effets attirent l'attention. Multiplication d'ombres, de dégradés, de "
          "rayons et de bordures colorées produit une interface bruyante où plus rien "
          "ne ressort. La règle est simple : un seul effet dominant par composant."),
        ul("Une carte : une bordure **ou** une ombre, rarement les deux appuyées.",
           "Un bouton : une couleur pleine, pas de dégradé + ombre + bordure.",
           "Un titre : une taille forte suffit ; inutile d'ajouter une ombre portée.",
           "Un état actif : un changement de fond ou de bordure, pas une animation "
           "permanente."),
        code("""/* Un composant surchargé */
.bouton {
  background: linear-gradient(45deg, red, blue);
  box-shadow: 0 10px 30px red, inset 0 0 10px blue;
  border: 3px dashed yellow;
  text-shadow: 2px 2px 2px black;
  transform: skew(-5deg);
}

/* Un composant lisible */
.bouton {
  background: var(--primaire-700);
  color: #fff;
  border: 0;
  border-radius: 8px;
  padding: .65rem 1.1rem;
  box-shadow: 0 2px 4px rgb(15 46 76 / 18%);
}""", "css", "Avant et après : la sobriété comme choix"),
        box("retenir", "Une ombre = une élévation",
            "Chaque niveau d'ombre doit correspondre à un niveau réel de la "
            "hiérarchie. Si deux éléments ont la même ombre, ils sont au même niveau : "
            "c'est une information, pas une décoration."),

        h(2, "Mode sombre et contraste élevé"),
        p("Une ombre noire sur fond noir disparaît. En mode sombre, la profondeur se "
          "traduit par des surfaces plus claires et des bordures subtiles, non par des "
          "ombres."),
        code("""@media (prefers-color-scheme: dark) {
  :root {
    --surface-0: #0d1620;
    --surface-1: #16222e;
    --surface-2: #1e2c3a;
    --bordure: #2a3b4c;
  }
  .carte {
    background: var(--surface-1);
    border: 1px solid var(--bordure);
    box-shadow: none;
  }
}""", "css", "La profondeur en mode sombre, sans ombre"),
        p("Testez toujours vos composants sur les deux thèmes. Un composant qui "
          "fonctionne en clair et disparaît en sombre n'est pas « presque terminé » : "
          "il est cassé pour une partie des utilisateurs."),
        box("methode", "Contrôle des effets",
            items=["Chaque ombre correspond-elle à un niveau de hiérarchie ?",
                   "Le focus reste-t-il visible sur tous les fonds ?",
                   "Les composants tiennent-ils en mode sombre ?",
                   "Le rendu tient-il en niveaux de gris ?",
                   "Aucun effet ne gêne-t-il la lecture du texte ?"]),
    ],
    "keypoints": [
        "La bordure occupe la boîte ; l'outline n'occupe pas d'espace.",
        "Le focus doit rester visible et contrasté sur tous les fonds.",
        "Une ombre suggère une élévation : elle doit correspondre à un niveau réel.",
        "En mode sombre, la profondeur passe par les surfaces, pas par les ombres.",
        "Un seul effet dominant par composant.",
        "Les effets se testent en contraste élevé et en niveaux de gris.",
    ],
    "bridge": "Les surfaces ont du relief. Le chapitre suivant traite les états et "
              "les composants d'interface : boutons, cartes, alertes, navigation.",
    "exercises": [
        ex("Construire une échelle d'ombres",
           "Créez quatre niveaux d'ombre cohérents pour votre projet.",
           ["Définissez-les comme variables.",
            "Associez chaque niveau à un composant.",
            "Vérifiez le rendu en mode sombre."],
           [("code", """:root {
  --ombre-1: 0 1px 2px rgb(15 46 76 / 8%);
  --ombre-2: 0 4px 10px rgb(15 46 76 / 10%);
  --ombre-3: 0 12px 28px rgb(15 46 76 / 14%);
  --ombre-4: 0 24px 60px rgb(15 46 76 / 20%);
}
@media (prefers-color-scheme: dark) {
  :root { --ombre-1: none; --ombre-2: none; --ombre-3: none; --ombre-4: none; }
  .carte, .menu, .dialogue { border: 1px solid var(--bordure); background: var(--surface-1); }
}"""),
            "Les quatre niveaux doivent rester perceptiblement distincts : un écart "
            "trop faible ne communique aucune hiérarchie.",
            "En mode sombre, remplacer l'ombre par une bordure et une surface plus "
            "claire conserve la séparation sans produire de halo noir."]),
        ex("Créer un bouton avec tous ses états",
           "Réalisez un bouton principal avec les états normal, survol, actif, focus et "
           "désactivé.",
           ["Conservez un contraste suffisant dans chaque état.",
            "Ne supprimez jamais le focus.",
            "Testez au clavier."],
           [("code", """.bouton {
  --fond: #0f2e4c;
  --texte: #ffffff;
  display: inline-flex;
  align-items: center;
  gap: .5rem;
  padding: .7rem 1.2rem;
  border: 0;
  border-radius: 8px;
  background: var(--fond);
  color: var(--texte);
  font: inherit;
  cursor: pointer;
  transition: background-color .2s ease;
}
.bouton:hover { background: #274b6d; }
.bouton:active { transform: translateY(1px); }
.bouton:focus-visible { outline: 3px solid #e0a21b; outline-offset: 3px; }
.bouton:disabled { opacity: .55; cursor: not-allowed; }"""),
            "Le survol assombrit ou éclaircit d'un cran, sans changer la teinte : "
            "l'identité reste stable.",
            "Au clavier, le focus ambre est visible sur fond clair comme sur fond "
            "sombre ; c'est la raison de sa couleur."]),
        ex("Réduire un composant surchargé",
           "Un bouton cumule dégradé, ombre colorée, bordure pointillée, texte ombré et "
           "inclinaison.",
           ["Identifiez les effets redondants.",
            "Proposez une version sobre avec un seul accent.",
            "Justifiez chaque suppression."],
           ["Le dégradé et l'ombre colorée portent le même message « important » : "
            "l'un des deux suffit. La bordure pointillée suggère un état particulier "
            "qui n'existe pas. L'inclinaison gêne la lisibilité du libellé.",
            "Version proposée : fond plein, rayon modéré, ombre légère, focus visible. "
            "L'attention vient de la couleur, pas du cumul d'effets.",
            "Chaque suppression retire du bruit : l'utilisateur identifie plus vite "
            "l'action principale."],
           level="Analyse"),
    ],
    "quiz": [
        quiz("Quelle propriété crée un contour qui ne décale pas la mise en page ?",
             ["`border`", "`outline`", "`box-shadow`", "`margin`"],
             1,
             "`outline` est dessiné hors du flux : il n'ajoute aucune épaisseur à la "
             "boîte, contrairement à `border`."),
        quiz("Que signifie une ombre très floue et très décalée ?",
             ["Un élément plat", "Un élément proche du support", "Un élément élevé au-dessus de la page", "Une erreur de rendu"],
             2,
             "Plus le flou et le décalage sont grands, plus l'objet paraît éloigné de "
             "la surface : l'élévation est perçue comme importante."),
        quiz("Comment exprimer la profondeur en mode sombre ?",
             ["Avec des ombres noires", "Avec des surfaces plus claires et des bordures", "Avec des dégradés", "En supprimant les bordures"],
             1,
             "Une ombre noire est invisible sur fond sombre ; l'élévation se traduit "
             "par une surface plus claire et une bordure fine."),
        quiz("Combien d'effets dominants un composant doit-il porter ?",
             ["Un seul", "Deux", "Trois", "Autant que possible"],
             0,
             "Un effet dominant suffit à hiérarchiser ; les cumuls produisent du bruit "
             "visuel et brouillent la lecture."),
        quiz("Que risque un `outline: none` non remplacé ?",
             ["Un meilleur rendu", "La perte du repère de focus au clavier", "Un décalage de mise en page", "Une erreur de validation"],
             1,
             "Sans contour visible, l'utilisateur au clavier ne sait plus où il se "
             "trouve dans la page."),
    ],
}
