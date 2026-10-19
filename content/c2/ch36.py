from bookkit.dsl import (box, code, defn, ex, fig, h, ol, p, quiz, table, ul)

CH = {
    "title": "GitOps : le dépôt comme source de vérité",
    "subtitle": "Faire converger un cluster vers l'état décrit dans Git, sans accès "
                "direct ni dérive silencieuse.",
    "duration": "3 h 00",
    "level": "Avancé",
    "prereq": "chapitre 75",
    "objectives": [
        "Expliquer les quatre principes du GitOps.",
        "Décrire le fonctionnement d'Argo CD et de Flux.",
        "Organiser un dépôt de déploiement.",
        "Gérer les environnements et la promotion.",
        "Traiter une dérive et un retour arrière.",
    ],
    "blocks": [
        h(2, "Quatre principes"),
        p("Le GitOps applique les principes du contrôle de version à l'exploitation : "
          "l'état désiré vit dans Git, un agent compare en continu le cluster à cet état, "
          "et toute modification passe par une demande de fusion."),
        fig("flow", "La boucle GitOps",
            ["Modification dans Git (demande de fusion)",
             "Revue et fusion",
             "Agent : lecture du dépôt",
             "Comparaison avec l'état du cluster",
             "Application de l'écart",
             "Rapport de synchronisation"],
            height=255),
        table(["Principe", "Conséquence", "Sans lui"],
              [["Déclaratif", "L'état est décrit", "Scripts impératifs fragiles"],
               ["Versionné", "Historique et retour arrière", "Aucune trace"],
               ["Tiré automatiquement", "Convergence continue", "Dérive possible"],
               ["Réconcilié en continu", "Correction des écarts", "Configuration qui pourrit"]],
              widths=[4.0, 4.6, 4.6], first_col_bold=True,
              caption="Quatre principes"),
        defn("Réconciliation", "Boucle qui compare l'état observé à l'état désiré et "
                               "applique les différences. Elle tourne en continu, sans "
                               "intervention humaine."),
        box("attention", "GitOps n'est pas « déployer depuis la CI »",
            "Un pipeline qui exécute `kubectl apply` à la fin reste du déploiement "
            "classique : si quelqu'un modifie le cluster à la main, rien ne le corrige. "
            "Le GitOps suppose un agent qui observe et répare."),

        h(2, "Argo CD"),
        p("Argo CD est un contrôleur installé dans le cluster. Il surveille des "
          "applications, chacune associée à un dépôt Git et à un chemin, puis affiche "
          "l'écart entre l'état désiré et l'état réel."),
        code("""apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: boutique-production
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/org/deploiement.git
    targetRevision: main
    path: environnements/production/boutique
  destination:
    server: https://kubernetes.default.svc
    namespace: boutique
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
      - CreateNamespace=true
      - ApplyOutOfSyncOnly=true
    retry:
      limit: 3
      backoff:
        duration: 10s
        factor: 2
        maxDuration: 3m""", "yaml", "Une application Argo CD"),
        table(["Réglage", "Effet", "Risque"],
              [["`prune: true`", "Supprime les ressources retirées de Git", "Suppression involontaire"],
               ["`selfHeal: true`", "Corrige les modifications manuelles", "Écrase un dépannage"],
               ["`ApplyOutOfSyncOnly`", "N'applique que les écarts", "Plus rapide"],
               ["`CreateNamespace`", "Crée l'espace de noms", "Droits élargis"],
               ["`retry`", "Réessaie en cas d'échec transitoire", "Boucle si l'erreur est permanente"]],
              widths=[4.6, 4.8, 3.8], first_col_bold=True,
              caption="Cinq réglages"),
        code("""# État des applications
argocd app list
argocd app get boutique-production

# Comparer sans appliquer
argocd app diff boutique-production

# Synchroniser manuellement
argocd app sync boutique-production --prune

# Revenir à une révision précédente
argocd app rollback boutique-production 12""", "bash", "Cinq commandes"),
        box("pratique", "`selfHeal` protège la convergence, pas le dépannage",
            "Pendant un incident, une correction manuelle urgente sera écrasée en quelques "
            "minutes. Si vous devez intervenir à la main, suspendez la synchronisation, "
            "consignez l'action, puis reportez la correction dans Git."),

        h(2, "Flux"),
        p("Flux fonctionne par ensembles de personnalisations (Kustomization) et sources "
          "Git. Il est plus modulaire et s'intègre naturellement à `kustomize` et Helm."),
        code("""apiVersion: source.toolkit.fluxcd.io/v1
kind: GitRepository
metadata:
  name: deploiement
  namespace: flux-system
spec:
  interval: 1m
  url: https://github.com/org/deploiement.git
  ref:
    branch: main
---
apiVersion: kustomize.toolkit.fluxcd.io/v1
kind: Kustomization
metadata:
  name: boutique-production
  namespace: flux-system
spec:
  interval: 5m
  path: ./environnements/production/boutique
  prune: true
  sourceRef:
    kind: GitRepository
    name: deploiement
  healthChecks:
    - apiVersion: apps/v1
      kind: Deployment
      name: boutique
      namespace: boutique""", "yaml", "Une synchronisation Flux"),
        table(["Aspect", "Argo CD", "Flux"],
              [["Interface", "Graphique riche", "Ligne de commande"],
               ["Modèle", "Application", "Sources et Kustomizations"],
               ["Multi-cluster", "Natif", "Par installation"],
               ["Intégration Helm", "Bonne", "Très bonne"],
               ["Courbe d'apprentissage", "Douce", "Plus abrupte"]],
              widths=[4.2, 4.4, 4.4], first_col_bold=True,
              caption="Cinq différences"),

        h(2, "Organiser le dépôt"),
        p("Le dépôt de déploiement est distinct du dépôt applicatif : il ne contient que "
          "des manifestes et des références d'images. Cette séparation évite qu'un "
          "changement de code déclenche un déploiement non relu."),
        code("""deploiement/
├── base/
│   └── boutique/
│       ├── deployment.yaml
│       ├── service.yaml
│       └── kustomization.yaml
├── environnements/
│   ├── recette/
│   │   └── boutique/
│   │       ├── kustomization.yaml   # image: 1.4.2
│   │       └── patch-replicas.yaml
│   └── production/
│       └── boutique/
│           ├── kustomization.yaml   # image: 1.4.1
│           └── patch-replicas.yaml
└── politiques/
    └── reseau.yaml""", "text", "Une structure de dépôt"),
        code("""# base/boutique/kustomization.yaml
resources:
  - deployment.yaml
  - service.yaml

# environnements/production/boutique/kustomization.yaml
resources:
  - ../../../base/boutique

images:
  - name: registry.exemple.fr/boutique
    newTag: "1.4.1"

replicas:
  - name: boutique
    count: 3

patches:
  - target:
      kind: Deployment
      name: boutique
    patch: |-
      - op: add
        path: /spec/template/spec/containers/0/resources
        value:
          requests: { cpu: 200m, memory: 256Mi }
          limits:   { cpu: "1",  memory: 512Mi }""", "yaml", "Une surcouche"),
        fig("flow", "Une promotion par demande de fusion",
            ["Image 1.4.2 publiée et signée",
             "Mise à jour de `recette/boutique` dans le dépôt",
             "Synchronisation automatique en recette",
             "Vérification fonctionnelle",
             "Demande de fusion vers `production`",
             "Synchronisation en production"],
            height=255),

        h(2, "Dérive et retour arrière"),
        p("La dérive est l'écart entre l'état réel et l'état déclaré. GitOps la détecte "
          "en continu ; l'important est de savoir si elle doit être corrigée ou intégrée."),
        table(["Type de dérive", "Origine", "Traitement"],
              [["Ressource modifiée à la main", "Intervention urgente", "Annuler ou intégrer"],
               ["Ressource ajoutée hors Git", "Script oublié", "Supprimer ou codifier"],
               ["Image mise à jour", "Déploiement manuel", "Écraser"],
               ["Secret modifié", "Rotation", "Externaliser le secret"]],
              widths=[5.0, 4.4, 4.6], first_col_bold=True,
              caption="Quatre dérives"),
        code("""# Retour arrière par Git : le seul moyen propre
git revert --no-edit 3f2a1c9
git push

# Ou revenir à une révision antérieure de l'application
argocd app rollback boutique-production 12

# Vérifier que l'état correspond à nouveau
argocd app get boutique-production --show-operation""", "bash",
             "Deux retours arrière"),
        box("attention", "`prune` supprime, y compris les volumes",
            "Une ressource retirée du dépôt est supprimée du cluster. Sur un "
            "`PersistentVolumeClaim`, cela peut signifier une perte de données. Protégez "
            "les ressources critiques par des annotations et une politique de rétention."),
        box("methode", "Adopter le GitOps",
            items=["Un dépôt de déploiement séparé du code applicatif.",
                   "Un agent installé et surveillé.",
                   "Des environnements représentés par des surcouches.",
                   "Une promotion par demande de fusion.",
                   "Une alerte sur l'état de synchronisation."]),
    ],
    "keypoints": [
        "Le GitOps suppose un agent qui réconcilie en continu.",
        "Le déclaratif, le versionnement, le tirage et la réconciliation forment le socle.",
        "Argo CD décrit des applications, Flux des sources et des personnalisations.",
        "`selfHeal` corrige les modifications manuelles.",
        "`prune` supprime les ressources retirées du dépôt.",
        "Le dépôt de déploiement est distinct du dépôt applicatif.",
        "Une promotion est une demande de fusion.",
        "Le retour arrière se fait par Git, pas par `kubectl`.",
    ],
    "bridge": "L'état converge. Reste à protéger ce qu'il contient : les secrets, puis "
              "à l'observer.",
    "exercises": [
        ex("Déclarer une application Argo CD",
           "Une application doit se synchroniser automatiquement.",
           ["Associez dépôt et chemin.",
            "Activez `prune` et `selfHeal`.",
            "Limitez les réessais."],
           [("yaml", """apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: boutique-production
  namespace: argocd
spec:
  source:
    repoURL: https://github.com/org/deploiement.git
    targetRevision: main
    path: environnements/production/boutique
  destination:
    server: https://kubernetes.default.svc
    namespace: boutique
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    retry:
      limit: 3
      backoff: { duration: 10s, factor: 2, maxDuration: 3m }"""),
            "`prune` et `selfHeal` donnent la convergence complète, avec les risques "
            "associés.",
            "Une limite de réessais évite de boucler indéfiniment sur une erreur de "
            "manifeste."]),
        ex("Gérer une dérive",
           "Un ingénieur a modifié le nombre de réplicas à la main.",
           ["Constatez l'écart.",
            "Décidez du traitement.",
            "Rétablissez la convergence."],
           [("bash", """# Constat
kubectl get deployment boutique -n production \\
  -o jsonpath='{.spec.replicas}'   # 5
grep -A2 replicas environnements/production/boutique/kustomization.yaml
# count: 3

# Décision : l'augmentation était temporaire
# Git est la source de vérité → laisser selfHeal corriger
argocd app diff boutique-production
argocd app sync boutique-production

# Si l'augmentation devait être permanente :
# modifier kustomization.yaml et fusionner"""),
            "La question n'est pas « qui a raison ? » mais « où est la source de vérité ? ».",
            "`selfHeal` corrige automatiquement en quelques minutes ; la synchronisation "
            "manuelle accélère."],
           level="Diagnostic"),
        ex("Préparer une promotion",
           "La version 1.4.2 doit passer de recette à production.",
           ["Vérifiez l'image.",
            "Modifiez la surcouche de production.",
            "Fusionnez après revue."],
           [("yaml", """# environnements/production/boutique/kustomization.yaml
images:
  - name: registry.exemple.fr/boutique
    newTag: "1.4.2"

# Vérification avant fusion
# cosign verify --key cosign.pub registry.exemple.fr/boutique:1.4.2
# argocd app diff boutique-production"""),
            "Une promotion est un changement de version dans un fichier, relu comme du "
            "code.",
            "La vérification de signature et le diff précèdent la fusion."],
           level="Architecture"),
    ],
    "quiz": [
        quiz("Quel principe distingue GitOps d'un simple déploiement ?",
             ["Le YAML", "La réconciliation continue", "Kubernetes", "Le dépôt"],
             1,
             "L'agent corrige les écarts en continu."),
        quiz("Que fait `selfHeal` dans Argo CD ?",
             ["Redémarre les pods", "Corrige les modifications manuelles",
              "Supprime les volumes", "Met à jour l'image"],
             1,
             "L'état déclaré reprend le dessus sur les modifications manuelles."),
        quiz("Que fait `prune` ?",
             ["Compresse les manifestes", "Supprime les ressources retirées de Git",
              "Réduit les réplicas", "Nettoie les journaux"],
             1,
             "C'est une suppression réelle, à utiliser avec précaution."),
        quiz("Où se décide une promotion GitOps ?",
             ["Dans `kubectl`", "Dans une demande de fusion",
              "Dans Argo CD", "Dans le registre"],
             1,
             "La promotion est un changement versionné et relu."),
        quiz("Comment revenir à une version précédente ?",
             ["`kubectl rollout undo` seul", "Un `git revert`",
              "Redémarrer les pods", "Supprimer le cluster"],
             1,
             "Le retour arrière passe par Git pour rester convergent."),
    ],
}
