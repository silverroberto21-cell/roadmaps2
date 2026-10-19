from bookkit.dsl import (box, code, defn, ex, fig, h, ol, p, quiz, table, ul)

CH = {
    "title": "FinOps : maîtriser le coût du cloud",
    "subtitle": "Rendre la dépense visible, attribuable et proportionnée à la valeur "
                "produite.",
    "duration": "3 h 00",
    "level": "Intermédiaire",
    "prereq": "chapitre 71",
    "objectives": [
        "Lire une facture cloud sans se tromper de coupable.",
        "Étiqueter les ressources pour attribuer les coûts.",
        "Distinguer économie réelle et report de coût.",
        "Dimensionner et réserver sans se bloquer.",
        "Installer un rituel de pilotage.",
    ],
    "blocks": [
        h(2, "Le coût suit l'architecture"),
        p("La facture cloud n'est pas un problème comptable : c'est le reflet des choix "
          "techniques. Une architecture qui transfère des téraoctets entre zones ou qui "
          "garde des instantanés pour toujours coûte cher, quelle que soit la remise "
          "négociée."),
        table(["Poste", "Origine", "Levier"],
              [["Calcul", "Instances et pods", "Dimensionnement, arrêt, réservation"],
               ["Stockage", "Volumes et objets", "Cycle de vie, compression"],
               ["Réseau sortant", "Transferts", "Cache, colocalisation"],
               ["Bases managées", "Instances et stockage", "Type, sauvegardes"],
               ["Observabilité", "Volume de journaux", "Rétention, échantillonnage"]],
              widths=[4.4, 4.4, 5.2], first_col_bold=True,
              caption="Cinq postes"),
        defn("Coût unitaire", "Dépense rapportée à une unité de valeur : par commande, par "
                              "utilisateur actif, par requête. C'est le seul indicateur qui "
                              "relie la dépense à l'activité."),
        fig("flow", "De la facture à la décision",
            ["Facture par service",
             "Attribution par étiquette et compte",
             "Comparaison au budget",
             "Détection des anomalies",
             "Décision technique ou produit",
             "Vérification de l'effet"],
            height=250),

        h(2, "Rendre la dépense visible"),
        p("Sans étiquetage, la facture reste un total opaque. Trois étiquettes suffisent à "
          "couvrir l'essentiel : l'application, l'environnement et le propriétaire."),
        code("""# Étiquettes obligatoires, appliquées par politique
# (Terraform)
locals {
  etiquettes = {
    application   = "boutique"
    environnement = var.environnement
    proprietaire  = "equipe-boutique"
    cout_centre   = "cc-421"
  }
}

resource "aws_instance" "app" {
  # ...
  tags = merge(local.etiquettes, { role = "applicatif" })
}

# Détecter les ressources non étiquetées
aws resourcegroupstaggingapi get-resources \\
  --tag-filters Key=environnement \\
  --query 'ResourceTagMappingList[].ResourceARN'""", "hcl", "Un étiquetage systématique"),
        table(["Étiquette", "Valeurs", "Usage"],
              [["`application`", "Nom du produit", "Vue par produit"],
               ["`environnement`", "dev, recette, production", "Séparer l'essentiel du reste"],
               ["`proprietaire`", "Équipe", "Responsabilisation"],
               ["`cout_centre`", "Code comptable", "Refacturation"]],
              widths=[4.2, 4.6, 5.2], first_col_bold=True,
              caption="Quatre étiquettes"),
        code("""# Anomalie de coût : détection par seuil relatif
aws ce get-cost-and-usage \\
  --time-period Start=2026-10-01,End=2026-10-19 \\
  --granularity DAILY --metrics UnblendedCost \\
  --group-by Type=DIMENSION,Key=SERVICE

# Budget avec alerte à 80 % et 100 %
aws budgets create-budget --account-id 123456789012 \\
  --budget file://budget.json --notifications-with-subscribers file://alertes.json""",
             "bash", "Deux contrôles"),
        box("pratique", "Une anomalie se juge en relatif",
            "Une facture qui double en un jour est suspecte ; une facture qui augmente de "
            "5 % avec 20 % de trafic en plus est saine. Comparez toujours la dépense à "
            "l'usage."),

        h(2, "Économiser sans casser"),
        p("Les économies faciles se trouvent dans les ressources oubliées, puis dans le "
          "dimensionnement. Les engagements viennent en dernier, quand l'usage est stable "
          "et connu."),
        table(["Levier", "Gain typique", "Risque"],
              [["Suppression des ressources orphelines", "5 à 15 %", "Faible"],
               ["Arrêt hors production", "10 à 30 %", "Moyen"],
               ["Dimensionnement ajusté", "10 à 25 %", "Performance"],
               ["Réservation / engagement", "20 à 40 %", "Blocage sur 1 à 3 ans"],
               ["Cycle de vie du stockage", "5 à 20 %", "Faible"],
               ["Réduction des journaux", "5 à 15 %", "Perte de diagnostic"]],
              widths=[5.0, 3.8, 5.2], first_col_bold=True,
              caption="Six leviers"),
        code("""# Chercher les volumes non attachés
aws ec2 describe-volumes --filters Name=status,Values=available \\
  --query 'Volumes[].{id:VolumeId,taille:Size,cree:CreationTime}'

# Chercher les adresses IP réservées non utilisées
aws ec2 describe-addresses --query 'Addresses[?AssociationId==null]'

# Chercher les instantanés de plus de 90 jours
aws ec2 describe-snapshots --owner-ids self \\
  --query 'Snapshots[?StartTime<=`2026-07-01`].[SnapshotId,StartTime,VolumeSize]'""",
             "bash", "Trois recherches"),
        box("attention", "Attention aux économies qui déplacent le coût",
            "Éteindre une base la nuit réduit la facture de calcul mais peut allonger le "
            "démarrage et provoquer des incidents. Une économie qui dégrade la fiabilité "
            "n'est pas une économie : c'est un transfert vers l'astreinte."),
        defn("Engagement", "Achat à l'avance d'une capacité pour une durée donnée, en "
                           "échange d'une remise. Il réduit le coût à condition que l'usage "
                           "reste supérieur à l'engagement."),

        h(2, "Dimensionner"),
        p("Le surdimensionnement est la norme par prudence. Le sous-dimensionnement coûte "
          "en incident. La bonne méthode consiste à mesurer, puis à viser une marge "
          "explicite plutôt qu'un facteur arbitraire."),
        code("""# Utilisation réelle sur 30 jours
kubectl top pods -n production --sort-by=cpu
kubectl top nodes

# Comparer la demande et la consommation
kubectl describe node | grep -A6 "Allocated resources"

# Exemple de constat : requests cpu = 2, usage p95 = 0,35
# → requests excessifs : le cluster réserve 6 fois le besoin""", "bash",
             "Un constat chiffré"),
        table(["Situation", "Constat", "Décision"],
              [["Usage p95 << requests", "Réservation excessive", "Ajuster les requests"],
               ["Usage proche des limites", "Risque d'éviction", "Augmenter ou optimiser"],
               ["Pics prévisibles", "Dimensionner pour la pointe", "Autoscaling"],
               ["Charge stable 24/7", "Bon candidat à l'engagement", "Réserver"]],
              widths=[4.6, 4.8, 4.6], first_col_bold=True,
              caption="Quatre constats"),
        code("""# Politique d'autoscaling fondée sur une métrique utile
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: api
  namespace: production
spec:
  scaleTargetRef: { apiVersion: apps/v1, kind: Deployment, name: api }
  minReplicas: 3
  maxReplicas: 20
  metrics:
    - type: Resource
      resource: { name: cpu, target: { type: Utilization, averageUtilization: 65 } }
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300""", "yaml", "Un autoscaling borné"),
        box("attention", "L'autoscaling ne remplace pas le dimensionnement",
            "Un service qui met trois minutes à démarrer ou qui dépend d'une base saturée "
            "ne gagne rien à multiplier les réplicas. L'autoscaling absorbe les variations, "
            "il ne corrige pas un goulot."),

        h(2, "Le rituel"),
        p("FinOps est une pratique régulière, pas un projet ponctuel. Un rituel mensuel "
          "suffit : regarder, attribuer, décider, vérifier."),
        table(["Rythme", "Question", "Participants"],
              [["Hebdomadaire", "Une anomalie est-elle apparue ?", "Astreinte"],
               ["Mensuel", "Quel est le coût unitaire ?", "Équipe et produit"],
               ["Trimestriel", "Les engagements sont-ils adaptés ?", "Finance et technique"],
               ["Annuel", "L'architecture reste-t-elle justifiée ?", "Direction"]],
              widths=[4.0, 5.6, 4.4], first_col_bold=True,
              caption="Quatre rythmes"),
        code("""# Tableau de bord minimal
# 1. Dépense du mois et projection
# 2. Coût par commande et par utilisateur actif
# 3. Top 5 des services par dépense
# 4. Ressources non étiquetées (objectif : zéro)
# 5. Économies réalisées et vérifiées""", "text", "Cinq chiffres"),
        box("methode", "Piloter les coûts",
            items=["Étiqueter avant d'optimiser.",
                   "Attribuer chaque dépense à une équipe.",
                   "Comparer la dépense à l'usage, pas au mois précédent seul.",
                   "Traiter d'abord les ressources orphelines.",
                   "S'engager seulement sur un usage stable et mesuré."]),
    ],
    "keypoints": [
        "La facture reflète les choix d'architecture.",
        "Sans étiquettes, aucune attribution n'est possible.",
        "Le coût unitaire relie la dépense à la valeur.",
        "Une anomalie se juge en relatif à l'usage.",
        "Les ressources orphelines sont le premier gisement.",
        "Les engagements ne valent que sur un usage stable.",
        "Une économie qui dégrade la fiabilité est un transfert de coût.",
        "Un rituel mensuel vaut mieux qu'un audit annuel.",
    ],
    "bridge": "Les coûts sont pilotés. Le chapitre suivant outille les équipes pour "
              "livrer sans dépendre d'un expert.",
    "exercises": [
        ex("Étiqueter et attribuer",
           "La facture ne distingue pas la recette de la production.",
           ["Choisissez trois étiquettes.",
            "Appliquez-les dans le code.",
            "Vérifiez l'absence de ressource non étiquetée."],
           [("hcl", """locals {
  etiquettes = {
    application   = "boutique"
    environnement = var.environnement
    proprietaire  = "equipe-boutique"
  }
}

# Politique : toute ressource sans ces trois étiquettes est refusée
# par un contrôle de conformité dans le pipeline."""),
            "Une étiquette appliquée manuellement finit toujours par manquer.",
            "Le contrôle doit être automatisé pour être fiable dans le temps."]),
        ex("Trouver des ressources orphelines",
           "Le compte contient des volumes et des adresses inutilisés.",
           ["Listez les volumes détachés.",
            "Listez les adresses libres.",
            "Chiffrez l'économie."],
           [("bash", """aws ec2 describe-volumes --filters Name=status,Values=available \\
  --query 'Volumes[].[VolumeId,Size,CreateTime]' --output table

aws ec2 describe-addresses --query 'Addresses[?AssociationId==null].[PublicIp]'

# Économie mensuelle = somme(taille_Go × prix_Go_mois) + IP non associées"""),
            "Un volume détaché reste facturé : il ne coûte rien à supprimer.",
            "Vérifiez la date de création avant de supprimer : un volume récent peut "
            "être en cours de migration."],
           level="Exploitation"),
        ex("Arbitrer un engagement",
           "Une remise de 30 % sur trois ans est proposée.",
           ["Vérifiez la stabilité de l'usage.",
            "Calculez le point mort.",
            "Décidez."],
           [("text", """Usage : 8 instances en moyenne, stable depuis 9 mois
Variation mensuelle : ±1 instance
Engagement proposé : 10 instances sur 3 ans, −30 %

Risque : si le projet migre vers une autre architecture, l'engagement
reste dû. Décision : engager 6 instances (75 % du plancher observé),
garder le reste à la demande."""),
            "N'engagez jamais la pointe : engagez le plancher observé.",
            "Un engagement est une dette : il doit rester inférieur à l'usage minimal "
            "crédible."],
           level="Finance"),
    ],
    "quiz": [
        quiz("Que permet l'étiquetage ?",
             ["Chiffrer les données", "Attribuer les coûts", "Accélérer le réseau",
              "Réduire la latence"],
             1,
             "Sans étiquette, la facture reste un total opaque."),
        quiz("Quel est le premier gisement d'économie ?",
             ["Les engagements", "Les ressources orphelines", "Les remises",
              "Le change"],
             1,
             "Elles coûtent sans produire de valeur."),
        quiz("Quand un engagement est-il raisonnable ?",
             ["Sur la pointe", "Sur le plancher d'usage stable", "Au hasard",
              "Toujours"],
             1,
             "Il faut rester en dessous de l'usage minimal crédible."),
        quiz("Pourquoi comparer la dépense à l'usage ?",
             ["Pour la comptabilité", "Pour distinguer croissance et dérive",
              "Pour payer moins", "Pour la conformité"],
             1,
             "Une hausse avec la charge est saine ; une hausse à charge constante est "
             "une dérive."),
        quiz("Que mesure le coût unitaire ?",
             ["Le prix d'une instance", "La dépense par unité de valeur",
              "La marge", "Le budget"],
             1,
             "Il relie la dépense à l'activité réelle."),
    ],
}
