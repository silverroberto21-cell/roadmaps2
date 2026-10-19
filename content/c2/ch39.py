from bookkit.dsl import (box, code, defn, ex, fig, h, ol, p, quiz, table, ul)

CH = {
    "title": "SRE : objectifs de fiabilité et gestion d'incident",
    "subtitle": "Décider combien de fiabilité suffit, mesurer l'écart et apprendre de "
                "chaque panne.",
    "duration": "3 h 30",
    "level": "Avancé",
    "prereq": "chapitre 78",
    "objectives": [
        "Définir un indicateur et un objectif de fiabilité.",
        "Calculer un budget d'erreur et l'utiliser pour décider.",
        "Organiser une réponse à incident.",
        "Conduire une analyse sans reproche.",
        "Éviter les pièges des objectifs mal calibrés.",
    ],
    "blocks": [
        h(2, "Fiabilité mesurable"),
        p("Un indicateur de niveau de service (SLI) décrit une expérience utilisateur ; un "
          "objectif de niveau de service (SLO) fixe la valeur visée ; un accord de niveau "
          "de service (SLA) engage juridiquement, avec compensation."),
        table(["Terme", "Définition", "Exemple"],
              [["SLI", "Mesure de l'expérience", "95 % des requêtes < 400 ms"],
               ["SLO", "Cible interne", "99,9 % de disponibilité mensuelle"],
               ["SLA", "Engagement contractuel", "99,5 %, sinon avoir"],
               ["Budget d'erreur", "Marge de manœuvre", "0,1 % = 43 min / mois"]],
              widths=[3.6, 5.0, 4.4], first_col_bold=True,
              caption="Quatre termes"),
        defn("Budget d'erreur", "Complément de l'objectif : pour 99,9 % sur 30 jours, le "
                                "budget est de 0,1 %, soit environ 43 minutes "
                                "d'indisponibilité. Il se consomme et se recharge."),
        code("""# Calcul du budget mensuel
# 30 jours = 43 200 minutes
# 99,9 %  → 43,2 min
# 99,95 % → 21,6 min
# 99,0 %  → 432 min (7 h 12)

# Le budget se consomme par événement, pas seulement par panne totale
# 1 % d'erreurs pendant une heure sur 43 200 min de trafic
# = 0,01 × 60 / 43 200 = 0,0014 % du budget""", "text", "Un calcul simple"),
        box("attention", "99,99 % n'est pas toujours un objectif raisonnable",
            "Quatre neufs imposent une redondance, des procédures et une astreinte "
            "permanente. Si l'utilisateur ne distingue pas 99,9 % de 99,99 %, le second "
            "coûte beaucoup plus cher sans bénéfice perçu."),

        h(2, "Choisir un indicateur"),
        p("Un bon indicateur est mesuré côté utilisateur, sur une fenêtre glissante, et "
          "correspond à ce qui compte réellement : une requête réussie et rapide."),
        fig("flow", "Construire un indicateur",
            ["Quel parcours utilisateur ?",
             "Quel événement compte comme réussi ?",
             "Quel seuil de latence ?",
             "Quelle fenêtre de mesure ?",
             "Quel objectif réaliste ?"],
            height=225),
        table(["Indicateur", "Formule", "Piège"],
              [["Disponibilité", "Requêtes non 5xx / total", "Une erreur 200 peut être un échec"],
               ["Latence", "Requêtes < seuil / total", "La moyenne masque la queue"],
               ["Freshness", "Données à jour / total", "Ignoré lors des incidents"],
               ["Taux d'échec", "Échecs / tentatives", "Ignore les abandons"]],
              widths=[3.8, 4.6, 4.6], first_col_bold=True,
              caption="Quatre indicateurs"),
        code("""# Un indicateur explicite
# SLI : proportion de requêtes /panier réussies en moins de 400 ms
# SLO : 99,9 % sur une fenêtre glissante de 30 jours

# Expression PromQL
(
  sum(rate(http_request_duration_seconds_bucket{route="/panier",le="0.4"}[5m]))
  - sum(rate(http_requests_total{route="/panier",status=~"5.."}[5m]))
)
/
sum(rate(http_requests_total{route="/panier"}[5m]))""", "promql",
             "Un indicateur mesuré"),
        table(["Objectif", "Indisponibilité mensuelle", "Redondance nécessaire"],
              [["99 %", "7 h 12", "Simple"],
               ["99,9 %", "43 min", "Multi-zone"],
               ["99,95 %", "22 min", "Bascule automatique"],
               ["99,99 %", "4 min", "Multi-région"]],
              widths=[3.6, 5.4, 5.0], first_col_bold=True,
              caption="Quatre objectifs et leurs coûts"),

        h(2, "Utiliser le budget"),
        p("Le budget d'erreur est un outil de décision, pas une statistique décorative. "
          "Tant qu'il reste du budget, on peut livrer plus vite ; quand il est épuisé, la "
          "fiabilité passe avant les fonctionnalités."),
        table(["État du budget", "Décision", "Conséquence"],
              [["> 50 %", "Livraisons normales", "Rythme habituel"],
               ["20 à 50 %", "Vigilance", "Revue des changements risqués"],
               ["< 20 %", "Ralentissement", "Priorité aux corrections"],
               ["Épuisé", "Gel des fonctionnalités", "Travail de fiabilité uniquement"]],
              widths=[4.0, 4.6, 4.4], first_col_bold=True,
              caption="Quatre états"),
        code("""# Consommation du budget sur 30 jours
1 - (
  sum(increase(http_requests_total{status!~"5.."}[30d]))
  /
  sum(increase(http_requests_total[30d]))
)

# Alerte quand il reste moins de 20 %
# (à exprimer sur la fenêtre glissante de l'objectif)""", "promql",
             "Deux mesures"),
        box("pratique", "Un budget qui n'a jamais été consommé est mal calibré",
            "Si l'objectif est atteint chaque mois avec une marge énorme, il est trop "
            "prudent : l'équipe investit dans une fiabilité que personne ne remarque. Un "
            "objectif utile est atteint avec quelques incidents évités de justesse."),

        h(2, "Répondre à un incident"),
        p("La réponse à incident est un rôle, pas une improvisation. La personne qui "
          "coordonne ne répare pas : elle organise, décide et communique."),
        table(["Rôle", "Responsabilité", "Ne fait pas"],
              [["Commandant d'incident", "Coordonner et décider", "Le diagnostic technique"],
               ["Enquêteur", "Diagnostiquer et corriger", "La communication externe"],
               ["Scribe", "Chronologie et décisions", "Les manipulations"],
               ["Communication", "Informer les parties", "Les modifications système"]],
              widths=[4.2, 4.8, 4.8], first_col_bold=True,
              caption="Quatre rôles"),
        ol("**Déclarer** : ouvrir un canal dédié et nommer un commandant.",
           "**Évaluer** : mesurer l'impact utilisateur et la sévérité.",
           "**Contenir** : stabiliser, quitte à dégrader une fonctionnalité.",
           "**Informer** : donner une heure de prochaine mise à jour.",
           "**Corriger** : appliquer le correctif le plus sûr, pas le plus élégant.",
           "**Clore** : vérifier le retour à la normale et planifier l'analyse."),
        code("""# Modèle de mise à jour, toutes les 30 minutes
[14:35] Incident INC-2026-041 — service de paiement
Impact : 12 % des paiements refusés depuis 14:12.
Cause probable : expiration d'un certificat interne.
Action en cours : bascule sur le certificat de secours.
Prochaine mise à jour : 15:05.""", "text", "Une communication utile"),
        box("attention", "Ne jamais redémarrer sans comprendre",
            "Un redémarrage qui « résout » le problème efface les preuves. Il est parfois "
            "nécessaire pour rétablir le service, mais il doit être consigné et suivi "
            "d'une analyse sur les données conservées."),

        h(2, "Analyser sans reproche"),
        p("Une analyse sans reproche cherche les causes systémiques : qu'est-ce qui a "
          "rendu l'erreur possible, indétectable ou coûteuse ? Elle produit des actions "
          "vérifiables, pas des promesses."),
        table(["Question", "Objectif", "Exemple de réponse"],
              [["Que s'est-il passé ?", "Chronologie factuelle", "Horodatage des événements"],
               ["Pourquoi est-ce arrivé ?", "Chaîne de causes", "Certificat non renouvelé"],
               ["Pourquoi n'a-t-on pas vu ?", "Détection", "Aucune alerte d'expiration"],
               ["Pourquoi si long ?", "Réponse", "Runbook absent"],
               ["Qu'est-ce qui change ?", "Actions", "Alerte + renouvellement automatique"]],
              widths=[4.4, 4.4, 4.8], first_col_bold=True,
              caption="Cinq questions"),
        code("""# Une action d'analyse est vérifiable si elle a un propriétaire, une date
# et un critère de réussite

- Action : ajouter une alerte à J-21 sur l'expiration des certificats
  Propriétaire : équipe plateforme
  Échéance : 2026-11-05
  Critère : une alerte de test déclenchée sur un certificat à J-21

- Action : automatiser le renouvellement ACME sur le certificat interne
  Propriétaire : équipe réseau
  Échéance : 2026-11-19
  Critère : renouvellement observé sans intervention""", "text",
             "Deux actions recevables"),
        table(["Anti-patron", "Pourquoi c'est inutile", "Remplacer par"],
              [["« Faire plus attention »", "Non vérifiable", "Contrôle automatisé"],
               ["« Ajouter des tests »", "Trop vague", "Test précis sur le scénario"],
               ["« Mettre à jour la documentation »", "Sans échéance", "Page et date"],
               ["« Améliorer la supervision »", "Sans critère", "Alerte nommée"]],
              widths=[4.6, 4.4, 4.6], first_col_bold=True,
              caption="Quatre anti-patrons"),
        box("methode", "Mettre en place une pratique SRE",
            items=["Un indicateur par parcours critique, pas vingt.",
                   "Un objectif négocié avec le produit.",
                   "Un tableau de bord public du budget.",
                   "Une astreinte avec des règles claires.",
                   "Une analyse sans reproche pour chaque incident majeur."]),
    ],
    "keypoints": [
        "SLI mesure, SLO cible, SLA engage.",
        "Le budget d'erreur rend la fiabilité négociable.",
        "99,9 % équivaut à environ 43 minutes par mois.",
        "Le budget pilote le rythme de livraison.",
        "Un budget jamais consommé signale un objectif trop bas.",
        "La réponse à incident distribue des rôles explicites.",
        "Redémarrer efface les preuves.",
        "Une action d'analyse a un propriétaire et une échéance.",
    ],
    "bridge": "Les principes sont posés. Le dernier chapitre les applique dans un projet "
              "complet, du commit à la production.",
    "exercises": [
        ex("Calculer un budget",
           "Un service vise 99,95 % sur 30 jours.",
           ["Calculez les minutes.",
            "Estimez la consommation.",
            "Décidez."],
           [("text", """# 30 jours = 43 200 minutes
# 99,95 % → 0,05 % × 43 200 = 21,6 minutes

# Incident de 12 minutes → 55 % du budget consommé
# Deux incidents de 8 minutes → 74 %

# Décision : budget sous 20 %, gel des fonctionnalités
# jusqu'à la correction des deux causes racines"""),
            "Le budget se calcule sur la fenêtre de l'objectif, pas sur le mois calendaire.",
            "La décision doit être prise à l'avance, sinon elle devient une négociation "
            "sous pression."]),
        ex("Définir un indicateur",
           "Le parcours de paiement doit être mesuré.",
           ["Choisissez l'événement.",
            "Fixez le seuil.",
            "Écrivez la requête."],
           [("promql", """# SLI : proportion de paiements réussis en moins de 800 ms
(
  sum(rate(http_request_duration_seconds_bucket{
    route="/paiement", le="0.8"}[5m]))
  - sum(rate(http_requests_total{
    route="/paiement", status=~"5.."}[5m]))
)
/
sum(rate(http_requests_total{route="/paiement"}[5m]))

# SLO : 99,5 % sur 30 jours glissants"""),
            "Le seuil de 800 ms doit venir d'une mesure d'acceptation, pas d'une "
            "intuition.",
            "Soustraire les erreurs évite de compter une réponse rapide mais en échec."]),
        ex("Conduire une analyse",
           "Un certificat expiré a provoqué 40 minutes d'indisponibilité.",
           ["Reconstituez la chronologie.",
            "Cherchez les causes systémiques.",
            "Écrivez deux actions vérifiables."],
           [("markdown", """## Chronologie
14:02 — premier échec TLS
14:07 — alerte de taux d'erreur (5 min de latence de détection)
14:15 — commandant nommé, enquête
14:28 — cause identifiée (certificat expiré à 13:59)
14:42 — certificat remplacé, service rétabli

## Causes systémiques
- Renouvellement manuel, sans rappel
- Aucune alerte d'expiration
- Runbook absent

## Actions
- Alerte à J-21 (plateforme, 2026-11-05)
- Renouvellement ACME automatisé (réseau, 2026-11-19)"""),
            "La latence de détection est une cause à part entière.",
            "Deux actions tenables valent mieux que dix intentions."],
           level="Incident"),
    ],
    "quiz": [
        quiz("Que mesure un SLI ?",
             ["Une cible", "Un engagement contractuel", "L'expérience réelle",
              "Un budget"],
             2,
             "C'est la mesure observée, avant toute cible."),
        quiz("Combien de minutes représente 99,9 % sur 30 jours ?",
             ["4 minutes", "43 minutes", "7 heures", "21 minutes"],
             1,
             "0,1 % de 43 200 minutes ≈ 43 minutes."),
        quiz("Que faire quand le budget d'erreur est épuisé ?",
             ["Accélérer", "Geler les fonctionnalités et fiabiliser",
              "Baisser l'objectif", "Ignorer"],
             1,
             "La règle est décidée à l'avance pour éviter les arbitrages sous pression."),
        quiz("Pourquoi une analyse sans reproche ?",
             ["Pour éviter les sanctions", "Pour trouver les causes systémiques",
              "Pour aller plus vite", "Pour la conformité"],
             1,
             "La blame culture fait taire les informations nécessaires."),
        quiz("Quelle action est recevable ?",
             ["« Faire attention »", "« Améliorer la supervision »",
              "« Alerte à J-21, propriétaire et date »", "« Ajouter des tests »"],
             2,
             "Elle est vérifiable et assignée."),
    ],
}
