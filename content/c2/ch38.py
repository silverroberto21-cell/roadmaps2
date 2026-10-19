from bookkit.dsl import (box, code, defn, ex, fig, h, ol, p, quiz, table, ul)

CH = {
    "title": "Observabilité : métriques, journaux et traces",
    "subtitle": "Comprendre ce que fait un système en production sans avoir à le "
                "deviner.",
    "duration": "3 h 30",
    "level": "Avancé",
    "prereq": "chapitre 77",
    "objectives": [
        "Distinguer surveillance et observabilité.",
        "Choisir le bon signal pour une question.",
        "Instrumenter une application avec OpenTelemetry.",
        "Écrire une requête PromQL utile.",
        "Réduire le bruit des alertes.",
    ],
    "blocks": [
        h(2, "Trois signaux, trois questions"),
        p("La surveillance répond à des questions connues d'avance. L'observabilité permet "
          "de répondre à des questions imprévues, à condition que le système émette assez "
          "d'information."),
        table(["Signal", "Répond à", "Coût", "Exemple"],
              [["Métrique", "Combien, à quelle fréquence", "Faible", "Latence p95"],
               ["Journal", "Que s'est-il passé exactement", "Élevé", "Erreur de validation"],
               ["Trace", "Où le temps a-t-il été passé", "Moyen", "Appel base lente"]],
              widths=[3.6, 5.2, 3.0, 4.2], first_col_bold=True,
              caption="Trois signaux"),
        defn("Observabilité", "Capacité à comprendre l'état interne d'un système à partir "
                              "de ses signaux externes, sans modifier le code ni "
                              "redéployer."),
        fig("tree", "Choisir son signal",
            ("Question posée", [
                ("Combien d'erreurs ?", ["Métrique"]),
                ("Quelle requête ?", ["Journal"]),
                ("Quel appel est lent ?", ["Trace"]),
            ]),
            height=230),
        box("pratique", "Les métriques sont peu coûteuses, les journaux ne le sont pas",
            "Une métrique est un agrégat périodique : quelques octets par série et par "
            "intervalle. Un journal est une ligne par événement : multiplié par le trafic, "
            "il devient la première source de coût d'observabilité."),

        h(2, "Métriques"),
        p("Une métrique se nomme, se type et s'étiquette. Le choix des étiquettes est "
          "décisif : chaque combinaison distincte crée une série temporelle."),
        table(["Type", "Usage", "Exemple"],
              [["Compteur", "Total cumulé", "`http_requests_total`"],
               ["Jauge", "Valeur instantanée", "`connections_actives`"],
               ["Histogramme", "Distribution", "`duration_seconds_bucket`"],
               ["Résumé", "Quantiles calculés", "`duration_seconds{quantile}`"]],
              widths=[3.6, 4.6, 5.6], first_col_bold=True,
              caption="Quatre types"),
        code("""# Exposition au format Prometheus
http_requests_total{method="GET",route="/panier",status="200"} 10432
http_request_duration_seconds_bucket{route="/panier",le="0.1"} 9810
http_request_duration_seconds_bucket{route="/panier",le="0.5"} 10390
http_request_duration_seconds_bucket{route="/panier",le="+Inf"} 10432

# Ne jamais mettre un identifiant unique en étiquette
# http_requests_total{user_id="84213"}  → explosion de séries""", "text",
             "Une exposition saine"),
        box("attention", "L'explosion de cardinalité",
            "Une étiquette dont le nombre de valeurs augmente avec le trafic (identifiant "
            "de commande, adresse IP, identifiant de session) multiplie les séries et peut "
            "faire tomber le serveur de métriques. Ces valeurs appartiennent aux journaux "
            "ou aux traces."),
        code("""# Débit de requêtes par route
sum by (route) (rate(http_requests_total[5m]))

# Taux d'erreur
sum(rate(http_requests_total{status=~"5.."}[5m]))
  / sum(rate(http_requests_total[5m]))

# Latence p95 (histogramme)
histogram_quantile(0.95,
  sum by (le, route) (rate(http_request_duration_seconds_bucket[5m])))

# Requêtes les plus lentes
topk(5, sum by (route) (rate(http_request_duration_seconds_sum[5m]))
        / sum by (route) (rate(http_request_duration_seconds_count[5m])))""",
             "promql", "Quatre requêtes"),
        defn("Quantile", "Valeur sous laquelle se situe une proportion donnée des "
                         "observations. Le p95 est la valeur qui couvre 95 % des requêtes : "
                         "il ignore les extrêmes, contrairement à la moyenne."),

        h(2, "Journaux"),
        p("Un journal exploitable est structuré, corrélé et filtrable. Une ligne de texte "
          "libre oblige à écrire des expressions régulières fragiles."),
        code("""{
  "ts": "2026-10-19T14:03:22.481Z",
  "niveau": "erreur",
  "service": "boutique",
  "version": "1.4.2",
  "trace_id": "4bf92f3577b34da6a3ce929d0e0e4736",
  "span_id": "00f067aa0ba902b7",
  "utilisateur": "u-9213",
  "message": "paiement refusé",
  "code": "CARTE_EXPIREE",
  "duree_ms": 812
}""", "json", "Une ligne structurée"),
        table(["Champ", "Rôle", "Obligatoire"],
              [["`ts`", "Horodatage", "Oui"],
               ["`niveau`", "Gravité", "Oui"],
               ["`service`", "Origine", "Oui"],
               ["`trace_id`", "Corrélation", "Oui"],
               ["`message`", "Description", "Oui"],
               ["`code`", "Motif exploitable", "Recommandé"]],
              widths=[3.4, 5.4, 3.8], first_col_bold=True,
              caption="Six champs"),
        code("""# Ne journalisez jamais ces valeurs
# - mots de passe, jetons, cookies
# - numéros de carte complets
# - données de santé identifiantes

# Si une valeur doit être rapprochée, utilisez une empreinte
import hashlib
empreinte = hashlib.sha256(email.encode()).hexdigest()[:12]""", "python",
             "Ce qui ne doit pas apparaître"),
        box("attention", "Le journal est une copie de la base",
            "Un journal trop verbeux reconstitue les données personnelles des "
            "utilisateurs. Il devient alors un traitement de données à part entière, avec "
            "les obligations de conservation et de suppression correspondantes."),

        h(2, "Traces"),
        p("Une trace suit une requête à travers plusieurs services. Chaque étape est un "
          "segment (span) avec un début, une fin et des attributs. Le contexte se propage "
          "d'un service à l'autre."),
        fig("flow", "Une trace distribuée",
            ["Requête utilisateur — 812 ms",
             "Passerelle — 12 ms",
             "Service panier — 180 ms",
             "Service stock — 40 ms",
             "Service paiement — 520 ms",
             "Base de données — 480 ms (dont 300 ms d'attente)"],
            height=250),
        code("""# Instrumentation OpenTelemetry (Node.js)
import { NodeSDK } from "@opentelemetry/sdk-node";
import { OTLPTraceExporter } from "@opentelemetry/exporter-trace-otlp-http";
import { HttpInstrumentation } from "@opentelemetry/instrumentation-http";

const sdk = new NodeSDK({
  serviceName: "boutique",
  traceExporter: new OTLPTraceExporter({ url: "http://collector:4318/v1/traces" }),
  instrumentations: [new HttpInstrumentation()],
});

sdk.start();

// Dans le code métier, un segment manuel
import { trace } from "@opentelemetry/api";
const span = trace.getTracer("boutique").startSpan("calculer-total");
try {
  await calculerTotal(panier);
} finally {
  span.end();
}""", "js", "Une instrumentation standard"),
        table(["Concept", "Rôle", "Piège"],
              [["Trace", "Ensemble des segments", "Échantillonnage nécessaire"],
               ["Span", "Une étape", "Attributs trop nombreux"],
               ["Contexte", "Propagation", "En-têtes perdus par un proxy"],
               ["Échantillonnage", "Réduction du volume", "Biais si mal réglé"],
               ["Collecteur", "Centralisation", "Point de défaillance"]],
              widths=[3.6, 4.6, 5.0], first_col_bold=True,
              caption="Cinq concepts"),
        code("""# Propager l'identifiant de trace dans les journaux
logging.basicConfig(
    format="%(asctime)s %(levelname)s trace_id=%(trace_id)s %(message)s"
)

# Vérifier la propagation sur deux services
curl -s -H "traceparent: 00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01" \\
  http://localhost:8080/panier -o /dev/null""", "python",
             "Corrélation et vérification"),

        h(2, "Alertes utiles"),
        p("Une alerte doit signaler un problème qui demande une action. Une alerte qui se "
          "déclenche sans conséquence apprend aux équipes à l'ignorer."),
        table(["Anti-patron", "Symptôme", "Correction"],
              [["Alerte sur cause", "« CPU élevé »", "Alerter sur l'effet utilisateur"],
               ["Seuil fixe", "Faux positifs", "Seuil relatif ou budget"],
               ["Alerte sans propriétaire", "Personne n'agit", "Assigner une équipe"],
               ["Trop d'alertes", "Fatigue", "Regrouper et hiérarchiser"],
               ["Aucune action", "Bruit", "Supprimer ou convertir en tableau de bord"]],
              widths=[4.2, 4.4, 4.6], first_col_bold=True,
              caption="Cinq anti-patrons"),
        code("""# Alerte sur un symptôme visible par l'utilisateur
- alert: TauxErreurEleve
  expr: |
    sum(rate(http_requests_total{status=~"5.."}[5m]))
      / sum(rate(http_requests_total[5m])) > 0.05
  for: 10m
  labels:
    severite: critique
    equipe: boutique
  annotations:
    resume: "Plus de 5 % d'erreurs sur 10 minutes"
    runbook: "https://wiki/runbooks/boutique-erreurs\"""", "yaml",
             "Une alerte exploitable"),
        code("""# Le routeur d'alertes évite le bruit
route:
  receiver: equipe-boutique
  group_by: [alertname, service]
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 4h
  routes:
    - matchers: [severite="critique"]
      receiver: astreinte
      repeat_interval: 1h
    - matchers: [severite="avertissement"]
      receiver: courriel
      repeat_interval: 24h""", "yaml", "Un routage hiérarchisé"),
        box("methode", "Instrumenter dans le bon ordre",
            items=["Mesurer la latence et le taux d'erreur côté utilisateur.",
                   "Journaliser en JSON avec identifiant de trace.",
                   "Tracer les traversées de service.",
                   "Réduire la cardinalité des métriques.",
                   "Alerter sur les symptômes, pas sur les causes."]),
    ],
    "keypoints": [
        "Métriques, journaux et traces répondent à des questions différentes.",
        "L'observabilité permet de répondre à des questions imprévues.",
        "Une étiquette à cardinalité variable fait exploser les séries.",
        "Le p95 décrit mieux l'expérience que la moyenne.",
        "Un journal structuré se filtre sans expression régulière.",
        "Les journaux ne doivent pas contenir de données personnelles.",
        "Une trace se propage par en-têtes entre services.",
        "Une alerte doit être actionnable et avoir un propriétaire.",
    ],
    "bridge": "Le système est observable. Le chapitre suivant transforme ces signaux en "
              "objectifs de fiabilité.",
    "exercises": [
        ex("Écrire trois requêtes",
           "Une équipe veut le débit, le taux d'erreur et le p95.",
           ["Utilisez `rate`.",
            "Agrégez par route.",
            "Calculez un rapport."],
           [("promql", """# Débit par route sur 5 minutes
sum by (route) (rate(http_requests_total[5m]))

# Taux d'erreur global
sum(rate(http_requests_total{status=~"5.."}[5m]))
  / sum(rate(http_requests_total[5m]))

# p95 par route
histogram_quantile(0.95,
  sum by (le, route) (rate(http_request_duration_seconds_bucket[5m])))"""),
            "`rate` exige un compteur et au moins deux points.",
            "L'agrégation par `le` est obligatoire avant `histogram_quantile`."]),
        ex("Corriger une cardinalité",
           "Une métrique contient 40 000 séries.",
           ["Trouvez l'étiquette fautive.",
            "Déplacez-la vers les journaux.",
            "Vérifiez la baisse."],
           [("text", """# Avant
http_requests_total{route="/commande", commande_id="CMD-88213"} 1
# 40 000 séries, une par commande

# Après
http_requests_total{route="/commande"} 1
# 1 série par route

# L'identifiant reste dans le journal et la trace
{"route": "/commande", "commande_id": "CMD-88213", "trace_id": "..."}"""),
            "Toute étiquette dont le cardinal est proportionnel au trafic est fautive.",
            "Le déplacement vers les journaux conserve la capacité d'investigation."],
           level="Diagnostic"),
        ex("Rédiger une alerte",
           "Les utilisateurs subissent des erreurs depuis dix minutes.",
           ["Alertez sur le taux d'erreur.",
            "Ajoutez une durée.",
            "Joignez un runbook."],
           [("yaml", """- alert: TauxErreurEleve
  expr: |
    sum(rate(http_requests_total{status=~"5.."}[5m]))
      / sum(rate(http_requests_total[5m])) > 0.05
  for: 10m
  labels:
    severite: critique
    equipe: boutique
  annotations:
    resume: "Plus de 5 % d'erreurs depuis 10 minutes"
    runbook: "https://wiki/runbooks/boutique-erreurs\""""),
            "`for` évite les déclenchements sur un pic isolé.",
            "Le runbook transforme l'alerte en action, même à trois heures du matin."]),
    ],
    "quiz": [
        quiz("Quel signal est le moins coûteux ?",
             ["Journal", "Trace", "Métrique", "Tous identiques"],
             2,
             "Une métrique est un agrégat périodique de quelques octets."),
        quiz("Pourquoi éviter les identifiants en étiquette ?",
             ["Ils sont illisibles", "Ils explosent la cardinalité",
              "Ils sont trop longs", "Ils sont chiffrés"],
             1,
             "Chaque valeur distincte crée une série temporelle."),
        quiz("Que mesure le p95 ?",
             ["La moyenne", "La valeur couvrant 95 % des observations",
              "Le maximum", "Le minimum"],
             1,
             "5 % des observations dépassent cette valeur."),
        quiz("À quoi sert un identifiant de trace dans un journal ?",
             ["À chiffrer", "À corréler des événements entre services",
              "À compresser", "À signer"],
             1,
             "Il relie les lignes d'une même requête distribuée."),
        quiz("Quel anti-patron d'alerte est cité ?",
             ["Alerter sur un symptôme", "Alerter sur une cause interne",
              "Assigner un propriétaire", "Joindre un runbook"],
             1,
             "Une cause interne peut n'avoir aucun impact utilisateur."),
    ],
}
