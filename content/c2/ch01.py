from bookkit.dsl import (box, code, defn, ex, fig, h, ol, p, quiz, table, ul)

CH = {
    "title": "La culture DevOps et ses métriques",
    "subtitle": "Pourquoi développement et exploitation se sont rapprochés, et comment "
                "mesurer honnêtement la performance d'une équipe.",
    "duration": "2 h 45",
    "level": "Débutant",
    "prereq": "chapitre 40",
    "objectives": [
        "Expliquer ce que le DevOps résout, et ce qu'il ne résout pas.",
        "Distinguer les quatre métriques DORA et leur usage.",
        "Situer les rôles de développement, d'exploitation et de fiabilité.",
        "Reconnaître les anti-patrons d'organisation.",
        "Choisir un premier chantier d'amélioration mesurable.",
    ],
    "blocks": [
        h(2, "Le problème d'origine"),
        p("Dans une organisation classique, une équipe écrit le logiciel et une autre "
          "l'exploite. La première est récompensée pour livrer vite, la seconde pour ne "
          "rien casser. Les deux optimisent des objectifs opposés, et le conflit est "
          "structurel, pas humain."),
        fig("compare", "Deux organisations, deux effets",
            ("EN SILOS", ["Livraisons rares", "Fenêtres de maintenance",
                          "Responsabilité floue en cas d'incident"],
             "EN FLUX", ["Livraisons fréquentes", "Petits changements",
                         "Responsabilité partagée"]),
            height=210),
        table(["Symptôme", "Cause organisationnelle", "Conséquence"],
              [["Livraisons trimestrielles", "Tests manuels longs", "Changements massifs"],
               ["« Ça marche chez moi »", "Environnements différents", "Incidents en production"],
               ["Personne ne sait déployer", "Connaissance tacite", "Dépendance à une personne"],
               ["Peur du déploiement", "Absence de retour arrière", "Décisions lentes"],
               ["Incidents répétés", "Aucune analyse post-mortem", "Mêmes pannes"]],
              widths=[4.2, 4.6, 4.0], first_col_bold=True,
              caption="Cinq symptômes et leurs causes"),
        defn("DevOps", "Ensemble de pratiques culturelles et techniques qui réduisent le "
                       "délai entre une idée et sa mise en production, tout en "
                       "augmentant la fiabilité. Ce n'est ni un poste ni un outil."),

        h(2, "Trois voies"),
        p("Le modèle des « trois voies » décrit les flux de valeur d'une organisation "
          "technique. Il sert de grille de lecture plus que de méthode prescriptive."),
        table(["Voie", "Principe", "Pratiques"],
              [["Flux", "Accélérer le passage du développement à la production",
                "Petits lots, automatisation, intégration continue"],
               ["Rétroaction", "Raccourcir la boucle d'information",
                "Supervision, tests en production, revues"],
               ["Apprentissage", "Cultiver l'expérimentation",
                "Post-mortems sans blâme, entraînement, kata"]],
              widths=[3.0, 4.8, 5.0], first_col_bold=True,
              caption="Trois voies et leurs pratiques"),
        p("La première voie sans la seconde produit des livraisons rapides et fragiles. "
          "La seconde sans la première produit une organisation qui comprend ses pannes "
          "mais ne livre pas. Les trois se tiennent."),

        h(2, "Les quatre métriques DORA"),
        p("Quatre indicateurs, issus de plusieurs années d'études, décrivent la "
          "performance de livraison sans mesurer les individus."),
        table(["Métrique", "Définition", "Bon ordre de grandeur"],
              [["Fréquence de déploiement", "Nombre de mises en production par période",
                "Plusieurs par jour"],
               ["Délai de livraison", "Du commit à la production", "Moins d'une heure"],
               ["Taux d'échec des changements", "Part des déploiements causant un incident",
                "Moins de 15 %"],
               ["Temps de rétablissement", "Durée de restauration après incident",
                "Moins d'une heure"]],
              widths=[4.2, 5.4, 3.0], first_col_bold=True,
              caption="Quatre métriques et leurs ordres de grandeur"),
        box("attention", "Ces métriques ne mesurent pas des personnes",
            "Utilisées pour évaluer une équipe ou un individu, elles sont détournées : "
            "on cesse de livrer pour améliorer le taux d'échec, ou l'on découpe les "
            "changements pour améliorer la fréquence. Elles décrivent un système."),
        fig("flow", "Le trajet mesuré par DORA",
            ["Idée validée",
             "Premier commit",
             "Intégration continue",
             "Déploiement en production",
             "Incident éventuel",
             "Rétablissement"],
            height=250),
        code("""# Mesurer le délai de livraison depuis l'historique Git
git log --merges --first-parent main \\
  --format="%h %ad %s" --date=iso | head -20

# Comparer deux périodes
git log --since="2026-01-01" --until="2026-04-01" --oneline | wc -l""",
             "bash", "Un premier indicateur, sans outil dédié"),

        h(2, "Les rôles"),
        p("Le DevOps n'efface pas les spécialités : il change leur point de contact. "
          "Trois familles de responsabilités coexistent dans une équipe mature."),
        table(["Rôle", "Responsabilité principale", "Piège"],
              [["Développement", "Fonctionnalité et qualité du code", "Ignorer la production"],
               ["Exploitation", "Disponibilité et capacité", "Devenir un guichet"],
               ["SRE", "Fiabilité mesurée par des objectifs", "Confondre avec support"],
               ["Plateforme", "Outils et parcours self-service", "Construire trop tôt"],
               ["Sécurité", "Menaces et conformité", "Arriver en fin de chaîne"]],
              widths=[3.2, 5.4, 4.2], first_col_bold=True,
              caption="Cinq rôles et leurs pièges"),
        defn("SRE", "Site Reliability Engineering : application des pratiques "
                    "d'ingénierie logicielle à l'exploitation, avec des objectifs de "
                    "niveau de service explicites et un budget d'erreur."),
        p("L'équipe de plateforme mérite une mention particulière : elle ne livre pas "
          "les applications, elle rend les autres équipes autonomes. Une plateforme "
          "construite avant d'avoir des utilisateurs est une dette, pas un actif."),

        h(2, "Les anti-patrons"),
        p("Beaucoup d'initiatives DevOps échouent pour des raisons identifiables. Les "
          "reconnaître tôt évite plusieurs mois d'efforts inutiles."),
        table(["Anti-patron", "Manifestation", "Alternative"],
              [["Équipe « DevOps » isolée", "Elle déploie pour les autres",
                "Autonomiser les équipes produit"],
               ["Automatisation du chaos", "Scripts non versionnés",
                "Tout dans le dépôt, revu"],
               ["Pipeline théâtral", "Vert sans test réel", "Tests qui peuvent échouer"],
               ["Culte de l'outil", "Kubernetes pour un site vitrine",
                "Commencer par le problème"],
               ["Post-mortem accusatoire", "« Qui a cassé ? »", "« Quel garde-fou manquait ? »"]],
              widths=[4.2, 4.6, 4.4], first_col_bold=True,
              caption="Cinq anti-patrons"),
        box("pratique", "Post-mortem sans blâme",
            "Un compte rendu d'incident décrit les faits, la chronologie, les hypothèses "
            "et les actions correctives. Il ne nomme pas de coupable : la personne qui "
            "a déclenché l'incident est celle qui avait le droit d'agir, et le système "
            "lui a permis de se tromper."),

        h(2, "Par où commencer"),
        p("Une transformation commence par un chantier mesurable, choisi pour son "
          "rapport entre effort et douleur évitée. Trois candidats reviennent presque "
          "toujours."),
        ol("**Réduire le délai de déploiement** : supprimer les étapes manuelles.",
           "**Augmenter la fréquence** : livrer par petits lots plus souvent.",
           "**Réduire le temps de rétablissement** : préparer le retour arrière."),
        code("""# Premier chantier : un déploiement en une commande
./scripts/deploy.sh production

# Ce qu'il doit faire, dans l'ordre
# 1. Construire un artefact reproductible
# 2. Exécuter les tests
# 3. Publier avec une version identifiable
# 4. Basculer le trafic
# 5. Vérifier la santé
# 6. Savoir revenir à la version précédente""", "bash",
             "Une cible simple et vérifiable"),
        box("methode", "Les trois questions d'un premier diagnostic",
            items=["Combien de temps s'écoule entre un commit et la production ?",
                   "Quelles étapes de ce trajet sont manuelles ?",
                   "Combien de temps faut-il pour revenir en arrière ?"]),
    ],
    "keypoints": [
        "Le DevOps réunit développement et exploitation autour d'un objectif commun.",
        "Trois voies : flux, rétroaction, apprentissage.",
        "DORA mesure la fréquence, le délai, le taux d'échec et le rétablissement.",
        "Ces métriques décrivent un système, jamais des individus.",
        "Le SRE fixe des objectifs de fiabilité explicites.",
        "Une équipe plateforme sert les autres équipes.",
        "Un post-mortem sans blâme améliore le système, pas la réputation.",
    ],
    "bridge": "La culture est posée ; reste le terrain. Le chapitre suivant entre dans "
              "le système d'exploitation qui héberge tout le reste : Linux.",
    "exercises": [
        ex("Mesurer son propre délai de livraison",
           "Choisissez trois déploiements récents et calculez le délai.",
           ["Relevez l'heure du dernier commit.",
            "Relevez l'heure de mise en production.",
            "Identifiez l'étape la plus longue."],
           ["Le délai se mesure du commit à la production, pas de la fin du "
            "développement au déploiement.",
            "L'étape la plus longue est souvent l'attente d'une validation manuelle, "
            "pas l'exécution technique.",
            ("code", """# Pour chaque déploiement
git log -1 --format=%cI <sha-du-commit>
# ... comparer avec l'horodatage du déploiement
# Reporter dans un tableau : commit | déploiement | durée""")]),
        ex("Écrire un post-mortem",
           "Un certificat expiré a rendu le site indisponible 40 minutes.",
           ["Décrivez la chronologie.",
            "Identifiez les garde-fous absents.",
            "Proposez trois actions datées."],
           [("markdown", """# Incident du 12 mars — certificat TLS expiré

## Chronologie
- 08:02 — premier signalement utilisateur
- 08:09 — alerte de supervision, prise en compte
- 08:21 — cause identifiée
- 08:42 — certificat renouvelé, service rétabli

## Causes
Le renouvellement était manuel et la date n'était suivie nulle part.
Aucune alerte n'existait à J-15.

## Actions
| Action | Responsable | Échéance |
|--------|-------------|----------|
| Renouvellement automatique | Équipe plateforme | 20 mars |
| Alerte à J-21 et J-7 | Équipe plateforme | 27 mars |
| Test de disponibilité externe | Astreinte | 10 avril |"""),
            "La chronologie distingue la détection, le diagnostic et le rétablissement : "
            "ce sont trois délais différents à améliorer.",
            "Chaque action a un responsable et une date, sinon elle ne sera pas faite."],
           level="Organisation"),
        ex("Choisir un premier chantier",
           "Votre équipe déploie tous les deux mois, avec quatre heures d'arrêt.",
           ["Calculez le coût de l'attente.",
            "Proposez un objectif à trois mois.",
            "Définissez l'indicateur de succès."],
           ["Un déploiement bimestriel de quatre heures limite à six livraisons par "
            "an : chaque correction attend en moyenne un mois.",
            "Objectif réaliste : un déploiement hebdomadaire automatisé en trois mois, "
            "sans augmenter les incidents.",
            "Indicateur : durée du déploiement, nombre de déploiements, taux d'échec, "
            "temps de retour arrière."],
           level="Stratégie"),
    ],
    "quiz": [
        quiz("Que désigne le DevOps ?",
             ["Un poste dans l'équipe", "Un ensemble de pratiques culturelles et techniques",
              "Un outil de déploiement", "Une certification"],
             1,
             "Le DevOps est une culture et un ensemble de pratiques, pas un rôle isolé."),
        quiz("Quelle métrique DORA mesure la rapidité de rétablissement ?",
             ["Fréquence de déploiement", "Délai de livraison",
              "Taux d'échec des changements", "Temps de rétablissement"],
             3,
             "Le temps de rétablissement mesure la durée entre l'incident et le retour "
             "à la normale."),
        quiz("Pourquoi éviter d'utiliser DORA pour évaluer des individus ?",
             ["Les chiffres sont faux", "Cela détourne les comportements",
              "Ce n'est pas assez précis", "C'est trop coûteux"],
             1,
             "Les métriques perdent leur sens dès qu'elles deviennent un critère "
             "d'évaluation personnelle."),
        quiz("Quel est le rôle d'une équipe plateforme ?",
             ["Déployer à la place des équipes", "Rendre les équipes autonomes",
              "Surveiller les développeurs", "Écrire la documentation"],
             1,
             "Elle fournit des outils et des parcours en libre-service."),
        quiz("Que contient un post-mortem sans blâme ?",
             ["Les noms des responsables", "Une chronologie et des actions correctives",
              "Une sanction", "Un rapport financier"],
             1,
             "Il documente les faits et les garde-fous à ajouter, sans accuser."),
    ],
}
