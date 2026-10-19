from bookkit.dsl import (box, code, defn, ex, fig, h, ol, p, quiz, table, ul)

CH = {
    "title": "Durcissement des conteneurs et du cluster",
    "subtitle": "Réduire ce qu'un conteneur peut faire, pour réduire ce qu'une faille "
                "peut coûter.",
    "duration": "3 h 15",
    "level": "Avancé",
    "prereq": "chapitres 17 et 21",
    "objectives": [
        "Connaître les frontières d'isolation réelles.",
        "Écrire un contexte de sécurité de pod.",
        "Restreindre les capacités et le système de fichiers.",
        "Isoler le réseau entre espaces de noms.",
        "Vérifier un durcissement au lieu de le supposer.",
    ],
    "blocks": [
        h(2, "Ce qu'un conteneur n'isole pas"),
        p("Un conteneur n'est pas une machine virtuelle : il partage le noyau de l'hôte. "
          "Les frontières sont des espaces de noms et des groupes de contrôle, pas une "
          "barrière matérielle."),
        table(["Ressource", "Isolée par", "Faille possible"],
              [["Système de fichiers", "Montages et racine", "Écriture hors volume"],
               ["Processus", "Espace de noms PID", "Orphelins sur l'hôte"],
               ["Réseau", "Espace de noms réseau", "Contournement par l'hôte"],
               ["Utilisateur", "Espace de noms utilisateur", "Exécution en root"],
               ["Noyau", "Partagé", "Faille de noyau = évasion"]],
              widths=[4.2, 5.0, 4.8], first_col_bold=True,
              caption="Cinq frontières"),
        defn("Évasion de conteneur", "Exploitation d'une faille ou d'une configuration "
                                     "permissive permettant à un processus de sortir de "
                                     "son conteneur et d'accéder à l'hôte."),
        fig("stack", "Couches de durcissement",
            ["Noyau partagé : mises à jour de l'hôte",
             "Runtime : pas de socket Docker monté",
             "Utilisateur : non root, racine en lecture seule",
             "Capacités : liste blanche minimale",
             "Système de fichiers : lecture seule",
             "Réseau : politiques et sorties contrôlées"],
            height=265),

        h(2, "Contexte de sécurité"),
        p("Kubernetes permet de déclarer précisément les droits d'un conteneur. Les "
          "valeurs par défaut sont permissives : il faut les restreindre explicitement."),
        code("""apiVersion: v1
kind: Pod
metadata:
  name: api
  namespace: boutique
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 10001
    runAsGroup: 10001
    fsGroup: 10001
    seccompProfile:
      type: RuntimeDefault
  containers:
    - name: api
      image: registry.exemple.fr/boutique:1.4.2
      securityContext:
        allowPrivilegeEscalation: false
        readOnlyRootFilesystem: true
        capabilities:
          drop: ["ALL"]
      volumeMounts:
        - name: temporaire
          mountPath: /tmp
        - name: cache
          mountPath: /app/.cache
  volumes:
    - name: temporaire
      emptyDir: { sizeLimit: 64Mi }
    - name: cache
      emptyDir: { sizeLimit: 256Mi }""", "yaml", "Un pod durci"),
        table(["Réglage", "Empêche", "Effet de bord"],
              [["`runAsNonRoot`", "Exécution en root", "Image non compatible"],
               ["`readOnlyRootFilesystem`", "Écriture hors volume", "Journaux à rediriger"],
               ["`drop: ALL`", "Capacités inutiles", "Besoin explicite à ajouter"],
               ["`allowPrivilegeEscalation: false`", "Élévation de privilèges", "Aucun"],
               ["`seccompProfile`", "Appels système dangereux", "Appels exotiques bloqués"]],
              widths=[5.6, 4.6, 4.0], first_col_bold=True,
              caption="Cinq réglages"),
        box("attention", "Un conteneur root contourne la plupart des protections",
            "Un processus root dans son conteneur peut, selon les capacités accordées, "
            "modifier des fichiers montés et attaquer par des chemins inattendus. "
            "L'utilisateur non privilégié est la première mesure, pas la dernière."),
        defn("seccomp", "Filtre d'appels système. Le profil `RuntimeDefault` bloque les "
                        "appels rarement utilisés, réduisant la surface d'attaque sans "
                        "configuration spécifique."),

        h(2, "Images et runtime"),
        p("Le durcissement commence avant le cluster : une image minimale et à jour "
          "supprime des outils qui servent aux attaquants après une intrusion."),
        code("""# Image distroless, sans shell ni gestionnaire de paquets
FROM node:22-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM gcr.io/distroless/nodejs22-debian12
WORKDIR /app
COPY --from=build /app/dist ./dist
COPY --from=build /app/node_modules ./node_modules
USER 10001
EXPOSE 3000
CMD ["dist/serveur.js"]""", "dockerfile", "Une image sans shell"),
        table(["Choix", "Gain", "Coût"],
              [["Image distroless", "Pas de shell pour l'attaquant", "Débogage plus difficile"],
               ["Utilisateur non root", "Moins de droits", "Permissions à ajuster"],
               ["Base alpine ou slim", "Surface réduite", "Bibliothèques C absentes"],
               ["Épinglage par empreinte", "Reproductibilité", "Mises à jour manuelles"]],
              widths=[4.6, 4.6, 4.8], first_col_bold=True,
              caption="Quatre choix"),
        code("""# Vérifier ce que l'image contient vraiment
docker run --rm -it --entrypoint /bin/sh registry.exemple.fr/boutique:1.4.2
# si le shell n'existe pas : l'image est bien minimale

# Lister les paquets installés
syft registry.exemple.fr/boutique:1.4.2 -o table | head -20""",
             "bash", "Deux vérifications"),
        box("attention", "Ne montez jamais le socket Docker dans un conteneur",
            "Un socket monté donne un contrôle total sur l'hôte : le conteneur peut lancer "
            "un conteneur privilégié. Cette pratique, fréquente dans les outils de "
            "construction, doit rester confinée à des runners jetables et isolés."),

        h(2, "Isolation réseau"),
        p("Par défaut, tous les pods d'un cluster peuvent se joindre. Une politique réseau "
          "qui refuse tout puis autorise le nécessaire transforme un cluster plat en "
          "ensemble de zones cloisonnées."),
        code("""# Refus par défaut dans l'espace de noms
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: refus-par-defaut
  namespace: boutique
spec:
  podSelector: {}
  policyTypes: [Ingress, Egress]
---
# Autoriser uniquement le trafic depuis l'ingress vers l'API
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: api-depuis-ingress
  namespace: boutique
spec:
  podSelector:
    matchLabels: { app: api }
  policyTypes: [Ingress]
  ingress:
    - from:
        - namespaceSelector:
            matchLabels: { kubernetes.io/metadata.name: ingress-nginx }
      ports:
        - protocol: TCP
          port: 3000""", "yaml", "Deux politiques"),
        table(["Règle", "Autorise", "Vérification"],
              [["Refus par défaut", "Rien", "Test de connexion refusé"],
               ["Depuis l'ingress", "Trafic entrant HTTP", "`curl` depuis un pod"],
               ["Vers la base", "Sortie vers 5432", "Connexion réussie"],
               ["Vers le DNS", "UDP 53", "Résolution fonctionnelle"]],
              widths=[4.2, 4.8, 5.0], first_col_bold=True,
              caption="Quatre règles"),
        box("pratique", "Le DNS est la première chose qu'on oublie de réautoriser",
            "Un refus de sortie total casse la résolution de noms et fait échouer toutes "
            "les connexions par nom d'hôte. Autorisez explicitement le port 53 vers le "
            "service DNS du cluster."),

        h(2, "Vérifier"),
        p("Un durcissement non vérifié est une intention. Quelques commandes montrent "
          "l'utilisateur effectif, les capacités et la possibilité d'écrire hors volume."),
        code("""# Utilisateur effectif
kubectl exec -n boutique deploy/api -- id
# uid=10001 gid=10001, pas uid=0

# Capacités disponibles
kubectl exec -n boutique deploy/api -- grep Cap /proc/self/status
# CapEff: 0000000000000000  → aucune capacité

# Écriture à la racine du système de fichiers
kubectl exec -n boutique deploy/api -- touch /essai
# touch: /essai: Read-only file system

# Politiques réseau appliquées
kubectl get networkpolicy -n boutique""", "bash", "Quatre vérifications"),
        table(["Contrôle", "Attendu", "Échec"],
              [["`id`", "UID non nul", "UID 0"],
               ["`CapEff`", "`0000000000000000`", "Capacités résiduelles"],
               ["`touch /`", "Lecture seule", "Écriture acceptée"],
               ["Connexion latérale", "Refusée", "Toutes les connexions passent"]],
              widths=[4.6, 5.0, 4.4], first_col_bold=True,
              caption="Quatre contrôles"),
        code("""# Test d'une connexion latérale non autorisée
kubectl run test --rm -it --image=busybox -n boutique --restart=Never -- \\
  wget -qO- --timeout=3 http://api:3000/sante
# attendu : timeout si la politique refuse

# Pod Security Standards : restreindre l'admission
kubectl label namespace boutique \\
  pod-security.kubernetes.io/enforce=restricted \\
  pod-security.kubernetes.io/audit=restricted \\
  pod-security.kubernetes.io/warn=restricted""", "bash", "Deux tests"),
        box("methode", "Durcir sans casser",
            items=["Commencer par l'utilisateur non root.",
                   "Activer la lecture seule et monter les volumes nécessaires.",
                   "Supprimer toutes les capacités, ajouter seulement le nécessaire.",
                   "Refuser le réseau par défaut, autoriser au cas par cas.",
                   "Vérifier par des commandes, pas par la lecture du manifeste."]),
    ],
    "keypoints": [
        "Un conteneur partage le noyau : l'isolation est logique.",
        "Un processus root dans le conteneur élargit fortement l'impact d'une faille.",
        "`runAsNonRoot`, `readOnlyRootFilesystem` et `drop: ALL` forment le socle.",
        "`seccompProfile: RuntimeDefault` réduit les appels système disponibles.",
        "Une image minimale supprime les outils utiles à l'attaquant.",
        "Le socket Docker ne se monte jamais dans un conteneur applicatif.",
        "Un refus réseau par défaut exige d'autoriser le DNS explicitement.",
        "Le durcissement se vérifie par des commandes.",
    ],
    "bridge": "Le cluster est durci. Le chapitre suivant conserve les traces nécessaires "
              "pour comprendre et prouver.",
    "exercises": [
        ex("Durcir un pod",
           "Un service Node tourne actuellement en root, avec écriture partout.",
           ["Passez en utilisateur non root.",
            "Activez la lecture seule.",
            "Supprimez les capacités."],
           [("yaml", """securityContext:
  runAsNonRoot: true
  runAsUser: 10001
  seccompProfile: { type: RuntimeDefault }
containers:
  - name: api
    securityContext:
      allowPrivilegeEscalation: false
      readOnlyRootFilesystem: true
      capabilities: { drop: ["ALL"] }
    volumeMounts:
      - { name: tmp, mountPath: /tmp }
volumes:
  - name: tmp
    emptyDir: { sizeLimit: 64Mi }"""),
            "Sans volume temporaire, l'écriture dans `/tmp` échoue et le service peut ne "
            "plus démarrer.",
            "Vérifiez avec `id` après déploiement : le manifeste ne suffit pas."]),
        ex("Isoler deux espaces de noms",
           "Le service de paiement ne doit pas être joignable depuis la boutique.",
           ["Refusez par défaut.",
            "Autorisez le DNS.",
            "Autorisez la passerelle."],
           [("yaml", """apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata: { name: refus, namespace: paiement }
spec:
  podSelector: {}
  policyTypes: [Ingress, Egress]
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata: { name: dns, namespace: paiement }
spec:
  podSelector: {}
  policyTypes: [Egress]
  egress:
    - to:
        - namespaceSelector: { matchLabels: { kubernetes.io/metadata.name: kube-system } }
      ports: [{ protocol: UDP, port: 53 }, { protocol: TCP, port: 53 }]
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata: { name: depuis-passerelle, namespace: paiement }
spec:
  podSelector: { matchLabels: { app: paiement } }
  policyTypes: [Ingress]
  ingress:
    - from:
        - namespaceSelector: { matchLabels: { kubernetes.io/metadata.name: ingress-nginx } }
      ports: [{ protocol: TCP, port: 8080 }]"""),
            "Le refus de sortie coupe le DNS : la règle DNS doit accompagner le refus.",
            "Le test se fait depuis un pod de l'espace `boutique`, qui doit voir sa "
            "connexion expirer."],
           level="Sécurité"),
        ex("Vérifier un durcissement",
           "L'équipe affirme avoir durci les conteneurs.",
           ["Contrôlez l'utilisateur.",
            "Contrôlez les capacités.",
            "Tentez une écriture."],
           [("bash", """kubectl exec -n boutique deploy/api -- id
kubectl exec -n boutique deploy/api -- grep CapEff /proc/self/status
kubectl exec -n boutique deploy/api -- touch /essai
kubectl run test --rm -it --image=busybox -n boutique --restart=Never -- \\
  wget -qO- --timeout=3 http://api:3000/sante"""),
            "Ces quatre commandes couvrent 80 % du risque réel.",
            "Un refus d'écriture et un timeout réseau sont de bons signes, pas des pannes."],
           level="Audit"),
    ],
    "quiz": [
        quiz("Qu'est-ce qui n'est pas isolé par un conteneur ?",
             ["Le système de fichiers", "Le noyau", "Le réseau", "Les processus"],
             1,
             "Le noyau est partagé avec l'hôte."),
        quiz("Quel réglage empêche l'écriture hors volumes ?",
             ["`runAsNonRoot`", "`readOnlyRootFilesystem`", "`drop: ALL`", "`seccomp`"],
             1,
             "Il rend la racine du conteneur en lecture seule."),
        quiz("Pourquoi un conteneur root est-il dangereux ?",
             ["Il consomme plus", "Il dispose de plus de droits en cas de faille",
              "Il démarre mieux", "Il est plus lent"],
             1,
             "L'impact d'une évasion ou d'une erreur devient majeur."),
        quiz("Que faut-il autoriser après un refus réseau global ?",
             ["Rien", "Le DNS", "Tout le cluster", "Internet"],
             1,
             "Sans DNS, toutes les connexions par nom échouent."),
        quiz("Comment vérifier un durcissement ?",
             ["Lire le manifeste", "Exécuter `id` et lire `/proc/self/status`",
              "Demander à l'équipe", "Consulter le schéma"],
             1,
             "Seule l'exécution prouve l'état réel."),
    ],
}
