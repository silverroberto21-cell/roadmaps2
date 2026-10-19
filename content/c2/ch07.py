from bookkit.dsl import (box, code, defn, ex, fig, h, ol, p, quiz, table, ul)

CH = {
    "title": "Provisionner une machine et gérer ses paquets",
    "subtitle": "Créer un serveur reproductible : système minimal, paquets maîtrisés, "
                "configuration initiale et durcissement.",
    "duration": "3 h 00",
    "level": "Intermédiaire",
    "prereq": "chapitre 46",
    "objectives": [
        "Installer un système minimal et le mettre à jour.",
        "Utiliser `apt` et `dnf` sans casser un serveur.",
        "Épingler des versions et comprendre les dépôts.",
        "Durcir un accès SSH et un pare-feu.",
        "Rendre une machine reproductible par un script d'amorçage.",
    ],
    "blocks": [
        h(2, "D'un système minimal à un serveur"),
        p("Un serveur n'a pas besoin d'environnement graphique. Chaque paquet installé "
          "est une surface de mise à jour et une vulnérabilité potentielle : le premier "
          "geste de durcissement est de réduire ce qui est présent."),
        fig("flow", "Les étapes d'un amorçage",
            ["Image minimale",
             "Mise à jour du système",
             "Comptes et accès SSH",
             "Pare-feu et fuseau horaire",
             "Outils d'exploitation",
             "Vérification et instantané"],
            height=250),
        code("""# Ubuntu / Debian
apt update && apt upgrade -y
apt install -y curl ca-certificates gnupg chrony unattended-upgrades

# RHEL / Rocky / Alma
dnf update -y
dnf install -y curl ca-certificates chrony dnf-automatic

# Vérifications de base
hostnamectl
timedatectl
free -h
df -h""", "bash", "Mise à jour et outils de base"),
        table(["Distribution", "Gestionnaire", "Paquets", "Remarque"],
              [["Debian / Ubuntu", "`apt`", "`.deb`", "Stable, très répandu"],
               ["RHEL / Rocky", "`dnf`", "`.rpm`", "Support long"],
               ["Alpine", "`apk`", "`.apk`", "Image minuscule"],
               ["Arch", "`pacman`", "`.pkg.tar.zst`", "À jour, rolling release"],
               ["Amazon Linux", "`dnf`", "`.rpm`", "Optimisé AWS"]],
              widths=[3.4, 3.0, 2.8, 3.4], first_col_bold=True,
              caption="Cinq familles de distributions"),
        defn("Dépôt", "Source de paquets signée par une clé. Ajouter un dépôt revient à "
                      "accorder sa confiance à son mainteneur : c'est une décision de "
                      "sécurité, pas une formalité."),

        h(2, "Maîtriser les paquets"),
        p("`apt upgrade` et `apt dist-upgrade` ne se comportent pas de la même façon : "
          "le second peut installer et supprimer des paquets pour satisfaire les "
          "dépendances. Sur un serveur, la différence compte."),
        code("""# Mises à jour
apt update                       # rafraîchit les index
apt upgrade -y                   # met à jour sans supprimer
apt full-upgrade -y              # autorise les changements de dépendances
apt install --only-upgrade nginx # un seul paquet

# Informations
apt list --installed | head
apt-cache policy nginx
apt-cache show nginx | head -20
dpkg -l | grep nginx
dpkg -L nginx                    # fichiers installés
dpkg -S /etc/nginx/nginx.conf    # paquet propriétaire""", "bash",
             "Huit commandes `apt` et `dpkg`"),
        code("""# Épingler une version
apt install nginx=1.24.0-1ubuntu1

# Empêcher une mise à jour
apt-mark hold nginx
apt-mark showhold
apt-mark unhold nginx

# Mises à jour de sécurité automatiques (Debian/Ubuntu)
dpkg-reconfigure -plow unattended-upgrades
# /etc/apt/apt.conf.d/20auto-upgrades
# APT::Periodic::Unattended-Upgrade "1";""", "bash",
             "Trois façons de maîtriser les versions"),
        box("attention", "Ne mélangez pas les sources",
            "Installer un paquet depuis un dépôt tiers pour une version plus récente "
            "peut bloquer les mises à jour du système entier. Préférez un paquet "
            "officiel, une image de conteneur ou une compilation isolée dans `/opt`."),
        table(["Besoin", "Solution système", "Alternative"],
              [["Version précise", "Épinglage `apt-mark`", "Conteneur"],
               ["Logiciel absent des dépôts", "Dépôt officiel signé", "Binaire dans `/opt`"],
               ["Isolation", "Utilisateur dédié", "Conteneur"],
               ["Mise à jour fréquente", "Dépôt amont", "Image reconstruite"],
               ["Rollback rapide", "Instantané de machine", "Déploiement bleu-vert"]],
              widths=[4.4, 4.6, 3.4], first_col_bold=True,
              caption="Cinq besoins et leurs réponses"),

        h(2, "Durcir l'accès"),
        p("Un serveur exposé à Internet reçoit des tentatives de connexion dès les "
          "premières minutes. Trois mesures suffisent à écarter l'immense majorité des "
          "attaques automatisées."),
        code("""# /etc/ssh/sshd_config
PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes
AllowUsers deploy admin
MaxAuthTries 3
ClientAliveInterval 300
X11Forwarding no""", "text", "Sept directives SSH"),
        code("""# Vérifier avant de recharger : une erreur peut vous verrouiller dehors
sshd -t
systemctl reload ssh

# Tester dans une seconde session avant de fermer la première
ssh -o PreferredAuthentications=publickey deploy@serveur""", "bash",
             "Deux vérifications indispensables"),
        code("""# Pare-feu : n'ouvrir que le nécessaire
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp
ufw allow 80,443/tcp
ufw enable
ufw status verbose

# Équivalent nftables
nft add table inet filtre
nft add chain inet filtre entree '{ type filter hook input priority 0; policy drop; }'
nft add rule inet filtre entree ct state established,related accept
nft add rule inet filtre entree tcp dport { 22, 80, 443 } accept""", "bash",
             "Un pare-feu minimal"),
        code("""# Protection contre la force brute
apt install -y fail2ban
# /etc/fail2ban/jail.local
[sshd]
enabled = true
maxretry = 4
findtime = 10m
bantime = 1h

systemctl enable --now fail2ban
fail2ban-client status sshd""", "bash", "Quatre lignes et un service"),
        box("pratique", "Compte d'administration plutôt que root",
            "Un compte nominatif avec `sudo` permet de tracer qui a fait quoi. "
            "`PermitRootLogin no` et `PasswordAuthentication no` suppriment les deux "
            "vecteurs les plus exploités."),

        h(2, "Amorçage reproductible"),
        p("Une machine configurée à la main n'est pas reproductible. Le script "
          "d'amorçage documente l'état attendu, et permet de recréer un serveur "
          "identique en quelques minutes."),
        code("""#!/usr/bin/env bash
# amorcage.sh — état initial d'un serveur Ubuntu 24.04
set -euo pipefail

export DEBIAN_FRONTEND=noninteractive

apt update
apt upgrade -y
apt install -y curl ca-certificates chrony ufw fail2ban unattended-upgrades

# Fuseau et synchronisation
timedatectl set-timezone Africa/Porto-Novo
systemctl enable --now chrony

# Utilisateur d'administration
id -u deploy &>/dev/null || adduser --disabled-password --gecos "" deploy
usermod -aG sudo deploy
install -d -m 700 -o deploy -g deploy /home/deploy/.ssh
cat > /home/deploy/.ssh/authorized_keys <<'KEY'
ssh-ed25519 AAAAC3Nza... deploy@poste
KEY
chown deploy:deploy /home/deploy/.ssh/authorized_keys
chmod 600 /home/deploy/.ssh/authorized_keys

# Durcissement
sed -i 's/^#\\?PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config
sed -i 's/^#\\?PasswordAuthentication.*/PasswordAuthentication no/' /etc/ssh/sshd_config
sshd -t

ufw --force enable
ufw allow 22/tcp
ufw allow 80,443/tcp

systemctl reload ssh
echo "Amorçage terminé\"""", "bash", "Un script d'amorçage complet"),
        table(["Élément", "Versionné", "Vérifié"],
              [["Script d'amorçage", "Oui, dans le dépôt", "Exécution sur machine neuve"],
               ["Configuration SSH", "Oui", "`sshd -t`"],
               ["Règles de pare-feu", "Oui", "`ufw status`"],
               ["Paquets et versions", "Oui", "Comparaison avec l'inventaire"],
               ["Secrets", "Non", "Coffre séparé"]],
              widths=[4.4, 4.4, 3.6], first_col_bold=True,
              caption="Ce qui doit être versionné"),
        defn("Idempotence", "Propriété d'une opération qui, répétée, produit le même "
                            "résultat. Un script d'amorçage doit pouvoir être relancé "
                            "sans échouer ni dupliquer."),
        code("""# Rendre les opérations idempotentes
id -u deploy &>/dev/null || adduser --disabled-password deploy
grep -q "^PermitRootLogin no" /etc/ssh/sshd_config || echo "PermitRootLogin no" >> /etc/ssh/sshd_config
ufw status | grep -q "22/tcp" || ufw allow 22/tcp""", "bash",
             "Trois modèles d'idempotence"),
        box("methode", "Check-list d'un serveur neuf",
            items=["Mises à jour appliquées et automatiques.",
                   "Fuseau horaire et synchronisation NTP.",
                   "Accès SSH par clé, root interdit.",
                   "Pare-feu en refus par défaut.",
                   "Journalisation et supervision branchées.",
                   "Instantané ou image de référence conservée."]),
    ],
    "keypoints": [
        "Un système minimal réduit la surface d'attaque.",
        "`apt full-upgrade` peut modifier des dépendances, `apt upgrade` non.",
        "Un dépôt tiers est une décision de sécurité.",
        "L'épinglage protège une version, au prix des correctifs.",
        "SSH par clé, sans root, testé avant déconnexion.",
        "Le pare-feu refuse par défaut et n'ouvre que le nécessaire.",
        "Un script d'amorçage doit être idempotent.",
        "Ce qui est fait à la main n'est pas reproductible.",
    ],
    "bridge": "La machine est prête. Le chapitre suivant la met en réseau : modèles, "
              "adressage et routage.",
    "exercises": [
        ex("Écrire un script d'amorçage",
           "Préparez un script réutilisable pour trois serveurs.",
           ["Mise à jour et paquets de base.",
            "Utilisateur et clé SSH.",
            "Pare-feu et vérifications."],
           [("code", """#!/usr/bin/env bash
set -euo pipefail
export DEBIAN_FRONTEND=noninteractive

apt update && apt upgrade -y
apt install -y curl chrony ufw fail2ban

timedatectl set-timezone Africa/Porto-Benin 2>/dev/null || true
systemctl enable --now chrony

id -u deploy &>/dev/null || adduser --disabled-password --gecos "" deploy
usermod -aG sudo deploy

ufw --force enable
ufw allow 22/tcp

sshd -t
systemctl reload ssh
systemctl enable --now fail2ban"""),
            "Le script se termine par les vérifications : une erreur de configuration "
            "SSH est détectée avant la déconnexion.",
            "`|| true` sur le fuseau évite un échec si la valeur est inconnue, sans "
            "masquer les autres erreurs."]),
        ex("Réduire une surface d'attaque",
           "Un serveur exécute un serveur web, une base et une tâche planifiée.",
           ["Listez les services actifs.",
            "Désactivez ce qui est inutile.",
            "Vérifiez les ports ouverts."],
           [("code", """systemctl list-unit-files --state=enabled
ss -ltnp
ufw status verbose

# Désactiver un service inutile
systemctl disable --now cups.service
systemctl mask cups.service

# Vérifier après redémarrage
systemctl list-units --type=service --state=running"""),
            "Un service activé mais inutilisé reste une surface de mise à jour et "
            "d'exploitation.",
            "`mask` empêche même un démarrage par dépendance, contrairement à `disable`."],
           level="Sécurité"),
        ex("Gérer une mise à jour risquée",
           "Une mise à jour de Nginx casse la configuration.",
           ["Sauvegardez la configuration.",
            "Épinglez la version précédente.",
            "Préparez un retour arrière."],
           [("code", """cp -a /etc/nginx /root/nginx-$(date +%F)
apt-mark hold nginx nginx-common

# Après analyse de la nouvelle version
apt-mark unhold nginx nginx-common
apt install nginx=1.24.0-1ubuntu1
nginx -t || { echo "Configuration invalide"; exit 1; }
systemctl reload nginx"""),
            "`nginx -t` valide la syntaxe avant tout rechargement : il évite une coupure "
            "complète.",
            "La copie horodatée de `/etc/nginx` permet de revenir à une configuration "
            "connue en quelques secondes."],
           level="Exploitation"),
    ],
    "quiz": [
        quiz("Quelle commande permet des changements de dépendances lors d'une mise à jour ?",
             ["`apt update`", "`apt upgrade`", "`apt full-upgrade`", "`apt install`"],
             2,
             "`full-upgrade` peut installer ou supprimer des paquets pour satisfaire les "
             "dépendances."),
        quiz("Pourquoi désactiver `PermitRootLogin` ?",
             ["Pour accélérer SSH", "Pour supprimer un vecteur d'attaque courant",
              "Pour économiser la mémoire", "Pour activer sudo"],
             1,
             "Les attaques automatisées ciblent massivement le compte root."),
        quiz("Que fait `apt-mark hold` ?",
             ["Désinstalle un paquet", "Empêche sa mise à jour",
              "Le rend prioritaire", "Le télécharge"],
             1,
             "Le paquet est conservé dans sa version actuelle."),
        quiz("Qu'est-ce qu'un script idempotent ?",
             ["Qui s'exécute vite", "Qui peut être relancé sans effet supplémentaire",
              "Qui ne fait rien", "Qui nécessite root"],
             1,
             "Le résultat reste identique quel que soit le nombre d'exécutions."),
        quiz("Pourquoi tester `sshd -t` avant de recharger ?",
             ["Pour accélérer", "Pour éviter de se verrouiller hors du serveur",
              "Pour redémarrer", "Pour lister les clés"],
             1,
             "Une configuration invalide empêcherait toute nouvelle connexion."),
    ],
}
