from bookkit.dsl import (box, code, defn, ex, fig, h, ol, p, quiz, table, ul)

CH = {
    "title": "HTTP/1.1, HTTP/2 et HTTP/3",
    "subtitle": "Le protocole des applications web, ses versions et ce qu'elles changent "
                "réellement.",
    "duration": "3 h 00",
    "level": "Intermédiaire",
    "prereq": "chapitre 51",
    "objectives": [
        "Décomposer une requête et une réponse HTTP.",
        "Interpréter les méthodes, statuts et en-têtes.",
        "Expliquer ce que chaque version apporte.",
        "Diagnostiquer un problème de cache ou de contenu.",
        "Choisir une configuration de serveur adaptée.",
    ],
    "blocks": [
        h(2, "Un protocole textuel devenu binaire"),
        p("HTTP/1.1 transporte des messages lisibles ; HTTP/2 et HTTP/3 utilisent un "
          "format binaire. Le modèle reste le même : une requête, une réponse, un "
          "ensemble d'en-têtes et un corps optionnel."),
        code("""GET /articles/css-grid HTTP/1.1
Host: exemple.fr
User-Agent: Mozilla/5.0
Accept: text/html,application/xhtml+xml
Accept-Encoding: gzip, br
If-None-Match: "a1b2c3"
Connection: keep-alive""", "http", "Une requête, ligne par ligne"),
        code("""HTTP/1.1 200 OK
Date: Thu, 15 Oct 2026 09:14:00 GMT
Content-Type: text/html; charset=utf-8
Content-Encoding: br
Cache-Control: public, max-age=300
ETag: "d4e5f6"
Vary: Accept-Encoding

<!doctype html>
…""", "http", "La réponse correspondante"),
        table(["Élément", "Rôle", "Taille typique"],
              [["Ligne de requête", "Méthode, cible, version", "20–80 octets"],
               ["En-têtes", "Métadonnées", "300–800 octets"],
               ["Corps", "Contenu", "Variable"],
               ["Ligne de statut", "Code et raison", "20 octets"]],
              widths=[4.0, 4.6, 4.6], first_col_bold=True,
              caption="Quatre parties d'un message"),

        h(2, "Méthodes et idempotence"),
        p("La méthode décrit l'intention. Certaines sont sûres (sans effet de bord), "
          "d'autres idempotentes (rejouables sans effet supplémentaire)."),
        table(["Méthode", "Sûre", "Idempotente", "Corps"],
              [["`GET`", "Oui", "Oui", "Non"],
               ["`HEAD`", "Oui", "Oui", "Non"],
               ["`POST`", "Non", "Non", "Oui"],
               ["`PUT`", "Non", "Oui", "Oui"],
               ["`PATCH`", "Non", "Non", "Oui"],
               ["`DELETE`", "Non", "Oui", "Parfois"]],
              widths=[2.8, 3.0, 3.4, 3.0], first_col_bold=True,
              caption="Six méthodes et leurs garanties"),
        defn("Idempotence HTTP", "Propriété d'une requête qui, répétée à l'identique, "
                                 "laisse le serveur dans le même état. Un `PUT` répété "
                                 "écrit la même ressource ; un `POST` répété crée deux "
                                 "ressources."),

        h(2, "Codes de statut"),
        table(["Classe", "Signification", "Exemples"],
              [["1xx", "Information", "`100 Continue`, `101 Switching Protocols`"],
               ["2xx", "Succès", "`200`, `201`, `204`, `206`"],
               ["3xx", "Redirection", "`301`, `302`, `304`, `307`, `308`"],
               ["4xx", "Erreur du client", "`400`, `401`, `403`, `404`, `409`, `422`, `429`"],
               ["5xx", "Erreur du serveur", "`500`, `502`, `503`, `504`"]],
              widths=[2.2, 4.0, 6.0], first_col_bold=True,
              caption="Cinq classes de codes"),
        code("""302 Found            redirection temporaire (méthode parfois changée)
307 Temporary Redirect  redirection temporaire, méthode préservée
301 Moved Permanently   redirection permanente (cache long)
308 Permanent Redirect  idem, méthode préservée

304 Not Modified      le cache est encore valide
429 Too Many Requests en-tête Retry-After attendu
503 Service Unavailable  surcharge ou maintenance planifiée""", "text",
             "Cinq codes souvent confondus"),
        box("attention", "`301` est mis en cache pour longtemps",
            "Un `301` mal placé reste dans les navigateurs et les caches intermédiaires "
            "pendant des mois. Pour un changement réversible, préférez `302` ou `307`."),

        h(2, "Les trois versions"),
        p("Chaque version répond à une limite de la précédente : le nombre de connexions, "
          "le blocage en tête de ligne, puis la latence d'établissement."),
        table(["Version", "Transport", "Multiplexage", "Limite principale"],
              [["HTTP/1.1", "TCP", "Non (pipelining abandonné)", "Blocage en tête de ligne"],
               ["HTTP/2", "TCP", "Oui, sur une connexion", "Blocage TCP en cas de perte"],
               ["HTTP/3", "QUIC (UDP)", "Oui, indépendant par flux", "Support client à vérifier"]],
              widths=[2.8, 3.4, 4.4, 4.0], first_col_bold=True,
              caption="Trois versions et leurs limites"),
        fig("compare", "Deux approches du multiplexage",
            ("HTTP/1.1", ["Six connexions par domaine", "Blocage en tête de ligne",
                          "En-têtes répétés"],
             "HTTP/2 ET 3", ["Une connexion unique", "Flux indépendants",
                             "En-têtes compressés"]),
            height=210),
        code("""# Vérifier la version réellement négociée
curl -sI --http2 https://exemple.fr | head -1
curl -sI --http3 https://exemple.fr | head -1

# Détails de la négociation TLS et ALPN
openssl s_client -connect exemple.fr:443 -alpn h2 -brief""", "bash",
             "Trois vérifications de version"),

        h(2, "Compression et contenus"),
        p("La compression réduit le poids transféré, au prix d'un peu de processeur. "
          "Elle s'applique au texte, jamais aux formats déjà compressés."),
        table(["Format", "Ratio", "Usage"],
              [["`gzip`", "Bon", "Universel"],
               ["`br` (Brotli)", "Meilleur", "Navigateurs modernes"],
               ["`zstd`", "Très bon et rapide", "Support récent"],
               ["Aucune", "—", "Images JPEG, WebP, vidéos"]],
              widths=[3.0, 3.6, 6.0], first_col_bold=True,
              caption="Quatre options de compression"),
        code("""# Nginx : compression et types concernés
gzip on;
gzip_comp_level 5;
gzip_min_length 256;
gzip_types text/css application/javascript application/json image/svg+xml;

# Ne jamais recompresser ce qui l'est déjà
# (JPEG, PNG, WebP, MP4, ZIP)""", "nginx", "Une configuration équilibrée"),
        defn("Négociation de contenu", "Mécanisme par lequel le client annonce ses "
                                       "capacités (`Accept-Encoding`) et le serveur "
                                       "choisit une représentation. `Vary` indique aux "
                                       "caches que la réponse dépend de cet en-tête."),

        h(2, "Cache HTTP"),
        p("Le cache est le levier de performance le plus rentable, à condition que les "
          "en-têtes soient justes. Deux stratégies se combinent : la fraîcheur et la "
          "revalidation."),
        code("""# Fichier versionné : cache long et immuable
Cache-Control: public, max-age=31536000, immutable

# HTML : toujours revalidé
Cache-Control: no-cache
ETag: "a1b2c3"

# API : fraîcheur courte, tolérance à la péremption
Cache-Control: public, max-age=60, stale-while-revalidate=30

# Donnée personnelle : jamais en cache partagé
Cache-Control: private, no-store""", "http", "Quatre politiques"),
        table(["Directive", "Effet", "Usage"],
              [["`max-age`", "Durée de fraîcheur", "Toutes ressources"],
               ["`no-cache`", "Revalider avant usage", "HTML"],
               ["`no-store`", "Ne pas stocker", "Données sensibles"],
               ["`immutable`", "Ne pas revalider", "Fichiers versionnés"],
               ["`stale-while-revalidate`", "Servir périmé en revalidant", "API"]],
              widths=[5.0, 4.6, 3.6], first_col_bold=True,
              caption="Cinq directives de cache"),
        code("""# Vérifier le comportement du cache
curl -sI https://exemple.fr/app.3f2a91.js | grep -i cache
curl -sI https://exemple.fr/ | grep -iE "etag|cache-control"

# Simuler une revalidation
curl -sI -H 'If-None-Match: "d4e5f6"' https://exemple.fr/ | head -1
# 304 Not Modified si le contenu est inchangé""", "bash",
             "Deux vérifications"),
        box("methode", "Diagnostic HTTP en cinq commandes",
            items=["`curl -I` : statut et en-têtes.",
                   "`curl -v` : échange complet, y compris TLS.",
                   "`curl -w` : chronométrage des étapes.",
                   "`curl -H` : simuler un cache ou un client.",
                   "`openssl s_client` : négociation TLS et ALPN."]),
    ],
    "keypoints": [
        "HTTP/1.1 est textuel, HTTP/2 et 3 sont binaires.",
        "La méthode exprime l'intention ; l'idempotence conditionne les reprises.",
        "Un `301` est mis en cache durablement.",
        "HTTP/2 multiplexe sur une connexion TCP unique.",
        "HTTP/3 supprime le blocage TCP en passant par QUIC.",
        "La compression ne s'applique pas aux formats déjà compressés.",
        "`no-cache` revalide, `no-store` interdit le stockage.",
        "`Vary` protège les variantes d'une réponse.",
    ],
    "bridge": "HTTP circule en clair. Le chapitre suivant ajoute le chiffrement qui "
              "protège et authentifie les échanges : TLS.",
    "exercises": [
        ex("Analyser une réponse",
           "Un fichier statique est rechargé à chaque visite.",
           ["Inspectez les en-têtes.",
            "Identifiez la cause.",
            "Proposez une politique de cache."],
           [("bash", """curl -sI https://exemple.fr/app.js
# HTTP/1.1 200 OK
# Cache-Control: no-cache
# ETag: "a1b2c3"

# Correction : nom versionné + cache long
# app.3f2a91.js
# Cache-Control: public, max-age=31536000, immutable"""),
            "`no-cache` force la revalidation à chaque requête, ce qui coûte un "
            "aller-retour même quand le contenu n'a pas changé.",
            "L'empreinte dans le nom rend le cache long sûr : tout changement produit "
            "une nouvelle URL."]),
        ex("Choisir le bon code",
           "Cinq situations doivent renvoyer un code approprié.",
           ["Création d'une ressource.",
            "Validation échouée.",
            "Trop de requêtes.",
            "Maintenance planifiée.",
            "Redirection permanente."],
           ["201 Created avec en-tête `Location`.",
            "422 Unprocessable Entity avec le détail des champs.",
            "429 Too Many Requests avec `Retry-After`.",
            "503 Service Unavailable avec `Retry-After`.",
            "308 Permanent Redirect, qui préserve la méthode."],
           level="HTTP"),
        ex("Comparer deux versions",
           "Mesurez le chargement d'une page en HTTP/1.1 et en HTTP/2.",
           ["Comptez les connexions.",
            "Comparez le temps total.",
            "Expliquez l'écart."],
           [("bash", """curl -s -o /dev/null -w "%{http_version} %{time_total}\\n" --http1.1 https://exemple.fr
curl -s -o /dev/null -w "%{http_version} %{time_total}\\n" --http2 https://exemple.fr

# Observer les connexions ouvertes dans l'onglet Réseau
# HTTP/1.1 : plusieurs connexions parallèles par domaine"""),
            "HTTP/2 réduit l'écart en multiplexant, mais le gain dépend du nombre de "
            "ressources et de la latence.",
            "Sur une page déjà optimisée et peu fournie, l'écart peut être faible : la "
            "version n'est pas une fin en soi."],
           level="Mesure"),
    ],
    "quiz": [
        quiz("Quelle méthode est idempotente mais non sûre ?",
             ["`GET`", "`PUT`", "`POST`", "`HEAD`"],
             1,
             "`PUT` modifie l'état mais peut être rejoué sans effet supplémentaire."),
        quiz("Que signifie un code 304 ?",
             ["Erreur", "Contenu inchangé, cache valide", "Redirection", "Créé"],
             1,
             "Le client peut réutiliser sa copie en cache."),
        quiz("Sur quel transport repose HTTP/3 ?",
             ["TCP", "QUIC sur UDP", "SCTP", "IP direct"],
             1,
             "QUIC apporte fiabilité et multiplexage au-dessus d'UDP."),
        quiz("Quelle directive interdit tout stockage ?",
             ["`no-cache`", "`no-store`", "`max-age=0`", "`private`"],
             1,
             "`no-store` empêche l'écriture dans tout cache."),
        quiz("Pourquoi ne pas compresser une image JPEG ?",
             ["C'est interdit", "Elle est déjà compressée",
              "Cela change les couleurs", "Cela prend trop de temps"],
             1,
             "La recompression n'apporte presque rien et coûte du processeur."),
    ],
}
