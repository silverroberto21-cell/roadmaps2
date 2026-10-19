from bookkit.dsl import (box, code, defn, ex, fig, h, ol, p, quiz, table, ul)

CH = {
    "title": "Azure et Google Cloud : équivalents et choix",
    "subtitle": "Transposer les concepts d'un fournisseur à l'autre, sans réapprendre "
                "chaque service depuis zéro.",
    "duration": "3 h 00",
    "level": "Intermédiaire",
    "prereq": "chapitre 66",
    "objectives": [
        "Construire une table d'équivalences entre fournisseurs.",
        "Comprendre les modèles d'identité d'Azure et de Google Cloud.",
        "Choisir un service de calcul équivalent.",
        "Comparer les modèles réseau.",
        "Évaluer un fournisseur sur des critères objectifs.",
    ],
    "blocks": [
        h(2, "Les concepts se ressemblent"),
        p("Les trois grands fournisseurs proposent les mêmes briques : identité, réseau "
          "virtuel, calcul, stockage, base managée, supervision. Seuls les noms et les "
          "détails d'intégration changent."),
        table(["Besoin", "AWS", "Azure", "Google Cloud"],
              [["Identité et permissions", "IAM", "Entra ID + RBAC", "Cloud IAM"],
               ["Réseau virtuel", "VPC", "Virtual Network", "VPC"],
               ["Machine virtuelle", "EC2", "Virtual Machines", "Compute Engine"],
               ["Conteneurs managés", "ECS / EKS", "Container Apps / AKS", "Cloud Run / GKE"],
               ["Fonction", "Lambda", "Functions", "Cloud Functions"],
               ["Stockage objet", "S3", "Blob Storage", "Cloud Storage"],
               ["Base relationnelle", "RDS", "Azure SQL / Flexible", "Cloud SQL"],
               ["Supervision", "CloudWatch", "Azure Monitor", "Cloud Monitoring"]],
              widths=[4.4, 2.8, 3.6, 3.2], first_col_bold=True,
              caption="Huit équivalences"),
        fig("columns", "Trois façons de nommer la même brique",
            [("AWS", ["IAM", "S3", "Lambda", "VPC"]),
             ("AZURE", ["Entra ID", "Blob", "Functions", "VNet"]),
             ("GCP", ["Cloud IAM", "Cloud Storage", "Cloud Functions", "VPC"])],
            height=200),
        defn("Équivalence fonctionnelle", "Deux services qui rendent le même service "
                                          "conceptuel avec des garanties différentes. "
                                          "Une migration ne consiste jamais à remplacer "
                                          "un nom par un autre."),

        h(2, "Identité"),
        p("L'identité est le premier service à comprendre, car tout le reste en dépend. "
          "Azure s'appuie sur un annuaire d'entreprise, Google Cloud sur des comptes et "
          "des rôles projet."),
        table(["Aspect", "AWS", "Azure", "Google Cloud"],
              [["Annuaire", "IAM", "Entra ID", "Cloud Identity"],
               ["Unité de permission", "Politique JSON", "Rôle RBAC", "Rôle IAM"],
               ["Portée", "Compte, ressource", "Abonnement, groupe, ressource",
                "Organisation, projet, ressource"],
               ["Identité de charge", "Rôle IAM", "Identité managée", "Compte de service"],
               ["Fédération", "OIDC / SAML", "Entra ID", "Workload Identity"]],
              widths=[3.6, 3.6, 4.0, 4.0], first_col_bold=True,
              caption="Cinq aspects de l'identité"),
        code("""# Azure : se connecter et lister les rôles d'un périmètre
az login
az account list --output table
az role assignment list --assignee alice@exemple.fr --all --output table

# Google Cloud : identité active et rôles projet
gcloud auth login
gcloud config list
gcloud projects get-iam-policy mon-projet \\
  --flatten="bindings[].members" \\
  --format="table(bindings.role, bindings.members)\"""", "bash",
             "Deux séries de commandes"),
        box("pratique", "Les identités managées remplacent les secrets",
            "Azure Managed Identity et Google Workload Identity fournissent des "
            "identifiants temporaires à une charge de travail. Le code n'a plus de mot "
            "de passe de base de données ni de clé de stockage."),

        h(2, "Calcul"),
        p("Le choix se fait sur trois critères : le modèle d'exécution, le besoin de "
          "contrôle et la familiarité de l'équipe."),
        table(["Besoin", "AWS", "Azure", "Google Cloud"],
              [["Machine virtuelle", "EC2", "VM", "Compute Engine"],
               ["Conteneur sans serveur", "Fargate", "Container Apps", "Cloud Run"],
               ["Kubernetes", "EKS", "AKS", "GKE"],
               ["Fonction événementielle", "Lambda", "Functions", "Cloud Functions"],
               ["Lot managé", "Batch", "Batch", "Batch"]],
              widths=[4.0, 3.4, 3.6, 3.4], first_col_bold=True,
              caption="Cinq besoins de calcul"),
        code("""# Azure Container Apps : déploiement depuis une image
az containerapp create \\
  --name api --resource-group demo --environment demo-env \\
  --image registry.exemple.fr/equipe/app:1.4.2 \\
  --target-port 3000 --ingress external \\
  --min-replicas 1 --max-replicas 5

# Cloud Run : équivalent chez Google
gcloud run deploy api \\
  --image europe-docker.pkg.dev/mon-projet/app/app:1.4.2 \\
  --region europe-west1 --allow-unauthenticated \\
  --min-instances 1 --max-instances 5 --port 3000""", "bash",
             "Deux déploiements comparables"),
        p("Les plateformes de conteneurs sans serveur facturent à la requête ou à la "
          "seconde d'instance active. Le paramètre `min-instances` évite les démarrages "
          "à froid, au prix d'une facturation permanente."),
        defn("Démarrage à froid", "Temps de démarrage d'une instance inactive. Il dépend "
                                  "de la taille de l'image, du runtime et des "
                                  "initialisations. Réduire l'image et préchauffer sont "
                                  "les deux leviers."),

        h(2, "Réseau"),
        p("Les modèles réseau diffèrent surtout par la gestion des adresses et des "
          "pare-feux. Le principe reste : séparer public et privé, n'ouvrir que le "
          "nécessaire."),
        table(["Aspect", "AWS", "Azure", "Google Cloud"],
              [["Réseau virtuel", "VPC", "VNet", "VPC"],
               ["Pare-feu", "Groupe de sécurité", "Groupe de sécurité réseau (NSG)",
                "Règles de pare-feu VPC"],
               ["Sortie privée", "NAT Gateway", "NAT Gateway", "Cloud NAT"],
               ["Lien privé vers un service", "PrivateLink", "Private Link",
                "Private Service Connect"],
               ["DNS interne", "Route 53 Resolver", "DNS privé Azure", "Cloud DNS privé"]],
              widths=[4.2, 3.6, 4.0, 3.6], first_col_bold=True,
              caption="Cinq aspects réseau"),
        code("""# Azure : créer un réseau et un sous-réseau
az network vnet create --resource-group demo --name vnet-demo \\
  --address-prefix 10.0.0.0/16 --subnet-name app --subnet-prefix 10.0.1.0/24

# Google Cloud : réseau et règle de pare-feu
gcloud compute networks create vpc-demo --subnet-mode=custom
gcloud compute networks subnets create app --network=vpc-demo \\
  --region=europe-west1 --range=10.0.1.0/24
gcloud compute firewall-rules create allow-https \\
  --network=vpc-demo --allow=tcp:443 --source-ranges=0.0.0.0/0""", "bash",
             "Deux configurations"),

        h(2, "Choisir"),
        p("Le choix d'un fournisseur se joue rarement sur la technique pure. Cinq "
          "critères objectifs pèsent davantage."),
        table(["Critère", "Question", "Poids"],
              [["Compétences existantes", "Que sait déjà l'équipe ?", "Fort"],
               ["Écosystème et services managés", "Le service dont j'ai besoin existe-t-il ?", "Fort"],
               ["Présence et latence", "Une région proche des utilisateurs ?", "Moyen"],
               ["Coût total", "Calcul, sortie réseau, support", "Fort"],
               ["Conformité", "Le fournisseur répond-il au cadre légal ?", "Décisif"]],
              widths=[4.6, 5.4, 3.0], first_col_bold=True,
              caption="Cinq critères de choix"),
        code("""# Comparer à l'identique : même région, même taille, même usage
# Coût mensuel estimé d'une petite application :
# - 2 instances de 2 vCPU / 4 Go
# - 100 Go de stockage objet
# - 200 Go de sortie réseau
# - une base managée de 2 vCPU / 8 Go

# Utiliser les calculateurs officiels avec la MÊME hypothèse de charge""",
             "bash", "Une méthode de comparaison"),
        box("attention", "Le coût de sortie fausse les comparaisons",
            "Une sortie réseau importante peut dépasser le coût de calcul. Un chiffrage "
            "qui ignore ce poste est faux, parfois d'un facteur deux."),
        box("methode", "Migrer d'un fournisseur à l'autre",
            items=["Inventorier les services réellement utilisés.",
                   "Classer : remplaçable, adaptable, spécifique.",
                   "Migrer d'abord les charges sans état.",
                   "Conserver une période de double fonctionnement.",
                   "Mesurer la latence et le coût après migration."]),
    ],
    "keypoints": [
        "Les trois fournisseurs proposent les mêmes briques conceptuelles.",
        "Une équivalence de nom ne garantit pas une équivalence de comportement.",
        "Azure s'appuie sur un annuaire d'entreprise, Google sur des projets.",
        "Les identités managées suppriment les secrets stockés.",
        "Les plateformes de conteneurs sans serveur facturent à l'usage.",
        "`min-instances` évite les démarrages à froid, à un coût fixe.",
        "Les modèles réseau diffèrent par les noms, pas par les principes.",
        "Le coût de sortie réseau doit entrer dans toute comparaison.",
    ],
    "bridge": "Les plateformes managées exécutent le code. Le chapitre suivant se "
              "concentre sur le modèle sans serveur.",
    "exercises": [
        ex("Construire une table d'équivalences",
           "Une architecture AWS doit être transposée sur Azure et Google Cloud.",
           ["Listez les briques utilisées.",
            "Associez un équivalent.",
            "Notez les différences de comportement."],
           [("markdown", """| AWS | Azure | Google Cloud | différence |
|-----|-------|--------------|------------|
| ECS Fargate | Container Apps | Cloud Run | facturation à la requête chez GCP |
| RDS | Azure SQL / Flexible Server | Cloud SQL | options de réplication |
| S3 | Blob Storage | Cloud Storage | classes et cycles de vie |
| CloudWatch | Azure Monitor | Cloud Monitoring | modèle d'alerte |"""),
            "La colonne « différence » est la plus importante : elle évite de supposer "
            "une équivalence parfaite.",
            "Les options de réplication et de bascule varient fortement d'un fournisseur "
            "à l'autre."]),
        ex("Déployer une même image sur deux plateformes",
           "Une image conteneur doit être servie par Azure Container Apps et Cloud Run.",
           ["Déployez sur la première.",
            "Déployez sur la seconde.",
            "Comparez le temps de démarrage."],
           [("bash", """# Azure
az containerapp create --name api --resource-group demo --environment demo-env \\
  --image registry.exemple.fr/equipe/app:1.4.2 --target-port 3000 \\
  --ingress external --min-replicas 0 --max-replicas 3

# Google Cloud
gcloud run deploy api --image registry.exemple.fr/equipe/app:1.4.2 \\
  --region europe-west1 --allow-unauthenticated --min-instances 0 --max-instances 3

# Mesurer après une période d'inactivité
curl -w "%{time_total}\\n" -o /dev/null -s https://api-xxxx.run.app/health"""),
            "Avec `min-replicas 0`, la première requête après inactivité subit un "
            "démarrage à froid ; la mesure le quantifie.",
            "Le temps de démarrage dépend surtout de la taille de l'image et des "
            "initialisations applicatives."],
           level="Cloud"),
        ex("Comparer deux options de coût",
           "Une API reçoit 200 000 requêtes par jour, avec des pics.",
           ["Estimez le coût en conteneur sans serveur.",
            "Estimez le coût en instance permanente.",
            "Tranchez selon le profil de charge."],
           ["Conteneur sans serveur : facturation à l'usage, avantageuse si les pics "
            "sont courts et les nuits calmes.",
            "Instance permanente : coût fixe, prévisible, préférable si la charge reste "
            "élevée en continu.",
            "Le point d'équilibre se calcule sur une semaine réelle, pas sur une moyenne "
            "mensuelle."],
           level="FinOps"),
    ],
    "quiz": [
        quiz("Quel service Azure fournit l'identité ?",
             ["IAM", "Entra ID", "Monitor", "VNet"],
             1,
             "Entra ID est l'annuaire et le service d'identité d'Azure."),
        quiz("Quel est l'équivalent de S3 chez Google Cloud ?",
             ["Cloud SQL", "Cloud Storage", "BigQuery", "Cloud Run"],
             1,
             "Cloud Storage est le service de stockage objet."),
        quiz("À quoi sert `min-instances` ?",
             ["Limiter le coût", "Éviter les démarrages à froid",
              "Réduire l'image", "Bloquer les accès"],
             1,
             "Une instance reste chaude, au prix d'une facturation permanente."),
        quiz("Pourquoi une équivalence de nom ne suffit-elle pas ?",
             ["Les noms changent", "Les garanties et comportements diffèrent",
              "Les régions sont différentes", "Les API sont identiques"],
             1,
             "Les détails de facturation, de réplication et de limites varient."),
    ],
}
