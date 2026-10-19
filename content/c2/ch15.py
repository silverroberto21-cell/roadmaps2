from bookkit.dsl import (box, code, defn, ex, fig, h, ol, p, quiz, table, ul)

CH = {
    "title": "Serveurs web : Nginx et Apache",
    "subtitle": "Servir des sites statiques et proxyfier des applications, avec une "
                "configuration lisible et vérifiée.",
    "duration": "3 h 15",
    "level": "Intermédiaire",
    "prereq": "chapitre 54",
    "objectives": [
        "Choisir entre serveur statique, proxy inverse et application.",
        "Écrire une configuration Nginx structurée.",
        "Comprendre les blocs Apache et les fichiers `.htaccess`.",
        "Configurer journaux, en-têtes et sécurité de base.",
        "Diagnostiquer une erreur 502 ou 403.",
    ],
    "blocks": [
        h(2, "Trois rôles"),
        p("Un serveur web peut servir des fichiers, relayer des requêtes vers une "
          "application, ou assurer les deux. Distinguer ces rôles évite les "
          "configurations confuses."),
        table(["Rôle", "Exemple", "Responsabilité"],
              [["Serveur statique", "HTML, CSS, images", "Fichiers et en-têtes"],
               ["Proxy inverse", "Nginx → Node.js", "Routage, TLS, limitation"],
               ["Équilibreur", "Nginx → trois applications", "Répartition et santé"],
               ["Serveur d'application", "Node, Gunicorn, PHP-FPM", "Logique métier"]],
              widths=[4.0, 4.6, 4.4], first_col_bold=True,
              caption="Quatre rôles et leur responsabilité"),
        fig("flow", "Nginx devant une application",
            ["Client → Nginx :443",
             "TLS terminé par Nginx",
             "Fichiers statiques servis directement",
             "Requêtes dynamiques → application :3000",
             "Réponse renvoyée au client",
             "Journaux d'accès et d'erreur"],
            height=255),

        h(2, "Nginx : une configuration par blocs"),
        p("Nginx organise sa configuration en contexte `http`, puis `server` par site, "
          "puis `location` par chemin. La directive la plus spécifique l'emporte."),
        code("""# /etc/nginx/sites-available/exemple.fr
server {
    listen 443 ssl;
    http2 on;
    server_name exemple.fr www.exemple.fr;

    ssl_certificate     /etc/letsencrypt/live/exemple.fr/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/exemple.fr/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;

    root /var/www/exemple;
    index index.html;

    access_log /var/log/nginx/exemple.access.log;
    error_log  /var/log/nginx/exemple.error.log warn;

    # Statique : cache long grâce à l'empreinte dans le nom
    location ~* \\.(css|js|woff2|avif|webp)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
        try_files $uri =404;
    }

    # Application derrière un proxy
    location /api/ {
        proxy_pass http://127.0.0.1:3000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 30s;
    }

    # Page unique : tout retombe sur index.html
    location / {
        try_files $uri $uri/ /index.html;
    }
}""", "nginx", "Une configuration complète"),
        code("""# Activer le site et vérifier
ln -s /etc/nginx/sites-available/exemple.fr /etc/nginx/sites-enabled/
rm /etc/nginx/sites-enabled/default

nginx -t
systemctl reload nginx
nginx -T | less        # configuration complète effective""", "bash",
             "Quatre étapes, une vérification"),
        table(["Directive", "Effet", "Piège"],
              [["`root`", "Répertoire des fichiers", "Doit exister et être lisible"],
               ["`try_files`", "Ordre de recherche", "Un `=404` final évite le listage"],
               ["`proxy_pass`", "Destination", "La barre finale change le chemin"],
               ["`expires`", "Cache navigateur", "Inutile sans nom versionné"],
               ["`client_max_body_size`", "Taille maximale", "1 Mo par défaut"]],
              widths=[4.2, 4.4, 4.4], first_col_bold=True,
              caption="Cinq directives à connaître"),
        box("attention", "La barre oblique de `proxy_pass`",
            "`proxy_pass http://127.0.0.1:3000/;` (avec barre) remplace le préfixe "
            "correspondant ; sans barre, il conserve le chemin complet. Cette différence "
            "explique de nombreuses erreurs 404 difficiles à voir."),

        h(2, "Apache : modules et fichiers `.htaccess`"),
        p("Apache utilise une architecture de modules et des fichiers de configuration "
          "par répertoire. `.htaccess` permet de modifier la configuration sans accès "
          "root, au prix de performances et de lisibilité."),
        code("""<VirtualHost *:443>
    ServerName exemple.fr
    ServerAlias www.exemple.fr
    DocumentRoot /var/www/exemple

    SSLEngine on
    SSLCertificateFile      /etc/letsencrypt/live/exemple.fr/fullchain.pem
    SSLCertificateKeyFile   /etc/letsencrypt/live/exemple.fr/privkey.pem
    SSLProtocol             all -SSLv3 -TLSv1 -TLSv1.1

    <Directory /var/www/exemple>
        Options -Indexes +FollowSymLinks
        AllowOverride All
        Require all granted
    </Directory>

    ProxyPreserveHost On
    ProxyPass        /api/ http://127.0.0.1:3000/api/
    ProxyPassReverse /api/ http://127.0.0.1:3000/api/

    ErrorLog  ${APACHE_LOG_DIR}/exemple.error.log
    CustomLog ${APACHE_LOG_DIR}/exemple.access.log combined
</VirtualHost>""", "apache", "Un hôte virtuel complet"),
        code("""# Modules nécessaires
a2enmod ssl proxy proxy_http headers rewrite http2
a2ensite exemple.fr
apachectl configtest
systemctl reload apache2

# .htaccess minimal
RewriteEngine On
RewriteCond %{HTTPS} off
RewriteRule ^ https://%{HTTP_HOST}%{REQUEST_URI} [L,R=301]""", "bash",
             "Cinq commandes"),
        table(["Critère", "Nginx", "Apache"],
              [["Modèle", "Événementiel", "Processus par connexion (MPM)"],
               ["Configuration", "Fichiers centralisés", "`.htaccess` possible"],
               ["Proxy inverse", "Très courant", "Possible"],
               ["Modules", "Compilation ou paquets", "Activation dynamique"],
               ["Mémoire", "Faible", "Plus élevée sous charge"]],
              widths=[4.0, 4.6, 4.4], first_col_bold=True,
              caption="Cinq critères de comparaison"),

        h(2, "Journaux et en-têtes"),
        p("Les journaux sont la première source d'information en cas d'incident. Un "
          "format enrichi coûte peu et répond à beaucoup de questions."),
        code("""# Format de journal enrichi
log_format principal '$remote_addr - $remote_user [$time_local] '
                     '"$request" $status $body_bytes_sent '
                     '"$http_referer" "$http_user_agent" '
                     'rt=$request_time uct=$upstream_connect_time '
                     'urt=$upstream_response_time';

access_log /var/log/nginx/access.log principal;""", "nginx",
             "Un format qui mesure le temps"),
        code("""# En-têtes de sécurité
add_header Strict-Transport-Security "max-age=63072000; includeSubDomains" always;
add_header X-Content-Type-Options "nosniff" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
add_header Content-Security-Policy "default-src 'self'" always;
add_header Permissions-Policy "camera=(), microphone=(), geolocation=()" always;""",
             "nginx", "Cinq en-têtes"),
        defn("`X-Forwarded-For`", "En-tête qui transporte l'adresse du client d'origine "
                                  "à travers un proxy. Sans lui, l'application voit "
                                  "l'adresse du proxy et ne peut ni journaliser ni "
                                  "limiter correctement."),

        h(2, "Diagnostiquer"),
        p("Trois codes concentrent les problèmes de configuration : 403, 404 et 502. "
          "Chacun a un petit nombre de causes."),
        table(["Code", "Cause fréquente", "Vérification"],
              [["403", "Droits ou `index` absent", "`namei -l /var/www/...`"],
               ["404", "`root` ou `try_files` incorrect", "`nginx -T`, `ls`"],
               ["502", "Application arrêtée ou port erroné", "`ss -ltnp`, journal"],
               ["504", "Application trop lente", "`request_time`, `upstream_response_time`"],
               ["413", "Corps trop volumineux", "`client_max_body_size`"],
               ["499", "Client parti avant la réponse", "Latence excessive"]],
              widths=[2.4, 5.2, 5.2], first_col_bold=True,
              caption="Six codes et leurs causes"),
        code("""# 403 : vérifier chaque niveau du chemin
namei -l /var/www/exemple/index.html

# 502 : l'application écoute-t-elle ?
ss -ltnp | grep 3000
journalctl -u mon-app -n 30 --no-pager

# Mesurer le temps applicatif
tail -f /var/log/nginx/access.log | awk '{print $NF, $(NF-2)}'""", "bash",
             "Trois vérifications ciblées"),
        box("pratique", "Tester depuis le serveur",
            "Une requête `curl -H \"Host: exemple.fr\" http://127.0.0.1/` teste la "
            "configuration sans passer par le DNS ni le pare-feu. Cela sépare un "
            "problème applicatif d'un problème réseau."),
        box("methode", "Avant de recharger",
            items=["`nginx -t` ou `apachectl configtest`.",
                   "Recharger, pas redémarrer, quand c'est possible.",
                   "Vérifier le journal d'erreur dans les secondes qui suivent.",
                   "Tester une URL connue et une URL inexistante."]),
    ],
    "keypoints": [
        "Un serveur web peut servir du statique, proxyfier, ou les deux.",
        "Nginx organise la configuration en `http`, `server`, `location`.",
        "La barre finale de `proxy_pass` change le chemin transmis.",
        "`try_files` définit l'ordre de résolution des fichiers.",
        "Apache peut se configurer par `.htaccess`, au prix de la performance.",
        "`X-Forwarded-For` préserve l'adresse du client.",
        "403, 404 et 502 ont des causes distinctes et identifiables.",
        "Toujours valider la configuration avant de recharger.",
    ],
    "bridge": "Un serveur suffit rarement. Le chapitre suivant répartit la charge et "
              "rapproche les contenus des utilisateurs.",
    "exercises": [
        ex("Servir une application derrière Nginx",
           "Une application Node écoute sur le port 3000.",
           ["Configurez le proxy.",
            "Transmettez les en-têtes.",
            "Vérifiez les fichiers statiques."],
           [("nginx", """server {
    listen 80;
    server_name exemple.fr;

    root /var/www/exemple;
    index index.html;

    location /assets/ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    location /api/ {
        proxy_pass http://127.0.0.1:3000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location / {
        try_files $uri /index.html;
    }
}"""),
            "Les fichiers statiques évitent de solliciter l'application pour des "
            "ressources immuables.",
            "Sans `X-Forwarded-Proto`, l'application croit recevoir du HTTP et peut "
            "générer des URL erronées."]),
        ex("Corriger une erreur 403",
           "Nginx renvoie 403 alors que le fichier existe.",
           ["Vérifiez les droits de chaque niveau.",
            "Vérifiez l'utilisateur du processus.",
            "Corrigez sans ouvrir à tout le monde."],
           [("bash", """namei -l /var/www/exemple/index.html
ps -o user= -p $(pgrep -f "nginx: worker" | head -1)

# Correction minimale : traversée pour tous, lecture pour nginx
chmod 755 /var/www /var/www/exemple
chmod 644 /var/www/exemple/index.html
chown -R www-data:www-data /var/www/exemple"""),
            "Un répertoire parent sans bit `x` empêche la traversée, même si le fichier "
            "est lisible.",
            "`chmod 755` sur les répertoires et `644` sur les fichiers suffisent ; "
            "inutile d'ouvrir l'écriture."],
           level="Diagnostic"),
        ex("Corriger une erreur 502",
           "Le proxy renvoie 502 après un déploiement.",
           ["Vérifiez l'écoute de l'application.",
            "Vérifiez le port configuré.",
            "Consultez les journaux applicatifs."],
           [("bash", """ss -ltnp | grep 3000
curl -v http://127.0.0.1:3000/health
journalctl -u mon-app -n 50 --no-pager
tail -20 /var/log/nginx/error.log

# Causes typiques : application non démarrée, port différent,
# écoute sur 127.0.0.1 alors que Nginx cherche une autre adresse,
# démarrage plus long que le délai de reprise"""),
            "Un 502 signifie que le proxy n'a pas pu joindre l'amont : la cause est en "
            "aval de Nginx.",
            "Après un déploiement, le démarrage peut dépasser le délai : une vérification "
            "de santé évite de router du trafic trop tôt."],
           level="Diagnostic"),
    ],
    "quiz": [
        quiz("Quel contexte Nginx définit un site ?",
             ["`http`", "`server`", "`location`", "`upstream`"],
             1,
             "Le bloc `server` correspond à un hôte virtuel."),
        quiz("Que change une barre finale dans `proxy_pass` ?",
             ["Rien", "Le chemin transmis à l'amont", "Le port", "Le protocole"],
             1,
             "Avec barre, le préfixe correspondant est remplacé ; sans, il est conservé."),
        quiz("Que signifie un 502 ?",
             ["Le client a mal formulé la requête", "Le proxy n'a pas pu joindre l'amont",
              "Le fichier est absent", "Trop de requêtes"],
             1,
             "Bad Gateway indique un échec de communication avec le service en amont."),
        quiz("Quel en-tête transmet l'adresse réelle du client ?",
             ["`Host`", "`X-Forwarded-For`", "`User-Agent`", "`Referer`"],
             1,
             "Il est renseigné par le proxy qui reçoit la requête d'origine."),
        quiz("Quelle commande valide une configuration Nginx ?",
             ["`nginx -v`", "`nginx -t`", "`nginx -s stop`", "`nginx -T` seulement"],
             1,
             "`-t` teste la syntaxe avant tout rechargement."),
    ],
}
