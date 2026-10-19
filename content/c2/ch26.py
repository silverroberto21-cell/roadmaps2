from bookkit.dsl import (box, code, defn, ex, fig, h, ol, p, quiz, table, ul)

CH = {
    "title": "AWS : services essentiels et bonnes pratiques",
    "subtitle": "Le socle d'un compte AWS : identités, réseau, calcul, stockage et "
                "supervision.",
    "duration": "3 h 30",
    "level": "Intermédiaire",
    "prereq": "chapitre 65",
    "objectives": [
        "Sécuriser les accès avec IAM.",
        "Construire un réseau VPC minimal.",
        "Choisir un service de calcul adapté.",
        "Utiliser le stockage objet correctement.",
        "Superviser et alerter sans bruit.",
    ],
    "blocks": [
        h(2, "IAM : identités et permissions"),
        p("Tout accès AWS passe par IAM. Une permission est accordée par une politique "
          "attachée à une identité ou à une ressource. Le compte root ne doit servir "
          "qu'à la création du compte et à quelques opérations exceptionnelles."),
        table(["Notion", "Rôle", "Bonne pratique"],
              [["Utilisateur", "Identité humaine", "Fédération plutôt que clés"],
               ["Rôle", "Identité assumable", "Préféré aux utilisateurs"],
               ["Politique", "Document JSON", "Moindre privilège"],
               ["Groupe", "Ensemble d'utilisateurs", "Permissions cohérentes"],
               ["Clé d'accès", "Identifiant programmatique", "Éviter, faire tourner"]],
              widths=[3.8, 4.6, 5.0], first_col_bold=True,
              caption="Cinq notions IAM"),
        code("""{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "LireUnSeulPrefixe",
      "Effect": "Allow",
      "Action": ["s3:GetObject", "s3:ListBucket"],
      "Resource": [
        "arn:aws:s3:::mon-site-assets",
        "arn:aws:s3:::mon-site-assets/images/*"
      ]
    }
  ]
}""", "json", "Une politique au moindre privilège"),
        code("""# Qui suis-je et quels droits ai-je ?
aws sts get-caller-identity
aws iam list-attached-user-policies --user-name alice
aws iam simulate-principal-policy \\
  --policy-source-arn arn:aws:iam::123456789012:user/alice \\
  --action-names s3:PutObject \\
  --resource-arns arn:aws:s3:::mon-site-assets/test.txt""", "bash",
             "Trois vérifications"),
        defn("Rôle assumable", "Identité temporaire obtenue par `sts:AssumeRole`, avec des "
                               "identifiants valables de quelques minutes à quelques "
                               "heures. Elle évite les clés d'accès permanentes."),
        box("attention", "Une clé d'accès dans un dépôt public est une compromission",
            "Les robots d'analyse trouvent une clé AWS en quelques minutes. Utilisez des "
            "rôles, des identités de charge de travail, et activez la détection de "
            "secrets dans la CI."),

        h(2, "VPC : un réseau isolé"),
        p("Un VPC délimite un réseau. Les sous-réseaux publics ont une route vers la "
          "passerelle Internet ; les privés sortent par une passerelle NAT ou des points "
          "de terminaison."),
        fig("flow", "Un VPC minimal",
            ["VPC 10.0.0.0/16",
             "Sous-réseau public 10.0.1.0/24 (répartiteur)",
             "Sous-réseau privé 10.0.11.0/24 (application)",
             "Sous-réseau privé 10.0.21.0/24 (base)",
             "Passerelle NAT pour les mises à jour",
             "Points de terminaison pour S3"],
            height=265),
        code("""# Créer un VPC avec deux sous-réseaux
VPC=$(aws ec2 create-vpc --cidr-block 10.0.0.0/16 \\
  --query 'Vpc.VpcId' --output text)

aws ec2 create-subnet --vpc-id $VPC --cidr-block 10.0.1.0/24 \\
  --availability-zone eu-west-3a --query 'Subnet.SubnetId' --output text
aws ec2 create-subnet --vpc-id $VPC --cidr-block 10.0.11.0/24 \\
  --availability-zone eu-west-3b --query 'Subnet.SubnetId' --output text

aws ec2 modify-vpc-attribute --vpc-id $VPC --enable-dns-hostnames""",
             "bash", "Trois commandes"),
        table(["Élément", "Fonction", "Piège"],
              [["Table de routage", "Dirige le trafic", "Une par sous-réseau"],
               ["Passerelle Internet", "Entrée et sortie publiques", "Coût horaire"],
               ["NAT", "Sortie des sous-réseaux privés", "Coût élevé au Go"],
               ["Groupe de sécurité", "Pare-feu avec état", "Pas de refus explicite"],
               ["Liste de contrôle réseau", "Filtre sans état", "À éviter sauf besoin"]],
              widths=[4.4, 4.4, 4.6], first_col_bold=True,
              caption="Cinq éléments réseau"),
        code("""# Groupe de sécurité : autoriser HTTPS depuis Internet uniquement
aws ec2 authorize-security-group-ingress \\
  --group-id sg-0123456789abcdef0 \\
  --protocol tcp --port 443 --cidr 0.0.0.0/0

# Ne jamais ouvrir 22/tcp à 0.0.0.0/0 sans restriction
# Préférer un accès via SSM Session Manager, sans port ouvert""", "bash",
             "Deux règles"),

        h(2, "Calcul"),
        p("AWS propose une gamme étendue de services de calcul. Le choix dépend de la "
          "durée d'exécution, du modèle de trafic et du besoin de contrôle du système."),
        table(["Service", "Modèle", "Adapté à"],
              [["EC2", "Machine virtuelle", "Contrôle complet, charges stables"],
               ["ECS / Fargate", "Conteneurs", "Services conteneurisés"],
               ["EKS", "Kubernetes managé", "Écosystème Kubernetes"],
               ["Lambda", "Fonction", "Événements, charges irrégulières"],
               ["App Runner", "Plateforme", "Service HTTP simple"]],
              widths=[3.4, 3.6, 6.4], first_col_bold=True,
              caption="Cinq services de calcul"),
        code("""# Lancer une instance avec un profil d'instance (sans clé)
aws ec2 run-instances \\
  --image-id ami-0123456789abcdef0 \\
  --instance-type t3.micro \\
  --iam-instance-profile Name=app-role \\
  --subnet-id subnet-0123456789abcdef0 \\
  --security-group-ids sg-0123456789abcdef0 \\
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Projet,Value=demo},{Key=Environnement,Value=test}]'""",
             "bash", "Un lancement étiqueté"),
        p("Le profil d'instance remplace les clés d'accès sur la machine : le code lit "
          "des identifiants temporaires fournis par le service de métadonnées. Aucun "
          "secret n'est stocké sur le disque."),

        h(2, "Stockage"),
        p("S3 stocke des objets, pas des fichiers avec une hiérarchie réelle. Les "
          "classes de stockage et les politiques de cycle de vie déterminent le coût."),
        code("""# Créer un compartiment privé avec chiffrement
aws s3api create-bucket --bucket mon-site-assets --region eu-west-3 \\
  --create-bucket-configuration LocationConstraint=eu-west-3

aws s3api put-public-access-block --bucket mon-site-assets \\
  --public-access-block-configuration \\
  "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"

aws s3api put-bucket-encryption --bucket mon-site-assets \\
  --server-side-encryption-configuration \\
  '{"Rules":[{"ApplyServerSideEncryptionByDefault":{"SSEAlgorithm":"AES256"}}]}'""",
             "bash", "Trois commandes de sécurisation"),
        code("""# Cycle de vie : archivage et suppression
aws s3api put-bucket-lifecycle-configuration --bucket mon-site-assets \\
  --lifecycle-configuration '{
    "Rules": [{
      "ID": "archiver",
      "Filter": {"Prefix": "sauvegardes/"},
      "Status": "Enabled",
      "Transitions": [{"Days": 30, "StorageClass": "STANDARD_IA"},
                      {"Days": 90, "StorageClass": "GLACIER"}],
      "Expiration": {"Days": 365}
    }]
  }'""", "bash", "Une politique de cycle de vie"),
        defn("Classe de stockage", "Niveau de durabilité et de disponibilité d'un objet, "
                                   "avec un coût et un délai de récupération différents. "
                                   "Le choix par défaut est rarement le moins cher à long "
                                   "terme."),

        h(2, "Supervision"),
        p("CloudWatch collecte métriques et journaux. Une alerte inutile est aussi "
          "coûteuse qu'une absence d'alerte : elle apprend à ignorer les notifications."),
        code("""# Alerte sur le taux d'erreur d'une fonction
aws cloudwatch put-metric-alarm \\
  --alarm-name api-erreurs \\
  --metric-name Errors --namespace AWS/Lambda \\
  --dimensions Name=FunctionName,Value=api \\
  --statistic Sum --period 300 --evaluation-periods 2 \\
  --threshold 10 --comparison-operator GreaterThanThreshold \\
  --alarm-actions arn:aws:sns:eu-west-3:123456789012:alertes""",
             "bash", "Une alerte utile"),
        table(["Type d'alerte", "Bruit", "Utilité"],
              [["Processeur > 80 %", "Élevé", "Faible seule"],
               ["Taux d'erreur > seuil", "Faible", "Forte"],
               ["Latence p95 > objectif", "Faible", "Forte"],
               ["Disque plein prévu", "Faible", "Forte"],
               ["Échec de sauvegarde", "Très faible", "Critique"]],
              widths=[4.6, 3.4, 5.4], first_col_bold=True,
              caption="Cinq types d'alerte"),
        box("methode", "Check-list d'un compte AWS",
            items=["Root avec MFA, sans clé d'accès.",
                   "Rôles plutôt qu'utilisateurs pour les services.",
                   "Étiquettes obligatoires à la création.",
                   "Journaux de flux activés sur le VPC.",
                   "Alerte de budget et de facturation.",
                   "Sauvegardes testées, pas seulement planifiées."]),
    ],
    "keypoints": [
        "IAM accorde les permissions ; le compte root ne sert qu'à l'exceptionnel.",
        "Les rôles évitent les clés d'accès permanentes.",
        "Un VPC sépare public et privé par tables de routage.",
        "Un groupe de sécurité est un pare-feu avec état, sans refus explicite.",
        "Le profil d'instance supprime les secrets sur la machine.",
        "S3 stocke des objets ; les classes de stockage changent le coût.",
        "Un compartiment doit bloquer tout accès public par défaut.",
        "Une alerte doit signaler un symptôme, pas une ressource.",
    ],
    "bridge": "AWS est un exemple ; les concepts se retrouvent ailleurs. Le chapitre "
              "suivant compare Azure et Google Cloud.",
    "exercises": [
        ex("Écrire une politique au moindre privilège",
           "Un service doit lire un préfixe S3 et écrire des journaux.",
           ["Limitez les actions.",
            "Limitez les ressources.",
            "Testez avec le simulateur."],
           [("json", """{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["s3:GetObject"],
      "Resource": "arn:aws:s3:::mon-site-assets/public/*"
    },
    {
      "Effect": "Allow",
      "Action": ["logs:CreateLogStream", "logs:PutLogEvents"],
      "Resource": "arn:aws:logs:eu-west-3:123456789012:log-group:/app/api:*"
    }
  ]
}"""),
            "La ressource précise évite d'accorder la lecture de tout le compartiment.",
            "Les permissions de journaux sont limitées au groupe concerné, ce qui empêche "
            "l'écriture dans les journaux d'audit."]),
        ex("Diagnostiquer un accès refusé",
           "Une fonction reçoit `AccessDenied` sur S3.",
           ["Vérifiez le rôle utilisé.",
            "Vérifiez la politique.",
            "Vérifiez la politique de compartiment."],
           [("bash", """aws sts get-caller-identity
aws iam get-role --role-name api-lambda --query 'Role.AssumeRolePolicyDocument'

# Tester la permission effective
aws iam simulate-principal-policy \\
  --policy-source-arn arn:aws:iam::123456789012:role/api-lambda \\
  --action-names s3:GetObject \\
  --resource-arns arn:aws:s3:::mon-site-assets/public/logo.svg

aws s3api get-bucket-policy --bucket mon-site-assets 2>/dev/null"""),
            "Un refus peut venir de la politique d'identité, de la politique de "
            "ressource, ou d'une limite de permissions.",
            "Le simulateur indique la décision finale et la politique qui l'a produite."],
           level="Diagnostic"),
        ex("Réduire la facture S3",
           "Le stockage coûte de plus en plus cher.",
           ["Analysez les classes utilisées.",
            "Ajoutez une politique de cycle de vie.",
            "Vérifiez les versions d'objets."],
           [("bash", """aws s3api list-objects-v2 --bucket mon-site-assets \\
  --query "Contents[].{cle:Key,taille:Size,classe:StorageClass}" --output table

aws s3api get-bucket-lifecycle-configuration --bucket mon-site-assets

# Les versions anciennes s'accumulent si le versionnement est activé
aws s3api list-object-versions --bucket mon-site-assets \\
  --query "Versions[?IsLatest==`false`].[Key,VersionId]" --output text | head"""),
            "Le versionnement sans expiration conserve indéfiniment les anciennes "
            "versions.",
            "Une règle `NoncurrentVersionExpiration` purge automatiquement ces versions."],
           level="FinOps"),
    ],
    "quiz": [
        quiz("Comment éviter les clés d'accès sur une instance EC2 ?",
             ["Les chiffrer sur disque", "Utiliser un profil d'instance",
              "Les mettre dans une variable", "Utiliser root"],
             1,
             "Le profil fournit des identifiants temporaires via le service de "
             "métadonnées."),
        quiz("Quel service fournit un réseau isolé ?",
             ["IAM", "VPC", "S3", "CloudWatch"],
             1,
             "Le VPC délimite le réseau et ses sous-réseaux."),
        quiz("Un groupe de sécurité peut-il refuser explicitement du trafic ?",
             ["Oui", "Non, il autorise seulement", "Seulement en sortie", "Seulement en entrée"],
             1,
             "Il n'existe que des règles d'autorisation ; le reste est refusé."),
        quiz("Que fait une politique de cycle de vie S3 ?",
             ["Chiffre les objets", "Change de classe et supprime après un délai",
              "Bloque l'accès public", "Réplique les objets"],
             1,
             "Elle automatise le passage entre classes et l'expiration."),
        quiz("Quel compte doit être protégé par MFA en priorité ?",
             ["Un utilisateur applicatif", "Le compte root", "Un rôle de service", "Un groupe"],
             1,
             "Le compte root ne doit être utilisé qu'en dernier recours."),
    ],
}
