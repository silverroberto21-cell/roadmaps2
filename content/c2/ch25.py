from bookkit.dsl import (box, code, defn, ex, fig, h, ol, p, quiz, table, ul)

CH = {
    "title": "Modèles de cloud et architecture de référence",
    "subtitle": "Ce que le cloud change réellement : responsabilités partagées, coûts "
                "variables et défaillances partielles.",
    "duration": "3 h 00",
    "level": "Intermédiaire",
    "prereq": "chapitre 64",
    "objectives": [
        "Distinguer IaaS, PaaS, CaaS et SaaS.",
        "Situer la responsabilité dans le modèle partagé.",
        "Concevoir pour la panne partielle.",
        "Comprendre les modèles de coût.",
        "Choisir entre plusieurs fournisseurs ou un seul.",
    ],
    "blocks": [
        h(2, "Quatre modèles de service"),
        p("Le cloud n'est pas un lieu, c'est un mode de consommation. Chaque modèle "
          "transfère une partie de la responsabilité opérationnelle au fournisseur."),
        table(["Modèle", "Vous gérez", "Le fournisseur gère", "Exemple"],
              [["IaaS", "OS, runtime, application", "Matériel, réseau, virtualisation", "VM"],
               ["CaaS", "Images, configuration", "Orchestration, nœuds", "Kubernetes managé"],
               ["PaaS", "Code, données", "Runtime, montée en charge", "Plateforme applicative"],
               ["Serverless", "Fonction, événement", "Tout le reste, à la demande", "Fonction managée"],
               ["SaaS", "Usage et données", "Tout", "Messagerie, CRM"]],
              widths=[3.2, 3.6, 4.6, 3.6], first_col_bold=True,
              caption="Cinq modèles de service"),
        fig("columns", "Le modèle de responsabilité partagée",
            [("FOURNISSEUR", ["Matériel", "Réseau physique", "Virtualisation", "Datacenters"]),
             ("CLIENT", ["Données", "Identités", "Configuration", "Code applicatif"])],
            height=200),
        defn("Responsabilité partagée", "Répartition explicite : le fournisseur sécurise "
                                        "l'infrastructure, le client sécurise ce qu'il "
                                        "y place. Une erreur de configuration reste "
                                        "toujours de la responsabilité du client."),
        box("attention", "« Managé » ne signifie pas « sécurisé »",
            "Une base de données managée mal configurée — accessible publiquement sans "
            "authentification — reste une fuite de données. Les incidents les plus "
            "médiatisés viennent presque toujours de configurations client, pas de "
            "défaillances du fournisseur."),

        h(2, "Concevoir pour la panne"),
        p("Dans le cloud, tout échoue partiellement et en permanence : une instance, une "
          "zone, un service managé. L'architecture doit continuer à fonctionner en mode "
          "dégradé."),
        table(["Niveau", "Portée", "Défaillance typique"],
              [["Région", "Zone géographique", "Rare, panne majeure"],
               ["Zone de disponibilité", "Datacenter isolé", "Plusieurs par an"],
               ["Instance", "Machine virtuelle", "Fréquente"],
               ["Service managé", "API, base", "Latence, quotas"]],
              widths=[4.2, 4.6, 4.6], first_col_bold=True,
              caption="Quatre niveaux de défaillance"),
        fig("flow", "Une architecture multi-zone",
            ["Répartiteur de charge régional",
             "Zone A : instance applicative",
             "Zone B : instance applicative",
             "Base primaire en A, réplique en B",
             "Stockage objet répliqué",
             "Supervision indépendante"],
            height=255),
        code("""# Vérifier la répartition sur plusieurs zones
aws ec2 describe-instances \\
  --filters "Name=tag:Role,Values=app" \\
  --query "Reservations[].Instances[].Placement.AvailabilityZone" \\
  --output text | tr '\\t' '\\n' | sort | uniq -c

# Une seule zone = point unique de défaillance""", "bash",
             "Une vérification de répartition"),
        p("Une architecture multi-zone coûte plus cher en matériel et en réplication. Ce "
          "coût se justifie par un objectif de disponibilité chiffré, pas par principe."),
        defn("Objectif de niveau de service", "Engagement chiffré, par exemple 99,9 % de "
                                              "disponibilité sur un mois, soit environ 43 "
                                              "minutes d'indisponibilité. Il oriente les "
                                              "choix d'architecture et leur coût."),

        h(2, "Modèles de coût"),
        p("Le cloud transforme un investissement en dépense variable. Cette souplesse a "
          "un revers : sans suivi, la facture croît sans qu'aucune décision ne soit "
          "prise."),
        table(["Poste", "Facturation", "Piège"],
              [["Calcul", "À la seconde ou à l'heure", "Instances oubliées"],
               ["Stockage", "Au Go-mois", "Instantanés anciens"],
               ["Sortie réseau", "Au Go sortant", "Souvent sous-estimé"],
               ["Requêtes", "Au million", "Boucles mal placées"],
               ["Adresses publiques", "À l'heure", "IP réservées inutilisées"]],
              widths=[3.8, 4.4, 5.2], first_col_bold=True,
              caption="Cinq postes de coût"),
        code("""# Identifier les ressources non utilisées
aws ec2 describe-volumes --filters Name=status,Values=available \\
  --query "Volumes[].{id:VolumeId,taille:Size}" --output table

aws ec2 describe-addresses --query "Addresses[?AssociationId==null]" --output table

# Suivre la dépense par service
aws ce get-cost-and-usage \\
  --time-period Start=2026-09-01,End=2026-10-01 \\
  --granularity MONTHLY --metrics BlendedCost \\
  --group-by Type=DIMENSION,Key=SERVICE""", "bash", "Trois commandes"),
        table(["Levier", "Effet", "Effort"],
              [["Étiquetage systématique", "Attribution des coûts", "Faible, initial"],
               ["Arrêt des environnements hors heures", "30 à 60 %", "Automatisation"],
               ["Ajustement des tailles", "20 à 40 %", "Mesure préalable"],
               ["Achats d'engagement", "20 à 50 %", "Analyse de stabilité"],
               ["Sortie réseau réduite", "Variable", "Architecture"]],
              widths=[5.0, 3.8, 4.0], first_col_bold=True,
              caption="Cinq leviers d'optimisation"),
        box("pratique", "Étiqueter à la création",
            "Une étiquette ajoutée plus tard ne répartit pas les coûts passés. Appliquez "
            "`projet`, `environnement` et `responsable` dès la première ressource, et "
            "interdisez la création sans étiquettes par politique."),

        h(2, "Un fournisseur ou plusieurs"),
        p("Le multi-cloud est souvent invoqué pour éviter la dépendance. Il multiplie "
          "aussi la complexité opérationnelle : deux réseaux, deux identités, deux "
          "supervisions."),
        table(["Situation", "Choix raisonnable", "Raison"],
              [["Startup, équipe réduite", "Un fournisseur", "Simplicité"],
               ["Exigence réglementaire de réversibilité", "Deux fournisseurs, portabilité",
                "Contrat"],
               ["Rachat ou héritage", "Consolidation progressive", "Coût de migration"],
               ["Service spécialisé", "Multi-cloud ciblé", "Meilleur outil par usage"]],
              widths=[5.0, 4.6, 4.0], first_col_bold=True,
              caption="Quatre situations"),
        code("""# Réduire la dépendance sans multi-cloud
- Conteneurs plutôt que services propriétaires
- Terraform plutôt que console
- Stockage compatible S3
- Kubernetes plutôt qu'orchestrateur propriétaire
- Sauvegardes exportables""", "text", "Cinq choix de portabilité"),
        p("La portabilité se prépare au niveau des interfaces : un conteneur, une "
          "infrastructure décrite, un stockage standard. Elle ne consiste pas à faire "
          "tourner la même architecture partout."),
        box("methode", "Avant d'ouvrir un compte cloud",
            items=["Un budget et une alerte de dépassement.",
                   "Une convention d'étiquetage.",
                   "Une politique d'accès par rôle, jamais root.",
                   "Une région choisie pour la latence et le droit applicable.",
                   "Une procédure de suppression des ressources de test."]),
    ],
    "keypoints": [
        "IaaS, CaaS, PaaS et serverless délèguent des responsabilités différentes.",
        "Le client reste responsable de sa configuration et de ses données.",
        "Tout échoue partiellement : l'architecture doit tolérer la panne.",
        "Une architecture multi-zone répond à un objectif chiffré.",
        "La sortie réseau est un poste souvent sous-estimé.",
        "Les étiquettes déterminent la capacité à analyser les coûts.",
        "Le multi-cloud ajoute de la complexité autant que de la liberté.",
        "La portabilité se prépare par les interfaces, pas par la duplication.",
    ],
    "bridge": "Le modèle est compris. Le chapitre suivant parcourt les services "
              "essentiels d'un fournisseur : AWS.",
    "exercises": [
        ex("Répartir les responsabilités",
           "Trois services doivent être classés selon le modèle partagé.",
           ["Une VM avec PostgreSQL",
            "Une base managée",
            "Une fonction serverless"],
           ["VM : le client gère l'OS, les correctifs, la sauvegarde, la haute "
            "disponibilité.",
            "Base managée : le fournisseur gère l'OS et les correctifs, le client gère "
            "les accès, le schéma et les sauvegardes logiques.",
            "Serverless : le fournisseur gère le runtime et la montée en charge, le "
            "client gère le code, les permissions et les quotas."],
           level="Architecture"),
        ex("Chiffrer un objectif de disponibilité",
           "Une équipe promet « une haute disponibilité ».",
           ["Transformez la promesse en chiffre.",
            "Calculez l'indisponibilité mensuelle.",
            "Déduisez l'architecture nécessaire."],
           ["« Haute disponibilité » n'est pas mesurable : choisissez 99,9 % ou 99,95 %.",
            "99,9 % sur 30 jours = environ 43 minutes ; 99,95 % = environ 21 minutes.",
            "43 minutes tolèrent une reprise manuelle ; 21 minutes exigent une reprise "
            "automatique multi-zone."],
           level="Architecture"),
        ex("Réduire une facture",
           "La facture mensuelle a doublé en trois mois.",
           ["Identifiez les trois premiers postes.",
            "Cherchez les ressources inertes.",
            "Proposez trois actions."],
           [("bash", """aws ce get-cost-and-usage --time-period Start=2026-09-01,End=2026-10-01 \\
  --granularity MONTHLY --metrics BlendedCost \\
  --group-by Type=DIMENSION,Key=SERVICE --output table

aws ec2 describe-instances --filters Name=instance-state-name,Values=stopped \\
  --query "Reservations[].Instances[].InstanceId" --output text

aws ec2 describe-volumes --filters Name=status,Values=available \\
  --query "Volumes[].VolumeId" --output text"""),
            "Un doublement vient souvent d'un environnement de test laissé actif ou "
            "d'instantanés jamais purgés.",
            "La suppression des volumes non attachés et des adresses non associées est "
            "immédiate et sans risque."],
           level="FinOps"),
    ],
    "quiz": [
        quiz("Qui est responsable de la configuration d'une base managée ?",
             ["Le fournisseur", "Le client", "Personne", "L'auditeur"],
             1,
             "Le fournisseur gère l'infrastructure ; la configuration reste au client."),
        quiz("Que signifie 99,9 % de disponibilité sur 30 jours ?",
             ["9 minutes d'arrêt", "Environ 43 minutes", "Environ 7 heures", "Aucun arrêt"],
             1,
             "0,1 % de 43 200 minutes représente environ 43 minutes."),
        quiz("Quel poste de coût est souvent sous-estimé ?",
             ["Le calcul", "Le stockage", "La sortie réseau", "Les adresses IP"],
             2,
             "Les transferts sortants sont facturés et augmentent avec l'usage."),
        quiz("Comment préparer la portabilité ?",
             ["Dupliquer l'architecture partout", "Standardiser les interfaces",
              "Choisir le moins cher", "Éviter les conteneurs"],
             1,
             "Conteneurs, IaC et stockage standard réduisent la dépendance."),
    ],
}
