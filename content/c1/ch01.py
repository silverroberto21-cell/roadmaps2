from bookkit.dsl import (box, code, defn, ex, fig, h, ol, p, quiz, quote, table, ul)

CH = {
    "title": "Comment fonctionne le Web",
    "subtitle": "Du câble au pixel : ce qui se passe réellement entre la barre d'adresse "
                "et l'affichage d'une page.",
    "duration": "2 h 30",
    "level": "Débutant",
    "prereq": "aucun",
    "objectives": [
        "Distinguer Internet, le Web et les services qui les composent.",
        "Décrire les étapes d'un chargement de page, de la résolution DNS au rendu.",
        "Expliquer le rôle respectif de HTML, CSS et JavaScript.",
        "Préparer un environnement de travail minimal et fonctionnel.",
        "Servir une page locale par HTTP et non par simple ouverture de fichier.",
    ],
    "blocks": [
        h(2, "Le Web n'est pas Internet"),
        p("La confusion est si répandue qu'elle fausse la compréhension de tout le "
          "reste. **Internet** est l'infrastructure : un réseau mondial de réseaux "
          "reliés par des câbles, des routeurs et des protocoles communs, dont le "
          "protocole IP. **Le Web** est un service qui utilise cette infrastructure : "
          "un ensemble de documents reliés par des liens, échangés selon le protocole "
          "HTTP et identifiés par des URL."),
        defn("Le Web", "Service d'information fondé sur trois inventions : l'URL "
                       "(l'adresse d'une ressource), HTTP (le protocole de transport "
                       "des messages) et HTML (le format des documents). Tim Berners-Lee "
                       "en propose le principe au CERN en 1989."),
        p("Sur Internet circulent bien d'autres services : la messagerie électronique "
          "(SMTP, IMAP), le transfert de fichiers (SFTP), la résolution de noms (DNS), "
          "la visioconférence, les jeux en réseau. Le Web est l'un d'entre eux, sans "
          "doute le plus visible, mais il ne se confond pas avec le réseau qui le "
          "porte."),
        fig("timeline", "Six dates qui expliquent le Web d'aujourd'hui",
            [("1969", "ARPANET : premiers paquets"),
             ("1989", "Proposition du World Wide Web"),
             ("1993", "Mosaic, premier navigateur grand public"),
             ("1995", "JavaScript, langage du navigateur"),
             ("2008", "HTML5 et CSS3"),
             ("2020", "Core Web Vitals")],
            note="Les dates retenues marquent des inflexions techniques, non des "
                 "inventions isolées.", height=205),
        p("Cette chronologie explique une caractéristique durable du Web : il a été "
          "conçu pour être **tolérant**. Un navigateur doit afficher une page même si "
          "une image manque, même si une règle CSS est invalide, même si un script "
          "échoue. Cette tolérance est une chance pour qui débute : une page "
          "imparfaite s'affiche quand même."),

        h(2, "Ce qui se passe quand vous ouvrez une page"),
        p("Saisissez une adresse, appuyez sur Entrée. En quelques centaines de "
          "millisecondes, une dizaine d'opérations s'enchaînent. Les comprendre vous "
          "évitera de chercher au mauvais endroit quand quelque chose ne fonctionne "
          "pas."),
        fig("flow", "Le trajet d'une requête HTTP",
            ["URL saisie dans la barre d'adresse",
             "Résolution DNS : nom de domaine → adresse IP",
             "Ouverture d'une connexion TCP, puis TLS si HTTPS",
             "Envoi de la requête HTTP et de ses en-têtes",
             "Réponse du serveur : code de statut, en-têtes, corps",
             "Analyse du HTML, chargement des ressources, rendu"],
            height=300),
        ol("**L'URL est analysée.** Le navigateur identifie le schéma (http ou https), "
           "l'hôte, le port éventuel, le chemin, les paramètres et l'ancre.",
           "**Le nom est résolu.** Le système interroge un résolveur DNS pour traduire "
           "le nom de domaine en adresse IP. Le résultat est mis en cache.",
           "**La connexion est établie.** TCP ouvre une session avec le serveur ; si "
           "l'URL est en HTTPS, une poignée de main TLS négocie le chiffrement.",
           "**La requête part.** Le navigateur envoie une méthode (GET le plus "
           "souvent), un chemin, une version de HTTP et des en-têtes.",
           "**Le serveur répond.** Il renvoie un code de statut, des en-têtes et un "
           "corps : généralement du HTML, parfois du JSON, une image, un fichier.",
           "**Le document est analysé.** Le navigateur construit l'arbre du document, "
           "télécharge les ressources référencées, calcule les styles, positionne les "
           "éléments et peint les pixels."),
        table(["Étape", "Ordre de grandeur", "Ce qui peut échouer"],
              [["Résolution DNS", "0 à 100 ms", "Nom mal orthographié, DNS indisponible"],
               ["Connexion TCP + TLS", "20 à 200 ms", "Port fermé, certificat invalide"],
               ["Requête et réponse", "50 ms à plusieurs secondes", "Erreur serveur, page trop lourde"],
               ["Chargement des ressources", "variable", "Fichier introuvable, blocage réseau"],
               ["Rendu", "16 ms par image idéalement", "CSS ou script bloquant"]],
              widths=[3.0, 2.6, 4.4], first_col_bold=True,
              caption="Les six étapes d'un chargement et leurs défaillances typiques"),
        p("La commande `curl` permet d'observer la réponse brute, sans navigateur. "
          "C'est un outil précieux pour distinguer un problème de serveur d'un "
          "problème d'affichage."),
        code("""$ curl -I https://example.com
HTTP/2 200
content-type: text/html; charset=UTF-8
content-length: 1256
last-modified: Thu, 17 Oct 2024 12:00:00 GMT

$ curl -s https://example.com | head -n 5
<!doctype html>
<html lang="en">
<head>
  <title>Example Domain</title>""", "bash", "Inspecter une réponse HTTP en ligne de commande"),

        h(2, "Les trois langages du front-end"),
        p("Une interface web repose sur trois technologies complémentaires. Les "
          "confondre est la première source d'erreurs de débutant : on demande à "
          "HTML de mettre en page, à CSS de réagir à un clic, à JavaScript de "
          "décrire un contenu."),
        table(["Langage", "Rôle", "Question à laquelle il répond", "Exemple"],
              [["HTML", "Structure et sens", "Qu'est-ce que ce contenu ?", "`<h1>Titre</h1>`"],
               ["CSS", "Présentation", "À quoi cela ressemble-t-il ?", "`h1 { color: navy }`"],
               ["JavaScript", "Comportement", "Que se passe-t-il ensuite ?", "`h1.hidden = true`"]],
              widths=[1.4, 2.2, 3.6, 2.8], first_col_bold=True,
              caption="Répartition des responsabilités entre les trois langages"),
        fig("stack", "Trois couches, un seul document",
            [("JavaScript — comportement", "réagit aux événements, modifie le document, "
                                           "appelle le réseau"),
             ("CSS — présentation", "couleurs, typographie, disposition, animations"),
             ("HTML — structure", "titres, paragraphes, listes, liens, images, formulaires")],
            height=225),
        h(3, "HTML : le sens avant l'apparence"),
        p("HTML décrit la **nature** du contenu. Un titre de niveau 1 n'est pas « du "
          "texte en gros » : c'est le titre principal du document, ce que les moteurs "
          "de recherche, les lecteurs d'écran et les outils d'export utilisent pour "
          "comprendre la page. Un navigateur sans feuille de style doit rester "
          "lisible : c'est le meilleur test de qualité d'un document HTML."),
        h(3, "CSS : une feuille de style, pas un thème"),
        p("CSS associe des règles à des éléments. La même page peut être affichée sur "
          "un téléphone, imprimée, lue par un lecteur d'écran ou rendue en mode "
          "sombre sans que le HTML change. Cette séparation permet de maintenir un "
          "site entier en modifiant quelques fichiers."),
        h(3, "JavaScript : le comportement, avec parcimonie"),
        p("JavaScript s'exécute dans le navigateur, dans un environnement isolé du "
          "système de fichiers. Il peut modifier la page, réagir aux actions de "
          "l'utilisateur et dialoguer avec un serveur. Une page doit néanmoins rester "
          "utile lorsque JavaScript est indisponible ou échoue : c'est le principe "
          "de l'**amélioration progressive**."),
        box("attention", "Ne pas confondre HTML et mise en forme",
            "Écrire `<h2>` pour obtenir du texte plus petit est une erreur de sens. "
            "Utilisez la hiérarchie correcte des titres, puis ajustez la taille avec "
            "CSS. Un document dont la hiérarchie est fausse pénalise l'accessibilité "
            "et le référencement, même s'il « ressemble » à ce que vous vouliez."),

        h(2, "Client et serveur : qui fait quoi"),
        p("Le **client** est le programme qui demande et affiche : ici, le navigateur. "
          "Le **serveur** est le programme qui répond : il lit une requête, exécute "
          "éventuellement du code, puis renvoie une réponse. Cette séparation est "
          "fondamentale : tout ce qui est envoyé au client peut être lu, copié et "
          "modifié par l'utilisateur."),
        fig("compare", "Deux machines, deux responsabilités",
            ("CLIENT (navigateur)", ["Affiche et met en page", "Exécute JavaScript",
                                     "Stocke des données locales", "Ne peut pas garder un secret"],
             "SERVEUR (application)", ["Reçoit les requêtes", "Applique les règles métier",
                                       "Accède aux bases de données", "Contrôle les accès"]),
            height=215),
        p("Conséquence pratique : une validation de formulaire côté client améliore "
          "le confort, mais elle ne remplace jamais une validation côté serveur. Un "
          "utilisateur peut désactiver JavaScript, modifier le HTML ou envoyer une "
          "requête forgée avec `curl`. Cette règle reviendra au chapitre 35."),
        p("On distingue deux grandes familles de sites. Les sites **statiques** "
          "servent des fichiers préparés à l'avance : rapides, simples, faciles à "
          "mettre en cache. Les sites **dynamiques** construisent la réponse à la "
          "demande, souvent à partir d'une base de données : personnalisation et "
          "fraîcheur, au prix d'une complexité supérieure."),

        h(2, "Préparer son environnement de travail"),
        p("Quatre outils suffisent pour commencer : un éditeur de texte, un "
          "navigateur récent, un terminal et un dossier de travail organisé."),
        ul("**Un éditeur de texte** conçu pour le code. Visual Studio Code est le plus "
           "répandu ; Sublime Text, Neovim ou WebStorm conviennent également. "
           "N'utilisez pas un traitement de texte : il insère une mise en forme "
           "invisible qui corrompt le HTML.",
           "**Un navigateur récent** avec ses outils de développement intégrés "
           "(F12). Chrome, Edge et Firefox offrent tous un inspecteur, une console, "
           "un onglet réseau et un onglet performance.",
           "**Un terminal** : Bash sous Linux et macOS, PowerShell ou WSL sous "
           "Windows. Les commandes de ce cours fonctionnent dans Bash.",
           "**Un dossier de projet** unique, sans espaces ni accents dans le nom, "
           "par exemple `mon-site`."),
        code("""mon-site/
├── index.html
├── css/
│   └── style.css
├── js/
│   └── app.js
└── images/
    └── logo.svg""", "text", "Une arborescence simple, lisible et durable"),
        p("Cette organisation n'est pas une convention arbitraire : elle sépare les "
          "responsabilités, facilite les liens relatifs et prépare le travail avec "
          "des outils de construction. Nous la retrouverons à chaque chapitre."),

        h(2, "Servir une page en local"),
        p("Il est tentant de double-cliquer sur un fichier HTML. Le navigateur "
          "l'ouvre alors avec le schéma `file://`. Cela suffit pour une page isolée, "
          "mais plusieurs fonctionnalités échouent : chargement de modules "
          "JavaScript, requêtes vers une API, certains accès au stockage. Il faut "
          "servir le dossier par HTTP."),
        p("Pour la première page de ce cours, créez `index.html` et démarrez un "
          "serveur local. Python fournit un serveur prêt à l'emploi, sans "
          "installation supplémentaire sur la plupart des systèmes."),
        code("""$ cd mon-site
$ python3 -m http.server 8000
Serving HTTP on 0.0.0.0 port 8000 ...
127.0.0.1 - - [19/Oct/2026 10:12:04] "GET / HTTP/1.1" 200 -""",
             "bash", "Démarrer un serveur HTTP local dans le dossier du projet"),
        p("Ouvrez ensuite `http://localhost:8000`. L'adresse `localhost` désigne votre "
          "propre machine ; le port 8000 identifie le programme qui écoute. Sous "
          "Visual Studio Code, l'extension Live Server produit le même effet avec "
          "un rechargement automatique."),
        code("""<!doctype html>
<html lang="fr">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Mon premier site</title>
</head>
<body>
  <h1>Bonjour, Web</h1>
  <p>Cette page est servie par HTTP, dans un navigateur.</p>
</body>
</html>""", "html", "Le squelette minimal d'une page HTML5 valide"),
        box("pratique", "Vérifier que tout fonctionne",
            "Si la page s'affiche mais que l'adresse commence par `file://`, vous "
            "avez ouvert le fichier directement. Si le navigateur affiche un message "
            "d'erreur, vérifiez que le serveur tourne toujours dans le terminal et "
            "que le port n'est pas déjà utilisé par un autre programme."),

        h(2, "Ce que vous allez apprendre, et dans quel ordre"),
        p("La suite du cours suit une progression volontairement linéaire. Les "
          "chapitres 2 à 8 construisent des documents HTML solides : structure, "
          "texte, liens, médias, tableaux, formulaires. Les chapitres 9 à 16 "
          "introduisent CSS et la mise en forme. Les chapitres 17 à 23 traitent la "
          "mise en page contemporaine et l'accessibilité. Les chapitres 24 à 31 "
          "ajoutent JavaScript et l'interactivité. Les chapitres 32 à 36 terminent "
          "par la qualité, la performance, la sécurité et un projet complet."),
        quote("Le Web est plus une invention sociale qu'une invention technique.",
              "Tim Berners-Lee"),
        p("Cette phrase rappelle l'essentiel : un site n'existe que par ses lecteurs. "
          "La technique sert la lecture, la navigation et l'accès, jamais l'inverse. "
          "Gardez ce critère en tête pour arbitrer tous les choix de ce cours."),
    ],
    "keypoints": [
        "Internet est l'infrastructure ; le Web est un service bâti sur HTTP, les URL et HTML.",
        "Un chargement de page enchaîne DNS, connexion, requête, réponse, analyse et rendu.",
        "HTML décrit le sens, CSS la présentation, JavaScript le comportement.",
        "Le client ne peut rien garder de secret : toute validation doit être reprise côté serveur.",
        "Un serveur local évite les limites du schéma file://.",
        "La tolérance du Web rend le début facile, mais la qualité exige de la rigueur.",
    ],
    "bridge": "Vous savez maintenant ce qui se passe entre l'adresse saisie et la page "
              "affichée. Le chapitre suivant installe un poste de travail complet et "
              "durable : éditeur configuré, navigateur maîtrisé, terminal apprivoisé.",
    "exercises": [
        ex("Décomposer une URL",
           "On considère l'adresse suivante : "
           "`https://www.exemple.fr:8443/blog/article-12?page=2&tri=date#commentaires`",
           ["Identifiez le schéma, l'hôte, le port, le chemin, la chaîne de requête et l'ancre.",
            "Indiquez lesquels de ces éléments sont envoyés au serveur dans une requête HTTP.",
            "Proposez une URL équivalente sans port explicite, en expliquant votre choix."],
           ["**Schéma** : `https`. **Hôte** : `www.exemple.fr` (le port par défaut de "
            "HTTPS est 443 ; 8443 est un port alternatif). **Chemin** : `/blog/article-12`. "
            "**Chaîne de requête** : `page=2&tri=date`. **Ancre** : `commentaires`.",
            "Le serveur reçoit le chemin et la chaîne de requête dans la ligne de "
            "requête. L'ancre n'est jamais transmise : elle est traitée localement par "
            "le navigateur pour faire défiler le document.",
            "`https://www.exemple.fr/blog/article-12?page=2&tri=date` suffit si le "
            "service écoute sur le port standard 443. Supprimer un port explicite "
            "n'est possible que si le serveur est configuré sur ce port ; dans le cas "
            "contraire, l'URL ne répond plus."],
           hint="Le port par défaut dépend du schéma : 80 pour HTTP, 443 pour HTTPS."),
        ex("Observer un chargement",
           "Ouvrez les outils de développement de votre navigateur, onglet Réseau, "
           "puis rechargez une page d'un site d'actualités.",
           ["Repérez le document HTML principal et notez son code de statut.",
            "Comptez le nombre de ressources chargées et identifiez les trois plus lourdes.",
            "Notez le temps total de chargement et proposez une cause probable des ralentissements."],
           ["Le document principal apparaît en première ligne, avec un statut 200 s'il "
            "est trouvé, 301 ou 302 s'il y a redirection, 404 s'il manque.",
            "Le nombre de ressources varie fortement d'un site à l'autre (souvent 40 à "
            "150). Les plus lourdes sont généralement des images, des polices ou des "
            "scripts tiers.",
            "Un temps total élevé s'explique le plus souvent par des images non "
            "optimisées, un grand nombre de scripts tiers bloquants, ou une latence "
            "réseau importante. La colonne « En attente » du navigateur aide à "
            "distinguer le temps serveur du temps de téléchargement."],
           hint="Triez la liste par taille décroissante : le diagnostic devient immédiat."),
        ex("Écrire et servir sa première page",
           "Créez un dossier `mon-site` contenant un fichier `index.html` valide, "
           "avec un titre d'onglet, un titre principal et un paragraphe.",
           ["Écrivez le document avec l'encodage UTF-8 et la langue française.",
            "Démarrez un serveur local sur le port 8000.",
            "Vérifiez dans l'onglet Réseau que la page est bien servie en HTTP 200.",
            "Modifiez le paragraphe puis rechargez : le changement doit apparaître."],
           [("code", """<!doctype html>
<html lang="fr">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Mon premier site</title>
</head>
<body>
  <h1>Bonjour, Web</h1>
  <p>Cette page est servie par HTTP, dans un navigateur.</p>
</body>
</html>"""),
            "Le serveur se lance avec `python3 -m http.server 8000` depuis le dossier "
            "du projet. L'onglet Réseau doit montrer une requête `GET /` avec le "
            "statut 200 et le type `text/html`.",
            "Si le navigateur affiche l'ancienne version, forcez un rechargement "
            "(Ctrl+Maj+R) : il conserve parfois une copie en cache. Vérifiez aussi que "
            "vous modifiez bien le fichier servi par le serveur, et non une copie "
            "située dans un autre dossier."],
           hint="Le serveur doit être lancé depuis le dossier qui contient index.html."),
        ex("Comparer deux sites",
           "Choisissez un site institutionnel et un site d'information. Analysez-les "
           "avec les outils de développement.",
           ["Comparez le nombre de requêtes et le poids total.",
            "Identifiez trois différences de structure HTML (hiérarchie des titres, "
            "navigation, formulaires).",
            "Rédigez une conclusion de dix lignes sur les compromis observés."],
           ["Les chiffres dépendent du moment de l'observation ; l'important est la "
            "méthode : même navigateur, même connexion, cache vidé.",
            "Un site institutionnel présente souvent une hiérarchie de titres plus "
            "régulière, une navigation stable et peu de scripts tiers. Un site "
            "d'information multiplie les modules, les publicités et les appels "
            "réseau, au détriment du poids et de la stabilité visuelle.",
            "La conclusion attendue distingue les contraintes : un site "
            "d'information privilégie la fraîcheur et le rendement publicitaire ; un "
            "site institutionnel privilégie l'accessibilité, la cohérence et la "
            "durabilité. Aucun des deux n'est « meilleur » : les choix techniques "
            "découlent du modèle d'affaires et du public."],
           level="Analyse"),
    ],
    "quiz": [
        quiz("Quelle affirmation décrit correctement la relation entre Internet et le Web ?",
             ["Le Web est le réseau physique ; Internet est l'ensemble des sites.",
              "Internet est l'infrastructure réseau ; le Web est un service qui l'utilise.",
              "Les deux termes sont synonymes depuis HTML5.",
              "Internet fonctionne sans protocole IP, contrairement au Web."],
             1,
             "Internet est le réseau mondial fondé sur IP ; le Web est un service "
             "applicatif (URL, HTTP, HTML) qui circule sur ce réseau."),
        quiz("Dans quel ordre se déroulent les étapes d'un chargement de page ?",
             ["Requête HTTP, DNS, connexion TCP, rendu",
              "DNS, connexion TCP, requête HTTP, rendu",
              "Connexion TCP, rendu, DNS, requête HTTP",
              "DNS, rendu, requête HTTP, connexion TCP"],
             1,
             "Le navigateur doit d'abord connaître l'adresse IP (DNS), puis établir la "
             "connexion, envoyer la requête et enfin analyser la réponse pour rendre."),
        quiz("Quel est le rôle du HTML ?",
             ["Décrire la présentation visuelle du document",
              "Décrire la structure et le sens du contenu",
              "Gérer les interactions et les animations",
              "Chiffrer les échanges avec le serveur"],
             1,
             "HTML décrit la nature du contenu (titres, paragraphes, listes, liens). "
             "La présentation relève de CSS, le comportement de JavaScript, le "
             "chiffrement de TLS."),
        quiz("Pourquoi ouvrir un fichier en file:// pose-t-il problème ?",
             ["Le navigateur refuse d'afficher le HTML.",
              "Les modules JavaScript et les requêtes réseau sont limités ou bloqués.",
              "Les images ne peuvent pas être affichées.",
              "Le fichier est automatiquement modifié."],
             1,
             "Le schéma file:// ne fournit pas d'origine HTTP : les modules, fetch et "
             "certaines API de stockage sont restreints pour des raisons de sécurité."),
        quiz("Où doit être effectuée une validation de formulaire réellement fiable ?",
             ["Uniquement dans le navigateur, avec JavaScript",
              "Uniquement dans le HTML, avec l'attribut required",
              "Côté serveur, complétée par une validation côté client pour le confort",
              "Dans la feuille de style CSS"],
             2,
             "Tout ce qui vient du client peut être modifié. La validation serveur est "
             "la seule barrière fiable ; celle du navigateur améliore l'expérience."),
    ],
}
