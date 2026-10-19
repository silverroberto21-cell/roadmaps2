from bookkit.dsl import (box, code, defn, ex, fig, h, ol, p, quiz, table, ul)

CH = {
    "title": "DNS : nommer, résoudre, diagnostiquer",
    "subtitle": "Le système qui traduit les noms en adresses, et dont la panne ressemble "
                "souvent à une panne réseau.",
    "duration": "3 h 00",
    "level": "Intermédiaire",
    "prereq": "chapitre 50",
    "objectives": [
        "Décrire la résolution d'un nom, du cache au serveur autoritaire.",
        "Choisir les types d'enregistrements adaptés.",
        "Configurer une zone et des sous-domaines.",
        "Diagnostiquer une résolution lente ou erronée.",
        "Comprendre la propagation et les TTL.",
    ],
    "blocks": [
        h(2, "Une hiérarchie de délégations"),
        p("Le DNS n'est pas un annuaire central : c'est une hiérarchie où chaque niveau "
          "délègue la responsabilité d'une partie des noms. La racine délègue `fr`, qui "
          "délègue `exemple.fr`."),
        fig("tree", "La hiérarchie des noms",
            ("racine (.)", [("fr", ["exemple.fr", "autre.fr"]),
                            ("com", ["exemple.com"]),
                            ("org", ["exemple.org"])]),
            height=235),
        code("""# Les treize serveurs racine (plus leurs instances anycast)
dig . NS +short

# Les serveurs du TLD
dig fr NS +short

# Les serveurs autoritaires d'une zone
dig exemple.fr NS +short""", "bash", "Trois niveaux de délégation"),
        defn("Serveur autoritaire", "Serveur qui détient réellement les données d'une "
                                    "zone. Les résolveurs interrogent les autoritaires "
                                    "puis mettent en cache les réponses."),

        h(2, "Le trajet d'une résolution"),
        p("Un résolveur récursif interroge la hiérarchie à la place du client, puis met "
          "en cache la réponse pendant la durée du TTL. C'est ce cache qui rend le DNS "
          "supportable."),
        fig("flow", "Résolution de www.exemple.fr",
            ["Client → résolveur : question",
             "Résolveur → racine : qui gère .fr ?",
             "Racine → serveurs .fr",
             "Serveurs .fr → autoritaires d'exemple.fr",
             "Autoritaire → enregistrement A",
             "Résolveur → client : réponse mise en cache"],
            height=265),
        code("""# Interroger un résolveur précis
dig @1.1.1.1 www.exemple.fr A
dig @8.8.8.8 www.exemple.fr AAAA

# Voir la délégation complète
dig +trace www.exemple.fr

# Mesurer le temps de résolution
dig www.exemple.fr | grep "Query time"

# Connaître le résolveur utilisé
resolvectl status
cat /etc/resolv.conf""", "bash", "Six commandes de résolution"),
        table(["Outil", "Usage", "Avantage"],
              [["`dig`", "Requête détaillée", "Référence, sortie complète"],
               ["`host`", "Réponse courte", "Rapide à lire"],
               ["`nslookup`", "Interactif", "Disponible partout"],
               ["`drill`", "Équivalent `dig`", "DNSSEC lisible"],
               ["`resolvectl query`", "Intégré à systemd", "Résout via les résolveurs"]],
              widths=[3.4, 4.6, 4.4], first_col_bold=True,
              caption="Cinq outils de requête"),

        h(2, "Les types d'enregistrements"),
        p("Un nom porte plusieurs types d'informations. Chacun a un usage précis, et "
          "certains sont indispensables à la messagerie ou à la sécurité."),
        table(["Type", "Rôle", "Exemple"],
              [["`A`", "Adresse IPv4", "`www 300 IN A 203.0.113.10`"],
               ["`AAAA`", "Adresse IPv6", "`www 300 IN AAAA 2001:db8::10`"],
               ["`CNAME`", "Alias vers un autre nom", "`blog IN CNAME www`"],
               ["`MX`", "Serveur de messagerie", "`@ IN MX 10 mail`"],
               ["`TXT`", "Texte libre", "SPF, vérification de domaine"],
               ["`NS`", "Serveurs de la zone", "`@ IN NS ns1`"],
               ["`SRV`", "Service et port", "`_https._tcp IN SRV 0 5 443 www`"],
               ["`CAA`", "Autorités de certification", "`@ IN CAA 0 issue \"letsencrypt.org\"`"]],
              widths=[2.4, 4.4, 5.6], first_col_bold=True,
              caption="Huit types d'enregistrements"),
        code("""; Zone exemple.fr
$TTL 3600
@   IN SOA ns1.exemple.fr. admin.exemple.fr. (
        2026031401 ; numéro de série
        7200       ; rafraîchissement
        3600       ; réessai
        1209600    ; expiration
        300 )      ; TTL négatif

@       IN NS   ns1.exemple.fr.
@       IN NS   ns2.exemple.fr.
@       IN A    203.0.113.10
www     IN A    203.0.113.10
api     IN CNAME www
@       IN MX   10 mail.exemple.fr.
@       IN TXT  "v=spf1 mx -all"
mail    IN A    203.0.113.20""", "text", "Une zone complète"),
        defn("SOA", "Start of Authority : enregistrement qui identifie le serveur "
                    "primaire, l'administrateur, et les durées de rafraîchissement. "
                    "Son numéro de série doit augmenter à chaque modification, sinon "
                    "les serveurs secondaires ne se mettent pas à jour."),
        box("attention", "CNAME n'est pas universel",
            "Un CNAME ne peut pas coexister avec d'autres enregistrements au même nom. "
            "On ne met donc jamais de CNAME à la racine du domaine (`@`) : utilisez un "
            "enregistrement `A`/`AAAA`, ou un mécanisme d'alias fourni par le "
            "gestionnaire de zone."),

        h(2, "TTL et propagation"),
        p("Le TTL indique combien de temps un résolveur peut conserver la réponse. Un TTL "
          "long réduit le trafic ; un TTL court accélère les changements. « La "
          "propagation » n'est rien d'autre que l'expiration progressive des caches."),
        table(["Contexte", "TTL conseillé", "Raison"],
              [["Enregistrement stable", "3600 à 86400", "Peu de requêtes"],
               ["Avant une migration", "300", "Bascule rapide"],
               ["Après migration", "3600", "Retour à la normale"],
               ["Service critique", "60 à 300", "Bascule en cas d'incident"],
               ["Enregistrement expérimental", "60", "Itération"]],
              widths=[4.0, 3.6, 4.8], first_col_bold=True,
              caption="Cinq politiques de TTL"),
        code("""# Vérifier depuis plusieurs résolveurs publics
for r in 1.1.1.1 8.8.8.8 9.9.9.9; do
  echo "— $r"
  dig @$r +short www.exemple.fr
done

# Vérifier le TTL restant
dig www.exemple.fr | grep -A1 "ANSWER SECTION\"""", "bash",
             "Deux vérifications de cohérence"),
        p("Baisser le TTL à 300 secondes **avant** une migration évite une fenêtre de "
          "plusieurs heures pendant laquelle une partie des visiteurs atteint encore "
          "l'ancienne adresse."),

        h(2, "Diagnostiquer"),
        p("Trois symptômes reviennent : le nom ne résout pas, il résout vers la mauvaise "
          "adresse, ou la résolution est lente. Chacun a des causes distinctes."),
        table(["Symptôme", "Cause probable", "Vérification"],
              [["NXDOMAIN", "Nom absent ou faute de frappe", "`dig` sur la zone"],
               ["SERVFAIL", "Zone cassée ou DNSSEC invalide", "`dig +dnssec`"],
               ["Mauvaise adresse", "Cache ancien ou zone non mise à jour",
                "TTL et numéro de série"],
               ["Lenteur", "Résolveur distant ou timeouts", "`dig` chronométré"],
               ["Échec intermittent", "Serveurs secondaires incohérents", "Interroger chaque NS"]],
              widths=[3.4, 4.6, 4.6], first_col_bold=True,
              caption="Cinq symptômes et leurs causes"),
        code("""# Interroger directement un serveur autoritaire
dig @ns1.exemple.fr www.exemple.fr A

# Vérifier la cohérence entre serveurs
for ns in $(dig +short NS exemple.fr); do
  echo "— $ns"
  dig @$ns +short www.exemple.fr
done

# Vérifier DNSSEC
dig +dnssec exemple.fr
delv exemple.fr

# Vider les caches locaux
resolvectl flush-caches
systemd-resolve --flush-caches 2>/dev/null || true""", "bash",
             "Quatre vérifications"),
        defn("DNSSEC", "Extension qui signe cryptographiquement les réponses DNS. Elle "
                       "protège contre l'empoisonnement de cache, mais ne chiffre pas "
                       "les requêtes : c'est le rôle de DoH et DoT."),
        box("methode", "Diagnostic DNS en quatre commandes",
            items=["`dig nom` : la réponse est-elle correcte ?",
                   "`dig @1.1.1.1 nom` : le résolveur local est-il en cause ?",
                   "`dig @ns1.zone nom` : la zone autoritaire est-elle à jour ?",
                   "`dig +trace nom` : où la délégation casse-t-elle ?"]),
    ],
    "keypoints": [
        "Le DNS est une hiérarchie de délégations, pas un annuaire central.",
        "Un résolveur récursif interroge la hiérarchie puis met en cache.",
        "Chaque type d'enregistrement a un usage précis.",
        "Un CNAME ne cohabite pas avec d'autres enregistrements.",
        "Le numéro de série SOA déclenche la propagation vers les secondaires.",
        "Le TTL détermine la durée de vie dans les caches.",
        "Baisser le TTL avant une migration évite une bascule partielle.",
        "`dig` et `+trace` localisent une panne de délégation.",
    ],
    "bridge": "Les noms résolvent. Le chapitre suivant décrit le protocole qui transporte "
              "les pages : HTTP.",
    "exercises": [
        ex("Créer une zone",
           "Le domaine `exemple.fr` doit servir un site et du courrier.",
           ["Déclarez les serveurs de noms.",
            "Ajoutez A, MX, TXT et CAA.",
            "Vérifiez avec `dig`."],
           [("text", """$TTL 300
@   IN SOA ns1.exemple.fr. admin.exemple.fr. (
        2026031501 7200 3600 1209600 300 )
@   IN NS  ns1.exemple.fr.
@   IN NS  ns2.exemple.fr.
@   IN A   203.0.113.10
www IN A   203.0.113.10
@   IN MX  10 mail.exemple.fr.
mail IN A  203.0.113.20
@   IN TXT "v=spf1 mx -all"
@   IN CAA 0 issue "letsencrypt.org\""""),
            "Un TTL de 300 facilite les ajustements pendant la mise en place.",
            "SPF et CAA sont deux enregistrements souvent oubliés qui conditionnent la "
            "délivrabilité du courrier et l'émission de certificats."]),
        ex("Diagnostiquer une résolution erronée",
           "Le site répond sur l'ancienne adresse après une migration.",
           ["Interrogez plusieurs résolveurs.",
            "Vérifiez le TTL restant.",
            "Vérifiez la zone autoritaire."],
           [("code", """dig +short www.exemple.fr
dig @1.1.1.1 +short www.exemple.fr
dig @ns1.exemple.fr +short www.exemple.fr

# Si l'autoritaire est correct et le résolveur faux : cache
dig www.exemple.fr | grep -E "TTL|Query time"
# Attendre l'expiration, ou demander la purge au fournisseur"""),
            "Un écart entre autoritaire et résolveur public est un cache non expiré, pas "
            "une zone mal configurée.",
            "Interroger chaque serveur de noms révèle une réplication incomplète entre "
            "primaire et secondaires."],
           level="Diagnostic"),
        ex("Vérifier une configuration de courrier",
           "Les messages partent mais arrivent en spam.",
           ["Vérifiez MX, SPF, DKIM et DMARC.",
            "Contrôlez la cohérence des noms.",
            "Vérifiez les enregistrements publics."],
           [("code", """dig +short MX exemple.fr
dig +short TXT exemple.fr
dig +short TXT _dmarc.exemple.fr
dig +short TXT selector1._domainkey.exemple.fr
dig +short -x 203.0.113.20     # nom inverse"""),
            "SPF autorise les serveurs d'envoi, DKIM signe les messages, DMARC indique "
            "la politique en cas d'échec.",
            "Un enregistrement inverse (PTR) cohérent améliore fortement la "
            "délivrabilité."],
           level="Diagnostic"),
    ],
    "quiz": [
        quiz("Quel type associe un nom à une adresse IPv4 ?",
             ["`AAAA`", "`A`", "`MX`", "`CNAME`"],
             1,
             "`A` contient une adresse IPv4, `AAAA` une adresse IPv6."),
        quiz("Que détermine le TTL ?",
             ["La vitesse du serveur", "La durée de mise en cache",
              "Le nombre de requêtes", "La priorité des MX"],
             1,
             "Chaque résolveur peut conserver la réponse pendant cette durée."),
        quiz("Pourquoi éviter un CNAME à la racine ?",
             ["C'est interdit par la loi", "Il ne peut coexister avec SOA et NS",
              "Il est trop lent", "Il casse TLS"],
             1,
             "Le CNAME exclut tout autre enregistrement au même nom."),
        quiz("Que signifie NXDOMAIN ?",
             ["Erreur serveur", "Le nom n'existe pas", "Zone expirée", "Timeout"],
             1,
             "Le nom demandé n'existe pas dans la zone."),
        quiz("Que fait `dig +trace` ?",
             ["Mesure le temps", "Suit la délégation depuis la racine",
              "Vide le cache", "Signe la requête"],
             1,
             "Il montre chaque étape de la résolution hiérarchique."),
    ],
}
