from bookkit.dsl import (box, code, defn, ex, fig, h, ol, p, quiz, table, ul)

CH = {
    "title": "Positionnement et couches",
    "subtitle": "Sortir du flux sans casser la page : position, empilement, menus et "
                "fenêtres modales.",
    "duration": "2 h 45",
    "level": "Intermédiaire",
    "prereq": "chapitre 19",
    "objectives": [
        "Choisir entre flux normal, position relative, absolue, fixe et sticky.",
        "Comprendre les contextes d'empilement et `z-index`.",
        "Construire un menu déroulant et une fenêtre modale accessibles.",
        "Éviter les pièges du positionnement absolu.",
        "Utiliser `position: sticky` sans effet de bord.",
    ],
    "blocks": [
        h(2, "Cinq valeurs de position"),
        p("Le flux normal place les éléments selon leur ordre dans le document. "
          "`position` permet d'en sortir, partiellement ou totalement. Chaque valeur "
          "correspond à un besoin précis."),
        table(["Valeur", "Comportement", "Référence", "Usage"],
              [["`static`", "Flux normal", "—", "Valeur par défaut"],
               ["`relative`", "Reste dans le flux, se décale", "Sa position d'origine", "Calage, contexte"],
               ["`absolute`", "Sort du flux, positionné", "Ancêtre positionné", "Infobulle, badge"],
               ["`fixed`", "Sort du flux, fixé à l'écran", "Fenêtre", "Barre d'action"],
               ["`sticky`", "Flux normal puis figé au défilement", "Conteneur de défilement", "En-tête de tableau"]],
              widths=[2.2, 4.4, 3.6, 3.0], first_col_bold=True,
              caption="Cinq valeurs de position et leur référence"),
        fig("compare", "Deux sorties du flux",
            ("RELATIVE", ["Conserve sa place", "Se décale visuellement", "Ne perturbe pas les voisins"],
             "ABSOLUTE", ["Retiré du flux", "Positionné par rapport à un ancêtre", "Peut chevaucher"]),
            height=195),
        code(""".carte { position: relative; }        /* devient l'ancêtre */

.badge {
  position: absolute;
  inset-block-start: -.5rem;
  inset-inline-end: -.5rem;
  background: #e0a21b;
  border-radius: 999px;
  padding: .1rem .45rem;
}""", "css", "Le motif classique du badge positionné"),

        h(2, "Sticky : figer au bon moment"),
        p("`position: sticky` combine le flux normal et le positionnement fixe : "
          "l'élément défile normalement jusqu'à atteindre un seuil, puis reste visible "
          "tant que son conteneur est à l'écran."),
        code(""".sommaire {
  position: sticky;
  top: 1rem;
  max-height: calc(100dvh - 2rem);
  overflow: auto;
}

thead th {
  position: sticky;
  top: 0;
  background: #fff;
  z-index: 1;
}""", "css", "Deux usages légitimes de sticky"),
        box("attention", "Sticky ne fonctionne pas toujours",
            items=["Un ancêtre avec `overflow: hidden` ou `auto` limite le collage.",
                   "Aucun seuil (`top`, `bottom`) n'est défini.",
                   "Le conteneur est trop court : l'élément n'a pas la place de coller.",
                   "Un ancêtre a `display: contents`, qui supprime la boîte."]),
        p("Ces quatre situations expliquent la quasi-totalité des « sticky qui ne "
          "collent pas ». L'inspecteur permet de vérifier chaque ancêtre."),

        h(2, "Empilement et z-index"),
        p("`z-index` n'ordonne que des éléments positionnés ou des enfants de "
          "conteneurs flex ou grid. Il ne fonctionne pas sur `position: static`."),
        code(""".menu     { position: absolute; z-index: 10; }
.voile    { position: fixed;    z-index: 20; }
.modale   { position: fixed;    z-index: 30; }
.infobulle{ position: absolute; z-index: 40; }
.notification { position: fixed; z-index: 50; }""", "css",
             "Une échelle de couches documentée"),
        defn("Contexte d'empilement", "Groupe d'éléments dont les `z-index` ne se "
                                      "comparent qu'entre eux. Un enfant ne peut jamais "
                                      "passer au-dessus d'un élément situé dans un "
                                      "contexte supérieur."),
        p("Un contexte d'empilement est créé par `position` avec un `z-index` non "
          "automatique, par `opacity` inférieur à 1, par `transform`, `filter`, "
          "`isolation: isolate` ou `contain: paint`. C'est la source des « mon menu "
          "passe sous un autre bloc malgré un z-index énorme »."),
        code(""".carte { transform: translateY(0); }  /* crée un contexte ! */
.menu  { z-index: 9999; }               /* reste enfermé dans ce contexte */""",
             "css", "L'effet de bord le plus fréquent de `transform`"),
        table(["Symptôme", "Cause", "Correction"],
              [["`z-index` ignoré", "Élément non positionné", "Ajouter `position`"],
               ["Menu sous un bloc", "Ancêtre transformé", "Sortir le menu du contexte"],
               ["Modale derrière le voile", "Contextes différents", "Regrouper dans un même contexte"],
               ["Ordre imprévisible", "`z-index` arbitraires", "Échelle documentée"]],
              widths=[3.4, 3.8, 3.8], first_col_bold=True,
              caption="Quatre problèmes d'empilement et leur remède"),

        h(2, "Menus déroulants accessibles"),
        p("Un menu doit s'ouvrir au clic **et** au clavier, se fermer avec Échap, "
          "piéger le focus tant qu'il est ouvert, et rendre le focus au déclencheur à "
          "la fermeture."),
        code("""<div class="menu">
  <button class="menu__declencheur" aria-expanded="false"
          aria-controls="menu-liste" id="menu-bouton">
    Menu
  </button>
  <ul class="menu__liste" id="menu-liste" hidden>
    <li><a href="/cours">Cours</a></li>
    <li><a href="/blog">Blog</a></li>
  </ul>
</div>""", "html", "Une structure de menu annonçable"),
        code(""".menu { position: relative; display: inline-block; }
.menu__liste {
  position: absolute;
  inset-block-start: calc(100% + .4rem);
  inset-inline-start: 0;
  min-width: 12rem;
  background: #fff;
  border: 1px solid #d5dee6;
  border-radius: 8px;
  box-shadow: 0 12px 28px rgb(15 46 76 / 14%);
  padding: .35rem 0;
  list-style: none;
  margin: 0;
  z-index: 20;
}
.menu__liste[hidden] { display: none; }""", "css", "Un menu positionné sous son déclencheur"),
        p("L'attribut `hidden` suffit à masquer le menu, mais il faut le basculer en "
          "JavaScript et mettre à jour `aria-expanded`. Le chapitre 27 détaille le "
          "comportement complet."),

        h(2, "Fenêtre modale"),
        p("Une modale est une boîte de dialogue qui interrompt le reste de la page. "
          "Elle doit bloquer l'interaction avec l'arrière-plan et rendre le focus à "
          "l'élément déclencheur."),
        code("""<dialog id="confirmation" aria-labelledby="titre-confirmation">
  <h2 id="titre-confirmation">Supprimer cet article ?</h2>
  <p>Cette action est définitive.</p>
  <form method="dialog">
    <button value="annuler">Annuler</button>
    <button value="supprimer" class="bouton--danger">Supprimer</button>
  </form>
</dialog>""", "html", "L'élément `dialog` natif"),
        code(""".dialog { border: 0; border-radius: 12px; padding: 1.5rem; max-width: 32rem; }
dialog::backdrop { background: rgb(15 46 76 / 55%); }
dialog[open] { animation: apparition 180ms ease-out; }""", "css",
             "Une modale native, stylée"),
        p("`<dialog>` offre gratuitement le piège de focus, la fermeture par Échap et "
          "le fond `::backdrop`. C'est un progrès considérable par rapport aux modales "
          "bricolées en `div`, qui oublient presque toujours l'accessibilité."),
        box("pratique", "`showModal()` plutôt que `show()`",
            "`dialog.show()` affiche la boîte sans bloquer l'arrière-plan. "
            "`dialog.showModal()` ajoute le piège de focus, le fond inerte et la "
            "fermeture par Échap : c'est la méthode à utiliser."),

        h(2, "Diagnostiquer un positionnement"),
        p("Un élément positionné se comporte mal pour trois raisons : l'ancêtre de "
          "référence n'est pas celui attendu, une propriété d'insertion manque, ou un "
          "contexte d'empilement l'enferme."),
        code("""/* Toujours définir au moins deux insertions pour maîtriser la position */
.outil {
  position: fixed;
  inset-block-end: 1.5rem;
  inset-inline-end: 1.5rem;
}

/* Vérifier l'ancêtre réel : l'inspecteur affiche la chaîne de positionnement */""",
             "css", "Deux insertions valent mieux qu'un décalage approximatif"),
        box("methode", "Méthode de diagnostic en quatre étapes",
            items=["Quel est l'ancêtre positionné le plus proche ? (inspecteur)",
                   "L'élément est-il dans un contexte d'empilement ? (transform, opacity)",
                   "Quelles insertions sont définies ? (`top`, `left`, `inset`)",
                   "L'ordre du DOM permet-il l'accessibilité au clavier ?"]),
    ],
    "keypoints": [
        "`relative` garde sa place, `absolute` sort du flux.",
        "Un élément `absolute` se réfère à son ancêtre positionné le plus proche.",
        "`sticky` exige un seuil et un conteneur de défilement adapté.",
        "`z-index` ne s'applique qu'aux éléments positionnés ou flex/grid.",
        "`transform` et `opacity` créent des contextes d'empilement.",
        "`<dialog>` et `showModal()` offrent l'accessibilité native.",
        "Une échelle de `z-index` documentée évite les conflits.",
    ],
    "bridge": "Le positionnement est maîtrisé. Le chapitre suivant assemble tout cela "
              "dans une démarche responsive complète.",
    "exercises": [
        ex("Badge sur une carte",
           "Placez un badge « Nouveau » en haut à droite d'une carte, sans décaler le "
           "contenu.",
           ["Utilisez `position: relative` sur la carte.",
            "Positionnez le badge avec `inset`.",
            "Vérifiez qu'il reste lisible sur mobile."],
           [("code", """.carte { position: relative; padding: 1.25rem; }
.badge {
  position: absolute;
  inset-block-start: .75rem;
  inset-inline-end: .75rem;
  background: #e0a21b;
  color: #1f2933;
  font-size: .75rem;
  font-weight: 700;
  padding: .2rem .55rem;
  border-radius: 999px;
}"""),
            "Le badge est retiré du flux : il ne pousse ni le titre ni le texte.",
            "Sur mobile, vérifiez que le badge ne recouvre pas le titre : ajoutez un "
            "`padding-inline-end` à la zone de titre si nécessaire."]),
        ex("En-tête de tableau collant",
           "Un tableau de 80 lignes doit garder ses en-têtes visibles au défilement.",
           ["Appliquez `position: sticky` sur les `th`.",
            "Ajoutez un fond opaque.",
            "Gérez l'empilement avec `z-index`."],
           [("code", """thead th {
  position: sticky;
  top: 0;
  z-index: 2;
  background: #0f2e4c;
  color: #fff;
}
/* Le conteneur défilant doit avoir une hauteur limitée */
.tableau { max-height: 60vh; overflow: auto; }"""),
            "Sans fond opaque, les lignes défilent derrière le texte de l'en-tête.",
            "Le `z-index` évite que les cellules du corps ne recouvrent l'en-tête ; il "
            "fonctionne parce que `th` est positionné."]),
        ex("Corriger une modale inaccessible",
           "Une modale est construite avec des `div`, le fond reste cliquable et le "
           "focus s'échappe.",
           ["Remplacez la structure par `dialog`.",
            "Ajoutez un titre relié par `aria-labelledby`.",
            "Rendez le focus au déclencheur."],
           [("code", """<dialog id="suppression" aria-labelledby="titre-supp">
  <h2 id="titre-supp">Supprimer la fiche ?</h2>
  <p>Cette action ne peut pas être annulée.</p>
  <form method="dialog">
    <button value="annuler">Annuler</button>
    <button value="confirmer">Supprimer</button>
  </form>
</dialog>

<script>
const d = document.getElementById("suppression");
d.showModal();
d.addEventListener("close", () => declencheur.focus());
</script>"""),
            "`showModal()` bloque l'arrière-plan, piège le focus et ferme sur Échap.",
            "Au retour, le focus doit revenir sur le bouton qui a ouvert la boîte, "
            "sinon l'utilisateur clavier repart du début de la page."],
           level="Accessibilité"),
    ],
    "quiz": [
        quiz("Par rapport à quoi se positionne un élément `absolute` ?",
             ["Toujours la fenêtre", "Son ancêtre positionné le plus proche", "Son parent direct", "Le body"],
             1,
             "Sans ancêtre positionné, la référence est le bloc initial (la fenêtre) ; "
             "d'où l'usage courant de `relative` sur le conteneur."),
        quiz("Quel attribut est indispensable pour que `sticky` fonctionne ?",
             ["`z-index`", "`top` ou un autre seuil", "`overflow`", "`transform`"],
             1,
             "Sans seuil, l'élément n'a aucune raison de se figer : `top: 0` par "
             "exemple."),
        quiz("Qu'est-ce qui crée un contexte d'empilement ?",
             ["`z-index: 0` sur un élément statique", "`transform`, `opacity < 1`, `filter`",
              "`display: flex` seul", "`margin: auto`"],
             1,
             "Ces propriétés créent un contexte qui isole les `z-index` des enfants."),
        quiz("Quelle méthode ouvre une modale en bloquant l'arrière-plan ?",
             ["`dialog.show()`", "`dialog.showModal()`", "`dialog.open()`", "`display: block`"],
             1,
             "`showModal()` active le mode modal : fond inerte, focus piégé, fermeture "
             "par Échap."),
        quiz("Que fait `inset-block-end: 1rem` ?",
             ["Définit la marge basse logique", "Positionne à 1 rem du bas (logique)",
              "Ajoute un espacement interne", "Crée une animation"],
             1,
             "C'est l'équivalent logique de `bottom` : il s'adapte au sens d'écriture."),
    ],
}
