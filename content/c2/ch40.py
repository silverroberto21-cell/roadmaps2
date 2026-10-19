from bookkit.dsl import (box, code, defn, ex, fig, h, ol, p, quiz, table, ul)

CH = {
    "title": "Projet final : une plateforme du commit à la production",
    "subtitle": "Assembler tout ce qui précède en un système livré, observable et "
                "exploitable.",
    "duration": "8 h 00",
    "level": "Projet",
    "prereq": "l'ensemble du cours",
    "objectives": [
        "Concevoir une plateforme complète et justifier ses choix.",
        "Automatiser de la construction à la production.",
        "Rendre le système observable et réversible.",
        "Documenter l'exploitation.",
        "Évaluer son travail avec une grille explicite.",
    ],
    "blocks": [
        h(2, "Le cahier des charges"),
        p("Vous devez livrer une petite application de gestion de commandes, avec une "
          "interface, une API et une base de données. Le système doit être reconstruit "
          "intégralement depuis un dépôt, sans intervention manuelle."),
        table(["Exigence", "Critère d'acceptation", "Chapitre de référence"],
              [["Reproductibilité", "Une machine neuve suffit", "74 à 76"],
               ["Livraison", "Pipeline vert puis déploiement", "78, 79"],
               ["Réversibilité", "Retour à la version précédente en 5 min", "80, 81"],
               ["Sécurité", "Aucun secret en clair", "77, 82"],
               ["Observabilité", "Trois signaux disponibles", "83"],
               ["Exploitation", "Runbook et objectifs écrits", "84"]],
              widths=[4.0, 5.8, 4.2], first_col_bold=True,
              caption="Six exigences"),
        box("attention", "Le projet se juge sur le système, pas sur le code",
            "Une application brillante déployée à la main ne satisfait pas le cahier des "
            "charges. À l'inverse, une application banale entièrement automatisée et "
            "observable le satisfait."),
        defn("Livrable", "Élément vérifiable remis à la fin du projet : dépôt, pipeline, "
                         "manifestes, documentation d'exploitation, journal d'incident "
                         "simulé."),

        h(2, "Architecture cible"),
        p("Le système tient dans un cluster unique. Trois environnements isolés partagent "
          "les mêmes manifestes, avec des surcouches de configuration."),
        fig("stack", "Les couches du système",
            ["Interface web (conteneur statique)",
             "API (conteneur applicatif, 3 réplicas)",
             "Base PostgreSQL (volume persistant)",
             "Ingress et certificat TLS",
             "Observabilité : métriques, journaux, traces",
             "Déploiement : images signées, GitOps"],
            height=265),
        code("""plateforme/
├── app/                    # code applicatif et tests
│   ├── Dockerfile
│   └── src/
├── infra/                  # Terraform : cluster, réseau, registre
│   ├── modules/
│   └── environnements/
├── deploiement/            # manifestes Kubernetes
│   ├── base/
│   └── environnements/{recette,production}
├── .github/workflows/      # CI/CD
└── docs/                   # runbooks, décisions, objectifs""", "text",
             "Un dépôt, quatre responsabilités"),
        p("Séparer `app`, `infra` et `deploiement` évite qu'un changement de code "
          "déclenche un changement d'infrastructure. Les trois dépôts peuvent être "
          "distincts dans une organisation réelle ; un seul dépôt avec trois dossiers "
          "suffit ici."),

        h(2, "Jalon 1 — Une application livrable"),
        p("Avant d'automatiser, l'application doit se construire et se tester en une "
          "commande, sur une machine neuve."),
        code("""# Dockerfile multi-étapes
FROM node:22-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --omit=dev

FROM node:22-alpine AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:22-alpine
WORKDIR /app
ENV NODE_ENV=production
COPY --from=deps /app/node_modules ./node_modules
COPY --from=build /app/dist ./dist
USER node
EXPOSE 3000
CMD ["node", "dist/serveur.js"]""", "dockerfile", "Une image en trois étapes"),
        table(["Vérification", "Commande", "Attendu"],
              [["Construction locale", "`docker build -t app .`", "Succès"],
               ["Tests", "`npm test`", "Tous verts"],
               ["Image non privilégiée", "`docker run --user 1000`", "Démarre"],
               ["Taille", "`docker images`", "Moins de 200 Mo"],
               ["Analyse", "`trivy image`", "Aucune faille critique"]],
              widths=[4.6, 4.8, 4.4], first_col_bold=True,
              caption="Cinq vérifications"),

        h(2, "Jalon 2 — Un pipeline complet"),
        p("Le pipeline vérifie, construit, signe et publie. Il ne déploie pas directement : "
          "le déploiement appartient au dépôt de manifestes."),
        code("""name: livraison
on:
  push:
    branches: [main]

permissions:
  contents: read
  packages: write
  id-token: write

jobs:
  verifier:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 22, cache: npm }
      - run: npm ci
      - run: npm run lint && npm test

  publier:
    needs: verifier
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
      - uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - uses: docker/build-push-action@v6
        with:
          push: true
          tags: ghcr.io/${{ github.repository }}:${{ github.sha }}
      - uses: sigstore/cosign-installer@v3
      - run: cosign sign --yes ghcr.io/${{ github.repository }}:${{ github.sha }}""",
             "yaml", "Un pipeline en deux tâches"),
        table(["Étape", "Preuve attendue", "Échec typique"],
              [["Lint et tests", "Journal vert", "Test instable"],
               ["Construction", "Image publiée", "Dépendance manquante"],
               ["Signature", "Attestation vérifiable", "Permission OIDC absente"],
               ["Mise à jour du dépôt", "Demande de fusion automatique", "Jeton en lecture seule"]],
              widths=[4.4, 4.8, 4.6], first_col_bold=True,
              caption="Quatre étapes et leurs preuves"),

        h(2, "Jalon 3 — L'infrastructure décrite"),
        p("Le cluster, le réseau et le registre sont décrits en Terraform. L'état est "
          "distant et verrouillé ; un second environnement peut être créé par "
          "changement de variables."),
        code("""# infra/environnements/recette/main.tf
module "cluster" {
  source = "../../modules/cluster"

  nom           = "plateforme-recette"
  region        = "eu-west-3"
  noeuds_min    = 2
  noeuds_max    = 4
  version_k8s   = "1.31"
}

output "kubeconfig" {
  value     = module.cluster.kubeconfig
  sensitive = true
}""", "hcl", "Un environnement paramétré"),
        box("pratique", "Un `plan` sans surprise",
            "Avant d'appliquer, le plan doit annoncer uniquement des ajouts lors d'une "
            "création et aucune destruction lors d'une mise à jour. Toute destruction "
            "inattendue est traitée comme un défaut du projet."),

        h(2, "Jalon 4 — Le déploiement convergent"),
        p("Les manifestes décrivent l'état désiré ; un agent le réconcilie. La version de "
          "l'image est un paramètre du dépôt, jamais une modification manuelle."),
        code("""# deploiement/environnements/production/kustomization.yaml
resources:
  - ../../base

images:
  - name: ghcr.io/org/plateforme
    newTag: "a1b2c3d"

replicas:
  - name: api
    count: 3

patches:
  - path: ressources.yaml""", "yaml", "Une surcouche de production"),
        table(["Contrôle", "Commande", "Attendu"],
              [["Synchronisation", "`argocd app get`", "`Synced`"],
               ["Santé", "`kubectl get pods`", "Tous prêts"],
               ["Dérive", "`argocd app diff`", "Vide"],
               ["Retour arrière", "`git revert` puis synchronisation", "Version précédente"]],
              widths=[4.0, 5.4, 4.4], first_col_bold=True,
              caption="Quatre contrôles"),

        h(2, "Jalon 5 — Secrets et sécurité"),
        p("Aucun secret ne figure dans un dépôt. Les valeurs sensibles viennent d'un "
          "coffre ou d'un fichier chiffré, et les droits sont nominatifs."),
        code("""# Vérifications avant remise
gitleaks detect --source . --verbose        # aucun secret
kubectl get secret -n production            # secrets gérés
trivy image --severity CRITICAL ghcr.io/... # aucune faille critique
kubectl get networkpolicy -n production     # trafic restreint""", "bash",
             "Quatre contrôles de sécurité"),
        table(["Risque", "Attendu", "Non conforme"],
              [["Secret en clair", "Aucun", "Une clé dans un YAML"],
               ["Image non signée", "Refusée au déploiement", "Déploiement accepté"],
               ["Conteneur privilégié", "Interdit", "`privileged: true`"],
               ["Trafic libre", "Politiques réseau", "Aucune politique"]],
              widths=[4.4, 4.6, 4.8], first_col_bold=True,
              caption="Quatre exigences de sécurité"),

        h(2, "Jalon 6 — Observabilité et exploitation"),
        p("Le système expose ses métriques, écrit des journaux structurés et propage un "
          "identifiant de trace. Un tableau de bord couvre les quatre signaux d'or."),
        table(["Signal d'or", "Mesure", "Seuil d'alerte"],
              [["Latence", "p95 par route", "> 800 ms pendant 10 min"],
               ["Trafic", "Requêtes par seconde", "Variation > 50 %"],
               ["Erreurs", "Taux 5xx", "> 2 % pendant 5 min"],
               ["Saturation", "CPU et connexions", "> 85 % pendant 15 min"]],
              widths=[3.8, 5.0, 5.0], first_col_bold=True,
              caption="Quatre signaux d'or"),
        code("""# docs/runbook.md
## Service indisponible

1. `argocd app get plateforme-production` → état de synchronisation
2. `kubectl get pods -n production` → pods en échec ?
3. `kubectl describe pod <nom>` → événements
4. `kubectl logs <nom> --previous` → journaux de l'instance précédente
5. Vérifier le certificat : `openssl s_client -connect ... | openssl x509 -noout -dates`
6. Si la version précédente fonctionnait : `git revert` et synchroniser
7. Consigner la chronologie dans `docs/incidents/`""", "markdown",
             "Un runbook utilisable"),
        box("methode", "Critères de réussite",
            items=["Le dépôt reconstruit le système sans étape manuelle.",
                   "Le pipeline est vert et l'artefact est signé.",
                   "Le déploiement converge depuis Git.",
                   "Aucun secret en clair.",
                   "Les quatre signaux d'or sont visibles.",
                   "Un retour arrière a été exécuté et chronométré."]),
    ],
    "keypoints": [
        "Le projet se juge sur le système livré, pas sur le code seul.",
        "Trois dossiers séparent application, infrastructure et déploiement.",
        "L'image se construit en plusieurs étapes et s'exécute sans privilèges.",
        "Le pipeline publie un artefact signé, il ne déploie pas directement.",
        "L'état Terraform est distant et verrouillé.",
        "Le déploiement converge depuis Git.",
        "Les quatre signaux d'or structurent la supervision.",
        "Un runbook et un retour arrière chronométré font partie du livrable.",
    ],
    "bridge": "Le cours se termine ici. Les annexes rassemblent les aides "
              "méthodologiques : glossaire, aide-mémoire et grille d'auto-évaluation.",
    "exercises": [
        ex("Jalon 1 — Construire et tester",
           "L'application doit se construire et se tester sans intervention.",
           ["Écrivez le Dockerfile.",
            "Exécutez les tests.",
            "Vérifiez l'utilisateur."],
           [("bash", """docker build -t app:local .
docker run --rm app:local npm test
docker run --rm --user 1000 app:local id
# attendu : uid=1000, pas root

docker images app:local
# attendu : moins de 200 Mo"""),
            "L'image finale ne contient que les dépendances de production.",
            "Un conteneur qui tourne en root est un défaut de sécurité, même en "
            "développement."]),
        ex("Jalon 4 — Déployer et revenir",
           "Une version doit être déployée puis remplacée.",
           ["Déployez la version A.",
            "Déployez la version B.",
            "Revenez à A et chronométrez."],
           [("bash", """# Version A
# kustomization.yaml → newTag: "a1b2c3d"
git commit -am "production: 1.4.1"
git push && argocd app sync plateforme-production

# Version B
# kustomization.yaml → newTag: "b2c3d4e"
git commit -am "production: 1.4.2"
git push && argocd app sync plateforme-production

# Retour arrière
git revert --no-edit HEAD && git push
argocd app sync plateforme-production
time kubectl rollout status deployment/api -n production"""),
            "Le retour arrière par Git reste convergent : aucune modification manuelle.",
            "Le temps mesuré doit être inférieur à cinq minutes, synchronisation "
            "comprise."],
           level="Projet"),
        ex("Jalon 6 — Simuler un incident",
           "Provoquez une panne et documentez la réponse.",
           ["Coupez un pod.",
            "Suivez l'alerte.",
            "Rédigez l'analyse."],
           [("markdown", """## Simulation
- Action : suppression d'un pod de l'API
- Détection : alerte de disponibilité en 40 s
- Impact : aucune erreur visible (3 réplicas)
- Résolution : recréation automatique en 25 s

## Enseignements
- Le readiness probe évite d'envoyer du trafic trop tôt
- L'alerte aurait dû préciser le nombre de réplicas disponibles
- Action : ajouter l'alerte « réplicas disponibles < 2 »"""),
            "Une panne sans impact reste instructive : elle révèle les marges réelles.",
            "L'analyse doit citer les délais mesurés, pas des impressions."],
           level="Incident"),
    ],
    "quiz": [
        quiz("Que doit permettre le dépôt seul ?",
             ["Compiler le code", "Reconstruire le système",
              "Remplacer Kubernetes", "Générer la documentation"],
             1,
             "La reproductibilité complète est le critère central."),
        quiz("Pourquoi séparer application, infrastructure et déploiement ?",
             ["Pour la mode", "Pour éviter les effets de bord entre changements",
              "Pour réduire les coûts", "Pour la sécurité"],
             1,
             "Un changement de code ne doit pas modifier l'infrastructure."),
        quiz("Que doit faire le pipeline vis-à-vis du déploiement ?",
             ["Déployer directement", "Publier un artefact signé",
              "Modifier le cluster", "Redémarrer les pods"],
             1,
             "Le déploiement passe par Git et l'agent de réconciliation."),
        quiz("Que mesure le retour arrière ?",
             ["La taille de l'image", "Le temps de restauration",
              "Le nombre de commits", "La couverture de tests"],
             1,
             "C'est un objectif mesurable du projet."),
        quiz("Quel signal d'or est lié aux ressources ?",
             ["Latence", "Trafic", "Erreurs", "Saturation"],
             3,
             "La saturation décrit l'utilisation des ressources."),
    ],
}
