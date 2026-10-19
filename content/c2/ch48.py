from bookkit.dsl import (box, code, defn, ex, fig, h, ol, p, quiz, table, ul)

CH = {
    "title": "Journalisation, audit et conservation",
    "subtitle": "Garder les traces utiles, supprimer les données inutiles et pouvoir "
                "prouver ce qui s'est passé.",
    "duration": "3 h 00",
    "level": "Avancé",
    "prereq": "chapitre 78",
    "objectives": [
        "Distinguer journal d'application, journal d'audit et piste d'audit.",
        "Concevoir une politique de rétention.",
        "Protéger l'intégrité des journaux.",
        "Répondre à une demande d'accès ou de suppression.",
        "Éviter la collecte inutile.",
    ],
    "blocks": [
        h(2, "Trois journaux différents"),
        p("Un journal d'application raconte ce que fait le logiciel ; un journal d'audit "
          "raconte qui a modifié le système ; une piste d'audit métier raconte qui a "
          "exercé quelle action sur quelles données. Les trois n'ont ni la même durée de "
          "vie ni le même public."),
        table(["Journal", "Contenu", "Destinataire"],
              [["Application", "Requêtes, erreurs, traces", "Équipe technique"],
               ["Système", "Services, noyau, authentification", "Exploitation et sécurité"],
               ["Audit Kubernetes", "Appels à l'API", "Sécurité et conformité"],
               ["Métier", "Actions sur les données", "Métier et juridique"]],
              widths=[4.2, 5.0, 4.8], first_col_bold=True,
              caption="Quatre journaux"),
        defn("Journal d'audit", "Enregistrement horodaté et attribuable des actions "
                                "sensibles : qui, quand, depuis où, sur quelle ressource et "
                                "avec quel résultat. Il doit être inaltérable."),
        fig("flow", "Le trajet d'une trace",
            ["Événement applicatif",
             "Écriture structurée sur la sortie standard",
             "Collecte par l'agent du nœud",
             "Agrégation et indexation",
             "Rétention par politique",
             "Recherche pendant une enquête"],
            height=250),
        code("""# Journal d'audit Kubernetes : politique minimale
apiVersion: audit.k8s.io/v1
kind: Policy
rules:
  - level: Metadata
    verbs: ["get", "list", "watch"]
  - level: RequestResponse
    verbs: ["create", "update", "patch", "delete"]
    resources:
      - group: ""
        resources: ["secrets", "configmaps"]
      - group: "rbac.authorization.k8s.io"
        resources: ["roles", "rolebindings", "clusterrolebindings"]
  - level: None
    users: ["system:kube-proxy"]""", "yaml", "Une politique d'audit"),
        table(["Niveau", "Enregistre", "Volume"],
              [["`None`", "Rien", "Nul"],
               ["`Metadata`", "Qui, quoi, quand", "Faible"],
               ["`Request`", "Métadonnées et corps de requête", "Moyen"],
               ["`RequestResponse`", "Requête et réponse", "Élevé"]],
              widths=[4.4, 5.0, 4.6], first_col_bold=True,
              caption="Quatre niveaux"),

        h(2, "Rétention"),
        p("Conserver tout pour toujours coûte cher et augmente l'exposition. Conserver "
          "trop peu empêche toute enquête. La durée se décide par catégorie, en fonction "
          "d'un besoin réel."),
        table(["Catégorie", "Durée typique", "Justification"],
              [["Journaux applicatifs", "30 à 90 jours", "Diagnostic courant"],
               ["Audit de sécurité", "1 an", "Enquête et conformité"],
               ["Audit d'accès aux données", "Selon obligation", "Preuve légale"],
               ["Métriques fines", "15 à 90 jours", "Analyse de tendance"],
               ["Traces", "7 à 30 jours", "Diagnostic de performance"]],
              widths=[5.0, 4.0, 5.0], first_col_bold=True,
              caption="Cinq durées"),
        code("""# Cycle de vie : chaud 30 jours, froid 1 an, suppression ensuite
aws s3api put-bucket-lifecycle-configuration \\
  --bucket journaux-app \\
  --lifecycle-configuration '{
    "Rules": [{
      "ID": "retention",
      "Filter": {"Prefix": "applicatif/"},
      "Status": "Enabled",
      "Transitions": [
        {"Days": 30, "StorageClass": "STANDARD_IA"},
        {"Days": 90, "StorageClass": "GLACIER"}
      ],
      "Expiration": {"Days": 400}
    }]
  }'""", "bash", "Une politique de cycle de vie"),
        box("attention", "Un journal expiré ne revient pas",
            "Une enquête ouverte trois mois après un incident ne trouvera rien si la "
            "rétention était de trente jours. La durée se fixe avec les parties prenantes, "
            "pas par défaut technique."),
        defn("Pseudonymisation", "Remplacement des identifiants directs par une valeur "
                                 "calculée, réversible seulement avec une clé conservée "
                                 "séparément. Elle réduit l'exposition sans rendre l'analyse "
                                 "impossible."),

        h(2, "Protéger l'intégrité"),
        p("Un journal modifiable par l'attaquant ne prouve rien. Trois mesures le "
          "protègent : l'écriture en ajout seul, la séparation des droits et la copie "
          "externe."),
        code("""# Compte d'écriture seul : peut publier, ne peut pas supprimer
# (principe appliqué côté fournisseur ou côté objet immuable)
aws s3api put-bucket-versioning --bucket journaux-audit \\
  --versioning-configuration Status=Enabled

aws s3api put-object-lock-configuration --bucket journaux-audit \\
  --object-lock-configuration '{
    "ObjectLockEnabled": "Enabled",
    "Rule": {"DefaultRetention": {"Mode": "COMPLIANCE", "Days": 365}}
  }'

# Séparer les rôles : l'application écrit, la sécurité lit
aws iam attach-role-policy --role-name app-journaux \\
  --policy-arn arn:aws:iam::aws:policy/...""", "bash", "Trois protections"),
        table(["Mesure", "Protège de", "Coût"],
              [["Ajout seul", "Falsification", "Faible"],
               ["Verrou d'objet", "Suppression", "Faible"],
               ["Compte séparé", "Compromission applicative", "Moyen"],
               ["Horodatage externe", "Antidatage", "Élevé"]],
              widths=[4.2, 5.4, 4.4], first_col_bold=True,
              caption="Quatre mesures"),
        box("pratique", "Le journal ne doit pas contenir ce que l'attaquant cherche",
            "Un journal qui enregistre des jetons, des mots de passe ou des numéros de "
            "carte complets devient une base de secrets. Filtrez à l'émission, pas à la "
            "lecture."),

        h(2, "Demandes d'accès et de suppression"),
        p("Les journaux contiennent des données personnelles dès qu'ils identifient une "
          "personne. Ils entrent donc dans le périmètre des demandes d'accès et de "
          "suppression, avec des exceptions légales à documenter."),
        ol("**Localiser** : savoir dans quels index et quelle rétention se trouve la donnée.",
           "**Extraire** : produire un export lisible pour la demande d'accès.",
           "**Supprimer** : effacer dans les journaux actifs et les copies froides.",
           "**Documenter** : consigner la demande, la réponse et l'exception appliquée."),
        code("""# Rechercher un identifiant dans les journaux (exemple OpenSearch)
curl -s -X GET "https://journaux.exemple.fr/applicatif/_search" \\
  -H "Content-Type: application/json" -d '{
    "query": {"term": {"empreinte_utilisateur": "a1b2c3d4e5f6"}},
    "size": 0,
    "aggs": {"par_jour": {"date_histogram": {"field": "@timestamp", "calendar_interval": "day"}}}
  }' | jq '.aggregations.par_jour.buckets'

# Supprimer par requête (si la politique le permet)
# POST applicatif/_delete_by_query
# { "query": { "term": { "empreinte_utilisateur": "a1b2c3d4e5f6" } } }""",
             "bash", "Deux opérations"),
        table(["Situation", "Réponse", "Trace à conserver"],
              [["Demande d'accès", "Export sous 30 jours", "Demande et date"],
               ["Demande de suppression", "Effacement ou exception motivée", "Décision"],
               ["Enquête de sécurité", "Conservation prolongée", "Motif et durée"],
               ["Litige", "Conservation jusqu'à clôture", "Référence du dossier"]],
              widths=[4.6, 5.0, 4.4], first_col_bold=True,
              caption="Quatre situations"),

        h(2, "Ce qu'il faut arrêter de collecter"),
        p("La première optimisation de coût et de risque consiste à ne pas collecter. "
          "Chaque champ supplémentaire est une donnée à protéger, à chercher et à purger."),
        table(["Champ", "Utilité réelle", "Décision"],
              [["Corps complet de requête", "Parfois", "Journaliser à la demande"],
               ["Adresse IP complète", "Sécurité", "Tronquer après 30 jours"],
               ["Identifiant de session", "Diagnostic", "Pseudonymiser"],
               ["Numéro de carte", "Aucune", "Ne jamais journaliser"],
               ["Pile d'appels complète", "Diagnostic", "Limiter aux erreurs"]],
              widths=[5.0, 4.4, 4.6], first_col_bold=True,
              caption="Cinq décisions"),
        code("""# Filtrage à l'émission : jamais de secret dans la sortie
import logging, re

SECRETS = re.compile(r"(password|token|authorization|cookie)", re.I)

class FiltreSensible(logging.Filter):
    def filter(self, record):
        message = record.getMessage()
        if SECRETS.search(message):
            record.msg = "[message filtré]"
            record.args = ()
        return True

logging.getLogger().addFilter(FiltreSensible())""", "python", "Un filtre à l'émission"),
        box("methode", "Politique de journalisation",
            items=["Une catégorie de journal par besoin.",
                   "Une durée de rétention décidée et documentée.",
                   "Aucune donnée sensible à l'émission.",
                   "Intégrité assurée par ajout seul et copie externe.",
                   "Une procédure d'accès et de suppression testée."]),
    ],
    "keypoints": [
        "Journal d'application, journal d'audit et piste métier ont des publics distincts.",
        "Le niveau d'audit détermine le volume enregistré.",
        "La rétention se décide par catégorie selon un besoin réel.",
        "Un journal expiré ne revient pas lors d'une enquête.",
        "L'intégrité exige l'ajout seul et une copie externe.",
        "Le journal ne doit jamais contenir de secrets.",
        "Les journaux relèvent des demandes d'accès et de suppression.",
        "Ne pas collecter est la première optimisation.",
    ],
    "bridge": "Les traces sont conservées et protégées. Le chapitre suivant met "
              "l'ensemble en œuvre.",
    "exercises": [
        ex("Définir une politique de rétention",
           "Les journaux applicatifs coûtent trop cher.",
           ["Classez les journaux.",
            "Fixez les durées.",
            "Automatisez la transition."],
           [("markdown", """| Catégorie | Chaud | Froid | Suppression |
| Applicatif | 30 j | 90 j | 180 j |
| Audit sécurité | 90 j | 12 mois | 18 mois |
| Métriques fines | 15 j | 90 j (agrégées) | 13 mois |
| Traces | 7 j | — | 7 j |"""),
            "Les journaux d'audit ont une durée plus longue : ils servent de preuve.",
            "L'agrégation des métriques permet de garder la tendance à faible coût."]),
        ex("Protéger un journal d'audit",
           "Un attaquant ne doit pas pouvoir effacer ses traces.",
           ["Activez le mode ajout seul.",
            "Séparez les droits.",
            "Vérifiez la suppression impossible."],
           [("bash", """aws s3api put-object-lock-configuration --bucket journaux-audit \\
  --object-lock-configuration '{
    "ObjectLockEnabled": "Enabled",
    "Rule": {"DefaultRetention": {"Mode": "COMPLIANCE", "Days": 365}}
  }'

# Test : la suppression doit échouer
aws s3 rm s3://journaux-audit/audit/2026-10-19.json
# An error occurred (AccessDenied)"""),
            "Le mode `COMPLIANCE` interdit la suppression même par un administrateur.",
            "Le test de suppression fait partie de la vérification : sans lui, la "
            "configuration n'est pas prouvée."],
           level="Sécurité"),
        ex("Répondre à une demande d'accès",
           "Un utilisateur demande toutes les traces le concernant.",
           ["Pseudonymisez les identifiants.",
            "Recherchez par empreinte.",
            "Exportez et consignez."],
           [("text", """1. Calcul de l'empreinte de l'adresse : sha256("u@exemple.fr")[:12]
2. Recherche dans les index applicatif et audit (≤ 30 jours)
3. Export des événements : horodatage, action, résultat — sans données d'autres personnes
4. Remise sécurisée sous 30 jours
5. Consignation : date de demande, périmètre, réponse, durée de traitement"""),
            "L'empreinte permet de retrouver les lignes sans stocker l'adresse en clair.",
            "L'export ne doit contenir que les événements de la personne concernée."],
           level="Conformité"),
    ],
    "quiz": [
        quiz("Que doit garantir un journal d'audit ?",
             ["Sa rapidité", "Son intégrité et son attribution",
              "Sa taille", "Sa couleur"],
             1,
             "Il sert de preuve : il ne doit pas être modifiable."),
        quiz("Que détermine le niveau `RequestResponse` ?",
             ["Rien", "L'enregistrement du corps de requête et de réponse",
              "La durée de rétention", "Le chiffrement"],
             1,
             "Il produit le plus gros volume d'audit."),
        quiz("Pourquoi ne pas journaliser les jetons ?",
             ["Trop longs", "Le journal devient une base de secrets",
              "Trop lents", "Non supportés"],
             1,
             "Un journal lisible par l'attaquant lui donne les clés."),
        quiz("Que fait le mode `COMPLIANCE` d'un verrou d'objet ?",
             ["Autorise la suppression", "Interdit la suppression pendant la durée",
              "Chiffre les objets", "Compresse"],
             1,
             "Même un administrateur ne peut pas lever le verrou avant l'échéance."),
        quiz("Première optimisation d'un volume de journaux ?",
             ["Compresser", "Ne pas collecter l'inutile", "Chiffrer", "Indexer"],
             1,
             "Chaque champ inutile coûte et expose."),
    ],
}
