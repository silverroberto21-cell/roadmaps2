from bookkit.dsl import (box, code, defn, ex, fig, h, ol, p, quiz, table, ul)

CH = {
    "title": "Helm et service mesh",
    "subtitle": "Paramétrer des déploiements complexes et ajouter une couche de "
                "communication entre services.",
    "duration": "3 h 15",
    "level": "Avancé",
    "prereq": "chapitre 63",
    "objectives": [
        "Structurer un chart Helm lisible.",
        "Paramétrer sans multiplier les fichiers de valeurs.",
        "Gérer les versions et les retours arrière.",
        "Situer le service mesh et ses cas d'usage réels.",
        "Éviter la complexité prématurée.",
    ],
    "blocks": [
        h(2, "Pourquoi un gestionnaire de paquets"),
        p("Une application Kubernetes se compose d'un déploiement, d'un service, d'un "
          "ingress, d'une configuration et parfois de tâches planifiées. Helm regroupe "
          "ces objets en un paquet versionné et paramétrable."),
        table(["Élément Helm", "Rôle", "Équivalent"],
              [["Chart", "Paquet d'objets", "Un dossier"],
               ["`values.yaml`", "Valeurs par défaut", "Configuration"],
               ["Template", "Objet paramétré", "Manifeste avec variables"],
               ["Release", "Instance installée", "Un déploiement nommé"],
               ["Dépôt", "Catalogue de charts", "Registre"]],
              widths=[3.6, 4.8, 4.6], first_col_bold=True,
              caption="Cinq notions Helm"),
        code("""mon-service/
├── Chart.yaml
├── values.yaml
├── values.production.yaml
└── templates/
    ├── deployment.yaml
    ├── service.yaml
    ├── ingress.yaml
    ├── configmap.yaml
    ├── _helpers.tpl
    └── NOTES.txt""", "text", "Une arborescence de chart"),
        code("""# Chart.yaml
apiVersion: v2
name: mon-service
description: API de démonstration
type: application
version: 1.4.2
appVersion: "1.4.2"
dependencies:
  - name: postgresql
    version: 15.5.x
    repository: https://charts.bitnami.com/bitnami
    condition: postgresql.enabled""", "yaml", "Un descripteur de chart"),

        h(2, "Paramétrer"),
        p("Un chart utile expose peu de valeurs, avec des défauts sûrs. Multiplier les "
          "paramètres rend le chart impossible à maintenir ; en figer trop le rend "
          "inutilisable."),
        code("""# values.yaml
replicaCount: 2

image:
  repository: registry.exemple.fr/equipe/app
  tag: "1.4.2"
  pullPolicy: IfNotPresent

resources:
  requests:
    cpu: 100m
    memory: 128Mi
  limits:
    cpu: 500m
    memory: 256Mi

ingress:
  enabled: true
  className: nginx
  host: api.exemple.fr
  tls: true

config:
  logLevel: info
  cacheTtl: 300

postgresql:
  enabled: true
  auth:
    database: app""", "yaml", "Des valeurs lisibles"),
        code("""# templates/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "mon-service.fullname" . }}
  labels:
    {{- include "mon-service.labels" . | nindent 4 }}
spec:
  replicas: {{ .Values.replicaCount }}
  selector:
    matchLabels:
      {{- include "mon-service.selectorLabels" . | nindent 6 }}
  template:
    metadata:
      labels:
        {{- include "mon-service.selectorLabels" . | nindent 8 }}
    spec:
      containers:
        - name: {{ .Chart.Name }}
          image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}"
          ports:
            - containerPort: 3000
          resources:
            {{- toYaml .Values.resources | nindent 12 }}""", "yaml",
             "Un template paramétré"),
        box("attention", "Ne dupliquez pas la logique dans les templates",
            "Les fonctions `include` et `_helpers.tpl` centralisent les noms, les "
            "étiquettes et les annotations. Un chart où chaque fichier recalcule le nom "
            "complet devient incohérent au premier renommage."),
        code("""# _helpers.tpl
{{- define "mon-service.fullname" -}}
{{- printf "%s-%s" .Release.Name .Chart.Name | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "mon-service.selectorLabels" -}}
app.kubernetes.io/name: {{ .Chart.Name }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end -}}""", "yaml", "Deux helpers"),

        h(2, "Installer, mettre à jour, revenir"),
        p("Helm conserve l'historique des releases. Une mise à jour ratée se corrige par "
          "un retour arrière en une commande, ce qui est un argument décisif en "
          "production."),
        code("""# Vérifier avant d'installer
helm lint mon-service/
helm template mon-service ./mon-service -f values.production.yaml | less

# Installer et mettre à jour
helm install api ./mon-service -n production -f values.production.yaml
helm upgrade api ./mon-service -n production -f values.production.yaml --atomic --timeout 5m

# Observer et revenir
helm list -n production
helm history api -n production
helm rollback api 3 -n production
helm uninstall api -n production""", "bash", "Neuf commandes"),
        table(["Option", "Effet", "Usage"],
              [["`--atomic`", "Annule en cas d'échec", "Production"],
               ["`--timeout`", "Délai maximal", "Toujours préciser"],
               ["`--wait`", "Attend que tout soit prêt", "Avec `--atomic`"],
               ["`--dry-run`", "Simule", "Avant une mise à jour"],
               ["`--reuse-values`", "Conserve les valeurs", "Attention aux dérives"]],
              widths=[4.2, 4.8, 4.0], first_col_bold=True,
              caption="Cinq options de mise à jour"),
        code("""# Vérifier l'écart entre l'état installé et le chart
helm diff upgrade api ./mon-service -n production -f values.production.yaml

# Inspecter les valeurs réellement appliquées
helm get values api -n production -a""", "bash", "Deux vérifications"),
        defn("Release", "Instance nommée d'un chart installée dans un namespace. Deux "
                        "releases du même chart peuvent coexister avec des valeurs "
                        "différentes."),

        h(2, "Service mesh"),
        p("Un service mesh ajoute un proxy à côté de chaque pod. Il décharge "
          "l'application de la gestion du trafic, du chiffrement entre services et de la "
          "traçabilité."),
        fig("flow", "Un maillage de services",
            ["Pod A + proxy latéral",
             "Pod B + proxy latéral",
             "Plan de contrôle : configuration",
             "Chiffrement mutuel automatique",
             "Routage fin, réessais, délais",
             "Métriques et traces par requête"],
            height=255),
        table(["Fonction", "Sans mesh", "Avec mesh"],
              [["Chiffrement inter-services", "Par application", "Automatique"],
               ["Réessais et délais", "Dans le code", "Déclaratif"],
               ["Trafic progressif", "Manuel ou ingress", "Piloté par politique"],
               ["Traçabilité", "Instrumentation", "Intégrée"],
               ["Coût", "Aucun", "Latence, mémoire, complexité"]],
              widths=[4.4, 4.4, 4.4], first_col_bold=True,
              caption="Cinq fonctions et leur coût"),
        code("""# Exemple Istio : répartition du trafic entre versions
apiVersion: networking.istio.io/v1
kind: VirtualService
metadata:
  name: api
spec:
  hosts: ["api"]
  http:
    - route:
        - destination:
            host: api
            subset: v1
          weight: 90
        - destination:
            host: api
            subset: v2
          weight: 10""", "yaml", "Une répartition 90/10"),
        code("""# Vérifier le maillage d'un pod
kubectl get pod api-xxxx -o jsonpath='{.spec.containers[*].name}'
# api  istio-proxy

# Métriques et configuration
istioctl analyze -n production
istioctl proxy-status""", "bash", "Trois vérifications"),

        h(2, "Faut-il un mesh ?"),
        p("Un service mesh résout des problèmes réels, mais il ajoute un composant "
          "critique à exploiter. Trois questions permettent de décider."),
        table(["Question", "Oui", "Non"],
              [["Plus de dix services avec du trafic croisé ?", "Envisageable", "Inutile"],
               ["Besoin de chiffrement inter-services ?", "Argument fort", "TLS d'ingress suffit"],
               ["Équipe capable d'exploiter un control plane ?", "Envisageable", "À reporter"],
               ["Besoin de tests de panne et de trafic progressif ?", "Argument fort", "Ingress suffit"]],
              widths=[6.6, 3.4, 3.4], first_col_bold=True,
              caption="Quatre questions de décision"),
        box("pratique", "Commencer sans mesh",
            "Un ingress, des sondes, des journaux structurés et des métriques couvrent "
            "l'essentiel des besoins d'une équipe de taille moyenne. Le mesh s'ajoute "
            "quand le problème est identifié, pas avant."),
        defn("Proxy latéral", "Conteneur ajouté automatiquement dans chaque pod, qui "
                              "intercepte le trafic réseau. Il applique la politique du "
                              "plan de contrôle sans modifier le code applicatif."),
        box("methode", "Adopter Helm progressivement",
            items=["Un chart par application, pas un chart par équipe.",
                   "Valeurs par environnement séparées et versionnées.",
                   "`helm lint` et `helm template` dans la CI.",
                   "`--atomic` en production.",
                   "Un retour arrière testé avant d'en avoir besoin."]),
    ],
    "keypoints": [
        "Helm regroupe des objets Kubernetes en un paquet paramétrable.",
        "Un chart expose peu de valeurs, avec des défauts sûrs.",
        "Les helpers évitent la duplication dans les templates.",
        "Une release est une instance nommée d'un chart.",
        "`--atomic` annule une mise à jour échouée.",
        "Le service mesh automatise chiffrement, routage et traçabilité.",
        "Il ajoute un composant critique et de la latence.",
        "Le mesh s'adopte quand le problème est identifié.",
    ],
    "bridge": "Le cluster est outillé. La partie suivante traite du cloud, du "
              "provisionnement et de la configuration.",
    "exercises": [
        ex("Écrire un chart minimal",
           "Le service doit être déployable avec trois valeurs.",
           ["Créez `Chart.yaml` et `values.yaml`.",
            "Écrivez le déploiement et le service.",
            "Vérifiez le rendu."],
           [("yaml", """# values.yaml
replicaCount: 2
image:
  repository: registry.exemple.fr/equipe/app
  tag: "1.4.2"
service:
  port: 80
  targetPort: 3000

# Vérification
helm lint mon-service
helm template mon-service ./mon-service | grep -A3 "kind: Deployment"
helm install api ./mon-service --dry-run --debug | head -40"""),
            "`helm template` produit le YAML final sans rien installer : c'est l'outil de "
            "vérification principal.",
            "Un chart trop paramétrable devient un langage à lui seul : trois valeurs "
            "suffisent pour démarrer."]),
        ex("Revenir à une version précédente",
           "Une mise à jour a introduit une régression.",
           ["Identifiez la révision.",
            "Revenez en arrière.",
            "Vérifiez l'état."],
           [("bash", """helm history api -n production
# REVISION  STATUS     CHART             DESCRIPTION
# 3         deployed   mon-service-1.4.2 upgrade
# 2         superseded mon-service-1.4.1 upgrade

helm rollback api 2 -n production --wait
helm status api -n production
kubectl rollout status deployment/api -n production"""),
            "Le retour arrière Helm restaure les manifestes de la révision précédente.",
            "`--wait` évite de considérer le retour terminé avant que les pods soient "
            "prêts."]),
        ex("Décider d'un service mesh",
           "Une équipe de six personnes exploite huit services.",
           ["Listez les besoins réels.",
            "Estimez le coût.",
            "Proposez une décision argumentée."],
           ["Besoins : chiffrement interne, traçabilité, tests de panne.",
            "Coût : un plan de contrôle, des proxys par pod, une courbe "
            "d'apprentissage.",
            "Décision : commencer par un ingress et des métriques ; envisager le mesh "
            "quand les tests de panne deviennent réguliers."],
           level="Architecture"),
    ],
    "quiz": [
        quiz("Quel fichier contient les valeurs par défaut d'un chart ?",
             ["`Chart.yaml`", "`values.yaml`", "`NOTES.txt`", "`_helpers.tpl`"],
             1,
             "`values.yaml` porte les défauts, surchargés à l'installation."),
        quiz("Que fait `--atomic` ?",
             ["Installe plus vite", "Annule la mise à jour si elle échoue",
              "Supprime le chart", "Garde les valeurs"],
             1,
             "Helm revient à la révision précédente en cas d'échec."),
        quiz("Qu'ajoute un service mesh ?",
             ["Un proxy par pod", "Une base de données", "Un ingress", "Un registre"],
             0,
             "Le proxy latéral intercepte et applique les politiques."),
        quiz("Quand adopter un service mesh ?",
             ["Dès le premier service", "Quand un besoin identifié le justifie",
              "Jamais", "Après Kubernetes uniquement"],
             1,
             "Il ajoute de la complexité : il se justifie par un problème réel."),
        quiz("Quelle commande vérifie le rendu d'un chart ?",
             ["`helm install`", "`helm template`", "`helm list`", "`helm rollback`"],
             1,
             "`helm template` produit le YAML final sans installer."),
    ],
}
