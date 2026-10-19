from bookkit.dsl import (box, code, defn, ex, fig, h, ol, p, quiz, table, ul)

CH = {
    "title": "Réseaux et volumes Docker",
    "subtitle": "Relier des conteneurs entre eux et conserver des données hors du cycle "
                "de vie d'un conteneur.",
    "duration": "3 h 00",
    "level": "Intermédiaire",
    "prereq": "chapitre 58",
    "objectives": [
        "Choisir un pilote réseau adapté.",
        "Résoudre des conteneurs par leur nom.",
        "Distinguer volume, montage de bind et tmpfs.",
        "Sauvegarder et restaurer un volume.",
        "Diagnostiquer un conteneur qui ne joint pas un autre.",
    ],
    "blocks": [
        h(2, "Cinq pilotes réseau"),
        p("Docker crée un réseau par défaut pour chaque projet, mais les pilotes "
          "intégrés couvrent des besoins distincts. Le réseau `bridge` par défaut, "
          "lui, n'offre pas la résolution par nom : c'est un piège classique."),
        table(["Pilote", "Portée", "Résolution DNS", "Usage"],
              [["`bridge`", "Hôte unique", "Oui, sur un réseau créé", "Défaut"],
               ["`host`", "Hôte unique", "Non (réseau de l'hôte)", "Performance"],
               ["`none`", "Aucun réseau", "Non", "Isolation totale"],
               ["`overlay`", "Multi-hôtes", "Oui", "Swarm"],
               ["`macvlan`", "Réseau physique", "Selon le réseau", "IP dans le LAN"]],
              widths=[3.0, 3.6, 3.2, 4.2], first_col_bold=True,
              caption="Cinq pilotes réseau"),
        code("""# Créer un réseau dédié
docker network create --driver bridge app-net
docker network inspect app-net

# Connecter deux conteneurs
docker run -d --name db  --network app-net postgres:16-alpine
docker run -d --name api --network app-net -p 8080:3000 mon-api:1.0

# Depuis api, la base est joignable par son nom
docker exec api getent hosts db
# 172.20.0.2      db""", "bash", "Quatre commandes"),
        defn("Résolution par nom", "Sur un réseau défini par l'utilisateur, Docker "
                                   "fournit un DNS interne : le nom du conteneur (ou son "
                                   "alias réseau) résout vers son adresse. C'est la base "
                                   "du service discovery local."),
        code("""# Vérifier la connectivité
docker exec api sh -c "wget -qO- http://db:5432 || true"

# Adresse IP d'un conteneur
docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' db

# Ne pas dépendre de l'IP : utiliser le nom
# Sur le réseau bridge par défaut, la résolution par nom ne fonctionne pas""",
             "bash", "Trois vérifications"),
        box("attention", "Le réseau `bridge` par défaut ne résout pas les noms",
            "Sans `--network` explicite, un conteneur obtient une adresse mais ne peut "
            "pas joindre un autre conteneur par son nom. Créez toujours un réseau "
            "dédié : c'est une ligne, et cela résout le problème."),

        h(2, "Exposer, publier, exposer entre conteneurs"),
        p("Trois notions sont souvent confondues : publier un port vers l'hôte, exposer "
          "un port aux autres conteneurs du réseau, et écouter sur une interface donnée."),
        table(["Notion", "Syntaxe", "Portée"],
              [["Publication", "`-p 8080:80`", "Hôte, éventuellement toutes les interfaces"],
               ["Publication locale", "`-p 127.0.0.1:8080:80`", "Hôte uniquement"],
               ["Exposition documentaire", "`EXPOSE 80`", "Aucun effet réseau"],
               ["Accès entre conteneurs", "Nom + port interne", "Réseau Docker"]],
              widths=[5.0, 5.0, 4.0], first_col_bold=True,
              caption="Quatre notions de port"),
        code("""# Publier uniquement sur l'interface locale
docker run -d -p 127.0.0.1:5432:5432 --name db postgres:16-alpine

# Publier sur toutes les interfaces (attention aux pare-feux)
docker run -d -p 0.0.0.0:8080:80 nginx:1.27-alpine

# Ouvrir un shell sans exposer de port
docker exec -it api sh""", "bash", "Trois exemples"),
        box("pratique", "Publier seulement ce qui doit l'être",
            "Une base de données n'a aucune raison de publier un port sur l'hôte : les "
            "autres conteneurs la joignent par le réseau Docker. `-p 5432:5432` sur "
            "`0.0.0.0` expose la base à tout le réseau."),

        h(2, "Volumes, bind mounts et tmpfs"),
        p("Un conteneur est éphémère : supprimer le conteneur supprime sa couche "
          "d'écriture. Pour conserver des données, il faut un espace extérieur."),
        table(["Type", "Emplacement", "Géré par", "Usage"],
              [["Volume nommé", "`/var/lib/docker/volumes`", "Docker", "Données persistantes"],
               ["Bind mount", "Chemin de l'hôte", "Vous", "Développement, configuration"],
               ["tmpfs", "Mémoire", "Noyau", "Fichiers temporaires sensibles"]],
              widths=[3.4, 5.0, 3.0, 4.0], first_col_bold=True,
              caption="Trois types de montage"),
        code("""# Volume nommé
docker volume create pgdata
docker run -d --name db -v pgdata:/var/lib/postgresql/data postgres:16-alpine

# Bind mount en lecture seule
docker run -d -v /etc/app/config.yml:/app/config.yml:ro mon-app:1.0

# Bind mount de développement (code source)
docker run -d -v "$PWD/src:/app/src" -p 3000:3000 node:22-alpine npm run dev

# tmpfs
docker run -d --tmpfs /run:rw,size=16m mon-app:1.0""", "bash",
             "Quatre montages"),
        defn("Volume nommé", "Espace de stockage géré par Docker, identifié par un nom et "
                             "indépendant du conteneur. C'est le choix recommandé pour les "
                             "données de production."),
        code("""# Lister et inspecter
docker volume ls
docker volume inspect pgdata

# Sauvegarder un volume dans une archive
docker run --rm \\
  -v pgdata:/data:ro \\
  -v "$PWD:/sauvegarde" \\
  alpine tar -czf /sauvegarde/pgdata-$(date +%F).tar.gz -C /data .

# Restaurer
docker run --rm \\
  -v pgdata:/data \\
  -v "$PWD:/sauvegarde:ro" \\
  alpine sh -c "cd /data && tar -xzf /sauvegarde/pgdata-2026-10-19.tar.gz\"""",
             "bash", "Trois commandes de sauvegarde"),
        box("attention", "Les droits du volume comptent",
            "Un conteneur qui tourne avec l'utilisateur 10001 ne peut pas écrire dans un "
            "volume appartenant à root. Corrigez la propriété avec "
            "`chown -R 10001:10001` depuis un conteneur temporaire, ou utilisez "
            "`--user` de façon cohérente."),

        h(2, "Diagnostiquer"),
        p("Un conteneur qui ne joint pas un autre a quatre causes principales : pas le "
          "même réseau, un nom mal orthographié, un port interne erroné, ou un service "
          "qui écoute sur l'interface locale du conteneur."),
        table(["Symptôme", "Cause", "Vérification"],
              [["`bad address`", "Nom non résolu", "Même réseau ?"],
               ["`connection refused`", "Port fermé", "`ss -ltnp` dans le conteneur"],
               ["`connection timeout`", "Pare-feu ou mauvais réseau", "`docker network inspect`"],
               ["Résolution vers une IP obsolète", "Conteneur recréé", "Utiliser le nom"]],
              widths=[5.0, 4.4, 4.6], first_col_bold=True,
              caption="Quatre symptômes"),
        code("""# Le conteneur écoute-t-il sur toutes les interfaces ?
docker exec api ss -ltnp
# LISTEN 0.0.0.0:3000  ← joignable
# LISTEN 127.0.0.1:3000 ← non joignable depuis un autre conteneur

# Les deux conteneurs partagent-ils un réseau ?
docker inspect -f '{{json .NetworkSettings.Networks}}' api
docker inspect -f '{{json .NetworkSettings.Networks}}' db""", "bash",
             "Deux vérifications décisives"),
        defn("Écoute sur `127.0.0.1`", "Un service lié à l'adresse de boucle n'accepte que "
                                      "les connexions provenant de son propre espace de "
                                      "noms réseau. C'est la cause la plus fréquente d'un "
                                      "« conteneur injoignable » alors qu'il tourne."),
        box("methode", "Diagnostic de connectivité entre conteneurs",
            items=["`docker network inspect` : les deux sont-ils connectés ?",
                   "`docker exec … getent hosts nom` : la résolution fonctionne-t-elle ?",
                   "`ss -ltnp` dans la cible : l'écoute est-elle sur `0.0.0.0` ?",
                   "Tester avec `nc -zv` depuis le conteneur source."]),
    ],
    "keypoints": [
        "Un réseau créé par l'utilisateur fournit la résolution par nom.",
        "Le réseau `bridge` par défaut ne résout pas les noms.",
        "Publier un port l'expose sur l'hôte, `EXPOSE` ne fait rien.",
        "Une base n'a pas besoin d'être publiée sur l'hôte.",
        "Un volume nommé survit à la suppression du conteneur.",
        "Un bind mount suit les modifications du code, un volume non.",
        "Les droits du volume doivent correspondre à l'utilisateur du conteneur.",
        "Un service lié à `127.0.0.1` est injoignable depuis un autre conteneur.",
    ],
    "bridge": "Les conteneurs communiquent et persistent. Le chapitre suivant assemble "
              "plusieurs services en une application cohérente.",
    "exercises": [
        ex("Relier une application et sa base",
           "L'API doit joindre PostgreSQL par son nom.",
           ["Créez un réseau dédié.",
            "Nommez les conteneurs.",
            "Vérifiez la résolution."],
           [("bash", """docker network create app-net

docker run -d --name db --network app-net \\
  -e POSTGRES_PASSWORD=secret -v pgdata:/var/lib/postgresql/data \\
  postgres:16-alpine

docker run -d --name api --network app-net -p 8080:3000 \\
  -e DATABASE_URL=postgres://postgres:secret@db:5432/postgres \\
  mon-api:1.0

docker exec api getent hosts db
docker logs api"""),
            "La chaîne de connexion utilise `db` comme nom d'hôte : c'est le DNS Docker "
            "qui résout.",
            "Aucun port de la base n'est publié sur l'hôte : elle n'est joignable que "
            "par le réseau Docker."]),
        ex("Sauvegarder et restaurer un volume",
           "Les données de la base doivent survivre à une perte de conteneur.",
           ["Sauvegardez vers une archive.",
            "Supprimez le conteneur.",
            "Restaurez dans un volume neuf."],
           [("bash", """# Sauvegarde
docker run --rm -v pgdata:/data:ro -v "$PWD:/s:rw" alpine \\
  tar -czf /s/pgdata.tgz -C /data .

# Perte du conteneur
docker rm -f db

# Restauration
docker volume create pgdata2
docker run --rm -v pgdata2:/data -v "$PWD:/s:ro" alpine \\
  sh -c "cd /data && tar -xzf /s/pgdata.tgz"
docker run -d --name db --network app-net -v pgdata2:/var/lib/postgresql/data postgres:16-alpine"""),
            "La sauvegarde s'effectue depuis un conteneur temporaire : elle ne dépend pas "
            "de l'état du service.",
            "Restaurer dans un volume neuf permet de comparer avant de basculer."]),
        ex("Diagnostiquer un conteneur injoignable",
           "L'API répond, mais elle ne joint pas la base.",
           ["Vérifiez le réseau.",
            "Vérifiez l'écoute.",
            "Vérifiez le nom."],
           [("bash", """docker inspect -f '{{json .NetworkSettings.Networks}}' api db
docker exec api getent hosts db
docker exec db ss -ltnp
docker exec api nc -zv db 5432

# Cause fréquente : postgres écoute sur 127.0.0.1
# Solution : configurer listen_addresses = '*'"""),
            "PostgreSQL écoute par défaut sur toutes les interfaces dans l'image "
            "officielle, mais une configuration personnalisée peut le restreindre.",
            "`nc -zv` distingue un refus (service absent) d'un timeout (réseau ou "
            "pare-feu)."],
           level="Diagnostic"),
    ],
    "quiz": [
        quiz("Quel pilote réseau offre la résolution par nom ?",
             ["`host`", "`none`", "`bridge` sur un réseau créé", "`macvlan` seul"],
             2,
             "Un réseau bridge défini par l'utilisateur fournit un DNS interne."),
        quiz("Que fait `-p 8080:80` ?",
             ["Expose le port 8080 du conteneur", "Publie le port 80 du conteneur sur 8080 de l'hôte",
              "Ouvre un tunnel", "Crée un volume"],
             1,
             "La syntaxe est `hôte:conteneur`."),
        quiz("Quel montage survit à la suppression du conteneur ?",
             ["La couche d'écriture", "Un volume nommé", "`tmpfs`", "Aucun"],
             1,
             "Le volume est indépendant du cycle de vie du conteneur."),
        quiz("Pourquoi un service lié à `127.0.0.1` est-il injoignable ?",
             ["Il est arrêté", "Il n'accepte que les connexions locales à son espace réseau",
              "Le port est réservé", "Docker le bloque"],
             1,
             "L'adresse de boucle n'est pas accessible depuis un autre conteneur."),
        quiz("Quel type de montage est en mémoire ?",
             ["Volume nommé", "Bind mount", "`tmpfs`", "Overlay"],
             2,
             "`tmpfs` réside en mémoire et disparaît à l'arrêt."),
    ],
}
