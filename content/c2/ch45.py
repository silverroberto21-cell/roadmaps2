from bookkit.dsl import (box, code, defn, ex, fig, h, ol, p, quiz, table, ul)

CH = {
    "title": "Plateforme interne et chemins d'or",
    "subtitle": "Faire de l'infrastructure un produit qui accélère les équipes au lieu "
                "de les ralentir.",
    "duration": "3 h 00",
    "level": "Avancé",
    "prereq": "chapitres 73 à 76",
    "objectives": [
        "Distinguer plateforme et tuyauterie.",
        "Définir un chemin d'or et son contrat.",
        "Concevoir un modèle de service réutilisable.",
        "Mesurer l'adoption et le délai de mise en production.",
        "Éviter la plateforme qui devient un goulot.",
    ],
    "blocks": [
        h(2, "Une plateforme est un produit"),
        p("Une plateforme interne fournit des capacités prêtes à l'emploi : déploiement, "
          "observabilité, secrets, bases, environnements. Comme un produit, elle a des "
          "utilisateurs, un contrat et une mesure de satisfaction."),
        table(["Approche", "Ce que fait l'équipe", "Résultat"],
              [["Tuyauterie", "Chaque équipe assemble ses outils", "Divergence et dette"],
               ["Plateforme", "Capacités fournies et supportées", "Standard et rapidité"],
               ["Centre de services", "L'équipe plateforme agit à la place", "File d'attente"]],
              widths=[4.4, 5.2, 4.4], first_col_bold=True,
              caption="Trois approches"),
        defn("Chemin d'or", "Parcours outillé et documenté qui permet de livrer un service "
                            "conforme sans décision d'architecture préalable. Il est "
                            "suffisant pour la majorité des cas, sans être obligatoire."),
        fig("flow", "Le parcours d'un nouveau service",
            ["Modèle de dépôt créé en une commande",
             "Pipeline fourni et vert",
             "Environnements provisionnés",
             "Observabilité branchée d'office",
             "Premier déploiement en production",
             "Tableau de bord et alertes actifs"],
            height=255),
        code("""# Créer un service depuis le modèle
platform new service boutique-catalogue --owner equipe-catalogue

# Ce qui est produit
boutique-catalogue/
├── .github/workflows/ci.yml      # fourni, à jour
├── deploy/base/                  # manifestes de référence
├── deploy/env/{recette,prod}/    # surcouches
├── infra/main.tf                 # base, file, secrets
├── docs/runbook.md               # squelette à compléter
└── README.md                     # comment livrer""", "bash", "Un service en une commande"),
        box("pratique", "Le chemin d'or doit être plus rapide que le contournement",
            "Si monter son propre pipeline prend une heure et que le modèle en demande "
            "trois, personne ne l'utilisera. La plateforme gagne par la commodité, jamais "
            "par l'obligation."),

        h(2, "Le contrat"),
        p("Un chemin d'or s'accompagne d'un contrat : ce que la plateforme garantit, ce "
          "qu'elle attend en retour, et comment sortir du chemin si le besoin l'exige."),
        table(["Élément", "Contenu", "Exemple"],
              [["Garanties", "Ce qui est maintenu", "Pipeline, TLS, journaux"],
               ["Niveaux de service", "Disponibilité, délais", "Réponse sous 2 jours"],
               ["Responsabilités", "Qui fait quoi", "Équipe : code, plateforme : socle"],
               ["Échappatoire", "Sortie documentée", "Pipeline personnalisé"]],
              widths=[3.8, 4.8, 5.4], first_col_bold=True,
              caption="Quatre clauses"),
        code("""# Contrat de plateforme (extrait)

## Ce que la plateforme fournit
- Un pipeline de référence maintenu, mis à jour automatiquement
- TLS et nom de domaine
- Journaux, métriques et traces collectés
- Sauvegarde quotidienne des bases fournies
- Astreinte sur le socle, du lundi au vendredi 8h-20h

## Ce que l'équipe fournit
- Un propriétaire nommé dans le dépôt
- Des tests qui échouent quand le service est cassé
- Un runbook à jour
- Un budget de performance respecté

## Hors périmètre
- Le code applicatif
- Les choix de modèle de données
- Les incidents liés à une dépendance non fournie""", "markdown",
             "Un contrat lisible"),

        h(2, "Modèle et auto-service"),
        p("Le modèle crée un service conforme en quelques minutes. L'auto-service évite "
          "la file d'attente : l'équipe obtient une base, un espace de noms ou un "
          "certificat sans ouvrir de ticket."),
        code("""# Ressource personnalisée : une base fournie en libre-service
apiVersion: platform.exemple.fr/v1
kind: BaseDeDonnees
metadata:
  name: catalogue
  namespace: boutique
spec:
  moteur: postgresql
  version: "16"
  taille: petite          # petite | moyenne | grande
  sauvegarde: quotidienne
  retentionJours: 14""", "yaml", "Une demande déclarative"),
        code("""# Ce que l'opérateur crée derrière la demande
# - une instance managée (ou un opérateur CloudNativePG)
# - un secret de connexion dans l'espace de noms
# - une politique de sauvegarde
# - des alertes de saturation
kubectl get basededonnees -n boutique
# NAME        MOTEUR      TAILLE   PRET   AGE
# catalogue   postgresql  petite   True   3m""", "bash", "Ce qui est produit"),
        table(["Capacité", "Avant", "Après"],
              [["Base de données", "Ticket, 3 jours", "Déclaratif, 5 minutes"],
               ["Certificat TLS", "Ticket, 1 jour", "Automatique"],
               ["Espace de noms", "Ticket, 1 jour", "Modèle, immédiat"],
               ["Tableau de bord", "À construire", "Fourni"]],
              widths=[4.6, 4.4, 5.0], first_col_bold=True,
              caption="Quatre capacités"),
        box("attention", "L'auto-service sans garde-fous produit du désordre",
            "Une capacité libre-service doit imposer des limites : quotas par espace de "
            "noms, tailles autorisées, versions supportées, étiquettes obligatoires. La "
            "liberté porte sur le choix, pas sur les règles."),
        defn("Opérateur Kubernetes", "Contrôleur qui étend l'API avec des ressources "
                                     "personnalisées et réconcilie leur état, comme le "
                                     "ferait un opérateur humain."),

        h(2, "Mesurer"),
        p("Une plateforme se juge sur le délai de mise en production d'un nouveau service "
          "et sur le temps que les équipes passent hors de leur métier. Ces deux mesures "
          "suffisent à décider des investissements."),
        table(["Indicateur", "Définition", "Cible"],
              [["Délai du premier déploiement", "Création → production", "< 1 jour"],
               ["Part des services sur le chemin d'or", "Adoption", "> 80 %"],
               ["Temps de restauration d'une capacité", "Demande → disponible", "< 10 min"],
               ["Tickets d'infrastructure", "Volume par mois", "En baisse"],
               ["Satisfaction", "Enquête trimestrielle", "> 4/5"]],
              widths=[5.2, 4.4, 4.4], first_col_bold=True,
              caption="Cinq indicateurs"),
        code("""# Mesure de l'adoption : dépôts utilisant le pipeline fourni
gh api orgs/mon-org/repos --paginate \\
  | jq -r '.[].name' \\
  | while read r; do
      gh api "repos/mon-org/$r/contents/.github/workflows/ci.yml" >/dev/null 2>&1 \\
        && echo "$r utilise le pipeline fourni"
    done""", "bash", "Une mesure d'adoption"),
        fig("compare", "Deux pièges opposés",
            ("PLATEFORME TROP FERMÉE", ["Contournements nombreux", "Équipes bloquées",
                                        "Perte de confiance"],
             "PLATEFORME TROP OUVERTE", ["Dérive et dette", "Coûts incontrôlés",
                                         "Incidents variés"]),
            height=210),

        h(2, "Organiser l'équipe"),
        p("Une plateforme demande une équipe restreinte, stable et proche des utilisateurs. "
          "Le piège classique est de la transformer en centre de services, qui répond aux "
          "demandes au lieu de construire des capacités."),
        table(["Rôle", "Responsabilité", "Piège"],
              [["Responsable produit", "Prioriser les capacités", "Arbitrage absent"],
               ["Ingénieur plateforme", "Construire et maintenir", "Surcharge d'exploitation"],
               ["Ingénieur fiabilité", "SLO du socle", "Confondu avec l'astreinte applicative"],
               ["Référent par équipe", "Remonter les besoins", "Canal informel"]],
              widths=[4.6, 4.6, 4.6], first_col_bold=True,
              caption="Quatre rôles"),
        code("""# Rituel mensuel de plateforme
1. Revue des indicateurs d'adoption
2. Trois irritants utilisateurs les plus fréquents
3. Une capacité à retirer (dette)
4. Une capacité à ajouter
5. Mise à jour du contrat""", "text", "Un rituel court"),
        box("methode", "Construire une plateforme",
            items=["Partir des parcours réels, pas des outils disponibles.",
                   "Livrer un chemin d'or complet avant d'en ajouter un second.",
                   "Rendre le contournement possible et visible.",
                   "Mesurer le délai de mise en production.",
                   "Retirer régulièrement des capacités devenues inutiles."]),
    ],
    "keypoints": [
        "Une plateforme est un produit avec des utilisateurs et un contrat.",
        "Un chemin d'or couvre le cas majoritaire, sans être obligatoire.",
        "Le chemin d'or gagne par la commodité, pas par l'obligation.",
        "Le contrat précise garanties, responsabilités et échappatoire.",
        "L'auto-service exige des quotas et des règles.",
        "L'opérateur transforme une demande déclarative en ressources réelles.",
        "L'adoption et le délai de mise en production sont les bons indicateurs.",
        "Une équipe plateforme construit des capacités, elle ne répond pas aux tickets.",
    ],
    "bridge": "Les équipes livrent vite sur un socle commun. Reste à sécuriser ce qui entre "
              "dans ce socle : la chaîne logicielle.",
    "exercises": [
        ex("Définir un chemin d'or",
           "Une équipe doit livrer un service en moins d'une journée.",
           ["Listez les étapes.",
            "Précisez ce qui est fourni.",
            "Fixez le contrat."],
           [("markdown", """## Chemin d'or — service HTTP
1. `platform new service <nom> --owner <equipe>`
2. Dépôt créé avec pipeline, manifestes et runbook
3. Environnements recette et production provisionnés automatiquement
4. Premier déploiement via une demande de fusion

Fourni : pipeline, TLS, journaux, métriques, traces, sauvegarde
Attendu : tests, propriétaire, runbook, budget de performance"""),
            "Le chemin d'or doit couvrir le cas majoritaire de bout en bout, sinon les "
            "équipes complètent à la main.",
            "Ce qui est attendu de l'équipe doit être vérifié automatiquement."]),
        ex("Créer une capacité en libre-service",
           "Les équipes demandent des bases par ticket.",
           ["Définissez une ressource.",
            "Précisez les tailles.",
            "Ajoutez des quotas."],
           [("yaml", """apiVersion: platform.exemple.fr/v1
kind: BaseDeDonnees
metadata: { name: catalogue, namespace: boutique }
spec:
  moteur: postgresql
  version: "16"
  taille: petite
  sauvegarde: quotidienne
  retentionJours: 14
---
# Quota par espace de noms
apiVersion: v1
kind: ResourceQuota
metadata: { name: bases, namespace: boutique }
spec:
  hard:
    count/basededonnees.platform.exemple.fr: "2\""""),
            "Les tailles prédéfinies évitent les demandes sur mesure ingérables.",
            "Le quota empêche un espace de noms de consommer tout le cluster."],
           level="Architecture"),
        ex("Mesurer l'adoption",
           "La direction veut savoir si la plateforme est utilisée.",
           ["Choisissez un indicateur.",
            "Mesurez-le.",
            "Interprétez."],
           [("text", """Indicateur : part des services déployés avec le pipeline fourni
Mesure : 34 dépôts sur 41 utilisent `.github/workflows/ci.yml` fourni → 83 %

Interprétation : adoption correcte, mais 7 dépôts hors chemin.
Action : contacter les 7 équipes, comprendre le motif avant d'imposer."""),
            "Un taux d'adoption sans explication des écarts ne permet pas d'agir.",
            "Les services hors chemin révèlent souvent un manque de la plateforme."],
           level="Produit"),
    ],
    "quiz": [
        quiz("Qu'est-ce qu'un chemin d'or ?",
             ["Une obligation", "Un parcours outillé pour le cas majoritaire",
              "Un outil propriétaire", "Un audit"],
             1,
             "Il doit rester plus rapide que le contournement."),
        quiz("Que doit contenir un contrat de plateforme ?",
             ["Uniquement les outils", "Garanties, responsabilités, échappatoire",
              "Le code source", "Les coûts"],
             1,
             "Sans échappatoire, la plateforme devient un blocage."),
        quiz("Pourquoi des quotas en libre-service ?",
             ["Pour facturer", "Pour éviter l'épuisement du socle",
              "Pour ralentir", "Pour la conformité"],
             1,
             "Une capacité sans limite finit par saturer le cluster."),
        quiz("Quel indicateur mesure l'utilité de la plateforme ?",
             ["Nombre d'outils", "Délai de mise en production",
              "Taille de l'équipe", "Nombre de clusters"],
             1,
             "C'est le temps gagné par les équipes qui compte."),
        quiz("Quel est le piège d'une plateforme trop fermée ?",
             ["Trop de liberté", "Les contournements", "Trop de support", "Trop de coûts"],
             1,
             "Les équipes recréent leur propre tuyauterie en parallèle."),
    ],
}
