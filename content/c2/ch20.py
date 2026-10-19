from bookkit.dsl import (box, code, defn, ex, fig, h, ol, p, quiz, table, ul)

CH = {
    "title": "Docker Compose : applications multi-services",
    "subtitle": "Décrire une application complète dans un fichier versionné, reproductible "
                "sur n'importe quelle machine.",
    "duration": "3 h 15",
    "level": "Intermédiaire",
    "prereq": "chapitre 59",
    "objectives": [
        "Écrire un fichier Compose lisible.",
        "Ordonner le démarrage avec les vérifications de santé.",
        "Gérer profils, variables et fichiers multiples.",
        "Comprendre la reconstruction et la persistance.",
        "Diagnostiquer un service qui ne démarre pas.",
    ],
    "blocks": [
        h(2, "Un fichier, une application"),
        p("Compose décrit des services, des réseaux et des volumes dans un fichier YAML "
          "versionné. Une commande recrée l'ensemble, ce qui rend l'environnement de "
          "développement reproductible."),
        code("""# compose.yaml
services:
  api:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "127.0.0.1:8080:3000"
    environment:
      DATABASE_URL: postgres://app:secret@db:5432/app
      LOG_LEVEL: info
    depends_on:
      db:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "wget", "-qO-", "http://127.0.0.1:3000/health"]
      interval: 10s
      timeout: 3s
      retries: 5

  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: app
      POSTGRES_PASSWORD: secret
      POSTGRES_DB: app
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U app -d app"]
      interval: 5s
      timeout: 3s
      retries: 10

  cache:
    image: redis:7-alpine
    command: ["redis-server", "--save", "", "--appendonly", "no"]

volumes:
  pgdata:""", "yaml", "Une application complète"),
        table(["Clé", "Rôle", "Remarque"],
              [["`services`", "Les processus", "Un service peut avoir plusieurs réplicas"],
               ["`build`", "Construction de l'image", "`context` et `dockerfile`"],
               ["`depends_on`", "Ordre de démarrage", "N'attend pas la disponibilité seule"],
               ["`healthcheck`", "État réel du service", "Utilisé par `condition`"],
               ["`volumes`", "Persistance", "Déclarés en bas"],
               ["`profiles`", "Groupes de services", "Utile en développement"]],
              widths=[3.6, 4.6, 4.6], first_col_bold=True,
              caption="Six clés essentielles"),
        defn("`depends_on` avec condition", "Forme longue qui attend que le service "
                                            "dépendant soit sain, et non seulement créé. "
                                            "Sans `condition`, Compose démarre les "
                                            "conteneurs dans l'ordre sans attendre qu'ils "
                                            "soient prêts."),

        h(2, "Commandes du quotidien"),
        p("Compose se pilote avec une seule commande déclinée en sous-commandes. La "
          "connaissance de cinq d'entre elles couvre presque tout l'usage quotidien."),
        code("""docker compose up -d            # démarrer en arrière-plan
docker compose ps               # état des services
docker compose logs -f api      # journaux d'un service
docker compose exec api sh      # shell dans un service
docker compose down             # arrêter et supprimer

docker compose up -d --build    # reconstruire les images modifiées
docker compose restart api
docker compose down -v          # supprimer aussi les volumes""", "bash",
             "Huit commandes"),
        table(["Commande", "Effet sur les volumes", "Effet sur les images"],
              [["`down`", "Conservés", "Conservées"],
               ["`down -v`", "Supprimés", "Conservées"],
               ["`down --rmi local`", "Conservés", "Images locales supprimées"],
               ["`up --build`", "Conservés", "Reconstruites"]],
              widths=[4.4, 4.6, 4.4], first_col_bold=True,
              caption="Quatre combinaisons à connaître"),
        fig("flow", "Le cycle d'une application Compose",
            ["Écriture du fichier compose.yaml",
             "Construction des images",
             "Création des réseaux et volumes",
             "Démarrage ordonné et vérifications",
             "Exploitation, journaux, mises à jour",
             "Arrêt et nettoyage"],
            height=250),
        box("attention", "`down -v` détruit les données",
            "L'option `-v` supprime les volumes déclarés. Sur un environnement de "
            "développement c'est pratique ; sur un environnement partagé, c'est une perte "
            "de données. Vérifiez toujours la cible avant d'exécuter."),

        h(2, "Surcharges et environnements"),
        p("Un fichier de base se combine avec des fichiers de surcharge. Cette "
          "composition évite de dupliquer la description entre développement et "
          "production."),
        code("""# compose.override.yaml — utilisé automatiquement en local
services:
  api:
    build:
      target: development
    volumes:
      - ./src:/app/src
    environment:
      LOG_LEVEL: debug
    ports:
      - "9229:9229"          # débogueur

# Lancement explicite avec deux fichiers
docker compose -f compose.yaml -f compose.prod.yaml up -d""", "yaml",
             "Deux fichiers, deux usages"),
        code("""# Profils : ne démarrer les outils qu'à la demande
services:
  api:
    # ...
  mailpit:
    image: axllent/mailpit
    profiles: ["dev"]
    ports: ["8025:8025"]

# Démarrage sans les profils
docker compose up -d
# Démarrage avec les outils de développement
docker compose --profile dev up -d""", "yaml", "Un profil d'outils"),
        table(["Fichier", "Rôle", "Versionné"],
              [["`compose.yaml`", "Définition commune", "Oui"],
               ["`compose.override.yaml`", "Surcharge locale", "Oui, mais générique"],
               ["`compose.prod.yaml`", "Production", "Oui"],
               ["`.env`", "Variables locales", "Non"],
               ["`.env.example`", "Modèle documenté", "Oui"]],
              widths=[4.6, 4.4, 4.4], first_col_bold=True,
              caption="Cinq fichiers et leur rôle"),
        code("""# Variables dans le fichier
environment:
  LOG_LEVEL: ${LOG_LEVEL:-info}
  DATABASE_URL: ${DATABASE_URL:?DATABASE_URL requise}

# Interpolation depuis .env
# .env
# LOG_LEVEL=debug
# DATABASE_URL=postgres://app:secret@db:5432/app""", "yaml",
             "Deux notations utiles"),

        h(2, "Construire ou utiliser une image"),
        p("En développement, la construction locale évite de publier une image à chaque "
          "modification. En production, une image publiée et épinglée garantit que "
          "l'artefact testé est celui déployé."),
        code("""# Développement : construire localement
services:
  api:
    build: .
    image: mon-api:dev

# Production : utiliser une image publiée, épinglée
services:
  api:
    image: registry.exemple.fr/equipe/app:1.4.2@sha256:9a8b7c...

# Ne pas mélanger les deux pour un même service
# en production : `build` doit être absent""", "yaml",
             "Deux configurations distinctes"),
        p("Un fichier Compose de production qui contient `build` finit toujours par "
          "déployer une construction locale non testée. Séparez explicitement les "
          "fichiers."),
        code("""# Vérifier la configuration effective avant de démarrer
docker compose config

# Voir la configuration avec les variables résolues
docker compose config --quiet && echo "syntaxe valide"

# Lister les images utilisées
docker compose images""", "bash", "Trois vérifications"),

        h(2, "Diagnostiquer"),
        p("Un service qui ne démarre pas sous Compose a cinq causes fréquentes. La "
          "lecture ordonnée des journaux et de l'état permet de trancher rapidement."),
        table(["Symptôme", "Cause", "Vérification"],
              [["Conteneur `exited (1)`", "Erreur applicative", "`logs`"],
               ["`unhealthy`", "Vérification trop stricte", "`healthcheck`"],
               ["`port is already allocated`", "Port occupé", "`ss -ltnp`"],
               ["`dependency failed`", "`depends_on` impossible", "`ps -a`"],
               ["Données perdues", "Volume mal nommé", "`volumes:`"],
               ["Variables vides", "`.env` absent", "`compose config`"]],
              widths=[4.4, 4.4, 4.4], first_col_bold=True,
              caption="Six symptômes"),
        code("""docker compose ps -a
docker compose logs --tail=50 --no-log-prefix api
docker compose config
docker inspect $(docker compose ps -q api) --format '{{.State.ExitCode}}'""",
             "bash", "Quatre commandes de diagnostic"),
        box("pratique", "La vérification de santé doit être simple",
            "Un `healthcheck` qui interroge toutes les dépendances rend un service "
            "« unhealthy » dès qu'une dépendance secondaire ralentit. Testez le service "
            "lui-même, et distinguez vivacité et capacité."),
        box("methode", "Avant de partager un fichier Compose",
            items=["`docker compose config` passe sans avertissement.",
                   "Aucun secret en clair dans le fichier.",
                   "Volumes nommés pour les données persistantes.",
                   "Vérifications de santé sur les services dépendants.",
                   "Ports publiés uniquement sur `127.0.0.1` en développement."]),
    ],
    "keypoints": [
        "Compose décrit services, réseaux et volumes dans un fichier versionné.",
        "`depends_on` seul n'attend pas que le service soit prêt.",
        "`down -v` supprime les volumes et donc les données.",
        "Les fichiers de surcharge évitent la duplication.",
        "Les profils limitent le démarrage des outils aux besoins.",
        "La production utilise une image épinglée, jamais `build`.",
        "`compose config` valide et révèle les variables résolues.",
        "Un port déjà occupé est une cause fréquente d'échec.",
    ],
    "bridge": "Une machine suffit pour Compose. À l'échelle d'un cluster, il faut un "
              "orchestrateur : Kubernetes.",
    "exercises": [
        ex("Écrire un Compose à trois services",
           "Une API, une base et un cache doivent démarrer ensemble.",
           ["Ordonnez le démarrage.",
            "Ajoutez les vérifications.",
            "Ne publiez que l'API."],
           [("yaml", """services:
  api:
    build: .
    ports: ["127.0.0.1:8080:3000"]
    environment:
      DATABASE_URL: postgres://app:secret@db:5432/app
      REDIS_URL: redis://cache:6379
    depends_on:
      db: { condition: service_healthy }
      cache: { condition: service_started }

  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: app
      POSTGRES_PASSWORD: secret
      POSTGRES_DB: app
    volumes: ["pgdata:/var/lib/postgresql/data"]
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U app -d app"]
      interval: 5s
      retries: 10

  cache:
    image: redis:7-alpine

volumes:
  pgdata:"""),
            "`condition: service_healthy` évite que l'API démarre avant que la base "
            "accepte les connexions.",
            "Le cache n'a pas besoin d'une vérification : Redis démarre assez vite pour "
            "que l'API gère une reconnexion."]),
        ex("Séparer développement et production",
           "Le fichier local monte les sources, la production utilise une image.",
           ["Écrivez la base.",
            "Ajoutez une surcharge de développement.",
            "Ajoutez un fichier de production."],
           [("yaml", """# compose.yaml
services:
  api:
    image: registry.exemple.fr/equipe/app:1.4.2
    environment:
      LOG_LEVEL: ${LOG_LEVEL:-info}

# compose.override.yaml (développement, automatique)
services:
  api:
    build: .
    image: mon-api:dev
    volumes: ["./src:/app/src"]
    environment:
      LOG_LEVEL: debug
    command: ["npm", "run", "dev"]

# Production
docker compose -f compose.yaml up -d"""),
            "En développement, Compose applique automatiquement `compose.override.yaml`.",
            "En production, on fournit seulement le fichier de base : l'image épinglée "
            "est utilisée telle quelle."]),
        ex("Diagnostiquer un service unhealthy",
           "L'API est `unhealthy` alors que le conteneur tourne.",
           ["Lisez la sortie de la vérification.",
            "Testez manuellement.",
            "Ajustez la vérification."],
           [("bash", """docker inspect $(docker compose ps -q api) \\
  --format '{{json .State.Health}}'

docker compose exec api wget -qO- http://127.0.0.1:3000/health
docker compose logs api | tail -30"""),
            "La sortie de la vérification est conservée dans l'état de santé : elle "
            "indique souvent un `connection refused` immédiat.",
            "Un délai de démarrage insuffisant se corrige avec `start_period`, pas en "
            "allongeant indéfiniment les intervalles."],
           level="Diagnostic"),
    ],
    "quiz": [
        quiz("Que fait `depends_on` sans condition ?",
             ["Attend la santé du service", "Démarre dans l'ordre sans attendre",
              "Crée un réseau", "Publie un port"],
             1,
             "Sans `condition`, seul l'ordre de démarrage est respecté."),
        quiz("Quelle commande supprime les volumes ?",
             ["`down`", "`down -v`", "`stop`", "`restart`"],
             1,
             "`-v` supprime les volumes déclarés."),
        quiz("Quel fichier est appliqué automatiquement en développement ?",
             ["`compose.prod.yaml`", "`compose.override.yaml`", "`.env`", "`Dockerfile`"],
             1,
             "Compose combine `compose.yaml` et `compose.override.yaml` par défaut."),
        quiz("Pourquoi ne pas laisser `build` dans un fichier de production ?",
             ["C'est plus lent", "Cela déploie une construction locale non testée",
              "Cela casse le réseau", "C'est obsolète"],
             1,
             "La production doit utiliser l'artefact exact qui a été testé."),
        quiz("Comment vérifier la configuration résolue ?",
             ["`docker compose ps`", "`docker compose config`", "`docker compose logs`", "`docker compose top`"],
             1,
             "`config` affiche la configuration effective, variables comprises."),
    ],
}
