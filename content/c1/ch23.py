from bookkit.dsl import (box, code, defn, ex, fig, h, ol, p, quiz, table, ul)

CH = {
    "title": "Accessibilité web",
    "subtitle": "Rendre un site utilisable par tous, sans exception : la qualité qui "
                "bénéficie à l'ensemble des utilisateurs.",
    "duration": "3 h 00",
    "level": "Intermédiaire",
    "prereq": "chapitre 22",
    "objectives": [
        "Comprendre les quatre principes WCAG.",
        "Écrire du HTML qui fonctionne avec un lecteur d'écran.",
        "Garantir une navigation complète au clavier.",
        "Concevoir des formulaires et des messages compréhensibles.",
        "Prioriser les corrections selon leur impact.",
    ],
    "blocks": [
        h(2, "Quatre principes, un cadre"),
        p("Les WCAG organisent les exigences en quatre principes : **perceptible**, "
          "**utilisable**, **compréhensible**, **robuste**. Chaque critère se range "
          "dans l'un d'eux et possède un niveau : A (indispensable), AA (standard "
          "attendu), AAA (renforcement)."),
        fig("columns", "Les quatre principes WCAG",
            [("Perceptible", ["Texte alternatif", "Contraste", "Sous-titres"]),
             ("Utilisable", ["Clavier", "Focus", "Temps suffisant"]),
             ("Compréhensible", ["Langue", "Erreurs explicites", "Cohérence"]),
             ("Robuste", ["HTML valide", "Nom, rôle, valeur", "Compatible AT"])],
            height=215),
        table(["Niveau", "Signification", "Cible"],
              [["A", "Minimum vital", "Tous les sites"],
               ["AA", "Standard courant", "Obligation légale dans de nombreux pays"],
               ["AAA", "Excellence", "Contenus spécialisés"]],
              widths=[2.0, 4.8, 4.8], first_col_bold=True,
              caption="Trois niveaux de conformité"),
        defn("Technologie d'assistance", "Lecteur d'écran, agrandisseur, plage braille, "
                                         "commande vocale : tout outil qui compense un "
                                         "besoin particulier."),

        h(2, "Le HTML d'abord"),
        p("La majorité des problèmes d'accessibilité viennent d'un HTML mal choisi, "
          "pas d'un manque d'ARIA. Un bouton est un `<button>`, un lien est un `<a>`, "
          "un titre est un `<h2>`. Les rôles ARIA ne remplacent pas ces éléments."),
        code("""<!-- Inaccessible : un div cliquable -->
<div class="bouton" onclick="envoyer()">Envoyer</div>

<!-- Accessible nativement -->
<button type="button" onclick="envoyer()">Envoyer</button>

<!-- Un lien qui navigue, un bouton qui agit -->
<a href="/contact">Nous contacter</a>
<button type="button" aria-expanded="false">Ouvrir le menu</button>""", "html",
             "Choisir l'élément natif avant d'ajouter ARIA"),
        box("retenir", "La première règle d'ARIA",
            "« Ne pas utiliser ARIA » est la première règle des spécifications. Un "
            "élément natif apporte gratuitement le rôle, le focus, les événements "
            "clavier et l'annonce."),
        code("""<!-- Le nom accessible vient du contenu, ou d'un attribut -->
<button><svg aria-hidden="true">…</svg> Fermer</button>
<button aria-label="Fermer la fenêtre"><svg aria-hidden="true">…</svg></button>

<!-- Les icônes seules doivent être nommées ; les icônes décoratives masquées -->
<img src="logo.svg" alt="Espritropic">      <!-- informative -->
<img src="motif.svg" alt="">                 <!-- décorative -->""", "html",
             "Nommer ce qui informe, masquer ce qui décore"),

        h(2, "Navigation au clavier"),
        p("Toute fonctionnalité doit être utilisable sans souris. Cela implique un "
          "ordre de tabulation logique, un focus toujours visible et des raccourcis "
          "prévisibles."),
        table(["Touche", "Comportement attendu", "Piège fréquent"],
              [["Tab", "Élément suivant", "`tabindex` positif qui casse l'ordre"],
               ["Maj+Tab", "Élément précédent", "Focus piégé sans issue"],
               ["Entrée", "Activer un lien ou un bouton", "`div` non activable"],
               ["Espace", "Activer un bouton, cocher", "Comportement absent"],
               ["Échap", "Fermer un menu ou une modale", "Aucune fermeture"],
               ["Flèches", "Parcourir un groupe", "Absentes"]],
              widths=[2.2, 4.6, 4.2], first_col_bold=True,
              caption="Six touches et les attentes associées"),
        code("""/* Ne jamais supprimer le focus sans remplacement */
:focus-visible {
  outline: 3px solid #e0a21b;
  outline-offset: 3px;
}

/* Lien d'évitement, indispensable sur les pages à navigation longue */
.skip-link { position: absolute; left: -999px; }
.skip-link:focus { left: 1rem; top: 1rem; background: #0f2e4c; color: #fff; }""",
             "css", "Deux fondements de la navigation clavier"),
        p("`tabindex` ne doit valoir que `0` (rendre focusable dans l'ordre naturel) ou "
          "`-1` (focusable par script). Les valeurs positives créent un ordre parallèle "
          "que personne ne maîtrise."),

        h(2, "Formulaires et messages"),
        p("Un formulaire accessible se remplit sans voir l'écran : chaque champ a un "
          "nom, une aide éventuelle, et les erreurs sont annoncées."),
        code("""<div class="champ">
  <label for="courriel">Adresse électronique <span aria-hidden="true">*</span></label>
  <input id="courriel" type="email" name="courriel" required
         autocomplete="email" aria-describedby="courriel-aide"
         aria-invalid="false">
  <p id="courriel-aide">Nous ne partagerons jamais votre adresse.</p>
</div>""", "html", "Un champ complet, nommé et décrit"),
        ul("Le caractère obligatoire est annoncé en texte, pas seulement par une couleur.",
           "L'erreur est liée au champ par `aria-describedby` et signalée par `aria-invalid`.",
           "Le focus se déplace sur le message d'erreur ou sur le premier champ fautif.",
           "Les valeurs saisies sont conservées après un échec."),
        code("""/* Masquer visuellement sans priver les lecteurs d'écran */
.visually-hidden {
  position: absolute; width: 1px; height: 1px;
  overflow: hidden; clip-path: inset(50%); white-space: nowrap;
}""", "css", "Le masquage accessible à ne pas confondre avec `display: none`"),

        h(2, "Images, médias et contenus complexes"),
        p("Les contenus non textuels doivent avoir une alternative équivalente. Pour "
          "une image complexe, l'`alt` résume et une description développe."),
        table(["Contenu", "Alternative", "Remarque"],
              [["Image informative", "`alt` descriptif", "Décrire l'information, pas le fichier"],
               ["Image décorative", "`alt=\"\"`", "Jamais d'attribut absent"],
               ["Graphique", "`alt` + tableau de données", "Le détail doit être accessible"],
               ["Vidéo", "Sous-titres et transcription", "Audio-description si nécessaire"],
               ["Audio", "Transcription", "Indispensable"],
               ["Tableau", "`caption`, `th`, `scope`", "Voir chapitre 7"]],
              widths=[2.8, 4.2, 4.0], first_col_bold=True,
              caption="Six types de contenus et leur alternative"),
        p("Un contenu animé doit pouvoir être mis en pause. Un contenu qui clignote "
          "plus de trois fois par seconde peut déclencher une crise d'épilepsie : il "
          "doit être évité."),

        h(2, "Prioriser les corrections"),
        p("L'accessibilité n'est pas binaire. Toutes les corrections n'ont pas le même "
          "impact, et certaines coûtent très peu."),
        table(["Correction", "Effort", "Impact"],
              [["`lang` sur `html`", "Très faible", "Élevé"],
               ["Focus visible", "Très faible", "Élevé"],
               ["`alt` sur les images", "Faible", "Élevé"],
               ["Contrastes conformes", "Faible", "Élevé"],
               ["Étiquettes de formulaire", "Faible", "Élevé"],
               ["Navigation clavier complète", "Moyen", "Très élevé"],
               ["Sous-titres vidéo", "Moyen à élevé", "Élevé"],
               ["Refonte d'un composant non accessible", "Élevé", "Variable"]],
              widths=[5.2, 2.6, 3.2], first_col_bold=True,
              caption="Huit corrections, classées par rapport effort/impact"),
        code("""# Audit automatisé (ne détecte qu'une partie des problèmes)
$ npx @axe-core/cli https://exemple.fr

# Audit manuel complémentaire
# 1. Parcourir toute la page au clavier
# 2. Désactiver les images
# 3. Tester avec un lecteur d'écran (NVDA, VoiceOver)
# 4. Zoomer à 200 %""", "bash", "Automatiser ce qui peut l'être, vérifier le reste à la main"),
        box("attention", "Les outils automatiques ne voient pas tout",
            "Un audit automatique détecte environ 30 à 40 % des problèmes. Le reste "
            "exige un parcours réel au clavier et au lecteur d'écran. Ne confondez pas "
            "« zéro erreur dans l'outil » et « site accessible »."),
        box("methode", "Audit express en dix minutes",
            items=["Tabuler dans toute la page : le focus est-il visible partout ?",
                   "Y a-t-il un lien d'évitement ?",
                   "Chaque image a-t-elle un `alt` justifié ?",
                   "Les contrastes sont-ils conformes ?",
                   "Le zoom à 200 % conserve-t-il l'information ?"]),
    ],
    "keypoints": [
        "Quatre principes WCAG : perceptible, utilisable, compréhensible, robuste.",
        "AA est le niveau attendu ; A est le minimum vital.",
        "Le HTML natif résout la majorité des besoins, avant ARIA.",
        "Tout doit être utilisable au clavier, avec un focus visible.",
        "Un nom accessible décrit l'action, pas l'icône.",
        "Les erreurs se lient aux champs et s'annoncent.",
        "Les audits automatiques couvrent moins de la moitié des problèmes.",
    ],
    "bridge": "La partie présentation est achevée. La suite entre dans le langage qui "
              "rend les pages vivantes : JavaScript.",
    "exercises": [
        ex("Rendre un composant accessible",
           "Ce bouton-icône n'a pas de nom et n'est pas utilisable au clavier.",
           ["Ajoutez un nom accessible.",
            "Préservez le focus.",
            "Masquez l'icône aux technologies d'assistance."],
           [("code", """<button type="button" class="fermer" aria-label="Fermer la fenêtre">
  <svg width="20" height="20" aria-hidden="true" focusable="false">
    <use href="icones/croix.svg#croix"></use>
  </svg>
</button>

<style>
.fermer:focus-visible { outline: 3px solid #e0a21b; outline-offset: 3px; }
</style>"""),
            "Un `<button>` est activable par Entrée et Espace, et reçoit le focus "
            "naturellement. `aria-label` fournit le nom absent.",
            "`aria-hidden=\"true\"` et `focusable=\"false\"` empêchent l'icône SVG "
            "d'être annoncée ou focalisée dans les anciens navigateurs."]),
        ex("Auditer une page au clavier",
           "Parcourez une page réelle uniquement avec Tab, Maj+Tab, Entrée et Échap.",
           ["Notez les points de blocage.",
            "Vérifiez l'ordre de tabulation.",
            "Corrigez au moins trois problèmes."],
           ["Blocages fréquents : menus qui ne s'ouvrent pas, modales sans piège de "
            "focus, éléments non atteignables, focus invisible.",
            "L'ordre doit suivre la lecture : s'il saute à droite puis à gauche, un "
            "`tabindex` positif ou un ordre visuel différent du DOM est en cause.",
            ("code", """/* Trois corrections rapides */
:focus-visible { outline: 3px solid #e0a21b; outline-offset: 3px; }
.skip-link:focus { position: static; }
[role="dialog"] { isolation: isolate; }""")],
           level="Audit"),
        ex("Écrire des messages d'erreur accessibles",
           "Trois champs échouent à la validation. Rédigez et structurez le retour.",
           ["Reliez chaque message à son champ.",
            "Annoncez le résumé des erreurs.",
            "Indiquez comment corriger."],
           [("code", """<div role="alert" class="resume-erreurs">
  <p><strong>3 erreurs empêchent l'envoi :</strong></p>
  <ul>
    <li><a href="#courriel">L'adresse électronique doit contenir un arobase.</a></li>
    <li><a href="#mdp">Le mot de passe doit comporter 12 caractères minimum.</a></li>
    <li><a href="#pays">Veuillez sélectionner un pays.</a></li>
  </ul>
</div>"""),
            "Le résumé est annoncé immédiatement (`role=\"alert\"`) et chaque lien "
            "conduit au champ fautif.",
            "Chaque message dit ce qui est attendu, pas seulement ce qui est refusé : "
            "« doit contenir un arobase » est actionnable."],
           level="Accessibilité"),
    ],
    "quiz": [
        quiz("Quels sont les quatre principes WCAG ?",
             ["Rapide, beau, simple, moderne",
              "Perceptible, utilisable, compréhensible, robuste",
              "Lisible, cliquable, imprimable, indexable",
              "HTML, CSS, JS, ARIA"],
             1,
             "Ces quatre principes structurent tous les critères de conformité."),
        quiz("Quel niveau de conformité est le standard attendu ?",
             ["A", "AA", "AAA", "Aucun"],
             1,
             "AA est le niveau visé par la plupart des réglementations et des "
             "référentiels publics."),
        quiz("Que faire d'une icône purement décorative dans un bouton ?",
             ["La décrire dans `alt`", "Ajouter `aria-hidden=\"true\"`",
              "La supprimer", "La rendre focusable"],
             1,
             "L'icône n'apporte pas d'information : elle doit être ignorée par les "
             "technologies d'assistance, le nom venant du bouton."),
        quiz("Quel `tabindex` est recommandé ?",
             ["`tabindex=\"5\"`", "`tabindex=\"0\"` ou `-1`", "`tabindex=\"1\"`", "Aucun, jamais"],
             1,
             "Les valeurs positives créent un ordre parallèle imprévisible ; `0` et "
             "`-1` sont les seules valeurs raisonnables."),
        quiz("Quelle proportion des problèmes un audit automatique détecte-t-il ?",
             ["100 %", "Environ 80 %", "Environ 30 à 40 %", "Moins de 5 %"],
             2,
             "Les outils repèrent les erreurs mécaniques ; le reste exige un test "
             "manuel au clavier et au lecteur d'écran."),
    ],
}
