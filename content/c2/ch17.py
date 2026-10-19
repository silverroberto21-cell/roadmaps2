from bookkit.dsl import (box, code, defn, ex, fig, h, ol, p, quiz, table, ul)

CH = {
    "title": "Docker : conteneurs, images et cycle de vie",
    "subtitle": "Comprendre ce qu'est réellement un conteneur, puis l'utiliser sans en "
                "faire une machine virtuelle.",
    "duration": "3 h 15",
    "level": "Intermédiaire",
    "prereq": "chapitre 56",
    "objectives": [
        "Distinguer conteneur, image et machine virtuelle.",
        "Exécuter et inspecter un conteneur.",
        "Écrire un Dockerfile lisible.",
        "Gérer les ressources et le cycle de vie.",
        "Nettoyer sans supprimer l'utile.",
    ],
    "blocks": [
        h(2, "Un processus isolé, pas une machine"),
        p("Un conteneur est un processus ordinaire, isolé par des mécanismes du noyau : "
          "espaces de noms pour la visibilité, groupes de contrôle pour les ressources. "
          "Il n'y a pas de noyau invité, donc pas de démarrage de système."),
        fig("compare", "Machine virtuelle et conteneur",
            ("MACHINE VIRTUELLE", ["Noyau invité complet", "Démarrage en dizaines de secondes",
                                   "Image de plusieurs Go"],
             "CONTENEUR", ["Partage le noyau", "Démarrage en millisecondes",
                           "Image de quelques Mo"]),
            height=215),
        table(["Aspect", "Machine virtuelle", "Conteneur"],
              [["Isolation", "Forte (matériel émulé)", "Processus (noyau partagé)"],
               ["Démarrage", "Secondes à minutes", "Millisecondes"],
               ["Densité", "Quelques-unes par hôte", "Des dizaines par hôte"],
               ["Sécurité", "Frontière matérielle", "Frontière du noyau"],
               ["Usage typique", "Système complet", "Service unique"]],
              widths=[3.4, 4.8, 4.8], first_col_bold=True,
              caption="Cinq différences"),
        defn("Image", "Archive immuable composée de couches empilées. Le conteneur est "
                      "une instance en exécution de cette image, avec une couche "
                      "d'écriture propre."),
        code("""# Exécuter et observer
docker run -d --name web -p 8080:80 nginx:1.27-alpine
docker ps
docker logs -f web
docker exec -it web sh
docker inspect web | head -40
docker stats web""", "bash", "Six commandes de base"),
        table(["Sous-commande", "Rôle", "Remarque"],
              [["`run`", "Créer et démarrer", "Une commande = un conteneur"],
               ["`ps`", "Lister", "`-a` inclut les arrêtés"],
               ["`logs`", "Sortie du processus", "`-f` en direct"],
               ["`exec`", "Commande dans le conteneur", "Diagnostic"],
               ["`inspect`", "Détails complets", "JSON"],
               ["`rm` / `rmi`", "Supprimer conteneur / image", "Ordre obligatoire"],
               ["`system df`", "Espace utilisé", "Premier réflexe de nettoyage"]],
              widths=[3.2, 5.4, 4.4], first_col_bold=True,
              caption="Sept sous-commandes usuelles"),

        h(2, "Le Dockerfile"),
        p("Un Dockerfile décrit une suite d'étapes. Chaque instruction crée une couche "
          "en cache : l'ordre des instructions détermine la vitesse de reconstruction."),
        code("""# syntax=docker/dockerfile:1
FROM node:22-alpine AS dependances
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci

FROM node:22-alpine AS construction
WORKDIR /app
COPY --from=dependances /app/node_modules ./node_modules
COPY . .
RUN npm run build

FROM nginx:1.27-alpine AS production
COPY --from=construction /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
HEALTHCHECK --interval=30s --timeout=3s \\
  CMD wget -qO- http://127.0.0.1/ >/dev/null || exit 1""",
             "dockerfile", "Une construction en trois étapes"),
        table(["Instruction", "Rôle", "Conseil"],
              [["`FROM`", "Image de base", "Épingler une version"],
               ["`WORKDIR`", "Répertoire de travail", "Toujours explicite"],
               ["`COPY`", "Copier des fichiers", "Copier le manifeste d'abord"],
               ["`RUN`", "Exécuter à la construction", "Regrouper et nettoyer"],
               ["`CMD`", "Commande par défaut", "Forme JSON"],
               ["`ENTRYPOINT`", "Commande fixe", "Souvent un script d'entrée"],
               ["`USER`", "Utilisateur d'exécution", "Ne jamais rester root"]],
              widths=[3.2, 5.4, 4.4], first_col_bold=True,
              caption="Sept instructions courantes"),
        code("""# Ordre des couches : le plus stable d'abord
COPY package*.json ./      # change rarement
RUN npm ci                 # cache réutilisé
COPY src/ ./src            # change souvent""", "dockerfile",
             "Un ordre pensé pour le cache"),
        box("attention", "Ne jamais copier `node_modules`",
            "Un `.dockerignore` évite d'envoyer au démon des dizaines de milliers de "
            "fichiers, de rendre le cache inopérant et d'embarquer des binaires "
            "incompatibles avec l'image."),
        code("""# .dockerignore
node_modules
.git
dist
coverage
*.log
.env
Dockerfile
README.md""", "text", "Un `.dockerignore` minimal"),

        h(2, "Cycle de vie et ressources"),
        p("Un conteneur s'arrête quand son processus principal se termine. Un conteneur "
          "dont le processus principal est un shell lancé sans commande s'arrête "
          "immédiatement : c'est une confusion fréquente."),
        code("""# Cycle de vie
docker create ... && docker start <id>
docker stop web          # SIGTERM puis SIGKILL après 10 s
docker stop -t 30 web    # laisser 30 s pour finir proprement
docker restart web
docker rm -f web

# Ressources
docker run -d --memory 512m --cpus 1.5 --pids-limit 200 mon-app:1.0
docker update --memory 1g web""", "bash", "Deux familles de commandes"),
        table(["Limite", "Option", "Effet d'un dépassement"],
              [["Mémoire", "`--memory`", "Processus tué (`OOMKilled`)"],
               ["Processeur", "`--cpus`", "Ralentissement, pas d'arrêt"],
               ["Processus", "`--pids-limit`", "Refus de création"],
               ["Redémarrage", "`--restart`", "Relance automatique"],
               ["Journal", "`--log-opt max-size`", "Rotation des logs"]],
              widths=[3.4, 4.6, 5.0], first_col_bold=True,
              caption="Cinq limites de ressources"),
        defn("`OOMKilled`", "État d'un conteneur dont le processus a été tué par le noyau "
                            "faute de mémoire. Le code de sortie est 137 ; il ne faut pas "
                            "le confondre avec un plantage applicatif."),
        code("""# Identifier un arrêt par manque de mémoire
docker inspect web --format '{{.State.OOMKilled}} {{.State.ExitCode}}'

# Journalisation bornée
docker run -d --log-opt max-size=10m --log-opt max-file=3 mon-app:1.0""",
             "bash", "Deux vérifications"),

        h(2, "Nettoyer"),
        p("Les images, conteneurs et volumes s'accumulent. Un disque plein sur l'hôte "
          "provoque des erreurs difficiles à interpréter."),
        code("""docker system df              # vue d'ensemble
docker system df -v           # détail par élément

docker container prune        # conteneurs arrêtés
docker image prune            # images sans étiquette
docker image prune -a         # toutes les images non utilisées
docker volume prune           # volumes non utilisés
docker builder prune

# Tout nettoyer sauf les volumes (attention)
docker system prune -af --volumes""", "bash", "Sept opérations de nettoyage"),
        box("attention", "`prune --volumes` détruit des données",
            "Un volume non monté n'est pas forcément inutile : il peut contenir une "
            "base arrêtée. Vérifiez avec `docker volume ls` et sauvegardez avant toute "
            "purge."),
        box("methode", "Inspection d'un conteneur qui ne démarre pas",
            items=["`docker logs` : message d'erreur applicatif.",
                   "`docker inspect --format '{{.State.ExitCode}}'` : code de sortie.",
                   "`docker run --rm -it image sh` : explorer l'image seule.",
                   "Vérifier les variables d'environnement et les volumes montés.",
                   "Vérifier les limites mémoire."]),
    ],
    "keypoints": [
        "Un conteneur est un processus isolé qui partage le noyau de l'hôte.",
        "Une image est immuable et composée de couches.",
        "Le cache de construction dépend de l'ordre des instructions.",
        "`.dockerignore` réduit le contexte et protège les secrets.",
        "Un conteneur s'arrête avec son processus principal.",
        "`--memory` tue, `--cpus` ralentit.",
        "Le code 137 signale souvent un manque de mémoire.",
        "Les volumes peuvent contenir des données : ne pas les purger à l'aveugle.",
    ],
    "bridge": "Les conteneurs fonctionnent. Le chapitre suivant construit des images "
              "réellement reproductibles et sûres.",
    "exercises": [
        ex("Écrire un Dockerfile multi-étapes",
           "Une application front-end doit être construite puis servie par Nginx.",
           ["Séparez dépendances, construction et exécution.",
            "Utilisez une image finale minimale.",
            "Ajoutez une vérification de santé."],
           [("dockerfile", """# syntax=docker/dockerfile:1
FROM node:22-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:1.27-alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
RUN adduser -D -H -u 10001 app 2>/dev/null || true
USER nginx
EXPOSE 80
HEALTHCHECK --interval=30s --timeout=3s CMD wget -qO- http://127.0.0.1/ || exit 1"""),
            "L'image finale ne contient ni Node ni les sources : elle est plus petite et "
            "présente moins de surface d'attaque.",
            "La vérification de santé permet à Docker et aux orchestrateurs de détecter "
            "un conteneur vivant mais incapable de servir."]),
        ex("Diagnostiquer un conteneur arrêté",
           "`docker ps -a` montre un conteneur arrêté immédiatement.",
           ["Consultez le code de sortie.",
            "Lisez les journaux.",
            "Reproduisez en interactif."],
           [("bash", """docker ps -a
docker inspect web --format '{{.State.ExitCode}} {{.State.OOMKilled}}'
docker logs web

# Explorer sans démarrer la commande par défaut
docker run --rm -it --entrypoint sh mon-app:1.0
# puis lancer la commande manuellement pour voir l'erreur"""),
            "Le code 0 avec un arrêt immédiat signifie que le processus principal s'est "
            "terminé normalement : souvent une commande mal formée.",
            "Le code 137 indique un arrêt par le noyau, généralement pour mémoire."],
           level="Diagnostic"),
        ex("Limiter l'empreinte d'un conteneur",
           "Un service consomme trop de mémoire et remplit le disque de journaux.",
           ["Mesurez la consommation.",
            "Fixez des limites.",
            "Configurez la rotation des journaux."],
           [("bash", """docker stats --no-stream
docker update --memory 512m --memory-swap 512m web
docker run -d --log-opt max-size=10m --log-opt max-file=3 mon-app:1.0

# Vérifier après application
docker inspect web --format '{{.HostConfig.Memory}} {{.HostConfig.LogConfig.Config}}'"""),
            "`--memory-swap` égal à `--memory` interdit le recours au swap, ce qui rend "
            "la limite prévisible.",
            "La rotation des journaux est souvent oubliée alors qu'elle remplit le disque "
            "en quelques jours."],
           level="Exploitation"),
    ],
    "quiz": [
        quiz("Qu'est-ce qu'un conteneur ?",
             ["Une machine virtuelle légère", "Un processus isolé partageant le noyau",
              "Une image exécutable", "Un hyperviseur"],
             1,
             "L'isolation repose sur les espaces de noms et les groupes de contrôle."),
        quiz("Pourquoi copier `package.json` avant le code source ?",
             ["Pour la sécurité", "Pour profiter du cache de construction",
              "Pour la lisibilité", "Ce n'est pas utile"],
             1,
             "Les dépendances changent rarement : la couche reste en cache."),
        quiz("Que fait `--memory 512m` en cas de dépassement ?",
             ["Ralentit le conteneur", "Tue le processus", "Écrit un journal", "Redémarre"],
             1,
             "Le noyau termine le processus, ce qui donne un code de sortie 137."),
        quiz("Que signifie le code de sortie 137 ?",
             ["Succès", "Erreur de syntaxe", "Arrêt par le noyau (mémoire)",
              "Port occupé"],
             2,
             "128 + 9 (SIGKILL), fréquemment causé par `OOMKilled`."),
        quiz("À quoi sert `.dockerignore` ?",
             ["À nettoyer les images", "À réduire le contexte de construction",
              "À limiter la mémoire", "À exposer des ports"],
             1,
             "Il évite d'envoyer des fichiers inutiles au démon Docker."),
    ],
}
