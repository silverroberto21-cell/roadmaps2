from bookkit.dsl import (box, code, defn, ex, fig, h, ol, p, quiz, table, ul)

CH = {
    "title": "Répartition de charge, proxy et CDN",
    "subtitle": "Répartir le trafic, absorber les pannes et rapprocher les contenus des "
                "utilisateurs.",
    "duration": "3 h 00",
    "level": "Intermédiaire",
    "prereq": "chapitre 55",
    "objectives": [
        "Choisir un algorithme de répartition adapté.",
        "Configurer une vérification de santé utile.",
        "Distinguer proxy inverse, proxy direct et CDN.",
        "Comprendre la terminaison TLS et le reroutage.",
        "Éviter les pièges de session et de cache.",
    ],
    "blocks": [
        h(2, "Ce que répartit un équilibreur"),
        p("Un équilibreur de charge distribue les requêtes entre plusieurs instances. "
          "Il apporte aussi la détection de panne, la terminaison TLS et parfois la "
          "limitation de débit."),
        fig("flow", "Une architecture à trois niveaux",
            ["Clients",
             "Équilibreur (TLS, routage)",
             "Instance 1 / Instance 2 / Instance 3",
             "Base de données partagée",
             "Journaux et métriques centralisés"],
            height=250),
        table(["Algorithme", "Principe", "Adapté à"],
              [["Round-robin", "Chacun son tour", "Instances équivalentes"],
               ["Least connections", "La moins chargée", "Requêtes longues"],
               ["IP hash", "Même client, même instance", "Sessions en mémoire"],
               ["Weighted", "Poids par capacité", "Machines hétérogènes"],
               ["Random", "Au hasard", "Grandes flottes"]],
              widths=[4.0, 4.8, 4.4], first_col_bold=True,
              caption="Cinq algorithmes"),
        code("""# Nginx : groupe d'amont
upstream application {
    least_conn;
    server 10.0.0.11:3000 max_fails=3 fail_timeout=30s;
    server 10.0.0.12:3000 max_fails=3 fail_timeout=30s;
    server 10.0.0.13:3000 backup;
    keepalive 32;
}

server {
    listen 443 ssl;
    server_name exemple.fr;
    # ...
    location / {
        proxy_pass http://application;
        proxy_next_upstream error timeout http_502 http_503;
        proxy_connect_timeout 2s;
        proxy_read_timeout 30s;
    }
}""", "nginx", "Un groupe avec secours"),
        defn("`backup`", "Serveur qui ne reçoit de trafic que si tous les autres sont "
                         "indisponibles. Utile pour une instance de secours ou une "
                         "version de maintenance."),
        box("attention", "Les sessions en mémoire cassent la répartition",
            "Si chaque instance garde la session dans sa mémoire, un utilisateur "
            "connecté sur l'instance 1 est déconnecté quand il tombe sur l'instance 2. "
            "Deux solutions : sessions partagées (base, Redis) ou affinité de session."),

        h(2, "Vérifications de santé"),
        p("Une vérification de santé qui ne teste que la connexion TCP est insuffisante : "
          "une application peut accepter des connexions et ne plus répondre. Un point "
          "d'entrée dédié doit vérifier les dépendances essentielles."),
        code("""# Nginx open source : vérification passive
# (max_fails / fail_timeout observent les échecs réels)
# Nginx Plus ajoute la vérification active.

# Alternative : HAProxy
backend application
    option httpchk GET /health
    http-check expect status 200
    default-server inter 3s fall 3 rise 2
    server app1 10.0.0.11:3000 check
    server app2 10.0.0.12:3000 check""", "text", "Deux approches"),
        code("""# Le point d'entrée doit rester simple et rapide
app.get("/health", async (req, res) => {
  try {
    await db.query("SELECT 1");
    res.json({ statut: "ok", version: process.env.VERSION });
  } catch (e) {
    res.status(503).json({ statut: "degrade", erreur: e.message });
  }
});""", "js", "Un point de santé utile"),
        table(["Niveau", "Teste", "Risque"],
              [["TCP", "Le port écoute", "Application bloquée acceptée"],
               ["HTTP 200", "Le processus répond", "Base inaccessible ignorée"],
               ["Dépendances", "Base, cache, files", "Santé trop stricte : tout tombe"],
               ["Synthétique", "Parcours utilisateur", "Coût et complexité"]],
              widths=[3.2, 4.6, 5.0], first_col_bold=True,
              caption="Quatre niveaux de vérification"),
        defn("Santé stricte ou tolérante", "Une vérification qui inclut toutes les "
                                           "dépendances peut retirer toutes les instances "
                                           "simultanément lors d'une panne de base. "
                                           "Distinguez `/health` (vivacité) et "
                                           "`/ready` (capacité à servir)."),

        h(2, "Proxy inverse et proxy direct"),
        p("Un proxy inverse représente les serveurs face aux clients ; un proxy direct "
          "représente les clients face aux serveurs. Les deux partagent la même "
          "technologie, mais pas le même rôle."),
        table(["Critère", "Proxy inverse", "Proxy direct"],
              [["Représente", "Les serveurs", "Les clients"],
               ["Position", "Devant l'application", "Devant le navigateur"],
               ["Usage", "TLS, routage, cache", "Filtrage, anonymisation"],
               ["Exemple", "Nginx, Traefik", "Squid, Envoy sortant"]],
              widths=[3.4, 4.8, 4.8], first_col_bold=True,
              caption="Quatre différences"),
        code("""# Proxy sortant : forcer une sortie par une IP fixe
proxy_pass http://sortie.interne:3128;

# Côté client, variables d'environnement
export HTTPS_PROXY=http://proxy.interne:3128
export NO_PROXY=localhost,127.0.0.1,.interne""", "bash",
             "Deux configurations courantes"),
        p("Un proxy sortant avec IP fixe est souvent exigé par les partenaires : ils "
          "autorisent une adresse, pas une plage entière. C'est aussi un point de "
          "journalisation centralisé."),

        h(2, "CDN"),
        p("Un réseau de distribution de contenu place des copies à proximité des "
          "utilisateurs. Le gain principal est la latence, puis la réduction de charge "
          "sur l'origine."),
        fig("columns", "Ce qu'un CDN apporte",
            [("LATENCE", ["Points de présence", "Connexions préétablies", "HTTP/3"]),
             ("CHARGE", ["Cache de bord", "Compression", "Absorption des pics"]),
             ("SÉCURITÉ", ["TLS géré", "Filtrage L3/L7", "Atténuation DDoS"])],
            height=200),
        code("""# En-têtes de cache appropriés pour un CDN
Cache-Control: public, max-age=300, s-maxage=3600, stale-while-revalidate=60

# Purger une URL après publication
curl -X POST https://api.cdn.exemple/purge \\
  -H "Authorization: Bearer $TOKEN" \\
  -H "Content-Type: application/json" \\
  -d '{"urls":["https://exemple.fr/article/12"]}'""", "http",
             "Deux opérations essentielles"),
        table(["Contenu", "Cache CDN", "Durée"],
              [["Image versionnée", "Oui", "1 an, immuable"],
               ["CSS/JS versionnés", "Oui", "1 an, immuable"],
               ["HTML public", "Oui, avec revalidation", "Minutes"],
               ["API publique", "Selon `s-maxage`", "Secondes à minutes"],
               ["Contenu personnalisé", "Non", "`private, no-store`"]],
              widths=[4.2, 4.4, 4.4], first_col_bold=True,
              caption="Cinq contenus et leur cache"),
        box("attention", "Le cache de bord cache aussi vos erreurs",
            "Une réponse 404 ou 500 mise en cache avec un `max-age` long reste servie "
            "après correction. Configurez un cache court pour les erreurs, ou purgez "
            "explicitement."),

        h(2, "Pannes et dégradation"),
        p("La répartition de charge doit être testée en panne : couper une instance, "
          "saturer une base, retirer un nœud. Une architecture non testée en panne est "
          "une hypothèse."),
        code("""# Test de résilience simple
# 1. Deux instances actives derrière l'équilibreur
# 2. Arrêt de l'instance 1
systemctl stop app@1
# 3. Vérifier que le trafic continue
for i in $(seq 50); do curl -s -o /dev/null -w "%{http_code} " https://exemple.fr/; done
# 4. Redémarrer et vérifier le retour en circulation""", "bash",
             "Un test reproductible"),
        table(["Mode de panne", "Symptôme", "Mitigation"],
              [["Instance morte", "Erreurs 502", "Vérification de santé"],
               ["Instance lente", "Latence, 499", "Délai et disjoncteur"],
               ["Base saturée", "Erreurs 500", "Cache, file d'attente"],
               ["Zone disponible indisponible", "Latence accrue", "Multi-zone"],
               ["Pic de trafic", "Saturation CPU", "Autoscaling, CDN"]],
              widths=[4.4, 4.2, 4.4], first_col_bold=True,
              caption="Cinq modes de panne"),
        defn("Disjoncteur", "Mécanisme qui cesse d'appeler une dépendance défaillante "
                            "pendant un délai, au lieu d'attendre son délai d'expiration "
                            "à chaque requête. Il protège la ressource et la latence."),
        box("methode", "Contrôles d'une architecture répartie",
            items=["Chaque instance est remplaçable sans état local.",
                   "Le point de santé distingue vivacité et capacité.",
                   "Le cache est purgé à chaque publication.",
                   "Une panne d'instance est testée régulièrement.",
                   "Les journaux portent l'identifiant de requête."]),
    ],
    "keypoints": [
        "L'algorithme dépend de la durée des requêtes et de l'homogénéité des instances.",
        "Les sessions en mémoire imposent une affinité ou un stockage partagé.",
        "Une vérification TCP ne prouve pas que l'application sert.",
        "Vivacité et capacité à servir sont deux questions distinctes.",
        "Un proxy inverse représente les serveurs, un proxy direct les clients.",
        "Un CDN réduit la latence et absorbe les pics.",
        "Les erreurs ne doivent pas être mises en cache longtemps.",
        "Une architecture de répartition se teste en panne.",
    ],
    "bridge": "L'infrastructure réseau est complète. La partie suivante entre dans les "
              "conteneurs et l'orchestration.",
    "exercises": [
        ex("Configurer un amont avec secours",
           "Deux instances actives et une de secours.",
           ["Définissez les délais.",
            "Activez le passage à l'instance suivante.",
            "Testez l'arrêt d'une instance."],
           [("nginx", """upstream application {
    least_conn;
    server 10.0.0.11:3000 max_fails=3 fail_timeout=30s;
    server 10.0.0.12:3000 max_fails=3 fail_timeout=30s;
    server 10.0.0.13:3000 backup;
    keepalive 32;
}

location / {
    proxy_pass http://application;
    proxy_connect_timeout 2s;
    proxy_read_timeout 30s;
    proxy_next_upstream error timeout http_502 http_503;
}"""),
            "Un délai de connexion court évite d'attendre une instance morte avant de "
            "passer à la suivante.",
            "`max_fails` et `fail_timeout` écartent temporairement une instance "
            "défaillante, sans intervention."]),
        ex("Choisir un algorithme",
           "Trois cas : API rapide, téléchargements longs, session en mémoire.",
           ["Justifiez chaque choix.",
            "Précisez la conséquence d'une panne.",
            "Indiquez l'alternative."],
           ["API rapide : round-robin, les instances sont interchangeables.",
            "Téléchargements longs : `least_conn`, pour ne pas empiler sur une instance "
            "déjà occupée.",
            "Session en mémoire : IP hash ou, mieux, sortir la session vers Redis pour "
            "retrouver l'interchangeabilité."],
           level="Architecture"),
        ex("Diagnostiquer une latence en pic",
           "Les temps de réponse augmentent brutalement à certaines heures.",
           ["Comparez les temps applicatifs et réseau.",
            "Vérifiez le cache.",
            "Cherchez une dépendance lente."],
           [("bash", """# Temps de réponse par minute
awk '{print $4, $NF}' /var/log/nginx/access.log \\
  | cut -c1-17 | sort | uniq -c | tail -20

# Temps amont (dernier champ du format enrichi)
awk '{print $(NF-2)}' /var/log/nginx/access.log | sort -n | tail -5

# Cache : taux de succès
grep -c " 200 " /var/log/nginx/access.log
grep -c " 304 " /var/log/nginx/access.log"""),
            "Un temps total élevé avec un temps amont faible indique un problème réseau "
            "ou de sérialisation côté proxy.",
            "Un temps amont élevé désigne l'application ou l'une de ses dépendances."],
           level="Diagnostic"),
    ],
    "quiz": [
        quiz("Quel algorithme convient à des sessions en mémoire ?",
             ["Round-robin", "IP hash", "Least connections", "Random"],
             1,
             "L'affinité par adresse envoie un client toujours vers la même instance."),
        quiz("Pourquoi une vérification TCP est-elle insuffisante ?",
             ["Elle est trop lente", "Elle ne prouve pas que l'application répond",
              "Elle nécessite root", "Elle ne fonctionne pas"],
             1,
             "Un processus bloqué peut accepter des connexions sans servir."),
        quiz("Que fait un CDN ?",
             ["Compile le code", "Rapproche les contenus des utilisateurs",
              "Gère les bases", "Remplace le DNS"],
             1,
             "Il met en cache au plus près des clients et absorbe la charge."),
        quiz("Pourquoi ne pas mettre en cache une erreur 500 ?",
             ["C'est interdit", "Elle resterait servie après correction",
              "Cela consomme trop", "Cela casse TLS"],
             1,
             "Un cache de bord persistant continue de servir l'erreur."),
        quiz("Qu'est-ce qu'un disjoncteur ?",
             ["Un fusible électrique", "Un arrêt temporaire des appels à une dépendance",
              "Un type de proxy", "Un algorithme de répartition"],
             1,
             "Il évite d'accumuler des attentes sur une dépendance défaillante."),
    ],
}
