from bookkit.dsl import (box, code, defn, ex, fig, h, ol, p, quiz, table, ul)

CH = {
    "title": "Transitions et animations",
    "subtitle": "Le mouvement guide l'attention, signale un changement d'état et "
                "raconte une relation de cause à effet. À petite dose.",
    "duration": "2 h 30",
    "level": "Intermédiaire",
    "prereq": "chapitre 15",
    "objectives": [
        "Distinguer transition, transformation et animation.",
        "Animer les propriétés qui ne déclenchent pas de recalcul de mise en page.",
        "Respecter `prefers-reduced-motion`.",
        "Concevoir des animations utiles, jamais décoratives à l'excès.",
        "Diagnostiquer une animation saccadée.",
    ],
    "blocks": [
        h(2, "Trois mécanismes distincts"),
        p("Une **transition** interpole entre deux états lorsqu'une propriété change. "
          "Une **transformation** déplace, tourne ou redimensionne sans modifier le "
          "flux. Une **animation** suit des étapes définies par `@keyframes`, "
          "éventuellement en boucle."),
        table(["Mécanisme", "Déclencheur", "Durée", "Usage"],
              [["`transition`", "Changement d'état", "Automatique", "Survol, focus, ouverture"],
               ["`transform`", "Propriété appliquée", "Instantanée ou animée", "Déplacement, échelle, rotation"],
               ["`@keyframes`", "Application de `animation`", "Contrôlée image par image", "Chargement, attention, boucle"]],
              widths=[2.4, 3.4, 2.4, 4.2], first_col_bold=True,
              caption="Trois façons de produire du mouvement"),
        code(""".bouton {
  transition: background-color .18s ease, transform .18s ease;
}
.bouton:hover { background: #274b6d; }
.bouton:active { transform: translateY(1px); }

.carte:hover { transform: translateY(-2px); box-shadow: 0 12px 28px rgb(15 46 76 / 14%); }""",
             "css", "Deux transitions sobres et utiles"),
        defn("Compositeur", "Partie du navigateur qui assemble les couches visuelles. "
                            "Les propriétés `transform` et `opacity` y sont traitées "
                            "sans recalcul de mise en page, ce qui les rend fluides."),

        h(2, "Ce qu'il faut animer"),
        p("Toutes les propriétés ne se valent pas. Animer `width`, `height`, `top` ou "
          "`margin` force le navigateur à recalculer la mise en page à chaque image : "
          "l'animation saccade sur les machines modestes."),
        table(["Propriété", "Coût", "Recommandation"],
              [["`transform`", "Faible (compositeur)", "À privilégier"],
               ["`opacity`", "Faible (compositeur)", "À privilégier"],
               ["`filter`", "Moyen", "Avec parcimonie"],
               ["`background-color`", "Moyen (peinture)", "Acceptable"],
               ["`width` / `height`", "Élevé (mise en page)", "Éviter"],
               ["`top` / `left`", "Élevé", "Remplacer par `transform`"],
               ["`box-shadow`", "Élevé (peinture)", "Limiter aux petits éléments"]],
              widths=[3.2, 3.8, 4.0], first_col_bold=True,
              caption="Coût des propriétés animées"),
        code("""/* À éviter : anime la mise en page */
.panneau { transition: height .3s; }

/* À privilégier : transform et opacity */
.panneau {
  transform: translateY(-100%);
  transition: transform .3s cubic-bezier(.2, .8, .2, 1);
}
.panneau.ouvert { transform: translateY(0); }""", "css",
             "Déplacer un panneau sans recalculer la page"),
        box("pratique", "`will-change`, à utiliser avec parcimonie",
            "`will-change: transform` prévient le navigateur qu'une propriété va "
            "changer et lui permet de préparer une couche. Appliqué à tous les "
            "éléments, il consomme de la mémoire et dégrade les performances."),

        h(2, "Courbes et durées"),
        p("La durée et la courbe d'accélération donnent le caractère du mouvement. "
          "Trop lent, il paraît lourd ; trop rapide, il devient imperceptible. Les "
          "interfaces réactives se situent entre 150 et 300 millisecondes."),
        fig("compare", "Deux courbes, deux sensations",
            ("ease-in-out", ["Départ et arrivée doux", "Naturel pour un panneau",
                             "Durée 250-300 ms"],
             "cubic-bezier(.2,.8,.2,1)", ["Départ rapide, arrivée douce",
                                          "Sensation de réactivité", "Durée 200 ms"]),
            height=190),
        code(""":root {
  --duree-rapide: 150ms;
  --duree-normale: 250ms;
  --duree-lente: 400ms;
  --courbe-standard: cubic-bezier(.2, .8, .2, 1);
  --courbe-entree: cubic-bezier(.05, .7, .1, 1);
  --courbe-sortie: cubic-bezier(.3, 0, .8, .15);
}""", "css", "Trois durées et trois courbes, réutilisables"),
        p("Une animation d'entrée peut être plus longue que celle de sortie : "
          "l'utilisateur attend l'apparition, mais souhaite retrouver son contexte "
          "rapidement. C'est un principe constant des interfaces soignées."),

        h(2, "Animations déclaratives"),
        p("`@keyframes` définit une séquence d'états. L'animation s'applique avec "
          "`animation`, qui accepte le nom, la durée, la courbe, le délai, le nombre "
          "de répétitions et le mode de remplissage."),
        code("""@keyframes apparition {
  from { opacity: 0; transform: translateY(8px); }
  to   { opacity: 1; transform: translateY(0); }
}

.message {
  animation: apparition 280ms var(--courbe-standard) both;
}

@keyframes pulsation {
  0%, 100% { opacity: 1; }
  50%      { opacity: .45; }
}
.chargement { animation: pulsation 1.4s ease-in-out infinite; }""", "css",
             "Deux animations : apparition et chargement"),
        table(["Propriété", "Rôle", "Valeur typique"],
              [["`animation-name`", "Nom du `@keyframes`", "`apparition`"],
               ["`animation-duration`", "Durée", "280ms"],
               ["`animation-timing-function`", "Courbe", "`cubic-bezier(...)`"],
               ["`animation-delay`", "Délai", "0 à 120ms"],
               ["`animation-iteration-count`", "Répétitions", "1 ou `infinite`"],
               ["`animation-fill-mode`", "État hors animation", "`both`"]],
              widths=[4.2, 3.4, 3.4], first_col_bold=True,
              caption="Six propriétés d'animation"),

        h(2, "Mouvement et accessibilité"),
        p("Certaines personnes souffrent de troubles vestibulaires : un mouvement "
          "ample, un parallaxe ou un zoom brutal peut provoquer nausée et vertige. La "
          "préférence système `prefers-reduced-motion` doit être respectée."),
        code("""@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}""", "css", "Neutraliser le mouvement sans casser les interfaces"),
        p("Réduire le mouvement ne signifie pas supprimer toute information : le "
          "changement d'état doit rester perceptible autrement — un changement de "
          "couleur, une icône, un texte."),
        box("attention", "Trois animations à éviter",
            items=["Le clignotement de plus de trois fois par seconde (risque de crise).",
                   "Le défilement automatique d'un carrousel sans bouton de pause.",
                   "Le zoom à l'entrée qui décale le contenu environnant."]),

        h(2, "Diagnostiquer une animation saccadée"),
        p("Une animation saccadée vient de trois causes : une propriété coûteuse, un "
          "travail excessif exécuté à chaque image, ou une couche compositeur "
          "saturée."),
        code("""/* Diagnostiquer dans les outils du navigateur */
/* 1. Ouvrir l'onglet Performance */
/* 2. Enregistrer 3 secondes pendant l'animation */
/* 3. Repérer les images > 16 ms (vertes = peinture, rouges = script) */""",
             "text", "Une méthode de mesure, pas une intuition"),
        table(["Symptôme", "Cause", "Correction"],
              [["Saccades régulières", "Propriété de mise en page animée", "Passer à `transform`"],
               ["Début d'animation lent", "Calcul initial trop lourd", "Préparer avec `will-change`"],
               ["Décalage du contenu", "Propriété qui modifie le flux", "Utiliser une transformation"],
               ["Batterie qui chauffe", "Animation infinie", "Limiter la durée, arrêter hors écran"]],
              widths=[3.4, 4.2, 3.4], first_col_bold=True,
              caption="Quatre symptômes d'animation et leur cause"),
        box("methode", "La règle des trois questions",
            items=["Cette animation apporte-t-elle une information ?",
                   "Que se passe-t-il si elle est désactivée ?",
                   "Dure-t-elle moins de 300 ms, sauf exception justifiée ?"]),
    ],
    "keypoints": [
        "Transition, transformation et animation répondent à trois besoins distincts.",
        "`transform` et `opacity` s'animent sans recalcul de mise en page.",
        "150 à 300 ms suffisent pour la plupart des transitions d'interface.",
        "Les durées et les courbes se définissent comme des variables.",
        "`prefers-reduced-motion` doit toujours être respecté.",
        "Une information ne doit jamais dépendre du mouvement seul.",
        "Une saccade se mesure dans l'onglet Performance, pas au ressenti.",
    ],
    "bridge": "La présentation est complète : typographie, couleurs, boîtes, "
              "composants, mouvement. La partie suivante passe à l'architecture et aux "
              "mises en page modernes.",
    "exercises": [
        ex("Animer un panneau latéral",
           "Créez un panneau qui glisse depuis la droite sans recalculer la page.",
           ["Utilisez `transform`.",
            "Ajoutez une transition réversible.",
            "Respectez les préférences de mouvement."],
           [("code", """.panneau {
  position: fixed;
  inset-block: 0;
  inset-inline-end: 0;
  width: min(22rem, 90vw);
  background: #fff;
  transform: translateX(100%);
  transition: transform .28s cubic-bezier(.2,.8,.2,1);
  box-shadow: -8px 0 30px rgb(15 46 76 / 18%);
}
.panneau[data-ouvert="true"] { transform: translateX(0); }

@media (prefers-reduced-motion: reduce) {
  .panneau { transition: none; }
}"""),
            "Le panneau reste dans le flux visuel mais hors écran ; `translateX(100%)` "
            "le place à droite sans jamais modifier la largeur du body.",
            "Sans transition, l'ouverture reste instantanée : l'information est "
            "conservée, seule l'animation disparaît."]),
        ex("Concevoir une animation de chargement",
           "Un bouton déclenche un envoi de formulaire qui dure une seconde.",
           ["Affichez un état de chargement dans le bouton.",
            "Empêchez le double envoi.",
            "Annoncez l'état aux technologies d'assistance."],
           [("code", """<button class="bouton" aria-busy="false">
  <span class="bouton__texte">Envoyer</span>
</button>

<style>
.bouton[aria-busy="true"] { cursor: progress; }
.bouton[aria-busy="true"] .bouton__texte::after {
  content: "";
  display: inline-block;
  width: .8em; height: .8em;
  margin-inline-start: .5em;
  border: 2px solid currentColor;
  border-inline-end-color: transparent;
  border-radius: 50%;
  animation: rotation .8s linear infinite;
}
@keyframes rotation { to { transform: rotate(1turn); } }
</style>"""),
            "`aria-busy=\"true\"` annonce le traitement ; le bouton reçoit `disabled` "
            "pendant l'envoi pour empêcher le double clic.",
            "Le mouvement du cercle est décoratif ; il est neutralisé par "
            "`prefers-reduced-motion` et remplacé par le texte « Envoi en cours… »."],
           level="Application"),
        ex("Corriger une animation coûteuse",
           "Cette animation fait saccader la page.",
           ["`.menu { transition: height .4s; }`",
            "`.carte:hover { margin-top: -8px; transition: margin .3s; }`",
            "`.fond { animation: deplacement 8s infinite; }` avec `background-position`"],
           ["Animer `height` recalcule la mise en page : préférer `transform: scaleY` "
            "ou une grille avec `grid-template-rows: 0fr → 1fr` si la hauteur doit "
            "réellement varier.",
            "Animer `margin` décale le contenu environnant : `transform: translateY(-8px)` "
            "produit le même effet sans reflow.",
            "`background-position` force une repeinture à chaque image : déplacer un "
            "pseudo-élément avec `transform` est beaucoup plus économique."],
           level="Diagnostic"),
    ],
    "quiz": [
        quiz("Quelle propriété s'anime sans recalcul de mise en page ?",
             ["`height`", "`margin`", "`transform`", "`top`"],
             2,
             "`transform` est traitée par le compositeur, comme `opacity`, sans "
             "recalcul du flux."),
        quiz("Quelle durée convient à une transition d'interface ?",
             ["10 ms", "150 à 300 ms", "1 s", "5 s"],
             1,
             "En dessous, le changement est imperceptible ; au-delà, l'interface "
             "paraît lente."),
        quiz("Que déclenche `prefers-reduced-motion: reduce` ?",
             ["Une désactivation du CSS",
              "Une préférence utilisateur pour limiter le mouvement",
              "Un mode sombre",
              "Une réduction de la résolution"],
             2 if False else 1,
             "Cette media query reflète un réglage système : l'utilisateur demande "
             "moins d'animations, souvent pour des raisons de santé."),
        quiz("Que fait `animation-fill-mode: both` ?",
             ["Elle répète l'animation",
              "Elle conserve les styles de début et de fin",
              "Elle inverse l'animation",
              "Elle la met en pause"],
             1,
             "`both` applique l'état initial avant le démarrage et l'état final après "
             "la fin, ce qui évite les retours brutaux."),
        quiz("Pourquoi éviter un carrousel à défilement automatique ?",
             ["Il consomme trop de mémoire",
              "Il peut déclencher des troubles vestibulaires et voler le contrôle",
              "Il n'est pas supporté",
              "Il empêche le référencement"],
             1,
             "Un mouvement automatique non pausable gêne l'attention et peut "
             "provoquer un malaise ; il doit au minimum proposer une pause."),
    ],
}
