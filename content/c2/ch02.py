from bookkit.dsl import (box, code, defn, ex, fig, h, ol, p, quiz, table, ul)

CH = {
    "title": "Linux : système de fichiers, processus et droits",
    "subtitle": "Le modèle mental d'un système Unix, sans lequel chaque commande devient "
                "une incantation.",
    "duration": "3 h 00",
    "level": "Débutant",
    "prereq": "chapitre 41",
    "objectives": [
        "Se repérer dans l'arborescence normalisée.",
        "Identifier et gérer les processus.",
        "Comprendre les droits et les appliquer correctement.",
        "Monter et vérifier un espace disque.",
        "Lire les journaux du système.",
    ],
    "blocks": [
        h(2, "Tout est fichier"),
        p("Unix expose matériel, périphériques et processus sous forme de fichiers ou de "
          "flux. Cette uniformité explique la puissance des outils en ligne de commande : "
          "ils lisent et écrivent des flux, quel que soit leur producteur."),
        code("""/dev/null      # puits : tout ce qu'on y écrit disparaît
/dev/zero      # source infinie d'octets nuls
/proc/cpuinfo  # informations matérielles, générées à la volée
/proc/1234/fd/1 # sortie standard du processus 1234""", "text",
             "Quatre fichiers qui ne sont pas des fichiers"),
        defn("Inode", "Structure du système de fichiers qui décrit un fichier : droits, "
                      "propriétaire, taille, dates, blocs occupés. Le nom du fichier "
                      "n'est qu'une entrée d'un répertoire qui pointe vers un inode."),
        code("""stat rapport.txt
#   File: rapport.txt
#   Size: 1024       Blocks: 8          IO Block: 4096   regular file
# Access: (0644/-rw-r--r--)  Uid: ( 1000/  alice)   Gid: ( 1000/  alice)""",
             "bash", "Un inode observé"),

        h(2, "L'arborescence normalisée"),
        p("La hiérarchie est standardisée par le FHS (Filesystem Hierarchy Standard). "
          "Savoir où chercher fait gagner un temps considérable."),
        table(["Chemin", "Contenu", "Remarque"],
              [["`/etc`", "Configuration", "Fichiers texte, versionnables"],
               ["`/var`", "Données variables", "Journaux, bases, caches"],
               ["`/usr`", "Programmes et bibliothèques", "Lecture seule en usage"],
               ["`/home`", "Répertoires personnels", "Données des utilisateurs"],
               ["`/tmp`", "Fichiers temporaires", "Effacé au redémarrage"],
               ["`/opt`", "Logiciels tiers", "Installations autonomes"],
               ["`/proc`", "État du noyau", "Système virtuel"]],
              widths=[2.6, 4.8, 5.0], first_col_bold=True,
              caption="Sept répertoires et leur rôle"),
        code("""# Se repérer
pwd                        # répertoire courant
ls -lah                    # détails, tailles lisibles, fichiers cachés
tree -L 2 /etc             # arborescence sur deux niveaux

# Chercher
find /var/log -name "*.log" -mtime -1     # modifiés depuis 24 h
find . -type f -size +100M                # gros fichiers
locate nginx.conf                         # index rapide (updatedb)""", "bash",
             "Six commandes de repérage"),
        box("attention", "L'espace dans les noms de fichiers",
            "`rm rapport final.txt` supprime deux fichiers. Citez toujours les chemins : "
            "`rm \"rapport final.txt\"`. Préférez des noms sans espaces ni accents dans "
            "les scripts."),

        h(2, "Les processus"),
        p("Un processus est un programme en cours d'exécution, identifié par un PID, "
          "avec un parent, un état et des ressources. Tout descend du processus 1, "
          "lancé par le noyau."),
        fig("tree", "La hiérarchie des processus",
            ("systemd (PID 1)", [("sshd", ["bash", "vim"]),
                                 ("nginx", ["worker 1", "worker 2"]),
                                 ("cron", ["tâche 1"])]),
            height=225),
        code("""ps aux                     # tous les processus
ps -eo pid,ppid,stat,pcpu,pmem,cmd --sort=-pcpu | head
top -b -n 1                # instantané
pgrep -af nginx            # chercher par nom
pstree -p                  # arborescence

kill 1234                  # SIGTERM : demande l'arrêt
kill -9 1234               # SIGKILL : tue sans négociation
kill -HUP 1234             # rechargement de configuration""", "bash",
             "Sept commandes de processus"),
        table(["Signal", "Numéro", "Effet", "Usage"],
              [["`SIGTERM`", "15", "Demande d'arrêt propre", "Par défaut"],
               ["`SIGKILL`", "9", "Arrêt immédiat, non capturable", "Dernier recours"],
               ["`SIGHUP`", "1", "Rechargement de configuration", "Nginx, sshd"],
               ["`SIGINT`", "2", "Interruption (Ctrl+C)", "Terminal"],
               ["`SIGSTOP`", "19", "Suspension", "Diagnostic"]],
              widths=[2.8, 2.4, 5.0, 3.4], first_col_bold=True,
              caption="Cinq signaux et leur usage"),
        box("pratique", "Arrêter avant de tuer",
            "`SIGTERM` laisse au programme le temps de fermer ses fichiers et de finir "
            "ses requêtes. `kill -9` interrompt tout : réservé aux processus bloqués, "
            "il peut laisser des verrous et des fichiers corrompus."),

        h(2, "Droits et propriété"),
        p("Chaque fichier possède un propriétaire, un groupe et trois jeux de droits : "
          "lecture, écriture, exécution. Les droits sont vérifiés dans l'ordre "
          "propriétaire, groupe, autres."),
        code("""-rw-r--r--  1 alice devs  1024 Mar 14 10:02 notes.txt
drwxr-xr-x  2 alice devs  4096 Mar 14 10:02 documents
lrwxrwxrwx  1 alice devs     8 Mar 14 10:02 lien -> notes.txt

# Type | propriétaire | groupe | autres
#  -   |   rw-        |  r--   |  r--""", "text", "Une ligne de `ls -l` décodée"),
        table(["Droit", "Fichier", "Répertoire"],
              [["`r`", "Lire le contenu", "Lister les entrées"],
               ["`w`", "Modifier le contenu", "Créer, renommer, supprimer"],
               ["`x`", "Exécuter", "Traverser (entrer dans)"]],
              widths=[2.2, 5.2, 5.4], first_col_bold=True,
              caption="Trois droits, deux significations"),
        code("""chmod 644 fichier      # rw-r--r--
chmod 755 script.sh    # rwxr-xr-x
chmod u+x script.sh    # ajoute l'exécution au propriétaire
chmod g-w fichier      # retire l'écriture au groupe

chown alice:devs fichier
chgrp devs fichier
umask                  # droits retirés à la création (0022)""", "bash",
             "Six commandes de droits"),
        code("""# Bits spéciaux
chmod 4755 programme   # setuid : s'exécute avec les droits du propriétaire
chmod 2775 dossier     # setgid : les nouveaux fichiers héritent du groupe
chmod 1777 /tmp        # sticky : seul le propriétaire peut supprimer

# Vérifier avant d'appliquer à tout un arbre
find /var/www -type f -exec chmod 640 {} \\;
find /var/www -type d -exec chmod 750 {} \\;""", "bash",
             "Trois bits à connaître, deux vérifications"),
        box("attention", "Ne jamais faire `chmod -R 777`",
            "Ce réflexe ouvre tous les fichiers à tous les utilisateurs et masque un "
            "problème de propriété. Sur un serveur, il transforme une erreur de "
            "configuration en faille de sécurité."),

        h(2, "Disques et systèmes de fichiers"),
        p("Un espace saturé est l'une des causes d'incident les plus fréquentes et les "
          "plus faciles à prévenir. Quatre commandes suffisent au diagnostic."),
        code("""df -h                      # occupation par système de fichiers
du -sh /var/* | sort -h    # répartition dans /var
lsblk                      # périphériques et points de montage
findmnt                    # montages actuels
ncdu /var                  # explorateur interactif""", "bash",
             "Cinq commandes de diagnostic disque"),
        code("""# Monter un volume
mkfs.ext4 /dev/sdb1
mount /dev/sdb1 /mnt/donnees

# Rendre le montage persistant (vérifier avec mount -a)
echo "UUID=$(blkid -s UUID -o value /dev/sdb1) /mnt/donnees ext4 defaults 0 2" \\
  >> /etc/fstab

# Tester sans redémarrer
mount -a""", "bash", "Un montage persistant"),
        p("Un inode peut être épuisé alors que l'espace disque reste disponible : des "
          "millions de petits fichiers suffisent. `df -i` révèle ce cas."),

        h(2, "Journaux"),
        p("`systemd-journald` centralise les journaux des services ; `rsyslog` écrit "
          "dans `/var/log`. Les deux se complètent."),
        code("""journalctl -u nginx --since "1 hour ago"
journalctl -p err -b            # erreurs depuis le démarrage
journalctl -f                   # suivi en direct
journalctl --disk-usage
journalctl --vacuum-time=14d    # purge

tail -f /var/log/auth.log
grep -i "failed" /var/log/auth.log | tail -20""", "bash",
             "Six commandes de journaux"),
        defn("Rotation", "Archivage et compression périodiques des journaux pour limiter "
                         "leur taille. `logrotate` applique une politique par service : "
                         "taille, fréquence, nombre d'archives conservées."),
        box("methode", "Diagnostic d'un service qui ne démarre pas",
            items=["`systemctl status service` : état et dernier message.",
                   "`journalctl -u service -n 50` : contexte complet.",
                   "Vérifier la configuration : `nginx -t`, `sshd -t`.",
                   "Vérifier les ports occupés : `ss -ltnp`.",
                   "Vérifier les droits du répertoire de travail."]),
    ],
    "keypoints": [
        "Unix expose beaucoup de ressources sous forme de fichiers et de flux.",
        "Le FHS normalise l'emplacement des fichiers.",
        "Un processus a un identifiant, un parent et un état.",
        "`SIGTERM` d'abord, `SIGKILL` en dernier recours.",
        "Les droits se lisent propriétaire, groupe, autres.",
        "`777` masque un problème de propriété et crée une faille.",
        "Un disque peut être saturé en espace ou en inodes.",
        "`journalctl` est le point d'entrée des journaux modernes.",
    ],
    "bridge": "Le système est compris. Le chapitre suivant le met en mouvement : le "
              "terminal et les commandes du quotidien.",
    "exercises": [
        ex("Diagnostiquer un disque plein",
           "`df -h` indique 100 % sur `/var` ; `du` ne trouve rien.",
           ["Vérifiez les inodes.",
            "Cherchez les fichiers supprimés encore ouverts.",
            "Corrigez et prévenez."],
           [("code", """df -h /var          # espace
df -i /var          # inodes

# Fichiers supprimés mais toujours ouverts par un processus
lsof +L1 | head
# Redémarrer le service concerné libère l'espace

# Si les inodes sont saturés : beaucoup de petits fichiers
find /var -xdev -type f | wc -l
find /var -xdev -type f -printf "%h\\n" | sort | uniq -c | sort -rn | head"""),
            "Un fichier supprimé mais encore ouvert continue d'occuper son inode et ses "
            "blocs : l'espace n'est rendu qu'à la fermeture.",
            "La saturation en inodes vient souvent d'un cache de sessions ou de "
            "courriels non purgé."],
           level="Diagnostic"),
        ex("Créer un utilisateur de service",
           "Un service doit tourner sans privilèges avec son propre répertoire.",
           ["Utilisateur sans shell de connexion.",
            "Répertoire de données accessible uniquement à lui.",
            "Unité systemd associée."],
           [("code", """useradd --system --no-create-home --shell /usr/sbin/nologin app
install -d -o app -g app -m 750 /var/lib/app

# /etc/systemd/system/app.service
[Unit]
Description=Application
After=network.target

[Service]
User=app
Group=app
WorkingDirectory=/var/lib/app
ExecStart=/opt/app/bin/serveur
Restart=on-failure

[Install]
WantedBy=multi-user.target"""),
            "Le compte système n'a pas de shell : une compromission ne donne pas "
            "d'accès interactif.",
            "`Restart=on-failure` couvre les arrêts anormaux, pas les arrêts volontaires."]),
        ex("Analyser une connexion refusée",
           "Le service écoute mais la connexion échoue.",
           ["Vérifiez l'écoute réelle.",
            "Vérifiez le pare-feu local.",
            "Vérifiez les journaux du service."],
           [("code", """ss -ltnp | grep :8080        # écoute sur 127.0.0.1 ou 0.0.0.0 ?
ss -lx | grep app             # sockets Unix

iptables -L -n -v             # règles IPv4
nft list ruleset              # nftables

journalctl -u app -n 30 --no-pager"""),
            "Une écoute sur `127.0.0.1` n'est joignable que depuis la machine : c'est "
            "la cause la plus fréquente d'un service « qui ne répond pas ».",
            "Le pare-feu et la configuration du service sont deux couches distinctes : "
            "les vérifier séparément évite de corriger au hasard."],
           level="Diagnostic"),
    ],
    "quiz": [
        quiz("Où se trouvent les fichiers de configuration d'un service ?",
             ["`/var`", "`/etc`", "`/usr`", "`/tmp`"],
             1,
             "`/etc` contient la configuration du système et des services."),
        quiz("Quel signal demande un arrêt propre ?",
             ["`SIGKILL`", "`SIGTERM`", "`SIGSTOP`", "`SIGHUP`"],
             1,
             "`SIGTERM` peut être capté par le programme pour fermer proprement."),
        quiz("Que signifie `chmod 755` pour un répertoire ?",
             ["Personne ne peut entrer", "Le propriétaire écrit, les autres lisent et traversent",
              "Tout le monde peut écrire", "Le répertoire est masqué"],
             1,
             "`rwxr-xr-x` : le propriétaire modifie, le groupe et les autres lisent et "
             "traversent."),
        quiz("Pourquoi `chmod -R 777` est-il une mauvaise pratique ?",
             ["C'est lent", "Il ouvre les fichiers à tous et masque un problème de droits",
              "Il supprime les fichiers", "Il ne fonctionne pas"],
             1,
             "Tous les utilisateurs peuvent alors lire et modifier les données."),
        quiz("Quelle commande montre les journaux d'un service systemd ?",
             ["`dmesg`", "`journalctl -u service`", "`tail /etc/log`", "`systemctl logs`"],
             1,
             "`journalctl -u` filtre les entrées d'une unité."),
    ],
}
