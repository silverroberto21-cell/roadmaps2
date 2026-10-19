from bookkit.dsl import (box, code, defn, ex, fig, h, ol, p, quiz, table, ul)

CH = {
    "title": "Internationalisation et contenu multilingue",
    "subtitle": "Un site qui change de langue, de sens de lecture et de format sans "
                "casser sa mise en page.",
    "duration": "2 h 45",
    "level": "Avancé",
    "prereq": "chapitre 38",
    "objectives": [
        "Déclarer correctement la langue d'un document.",
        "Produire des mises en page compatibles avec l'écriture de droite à gauche.",
        "Formater dates, nombres et devises avec `Intl`.",
        "Gérer les pluriels et les traductions sans concaténation.",
        "Organiser les fichiers de traduction d'un projet.",
    ],
    "blocks": [
        h(2, "Trois mots à distinguer"),
        p("L'internationalisation prépare le code à toutes les langues. La localisation "
          "adapte un produit à un marché précis. La traduction n'est qu'une partie de "
          "la localisation : une date, une monnaie, une adresse ou une couleur peuvent "
          "aussi changer."),
        table(["Terme", "Portée", "Exemple"],
              [["Internationalisation", "Code et structure", "`lang`, `dir`, `Intl`"],
               ["Localisation", "Contenu et usages", "Formats, images, ton"],
               ["Traduction", "Texte", "Fichiers de messages"],
               ["Adaptation", "Produit et marché", "Paiement, droit, support"]],
              widths=[4.0, 4.4, 4.2], first_col_bold=True,
              caption="Quatre termes souvent confondus"),
        defn("Locale", "Identifiant de langue et de région, au format BCP 47 : `fr`, "
                       "`fr-CA`, `pt-BR`, `zh-Hans`. Il ne désigne pas seulement une "
                       "langue mais un ensemble de conventions."),

        h(2, "Déclarer la langue et le sens"),
        p("L'attribut `lang` n'est pas décoratif : il détermine la prononciation du "
          "lecteur d'écran, la césure, la correction orthographique et le rendu des "
          "caractères chinois ou japonais."),
        code("""<!doctype html>
<html lang="fr">
<head>
  <meta charset="utf-8">
</head>
<body>
  <h1>Notre équipe</h1>
  <p>Notre partenaire s'appelle <span lang="en">Northwind Traders</span>.</p>

  <!-- Sens de lecture : rtl pour l'arabe et l'hébreu -->
  <div lang="ar" dir="rtl">مرحبا بكم في موقعنا</div>

  <!-- Un extrait de code reste de gauche à droite -->
  <code dir="ltr" lang="en">npm install</code>
</body>
</html>""", "html", "Une langue déclarée au bon endroit"),
        table(["Situation", "Déclaration", "Raison"],
              [["Document principal", "`<html lang=\"fr\">`", "Langue par défaut"],
               ["Citation en anglais", "`<q lang=\"en\">`", "Prononciation correcte"],
               ["Nom propre étranger", "`<span lang=\"en\">`", "Césure et synthèse"],
               ["Bloc de code", "`lang=\"en\"` + `dir=\"ltr\"`", "Lecture technique"],
               ["Page en arabe", "`lang=\"ar\" dir=\"rtl\"`", "Sens de lecture"]],
              widths=[4.0, 5.0, 3.6], first_col_bold=True,
              caption="Cinq cas de déclaration"),
        box("attention", "`dir=\"rtl\"` ne suffit pas",
            "Une page écrite avec `margin-left` et `float: left` restera cassée en "
            "arabe. Il faut employer les propriétés logiques dès le départ : "
            "`margin-inline-start`, `padding-inline-end`, `inline-size`, "
            "`border-start-start-radius`."),

        h(2, "Propriétés logiques"),
        p("Les propriétés logiques remplacent les directions physiques par des "
          "directions relatives au sens de lecture. La même feuille de style sert alors "
          "les deux sens."),
        table(["Physique", "Logique", "Équivalent en RTL"],
              [["`margin-left`", "`margin-inline-start`", "Marge à droite"],
               ["`margin-right`", "`margin-inline-end`", "Marge à gauche"],
               ["`padding-top`", "`padding-block-start`", "Inchangé"],
               ["`width`", "`inline-size`", "Inchangé"],
               ["`text-align: left`", "`text-align: start`", "Aligné à droite"],
               ["`border-top-left-radius`", "`border-start-start-radius`", "Coin opposé"]],
              widths=[4.2, 5.2, 3.2], first_col_bold=True,
              caption="Six conversions utiles"),
        code(""".carte {
  margin-inline-start: 1rem;      /* gauche en LTR, droite en RTL */
  padding-inline: 1.5rem;
  border-inline-start: 3px solid var(--accent);
  text-align: start;
}

/* Icône directionnelle : retournée automatiquement */
.chevron:dir(rtl) { transform: scaleX(-1); }""", "css",
             "Une mise en page qui fonctionne dans les deux sens"),
        fig("compare", "Deux approches de la direction",
            ("DIRECTIONS PHYSIQUES", ["Duplication de feuille", "Correctifs par locale",
                                      "Fragile"],
             "PROPRIÉTÉS LOGIQUES", ["Une seule feuille", "Sens automatique",
                                     "Maintenable"]),
            height=200),

        h(2, "Formater avec `Intl`"),
        p("L'API `Intl` du navigateur connaît les conventions de chaque locale. Elle "
          "évite d'écrire des formats à la main, qui seront faux pour la moitié de la "
          "planète."),
        code("""const date = new Date("2026-03-14T15:00:00Z");

new Intl.DateTimeFormat("fr-FR", { dateStyle: "long" }).format(date);
// « 14 mars 2026 »

new Intl.DateTimeFormat("en-US", { dateStyle: "long" }).format(date);
// "March 14, 2026"

new Intl.NumberFormat("fr-FR", { style: "currency", currency: "EUR" })
  .format(1234.5);          // « 1 234,50 € » (espace insécable)

new Intl.NumberFormat("de-DE").format(1234.5);   // "1.234,5"

new Intl.RelativeTimeFormat("fr", { numeric: "auto" }).format(-2, "day");
// « avant-hier »""", "js", "Quatre formats, zéro calcul manuel"),
        table(["Objet", "Usage", "Piège évité"],
              [["`DateTimeFormat`", "Dates et heures", "Ordre jour/mois"],
               ["`NumberFormat`", "Nombres, devises, unités", "Séparateurs"],
               ["`RelativeTimeFormat`", "« il y a 3 jours »", "Pluriels"],
               ["`PluralRules`", "Catégorie de pluriel", "Règles slaves, arabes"],
               ["`Collator`", "Tri alphabétique", "Accents et ligatures"],
               ["`ListFormat`", "Énumérations", "« a, b et c »"]],
              widths=[4.0, 5.0, 3.6], first_col_bold=True,
              caption="Six objets `Intl`"),
        code("""// Trier correctement
["écureuil", "elephant", "Étoile", "zèbre"]
  .sort(new Intl.Collator("fr").compare);
// ["écureuil", "elephant", "Étoile", "zèbre"]

// Énumérer
new Intl.ListFormat("fr", { style: "long", type: "conjunction" })
  .format(["CSS", "HTML", "JavaScript"]);
// « CSS, HTML et JavaScript »""", "js", "Deux usages souvent oubliés"),

        h(2, "Traduire sans concaténer"),
        p("Concaténer des fragments de phrase produit des traductions impossibles. Un "
          "message complet, avec des emplacements nommés, se traduit correctement dans "
          "toutes les langues."),
        code("""// À éviter : ordre des mots figé
const message = "Bonjour " + prenom + ", vous avez " + n + " message" + (n > 1 ? "s" : "");

// À privilégier : message complet et paramétré
const messages = {
  fr: {
    salutation: "Bonjour {prenom}, vous avez {n, plural, =0 {aucun message} one {un message} other {# messages}}.",
    panier: "{n, plural, =0 {Votre panier est vide} one {Un article} other {# articles}}",
  },
  en: {
    salutation: "Hello {prenom}, you have {n, plural, =0 {no messages} one {one message} other {# messages}}.",
    panier: "{n, plural, =0 {Your cart is empty} one {One item} other {# items}}",
  },
};""", "js", "Des messages complets, avec pluriels"),
        p("Le standard ICU MessageFormat décrit ces messages. Les bibliothèques de "
          "traduction l'implémentent ; à défaut, `Intl.PluralRules` permet de choisir "
          "la forme correcte."),
        code("""const regles = new Intl.PluralRules("pl");
regles.select(1);   // "one"
regles.select(2);   // "few"
regles.select(5);   // "many"   — le polonais distingue plus de formes que le français""",
             "js", "Des règles de pluriel qui varient selon la langue"),
        box("retenir", "Le texte traduit change de longueur",
            "L'allemand et le finnois allongent, le chinois raccourcit. Prévoyez 30 % "
            "de marge dans les boutons, les onglets et les libellés de formulaire, et "
            "testez avec la traduction la plus longue dès la conception."),

        h(2, "Organiser les traductions"),
        p("Un fichier par langue, avec des clés stables et un espace de noms par écran. "
          "Les clés ne doivent jamais être les phrases elles-mêmes : une correction "
          "d'orthographe casserait toutes les traductions."),
        code("""locales/
├── fr.json
├── en.json
└── ar.json

# fr.json
{
  "panier.titre": "Votre panier",
  "panier.vide": "Aucun article pour le moment.",
  "panier.total": "Total : {montant}",
  "panier.commander": "Commander"
}""", "text", "Une arborescence de traductions"),
        code("""// Chargement à la demande, une locale à la fois
async function charger(locale) {
  const reponse = await fetch(`/locales/${locale}.json`);
  if (!reponse.ok) throw new Error(`Locale indisponible : ${locale}`);
  return reponse.json();
}

// Détection initiale, avec repli explicite
const preferee = navigator.language;             // "fr-CD"
const supportees = ["fr", "en", "ar"];
const locale = supportees.find(l => preferee.startsWith(l)) ?? "fr";
document.documentElement.lang = locale;""", "js", "Charger et détecter"),
        table(["Pratique", "Bénéfice", "Coût"],
              [["Clés stables", "Traductions durables", "Discipline"],
               ["Fichiers par langue", "Chargement ciblé", "Synchronisation"],
               ["Repli explicite", "Jamais de page vide", "Une langue de référence"],
               ["Pseudo-localisation", "Repère les textes trop longs", "Test automatisé"],
               ["Validation en intégration", "Clés manquantes détectées", "Configuration"]],
              widths=[4.0, 4.6, 4.0], first_col_bold=True,
              caption="Cinq pratiques d'organisation"),
        box("methode", "Tester une traduction",
            items=["Passez l'interface en pseudo-locale (`[!!! Ɓöñĵöüŕ !!!]`).",
                   "Vérifiez les débordements et les troncatures.",
                   "Testez en arabe avec `dir=\"rtl\"`.",
                   "Vérifiez chaque date et chaque montant affiché."]),
    ],
    "keypoints": [
        "`lang` conditionne prononciation, césure et rendu typographique.",
        "`dir` déclare le sens de lecture ; il ne suffit pas sans propriétés logiques.",
        "Les propriétés logiques remplacent les directions physiques.",
        "`Intl` formate dates, nombres, devises et pluriels selon la locale.",
        "Les messages complets se traduisent ; les fragments concaténés non.",
        "Le texte traduit change de longueur : prévoir de la marge.",
        "Les clés de traduction doivent être stables et jamais être les phrases.",
    ],
    "bridge": "Le site parle plusieurs langues. Le dernier chapitre traite de ce qui "
              "assure la durée : la maintenance et le travail en équipe.",
    "exercises": [
        ex("Rendre une carte compatible RTL",
           "Cette carte utilise des marges et des alignements physiques.",
           ["Convertissez en propriétés logiques.",
            "Vérifiez avec `dir=\"rtl\"`.",
            "Contrôlez les icônes directionnelles."],
           [("code", """.carte {
  margin-left: 0;                 /* → margin-inline-start */
  padding: 1rem 1rem 1rem 2rem;   /* → padding-block + padding-inline */
  border-left: 3px solid #e0a21b; /* → border-inline-start */
  text-align: left;               /* → text-align: start */
}

/* Version logique */
.carte {
  margin-inline-start: 0;
  padding-block: 1rem;
  padding-inline: 1rem 1rem;
  padding-inline-start: 2rem;
  border-inline-start: 3px solid #e0a21b;
  text-align: start;
}"""),
            "Les quatre conversions correspondent exactement, sans duplication de "
            "feuille de style.",
            "Les icônes directionnelles (flèches, chevrons) se retournent via "
            "`transform: scaleX(-1)` en contexte RTL."]),
        ex("Formater une facture",
           "Affichez une date, un montant et un délai selon trois locales.",
           ["Utilisez `Intl`, jamais de gabarit manuel.",
            "Vérifiez les espaces insécables.",
            "Testez le pluriel."],
           [("code", """function ligne(locale) {
  const date = new Intl.DateTimeFormat(locale, { dateStyle: "long" }).format(new Date());
  const montant = new Intl.NumberFormat(locale, {
    style: "currency", currency: "EUR",
  }).format(1234.5);
  const delai = new Intl.RelativeTimeFormat(locale, { numeric: "auto" })
    .format(-7, "day");
  return { date, montant, delai };
}

ligne("fr-FR");   // { date: "19 octobre 2026", montant: "1 234,50 €", delai: "la semaine dernière" }
ligne("en-GB");   // { date: "19 October 2026", montant: "€1,234.50", delai: "last week" }"""),
            "`dateStyle: \"long\"` produit un ordre et des noms de mois corrects sans "
            "tableau manuel.",
            "Les espaces insécables du format français empêchent le montant d'être coupé "
            "entre deux lignes."]),
        ex("Écrire des messages traduisibles",
           "Réécrivez un message construit par concaténation.",
           ["`\"Vous avez \" + n + \" nouveau\" + (n>1?\"x\":\"\") + \" message\" + (n>1?\"s\":\"\")`",
            "Prévoyez le cas zéro.",
            "Prévoyez une seconde langue."],
           [("code", """{
  "fr": "{n, plural, =0 {Aucun nouveau message} one {Un nouveau message} other {# nouveaux messages}}",
  "en": "{n, plural, =0 {No new messages} one {One new message} other {# new messages}}",
  "ar": "{n, plural, =0 {لا رسائل جديدة} one {رسالة جديدة واحدة} two {رسالتان جديدتان} few {# رسائل جديدة} other {# رسالة جديدة}}"
}"""),
            "L'arabe distingue six catégories de pluriel : une concaténation ne peut "
            "pas les exprimer.",
            "Le cas zéro est explicite, car « 0 message » ne se dit pas de la même façon "
            "dans toutes les langues."],
           level="Internationalisation"),
    ],
    "quiz": [
        quiz("Que détermine l'attribut `lang` ?",
             ["La couleur du texte", "La prononciation, la césure et le rendu",
              "La taille de police", "Le sens de lecture"],
             1,
             "Il indique la langue du contenu aux navigateurs et aux technologies "
             "d'assistance."),
        quiz("Quelle propriété remplace `margin-left` en écriture logique ?",
             ["`margin-start`", "`margin-inline-start`", "`margin-block-start`", "`margin-left`"],
             1,
             "`inline` suit l'axe du texte, donc le sens de lecture."),
        quiz("Quel objet `Intl` formate une devise ?",
             ["`DateTimeFormat`", "`NumberFormat`", "`Collator`", "`ListFormat`"],
             1,
             "`NumberFormat` avec `style: \"currency\"` gère le symbole et le placement."),
        quiz("Pourquoi éviter de concaténer des fragments traduits ?",
             ["Pour la performance", "Parce que l'ordre des mots varie",
              "Pour la sécurité", "Ce n'est pas un problème"],
             1,
             "Chaque langue a son ordre et ses accords : un message complet est "
             "nécessaire."),
        quiz("Que faut-il prévoir pour un texte traduit ?",
             ["Une longueur identique", "Une marge de 30 % environ",
              "Une police unique", "Un alignement à gauche"],
             1,
             "L'allemand ou le finnois allongent fortement les libellés."),
    ],
}
