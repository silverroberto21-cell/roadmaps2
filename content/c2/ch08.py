from bookkit.dsl import (box, code, defn, ex, fig, h, ol, p, quiz, table, ul)

CH = {
    "title": "Environnements, secrets et configuration",
    "subtitle": "Séparer ce qui change d'un environnement à l'autre, sans jamais "
                "versionner de secret.",
    "duration": "2 h 45",
    "level": "Intermédiaire",
    "prereq": "chapitre 47",
    "objectives": [
        "Distinguer configuration, code et secret.",
        "Gérer des environnements de développement, de test et de production.",
        "Charger des variables d'environnement proprement.",
        "Choisir un coffre de secrets adapté.",
        "Faire tourner un secret compromis sans interruption.",
    ],
    "blocks": [
        h(2, "Trois natures de données"),
        p("Tout ce qu'une application lit à l'exécution n'a pas le même statut. "
          "Confondre ces catégories conduit soit à versionner des secrets, soit à "
          "recompiler pour changer une URL."),
        table(["Nature", "Exemple", "Où", "Versionné"],
              [["Code", "Fonction, requête", "Dépôt", "Oui"],
               ["Configuration", "Port, niveau de journal", "Variables, fichier", "Oui, par défaut"],
               ["Secret", "Mot de passe, clé d'API", "Coffre", "Jamais"]],
              widths=[3.0, 4.8, 3.4, 2.8], first_col_bold=True,
              caption="Trois natures de données"),
        defn("Configuration douze facteurs", "Principe issu du manifeste Twelve-Factor App : "
                                            "la configuration est stockée dans "
                                            "l'environnement, jamais dans le code, pour "
                                            "que le même artefact fonctionne partout."),
        code("""# Mauvais : la configuration est dans le code
const api = "https://api.production.exemple.fr";

# Bon : la configuration vient de l'environnement
const api = process.env.API_URL;
if (!api) throw new Error("API_URL manquante");""", "js",
             "La configuration sort du code"),

        h(2, "Les environnements"),
        p("Chaque environnement a un rôle. Trop d'environnements coûtent cher à "
          "maintenir ; trop peu font tester en production."),
        table(["Environnement", "Données", "Accès", "Usage"],
              [["Développement", "Fictives", "Local", "Itération rapide"],
               ["Test / intégration", "Fictives", "CI", "Vérification automatique"],
               ["Préproduction", "Copie anonymisée", "Équipe", "Validation finale"],
               ["Production", "Réelles", "Restreint", "Clients"]],
              widths=[3.6, 3.6, 2.6, 4.2], first_col_bold=True,
              caption="Quatre environnements et leur rôle"),
        fig("flow", "Un artefact, plusieurs environnements",
            ["Construction unique",
             "Artefact versionné (image, paquet)",
             "Développement : configuration locale",
             "Préproduction : configuration de recette",
             "Production : configuration réelle",
             "Aucune reconstruction entre les étapes"],
            height=255),
        p("Reconstruire une application pour chaque environnement annule la garantie "
          "que l'artefact testé est celui déployé. La règle est : construire une fois, "
          "configurer à l'exécution."),
        code("""# Une image, plusieurs configurations
docker run -e APP_ENV=production -e LOG_LEVEL=info mon-app:1.4.2
docker run -e APP_ENV=staging   -e LOG_LEVEL=debug mon-app:1.4.2""", "bash",
             "Le même artefact, deux comportements"),

        h(2, "Charger la configuration"),
        p("Un fichier `.env` est un outil de développement local, pas un mécanisme de "
          "production. Il doit être ignoré par Git et chargé explicitement."),
        code("""# .env — développement uniquement
APP_ENV=development
LOG_LEVEL=debug
DATABASE_URL=postgres://app:app@localhost:5432/app
SESSION_SECRET=dev-uniquement-ne-pas-reutiliser""", "text",
             "Un fichier local, ignoré"),
        code("""# .gitignore
.env
.env.*
!.env.example

# .env.example — versionné, sans valeurs sensibles
APP_ENV=development
LOG_LEVEL=debug
DATABASE_URL=
SESSION_SECRET=""", "text", "Un modèle versionné"),
        code("""# Bash : refuser de démarrer si une variable manque
set -euo pipefail
: "${DATABASE_URL:?DATABASE_URL non définie}"

# Docker Compose : valeurs par défaut et fichier local
services:
  app:
    environment:
      LOG_LEVEL: ${LOG_LEVEL:-info}
    env_file:
      - .env.local""", "bash", "Deux chargements explicites"),
        box("attention", "Un secret n'est pas une variable comme les autres",
            "Les variables d'environnement sont visibles dans `/proc/<pid>/environ`, "
            "dans `docker inspect` et dans les journaux d'erreur. Pour un secret "
            "critique, préférez un fichier monté en lecture seule ou un coffre "
            "interrogé au démarrage."),
        table(["Emplacement", "Visibilité", "Recommandation"],
              [["Variable d'environnement", "Processus, outils", "Configuration courante"],
               ["Fichier monté", "Processus uniquement", "Secrets sensibles"],
               ["Coffre (Vault, SOPS)", "Contrôlée et auditée", "Production"],
               ["Argument de commande", "`ps`, historique", "Jamais"],
               ["Commit Git", "Permanent", "Jamais"]],
              widths=[4.2, 4.2, 4.0], first_col_bold=True,
              caption="Cinq emplacements et leur exposition"),

        h(2, "Chiffrer les secrets versionnés"),
        p("Certains secrets doivent accompagner un dépôt : configuration de cluster, "
          "clés de chiffrement de disque. Le chiffrement asymétrique permet de les "
          "versionner sans les exposer."),
        code("""# SOPS avec une clé age
age-keygen -o key.txt
export SOPS_AGE_KEY_FILE=key.txt

sops --encrypt --age age1ql3z... config.yaml > config.enc.yaml
sops --decrypt config.enc.yaml

# Le fichier chiffré est versionné ; la clé privée reste dans le coffre
git add config.enc.yaml""", "bash", "Quatre commandes"),
        code("""# .sops.yaml — règles par chemin
creation_rules:
  - path_regex: secrets/production/.*\\.yaml$
    age: age1ql3z7hjy54pw3hyww5ayyfg7zqgvc7w3j2elw8zmrj2kg5sfn9aqmcac8p
  - path_regex: secrets/developpement/.*\\.yaml$
    age: age1developpement...""", "yaml",
             "Une règle par environnement"),
        defn("Enveloppe de chiffrement", "Technique où une clé de données chiffre le "
                                         "secret, et une clé maîtresse chiffre la clé de "
                                         "données. La rotation de la clé maîtresse ne "
                                         "demande alors qu'un rechiffrement de l'enveloppe."),

        h(2, "Faire tourner un secret"),
        p("Un secret compromis doit être remplacé sans interruption. Une procédure de "
          "rotation préparée à l'avance transforme un incident majeur en opération "
          "courante."),
        ol("Créer le nouveau secret, sans supprimer l'ancien.",
           "Déployer la nouvelle valeur sur les consommateurs.",
           "Vérifier que tout fonctionne avec la nouvelle valeur.",
           "Révoquer l'ancienne valeur.",
           "Consigner la rotation et sa date."),
        code("""# Rotation d'un secret applicatif
# 1. Générer
openssl rand -base64 48

# 2. Écrire dans le coffre sous une nouvelle version
vault kv put secret/app session_key=@nouvelle-cle.txt

# 3. Redémarrer les services consommateurs, un par un
kubectl rollout restart deployment/app

# 4. Vérifier
kubectl rollout status deployment/app

# 5. Révoquer l'ancienne version
vault kv metadata put -max-versions=2 secret/app

# 6. Tracer
echo "$(date -I) rotation session_key terminée" >> journal-rotations.log""",
             "bash", "Six étapes traçables"),
        table(["Secret", "Fréquence", "Durée de validité"],
              [["Clé d'API interne", "Annuelle", "12 mois"],
               ["Mot de passe de base", "Semestrielle", "6 mois"],
               ["Jeton de déploiement", "Trimestrielle", "3 mois"],
               ["Certificat TLS", "Automatique", "90 jours"],
               ["Secret compromis", "Immédiate", "0"]],
              widths=[4.4, 4.0, 4.2], first_col_bold=True,
              caption="Cinq secrets et leur rotation"),
        box("pratique", "Toujours savoir qui lit un secret",
            "Un coffre journalise les accès. Sans journal, une compromission est "
            "indétectable : on ne sait ni quand ni par qui le secret a été lu."),
        box("methode", "Vérifications avant la production",
            items=["`.env` figure dans `.gitignore`.",
                   "`.env.example` documente toutes les variables.",
                   "Aucun secret dans l'historique Git (`git log -p | grep`).",
                   "Les secrets de production sont dans un coffre.",
                   "La procédure de rotation est écrite et testée."]),
    ],
    "keypoints": [
        "Code, configuration et secret sont trois natures distinctes.",
        "La configuration vient de l'environnement, pas du code.",
        "On construit une fois, on configure à l'exécution.",
        "`.env` est un outil local, jamais une source de vérité.",
        "Les variables d'environnement sont visibles par le processus.",
        "SOPS chiffre les secrets qui doivent être versionnés.",
        "Une rotation se prépare avec deux versions simultanées.",
        "Sans journal d'accès, une compromission reste invisible.",
    ],
    "bridge": "L'application a une configuration saine. Reste à la relier au monde : "
              "le chapitre suivant ouvre la partie réseaux.",
    "exercises": [
        ex("Extraire la configuration du code",
           "Une application contient trois URL codées en dur.",
           ["Identifiez les valeurs variables.",
            "Nommez-les selon la convention.",
            "Validez au démarrage."],
           [("code", """// config.js
const requis = ["API_URL", "SESSION_SECRET"];
const manquantes = requis.filter((cle) => !process.env[cle]);
if (manquantes.length) {
  throw new Error(`Variables manquantes : ${manquantes.join(", ")}`);
}

export const config = {
  apiUrl: process.env.API_URL,
  logLevel: process.env.LOG_LEVEL ?? "info",
  port: Number(process.env.PORT ?? 3000),
  sessionSecret: process.env.SESSION_SECRET,
};"""),
            "L'échec au démarrage vaut mieux qu'une erreur obscure à la première requête.",
            "Une valeur par défaut explicite (`info`, `3000`) documente le comportement "
            "attendu."]),
        ex("Chiffrer un fichier de secrets",
           "Un dépôt doit contenir la configuration d'un cluster.",
           ["Générez une paire de clés.",
            "Chiffrez le fichier.",
            "Vérifiez qu'il est illisible sans clé."],
           [("bash", """age-keygen -o age.key
sops --encrypt --age "$(age-keygen -y age.key)" cluster.yaml > cluster.enc.yaml

# Vérifier le contenu chiffré
head -5 cluster.enc.yaml

# Déchiffrer en développement
SOPS_AGE_KEY_FILE=age.key sops --decrypt cluster.enc.yaml"""),
            "La clé privée ne doit jamais être versionnée ; elle vit dans le coffre ou "
            "sur le poste de l'administrateur.",
            "Le contrôle `head` confirme que les valeurs ne sont plus lisibles en clair."]),
        ex("Préparer une rotation",
           "Une clé d'API a été publiée par erreur dans un ticket.",
           ["Créez la nouvelle clé.",
            "Déployez-la progressivement.",
            "Révoquez l'ancienne et vérifiez les journaux."],
           ["La clé est publique dès sa publication : la révocation est obligatoire, "
            "même si aucun usage malveillant n'est détecté.",
            "Déployer d'abord la nouvelle valeur évite une coupure pendant la rotation.",
            "Les journaux d'accès au coffre et de l'API révèlent un usage indu pendant "
            "la fenêtre d'exposition."],
           level="Sécurité"),
    ],
    "quiz": [
        quiz("Où doit vivre la configuration d'une application ?",
             ["Dans le code", "Dans l'environnement d'exécution",
              "Dans l'image de conteneur", "Dans le README"],
             1,
             "Le même artefact doit fonctionner dans tous les environnements."),
        quiz("Pourquoi `.env` ne doit-il jamais être versionné en production ?",
             ["Il est trop gros", "Il contient des secrets et diffère par environnement",
              "Git le refuse", "Il ralentit les tests"],
             1,
             "Le fichier contient des valeurs sensibles propres à un environnement."),
        quiz("Que fait SOPS ?",
             ["Compresser des fichiers", "Chiffrer des fichiers de configuration",
              "Gérer les branches", "Surveiller les services"],
             1,
             "Il chiffre les valeurs tout en laissant la structure lisible."),
        quiz("Quelle est la première étape d'une rotation de secret ?",
             ["Révoquer l'ancien", "Créer le nouveau",
              "Redémarrer les serveurs", "Prévenir les utilisateurs"],
             1,
             "On déploie le nouveau avant de révoquer l'ancien, pour éviter une coupure."),
        quiz("Pourquoi éviter un secret en argument de commande ?",
             ["C'est lent", "Il est visible dans `ps` et l'historique",
              "Cela ne fonctionne pas", "C'est trop long"],
             1,
             "Les arguments de processus sont lisibles par les autres utilisateurs."),
    ],
}
