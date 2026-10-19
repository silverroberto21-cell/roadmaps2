from bookkit.dsl import (box, code, defn, ex, fig, h, ol, p, quiz, table, ul)

CH = {
    "title": "SSH : accès distant et tunnels",
    "subtitle": "Administrer des machines sans mot de passe, automatiser des accès et "
                "traverser des réseaux fermés.",
    "duration": "3 h 00",
    "level": "Intermédiaire",
    "prereq": "chapitre 53",
    "objectives": [
        "Configurer une authentification par clé.",
        "Utiliser un fichier `~/.ssh/config` efficace.",
        "Transférer des fichiers et des ports.",
        "Durcir un serveur SSH.",
        "Diagnostiquer un refus de connexion.",
    ],
    "blocks": [
        h(2, "Authentification par clé"),
        p("Une paire de clés remplace un mot de passe : la clé privée reste sur le "
          "poste, la clé publique est déposée sur le serveur. Le serveur lance un défi "
          "que seul le détenteur de la clé privée peut relever."),
        code("""# Générer une paire Ed25519, recommandée
ssh-keygen -t ed25519 -C "alice@portable" -f ~/.ssh/id_ed25519

# Déposer la clé publique (méthode simple)
ssh-copy-id -i ~/.ssh/id_ed25519.pub deploy@serveur

# Vérifier les droits : SSH refuse les clés trop permissives
chmod 700 ~/.ssh
chmod 600 ~/.ssh/id_ed25519 ~/.ssh/authorized_keys
chmod 644 ~/.ssh/id_ed25519.pub""", "bash", "Quatre commandes, un accès"),
        table(["Type de clé", "Longueur", "Recommandation"],
              [["Ed25519", "256 bits", "Par défaut, rapide et sûre"],
               ["RSA", "≥ 3072 bits", "Compatibilité ancienne"],
               ["ECDSA", "256–521 bits", "Correct, moins courant"],
               ["DSA", "1024 bits", "À ne plus utiliser"]],
              widths=[4.0, 4.2, 5.0], first_col_bold=True,
              caption="Quatre types de clés"),
        defn("Agent SSH", "Programme qui conserve les clés déverrouillées en mémoire pour "
                          "la session. Il évite de ressaisir la phrase secrète à chaque "
                          "connexion, sans jamais écrire la clé en clair sur disque."),
        code("""# Démarrer l'agent et y ajouter une clé
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519
ssh-add -l

# Durée de vie limitée, utile sur une machine partagée
ssh-add -t 8h ~/.ssh/id_ed25519

# Sur macOS, l'agent est lié au trousseau
ssh-add --apple-use-keychain ~/.ssh/id_ed25519""", "bash",
             "Quatre commandes d'agent"),

        h(2, "Fichier de configuration"),
        p("`~/.ssh/config` évite de retenir des options par cœur. Il autorise aussi des "
          "raccourcis et des configurations par hôte, ce qui rend les scripts lisibles."),
        code("""Host *
    AddKeysToAgent yes
    ServerAliveInterval 60
    ServerAliveCountMax 3
    HashKnownHosts yes

Host prod
    HostName 203.0.113.10
    User deploy
    IdentityFile ~/.ssh/id_ed25519_prod
    Port 2222

Host *.interne
    User admin
    ProxyJump bastion

Host bastion
    HostName bastion.exemple.fr
    User jump
    IdentityFile ~/.ssh/id_ed25519""", "text", "Une configuration lisible"),
        table(["Directive", "Effet", "Usage"],
              [["`HostName`", "Adresse réelle", "Alias court"],
               ["`User`", "Utilisateur", "Éviter `user@host`"],
               ["`IdentityFile`", "Clé à utiliser", "Une clé par environnement"],
               ["`ProxyJump`", "Passerelle intermédiaire", "Réseau cloisonné"],
               ["`LocalForward`", "Tunnel local", "Base non exposée"],
               ["`ServerAliveInterval`", "Maintien de session", "Connexions instables"]],
              widths=[4.4, 4.4, 4.0], first_col_bold=True,
              caption="Six directives utiles"),
        code("""# Utilisation des alias
ssh prod
scp fichier.tar.gz prod:/tmp/
rsync -avz --progress ./site/ prod:/var/www/site/

# Exécuter une commande sans session interactive
ssh prod "systemctl status nginx --no-pager\"""", "bash",
             "Quatre usages de l'alias"),

        h(2, "Tunnels et transferts"),
        p("Un tunnel SSH transporte un autre protocole dans une connexion chiffrée. "
          "C'est un moyen simple d'accéder à un service non exposé, sans ouvrir de port "
          "supplémentaire."),
        fig("columns", "Trois types de transfert",
            [("LOCAL (-L)", ["Port local → distant", "Accéder à une base interne"]),
             ("DISTANT (-R)", ["Port distant → local", "Exposer un service de test"]),
             ("DYNAMIQUE (-D)", ["Proxy SOCKS", "Navigation via le serveur"])],
            height=200),
        code("""# Local : le port 5432 du serveur devient localhost:15432
ssh -L 15432:localhost:5432 prod

# Distant : le port 8080 du serveur renvoie vers le poste local
ssh -R 8080:localhost:3000 prod

# Proxy SOCKS sur le port local 1080
ssh -D 1080 prod

# Dans la configuration, pour ne pas y penser
Host prod-db
    HostName 203.0.113.10
    User deploy
    LocalForward 15432 localhost:5432""", "bash", "Quatre tunnels"),
        box("attention", "Un tunnel distant ouvre une porte",
            "`-R` expose un service local sur la machine distante. Par défaut, il "
            "n'écoute que sur `localhost` distant, ce qui est le comportement sûr. "
            "N'utilisez pas `GatewayPorts yes` sans comprendre la conséquence."),
        code("""# Transfert de fichiers
scp -r dossier/ prod:/tmp/
rsync -avz --delete --exclude ".git" ./site/ prod:/var/www/site/

# Mode SFTP interactif
sftp prod""", "bash", "Trois transferts"),
        defn("ProxyJump", "Mécanisme qui ouvre une connexion SSH à travers un hôte "
                          "intermédiaire, sans tunnel manuel. Il remplace l'ancien "
                          "`ProxyCommand` dans la plupart des cas."),

        h(2, "Durcir le serveur"),
        p("Un serveur SSH exposé subit des tentatives automatisées en permanence. La "
          "configuration par défaut est raisonnable, mais quelques directives la "
          "renforcent nettement."),
        code("""# /etc/ssh/sshd_config.d/10-durcissement.conf
PermitRootLogin no
PasswordAuthentication no
KbdInteractiveAuthentication no
PubkeyAuthentication yes
AllowUsers deploy admin
MaxAuthTries 3
LoginGraceTime 20
X11Forwarding no
AllowTcpForwarding no
ClientAliveInterval 300
ClientAliveCountMax 2""", "text", "Onze directives de durcissement"),
        code("""# Valider avant de recharger, toujours
sshd -t
systemctl reload ssh

# Vérifier depuis une seconde session avant de fermer la première
ssh -o BatchMode=yes deploy@serveur true && echo "accès par clé OK\"""", "bash",
             "Deux vérifications vitales"),
        table(["Risque", "Mesure", "Effet"],
              [["Force brute sur mot de passe", "Clés uniquement", "Supprime le vecteur"],
               ["Compromission de root", "`PermitRootLogin no`", "Traçabilité par compte"],
               ["Rebond interne", "`AllowTcpForwarding no`", "Limite le pivot"],
               ["Balayage de ports", "`fail2ban`", "Blocage temporaire"],
               ["Vol de clé", "Phrase secrète + agent", "Clé inutilisable seule"]],
              widths=[5.0, 4.4, 3.6], first_col_bold=True,
              caption="Cinq risques et leurs mesures"),

        h(2, "Diagnostiquer"),
        p("Un refus SSH a cinq causes principales. Le message d'erreur du client indique "
          "presque toujours laquelle."),
        table(["Message", "Cause", "Action"],
              [["`Connection refused`", "Service arrêté ou port filtré", "Vérifier `ss -ltnp`"],
               ["`Permission denied (publickey)`", "Clé absente ou droits incorrects", "`ssh -vvv`"],
               ["`Host key verification failed`", "Empreinte changée", "Vérifier, puis `known_hosts`"],
               ["`Connection timed out`", "Pare-feu ou routage", "`nc -zv`"],
               ["`Too many authentication failures`", "Trop de clés proposées", "`IdentitiesOnly yes`"]],
              widths=[4.6, 4.6, 3.8], first_col_bold=True,
              caption="Cinq messages et leur cause"),
        code("""# Diagnostic détaillé côté client
ssh -vvv deploy@serveur 2>&1 | tail -40

# Côté serveur, en cas d'échec
journalctl -u ssh -n 50 --no-pager
tail -f /var/log/auth.log

# Tester le port sans SSH
nc -zv serveur 22""", "bash", "Trois sources de diagnostic"),
        box("methode", "Rotation d'une clé compromise",
            items=["Retirer la clé publique de `authorized_keys`.",
                   "Vérifier les connexions récentes dans `auth.log`.",
                   "Générer une nouvelle paire avec phrase secrète.",
                   "Déployer la nouvelle clé et tester.",
                   "Consigner la rotation."]),
    ],
    "keypoints": [
        "L'authentification par clé remplace le mot de passe.",
        "Ed25519 est le choix par défaut recommandé.",
        "Les droits sur `~/.ssh` doivent être restrictifs.",
        "L'agent conserve les clés déverrouillées pour la session.",
        "`~/.ssh/config` rend les accès lisibles et reproductibles.",
        "Les tunnels évitent d'exposer des ports inutiles.",
        "`PermitRootLogin no` et `PasswordAuthentication no` sont les deux mesures de base.",
        "Toujours tester avant de fermer la session qui a modifié SSH.",
    ],
    "bridge": "L'accès distant est maîtrisé. Le chapitre suivant installe le logiciel "
              "qui répond aux requêtes : le serveur web.",
    "exercises": [
        ex("Configurer un accès par rebond",
           "Les serveurs internes ne sont joignables que via un bastion.",
           ["Déclarez le bastion.",
            "Déclarez les serveurs internes.",
            "Testez sans commande complexe."],
           [("text", """Host bastion
    HostName bastion.exemple.fr
    User jump
    IdentityFile ~/.ssh/id_bastion

Host web1 web2
    User deploy
    ProxyJump bastion
    IdentityFile ~/.ssh/id_deploy

Host *.interne
    User admin
    ProxyJump bastion
    IdentitiesOnly yes"""),
            "`ProxyJump` remplace une commande `ssh -J` longue et fragile.",
            "`IdentitiesOnly yes` évite l'échec « too many authentication failures » "
            "quand l'agent propose trop de clés."]),
        ex("Ouvrir un tunnel vers une base",
           "La base PostgreSQL n'est accessible que depuis le serveur.",
           ["Créez le tunnel.",
            "Connectez-vous en local.",
            "Vérifiez la fermeture."],
           [("bash", """ssh -N -L 15432:localhost:5432 deploy@serveur

# Dans un autre terminal
psql -h 127.0.0.1 -p 15432 -U app -d app

# Vérifier l'écoute locale
ss -ltnp | grep 15432"""),
            "`-N` n'ouvre pas de shell : la connexion ne sert qu'au tunnel.",
            "Le tunnel se ferme avec la session SSH : pour un usage durable, utilisez "
            "`autossh` ou une unité systemd."]),
        ex("Diagnostiquer un refus",
           "`Permission denied (publickey)` sur un serveur qui fonctionnait hier.",
           ["Vérifiez la clé proposée.",
            "Vérifiez les droits.",
            "Consultez le journal serveur."],
           [("bash", """ssh -vvv deploy@serveur 2>&1 | grep -A3 "Offering"
ls -l ~/.ssh
ssh-add -l

# Côté serveur (via la console du fournisseur)
journalctl -u ssh -n 30
grep "deploy" /var/log/auth.log | tail"""),
            "`ssh -vvv` montre les clés proposées et celles acceptées ou refusées.",
            "Des droits trop ouverts sur `authorized_keys` provoquent un refus "
            "silencieux côté serveur."],
           level="Diagnostic"),
    ],
    "quiz": [
        quiz("Quelle clé est recommandée par défaut ?",
             ["RSA 1024", "DSA", "Ed25519", "ECDSA 521"],
             2,
             "Ed25519 offre une bonne sécurité avec des clés courtes et rapides."),
        quiz("Que fait `ProxyJump` ?",
             ["Chiffre la session", "Traverse un hôte intermédiaire",
              "Ouvre un SOCKS", "Copie des fichiers"],
             1,
             "Il ouvre la connexion via un bastion, de façon transparente."),
        quiz("Quelle directive interdit l'accès root ?",
             ["`AllowUsers`", "`PermitRootLogin no`", "`MaxAuthTries`", "`PasswordAuthentication no`"],
             1,
             "`PermitRootLogin no` empêche toute connexion directe en root."),
        quiz("Que signifie `Permission denied (publickey)` ?",
             ["Le réseau est coupé", "La clé proposée n'est pas acceptée",
              "Le serveur est éteint", "Le DNS échoue"],
             1,
             "Le serveur a refusé toutes les clés proposées."),
        quiz("Quel transfert expose un service local sur le serveur distant ?",
             ["`-L`", "`-R`", "`-D`", "`-N`"],
             1,
             "`-R` crée un transfert distant vers le poste local."),
    ],
}
