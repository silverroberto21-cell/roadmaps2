from bookkit.dsl import (box, code, defn, ex, fig, h, ol, p, quiz, table, ul)

CH = {
    "title": "TLS et certificats",
    "subtitle": "Chiffrer, authentifier et renouveler : ce que TLS garantit, et ce "
                "qu'il ne garantit pas.",
    "duration": "3 h 00",
    "level": "Intermédiaire",
    "prereq": "chapitre 52",
    "objectives": [
        "Décrire une poignée de main TLS 1.3.",
        "Choisir un type de certificat adapté.",
        "Automatiser l'émission et le renouvellement.",
        "Vérifier une chaîne de confiance.",
        "Éviter les erreurs de configuration les plus fréquentes.",
    ],
    "blocks": [
        h(2, "Trois garanties"),
        p("TLS assure la confidentialité, l'intégrité et l'authentification du serveur. "
          "Il ne protège pas contre une application vulnérable, ni contre un serveur "
          "mal configuré, ni contre un attaquant qui contrôle la machine."),
        table(["Garantie", "Mécanisme", "Limite"],
              [["Confidentialité", "Chiffrement symétrique", "Métadonnées visibles"],
               ["Intégrité", "Code d'authentification de message", "Ne protège pas les sauvegardes"],
               ["Authentification", "Certificat et chaîne de confiance", "Sauf certificat volé"],
               ["Confidentialité persistante", "Échange éphémère (ECDHE)", "Sauf clé compromise"]],
              widths=[3.6, 4.6, 5.0], first_col_bold=True,
              caption="Quatre garanties et leurs limites"),
        fig("flow", "Une poignée de main TLS 1.3",
            ["Client → serveur : ClientHello (versions, suites, clé publique éphémère)",
             "Serveur → client : ServerHello, certificat, preuve de possession",
             "Client : vérifie la chaîne et le nom",
             "Les deux calculent les mêmes clés de session",
             "Échange chiffré — un seul aller-retour"],
            height=255),
        defn("Confidentialité persistante", "Propriété d'une session dont la clé de "
                                            "session ne peut pas être reconstituée même "
                                            "si la clé privée du serveur est compromise "
                                            "plus tard."),
        p("TLS 1.3 supprime les suites obsolètes, réduit la poignée de main à un "
          "aller-retour et impose la confidentialité persistante. TLS 1.2 reste présent "
          "pour compatibilité ; TLS 1.0 et 1.1 sont à désactiver."),

        h(2, "Certificats"),
        p("Un certificat lie un nom à une clé publique, et il est signé. Sa validité "
          "repose sur trois vérifications : la chaîne de confiance, le nom, et les "
          "dates."),
        code("""# Examiner un certificat
openssl s_client -connect exemple.fr:443 -servername exemple.fr </dev/null 2>/dev/null \\
  | openssl x509 -noout -subject -issuer -dates -ext subjectAltName

# Vérifier la chaîne complète
openssl s_client -connect exemple.fr:443 -showcerts </dev/null

# Vérifier une date d'expiration à distance
echo | openssl s_client -connect exemple.fr:443 2>/dev/null \\
  | openssl x509 -noout -enddate""", "bash", "Trois examens de certificat"),
        table(["Type", "Validation", "Usage"],
              [["DV (Domain Validation)", "Contrôle du nom", "Sites courants"],
               ["OV (Organization Validation)", "Documents de l'organisation", "Entreprises"],
               ["EV (Extended Validation)", "Vérification renforcée", "Rare, peu d'effet visible"],
               ["Auto-signé", "Aucune", "Interne, tests"],
               ["Interne (PKI privée)", "Autorité interne", "Services internes"]],
              widths=[5.0, 4.2, 4.0], first_col_bold=True,
              caption="Cinq types de certificats"),
        box("attention", "Un certificat auto-signé n'est pas une sécurité",
            "Il chiffre mais n'authentifie pas : le client ne peut pas distinguer le "
            "vrai serveur d'une interception. Dans un réseau interne, déployez une "
            "autorité de certification interne et installez sa racine sur les machines."),

        h(2, "Automatiser avec ACME"),
        p("Un certificat oublié expire. L'automatisation n'est pas un confort : c'est la "
          "seule manière fiable de respecter une durée de vie de 90 jours."),
        code("""# Certbot avec Nginx
apt install -y certbot python3-certbot-nginx
certbot --nginx -d exemple.fr -d www.exemple.fr

# Vérifier le renouvellement automatique
systemctl list-timers | grep certbot
certbot renew --dry-run

# Renouvellement manuel et rechargement
certbot renew --deploy-hook "systemctl reload nginx\"""", "bash",
             "Une automatisation complète"),
        code("""# ACME avec un client plus léger
curl https://get.acme.sh | sh -s email=admin@exemple.fr
~/.acme.sh/acme.sh --issue -d exemple.fr -w /var/www/certbot

~/.acme.sh/acme.sh --install-cert -d exemple.fr \\
  --key-file       /etc/nginx/tls/exemple.fr.key \\
  --fullchain-file /etc/nginx/tls/exemple.fr.crt \\
  --reloadcmd      "systemctl reload nginx\"""", "bash",
             "Une alternative répandue"),
        table(["Méthode de validation", "Principe", "Condition"],
              [["HTTP-01", "Fichier servi sous `/.well-known/acme-challenge/`", "Port 80 accessible"],
               ["DNS-01", "Enregistrement TXT temporaire", "Accès à l'API DNS"],
               ["TLS-ALPN-01", "Réponse pendant la négociation TLS", "Port 443 libre"]],
              widths=[4.4, 5.6, 3.2], first_col_bold=True,
              caption="Trois méthodes de validation"),
        p("DNS-01 est la seule méthode qui permet d'obtenir un certificat wildcard "
          "(`*.exemple.fr`) et qui fonctionne pour un serveur non exposé à Internet."),

        h(2, "Configurer correctement"),
        p("Une configuration TLS se juge sur trois points : versions autorisées, "
          "algorithmes, et redirection permanente depuis HTTP."),
        code("""# Nginx
server {
    listen 80;
    server_name exemple.fr www.exemple.fr;
    return 301 https://exemple.fr$request_uri;
}

server {
    listen 443 ssl;
    http2 on;
    server_name exemple.fr;

    ssl_certificate     /etc/letsencrypt/live/exemple.fr/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/exemple.fr/privkey.pem;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 1d;

    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains" always;
    add_header X-Content-Type-Options nosniff always;

    root /var/www/site;
    index index.html;
}""", "nginx", "Une configuration de référence"),
        code("""# Vérifier et recharger
nginx -t && systemctl reload nginx

# Tester les versions négociées
openssl s_client -connect exemple.fr:443 -tls1_1 </dev/null 2>&1 | grep -i error
openssl s_client -connect exemple.fr:443 -tls1_3 </dev/null 2>&1 | grep Protocol""",
             "bash", "Deux vérifications"),
        box("pratique", "HSTS a des conséquences",
            "`Strict-Transport-Security` interdit au navigateur tout accès en HTTP "
            "pendant la durée indiquée. Un `max-age` long sur un sous-domaine mal "
            "configuré peut rendre un service inaccessible. Commencez par une durée "
            "courte."),

        h(2, "Diagnostiquer"),
        table(["Symptôme", "Cause probable", "Vérification"],
              [["Certificat expiré", "Renouvellement manuel", "`openssl s_client`"],
               ["Nom absent du SAN", "Mauvais domaine couvert", "`subjectAltName`"],
               ["Chaîne incomplète", "`fullchain` non utilisé", "Navigateur : chaîne"],
               ["Erreur TLS 1.0", "Client ancien", "Journal serveur"],
               ["Certificat non approuvé", "PKI interne non déployée", "Magasin racine"],
               ["Handshake lent", "OCSP ou session mal configurée", "Mesure répétée"]],
              widths=[3.8, 4.6, 4.6], first_col_bold=True,
              caption="Six symptômes et leurs causes"),
        defn("OCSP", "Protocole de vérification de révocation d'un certificat. Le "
                     "stapling permet au serveur de fournir la preuve lui-même, ce qui "
                     "évite un aller-retour du client vers l'autorité."),
        box("methode", "Contrôles avant mise en production",
            items=["`TLS 1.2` et `1.3` uniquement.",
                   "`fullchain.pem` utilisé, pas seulement le certificat feuille.",
                   "Redirection HTTP → HTTPS permanente.",
                   "Renouvellement automatique testé par `--dry-run`.",
                   "Alerte à J-21 sur la date d'expiration."]),
    ],
    "keypoints": [
        "TLS garantit confidentialité, intégrité et authentification du serveur.",
        "La confidentialité persistante protège contre la compromission ultérieure d'une clé.",
        "TLS 1.3 réduit la poignée de main à un aller-retour.",
        "Un certificat couvre des noms listés dans `subjectAltName`.",
        "Un certificat auto-signé chiffre sans authentifier.",
        "ACME automatise l'émission et le renouvellement.",
        "DNS-01 est nécessaire pour un certificat wildcard.",
        "HSTS engage durablement le navigateur.",
    ],
    "bridge": "Le trafic web est chiffré. Le chapitre suivant traite de l'accès "
              "d'administration à distance : SSH.",
    "exercises": [
        ex("Diagnostiquer une expiration",
           "Des utilisateurs signalent une alerte de sécurité depuis ce matin.",
           ["Vérifiez la date d'expiration.",
            "Identifiez le mécanisme de renouvellement.",
            "Corrigez et prévenez."],
           [("bash", """echo | openssl s_client -connect exemple.fr:443 2>/dev/null \\
  | openssl x509 -noout -enddate

systemctl list-timers | grep certbot
journalctl -u certbot --since "7 days ago"

certbot renew --force-renewal
nginx -t && systemctl reload nginx"""),
            "Le journal de Certbot indique si le renouvellement a échoué, et pourquoi : "
            "port 80 fermé, défi DNS expiré, quota atteint.",
            "Une alerte à J-21 aurait laissé trois semaines pour réagir : c'est la "
            "mesure préventive à mettre en place."]),
        ex("Configurer HTTPS complet",
           "Le site doit rediriger HTTP, servir TLS 1.2+ et envoyer HSTS.",
           ["Écrivez les deux blocs serveur.",
            "Vérifiez la chaîne.",
            "Testez la redirection."],
           [("nginx", """server {
    listen 80;
    server_name exemple.fr www.exemple.fr;
    return 301 https://exemple.fr$request_uri;
}

server {
    listen 443 ssl;
    http2 on;
    server_name exemple.fr;
    ssl_certificate     /etc/letsencrypt/live/exemple.fr/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/exemple.fr/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    add_header Strict-Transport-Security "max-age=300" always;
}"""),
            "Commencez par un `max-age` court, puis augmentez après quelques jours "
            "d'observation.",
            "`fullchain.pem` contient le certificat et les intermédiaires : sans eux, "
            "certains clients ne peuvent pas valider la chaîne."]),
        ex("Mettre en place une PKI interne",
           "Trois services internes doivent se faire confiance.",
           ["Créez une autorité racine.",
            "Émettez un certificat par service.",
            "Déployez la racine sur les clients."],
           [("bash", """# Autorité racine
openssl req -x509 -newkey rsa:4096 -days 3650 -nodes \\
  -keyout racine.key -out racine.crt -subj "/CN=PKI interne"

# Certificat de service avec SAN
openssl req -newkey rsa:2048 -nodes -keyout api.key -out api.csr \\
  -subj "/CN=api.interne"
openssl x509 -req -in api.csr -CA racine.crt -CAkey racine.key \\
  -CAcreateserial -days 365 -out api.crt \\
  -extfile <(printf "subjectAltName=DNS:api.interne")

# Déploiement de la racine
cp racine.crt /usr/local/share/ca-certificates/pki-interne.crt
update-ca-certificates"""),
            "La clé de la racine doit être conservée hors ligne : sa compromission "
            "invalide toute la PKI.",
            "Le SAN est obligatoire pour les navigateurs modernes ; le CN seul ne suffit "
            "plus."],
           level="Sécurité"),
    ],
    "quiz": [
        quiz("Que garantit TLS ?",
             ["La disponibilité", "La confidentialité, l'intégrité et l'authentification",
              "La vitesse", "La conformité RGPD"],
             1,
             "TLS protège l'échange, pas l'application ni la disponibilité."),
        quiz("Où figurent les noms couverts par un certificat ?",
             ["Dans le CN uniquement", "Dans `subjectAltName`", "Dans la clé privée", "Dans le CSR"],
             1,
             "Les navigateurs modernes ignorent le CN et se fondent sur le SAN."),
        quiz("Quelle validation ACME permet un certificat wildcard ?",
             ["HTTP-01", "TLS-ALPN-01", "DNS-01", "Aucune"],
             2,
             "Seule DNS-01 prouve le contrôle de tout le domaine."),
        quiz("Que fait HSTS ?",
             ["Chiffre le trafic", "Interdit HTTP au navigateur pendant `max-age`",
              "Renouvelle le certificat", "Compresse les en-têtes"],
             1,
             "Le navigateur refuse toute connexion non chiffrée pendant la durée "
             "indiquée."),
        quiz("Pourquoi utiliser `fullchain.pem` ?",
             ["Il est plus petit", "Il contient les intermédiaires nécessaires",
              "Il n'expire pas", "Il est plus rapide"],
             1,
             "Sans les intermédiaires, la chaîne de confiance est incomplète."),
    ],
}
