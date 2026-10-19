from bookkit.dsl import (box, code, defn, ex, fig, h, ol, p, quiz, table, ul)

CH = {
    "title": "Services, entrées et configuration",
    "subtitle": "Exposer les applications, répartir le trafic et sortir la configuration "
                "des images.",
    "duration": "3 h 15",
    "level": "Intermédiaire",
    "prereq": "chapitre 61",
    "objectives": [
        "Choisir le type de Service adapté.",
        "Exposer une application HTTP avec un Ingress.",
        "Distinguer ConfigMap et Secret.",
        "Monter une configuration par variable ou par fichier.",
        "Diagnostiquer une erreur 404 ou 503 d'ingress.",
    ],
    "blocks": [
        h(2, "Le problème de l'adresse instable"),
        p("Les pods vont et viennent : leur adresse change. Un Service fournit une "
          "adresse et un nom stables, et répartit le trafic entre les pods qui "
          "correspondent à un sélecteur."),
        fig("flow", "Du pod au client",
            ["Client",
             "Ingress (nom d'hôte, TLS)",
             "Service (nom stable, répartition)",
             "Pods sélectionnés par étiquette",
             "Conteneurs"],
            height=245),
        table(["Type", "Portée", "Usage"],
              [["`ClusterIP`", "Interne au cluster", "Communication entre services"],
               ["`NodePort`", "Un port sur chaque nœud", "Développement, cas particulier"],
               ["`LoadBalancer`", "Fournisseur cloud", "Exposition directe"],
               ["`ExternalName`", "Alias DNS", "Service externe"],
               ["`Headless`", "Aucune IP virtuelle", "Accès direct aux pods"]],
              widths=[3.6, 4.4, 5.0], first_col_bold=True,
              caption="Cinq types de Service"),
        code("""apiVersion: v1
kind: Service
metadata:
  name: api
  namespace: production
spec:
  type: ClusterIP
  selector:
    app: api
  ports:
    - name: http
      port: 80
      targetPort: 3000
  sessionAffinity: None""", "yaml", "Un Service interne"),
        defn("Sélecteur", "Un Service ne référence pas des pods par leur nom, mais par "
                           "leurs étiquettes. Toute modification d'étiquette peut retirer "
                           "un pod du Service sans le supprimer."),
        code("""# Vérifier quels pods sont sélectionnés
kubectl get endpointslices -n production
kubectl describe service api -n production
kubectl get pods -n production --show-labels | grep app=api""", "bash",
             "Trois vérifications"),
        box("attention", "Un Service sans point de terminaison",
            "Si `kubectl get endpoints` renvoie une liste vide, le sélecteur ne "
            "correspond à aucun pod prêt. C'est la cause la plus fréquente d'un 503 : le "
            "Service existe, mais il ne sait pas où envoyer le trafic."),

        h(2, "Ingress"),
        p("Un Ingress décrit un routage HTTP par nom d'hôte et par chemin. Il nécessite un "
          "contrôleur d'ingress, qui est le composant réellement exposé."),
        code("""apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: site
  namespace: production
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/proxy-body-size: "10m"
spec:
  ingressClassName: nginx
  tls:
    - hosts: ["exemple.fr"]
      secretName: exemple-fr-tls
  rules:
    - host: exemple.fr
      http:
        paths:
          - path: /api
            pathType: Prefix
            backend:
              service:
                name: api
                port:
                  number: 80
          - path: /
            pathType: Prefix
            backend:
              service:
                name: web
                port:
                  number: 80""", "yaml", "Un ingress complet"),
        table(["Champ", "Rôle", "Piège"],
              [["`ingressClassName`", "Contrôleur utilisé", "Absent → ingress ignoré"],
               ["`pathType`", "Mode de correspondance", "`Prefix` souvent attendu"],
               ["`tls.secretName`", "Certificat", "Doit exister dans le même namespace"],
               ["`annotations`", "Réglages du contrôleur", "Spécifiques au contrôleur"],
               ["`host`", "Nom de domaine", "Doit correspondre au DNS"]],
              widths=[4.4, 4.6, 4.6], first_col_bold=True,
              caption="Cinq champs et leurs pièges"),
        code("""# Vérifier l'ordre des couches
kubectl get ingress -n production
kubectl describe ingress site -n production
kubectl get svc -n ingress-nginx
curl -H "Host: exemple.fr" http://<ip-du-controleur>/api/health""",
             "bash", "Quatre vérifications"),
        defn("Contrôleur d'ingress", "Composant qui surveille les objets Ingress et "
                                     "reconfigure un proxy (Nginx, Traefik, Envoy) en "
                                     "conséquence. Sans lui, un Ingress n'a aucun effet."),

        h(2, "Configuration externe"),
        p("Une image ne doit pas contenir la configuration de l'environnement. ConfigMap "
          "porte les valeurs non sensibles, Secret les valeurs sensibles."),
        code("""apiVersion: v1
kind: ConfigMap
metadata:
  name: api-config
  namespace: production
data:
  LOG_LEVEL: "info"
  CACHE_TTL: "300"
  app.properties: |
    feature.newMenu=true
    feature.betaBanner=false""", "yaml", "Une ConfigMap mixte"),
        code("""apiVersion: v1
kind: Secret
metadata:
  name: api-secret
  namespace: production
type: Opaque
stringData:
  DATABASE_URL: postgres://app:secret@db:5432/app""", "yaml",
             "Un Secret minimal"),
        box("attention", "Un Secret n'est pas chiffré par défaut",
            "Les secrets Kubernetes sont encodés en base64 et stockés dans `etcd`. Sans "
            "chiffrement au repos ni contrôle d'accès strict, ils sont lisibles par toute "
            "personne ayant accès à l'API. Utilisez un gestionnaire de secrets externe "
            "pour la production."),
        code("""# Consommer en variables
envFrom:
  - configMapRef: { name: api-config }
  - secretRef:    { name: api-secret }

# Consommer une clé précise
env:
  - name: LOG_LEVEL
    valueFrom:
      configMapKeyRef: { name: api-config, key: LOG_LEVEL }

# Consommer en fichier
volumes:
  - name: config
    configMap: { name: api-config }
volumeMounts:
  - name: config
    mountPath: /etc/app
    readOnly: true""", "yaml", "Trois modes de consommation"),
        table(["Mode", "Rechargement automatique", "Usage"],
              [["`envFrom`", "Non, au redémarrage", "Configuration simple"],
               ["`env` ciblé", "Non", "Une clé précise"],
               ["Volume", "Oui, avec délai", "Fichiers de configuration"],
               ["Argument", "Non", "Valeur figée"]],
              widths=[3.6, 5.0, 4.8], first_col_bold=True,
              caption="Quatre modes et leur réactivité"),
        box("pratique", "Monter un fichier sans écraser le reste",
            "Monter une ConfigMap dans `/etc/app` masque tout le contenu existant de ce "
            "répertoire. Utilisez `subPath` pour un fichier unique, en acceptant de perdre "
            "la mise à jour automatique."),

        h(2, "Réseau et DNS interne"),
        p("Chaque Service obtient un nom DNS interne. Le format varie selon le namespace "
          "et le besoin de qualification."),
        code("""# Depuis un pod du même namespace
curl http://api:80/health

# Depuis un autre namespace
curl http://api.production.svc.cluster.local/health

# Vérifier la résolution
kubectl run -it --rm debug --image=alpine --restart=Never -- sh
# nslookup api.production.svc.cluster.local""", "bash",
             "Trois formes de nom"),
        table(["Nom", "Résolution", "Portée"],
              [["`api`", "Service du namespace courant", "Local"],
               ["`api.production`", "Service dans un namespace nommé", "Cluster"],
               ["`api.production.svc`", "Forme intermédiaire", "Cluster"],
               ["`api.production.svc.cluster.local`", "Nom complet", "Cluster"]],
              widths=[6.0, 5.0, 3.0], first_col_bold=True,
              caption="Quatre formes de nom DNS"),
        p("Un `NetworkPolicy` peut restreindre ces communications. Sans politique, tous "
          "les pods d'un cluster communiquent librement : c'est un choix par défaut "
          "permissif à corriger dès que plusieurs équipes partagent un cluster."),

        h(2, "Diagnostiquer"),
        p("Un 404 et un 503 d'ingress n'ont pas la même signification : le premier "
          "concerne le routage, le second le service en amont."),
        table(["Symptôme", "Cause probable", "Vérification"],
              [["404", "Nom d'hôte ou chemin non routé", "`describe ingress`"],
               ["503", "Service sans endpoint", "`endpointslices`"],
               ["502", "Pod qui refuse la connexion", "`logs` du pod"],
               ["504", "Pod trop lent", "Délais du contrôleur"],
               ["TLS invalide", "Secret absent ou expiré", "`describe ingress`"],
               ["Redirection infinie", "Protocole transmis incorrect", "En-têtes du contrôleur"]],
              widths=[4.0, 5.0, 4.4], first_col_bold=True,
              caption="Six symptômes"),
        code("""kubectl describe ingress site -n production | tail -20
kubectl get endpointslices -n production -o wide
kubectl logs -n ingress-nginx deploy/ingress-nginx-controller --tail=50
kubectl get secret exemple-fr-tls -n production""", "bash",
             "Quatre commandes"),
        box("methode", "Diagnostic d'un ingress",
            items=["Le contrôleur d'ingress est-il installé et exposé ?",
                   "L'objet Ingress utilise-t-il le bon `ingressClassName` ?",
                   "Le service a-t-il des endpoints prêts ?",
                   "Les pods répondent-ils sur `targetPort` ?",
                   "Le DNS pointe-t-il vers le contrôleur ?"]),
    ],
    "keypoints": [
        "Un Service fournit un nom et une adresse stables.",
        "Le sélecteur relie un Service à des pods par étiquettes.",
        "Un Service sans endpoint renvoie 503.",
        "Un Ingress n'a d'effet qu'avec un contrôleur installé.",
        "`pathType` détermine la correspondance des chemins.",
        "ConfigMap pour le non-sensible, Secret pour le sensible.",
        "Un Secret est encodé, pas chiffré, par défaut.",
        "Les volumes de configuration se mettent à jour, les variables non.",
    ],
    "bridge": "Les applications sont exposées. Le chapitre suivant traite de ce qui "
              "persiste : stockage et état dans un cluster.",
    "exercises": [
        ex("Exposer une API par Ingress",
           "L'API doit être joignable sur `api.exemple.fr` en HTTPS.",
           ["Créez le Service.",
            "Créez l'Ingress avec TLS.",
            "Vérifiez le routage."],
           [("yaml", """apiVersion: v1
kind: Service
metadata: { name: api, namespace: production }
spec:
  selector: { app: api }
  ports: [{ port: 80, targetPort: 3000 }]
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: api
  namespace: production
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  ingressClassName: nginx
  tls:
    - hosts: ["api.exemple.fr"]
      secretName: api-tls
  rules:
    - host: api.exemple.fr
      http:
        paths:
          - path: /
            pathType: Prefix
            backend: { service: { name: api, port: { number: 80 } } }"""),
            "`cert-manager` crée le secret TLS à partir de l'annotation et du bloc `tls`.",
            "Le `Service` reste en `ClusterIP` : seul l'ingress est exposé."]),
        ex("Externaliser la configuration",
           "La même image doit fonctionner en recette et en production.",
           ["Créez deux ConfigMaps.",
            "Référencez-les par nom.",
            "Vérifiez la valeur effective."],
           [("bash", """kubectl create configmap api-config -n recette \\
  --from-literal=LOG_LEVEL=debug --from-literal=ENV=recette

kubectl create configmap api-config -n production \\
  --from-literal=LOG_LEVEL=info --from-literal=ENV=production

kubectl exec -n production deploy/api -- env | grep -E "LOG_LEVEL|ENV\""""),
            "L'image est identique : seule la configuration du namespace change.",
            "La vérification dans le pod évite de supposer que le déploiement a bien "
            "repris la configuration."]),
        ex("Diagnostiquer un 503",
           "L'ingress renvoie 503 pour `api.exemple.fr`.",
           ["Vérifiez les endpoints.",
            "Vérifiez les étiquettes.",
            "Vérifiez les sondes."],
           [("bash", """kubectl get endpointslices -n production -l kubernetes.io/service-name=api
kubectl get pods -n production --show-labels | grep app=api
kubectl describe pod -n production -l app=api | grep -A5 Readiness

# Un pod non prêt ne figure pas dans les endpoints
kubectl get pods -n production -o wide"""),
            "Un Service sans endpoint prêt renvoie 503 : soit aucune étiquette ne "
            "correspond, soit les pods ne sont pas prêts.",
            "Une sonde readiness trop stricte retire tous les pods en même temps, ce qui "
            "produit exactement ce symptôme."],
           level="Diagnostic"),
    ],
    "quiz": [
        quiz("Quel type de Service est interne au cluster ?",
             ["`NodePort`", "`LoadBalancer`", "`ClusterIP`", "`ExternalName`"],
             2,
             "`ClusterIP` n'est joignable que depuis l'intérieur du cluster."),
        quiz("Que renvoie un Service sans endpoint ?",
             ["200", "404", "503", "302"],
             2,
             "Le proxy n'a aucune destination : il renvoie une indisponibilité."),
        quiz("Que faut-il pour qu'un Ingress fonctionne ?",
             ["Un secret TLS", "Un contrôleur d'ingress", "Un NodePort", "Un pod dédié"],
             1,
             "Le contrôleur traduit l'Ingress en configuration de proxy."),
        quiz("Un Secret Kubernetes est-il chiffré par défaut ?",
             ["Oui, avec AES", "Non, seulement encodé en base64",
              "Oui, avec la clé du cluster", "Cela dépend du namespace"],
             1,
             "Seul le chiffrement au repos de `etcd` protège réellement les valeurs."),
        quiz("Quel mode de configuration se met à jour sans redémarrage ?",
             ["`envFrom`", "`env` ciblé", "Un volume monté", "Un argument de commande"],
             2,
             "Le kubelet rafraîchit les fichiers montés depuis une ConfigMap."),
    ],
}
