from bookkit.dsl import (box, code, defn, ex, fig, h, ol, p, quiz, table, ul)

CH = {
    "title": "Premiers pas en CSS",
    "subtitle": "Une règle, un sélecteur, une déclaration : la grammaire d'une feuille "
                "de style et la logique de la cascade.",
    "duration": "2 h 45",
    "level": "Débutant",
    "prereq": "chapitre 8",
    "objectives": [
        "Écrire et organiser une feuille de style lisible.",
        "Comprendre la cascade, l'héritage et la spécificité.",
        "Utiliser les sélecteurs simples et les combinateurs.",
        "Appliquer des styles sans casser la structure du document.",
        "Diagnostiquer une règle qui ne s'applique pas.",
    ],
    "blocks": [
        h(2, "Une grammaire simple"),
        p("Une feuille de style est une suite de règles. Chaque règle associe un "
          "**sélecteur** à un bloc de **déclarations**. Une déclaration comporte une "
          "propriété et une valeur, séparées par deux-points et terminées par un "
          "point-virgule."),
        code("""/* sélecteur { propriété: valeur; } */
h1 {
  color: #0f2e4c;
  font-size: 2rem;
  line-height: 1.2;
}

.citation {
  border-left: 3px solid #e0a21b;
  padding-left: 1rem;
  color: #274b6d;
}""", "css", "Deux règles, quatre déclarations"),
        p("Les commentaires `/* ... */` servent à documenter une intention, pas à "
          "commenter l'évidence. `/* couleur du titre */` n'apporte rien ; "
          "`/* contraste vérifié AA sur fond blanc */` informe."),
        table(["Élément de syntaxe", "Exemple", "Remarque"],
              [["Sélecteur", "`p`, `.intro`, `#entete`", "Cible les éléments"],
               ["Déclaration", "`color: navy;`", "Une propriété, une valeur"],
               ["Combinateur", "`article > p`", "Relation entre sélecteurs"],
               ["Pseudo-classe", "`a:hover`", "État de l'élément"],
               ["Pseudo-élément", "`p::first-line`", "Partie d'un élément"],
               ["At-règle", "`@media`, `@supports`", "Bloc conditionnel"]],
              widths=[3.0, 3.8, 4.2], first_col_bold=True,
              caption="Le vocabulaire de base de CSS"),

        h(2, "Trois façons d'intégrer du CSS"),
        p("Une feuille externe est la bonne pratique : elle est mise en cache, "
          "partagée entre les pages et maintenable. Les deux autres méthodes ont des "
          "usages marginaux."),
        table(["Méthode", "Écriture", "Quand l'utiliser"],
              [["Externe", "`<link rel=\"stylesheet\" href=\"style.css\">`", "Toujours, en production"],
               ["Interne", "`<style>` dans le `head`", "Prototype, page isolée"],
               ["En ligne", "`style=\"color:red\"`", "Jamais, sauf courriel HTML"]],
              widths=[2.2, 5.4, 4.4], first_col_bold=True,
              caption="Trois méthodes d'intégration et leur légitimité"),
        p("L'attribut `style` en ligne l'emporte sur toute feuille externe, sauf "
          "`!important`. Il mélange contenu et présentation, empêche la mise en cache "
          "et rend la maintenance impossible. Les générateurs de courriels y "
          "recourent parce que les clients de messagerie ignorent les feuilles "
          "externes : c'est une contrainte de format, pas un modèle."),
        code("""<head>
  <meta charset="utf-8">
  <link rel="stylesheet" href="css/reset.css">
  <link rel="stylesheet" href="css/style.css">
  <link rel="stylesheet" href="css/print.css" media="print">
</head>""", "html", "Une organisation en couches, chargée dans l'ordre"),

        h(2, "La cascade : qui gagne ?"),
        p("Lorsque plusieurs règles visent le même élément, le navigateur arbitre "
          "selon un ordre précis. Comprendre cet ordre évite l'usage réflexe de "
          "`!important`, qui transforme une feuille de style en champ de bataille."),
        fig("flow", "L'ordre de la cascade, du plus faible au plus fort",
            ["Styles du navigateur (user agent)",
             "Styles de l'utilisateur",
             "Styles de l'auteur (votre CSS)",
             "Styles en ligne (attribut style)",
             "Déclarations !important",
             "Transitions et animations en cours"],
            height=300),
        p("À origine égale, deux critères décident : la **spécificité** du sélecteur, "
          "puis l'**ordre d'apparition** — la règle la plus tardive l'emporte. La "
          "spécificité se calcule en trois compteurs : identifiants, classes et "
          "attributs, éléments."),
        table(["Sélecteur", "Spécificité", "Commentaire"],
              [["`p`", "0-0-1", "Un élément"],
               ["`.intro`", "0-1-0", "Une classe"],
               ["`#entete`", "1-0-0", "Un identifiant"],
               ["`nav a`", "0-0-2", "Deux éléments"],
               ["`article .intro p`", "0-1-2", "Une classe, deux éléments"],
               ["`a:hover`", "0-1-1", "Pseudo-classe = classe"],
               ["`style=\"...\"`", "1-0-0-0", "En ligne, priorité supérieure"]],
              widths=[3.6, 2.6, 5.0], caption="Quelques sélecteurs et leur poids"),
        box("attention", "`!important` n'est pas une solution",
            "Chaque `!important` en appelle un autre. Si vous devez en écrire, c'est "
            "que la structure des sélecteurs est mauvaise. La solution durable est de "
            "réduire la spécificité et d'organiser les couches (`@layer`)."),
        code("""@layer reset, base, composants, utilitaires;

@layer base {
  h1 { color: #0f2e4c; }
}
@layer utilitaires {
  .texte-rouge { color: #a63a32; }
}""", "css", "Les couches CSS rendent l'ordre explicite"),

        h(2, "Héritage"),
        p("Certaines propriétés se transmettent des parents aux enfants — la couleur, "
          "la police, l'interligne — d'autres non : les marges, les bordures, le "
          "positionnement. Comprendre cette distinction évite d'écrire des règles "
          "inutiles."),
        table(["Propriété", "Héritée ?", "Pourquoi"],
              [["`color`", "Oui", "Un texte hérite de la couleur de son contexte"],
               ["`font-family`", "Oui", "La typographie se propage"],
               ["`line-height`", "Oui", "L'interligne suit la police"],
               ["`margin`", "Non", "Chaque bloc gère ses espacements"],
               ["`border`", "Non", "Chaque élément a son cadre"],
               ["`display`", "Non", "Le mode de boîte est local"],
               ["`background`", "Non", "Le fond ne se répète pas par héritage"]],
              widths=[3.0, 2.0, 5.0], first_col_bold=True,
              caption="Sept propriétés et leur comportement d'héritage"),
        code("""body {
  color: #1f2933;
  font-family: system-ui, sans-serif;
  line-height: 1.6;
}
/* Tous les enfants héritent de ces trois propriétés. Inutile de les répéter. */""",
             "css", "Trois propriétés héritées règlent l'essentiel du texte"),
        p("Les valeurs `inherit`, `initial` et `unset` permettent de contrôler "
          "explicitement ce comportement. `all: unset` réinitialise tout, ce qui est "
          "utile pour un composant isolé, rarement ailleurs."),

        h(2, "Sélecteurs et combinateurs"),
        p("Un sélecteur peut combiner plusieurs conditions. La lecture se fait de "
          "droite à gauche : le navigateur part des éléments candidats, puis remonte "
          "leurs ancêtres."),
        code("""/* Descendant : tout p dans article */
article p { color: #274b6d; }

/* Enfant direct : uniquement les p enfants immédiats */
article > p { margin-bottom: 1rem; }

/* Frère adjacent : le premier p qui suit un h2 */
h2 + p { margin-top: 0; }

/* Frère général : tous les p qui suivent un h2 */
h2 ~ p { color: #1f2933; }

/* Sélecteur d'attribut */
a[href^="https://"]::after { content: " ↗"; }
input[type="email"] { border-color: #274b6d; }""", "css", "Cinq combinaisons utiles"),
        table(["Sélecteur", "Cible", "Coût"],
              [["`*`", "Tous les éléments", "Élevé, à éviter"],
               ["`.classe`", "Tous les éléments portant la classe", "Faible"],
               ["`[type=email]`", "Attribut exact", "Faible"],
               ["`a:hover`", "État", "Faible"],
               ["`:focus-visible`", "Focus clavier", "Faible"],
               ["`:nth-child(2n)`", "Éléments pairs", "Moyen"],
               ["`:has(img)`", "Parent contenant une image", "Variable, récent"]],
              widths=[3.2, 4.8, 3.0], caption="Sept sélecteurs et leur coût de calcul"),

        h(2, "Diagnostiquer une règle qui ne s'applique pas"),
        p("Une règle CSS ne s'applique pas pour quatre raisons : le sélecteur ne cible "
          "rien, une règle plus spécifique l'emporte, la propriété est invalide, ou la "
          "feuille n'est pas chargée. L'inspecteur répond à ces quatre questions."),
        code("""$ curl -sI http://localhost:8000/css/style.css
HTTP/1.0 200 OK
Content-type: text/css

# 404 : mauvais chemin. 200 : la feuille est servie.""", "bash",
             "Vérifier qu'une feuille de style est bien servie"),
        table(["Symptôme", "Cause probable", "Vérification"],
              [["Aucun style du tout", "Chemin erroné, 404", "Onglet Réseau"],
               ["Une règle sur deux s'applique", "Erreur de syntaxe avant", "Console, feuille source"],
               ["Un style est ignoré", "Règle plus spécifique", "Styles barrés"],
               ["La couleur ne change pas", "Variable non définie", "Valeur en rouge dans l'inspecteur"],
               ["Rien ne change après modification", "Cache navigateur", "Rechargement forcé"]],
              widths=[3.4, 3.8, 4.0], first_col_bold=True,
              caption="Cinq symptômes et leur diagnostic"),
        box("methode", "Le rituel du diagnostic CSS",
            items=["La feuille est-elle chargée ? (Réseau)",
                   "Le sélecteur cible-t-il un élément réel ? (Console : document.querySelector)",
                   "Quelle règle gagne ? (Styles, ordre et spécificité)",
                   "La propriété est-elle écrite correctement ? (surlignage de l'inspecteur)",
                   "Le cache est-il en cause ? (rechargement forcé)"]),
    ],
    "keypoints": [
        "Une règle CSS associe un sélecteur à des déclarations.",
        "La feuille externe est la seule méthode raisonnable en production.",
        "La cascade arbitre : origine, spécificité, ordre.",
        "`!important` signale une organisation défaillante.",
        "Certaines propriétés s'héritent, d'autres non : la distinction évite du code inutile.",
        "Les combinateurs expriment des relations entre éléments.",
        "Quatre causes expliquent une règle inopérante : cible, conflit, syntaxe, chargement.",
    ],
    "bridge": "Vous savez écrire une règle. Le chapitre suivant approfondit les "
              "sélecteurs et les variables pour construire des feuilles de style "
              "maintenables.",
    "exercises": [
        ex("Écrire sa première feuille",
           "Reprenez la page du chapitre 3 et ajoutez une feuille de style externe.",
           ["Modifiez la couleur du texte, la police et l'interligne du corps.",
            "Distinguez les titres `h1` et `h2` par la taille et la couleur.",
            "Ajoutez une classe `.intro` avec une bordure gauche ambre."],
           [("code", """body {
  font-family: system-ui, -apple-system, "Segoe UI", sans-serif;
  color: #1f2933;
  line-height: 1.65;
  max-width: 42rem;
  margin: 0 auto;
  padding: 2rem 1.25rem;
}
h1 { color: #0f2e4c; font-size: 2.25rem; line-height: 1.15; }
h2 { color: #274b6d; font-size: 1.5rem; margin-top: 2.5rem; }
.intro {
  border-left: 4px solid #e0a21b;
  padding-left: 1rem;
  font-size: 1.125rem;
}"""),
            "`max-width` et `margin: auto` centrent le contenu sans positionnement "
            "absolu. C'est la base d'une colonne de lecture confortable : 60 à "
            "75 caractères par ligne.",
            "Les tailles en `rem` se rapportent à la taille de police racine, ce qui "
            "respecte les préférences de l'utilisateur. Les `px` figent la taille."]),
        ex("Résoudre un conflit de spécificité",
           "Pourquoi le paragraphe reste-t-il bleu alors que la règle `.alerte` "
           "demande du rouge ?",
           ["`#contenu p { color: blue; }`",
            "`.alerte { color: red; }`",
            "`<div id=\"contenu\"><p class=\"alerte\">Texte</p></div>`",
            "Proposez trois corrections, dont une sans toucher au HTML."],
           ["L'identifiant vaut 1-0-0, la classe 0-1-0 : le sélecteur avec `#contenu` "
            "gagne, quelle que soit la position de la règle.",
            "Corrections possibles : réduire la spécificité de la règle d'identifiant "
            "(`.contenu p`), augmenter celle de l'alerte (`p.alerte`, insuffisant ; "
            "`.contenu .alerte` suffit), ou introduire des couches `@layer` pour "
            "déclarer l'ordre d'importance.",
            "La correction durable consiste à supprimer les identifiants du style : "
            "ils sont prévus pour les ancres et le JavaScript, pas pour la "
            "présentation."],
           level="Diagnostic"),
        ex("Organiser une feuille de style",
           "Réorganisez ce fichier de 300 lignes en sections lisibles.",
           ["Ajoutez un sommaire en commentaire.",
            "Regroupez les règles par fonction : base, mise en page, composants.",
            "Supprimez les doublons et les `!important` inutiles."],
           [("code", """/* ==========================================================================
   Sommaire
   1. Variables et réglages de base
   2. Typographie
   3. Mise en page
   4. Composants
   5. Utilitaires
   6. Adaptations (media queries)
   ========================================================================== */

/* 1. Variables ------------------------------------------------------------ */
:root {
  --couleur-texte: #1f2933;
  --couleur-primaire: #0f2e4c;
  --espace: 1rem;
}"""),
            "Un sommaire en tête de fichier permet de retrouver une section en "
            "quelques secondes. Il doit être mis à jour quand le fichier évolue.",
            "Les variables CSS centralisent les décisions visuelles : changer la "
            "couleur primaire ne demande qu'une modification. Nous les approfondissons "
            "au chapitre 17."],
           level="Organisation"),
    ],
    "quiz": [
        quiz("Quelle méthode d'intégration du CSS est recommandée en production ?",
             ["L'attribut `style`", "La balise `<style>`", "La feuille externe", "Les trois sont équivalentes"],
             2,
             "La feuille externe est mise en cache, partagée et maintenable ; les "
             "autres méthodes mélangent contenu et présentation."),
        quiz("Quelle règle l'emporte entre `p { color: red }` et `.intro { color: blue }` ?",
             ["La première, car elle est plus tôt",
              "La seconde, car une classe pèse plus qu'un élément",
              "Les deux s'appliquent",
              "Aucune, le conflit bloque le rendu"],
             1,
             "La spécificité de `.intro` (0-1-0) est supérieure à celle de `p` "
             "(0-0-1), quelle que soit la position."),
        quiz("Quelle propriété est héritée par défaut ?",
             ["`margin`", "`border`", "`color`", "`display`"],
             2,
             "La couleur, la police et l'interligne s'héritent ; les marges, bordures "
             "et le mode d'affichage restent locaux."),
        quiz("À quoi sert `@layer` ?",
             ["À créer des animations",
              "À déclarer l'ordre de priorité entre groupes de règles",
              "À importer des polices",
              "À définir des variables"],
             1,
             "Les couches rendent l'ordre de la cascade explicite et évitent de "
             "recourir à `!important` pour arbitrer entre composants et utilitaires."),
        quiz("Que signifie un sélecteur `h2 + p` ?",
             ["Tous les `p` à l'intérieur d'un `h2`",
              "Le premier `p` qui suit immédiatement un `h2`",
              "Tous les `p` qui suivent un `h2`",
              "Les `h2` et les `p`"],
             1,
             "`+` est le combinateur de frère adjacent : il cible l'élément qui suit "
             "immédiatement, au même niveau."),
    ],
}
