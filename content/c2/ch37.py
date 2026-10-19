from bookkit.dsl import (box, code, defn, ex, fig, h, ol, p, quiz, table, ul)

CH = {
    "title": "Gestion des secrets",
    "subtitle": "Stocker, distribuer et faire tourner les informations sensibles sans "
                "les laisser traîner dans un dépôt.",
    "duration": "3 h 00",
    "level": "Avancé",
    "prereq": "chapitre 76",
    "objectives": [
        "Distinguer un secret d'une configuration.",
        "Choisir entre coffre, scellement et chiffrement de dépôt.",
        "Brancher un secret dans un conteneur.",
        "Organiser la rotation.",
        "Détecter une fuite et réagir.",
    ],
    "blocks": [
        h(2, "Ce qui est secret, ce qui ne l'est pas"),
        p("Un secret est une valeur dont la divulgation permet d'agir : mot de passe, clé "
          "d'API, certificat privé, jeton. Une configuration est une valeur dont la "
          "divulgation est sans conséquence : nom d'hôte, niveau de journalisation."),
        table(["Valeur", "Nature", "Emplacement"],
              [["Mot de passe de base", "Secret", "Coffre"],
               ["Clé d'API tierce", "Secret", "Coffre"],
               ["Nom de domaine", "Configuration", "Git"],
               ["Niveau de journalisation", "Configuration", "Git"],
               ["Certificat public", "Public", "Git"],
               ["Clé privée TLS", "Secret", "Coffre"]],
              widths=[4.6, 3.6, 4.4], first_col_bold=True,
              caption="Six valeurs classées"),
        box("attention", "Un secret dans Git reste dans l'historique",
            "Supprimer un fichier ne supprime pas son contenu : il reste dans les commits "
            "antérieurs, dans les caches d'interface et dans les clones. La seule réaction "
            "valable est de révoquer la valeur et d'en émettre une nouvelle."),
        defn("Rotation", "Remplacement périodique d'un secret par une nouvelle valeur, "
                         "avec une période de recouvrement pendant laquelle les deux "
                         "valeurs sont acceptées."),

        h(2, "Trois familles de solutions"),
        p("Les outils diffèrent par l'endroit où le secret est lisible et par le moment "
          "où il est déchiffré. Le choix dépend de qui doit pouvoir le lire et quand."),
        table(["Famille", "Exemples", "Secret lisible par"],
              [["Coffre central", "Vault, AWS Secrets Manager", "Application, à l'exécution"],
               ["Secret scellé", "Sealed Secrets, SOPS", "Le contrôleur du cluster"],
               ["Secret chiffré dans Git", "SOPS + KMS", "Ceux qui ont la clé"],
               ["Secret de CI", "Variables protégées", "Le pipeline"]],
              widths=[4.6, 4.6, 4.4], first_col_bold=True,
              caption="Quatre familles"),
        fig("compare", "Deux stratégies",
            ("CHIFFRÉ DANS GIT", ["Versionné avec le code", "Déchiffré au déploiement",
                                  "Simple, mais clé à protéger"],
             "COFFRE CENTRAL", ["Hors du dépôt", "Lu à l'exécution",
                                "Rotation et audit natifs"]),
            height=215),

        h(2, "SOPS et Sealed Secrets"),
        p("Chiffrer un fichier de secrets dans Git rend la configuration complète et "
          "versionnée. Cela déplace le problème : la clé de déchiffrement devient le "
          "secret critique."),
        code("""# .sops.yaml — règles de chiffrement par chemin
creation_rules:
  - path_regex: environnements/production/.*\\.yaml$
    kms: arn:aws:kms:eu-west-3:123456789012:key/abcd-1234
  - path_regex: environnements/recette/.*\\.yaml$
    age: age1ql3z7hjy54pw3hyww5ayyfg7zqgvc7w3j2elw8zmrj2kg5sfn9aqmcac8p

# Chiffrer puis vérifier
sops --encrypt --in-place environnements/production/secrets.yaml
sops --decrypt environnements/production/secrets.yaml | head -3""", "yaml",
             "Un chiffrement par environnement"),
        code("""# Sealed Secrets — chiffrement asymétrique
kubeseal --format yaml < secret.yaml > secret-scellé.yaml

# Le secret scellé est versionné sans risque
apiVersion: bitnami.com/v1alpha1
kind: SealedSecret
metadata:
  name: base
  namespace: production
spec:
  encryptedData:
    motdepasse: AgBy3i4OJSWK+PiTy...""", "yaml", "Un secret scellé"),
        table(["Critère", "SOPS", "Sealed Secrets"],
              [["Portée", "N'importe quel YAML", "Objets Kubernetes"],
               ["Clé", "KMS, age, PGP", "Clé du contrôleur"],
               ["Rotation", "Manuelle", "Par renouvellement de clé"],
               ["Hors cluster", "Oui", "Non"],
               ["Complexité", "Faible", "Moyenne"]],
              widths=[3.8, 4.4, 4.4], first_col_bold=True,
              caption="Cinq critères"),
        box("attention", "Chiffrer ne protège pas d'un dépôt public",
            "Un fichier chiffré peut être publié sans risque immédiat, mais tout le monde "
            "peut tenter de le déchiffrer hors ligne. La clé doit être robuste et "
            "tournée régulièrement."),

        h(2, "Consommer un secret"),
        p("Un conteneur reçoit un secret par variable d'environnement ou par fichier "
          "monté. Le fichier est préférable pour les valeurs longues et pour la rotation "
          "sans redémarrage."),
        code("""# Variable d'environnement
env:
  - name: DATABASE_URL
    valueFrom:
      secretKeyRef:
        name: base
        key: url

# Fichier monté (rotation possible)
volumes:
  - name: secrets
    secret:
      secretName: base
volumeMounts:
  - name: secrets
    mountPath: /run/secrets
    readOnly: true""", "yaml", "Deux modes de montage"),
        code("""# Externe : synchronisation depuis un coffre
apiVersion: external-secrets.io/v1
kind: ExternalSecret
metadata:
  name: base
  namespace: production
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: vault
    kind: ClusterSecretStore
  target:
    name: base
  data:
    - secretKey: motdepasse
      remoteRef:
        key: production/base
        property: motdepasse""", "yaml", "Un secret synchronisé"),
        box("pratique", "Un secret monté n'est pas mis à jour partout",
            "Un fichier monté est rafraîchi par le kubelet, mais l'application doit "
            "relire le fichier. Une variable d'environnement, elle, n'est jamais mise à "
            "jour : elle exige un redémarrage."),

        h(2, "Rotation"),
        p("Faire tourner un secret sans coupure exige que l'ancienne et la nouvelle "
          "valeur soient valides simultanément. Cette période de recouvrement se planifie."),
        ol("Émettre la nouvelle valeur et l'accepter en plus de l'ancienne.",
           "Déployer la nouvelle valeur auprès des consommateurs.",
           "Vérifier que plus aucun consommateur n'utilise l'ancienne.",
           "Révoquer l'ancienne valeur.",
           "Consigner la rotation et sa date."),
        code("""# Vérifier l'âge des secrets (exemple Vault)
vault kv metadata get secret/production/base | grep -E 'created_time|updated_time'

# Renouveler un jeton de base (double validation)
# 1. ajouter le nouveau jeton
# 2. déployer
# 3. attendre la fin des sessions actives
# 4. supprimer l'ancien jeton
# 5. vérifier les erreurs d'authentification

# Détecter un usage résiduel de l'ancien secret
kubectl logs -n production deploy/app --since=1h | grep -c "401\"""",
             "bash", "Trois vérifications"),
        table(["Type de secret", "Durée de vie", "Rotation"],
              [["Mot de passe de base", "6 à 12 mois", "Planifiée"],
               ["Clé d'API", "3 à 6 mois", "Automatisée"],
               ["Jeton de courte durée", "Minutes à heures", "Automatique"],
               ["Certificat TLS", "90 jours", "Automatique (ACME)"],
               ["Clé de chiffrement", "1 an", "Avec ré-chiffrement"]],
              widths=[5.0, 4.0, 4.0], first_col_bold=True,
              caption="Cinq durées de vie"),

        h(2, "Détecter et réagir à une fuite"),
        p("La détection peut être préventive (analyse du dépôt) ou réactive (alerte d'un "
          "fournisseur). Dans les deux cas, la première action est la révocation."),
        table(["Étape", "Action", "Délai cible"],
              [["1", "Révoquer le secret", "Minutes"],
               ["2", "Émettre un remplacement", "Minutes"],
               ["3", "Déployer la nouvelle valeur", "Heures"],
               ["4", "Chercher l'usage malveillant", "Heures"],
               ["5", "Corriger la cause racine", "Jours"],
               ["6", "Documenter et informer", "Jours"]],
              widths=[2.4, 7.6, 4.0], first_col_bold=True,
              caption="Six étapes"),
        code("""# Analyse préventive : chercher des motifs de secrets
gitleaks detect --source . --verbose
trufflehog git file://. --only-verified

# Bloquer avant le commit
pre-commit install
# .pre-commit-config.yaml
# - repo: https://github.com/gitleaks/gitleaks
#   hooks: [{ id: gitleaks }""", "bash", "Trois protections"),
        box("methode", "Règles de gestion des secrets",
            items=["Aucun secret en clair dans un dépôt, même privé.",
                   "Un secret par environnement et par service.",
                   "Un accès nominatif au coffre, journalisé.",
                   "Rotation planifiée et testée.",
                   "Révocation immédiate dès qu'une fuite est suspectée."]),
    ],
    "keypoints": [
        "Un secret est une valeur qui permet d'agir.",
        "Un fichier supprimé reste dans l'historique Git.",
        "Un coffre central lit le secret à l'exécution.",
        "Le chiffrement dans Git déplace le secret vers la clé.",
        "Un fichier monté se rafraîchit, une variable d'environnement non.",
        "La rotation exige une période de recouvrement.",
        "La révocation précède toujours l'analyse.",
        "Un secret détecté est un secret compromis.",
    ],
    "bridge": "Les secrets sont protégés. Le chapitre suivant rend le système "
              "observable.",
    "exercises": [
        ex("Classer des valeurs",
           "Six valeurs doivent être rangées entre Git et coffre.",
           ["Identifiez la nature.",
            "Justifiez chaque choix.",
            "Précisez l'emplacement."],
           ["Nom d'hôte → Git. Niveau de journalisation → Git. Certificat public → Git.",
            "Mot de passe de base → coffre. Clé d'API → coffre. Clé privée → coffre.",
            "Règle : une valeur qui permet d'agir est un secret."]),
        ex("Monter un secret",
           "Une application doit lire un mot de passe sans redémarrage.",
           ["Créez le secret.",
            "Montez-le en fichier.",
            "Faites relire le fichier."],
           [("yaml", """apiVersion: v1
kind: Secret
metadata:
  name: base
  namespace: production
type: Opaque
stringData:
  motdepasse: "changé-a-la-creation"
---
# Montage
volumes:
  - name: secrets
    secret:
      secretName: base
volumeMounts:
  - name: secrets
    mountPath: /run/secrets
    readOnly: true

# L'application relit /run/secrets/motdepasse à chaque connexion"""),
            "`stringData` évite l'encodage base64 manuel à la création.",
            "Le fichier est rafraîchi par le kubelet, avec un délai de l'ordre de la "
            "minute."]),
        ex("Réagir à une fuite",
           "Une clé d'API a été publiée dans un dépôt public.",
           ["Révoquez.",
            "Remplacez.",
            "Cherchez l'usage."],
           [("markdown", """1. Révoquer la clé dans la console du fournisseur (2 min)
2. Créer une nouvelle clé, la stocker dans le coffre
3. Déployer la nouvelle valeur
4. Consulter les journaux d'accès de la clé : adresses, dates, volumes
5. Vérifier les factures et les quotas
6. Ajouter une détection automatique dans la CI
7. Documenter l'incident"""),
            "Attendre avant de révoquer laisse la fenêtre d'exploitation ouverte.",
            "Les journaux du fournisseur permettent de savoir si la clé a servi."],
           level="Incident"),
    ],
    "quiz": [
        quiz("Que faire d'un secret poussé par erreur dans Git ?",
             ["Supprimer le fichier", "Réécrire l'historique", "Révoquer et remplacer",
              "Rendre le dépôt privé"],
             2,
             "La valeur doit être considérée comme compromise."),
        quiz("Quel avantage d'un secret monté en fichier ?",
             ["Il est chiffré", "Il peut être rafraîchi",
              "Il est plus court", "Il évite le coffre"],
             1,
             "Le kubelet met à jour le contenu monté."),
        quiz("Que déplace le chiffrement d'un secret dans Git ?",
             ["Le problème vers la clé", "Rien", "Le secret vers le cluster",
              "Le secret vers la CI"],
             0,
             "La clé de déchiffrement devient le véritable secret."),
        quiz("Pourquoi une période de recouvrement ?",
             ["Pour économiser", "Pour éviter une coupure pendant la rotation",
              "Pour chiffrer", "Pour auditer"],
             1,
             "Les deux valeurs sont acceptées le temps de la bascule."),
        quiz("Quelle est la première action en cas de fuite ?",
             ["Analyser", "Révoquer", "Informer", "Documenter"],
             1,
             "La révocation ferme la fenêtre d'exploitation."),
    ],
}
