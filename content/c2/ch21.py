from bookkit.dsl import (box, code, defn, ex, fig, h, ol, p, quiz, table, ul)

CH = {
    "title": "Kubernetes : modèle et objets fondamentaux",
    "subtitle": "Comprendre la boucle de contrôle qui maintient un état désiré, avant "
                "d'apprendre des commandes.",
    "duration": "3 h 15",
    "level": "Intermédiaire",
    "prereq": "chapitre 60",
    "objectives": [
        "Décrire l'architecture d'un cluster.",
        "Écrire un manifeste déclaratif.",
        "Utiliser `Pod`, `ReplicaSet` et `Deployment` à bon escient.",
        "Lire un état de pod (`Pending`, `CrashLoopBackOff`).",
        "Diagnostiquer un déploiement qui ne progresse pas.",
    ],
    "blocks": [
        h(2, "Un état désiré, pas des commandes"),
        p("Kubernetes ne reçoit pas d'ordres de démarrage : il reçoit une description de "
          "l'état souhaité. Des contrôleurs comparent en boucle l'état réel à cet état et "
          "agissent pour réduire l'écart."),
        fig("flow", "La boucle de réconciliation",
            ["Manifeste appliqué",
             "État désiré stocké dans etcd",
             "Contrôleur : compare réel et désiré",
             "Action : créer, supprimer, remplacer",
             "État observé mis à jour",
             "Nouvelle comparaison, en continu"],
            height=255),
        table(["Composant", "Rôle", "Où"],
              [["`kube-apiserver`", "Point d'entrée de l'API", "Control plane"],
               ["`etcd`", "Stockage de l'état", "Control plane"],
               ["`kube-scheduler`", "Placement des pods", "Control plane"],
               ["`controller-manager`", "Boucles de contrôle", "Control plane"],
               ["`kubelet`", "Exécution sur le nœud", "Chaque nœud"],
               ["`kube-proxy`", "Réseau des services", "Chaque nœud"],
               ["Runtime", "Conteneurs (containerd)", "Chaque nœud"]],
              widths=[4.0, 5.2, 3.6], first_col_bold=True,
              caption="Sept composants"),
        defn("Réconciliation", "Processus continu qui compare l'état observé à l'état "
                               "désiré et corrige l'écart. C'est ce qui rend Kubernetes "
                               "auto-réparateur : un pod supprimé est recréé."),

        h(2, "Le vocabulaire minimal"),
        p("Quatre objets suffisent pour démarrer. Chacun a une responsabilité précise, et "
          "les confondre conduit à des manifestes inutilement compliqués."),
        table(["Objet", "Rôle", "Durée de vie"],
              [["`Pod`", "Un ou plusieurs conteneurs colocalisés", "Éphémère"],
               ["`ReplicaSet`", "Maintient N copies d'un pod", "Permanent"],
               ["`Deployment`", "Gère les versions et les montées progressives", "Permanent"],
               ["`Service`", "Adresse stable devant des pods", "Permanent"],
               ["`ConfigMap` / `Secret`", "Configuration externe", "Permanent"],
               ["`Namespace`", "Cloisonnement logique", "Permanent"]],
              widths=[4.4, 5.6, 3.0], first_col_bold=True,
              caption="Six objets essentiels"),
        code("""apiVersion: apps/v1
kind: Deployment
metadata:
  name: api
  namespace: production
  labels:
    app: api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: api
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  template:
    metadata:
      labels:
        app: api
    spec:
      containers:
        - name: api
          image: registry.exemple.fr/equipe/app:1.4.2
          ports:
            - containerPort: 3000
          envFrom:
            - configMapRef:
                name: api-config
          resources:
            requests:
              cpu: 100m
              memory: 128Mi
            limits:
              cpu: 500m
              memory: 256Mi
          readinessProbe:
            httpGet:
              path: /ready
              port: 3000
            periodSeconds: 5
          livenessProbe:
            httpGet:
              path: /health
              port: 3000
            initialDelaySeconds: 10
            periodSeconds: 20""", "yaml", "Un déploiement complet"),
        box("attention", "Ne créez pas de pods seuls",
            "Un `Pod` créé directement n'est pas surveillé : s'il meurt, rien ne le "
            "recrée. Utilisez un `Deployment`, qui gère un `ReplicaSet`, qui gère les "
            "pods. Les pods directs servent au diagnostic."),

        h(2, "Requêtes et limites"),
        p("Les ressources se déclarent en deux valeurs : la requête détermine le placement, "
          "la limite provoque un étranglement ou un arrêt. Les confondre produit des "
          "clusters instables."),
        table(["Champ", "Effet sur le placement", "Effet à l'exécution"],
              [["`requests.cpu`", "Réservation", "Garantie minimale"],
               ["`limits.cpu`", "Aucun", "Étranglement (throttling)"],
               ["`requests.memory`", "Réservation", "Aucun"],
               ["`limits.memory`", "Aucun", "`OOMKilled` si dépassement"]],
              widths=[4.4, 4.6, 4.6], first_col_bold=True,
              caption="Quatre champs et leurs effets"),
        code("""# Vérifier la consommation réelle
kubectl top pods -n production
kubectl describe pod -n production -l app=api | grep -A3 "Limits"

# Un pod tué pour mémoire
kubectl get pod -n production -l app=api \\
  -o jsonpath='{range .items[*]}{.metadata.name}{" "}{.status.containerStatuses[*].lastState.terminated.reason}{"\\n"}{end}'""",
             "bash", "Deux vérifications"),
        p("Une requête trop élevée rend un pod impossible à placer (`Pending`). Une "
          "limite trop basse provoque des redémarrages en boucle. Les valeurs se "
          "mesurent, elles ne se devinent pas."),

        h(2, "Sondes"),
        p("Trois sondes répondent à trois questions différentes. Les confondre est l'une "
          "des erreurs les plus coûteuses en production."),
        table(["Sonde", "Question", "Conséquence d'un échec"],
              [["`livenessProbe`", "Le processus est-il vivant ?", "Redémarrage du conteneur"],
               ["`readinessProbe`", "Peut-il recevoir du trafic ?", "Retiré du service"],
               ["`startupProbe`", "Le démarrage est-il terminé ?", "Désactive les autres"]],
              widths=[3.8, 5.0, 4.8], first_col_bold=True,
              caption="Trois sondes"),
        code("""# Startup : laisser le temps à une application lente
startupProbe:
  httpGet: { path: /health, port: 3000 }
  failureThreshold: 30
  periodSeconds: 2

# Readiness : dépendances secondaires incluses
readinessProbe:
  httpGet: { path: /ready, port: 3000 }
  periodSeconds: 5

# Liveness : le processus seul, jamais les dépendances
livenessProbe:
  httpGet: { path: /health, port: 3000 }
  periodSeconds: 20""", "yaml", "Trois sondes bien réglées"),
        box("attention", "Une liveness qui teste la base redémarre tout",
            "Si la liveness interroge la base de données, une panne de base provoque le "
            "redémarrage de tous les pods applicatifs. La liveness teste le processus ; "
            "la readiness teste la capacité à servir."),

        h(2, "Appliquer et observer"),
        p("`kubectl apply` envoie un manifeste, `kubectl diff` montre l'écart, et "
          "`kubectl rollout` suit le déploiement. Ces trois commandes forment le socle "
          "du travail quotidien."),
        code("""kubectl apply -f deployment.yaml
kubectl diff -f deployment.yaml
kubectl get pods -n production -w
kubectl describe pod api-7d9f8c6b5-x2k4m -n production
kubectl logs -n production -l app=api --tail=50
kubectl rollout status deployment/api -n production
kubectl rollout history deployment/api -n production
kubectl rollout undo deployment/api -n production""", "bash",
             "Huit commandes de base"),
        table(["État du pod", "Signification", "Première vérification"],
              [["`Pending`", "Non planifié", "`describe`, ressources et contraintes"],
               ["`ContainerCreating`", "Image ou volume", "`describe`, événements"],
               ["`ImagePullBackOff`", "Image inaccessible", "Nom, registre, secret"],
               ["`CrashLoopBackOff`", "Le conteneur meurt", "`logs --previous`"],
               ["`Running` non prêt", "Sonde readiness", "`describe`, `exec`"],
               ["`Terminating` bloqué", "Finaliseur", "`describe`"]],
              widths=[4.2, 4.4, 5.0], first_col_bold=True,
              caption="Six états et leur piste"),

        h(2, "Diagnostiquer"),
        p("Un déploiement bloqué se diagnostique dans un ordre précis : événements, état "
          "des pods, journaux, puis ressources du nœud."),
        code("""kubectl get events -n production --sort-by=.lastTimestamp | tail -20
kubectl describe deployment api -n production
kubectl get pods -n production -o wide
kubectl logs api-7d9f8c6b5-x2k4m -n production --previous
kubectl describe node $(kubectl get pods -n production -o wide | awk 'NR==2{print $7}')
kubectl top nodes""", "bash", "Six commandes ordonnées"),
        box("methode", "Diagnostic d'un déploiement bloqué",
            items=["`get pods` : quel est l'état exact ?",
                   "`describe` : quels événements récents ?",
                   "`logs --previous` : que dit le conteneur mort ?",
                   "Ressources : le pod tient-il dans un nœud ?",
                   "Sondes : sont-elles trop strictes ou trop précoces ?"]),
    ],
    "keypoints": [
        "Kubernetes réconcilie en continu l'état réel et l'état désiré.",
        "Un pod est éphémère ; un Deployment gère les pods.",
        "Les requêtes déterminent le placement, les limites l'exécution.",
        "Une requête trop élevée produit un pod `Pending`.",
        "La liveness redémarre, la readiness retire du trafic.",
        "Une liveness qui teste une dépendance provoque des redémarrages en cascade.",
        "`CrashLoopBackOff` se diagnostique avec `logs --previous`.",
        "`rollout undo` revient à la version précédente.",
    ],
    "bridge": "Les pods tournent. Le chapitre suivant les expose et les configure : "
              "services, entrées et configuration.",
    "exercises": [
        ex("Écrire un déploiement complet",
           "Le service doit tourner en trois exemplaires avec des sondes.",
           ["Déclarez les ressources.",
            "Ajoutez readiness et liveness.",
            "Vérifiez le déploiement."],
           [("yaml", """apiVersion: apps/v1
kind: Deployment
metadata: { name: web, namespace: production }
spec:
  replicas: 3
  selector: { matchLabels: { app: web } }
  template:
    metadata: { labels: { app: web } }
    spec:
      containers:
        - name: web
          image: registry.exemple.fr/equipe/web:1.4.2
          ports: [{ containerPort: 8080 }]
          resources:
            requests: { cpu: 100m, memory: 128Mi }
            limits:   { cpu: 500m, memory: 256Mi }
          readinessProbe:
            httpGet: { path: /, port: 8080 }
            periodSeconds: 5
          livenessProbe:
            httpGet: { path: /healthz, port: 8080 }
            initialDelaySeconds: 10
            periodSeconds: 20"""),
            "`maxUnavailable: 0` garantit que le service reste disponible pendant la "
            "montée de version.",
            "Des sondes distinctes évitent qu'un incident de dépendance déclenche des "
            "redémarrages."]),
        ex("Diagnostiquer un CrashLoopBackOff",
           "Un pod redémarre toutes les trente secondes.",
           ["Lisez les journaux du conteneur mort.",
            "Vérifiez la configuration.",
            "Testez l'image localement."],
           [("bash", """kubectl get pod api-xxxx -n production
kubectl describe pod api-xxxx -n production | tail -30
kubectl logs api-xxxx -n production --previous

# Vérifier la configuration montée
kubectl exec -it api-xxxx -n production -- env | sort
kubectl get configmap api-config -n production -o yaml"""),
            "`--previous` est essentiel : les journaux du conteneur actuel sont souvent "
            "vides car il vient de redémarrer.",
            "Une variable absente ou une base injoignable provoque une sortie immédiate "
            "avec un message explicite."],
           level="Diagnostic"),
        ex("Corriger un pod Pending",
           "Le pod reste `Pending` après application.",
           ["Lisez les événements.",
            "Vérifiez les ressources demandées.",
            "Corrigez la contrainte."],
           [("bash", """kubectl describe pod web-xxxx -n production | grep -A10 Events

# Exemples de messages
# 0/3 nodes are available: 3 Insufficient memory.
# 0/3 nodes are available: 3 node(s) had untolerated taint.

kubectl describe nodes | grep -A5 "Allocated resources\""""),
            "Un `Pending` est presque toujours un problème de ressources, de sélecteur de "
            "nœud ou de tolérance.",
            "Les événements du pod indiquent la contrainte exacte qui empêche le "
            "placement."],
           level="Diagnostic"),
    ],
    "quiz": [
        quiz("Que fait Kubernetes quand un pod d'un Deployment meurt ?",
             ["Rien", "Il le recrée", "Il redémarre le nœud", "Il alerte seulement"],
             1,
             "Le contrôleur compare le nombre de réplicas et recrée le pod manquant."),
        quiz("Quel effet a `limits.cpu` ?",
             ["Redémarre le conteneur", "Étrangle le processeur disponible",
              "Réserve un cœur", "Augmente la priorité"],
             1,
             "Le conteneur est ralenti, jamais tué, pour une limite CPU."),
        quiz("Que fait une readiness en échec ?",
             ["Redémarre le conteneur", "Retire le pod du service",
              "Supprime le pod", "Augmente les réplicas"],
             1,
             "Le pod reste vivant mais ne reçoit plus de trafic."),
        quiz("Que signifie `CrashLoopBackOff` ?",
             ["Le pod attend un nœud", "Le conteneur redémarre en boucle",
              "L'image est absente", "La sonde est trop lente"],
             1,
             "Le conteneur se termine immédiatement après chaque démarrage."),
        quiz("Quelle commande annule un déploiement ?",
             ["`kubectl delete pod`", "`kubectl rollout undo`", "`kubectl scale 0`", "`kubectl apply`"],
             1,
             "`rollout undo` revient à la révision précédente."),
    ],
}
