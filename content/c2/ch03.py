from bookkit.dsl import (box, code, defn, ex, fig, h, ol, p, quiz, table, ul)

CH = {
    "title": "Le terminal au quotidien",
    "subtitle": "Redirections, tubes, filtres et recherche : composer des commandes "
                "simples pour résoudre des problèmes complexes.",
    "duration": "3 h 00",
    "level": "Débutant",
    "prereq": "chapitre 42",
    "objectives": [
        "Maîtriser les trois flux standard et leurs redirections.",
        "Composer des commandes avec les tubes.",
        "Utiliser les filtres de texte essentiels.",
        "Rechercher efficacement dans des fichiers et des arborescences.",
        "Gagner du temps avec l'historique et les alias.",
    ],
    "blocks": [
        h(2, "Trois flux"),
        p("Chaque programme reçoit une entrée et produit deux sorties : les résultats "
          "et les erreurs. Les trois flux sont numérotés et peuvent être redirigés "
          "indépendamment."),
        table(["Numéro", "Nom", "Par défaut", "Redirection"],
              [["0", "Entrée standard", "Clavier", "`<`"],
               ["1", "Sortie standard", "Terminal", "`>` ou `>>`"],
               ["2", "Erreur standard", "Terminal", "`2>` ou `2>>`"]],
              widths=[2.0, 4.2, 3.4, 3.6], first_col_bold=True,
              caption="Trois flux et leurs redirections"),
        code("""commande > sortie.txt          # écrase le fichier
commande >> sortie.txt         # ajoute à la fin
commande 2> erreurs.txt        # erreurs seules
commande > tout.txt 2>&1       # les deux dans le même fichier
commande &> tout.txt           # forme courte (bash)
commande 2>/dev/null           # ignore les erreurs
commande < entree.txt          # lit depuis un fichier

# Pipe : la sortie d'une commande devient l'entrée de la suivante
ls -l | wc -l""", "bash", "Les six redirections indispensables"),
        box("attention", "`>` écrase sans avertir",
            "Une faute de frappe sur `>` à la place de `>>` détruit un fichier. Activez "
            "`set -o noclobber` dans vos scripts pour interdire l'écrasement accidentel, "
            "et utilisez `>|` lorsque l'écrasement est volontaire."),
        defn("Tube (pipe)", "Connexion entre la sortie standard d'un processus et "
                            "l'entrée standard du suivant. Les deux s'exécutent en "
                            "parallèle et traitent les données en flux, sans fichier "
                            "intermédiaire."),

        h(2, "Composer avec les tubes"),
        p("Une commande complexe se construit par étapes, chacune vérifiable. La règle "
          "est simple : on construit progressivement, en regardant le résultat à chaque "
          "ajout."),
        code("""# Les 5 plus gros fichiers de /var
du -ah /var 2>/dev/null | sort -rh | head -5

# Les 10 adresses IP les plus fréquentes dans un journal
awk '{print $1}' /var/log/nginx/access.log | sort | uniq -c | sort -rn | head -10

# Les erreurs d'hier, sans les avertissements
journalctl --since yesterday -p err | grep -v "warning" | wc -l""", "bash",
             "Trois compositions utiles"),
        fig("flow", "Un tube, étape par étape",
            ["`journalctl -u nginx` produit des lignes",
             "`grep \" 500 \"` filtre les erreurs serveur",
             "`awk '{print $7}'` extrait l'URL",
             "`sort | uniq -c` compte les occurrences",
             "`sort -rn | head` garde le sommet"],
            height=250),
        table(["Commande", "Rôle", "Option utile"],
              [["`grep`", "Filtrer par motif", "`-i`, `-v`, `-c`, `-r`"],
               ["`awk`", "Extraire des colonnes", "`{print $n}`"],
               ["`sed`", "Remplacer du texte", "`s/a/b/g`"],
               ["`sort`", "Trier", "`-n`, `-r`, `-k`"],
               ["`uniq`", "Dédoublonner", "`-c` (après tri)"],
               ["`cut`", "Découper par caractère", "`-d -f`"],
               ["`wc`", "Compter", "`-l`, `-w`, `-c`"],
               ["`head` / `tail`", "Début ou fin", "`-n`, `-f`"],
               ["`tr`", "Transliterer", "`-d`, `-s`"],
               ["`xargs`", "Transformer en arguments", "`-n`, `-P`"]],
              widths=[2.6, 5.0, 4.0], first_col_bold=True,
              caption="Dix filtres essentiels"),
        code("""# grep : les options qui changent tout
grep -rn "TODO" src/            # récursif avec numéros de ligne
grep -i "erreur" journal.log    # insensible à la casse
grep -v "^#" config.conf        # exclure les commentaires
grep -c "GET" access.log        # compter les lignes
grep -E "(500|502|503)" access.log   # expressions étendues

# sed : remplacer dans un flux
sed 's/http:/https:/g' urls.txt
sed -i.bak 's/localhost/127.0.0.1/g' config.ini   # avec sauvegarde""", "bash",
             "Deux outils, six usages"),

        h(2, "Rechercher"),
        p("`find` parcourt l'arborescence et applique des tests ; `grep` cherche dans le "
          "contenu. Les combiner résout la plupart des recherches réelles."),
        code("""# Fichiers modifiés depuis 7 jours, plus gros que 1 Mo
find /var/log -type f -mtime -7 -size +1M -ls

# Supprimer les fichiers de plus de 30 jours, avec affichage préalable
find /tmp -type f -mtime +30 -print
find /tmp -type f -mtime +30 -delete

# Chercher un contenu dans les fichiers trouvés
find . -name "*.py" -exec grep -l "import requests" {} +

# Éviter de descendre dans .git
find . -path ./.git -prune -o -name "*.md" -print""", "bash",
             "Quatre recherches composées"),
        code("""# Alternatives modernes, plus rapides et plus lisibles
rg "TODO" --glob '!node_modules'      # ripgrep
fd -e py -x grep -l requests         # fd + exécution
fzf                                   # sélection interactive

# Localiser une commande
command -v nginx
type -a python3
which -a python3""", "bash", "Outils et localisation"),
        p("`command -v` est plus fiable que `which` dans un script : c'est une primitive "
          "du shell, et son code de retour indique directement si la commande existe."),

        h(2, "Historique, alias et raccourcis"),
        p("Le shell conserve un historique exploitable. Bien utilisé, il évite de retaper "
          "des commandes longues et de rechercher dans une documentation."),
        code("""history | grep ssh              # retrouver une commande
Ctrl+R                          # recherche inversée
!!                              # rejouer la dernière commande
sudo !!                         # la rejouer avec sudo
!$                              # dernier argument de la commande précédente
Ctrl+A / Ctrl+E                 # début / fin de ligne
Ctrl+U / Ctrl+K                 # effacer avant / après le curseur""", "bash",
             "Neuf raccourcis qui font gagner des heures"),
        code("""# ~/.bashrc
alias ll='ls -lah --color=auto'
alias gs='git status -sb'
alias dc='docker compose'

# Sortie plus sûre
set -o noclobber

# Un PATH lisible
export PATH="$HOME/.local/bin:$PATH\"""", "bash", "Quatre lignes de configuration"),
        table(["Raccourci", "Effet", "Usage"],
              [["`Ctrl+C`", "Interrompt la commande", "Sortir d'un programme bloqué"],
               ["`Ctrl+D`", "Fin d'entrée", "Quitter un shell"],
               ["`Ctrl+Z`", "Suspend", "Reprendre avec `fg`"],
               ["`Ctrl+L`", "Efface l'écran", "Sans perdre l'historique"],
               ["`Ctrl+W`", "Efface le mot précédent", "Corriger une faute"]],
              widths=[3.0, 5.0, 4.6], first_col_bold=True,
              caption="Cinq raccourcis de contrôle"),

        h(2, "Travailler avec des flux volumineux"),
        p("Un fichier de plusieurs gigaoctets ne tient pas en mémoire. Les outils de flux "
          "traitent ligne par ligne, ce qui permet de l'analyser sans le charger."),
        code("""# Suivre un journal en direct, en filtrant
tail -f /var/log/nginx/access.log | grep --line-buffered " 500 "

# Traiter un gros fichier compressé sans le décompresser
zcat archive.log.gz | awk '$9 == 500 {n++} END {print n}'

# Échantillonner au lieu de tout lire
head -n 100000 gros.csv | awk -F, '{somme += $3} END {print somme/NR}'

# Paralléliser un traitement
cat liste.txt | xargs -n 1 -P 4 traiter.sh""", "bash",
             "Quatre techniques de flux"),
        defn("Code de retour", "Entier renvoyé par un processus : 0 pour un succès, une "
                               "valeur non nulle pour un échec. Il permet d'enchaîner "
                               "des commandes de façon conditionnelle."),
        code("""commande && echo "succès"    # la seconde s'exécute si la première réussit
commande || echo "échec"     # la seconde s'exécute si la première échoue
commande; echo $?            # afficher le code de retour
set -e                       # arrêter un script à la première erreur""", "bash",
             "Quatre usages du code de retour"),
        box("methode", "Construire une commande complexe",
            items=["Écrire la première étape et regarder sa sortie.",
                   "Ajouter un tube, vérifier à nouveau.",
                   "Sauvegarder la version qui fonctionne dans un script.",
                   "Commenter chaque étape en une phrase."]),
    ],
    "keypoints": [
        "Trois flux : entrée, sortie, erreur, numérotés 0, 1 et 2.",
        "`>` écrase, `>>` ajoute ; `noclobber` protège.",
        "Un tube connecte la sortie d'un programme à l'entrée du suivant.",
        "Les filtres se composent : filtrer, extraire, trier, compter.",
        "`find` teste l'arborescence, `grep` le contenu.",
        "`command -v` est la façon fiable de tester une commande.",
        "Un code de retour 0 signifie succès.",
        "Les flux se traitent ligne par ligne, sans charger en mémoire.",
    ],
    "bridge": "Les commandes s'enchaînent à la main. Le chapitre suivant les écrit dans "
              "des scripts pour les répéter sans erreur.",
    "exercises": [
        ex("Compter les erreurs par URL",
           "Un journal Nginx contient des lignes au format combiné.",
           ["Filtrez les codes 5xx.",
            "Extrayez l'URL.",
            "Comptez et triez."],
           [("code", """awk '$9 ~ /^5/ {print $7}' /var/log/nginx/access.log \\
  | sort | uniq -c | sort -rn | head -20

# Résultat attendu
#  142 /api/commandes
#   87 /api/paiement
#   31 /recherche"""),
            "Le champ 9 du format combiné est le code HTTP, le champ 7 l'URL.",
            "`sort` avant `uniq -c` est obligatoire : `uniq` ne compare que les lignes "
            "adjacentes."]),
        ex("Sauvegarder sans écraser",
           "Un script de sauvegarde quotidien doit conserver 7 jours.",
           ["Nommez avec la date.",
            "Compressez.",
            "Purgez les archives anciennes."],
           [("code", """#!/usr/bin/env bash
set -euo pipefail

DEST=/var/backups/app
mkdir -p "$DEST"

tar -czf "$DEST/app-$(date +%F).tar.gz" -C /var/www app

find "$DEST" -name "app-*.tar.gz" -mtime +7 -delete"""),
            "`set -euo pipefail` arrête le script sur erreur, variable non définie ou "
            "échec dans un tube.",
            "La date dans le nom rend chaque archive unique et triable."]),
        ex("Trouver la cause d'une saturation",
           "Le serveur ralentit ; vous devez identifier le processus coupable.",
           ["Triez par processeur et par mémoire.",
            "Vérifiez les entrées-sorties.",
            "Observez l'évolution."],
           [("code", """# Processus les plus gourmands
ps -eo pid,ppid,pcpu,pmem,etime,cmd --sort=-pcpu | head
ps -eo pid,pcpu,pmem,cmd --sort=-pmem | head

# Entrées-sorties par processus
iotop -oPa

# Suivi de la charge
uptime
vmstat 1 5
pidstat 1 5"""),
            "La charge (`load average`) élevée avec un processeur peu utilisé indique "
            "souvent une attente d'entrées-sorties.",
            "`etime` donne l'ancienneté du processus : un processus récent et gourmand "
            "est souvent le déclencheur."],
           level="Diagnostic"),
    ],
    "quiz": [
        quiz("Comment rediriger uniquement les erreurs ?",
             ["`> fichier`", "`2> fichier`", "`&> fichier`", "`< fichier`"],
             1,
             "Le flux 2 est celui de l'erreur standard."),
        quiz("Que fait `commande | grep erreur` ?",
             ["Écrit dans un fichier", "Filtre la sortie de la commande",
              "Redirige les erreurs", "Répète la commande"],
             1,
             "Le tube envoie la sortie standard dans l'entrée de `grep`."),
        quiz("Pourquoi `uniq -c` exige-t-il un `sort` préalable ?",
             ["Pour la vitesse", "Parce qu'il ne compare que les lignes adjacentes",
              "Pour éviter les erreurs", "Ce n'est pas nécessaire"],
             1,
             "Deux lignes identiques non adjacentes sont comptées séparément."),
        quiz("Que signifie un code de retour 0 ?",
             ["Une erreur", "Un succès", "Une pause", "Rien"],
             1,
             "En Unix, 0 indique le succès ; toute autre valeur indique un échec."),
        quiz("Quelle commande affiche la fin d'un fichier en direct ?",
             ["`head -f`", "`tail -f`", "`cat -f`", "`less -f`"],
             1,
             "`tail -f` suit les nouvelles lignes au fur et à mesure."),
    ],
}
