from bookkit.dsl import (box, code, defn, ex, fig, h, ol, p, quiz, table, ul)

CH = {
    "title": "Réseaux : modèles et couches",
    "subtitle": "Comprendre ce qui se passe entre deux machines, du câble à "
                "l'application.",
    "duration": "3 h 00",
    "level": "Intermédiaire",
    "prereq": "chapitre 48",
    "objectives": [
        "Situer les protocoles dans les modèles en couches.",
        "Décrire le trajet d'un paquet entre deux machines.",
        "Diagnostiquer une panne couche par couche.",
        "Comprendre encapsulation et MTU.",
        "Utiliser les outils d'observation réseau.",
    ],
    "blocks": [
        h(2, "Deux modèles, une même réalité"),
        p("Le modèle OSI en sept couches est un outil pédagogique ; le modèle TCP/IP en "
          "quatre couches décrit ce qui est réellement implémenté. Les deux se "
          "correspondent."),
        table(["OSI", "TCP/IP", "Exemples", "Unité"],
              [["7 Application", "Application", "HTTP, DNS, SSH", "Données"],
               ["6 Présentation", "Application", "TLS, encodage", "Données"],
               ["5 Session", "Application", "Sessions, cookies", "Données"],
               ["4 Transport", "Transport", "TCP, UDP, QUIC", "Segment"],
               ["3 Réseau", "Internet", "IP, ICMP, routage", "Paquet"],
               ["2 Liaison", "Accès réseau", "Ethernet, Wi-Fi, ARP", "Trame"],
               ["1 Physique", "Accès réseau", "Câble, fibre, ondes", "Bit"]],
              widths=[3.0, 3.0, 4.4, 2.6], first_col_bold=True,
              caption="Sept couches et leur équivalent"),
        fig("flow", "Le trajet d'une requête HTTPS",
            ["Application : le navigateur construit la requête",
             "TLS : chiffrement de la session",
             "TCP : découpage en segments, numérotation",
             "IP : adressage et routage vers la destination",
             "Ethernet : trame vers la passerelle",
             "Câble ou ondes : transmission physique"],
            height=270),
        defn("Encapsulation", "Chaque couche ajoute son en-tête aux données de la couche "
                              "supérieure. À la réception, les en-têtes sont retirés "
                              "dans l'ordre inverse."),

        h(2, "Ce que chaque couche garantit"),
        p("Une panne réseau se diagnostique en partant du bas : si la couche 3 échoue, "
          "inutile de vérifier la couche 7. Cette progression évite les fausses pistes."),
        table(["Couche", "Question", "Outil"],
              [["1–2", "Le lien est-il actif ?", "`ip link`, `ethtool`"],
               ["3", "La destination est-elle joignable ?", "`ping`, `traceroute`"],
               ["3", "Le routage est-il correct ?", "`ip route`"],
               ["4", "Le port est-il ouvert ?", "`nc`, `ss`, `telnet`"],
               ["7", "Le service répond-il ?", "`curl`, `dig`"]],
              widths=[2.6, 5.6, 4.0], first_col_bold=True,
              caption="Cinq couches et leurs outils"),
        code("""# Descendre la pile, dans l'ordre
ip link show                    # la carte est-elle UP ?
ip addr show                    # une adresse est-elle configurée ?
ip route                        # existe-t-il une route par défaut ?
ping -c 3 1.1.1.1               # la couche 3 répond-elle ?
ping -c 3 exemple.fr            # la résolution DNS fonctionne-t-elle ?
nc -zv exemple.fr 443           # le port est-il ouvert ?
curl -I https://exemple.fr      # l'application répond-elle ?""", "bash",
             "Sept vérifications ordonnées"),
        box("pratique", "Le diagnostic en trois questions",
            "« Est-ce que ça marche ailleurs ? » sépare un problème local d'un problème "
            "global. « Depuis quand ? » oriente vers un changement. « Qu'est-ce qui a "
            "changé ? » trouve la cause dans la majorité des cas."),

        h(2, "Commutateurs, routeurs, passerelles"),
        p("Un commutateur relie des machines d'un même réseau local ; un routeur relie "
          "des réseaux différents. Une passerelle est le routeur par lequel sortent les "
          "paquets destinés à l'extérieur."),
        fig("compare", "Deux équipements, deux rôles",
            ("COMMUTATEUR (COUCHE 2)", ["Relie des machines proches",
                                        "Utilise les adresses MAC",
                                        "Ne modifie pas les paquets IP"],
             "ROUTEUR (COUCHE 3)", ["Relie des réseaux",
                                    "Utilise les adresses IP",
                                    "Décrémente le TTL"]),
            height=215),
        code("""# Table de routage
ip route
# default via 192.168.1.1 dev eth0 proto dhcp metric 100
# 192.168.1.0/24 dev eth0 proto kernel scope link src 192.168.1.20

# Table ARP : correspondance IP ↔ MAC
ip neigh

# Suivre le chemin
traceroute -n exemple.fr
mtr --report exemple.fr""", "bash", "Trois tables et deux outils"),
        defn("MTU", "Taille maximale d'une unité de transmission. Sur Ethernet, 1500 "
                    "octets en général. Un paquet plus gros est fragmenté ou rejeté, "
                    "ce qui provoque des symptômes déroutants : petites requêtes "
                    "réussies, grosses requêtes bloquées."),

        h(2, "TCP, UDP et QUIC"),
        p("Le transport décide de la fiabilité et de l'ordre. TCP garantit la livraison "
          "et la séquence ; UDP non ; QUIC ajoute la fiabilité au-dessus d'UDP avec "
          "moins de latence d'établissement."),
        table(["Protocole", "Fiabilité", "Ordre", "Usage"],
              [["TCP", "Oui", "Oui", "HTTP/1.1, SSH, bases"],
               ["UDP", "Non", "Non", "DNS, VoIP, jeux, QUIC"],
               ["QUIC", "Oui", "Oui", "HTTP/3, multiplexage sans blocage"]],
              widths=[3.0, 3.2, 2.6, 5.2], first_col_bold=True,
              caption="Trois protocoles de transport"),
        code("""# Établissement TCP : trois messages
# 1. SYN         client → serveur
# 2. SYN-ACK     serveur → client
# 3. ACK         client → serveur
# Puis les données circulent.

# Fermeture : quatre messages (FIN, ACK, FIN, ACK)

# Observer les états des connexions
ss -tan state established
ss -s""", "bash", "Trois étapes, quatre fermetures"),
        defn("Handshake", "Négociation initiale entre deux pairs. Pour TLS au-dessus de "
                          "TCP, elle ajoute deux allers-retours, ce qui motive la "
                          "reprise de session et QUIC."),
        code("""# Capture de trafic (à utiliser avec discernement)
tcpdump -i eth0 -n port 443 -c 20
tcpdump -i any -nn -A port 53

# Analyse détaillée
tshark -i eth0 -f "tcp port 443"
# Wireshark offre la même analyse en interface graphique""", "bash",
             "Deux captures, une analyse"),

        h(2, "Latence, débit et perte"),
        p("Trois grandeurs décrivent une liaison. Le débit n'est pas la latence : une "
          "liaison très rapide peut être inutilisable pour une application interactive "
          "si l'aller-retour est long."),
        table(["Grandeur", "Mesure", "Outil"],
              [["Latence", "Aller-retour en ms", "`ping`, `mtr`"],
               ["Débit", "Octets par seconde", "`iperf3`, `curl -w`"],
               ["Perte", "Pourcentage de paquets perdus", "`mtr`, `ping`"],
               ["Gigue", "Variation de la latence", "`mtr`, mesures répétées"]],
              widths=[3.0, 5.0, 4.0], first_col_bold=True,
              caption="Quatre grandeurs réseau"),
        code("""# Mesure de débit entre deux machines
# Sur le serveur
iperf3 -s
# Sur le client
iperf3 -c serveur.exemple.fr -t 10 -P 4

# Temps détaillé d'une requête HTTP
curl -o /dev/null -s -w \\
  "dns %{time_namelookup} | connexion %{time_connect} | tls %{time_appconnect} | total %{time_total}\\n" \\
  https://exemple.fr""", "bash", "Deux mesures reproductibles"),
        box("methode", "Diagnostic réseau en cinq commandes",
            items=["`ip addr` et `ip route` : la configuration locale.",
                   "`ping` la passerelle, puis une adresse publique.",
                   "`dig` : la résolution de noms.",
                   "`nc -zv hote port` : l'accessibilité du port.",
                   "`curl -v` : le comportement applicatif."]),
    ],
    "keypoints": [
        "OSI est un modèle pédagogique ; TCP/IP décrit l'implémentation.",
        "L'encapsulation ajoute un en-tête par couche.",
        "Un diagnostic progresse du bas vers le haut de la pile.",
        "Le commutateur relie un réseau local, le routeur relie des réseaux.",
        "La MTU explique les échecs sur gros paquets uniquement.",
        "TCP garantit la livraison, UDP non, QUIC ajoute la fiabilité.",
        "Latence et débit sont deux mesures distinctes.",
    ],
    "bridge": "Les couches sont posées. Le chapitre suivant entre dans l'adressage : "
              "IP, masques et routage.",
    "exercises": [
        ex("Diagnostiquer une panne",
           "Un serveur ne répond plus en HTTPS, mais `ping` fonctionne.",
           ["Vérifiez la configuration locale.",
            "Testez le port.",
            "Observez le service."],
           [("code", """ip addr show
ip route
ping -c 2 192.168.1.1
nc -zv exemple.fr 443
ss -ltnp | grep :443
curl -vk https://exemple.fr 2>&1 | head -20"""),
            "`ping` qui fonctionne et HTTPS qui échoue oriente vers le port, le service "
            "ou TLS — pas vers le réseau.",
            "`curl -v` affiche chaque étape : résolution, connexion, négociation TLS, "
            "réponse HTTP."],
           level="Diagnostic"),
        ex("Suivre un paquet",
           "Une requête traverse trois routeurs avant d'atteindre sa destination.",
           ["Observez les sauts.",
            "Identifiez les latences anormales.",
            "Distinguez perte locale et perte distante."],
           [("code", """mtr --report --report-cycles 10 exemple.fr
# Loss%  Snt  Last  Avg  Best  Wrst  StDev  Host
#  0.0%   10   1.1  1.2   1.0   1.6   0.2   192.168.1.1
#  0.0%   10   8.4  9.1   8.0  11.2   0.9   10.0.0.1
# 33.0%   10  42.0 43.7  41.2  48.9   2.1   transit.exemple
#  0.0%   10  41.8 42.9  41.5  47.0   1.8   cible.exemple"""),
            "Une perte qui apparaît à un saut puis disparaît au suivant correspond "
            "souvent à une limitation de débit des réponses ICMP, pas à une vraie perte.",
            "Une perte qui persiste jusqu'à la destination est réelle et affecte les "
            "applications sensibles."],
           level="Diagnostic"),
        ex("Tester une MTU",
           "Les petites requêtes passent, les gros transferts bloquent.",
           ["Testez avec DF (don't fragment).",
            "Diminuez la taille jusqu'au succès.",
            "Corrigez la MTU."],
           [("code", """# Tester sans fragmentation
ping -M do -s 1472 -c 2 exemple.fr   # 1472 + 28 = 1500
ping -M do -s 1400 -c 2 exemple.fr

# Ajuster la MTU de l'interface (persistant via NetworkManager)
ip link set dev eth0 mtu 1400
nmcli connection modify eth0 802-3-ethernet.mtu 1400
nmcli connection up eth0"""),
            "La valeur testée exclut les en-têtes IP et ICMP : 1472 + 28 = 1500.",
            "Un tunnel VPN réduit souvent la MTU utile : c'est une cause fréquente de "
            "blocage sur gros paquets."],
           level="Diagnostic"),
    ],
    "quiz": [
        quiz("À quelle couche se situe IP ?",
             ["Liaison", "Réseau", "Transport", "Application"],
             1,
             "IP est le protocole de la couche réseau (couche 3)."),
        quiz("Quel protocole garantit la livraison et l'ordre ?",
             ["UDP", "TCP", "ICMP", "ARP"],
             1,
             "TCP gère acquittements, retransmissions et séquencement."),
        quiz("Que fait l'encapsulation ?",
             ["Compresse les données", "Ajoute un en-tête à chaque couche",
              "Chiffre le trafic", "Réduit la latence"],
             1,
             "Chaque couche ajoute ses métadonnées puis les retire à la réception."),
        quiz("Quel outil teste l'ouverture d'un port ?",
             ["`ping`", "`nc -zv`", "`dig`", "`ip route`"],
             1,
             "`nc -zv` tente une connexion TCP sur le port indiqué."),
        quiz("Que mesure la latence ?",
             ["Le débit maximal", "Le temps d'aller-retour",
              "La perte de paquets", "La taille des paquets"],
             1,
             "Elle s'exprime en millisecondes d'aller-retour."),
    ],
}
