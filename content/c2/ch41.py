from bookkit.dsl import (box, code, defn, ex, fig, h, ol, p, quiz, table, ul)

CH = {
    "title": "Messagerie et files d'attente",
    "subtitle": "Découpler les services par des messages, sans perdre ni dupliquer le "
                "travail.",
    "duration": "3 h 15",
    "level": "Avancé",
    "prereq": "chapitre 68",
    "objectives": [
        "Distinguer file et journal d'événements.",
        "Choisir une garantie de livraison.",
        "Concevoir un consommateur idempotent.",
        "Gérer l'ordre et les messages toxiques.",
        "Exploiter une file en production.",
    ],
    "blocks": [
        h(2, "Pourquoi un intermédiaire"),
        p("Un appel direct entre deux services couple leur disponibilité : si le "
          "destinataire est lent ou arrêté, l'appelant attend ou échoue. Une file "
          "interpose un stockage durable qui absorbe les pics et découple les rythmes."),
        fig("compare", "Appel direct et message",
            ("APPEL DIRECT", ["Attente de la réponse", "Panne propagée",
                              "Débit imposé par le plus lent"],
             "VIA UNE FILE", ["Accusé de réception rapide", "Panne absorbée",
                              "Débit lissé"]),
            height=215),
        table(["Besoin", "Solution", "Exemple"],
              [["Distribuer des tâches", "File de travail", "SQS, RabbitMQ"],
               ["Diffuser un événement", "Journal", "Kafka, Kinesis"],
               ["Différer un traitement", "File avec délai", "SQS délai"],
               ["Ordonner par clé", "Partition", "Kafka, SQS FIFO"]],
              widths=[5.0, 4.4, 4.6], first_col_bold=True,
              caption="Quatre besoins"),
        defn("Journal d'événements", "Suite ordonnée et persistante d'enregistrements que "
                                     "plusieurs consommateurs peuvent lire à leur propre "
                                     "position. Les messages ne disparaissent pas à la "
                                     "lecture."),

        h(2, "Garanties de livraison"),
        p("Aucun système distribué ne garantit exactement une fois sans coût important. "
          "En pratique, on choisit au moins une fois et on rend le traitement idempotent."),
        table(["Garantie", "Risque", "Usage"],
              [["Au plus une fois", "Perte de message", "Métriques, journaux"],
               ["Au moins une fois", "Doublon", "Paiement, commande"],
               ["Exactement une fois", "Coût et complexité", "Cas particulier"]],
              widths=[4.4, 4.6, 5.0], first_col_bold=True,
              caption="Trois garanties"),
        code("""# Politique de réessai avec file de lettres mortes (SQS)
aws sqs create-queue --queue-name commandes \\
  --attributes '{
    "VisibilityTimeout": "60",
    "MessageRetentionPeriod": "1209600",
    "RedrivePolicy": "{\\"deadLetterTargetArn\\":\\"arn:aws:sqs:eu-west-3:123456789012:commandes-dlq\\",\\"maxReceiveCount\\":\\"5\\"}"
  }'

# Consommation par lots
aws sqs receive-message --queue-url "$URL" \\
  --max-number-of-messages 10 --wait-time-seconds 20""", "bash",
             "Une file protégée"),
        defn("Message toxique", "Message qu'un consommateur ne parvient jamais à traiter. "
                                "Sans limite de réessai, il bloque la file indéfiniment."),
        box("attention", "Un message toxique bloque une file ordonnée",
            "Sur une file FIFO, un message en échec empêche la progression de tous les "
            "messages suivants de la même clé. La limite de réception et la file de "
            "lettres mortes sont obligatoires."),

        h(2, "Consommateur idempotent"),
        p("Un consommateur peut recevoir deux fois le même message : après un délai de "
          "visibilité expiré, après un redémarrage, après un réessai. Chaque traitement "
          "doit être rejouable sans effet supplémentaire."),
        code("""import json, os, psycopg

def traiter(message):
    corps = json.loads(message["Body"])
    cle = corps["idempotency_key"]

    with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO traitements (cle) VALUES (%s) "
                "ON CONFLICT (cle) DO NOTHING RETURNING cle",
                (cle,),
            )
            if cur.fetchone() is None:
                return "deja_traite"          # doublon ignoré

            cur.execute(
                "UPDATE commandes SET statut = 'payee' WHERE id = %s",
                (corps["commande_id"],),
            )
    return "traite"
""", "python", "Une clé d'idempotence en base"),
        table(["Stratégie", "Support", "Limite"],
              [["Clé unique en base", "Relationnelle", "Écriture supplémentaire"],
               ["Verrou distribué", "Redis", "Expiration à régler"],
               ["État explicite", "Toute base", "Nécessite un modèle clair"],
               ["Déduplication par empreinte", "Journal", "Fenêtre limitée"]],
              widths=[4.8, 4.2, 5.0], first_col_bold=True,
              caption="Quatre stratégies"),
        box("pratique", "Acquittez après le traitement, jamais avant",
            "Supprimer le message dès sa réception fait perdre le travail en cas de "
            "plantage. L'accusé de réception doit suivre l'écriture effective, même s'il "
            "en résulte parfois un doublon."),

        h(2, "Ordre et partitionnement"),
        p("L'ordre global coûte cher : il impose un seul consommateur. En pratique, on "
          "garantit l'ordre par clé métier — une commande, un compte — grâce au "
          "partitionnement."),
        code("""# Producteur Kafka : la clé détermine la partition
kafka-console-producer --topic commandes \\
  --property "parse.key=true" --property "key.separator=:" <<'EOF'
CMD-1001:{"etape":"creee"}
CMD-1001:{"etape":"payee"}
CMD-1002:{"etape":"creee"}
EOF

# Consommation d'un groupe, décalage visible
kafka-consumer-groups --bootstrap-server localhost:9092 \\
  --describe --group paiements""", "bash", "Un ordre par clé"),
        table(["Contrainte", "Conséquence", "Réglage"],
              [["Ordre global", "Un seul consommateur", "À éviter"],
               ["Ordre par clé", "Parallélisme par partition", "Clé métier stable"],
               ["Rejeu", "Position conservée", "Rétention suffisante"],
               ["Débit", "Plus de partitions", "Coût de coordination"]],
              widths=[4.4, 4.6, 4.8], first_col_bold=True,
              caption="Quatre conséquences"),
        fig("flow", "Un pipeline d'événements",
            ["Service producteur",
             "Journal partitionné (clé = commande)",
             "Groupe de consommateurs",
             "Traitement idempotent",
             "Écriture en base",
             "Accusé de réception et métriques"],
            height=250),

        h(2, "Exploiter"),
        p("Une file se surveille comme un service : profondeur, âge du plus ancien "
          "message, taux d'échec, nombre de réessais. Ces quatre indicateurs révèlent un "
          "consommateur trop lent ou bloqué."),
        table(["Indicateur", "Seuil d'alerte", "Interprétation"],
              [["Profondeur", "Croissance continue", "Consommateur trop lent"],
               ["Âge du plus ancien", "> 5 min", "Traitement en retard"],
               ["Taux d'échec", "> 1 %", "Cause de traitement"],
               ["Réessais", "> 3 par message", "Message toxique probable"]],
              widths=[4.4, 4.4, 5.0], first_col_bold=True,
              caption="Quatre indicateurs"),
        code("""# Métriques CloudWatch d'une file SQS
aws cloudwatch get-metric-statistics \\
  --namespace AWS/SQS --metric-name ApproximateAgeOfOldestMessage \\
  --dimensions Name=QueueName,Value=commandes \\
  --start-time 2026-10-19T00:00:00Z --end-time 2026-10-19T12:00:00Z \\
  --period 300 --statistics Maximum

# Inspecter la file de lettres mortes
aws sqs receive-message --queue-url "$DLQ" --max-number-of-messages 5""",
             "bash", "Deux diagnostics"),
        box("methode", "Concevoir une file",
            items=["Une clé métier qui garantit l'ordre utile.",
                   "Une limite de réessai et une file de lettres mortes.",
                   "Un consommateur idempotent, testé par rejeu.",
                   "Une rétention compatible avec le rejeu prévu.",
                   "Une alerte sur l'âge du plus ancien message."]),
    ],
    "keypoints": [
        "Une file découple la disponibilité et lisse les pics.",
        "Un journal se lit à sa propre position, sans consommer.",
        "« Au moins une fois » impose l'idempotence.",
        "On acquitte après le traitement, jamais avant.",
        "Un message toxique exige une limite de réessai.",
        "L'ordre se garantit par clé, pas globalement.",
        "Quatre indicateurs suffisent à surveiller une file.",
        "La rétention doit couvrir le rejeu prévu.",
    ],
    "bridge": "Les services communiquent par messages. Le chapitre suivant mesure ce "
              "qu'ils peuvent supporter.",
    "exercises": [
        ex("Configurer réessais et lettres mortes",
           "Un consommateur échoue parfois sur des messages corrompus.",
           ["Ajoutez une limite.",
            "Créez la file de lettres mortes.",
            "Vérifiez le routage."],
           [("bash", """aws sqs create-queue --queue-name commandes-dlq
aws sqs create-queue --queue-name commandes \\
  --attributes '{
    "VisibilityTimeout": "60",
    "RedrivePolicy": "{\\"deadLetterTargetArn\\":\\"arn:aws:sqs:eu-west-3:123456789012:commandes-dlq\\",\\"maxReceiveCount\\":\\"5\\"}"
  }'

# Envoyer un message volontairement invalide, puis constater
aws sqs get-queue-attributes --queue-url "$DLQ" \\
  --attribute-names ApproximateNumberOfMessages"""),
            "`maxReceiveCount` compte les réceptions, pas les échecs métier.",
            "La file de lettres mortes doit elle-même être surveillée : y déposer un "
            "message est un signal."]),
        ex("Rendre un traitement rejouable",
           "Le même message peut arriver deux fois.",
           ["Ajoutez une clé.",
            "Rendez l'insertion conditionnelle.",
            "Testez le rejeu."],
           [("python", """def traiter(corps):
    with psycopg.connect(DSN) as conn, conn.cursor() as cur:
        cur.execute(
            "INSERT INTO traitements (cle) VALUES (%s) "
            "ON CONFLICT (cle) DO NOTHING RETURNING cle", (corps["cle"],))
        if cur.fetchone() is None:
            return "deja_traite"
        cur.execute("UPDATE stock SET qte = qte - %s WHERE sku = %s",
                    (corps["qte"], corps["sku"]))
    return "traite\""""),
            "L'insertion conditionnelle sert de verrou : une seule exécution passe.",
            "Le test consiste à appeler deux fois la fonction avec le même corps."],
           level="Fiabilité"),
        ex("Diagnostiquer un retard",
           "L'âge du plus ancien message dépasse trente minutes.",
           ["Comparez débit entrant et sortant.",
            "Cherchez un message bloquant.",
            "Proposez une correction."],
           [("text", """Entrant : 120 msg/min
Sortant : 118 msg/min
Âge du plus ancien : 34 min

Hypothèse 1 : consommateur trop lent → augmenter le parallélisme
Hypothèse 2 : message toxique → vérifier les réessais et la DLQ
Hypothèse 3 : partition bloquée → inspecter le décalage par partition

Décision : mesurer le temps de traitement par message avant d'ajouter
des consommateurs ; si un message dépasse 10x la médiane, le sortir de la file."""),
            "L'écart de débit explique la croissance de la profondeur : 2 msg/min "
            "s'accumulent.",
            "Ajouter des consommateurs ne résout pas un message qui bloque une partition."],
           level="Diagnostic"),
    ],
    "quiz": [
        quiz("Que garantit une file « au moins une fois » ?",
             ["Aucun doublon", "Aucune perte", "Un ordre global", "Une latence nulle"],
             1,
             "Le message peut être livré plusieurs fois, mais pas perdu."),
        quiz("Quand faut-il acquitter un message ?",
             ["À la réception", "Après le traitement", "Jamais", "Au redémarrage"],
             1,
             "Un accusé trop tôt fait perdre le travail en cas de panne."),
        quiz("À quoi sert une file de lettres mortes ?",
             ["Accélérer", "Isoler les messages non traitables",
              "Compresser", "Ordonner"],
             1,
             "Elle évite le blocage et permet l'analyse."),
        quiz("Comment garantir l'ordre utile ?",
             ["Un seul consommateur", "Par clé métier", "Par heure", "Par taille"],
             1,
             "Le partitionnement par clé conserve l'ordre de chaque entité."),
        quiz("Quel indicateur révèle un consommateur bloqué ?",
             ["Le nombre de producteurs", "L'âge du plus ancien message",
              "La taille du disque", "Le nombre de partitions"],
             1,
             "Il mesure le retard réel du traitement."),
    ],
}
