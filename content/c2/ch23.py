from bookkit.dsl import (box, code, defn, ex, fig, h, ol, p, quiz, table, ul)

CH = {
    "title": "Stockage et applications à état",
    "subtitle": "Faire tourner une base de données dans un orchestrateur sans perdre ses "
                "données.",
    "duration": "3 h 00",
    "level": "Avancé",
    "prereq": "chapitre 62",
    "objectives": [
        "Distinguer stockage éphémère et persistant.",
        "Choisir entre `emptyDir`, `hostPath` et volume persistant.",
        "Comprendre `PersistentVolume` et `PersistentVolumeClaim`.",
        "Utiliser un `StatefulSet` à bon escient.",
        "Sauvegarder et restaurer des données de cluster.",
    ],
    "blocks": [
        h(2, "Un pod est remplaçable, une donnée ne l'est pas"),
        p("Par conception, un pod peut être supprimé à tout moment. Toute donnée écrite "
          "dans son système de fichiers disparaît avec lui. Le stockage persistant est "
          "donc un choix explicite, pas un détail d'implémentation."),
        table(["Type", "Durée de vie", "Partage", "Usage"],
              [["`emptyDir`", "Celle du pod", "Entre conteneurs du pod", "Cache, temporaires"],
               ["`hostPath`", "Celle du nœud", "Non", "Démon, cas particuliers"],
               ["`PersistentVolume`", "Indépendante", "Selon le mode", "Données applicatives"],
               ["Stockage objet", "Indépendante", "Oui", "Fichiers, sauvegardes"]],
              widths=[4.0, 3.6, 4.2, 4.2], first_col_bold=True,
              caption="Quatre types de stockage"),
        defn("Volume persistant", "Ressource de stockage provisionnée par un "
                                  "administrateur ou dynamiquement, indépendante du cycle "
                                  "de vie des pods."),
        code("""# emptyDir : partagé entre deux conteneurs du même pod
volumes:
  - name: cache
    emptyDir:
      sizeLimit: 500Mi
volumeMounts:
  - name: cache
    mountPath: /var/cache/app""", "yaml", "Un volume éphémère partagé"),

        h(2, "PV, PVC et classes de stockage"),
        p("Un `PersistentVolume` décrit un espace disponible ; un "
          "`PersistentVolumeClaim` en demande une partie. La liaison se fait selon la "
          "taille, le mode d'accès et la classe."),
        fig("flow", "Le cycle d'un volume persistant",
            ["StorageClass : provisionnement dynamique",
             "PVC : demande de 20 Gi en ReadWriteOnce",
             "Liaison à un PV",
             "Montage dans le pod",
             "Détachement à la suppression du pod",
             "Rétention selon `reclaimPolicy`"],
            height=255),
        code("""apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: pgdata
  namespace: production
spec:
  accessModes: ["ReadWriteOnce"]
  storageClassName: standard
  resources:
    requests:
      storage: 20Gi""", "yaml", "Une demande de volume"),
        table(["Mode d'accès", "Signification", "Usage"],
              [["`ReadWriteOnce`", "Un seul nœud en écriture", "Bases de données"],
               ["`ReadOnlyMany`", "Plusieurs nœuds en lecture", "Contenus partagés"],
               ["`ReadWriteMany`", "Plusieurs nœuds en écriture", "Systèmes de fichiers réseau"],
               ["`ReadWriteOncePod`", "Un seul pod", "Isolation stricte"]],
              widths=[4.2, 5.0, 4.4], first_col_bold=True,
              caption="Quatre modes d'accès"),
        code("""# Vérifier la liaison
kubectl get pvc -n production
# NAME     STATUS   VOLUME    CAPACITY   STORAGECLASS
# pgdata   Bound    pvc-...   20Gi       standard

kubectl describe pvc pgdata -n production | tail -10""", "bash",
             "Deux vérifications"),
        box("attention", "`reclaimPolicy` décide du sort des données",
            "Avec `Delete`, la suppression du PVC supprime le volume sous-jacent. Avec "
            "`Retain`, le volume survit mais doit être nettoyé manuellement. Vérifiez la "
            "politique de votre classe de stockage avant toute suppression."),

        h(2, "StatefulSet"),
        p("Un `Deployment` traite ses réplicas comme interchangeables. Un `StatefulSet` "
          "donne à chacune une identité stable : nom, réseau et volume propres."),
        table(["Aspect", "Deployment", "StatefulSet"],
              [["Identité des pods", "Aléatoire", "Ordonnée (`db-0`, `db-1`)"],
               ["Volumes", "Partagés ou absents", "Un par pod"],
               ["Ordre de démarrage", "Simultané", "Séquentiel"],
               ["Cas d'usage", "Sans état", "Bases, files, clusters"]],
              widths=[3.6, 5.0, 5.0], first_col_bold=True,
              caption="Quatre différences"),
        code("""apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: db
  namespace: production
spec:
  serviceName: db
  replicas: 3
  selector:
    matchLabels: { app: db }
  template:
    metadata:
      labels: { app: db }
    spec:
      containers:
        - name: postgres
          image: postgres:16
          volumeMounts:
            - name: data
              mountPath: /var/lib/postgresql/data
  volumeClaimTemplates:
    - metadata:
        name: data
      spec:
        accessModes: ["ReadWriteOnce"]
        storageClassName: standard
        resources:
          requests:
            storage: 20Gi""", "yaml", "Un StatefulSet de trois réplicas"),
        p("Chaque pod reçoit un PVC nommé `data-db-0`, `data-db-1`, `data-db-2`. "
          "Supprimer le StatefulSet ne supprime pas ces PVC : c'est une protection contre "
          "la perte accidentelle, mais aussi une source de coût si l'on oublie de "
          "nettoyer."),
        code("""# Un StatefulSet ne suffit pas à faire une base répliquée
# Il faut un mécanisme de réplication et d'élection :
# - opérateur PostgreSQL (CloudNativePG, Zalando)
# - opérateur MySQL (Vitess, Percona)
# - Redis avec Sentinel ou Cluster

kubectl get statefulset -n production
kubectl get pvc -n production -l app=db""", "bash",
             "Deux vérifications et une mise en garde"),

        h(2, "Sauvegarder"),
        p("Une réplication n'est pas une sauvegarde : une erreur logique se réplique "
          "instantanément. Une sauvegarde doit être externalisée et testée."),
        code("""# Sauvegarde logique d'une base PostgreSQL
kubectl exec -n production db-0 -- \\
  pg_dump -U app -Fc app > app-$(date +%F).dump

# Sauvegarde vers un stockage objet
kubectl exec -n production db-0 -- \\
  pg_dump -U app -Fc app | gzip | \\
  aws s3 cp - s3://sauvegardes/app/$(date +%F).dump.gz

# Restauration dans une base de test
createdb -h db-test -U app restauration
pg_restore -h db-test -U app -d restauration app-2026-10-19.dump""", "bash",
             "Trois opérations"),
        table(["Méthode", "Avantage", "Limite"],
              [["`pg_dump`", "Simple, portable", "Lent sur gros volumes"],
               ["Instantané de volume", "Rapide", "Dépend du fournisseur"],
               ["Archivage continu (WAL)", "Restauration à un instant", "Complexe à exploiter"],
               ["Réplique logique", "Migration à chaud", "Ne remplace pas la sauvegarde"]],
              widths=[4.6, 4.6, 4.4], first_col_bold=True,
              caption="Quatre méthodes de sauvegarde"),
        defn("Restauration à un instant", "Capacité à restaurer l'état de la base à une "
                                          "seconde précise, en rejouant les journaux "
                                          "d'écriture jusqu'à l'instant voulu. C'est le "
                                          "seul moyen de corriger une suppression "
                                          "accidentelle sans perdre les transactions "
                                          "ultérieures."),
        code("""# Vérifier l'âge de la dernière sauvegarde
aws s3 ls s3://sauvegardes/app/ | tail -5

# Une sauvegarde non testée n'existe pas
# Automatiser une restauration hebdomadaire dans un environnement jetable""",
             "bash", "Deux réflexes"),

        h(2, "Cas des applications à état"),
        p("Faire tourner une base dans Kubernetes est possible, et parfois souhaitable. "
          "Une décision éclairée pèse trois éléments : l'équipe, le volume et le besoin "
          "de portabilité."),
        table(["Situation", "Recommandation", "Raison"],
              [["Petite équipe, base critique", "Service managé", "Exploitation déléguée"],
               ["Contrainte réglementaire", "Auto-hébergé", "Contrôle des données"],
               ["Développement et tests", "Dans le cluster", "Simplicité"],
               ["Forte croissance", "Service managé", "Sauvegardes, réplicas, montée en charge"],
               ["Multi-cloud strict", "Opérateur", "Portabilité"]],
              widths=[5.0, 4.4, 4.2], first_col_bold=True,
              caption="Cinq situations et leur recommandation"),
        box("methode", "Check-list d'une application à état",
            items=["PVC dimensionné et classe de stockage documentée.",
                   "Politique de rétention vérifiée.",
                   "Sauvegarde externalisée et restaurée régulièrement.",
                   "Un seul écrivain par volume.",
                   "Sondes adaptées à la base, pas au conteneur générique."]),
    ],
    "keypoints": [
        "Le système de fichiers d'un pod disparaît avec lui.",
        "`emptyDir` vit aussi longtemps que le pod.",
        "Un PVC demande un volume, un PV le fournit.",
        "Le mode d'accès conditionne les possibilités de montage.",
        "`reclaimPolicy` décide de la conservation des données.",
        "Un StatefulSet donne une identité et un volume par pod.",
        "Un StatefulSet ne fournit pas la réplication applicative.",
        "Une réplication n'est pas une sauvegarde.",
    ],
    "bridge": "Les applications à état sont maîtrisées. Le chapitre suivant outille le "
              "déploiement de tout cela : Helm et service mesh.",
    "exercises": [
        ex("Monter un volume persistant",
           "Une application doit conserver ses fichiers entre deux redémarrages.",
           ["Créez le PVC.",
            "Montez-le dans le déploiement.",
            "Vérifiez la persistance."],
           [("yaml", """apiVersion: v1
kind: PersistentVolumeClaim
metadata: { name: uploads, namespace: production }
spec:
  accessModes: ["ReadWriteOnce"]
  resources: { requests: { storage: 10Gi } }
---
# dans le Deployment
volumes:
  - name: uploads
    persistentVolumeClaim: { claimName: uploads }
volumeMounts:
  - name: uploads
    mountPath: /app/uploads"""),
            "Écrire dans `/app/uploads`, redémarrer le pod, vérifier que le fichier est "
            "toujours là.",
            "Sans PVC, les fichiers disparaissent au redémarrage : c'est le premier test "
            "à faire pour valider une configuration."]),
        ex("Sauvegarder et restaurer",
           "La base doit être sauvegardée chaque nuit et restaurable.",
           ["Automatisez la sauvegarde.",
            "Testez la restauration.",
            "Documentez la procédure."],
           [("bash", """# Job Kubernetes de sauvegarde
apiVersion: batch/v1
kind: CronJob
metadata: { name: db-backup, namespace: production }
spec:
  schedule: "0 2 * * *"
  jobTemplate:
    spec:
      template:
        spec:
          restartPolicy: OnFailure
          containers:
            - name: dump
              image: postgres:16
              command: ["/bin/sh", "-c"]
              args:
                - pg_dump -h db -U app -Fc app | gzip > /backup/app-$(date +%F).dump.gz
              volumeMounts:
                - { name: backup, mountPath: /backup }
          volumes:
            - name: backup
              persistentVolumeClaim: { claimName: backups }"""),
            "La sauvegarde doit écrire sur un volume distinct de celui de la base.",
            "La restauration mensuelle dans un environnement jetable est la seule preuve "
            "que la sauvegarde est exploitable."]),
        ex("Choisir un modèle de stockage",
           "Trois applications : cache, téléversements, base critique.",
           ["Associez un type de volume.",
            "Justifiez la durée de vie.",
            "Indiquez la sauvegarde."],
           ["Cache : `emptyDir`, perdu au redémarrage, aucune sauvegarde.",
            "Téléversements : PVC `ReadWriteMany` ou stockage objet, sauvegarde "
            "quotidienne.",
            "Base critique : volume persistant avec rétention, sauvegarde externalisée et "
            "restauration testée, ou service managé."],
           level="Architecture"),
    ],
    "quiz": [
        quiz("Quel volume survit à la suppression du pod ?",
             ["`emptyDir`", "Un PVC", "Un montage `tmpfs`", "Aucun"],
             1,
             "Le volume persistant est indépendant du cycle de vie du pod."),
        quiz("Que signifie `ReadWriteOnce` ?",
             ["Un seul pod peut écrire", "Un seul nœud peut monter en écriture",
              "Lecture seule", "Écriture unique"],
             1,
             "Le volume est monté en écriture par un seul nœud à la fois."),
        quiz("Quel objet donne une identité stable aux réplicas ?",
             ["`Deployment`", "`ReplicaSet`", "`StatefulSet`", "`DaemonSet`"],
             2,
             "Les pods sont nommés et ordonnés, avec un volume par pod."),
        quiz("Pourquoi une réplication ne remplace-t-elle pas une sauvegarde ?",
             ["Elle est trop lente", "Une erreur logique se réplique",
              "Elle coûte trop cher", "Elle n'est pas fiable"],
             2,
             "Une suppression accidentelle est reproduite instantanément sur les réplicas."),
        quiz("Que fait `reclaimPolicy: Retain` ?",
             ["Supprime le volume", "Conserve le volume après suppression du PVC",
              "Réutilise le volume", "Chiffre le volume"],
             1,
             "Les données restent, mais nécessitent un nettoyage manuel."),
    ],
}
