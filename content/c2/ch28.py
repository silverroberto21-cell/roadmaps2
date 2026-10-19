from bookkit.dsl import (box, code, defn, ex, fig, h, ol, p, quiz, table, ul)

CH = {
    "title": "Serverless : fonctions et événements",
    "subtitle": "Exécuter du code sans serveur à gérer, en comprenant les contraintes du "
                "modèle.",
    "duration": "3 h 00",
    "level": "Intermédiaire",
    "prereq": "chapitre 67",
    "objectives": [
        "Reconnaître les charges adaptées au modèle sans serveur.",
        "Écrire une fonction idempotente.",
        "Gérer délais, mémoire et concurrence.",
        "Éviter les pièges de facturation.",
        "Concevoir une chaîne d'événements fiable.",
    ],
    "blocks": [
        h(2, "Le modèle"),
        p("Une fonction est exécutée à la demande, facturée à l'invocation et à la durée. "
          "Le fournisseur gère le système, la montée en charge et la disponibilité. "
          "L'unité de déploiement n'est plus une machine mais une fonction."),
        fig("flow", "Le cycle d'une invocation",
            ["Événement : requête HTTP, fichier, message",
             "Plateforme : instance disponible ou créée",
             "Initialisation du contexte",
             "Exécution du gestionnaire",
             "Retour du résultat ou de l'erreur",
             "Instance gelée, réutilisée ou détruite"],
            height=255),
        table(["Contrainte", "Ordre de grandeur", "Conséquence"],
              [["Durée maximale", "Quelques minutes", "Pas de traitement très long"],
               ["Mémoire", "128 Mo à quelques Go", "Le CPU suit la mémoire"],
               ["Taille du paquet", "Quelques dizaines de Mo", "Dépendances limitées"],
               ["Concurrence", "Quota par compte", "File d'attente en cas de pic"],
               ["Stockage temporaire", "500 Mo à 10 Go", "Éphémère, non partagé"]],
              widths=[4.0, 4.2, 5.0], first_col_bold=True,
              caption="Cinq contraintes"),
        defn("Démarrage à froid", "Création d'une nouvelle instance pour servir une "
                                  "requête. Il dépend de la taille du paquet, du runtime "
                                  "et des initialisations au chargement du module."),

        h(2, "Écrire une fonction"),
        p("Le gestionnaire reçoit un événement et un contexte. La logique doit être "
          "courte, idempotente, et sortir les initialisations coûteuses du gestionnaire "
          "pour les réutiliser entre invocations."),
        code("""// Initialisation hors gestionnaire : réutilisée entre invocations
import { Client } from "pg";

let client;

async function obtenirClient() {
  if (!client) {
    client = new Client({ connectionString: process.env.DATABASE_URL });
    await client.connect();
  }
  return client;
}

export async function handler(event) {
  const { id } = JSON.parse(event.body ?? "{}");
  if (!id) {
    return { statusCode: 400, body: JSON.stringify({ erreur: "id requis" }) };
  }

  const db = await obtenirClient();
  const resultat = await db.query("SELECT * FROM commandes WHERE id = $1", [id]);

  if (!resultat.rowCount) {
    return { statusCode: 404, body: JSON.stringify({ erreur: "introuvable" }) };
  }
  return { statusCode: 200, body: JSON.stringify(resultat.rows[0]) };
}""", "js", "Une fonction avec client réutilisé"),
        table(["Bonne pratique", "Raison", "Effet"],
              [["Initialiser hors gestionnaire", "Réutilisation de l'instance", "Latence réduite"],
               ["Fermer les connexions proprement", "Épuisement du pool", "Stabilité"],
               ["Limiter les dépendances", "Taille du paquet", "Démarrage à froid réduit"],
               ["Journaliser en JSON", "Exploitation", "Recherche facilitée"],
               ["Rendre idempotent", "Réessais automatiques", "Pas de doublon"]],
              widths=[5.0, 4.4, 4.2], first_col_bold=True,
              caption="Cinq bonnes pratiques"),
        code("""// Une fonction idempotente : la même requête peut être rejouée
async function traiterPaiement(evenement) {
  const deja = await db.query(
    "SELECT 1 FROM paiements WHERE idempotency_key = $1",
    [evenement.cle]
  );
  if (deja.rowCount) return { statut: "deja_traite" };

  await db.query("INSERT INTO paiements (idempotency_key, montant) VALUES ($1, $2)",
    [evenement.cle, evenement.montant]);
  return { statut: "traite" };
}""", "js", "Une clé d'idempotence"),
        box("attention", "Les réessais sont automatiques",
            "Une fonction peut être exécutée plusieurs fois pour un même événement en cas "
            "d'erreur ou de délai dépassé. Sans clé d'idempotence, chaque réessai crée un "
            "doublon : double débit, double courriel, double commande."),

        h(2, "Mémoire, délai et concurrence"),
        p("La mémoire allouée détermine le processeur disponible et le coût. Un "
          "réglage par défaut est rarement optimal : la mesure donne le bon compromis."),
        code("""# Mesurer le temps d'exécution par niveau de mémoire
for mem in 256 512 1024 2048; do
  aws lambda update-function-configuration \\
    --function-name api --memory-size $mem >/dev/null
  sleep 5
  aws lambda invoke --function-name api --payload '{"body":"{\\"id\\":1}"}' \\
    /tmp/sortie.json >/dev/null
  echo "$mem Mo : $(grep -o '"duration":[0-9.]*' /tmp/sortie.json)"
done""", "bash", "Une mesure comparative"),
        table(["Situation", "Réglage", "Raison"],
              [["Fonction liée au CPU", "Plus de mémoire", "Le CPU augmente avec la mémoire"],
               ["Fonction d'attente réseau", "Mémoire modérée", "Le CPU n'est pas le facteur"],
               ["Démarrage à froid critique", "Mémoire élevée, paquet réduit", "Moins de latence"],
               ["Coût minimal", "Mesurer, pas deviner", "Le moins cher n'est pas le plus petit"]],
              widths=[5.0, 4.6, 4.0], first_col_bold=True,
              caption="Quatre situations"),
        code("""# Limiter la concurrence pour protéger une base
aws lambda put-function-concurrency \\
  --function-name api --reserved-concurrent-executions 20

# File d'attente en cas de dépassement (asynchrone)
# Configurer une file de lettres mortes pour les échecs
aws lambda update-function-configuration \\
  --function-name api \\
  --dead-letter-config TargetArn=arn:aws:sqs:eu-west-3:123456789012:api-dlq""",
             "bash", "Deux protections"),
        defn("File de lettres mortes", "File qui reçoit les événements qu'une fonction n'a "
                                       "pas pu traiter. Elle évite la perte silencieuse et "
                                       "permet le rejeu après correction."),

        h(2, "Concevoir une chaîne d'événements"),
        p("Un enchaînement de fonctions doit tolérer les échecs partiels. La configuration "
          "la plus robuste combine file d'attente, idempotence et lettre morte."),
        fig("flow", "Une chaîne fiable",
            ["Événement source",
             "File (stockage durable, accusé de réception)",
             "Fonction de traitement",
             "Succès : suppression du message",
             "Échec : réessai avec recul",
             "Échec définitif : file de lettres mortes"],
            height=255),
        code("""# Déclencheur SQS avec traitement par lots
aws lambda create-event-source-mapping \\
  --function-name traiter-commandes \\
  --event-source-arn arn:aws:sqs:eu-west-3:123456789012:commandes \\
  --batch-size 10 \\
  --maximum-batching-window-in-seconds 5 \\
  --function-response-types ReportBatchItemFailures""", "bash",
             "Un déclencheur avec échecs partiels"),
        p("`ReportBatchItemFailures` permet de ne réessayer que les messages en échec : "
          "sans cette option, tout le lot est rejoué et les messages valides sont traités "
          "deux fois."),
        table(["Mécanisme", "Protège contre", "Limite"],
              [["File", "Perte d'événement", "Latence supplémentaire"],
               ["Idempotence", "Doublons", "Nécessite une clé"],
               ["Lettre morte", "Boucle infinie", "Rejeu manuel"],
               ["Limite de concurrence", "Saturation aval", "File d'attente"],
               ["Délai", "Dépendance lente", "Échec explicite"]],
              widths=[4.2, 4.6, 4.8], first_col_bold=True,
              caption="Cinq mécanismes de fiabilité"),

        h(2, "Coût et pièges"),
        p("La facturation à l'usage est avantageuse pour une charge irrégulière, "
          "défavorable pour une charge constante. Quelques pièges suffisent à multiplier "
          "la facture."),
        table(["Piège", "Effet", "Correction"],
              [["Boucle de réessai", "Facture et erreurs", "Lettre morte, idempotence"],
               ["Paquet géant", "Démarrages à froid", "Dépendances minimales"],
               ["Attente active", "Durée facturée élevée", "Événements plutôt que boucles"],
               ["Concurrence non limitée", "Saturation de la base", "Quota réservé"],
               ["Journaux verbeux", "Coût de stockage", "Niveaux et rétention"]],
              widths=[4.2, 4.6, 4.8], first_col_bold=True,
              caption="Cinq pièges de coût"),
        code("""# Surveiller les erreurs et la durée
aws cloudwatch get-metric-statistics \\
  --namespace AWS/Lambda --metric-name Duration \\
  --dimensions Name=FunctionName,Value=api \\
  --start-time 2026-10-01T00:00:00Z --end-time 2026-10-02T00:00:00Z \\
  --period 3600 --statistics Average Maximum""", "bash",
             "Une mesure de durée"),
        box("methode", "Avant d'adopter le serverless",
            items=["La charge est-elle irrégulière ou faible ?",
                   "La durée d'exécution reste-t-elle sous la limite ?",
                   "Les dépendances tiennent-elles dans un paquet raisonnable ?",
                   "Les traitements sont-ils idempotents ?",
                   "Le coût à charge constante a-t-il été comparé ?"]),
    ],
    "keypoints": [
        "Le serverless facture à l'invocation et à la durée.",
        "Les initialisations hors gestionnaire réduisent la latence.",
        "Une fonction peut être exécutée plusieurs fois : l'idempotence est obligatoire.",
        "La mémoire allouée détermine aussi le processeur.",
        "La concurrence se limite pour protéger les dépendances.",
        "Une file de lettres mortes évite la perte silencieuse.",
        "`ReportBatchItemFailures` évite de rejouer tout un lot.",
        "Une charge constante coûte souvent moins cher en permanence.",
    ],
    "bridge": "Les fonctions s'exécutent. Le chapitre suivant décrit l'infrastructure "
              "comme du code, avec Terraform.",
    "exercises": [
        ex("Rendre une fonction idempotente",
           "Un traitement de commande peut être rejoué après un délai dépassé.",
           ["Ajoutez une clé d'idempotence.",
            "Vérifiez avant de traiter.",
            "Consignez le résultat."],
           [("code", """async function traiterCommande(commande) {
  const cle = commande.id;

  const existante = await db.query(
    "SELECT statut FROM commandes WHERE idempotency_key = $1", [cle]
  );
  if (existante.rowCount) return { statut: existante.rows[0].statut, rejoue: true };

  await db.query(
    "INSERT INTO commandes (idempotency_key, montant, statut) VALUES ($1,$2,'en_cours')",
    [cle, commande.montant]
  );

  const resultat = await paiement.debiter(commande);
  await db.query("UPDATE commandes SET statut = $1 WHERE idempotency_key = $2",
    [resultat.statut, cle]);

  return { statut: resultat.statut, rejoue: false };
}"""),
            "La clé est fournie par la source de l'événement, pas générée dans la "
            "fonction.",
            "Le statut intermédiaire permet de distinguer un traitement en cours d'un "
            "traitement terminé."]),
        ex("Choisir la mémoire optimale",
           "Le réglage par défaut coûte cher sans être rapide.",
           ["Mesurez plusieurs niveaux.",
            "Calculez le coût par invocation.",
            "Choisissez le meilleur compromis."],
           [("bash", """# Relevé de mesures
# 256 Mo  : 1 200 ms → coût relatif 1.00
# 512 Mo  :   700 ms → coût relatif 0.58
# 1024 Mo :   480 ms → coût relatif 0.80
# 2048 Mo :   420 ms → coût relatif 1.40

# Le meilleur compromis est 512 Mo : plus rapide et moins cher que 256 Mo"""),
            "Le coût dépend du produit mémoire × durée : augmenter la mémoire peut "
            "réduire la durée plus que proportionnellement.",
            "La mesure doit se faire sur un échantillon représentatif, pas sur une "
            "requête unique."]),
        ex("Concevoir une chaîne fiable",
           "Un fichier déposé doit déclencher un traitement d'image.",
           ["Passez par une file.",
            "Gérez les échecs partiels.",
            "Prévoyez un rejeu."],
           [("markdown", """1. Dépôt S3 → événement `ObjectCreated`
2. Écriture d'un message dans SQS (stockage durable)
3. Fonction déclenchée par SQS, lot de 5
4. Traitement par message, `ReportBatchItemFailures`
5. En cas d'échec après 3 réessais → file de lettres mortes
6. Rejeu manuel après correction, avec la même clé d'idempotence"""),
            "S3 vers Lambda directement fonctionne, mais SQS ajoute un stockage durable "
            "et un mécanisme de réessai contrôlé.",
            "Le rejeu manuel doit être documenté : il fait partie du fonctionnement "
            "normal, pas d'une urgence."],
           level="Architecture"),
    ],
    "quiz": [
        quiz("Sur quoi repose la facturation serverless ?",
             ["Le nombre de serveurs", "Les invocations et la durée",
              "Le stockage seul", "La bande passante"],
             1,
             "La mémoire allouée multiplie la durée facturée."),
        quiz("Pourquoi une fonction doit-elle être idempotente ?",
             ["Pour la sécurité", "Parce qu'elle peut être rejouée",
              "Pour la vitesse", "Pour réduire la mémoire"],
             1,
             "Les réessais automatiques peuvent exécuter deux fois le même événement."),
        quiz("Où placer les initialisations coûteuses ?",
             ["Dans le gestionnaire", "Hors du gestionnaire",
              "Dans une variable locale", "Dans le paquet"],
             1,
             "Elles sont réutilisées si l'instance est réutilisée."),
        quiz("À quoi sert une file de lettres mortes ?",
             ["Accélérer les fonctions", "Conserver les événements non traités",
              "Compresser les messages", "Chiffrer les données"],
             1,
             "Elle permet d'analyser et de rejouer les échecs définitifs."),
        quiz("Quand le serverless coûte-t-il plus cher ?",
             ["Charge irrégulière", "Charge constante et élevée",
              "Petits volumes", "Trafic nocturne"],
             1,
             "Une instance permanente devient plus économique à charge continue."),
    ],
}
