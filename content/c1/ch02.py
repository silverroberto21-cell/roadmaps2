from bookkit.dsl import (box, code, defn, ex, fig, h, ol, p, quiz, table, ul)

CH = {
    "title": "Installer et maîtriser son environnement",
    "subtitle": "Un poste de travail bien réglé fait gagner des semaines. Voici celui "
                "que vous garderez pendant tout le cours.",
    "duration": "2 h 00",
    "level": "Débutant",
    "prereq": "chapitre 1",
    "objectives": [
        "Installer et configurer un éditeur de code adapté au développement web.",
        "Utiliser les outils de développement du navigateur pour inspecter et modifier une page.",
        "Créer une arborescence de projet propre et la versionner dès le départ.",
        "Valider un document HTML et détecter les erreurs de structure.",
        "Adopter des raccourcis et des conventions qui accélèrent le travail quotidien.",
    ],
    "blocks": [
        h(2, "L'éditeur de code : un instrument, pas un accessoire"),
        p("Un éditeur de code n'est pas un traitement de texte. Il comprend la "
          "syntaxe, plie les blocs, signale les parenthèses non fermées, propose des "
          "chemins de fichiers et exécute des outils externes. Le choix exact importe "
          "moins que la régularité de son usage : un éditeur médiocre bien configuré "
          "vaut mieux qu'un outil prestigieux mal maîtrisé."),
        p("Trois familles coexistent. Les éditeurs **graphiques** (Visual Studio Code, "
          "Sublime Text, WebStorm) offrent une prise en main immédiate et un vaste "
          "écosystème d'extensions. Les éditeurs **modaux** (Neovim, Emacs) exigent un "
          "apprentissage plus long mais restent dans le terminal et se pilotent au "
          "clavier. Les **IDE complets** intègrent débogueur, tests et gestion de "
          "projet dans une seule application."),
        table(["Outil", "Points forts", "Limites", "Public"],
              [["Visual Studio Code", "Extensions, terminal intégré, débogage, gratuit",
                "Consommation mémoire, dépendance à Electron", "Très large"],
               ["Sublime Text", "Rapidité, légèreté, multi-curseurs", "Payant, écosystème plus restreint", "Confirmé"],
               ["WebStorm", "Réfactorisation, analyse de code avancée", "Licence payante, lourd", "Professionnel"],
               ["Neovim / Emacs", "Contrôle total, travail à distance", "Courbe d'apprentissage abrupte", "Expert"]],
              widths=[2.4, 3.9, 3.4, 2.3], first_col_bold=True,
              caption="Quatre éditeurs, quatre philosophies"),
        p("Ce cours utilise Visual Studio Code dans ses captures et ses raccourcis, "
          "mais les principes restent valables ailleurs. L'important est de connaître "
          "au moins dix raccourcis par cœur, de comprendre la recherche globale et "
          "d'utiliser le formatage automatique."),
        h(3, "Les réglages indispensables"),
        p("Après l'installation, réglez au minimum les éléments suivants. Ils évitent "
          "les erreurs invisibles : espaces et tabulations mélangés, encodage "
          "incorrect, fin de ligne différente selon le système."),
        code("""{
  "editor.formatOnSave": true,
  "editor.tabSize": 2,
  "editor.insertSpaces": true,
  "editor.detectIndentation": false,
  "editor.rulers": [100],
  "files.encoding": "utf8",
  "files.eol": "\\n",
  "files.trimTrailingWhitespace": true,
  "files.insertFinalNewline": true,
  "html.format.wrapLineLength": 100
}""", "json", "Réglages minimaux d'un poste de développement web"),
        p("L'indentation à deux espaces est la convention dominante en HTML, CSS et "
          "JavaScript. Peu importe le nombre, tant qu'il est **constant** dans un "
          "projet : un fichier qui mélange espaces et tabulations produit des "
          "différences illisibles dans Git."),
        box("pratique", "Les dix raccourcis à connaître",
            items=["Ctrl+P (Cmd+P) : ouvrir un fichier par son nom",
                   "Ctrl+Maj+F : rechercher dans tout le projet",
                   "Ctrl+D : sélectionner l'occurrence suivante du mot",
                   "Alt+clic : ajouter un curseur multiple",
                   "Ctrl+/ : commenter la sélection",
                   "Ctrl+Maj+P : palette de commandes",
                   "Ctrl+` : ouvrir le terminal intégré",
                   "Alt+Maj+F : formater le document",
                   "Ctrl+G : aller à la ligne",
                   "F12 : aller à la définition"]),

        h(2, "Les outils du navigateur"),
        p("Le navigateur contient un atelier complet, souvent sous-estimé. Ouvrez-le "
          "avec F12, Ctrl+Maj+I ou par le menu. Cinq panneaux suffisent au quotidien."),
        table(["Panneau", "Usage principal", "Ce qu'on y cherche"],
              [["Éléments", "Inspecter et modifier le DOM et les styles", "Boîte d'un élément, règle CSS appliquée"],
               ["Console", "Exécuter du JavaScript, lire les erreurs", "Message d'erreur, valeur d'une variable"],
               ["Réseau", "Observer les requêtes HTTP", "Statut, taille, temps, en-têtes"],
               ["Sources", "Déboguer les scripts, poser des points d'arrêt", "Ordre d'exécution, portée"],
               ["Application", "Inspecter le stockage et les cookies", "localStorage, cookies, cache"]],
              widths=[2.2, 4.4, 4.4], first_col_bold=True,
              caption="Les cinq panneaux des outils de développement"),
        p("Le panneau **Éléments** est le plus utilisé. Un clic droit sur une zone de "
          "la page, puis « Inspecter », ouvre l'arbre du document à l'endroit exact. "
          "Le volet des styles montre toutes les règles qui s'appliquent, y compris "
          "celles héritées et celles écrasées. C'est là que se résolvent 80 % des "
          "questions de mise en forme."),
        fig("hub", "Ce que révèlent les outils de développement",
            ("F12", ["Structure réelle du DOM", "Styles calculés et cascade",
                     "Requêtes et temps réseau", "Erreurs JavaScript", "Stockage local"]),
            height=235),
        box("attention", "Les modifications ne sont pas enregistrées",
            "Tout ce que vous modifiez dans les outils de développement disparaît au "
            "rechargement. Cet espace sert à **expérimenter**, pas à corriger. Une "
            "fois la bonne valeur trouvée, reportez-la dans votre fichier CSS."),
        h(3, "Simuler un appareil"),
        p("Le bouton d'appareil (Ctrl+Maj+M) active le mode responsive : largeur "
          "libre, appareils prédéfinis, émulation du tactile et du réseau lent. "
          "Attention : l'émulation ne remplace pas un téléphone réel. Les différences "
          "de police, de densité d'écran et de performance y sont sensibles."),

        h(2, "Le terminal, allié du développeur web"),
        p("Le terminal n'est pas réservé aux administrateurs système. Il sert à "
          "lancer un serveur local, installer des dépendances, initialiser Git, "
          "minifier des fichiers ou exécuter des tests. Six commandes couvrent "
          "l'essentiel des besoins de ce cours."),
        table(["Commande", "Effet", "Exemple"],
              [["`cd dossier`", "Changer de dossier", "`cd mon-site`"],
               ["`ls -la`", "Lister le contenu, fichiers cachés inclus", "`ls -la css`"],
               ["`mkdir nom`", "Créer un dossier", "`mkdir images`"],
               ["`cp source cible`", "Copier", "`cp index.html sauvegarde.html`"],
               ["`mv source cible`", "Déplacer ou renommer", "`mv style.css css/`"],
               ["`rm fichier`", "Supprimer (définitif)", "`rm brouillon.html`"]],
              widths=[3.0, 4.6, 3.4], caption="Six commandes pour survivre dans un terminal"),
        p("Sous Windows, PowerShell accepte la plupart de ces commandes avec des "
          "variantes (`dir`, `copy`, `move`, `del`). Windows Subsystem for Linux "
          "(WSL) offre un terminal Bash complet et évite les allers-retours "
          "d'apprentissage ; nous le recommandons pour la suite du cours."),
        code("""$ pwd
/home/you/mon-site
$ mkdir -p css js images
$ touch index.html css/style.css js/app.js
$ ls -R
.:
css  images  index.html  js

./css:
style.css

./js:
app.js

./images:""", "bash", "Créer une arborescence de projet complète en quatre commandes"),

        h(2, "Organiser le dossier de travail"),
        p("Un projet web se reconnaît à son arborescence. La structure proposée au "
          "chapitre 1 se précise : les fichiers sources restent à la racine, les "
          "ressources sont rangées par nature, et les éléments générés sont isolés."),
        code("""mon-site/
├── index.html
├── a-propos.html
├── contact.html
├── css/
│   ├── reset.css
│   └── style.css
├── js/
│   └── app.js
├── images/
│   ├── logo.svg
│   └── illustration.webp
├── fonts/
│   └── inter-var.woff2
├── favicon.ico
└── README.md""", "text", "Arborescence d'un site statique de taille moyenne"),
        p("Trois règles rendent cette organisation durable. **Un nom, un rôle** : "
          "`style.css` contient la présentation, jamais le comportement. **Pas "
          "d'espaces ni d'accents** dans les chemins : les URL doivent rester "
          "lisibles et stables. **Tout en minuscules** : sur un serveur Linux, "
          "`Logo.PNG` et `logo.png` désignent deux fichiers différents, ce qui "
          "provoque des erreurs invisibles sur votre machine Windows ou macOS."),
        box("attention", "Le piège des majuscules",
            "Un fichier nommé `Image.PNG` référencé en `image.png` s'affiche sur "
            "macOS (système insensible à la casse par défaut) et renvoie une erreur "
            "404 sur un serveur Linux. C'est l'une des causes les plus fréquentes de "
            "« ça marchait chez moi »."),

        h(2, "Versionner dès le premier fichier"),
        p("Git enregistre l'historique du projet et permet de revenir en arrière. "
          "L'installer dès le premier jour évite la tentation des sauvegardes "
          "manuelles (`site-final-v2-vraiment-final.html`)."),
        code("""$ git init
$ git config user.name "Votre Nom"
$ git config user.email "vous@exemple.fr"
$ printf "node_modules/\\n.DS_Store\\n*.log\\n" > .gitignore
$ git add .
$ git commit -m "Structure initiale du projet"
[main (root-commit) 8f3c2a1] Structure initiale du projet
 5 files changed, 84 insertions(+)""", "bash", "Initialiser un dépôt Git dans un projet web"),
        p("Le fichier `.gitignore` liste ce qui ne doit jamais être versionné : "
          "dépendances installées, fichiers système, journaux, variables "
          "d'environnement. Nous reviendrons en détail sur Git au chapitre 35 ; il "
          "suffit ici de prendre l'habitude de commiter à chaque étape terminée."),

        h(2, "Valider son HTML"),
        p("Un document valide respecte la grammaire du langage. La validation détecte "
          "les balises non fermées, les attributs inconnus, les imbrications "
          "interdites et les erreurs d'encodage. Elle ne garantit pas la qualité "
          "d'un contenu, mais elle élimine une catégorie entière de bogues."),
        p("Le service du W3C (`validator.w3.org`) accepte une URL, un fichier ou un "
          "texte collé. En local, l'extension « W3C Web Validator » ou l'outil en "
          "ligne de commande `vnu` produisent le même diagnostic sans quitter "
          "l'éditeur."),
        code("""$ npm install --global vnu-jar
$ vnu --errors-only index.html
"file:index.html":12.5-12.9: error: Element "h1" not allowed as child of element
"span" in this context.""", "bash", "Valider un fichier HTML en ligne de commande"),
        p("Le message indique le fichier, la ligne, la colonne et la règle violée. "
          "Lisez-le littéralement : la cause est presque toujours là où le "
          "validateur la situe, et non dans le fichier « coupable » supposé."),
        box("methode", "Trois vérifications après chaque page",
            items=["Valider le document ; corriger toutes les erreurs, examiner les avertissements.",
                   "Afficher la page sans CSS : la structure doit rester compréhensible.",
                   "Naviguer uniquement au clavier : chaque lien et chaque bouton doit être atteignable."]),

        h(2, "Un environnement reproductible"),
        p("Votre poste finira par changer, ou vous travaillerez à deux. Notez la "
          "configuration dans un fichier `README.md` : version de l'éditeur, "
          "extensions utilisées, commandes de lancement, conventions de nommage. "
          "Ce réflexe, emprunté au monde DevOps, s'appelle la **documentation "
          "exécutable** : ce qui n'est pas écrit n'existe pas."),
        code("""# Mon site — notes de développement

## Lancer le projet
    python3 -m http.server 8000
    # puis http://localhost:8000

## Conventions
- HTML : 2 espaces, attributs sur une ligne si < 100 caractères
- CSS : classes en kebab-case, pas d'ID pour le style
- Images : WebP, largeur maximale 1600 px

## Extensions VS Code
- Live Server, Prettier, W3C Web Validator, axe DevTools""", "markdown",
             "Un README minimal mais suffisant pour reprendre le projet"),
        p("Ce fichier sera lu par vous-même dans six mois. C'est le meilleur "
          "investissement de la première semaine."),
    ],
    "keypoints": [
        "L'éditeur se règle : indentation constante, UTF-8, formatage à l'enregistrement.",
        "Les outils du navigateur servent à comprendre et expérimenter, pas à corriger.",
        "Six commandes de terminal suffisent pour organiser un projet web.",
        "Les chemins s'écrivent en minuscules, sans espaces ni accents.",
        "Git s'installe dès le premier fichier, pas à la fin du projet.",
        "Valider le HTML supprime une catégorie entière d'erreurs silencieuses.",
    ],
    "bridge": "Le poste est prêt et le projet versionné. Le chapitre suivant entre "
              "dans le vif du sujet : la structure d'un document HTML, du doctype "
              "aux métadonnées.",
    "exercises": [
        ex("Configurer son poste",
           "Installez un éditeur, réglez l'indentation à deux espaces, activez le "
           "formatage à l'enregistrement et l'encodage UTF-8.",
           ["Créez un dossier `atelier` contenant `index.html` et `css/style.css`.",
            "Vérifiez que l'enregistrement formate automatiquement le fichier.",
            "Provoquez volontairement une erreur de validation et corrigez-la."],
           ["Le fichier de réglages se trouve dans les préférences de l'éditeur "
            "(format JSON). Les options `editor.tabSize`, `editor.insertSpaces`, "
            "`files.encoding` et `editor.formatOnSave` suffisent.",
            "Pour tester le formatage, écrivez une ligne très longue et mal indentée, "
            "enregistrez : le formateur la réorganise selon la règle configurée.",
            "Une erreur typique consiste à fermer une balise dans le mauvais ordre : "
            "`<p><strong>texte</p></strong>`. Le validateur signale l'imbrication "
            "incorrecte ; la correction consiste à fermer d'abord `strong`, puis `p`."]),
        ex("Enquête dans les outils de développement",
           "Ouvrez un site de presse, puis inspectez un titre et une image.",
           ["Relevez la taille de la police réellement appliquée au titre.",
            "Identifiez la règle CSS responsable et son fichier d'origine.",
            "Modifiez la couleur du titre depuis l'inspecteur, puis rechargez."],
           ["Le volet « Styles » affiche la police calculée (par exemple 32 px) et "
            "la règle correspondante avec son sélecteur et son fichier source.",
            "La règle gagnante est celle qui apparaît en premier et n'est pas barrée. "
            "Les règles barrées sont écrasées par plus spécifiques ou plus tardives.",
            "Après rechargement, la couleur d'origine revient : la modification n'a "
            "pas été enregistrée. C'est la démonstration du caractère temporaire de "
            "l'inspecteur."]),
        ex("Créer une arborescence et la versionner",
           "Créez un projet `portfolio` avec les dossiers `css`, `js`, `images`, un "
           "fichier `index.html`, un `.gitignore` et un dépôt Git.",
           ["Respectez la convention de nommage en minuscules.",
            "Ajoutez un premier commit explicite.",
            "Modifiez un fichier, puis vérifiez l'état du dépôt avant de commiter."],
           [("code", """$ mkdir -p portfolio/{css,js,images} && cd portfolio
$ touch index.html css/style.css js/app.js
$ printf "node_modules/\\n.DS_Store\\n*.log\\n" > .gitignore
$ git init && git add . && git commit -m "Structure initiale du portfolio\""""),
            "`git status` montre ensuite les fichiers modifiés en rouge et ceux "
            "indexés en vert. `git diff` affiche le détail des changements non "
            "indexés ; `git add` les prépare ; `git commit` les enregistre.",
            "Un commit doit décrire une intention : « Ajoute la page d'accueil », "
            "non « maj ». Cette discipline rend l'historique lisible et les retours "
            "arrière sûrs."]),
        ex("Diagnostiquer une page cassée",
           "On vous transmet ce document. Il s'affiche mal et la validation échoue. "
           "Trouvez les trois erreurs, expliquez-les et corrigez-les.",
           ["`<html><head><title>Test</title></head><body><h1>Bienvenue<h1>"
            "<p>Texte <b>important</p></b></body>`",
            "Indiquez pour chaque erreur la conséquence à l'écran.",
            "Proposez une version valide et sémantiquement correcte."],
           ["Trois erreurs : la balise `h1` est fermée par une autre ouverture de "
            "`h1` (le navigateur referme automatiquement, mais la structure devient "
            "ambiguë) ; les balises `b` et `p` s'entrecroisent ; le document n'a pas "
            "de `<!doctype html>`, ce qui déclenche le mode « quirks ».",
            "Conséquences : la hiérarchie des titres est fausse, le style peut se "
            "propager de travers, et le mode quirks modifie le calcul des tailles "
            "et des marges, rendant la mise en page imprévisible.",
            ("code", """<!doctype html>
<html lang="fr">
<head>
  <meta charset="utf-8">
  <title>Test</title>
</head>
<body>
  <h1>Bienvenue</h1>
  <p>Texte <strong>important</strong></p>
</body>
</html>""")],
           level="Diagnostic"),
    ],
    "quiz": [
        quiz("Pourquoi faut-il éviter les espaces et les accents dans les noms de fichiers ?",
             ["Ils empêchent le navigateur d'ouvrir le fichier",
              "Ils doivent être encodés dans les URL et peuvent différer selon les systèmes",
              "Ils rendent le HTML invalide",
              "Ils empêchent Git de fonctionner"],
             1,
             "Les caractères non ASCII sont encodés dans les URL ; selon le système "
             "de fichiers, le cas et la normalisation Unicode varient, ce qui produit "
             "des erreurs 404 difficiles à diagnostiquer."),
        quiz("Que se passe-t-il lorsqu'on modifie une règle CSS dans l'inspecteur ?",
             ["La modification est enregistrée dans le fichier CSS",
              "La modification est appliquée jusqu'au rechargement, puis perdue",
              "La modification est enregistrée dans le cache du navigateur",
              "La modification est envoyée au serveur"],
             1,
             "L'inspecteur agit sur une copie en mémoire de la feuille de style. Le "
             "rechargement réinitialise tout ; il faut reporter la valeur dans le "
             "fichier source."),
        quiz("Quel réglage évite les différences d'indentation dans un projet ?",
             ["Activer la détection automatique de l'indentation",
              "Fixer une taille et un type d'indentation, et désactiver la détection",
              "Utiliser des tabulations uniquement",
              "Formater manuellement chaque fichier"],
             1,
             "La détection automatique reproduit l'indentation existante, y compris "
             "ses incohérences. Fixer la règle et la partager est la seule approche "
             "stable."),
        quiz("À quoi sert le fichier .gitignore ?",
             ["À exclure des fichiers du suivi de version",
              "À empêcher Git de créer un dépôt",
              "À chiffrer les fichiers sensibles",
              "À lister les contributeurs autorisés"],
             0,
             "`.gitignore` indique à Git les motifs de fichiers à ne pas suivre : "
             "dépendances, journaux, secrets locaux. Il ne protège pas un fichier "
             "déjà commité."),
        quiz("Quel panneau du navigateur permet de connaître le temps de réponse d'un serveur ?",
             ["Éléments", "Console", "Réseau", "Application"],
             2,
             "Le panneau Réseau affiche pour chaque requête le temps d'attente du "
             "serveur, le temps de téléchargement et la taille transférée."),
    ],
}
