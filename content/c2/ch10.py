from bookkit.dsl import (box, code, defn, ex, fig, h, ol, p, quiz, table, ul)

CH = {
    "title": "Adressage IP, sous-réseaux et routage",
    "subtitle": "Découper un réseau en blocs cohérents et comprendre pourquoi une "
                "adresse est joignable ou non.",
    "duration": "3 h 15",
    "level": "Intermédiaire",
    "prereq": "chapitre 49",
    "objectives": [
        "Lire une adresse IPv4 et son masque.",
        "Calculer un réseau, une diffusion et une plage utile.",
        "Découper un réseau en sous-réseaux.",
        "Comprendre NAT et adressage privé.",
        "Lire et modifier une table de routage.",
    ],
    "blocks": [
        h(2, "Une adresse, un masque"),
        p("Une adresse IPv4 est un nombre de 32 bits écrit en quatre octets. Le masque "
          "indique combien de bits identifient le réseau ; les bits restants identifient "
          "l'hôte."),
        code("""192.168.10.42
11000000.10101000.00001010.00101010

Masque 255.255.255.0  =  /24
11111111.11111111.11111111.00000000
         réseau (24 bits)      hôtes (8 bits)

Réseau    : 192.168.10.0
Premier   : 192.168.10.1
Dernier   : 192.168.10.254
Diffusion : 192.168.10.255
Hôtes     : 254 (2^8 - 2)""", "text", "Une adresse décodée"),
        table(["Préfixe", "Masque", "Adresses", "Hôtes utiles"],
              [["/24", "255.255.255.0", "256", "254"],
               ["/25", "255.255.255.128", "128", "126"],
               ["/26", "255.255.255.192", "64", "62"],
               ["/27", "255.255.255.224", "32", "30"],
               ["/28", "255.255.255.240", "16", "14"],
               ["/30", "255.255.255.252", "4", "2"],
               ["/31", "255.255.255.254", "2", "2 (lien point à point)"],
               ["/32", "255.255.255.255", "1", "1 (hôte seul)"]],
              widths=[2.4, 4.4, 3.0, 3.6], first_col_bold=True,
              caption="Huit préfixes courants"),
        defn("CIDR", "Notation qui exprime le masque par le nombre de bits de réseau, "
                      "par exemple `/24`. Elle remplace les anciennes classes A, B et C."),
        p("Deux adresses sont réservées dans chaque sous-réseau : celle dont tous les "
          "bits d'hôte valent 0 désigne le réseau, celle dont tous les bits valent 1 "
          "sert à la diffusion. D'où la règle `2^n - 2`."),

        h(2, "Découper un réseau"),
        p("Découper un /24 en quatre /26 est l'exercice de base. Chaque sous-réseau "
          "avance de 64 adresses : on ajoute ce pas à l'adresse réseau précédente."),
        code("""Réseau de départ : 192.168.10.0/24

/26 → 4 sous-réseaux de 64 adresses, 62 hôtes utiles

1. 192.168.10.0/26    .1  → .62     diffusion .63
2. 192.168.10.64/26   .65 → .126    diffusion .127
3. 192.168.10.128/26  .129 → .190   diffusion .191
4. 192.168.10.192/26  .193 → .254   diffusion .255""", "text",
             "Un découpage en quatre"),
        code("""# Calculs rapides avec ipcalc
ipcalc 192.168.10.42/26
ipcalc -n 192.168.10.42/26
ipcalc -r 10.0.0.0/22

# Vérifier la cohérence d'un plan d'adressage
# /22 couvre 10.0.0.0 à 10.0.3.255 : attention aux chevauchements""", "bash",
             "Trois vérifications"),
        table(["Besoin", "Taille conseillée", "Remarque"],
              [["Lien point à point", "/30 ou /31", "Deux adresses"],
               ["Petit service", "/28", "14 hôtes"],
               ["Bureau", "/26", "62 hôtes"],
               ["Étage", "/24", "254 hôtes"],
               ["Site", "/22 ou plus", "Planifier la croissance"]],
              widths=[4.0, 4.0, 4.2], first_col_bold=True,
              caption="Cinq tailles selon l'usage"),
        box("attention", "Un chevauchement casse le routage",
            "Deux sous-réseaux qui se recouvrent rendent le routage ambigu : certaines "
            "adresses sont joignables par deux chemins. Un plan d'adressage se dessine "
            "et se documente avant tout déploiement."),

        h(2, "Adresses privées et NAT"),
        p("Trois blocs sont réservés aux réseaux privés et ne sont pas routés sur "
          "Internet. Le NAT traduit une adresse privée en adresse publique pour sortir."),
        table(["Bloc", "Plage", "Taille", "Usage"],
              [["10.0.0.0/8", "10.0.0.0 – 10.255.255.255", "16,7 M", "Grands réseaux"],
               ["172.16.0.0/12", "172.16.0.0 – 172.31.255.255", "1 M", "Réseaux moyens"],
               ["192.168.0.0/16", "192.168.0.0 – 192.168.255.255", "65 536", "Maisons, PME"],
               ["100.64.0.0/10", "100.64.0.0 – 100.127.255.255", "4 M", "Opérateurs (CGNAT)"]],
              widths=[3.2, 5.6, 2.4, 3.2], first_col_bold=True,
              caption="Quatre plages réservées"),
        code("""# NAT sortant (masquerade) sur un routeur Linux
iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
sysctl -w net.ipv4.ip_forward=1

# Équivalent nftables
nft add table ip nat
nft add chain ip nat postrouting '{ type nat hook postrouting priority 100; }'
nft add rule ip nat postrouting oifname "eth0" masquerade""", "bash",
             "Deux écritures du même NAT"),
        defn("CGNAT", "Carrier-Grade NAT : plusieurs abonnés partagent une adresse "
                      "publique. Conséquence : l'IPv4 seule ne permet plus d'héberger "
                      "un service joignable de l'extérieur sans mécanisme dédié."),
        p("IPv6 supprime la pénurie d'adresses : 128 bits, soit un nombre d'adresses "
          "considérable. Chaque appareil peut avoir une adresse publique ; la "
          "protection repose alors sur le pare-feu, pas sur la traduction d'adresses."),

        h(2, "Routage"),
        p("Un hôte compare l'adresse de destination à son masque. Si elle est dans le "
          "même réseau, il écrit directement ; sinon, il envoie à la passerelle."),
        fig("flow", "La décision de routage",
            ["Destination dans mon réseau ?",
             "Oui → envoi direct par ARP",
             "Non → envoi à la passerelle par défaut",
             "Le routeur consulte sa table",
             "Route correspondante → prochain saut",
             "Aucune route → ICMP destination unreachable"],
            height=255),
        code("""ip route
# default via 192.168.1.1 dev eth0
# 192.168.1.0/24 dev eth0 scope link

# Ajouter une route vers un réseau interne via un tunnel
ip route add 10.20.0.0/16 via 192.168.1.5 dev eth0

# Route plus spécifique = prioritaire, quelle que soit la métrique
# 10.20.5.0/24 l'emporte sur 10.20.0.0/16

# Vérifier le chemin réellement utilisé
ip route get 10.20.5.17""", "bash", "Quatre opérations de routage"),
        table(["Commande", "Effet", "Persistance"],
              [["`ip route add`", "Route immédiate", "Perdue au redémarrage"],
               ["`ip route replace`", "Remplace une route", "Immédiate"],
               ["`ip route del`", "Supprime", "Immédiate"],
               ["`nmcli`", "Route persistante", "Survit au redémarrage"],
               ["`/etc/network/interfaces`", "Debian classique", "Au redémarrage"]],
              widths=[4.0, 4.4, 4.0], first_col_bold=True,
              caption="Cinq façons de gérer une route"),
        code("""# Passerelle par défaut avec NetworkManager
nmcli connection modify eth0 ipv4.gateway 192.168.1.1
nmcli connection modify eth0 +ipv4.routes "10.20.0.0/16 192.168.1.5"
nmcli connection up eth0""", "bash", "Deux routes persistantes"),
        box("pratique", "Toujours vérifier avec `ip route get`",
            "Cette commande indique la route réellement choisie pour une destination, "
            "ce qui évite de raisonner sur une table incomplète ou mal comprise."),
        box("methode", "Concevoir un plan d'adressage",
            items=["Lister les sites, services et liens.",
                   "Attribuer un bloc par site, avec marge de croissance.",
                   "Documenter réseau, masque, passerelle et VLAN.",
                   "Réserver les premières et dernières adresses.",
                   "Versionner le plan avec l'infrastructure."]),
    ],
    "keypoints": [
        "Une adresse IPv4 fait 32 bits ; le masque sépare réseau et hôtes.",
        "Deux adresses par sous-réseau sont réservées : réseau et diffusion.",
        "`2^n - 2` donne le nombre d'hôtes utiles.",
        "/31 et /32 ont des usages particuliers.",
        "Trois blocs sont réservés aux réseaux privés.",
        "Le NAT traduit les adresses privées pour sortir.",
        "La route la plus spécifique est prioritaire.",
        "`ip route get` montre la décision réelle.",
    ],
    "bridge": "Les adresses circulent. Reste à les nommer : le chapitre suivant traite "
              "du DNS.",
    "exercises": [
        ex("Découper un /24 en trois sous-réseaux",
           "Il faut 100, 50 et 20 hôtes.",
           ["Choisissez les préfixes.",
            "Calculez les plages.",
            "Vérifiez les chevauchements."],
           [("code", """100 hôtes → /25 (126 utiles)  192.168.10.0/25
 50 hôtes → /26 (62 utiles)   192.168.10.128/26
 20 hôtes → /27 (30 utiles)   192.168.10.192/27

# Reste : 192.168.10.224/27 pour la croissance

ipcalc 192.168.10.128/26
ipcalc 192.168.10.192/27"""),
            "On arrondit toujours au préfixe immédiatement supérieur au besoin : 100 "
            "hôtes exigent /25, pas /26 (62).",
            "Documenter la plage restante évite de la réattribuer par erreur plus tard."]),
        ex("Diagnostiquer un conflit d'adresses",
           "Deux machines répondent à la même adresse IP.",
           ["Repérez la duplication.",
            "Identifiez les deux machines.",
            "Corrigez et prévenez."],
           [("code", """# Observer les conflits ARP
ip -s neigh | grep -i fail
arping -D -I eth0 192.168.1.50

# Vérifier la configuration
ip addr show

# Prévention : réservation DHCP par adresse MAC
# Dans le serveur DHCP : host poste-12 { hardware ethernet ...; fixed-address ...; }"""),
            "Un conflit se manifeste par des coupures intermittentes, des entrées ARP "
            "instables et des erreurs `duplicate address detected` dans le journal.",
            "La réservation DHCP centralise l'attribution : deux administrateurs ne "
            "peuvent plus attribuer la même adresse à la main."],
           level="Diagnostic"),
        ex("Vérifier une route asymétrique",
           "Le serveur répond, mais les connexions TCP n'aboutissent pas.",
           ["Vérifiez les tables des deux côtés.",
            "Comparez les chemins aller et retour.",
            "Corrigez la passerelle."],
           [("code", """ip route get 203.0.113.10
traceroute -n 203.0.113.10
# Sur le serveur distant
ip route get <adresse-du-client>"""),
            "Une route asymétrique peut casser TLS ou les pare-feux stateful : les "
            "paquets de retour ne suivent pas le chemin attendu.",
            "Comparer `ip route get` des deux côtés identifie immédiatement la "
            "divergence de passerelle."],
           level="Diagnostic"),
    ],
    "quiz": [
        quiz("Combien d'hôtes utiles dans un /26 ?",
             ["64", "62", "30", "126"],
             1,
             "2^6 - 2 = 62 hôtes utiles."),
        quiz("Quelle est l'adresse de diffusion d'un /24 en 192.168.1.0 ?",
             ["192.168.1.0", "192.168.1.1", "192.168.1.255", "192.168.1.254"],
             2,
             "L'adresse de diffusion a tous les bits d'hôte à 1."),
        quiz("Quel bloc est réservé aux réseaux privés ?",
             ["8.8.8.0/24", "172.16.0.0/12", "1.1.1.0/24", "203.0.113.0/24"],
             1,
             "Les trois blocs privés sont 10/8, 172.16/12 et 192.168/16."),
        quiz("Comment un hôte décide-t-il d'utiliser la passerelle ?",
             ["Au hasard", "En comparant la destination à son masque",
              "Par le DNS", "Par le pare-feu"],
             1,
             "Si la destination n'est pas dans le réseau local, il envoie à la "
             "passerelle."),
        quiz("Quelle route gagne si deux correspondent ?",
             ["La plus ancienne", "La plus spécifique", "La plus rapide", "La première"],
             1,
             "Le préfixe le plus long l'emporte toujours."),
    ],
}
