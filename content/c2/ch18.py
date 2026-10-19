from bookkit.dsl import (box, code, defn, ex, fig, h, ol, p, quiz, table, ul)

CH = {
    "title": "Images reproductibles et sûres",
    "subtitle": "Construire des images qu'on peut reconstruire à l'identique, analyser "
                "et mettre à jour.",
    "duration": "3 h 00",
    "level": "Intermédiaire",
    "prereq": "chapitre 57",
    "objectives": [
        "Épingler les dépendances pour une construction reproductible.",
        "Réduire la taille et la surface d'attaque d'une image.",
        "Exécuter un conteneur sans privilèges.",
        "Analyser et corriger les vulnérabilités.",
        "Publier et versionner des images.",
    ],
    "blocks": [
        h(2, "Reproductible, pas seulement fonctionnel"),
        p("Une image est reproductible si la reconstruire depuis les mêmes sources donne "
          "le même résultat. Sans épinglage, `latest` change sous vos pieds et deux "
          "constructions le même jour peuvent différer."),
        table(["Élément", "Non reproductible", "Reproductible"],
              [["Image de base", "`node:latest`", "`node:22.9.0-alpine3.20@sha256:…`"],
               ["Dépendances", "`npm install`", "`npm ci` avec verrou"],
               ["Paquets système", "`apt install curl`", "`apt install curl=8.5.0-2`"],
               ["Date de construction", "Intégrée", "Argument stable"],
               ["Ordre des fichiers", "Variable", "Copie triée"]],
              widths=[3.6, 4.6, 4.8], first_col_bold=True,
              caption="Cinq sources de variabilité"),
        code("""# Épinglage par empreinte : le plus strict
FROM node:22.9.0-alpine3.20@sha256:4c2f3a1b... AS build

# Mise à jour de l'empreinte : outil dédié
docker pull node:22.9.0-alpine3.20
docker inspect --format '{{index .RepoDigests 0}}' node:22.9.0-alpine3.20""",
             "dockerfile", "Deux commandes d'épinglage"),
        defn("Empreinte d'image", "Identifiant de contenu calculé sur l'ensemble des "
                                  "couches. Contrairement à une étiquette, il ne peut pas "
                                  "être déplacé vers un autre contenu."),
        code("""# Construction avec des arguments de compilation et des métadonnées
docker build \\
  --build-arg VERSION=$(git describe --tags --always) \\
  --build-arg COMMIT=$(git rev-parse --short HEAD) \\
  --label org.opencontainers.image.revision=$COMMIT \\
  -t registry.exemple.fr/app:1.4.2 .""", "bash",
             "Deux informations traçables"),

        h(2, "Réduire la taille"),
        p("Une image plus petite se télécharge plus vite, contient moins de composants "
          "vulnérables et expose moins de binaires utilisables par un attaquant."),
        table(["Technique", "Gain typique", "Remarque"],
              [["Multi-étapes", "50 à 90 %", "Seul l'artefact final est conservé"],
               ["Image de base minimale", "30 à 70 %", "Alpine, distroless, scratch"],
               ["Suppression des caches", "5 à 15 %", "Dans la même couche `RUN`"],
               ["`.dockerignore`", "Variable", "Évite d'envoyer l'inutile"],
               ["Pas de compilateur", "Élevé", "Construire ailleurs"]],
              widths=[4.4, 3.4, 5.0], first_col_bold=True,
              caption="Cinq techniques de réduction"),
        code("""# Mauvais : le cache reste dans l'image
RUN apt-get update && apt-get install -y curl

# Bon : mise à jour, installation et nettoyage dans une seule couche
RUN apt-get update \\
 && apt-get install -y --no-install-recommends curl \\
 && rm -rf /var/lib/apt/lists/*""", "dockerfile",
             "Une seule couche, aucun résidu"),
        code("""# Vérifier la taille et le contenu
docker images app
docker history app:1.4.2
dive app:1.4.2        # exploration interactive des couches""", "bash",
             "Trois outils d'analyse"),

        h(2, "Exécuter sans privilèges"),
        p("Par défaut, le processus d'un conteneur est root. Une évasion ou une faille "
          "applicative donne alors des droits élevés à l'intérieur, et parfois au-delà."),
        code("""# Créer un utilisateur et basculer avant la commande finale
FROM node:22.9.0-alpine3.20
WORKDIR /app
COPY --chown=node:node . .
USER node
CMD ["node", "server.js"]""", "dockerfile", "Deux lignes suffisent"),
        code("""# Au niveau de l'exécution
docker run -d \\
  --user 10001:10001 \\
  --read-only \\
  --tmpfs /tmp \\
  --cap-drop ALL \\
  --security-opt no-new-privileges \\
  mon-app:1.0""", "bash", "Cinq restrictions"),
        table(["Option", "Effet", "Contrepartie"],
              [["`--read-only`", "Système de fichiers immuable", "Prévoir un volume pour les écritures"],
               ["`--cap-drop ALL`", "Supprime les capacités", "En réaccorder si nécessaire"],
               ["`no-new-privileges`", "Bloque l'élévation", "Aucune"],
               ["`--user`", "Utilisateur non privilégié", "Droits sur les volumes"],
               ["`--tmpfs /tmp`", "Espace temporaire en mémoire", "Consommation RAM"]],
              widths=[4.4, 4.4, 4.4], first_col_bold=True,
              caption="Cinq restrictions d'exécution"),
        box("attention", "Monter le socket Docker donne les pleins pouvoirs",
            "`-v /var/run/docker.sock:/var/run/docker.sock` permet à un conteneur de "
            "créer un conteneur privilégié sur l'hôte. C'est une évasion de privilèges "
            "immédiate ; ne l'accordez jamais à un conteneur non fiable."),

        h(2, "Analyser les vulnérabilités"),
        p("Une image contient un système d'exploitation en réduction : ses paquets ont "
          "des vulnérabilités connues. L'analyse doit être automatisée, sinon elle n'est "
          "jamais faite."),
        code("""# Analyse locale
docker scout quickview app:1.4.2
docker scout cves app:1.4.2 --only-severity critical,high

# Alternatives
trivy image --severity HIGH,CRITICAL app:1.4.2
grype app:1.4.2 --fail-on high

# Analyse du Dockerfile
hadolint Dockerfile""", "bash", "Cinq outils d'analyse"),
        code("""# Exemple de sortie trivy

app:1.4.2 (alpine 3.20.3)
Total: 3 (HIGH: 2, CRITICAL: 1)

┌────────────┬────────────────┬──────────┬───────────────────┐
│  Library   │ Vulnerability  │ Severity │ Installed Version │
├────────────┼────────────────┼──────────┼───────────────────┤
│ libcrypto3 │ CVE-2026-12345 │ CRITICAL │ 3.3.1-r0          │
│ libssl3    │ CVE-2026-12346 │ HIGH     │ 3.3.1-r0          │
└────────────┴────────────────┴──────────┴───────────────────┘""",
             "text", "Un rapport lisible"),
        table(["Niveau", "Délai de correction", "Action"],
              [["Critique", "24 heures", "Bloquer la publication"],
               ["Élevée", "7 jours", "Planifier"],
               ["Moyenne", "30 jours", "Suivi"],
               ["Faible", "Prochain cycle", "Documenter"]],
              widths=[3.2, 4.4, 5.4], first_col_bold=True,
              caption="Quatre niveaux et leurs délais"),
        p("Une vulnérabilité sans correctif disponible ne se traite pas en mettant à jour : "
          "il faut réduire l'exposition, isoler le service ou remplacer le composant."),

        h(2, "Publier et versionner"),
        p("Une image se publie dans un registre, étiquetée par version, et accompagnée "
          "d'informations de provenance. Les étiquettes mobiles (`latest`) ne doivent "
          "jamais être utilisées en production."),
        code("""# Étiqueter et pousser
docker tag app:1.4.2 registry.exemple.fr/equipe/app:1.4.2
docker tag app:1.4.2 registry.exemple.fr/equipe/app:1.4
docker push registry.exemple.fr/equipe/app:1.4.2
docker push registry.exemple.fr/equipe/app:1.4

# Authentification
docker login registry.exemple.fr

# Signature (cosign)
cosign sign --key cosign.key registry.exemple.fr/equipe/app:1.4.2""", "bash",
             "Cinq commandes de publication"),
        table(["Étiquette", "Signification", "Usage"],
              [["`1.4.2`", "Version exacte", "Production"],
               ["`1.4`", "Dernière 1.4.x", "Commodité"],
               ["`latest`", "Dernière publiée", "Jamais en production"],
               ["`sha-a1b2c3`", "Commit source", "Traçabilité"],
               ["`main`", "Dernière de la branche", "Test"]],
              widths=[3.6, 4.6, 4.6], first_col_bold=True,
              caption="Cinq conventions d'étiquetage"),
        box("methode", "Guide de construction d'image",
            items=["Image de base épinglée par empreinte.",
                   "Aucun secret dans les couches.",
                   "Utilisateur non privilégié.",
                   "Analyse de vulnérabilités dans la CI.",
                   "Étiquette de version immuable et signature."]),
    ],
    "keypoints": [
        "Une image reproductible épingle base et dépendances.",
        "L'empreinte identifie un contenu, l'étiquette peut être déplacée.",
        "Multi-étapes et base minimale réduisent taille et surface d'attaque.",
        "Le nettoyage doit se faire dans la même couche `RUN`.",
        "Un conteneur doit tourner avec un utilisateur non privilégié.",
        "Le socket Docker monté est une évasion de privilèges.",
        "L'analyse de vulnérabilités doit être automatisée.",
        "Une version de production est immuable et signée.",
    ],
    "bridge": "Les images sont propres. Le chapitre suivant les relie entre elles : "
              "réseaux et volumes.",
    "exercises": [
        ex("Réduire une image de 1,2 Go",
           "Une image Node embarque les sources et les outils de construction.",
           ["Passez en multi-étapes.",
            "Choisissez une base minimale.",
            "Vérifiez la taille."],
           [("dockerfile", """FROM node:22.9.0-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:22.9.0-alpine
WORKDIR /app
ENV NODE_ENV=production
COPY package*.json ./
RUN npm ci --omit=dev && npm cache clean --force
COPY --from=build /app/dist ./dist
USER node
CMD ["node", "dist/server.js"]"""),
            "L'image finale ne contient que les dépendances d'exécution et l'artefact.",
            "`npm cache clean --force` dans la même couche évite de conserver le cache "
            "de téléchargement."]),
        ex("Restreindre l'exécution",
           "Le service doit tourner sans droits particuliers.",
           ["Utilisateur non privilégié.",
            "Système de fichiers en lecture seule.",
            "Suppression des capacités."],
           [("bash", """docker run -d \\
  --name app \\
  --user 10001:10001 \\
  --read-only \\
  --tmpfs /tmp:rw,size=64m \\
  --cap-drop ALL \\
  --security-opt no-new-privileges \\
  -p 8080:3000 \\
  registry.exemple.fr/equipe/app:1.4.2

# Vérifier
docker inspect app --format '{{.Config.User}} {{.HostConfig.ReadonlyRootfs}}'"""),
            "Un service qui écrit dans son répertoire courant échouera : c'est justement "
            "ce que la restriction révèle.",
            "`--tmpfs` fournit un espace d'écriture éphémère pour les fichiers temporaires."],
           level="Sécurité"),
        ex("Traiter une vulnérabilité critique",
           "L'analyse signale une CVE critique dans la bibliothèque TLS.",
           ["Identifiez le paquet.",
            "Mettez à jour la base.",
            "Vérifiez et republiez."],
           [("bash", """trivy image --severity CRITICAL app:1.4.2

# Mise à jour de l'image de base
docker pull node:22.9.0-alpine3.20
docker build --no-cache -t app:1.4.3 .
trivy image --severity CRITICAL app:1.4.3

# Publier seulement si l'analyse est propre
docker push registry.exemple.fr/equipe/app:1.4.3"""),
            "`--no-cache` garantit que la nouvelle base est réellement utilisée.",
            "La publication conditionnée à une analyse propre empêche la réintroduction "
            "du défaut."],
           level="Sécurité"),
    ],
    "quiz": [
        quiz("Pourquoi épingler une image par empreinte ?",
             ["Pour accélérer le téléchargement", "Parce qu'une étiquette peut changer",
              "Pour réduire la taille", "Pour signer l'image"],
             1,
             "Seule l'empreinte garantit un contenu identique dans le temps."),
        quiz("Où doivent se faire le nettoyage des caches de paquets ?",
             ["Dans une couche séparée", "Dans la même couche `RUN`",
              "Après la construction", "Dans un volume"],
             1,
             "Une suppression dans une autre couche ne réduit pas la taille finale."),
        quiz("Pourquoi éviter `--user root` en production ?",
             ["C'est plus lent", "Une faille applicative donne des droits élevés",
              "Cela empêche les logs", "C'est obsolète"],
             1,
             "Le principe du moindre privilège limite l'impact d'une compromission."),
        quiz("Que permet de faire un socket Docker monté ?",
             ["Lire les logs", "Créer des conteneurs privilégiés sur l'hôte",
              "Accélérer les builds", "Partager des volumes"],
             1,
             "C'est une évasion de privilèges : à éviter absolument."),
        quiz("Quelle étiquette ne doit jamais servir en production ?",
             ["`1.4.2`", "`1.4`", "`sha-a1b2c3`", "`latest`"],
             3,
             "`latest` n'est pas immuable et peut pointer vers un contenu inconnu."),
    ],
}
