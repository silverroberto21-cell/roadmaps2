from bookkit.dsl import (box, code, defn, ex, fig, h, ol, p, quiz, table, ul)

CH = {
    "title": "Scripts shell et automatisation",
    "subtitle": "Transformer une suite de commandes en outil fiable, testé et "
                "documenté.",
    "duration": "3 h 15",
    "level": "Intermédiaire",
    "prereq": "chapitre 43",
    "objectives": [
        "Écrire un script robuste en Bash.",
        "Gérer variables, arguments et valeurs par défaut.",
        "Contrôler les erreurs et les interruptions.",
        "Tester un script avant de l'utiliser en production.",
        "Savoir quand choisir un langage plutôt que le shell.",
    ],
    "blocks": [
        h(2, "L'en-tête d'un script fiable"),
        p("Un script sans en-tête échoue de la pire façon : il continue après une erreur. "
          "Trois options et une vérification d'interpréteur suffisent à éviter la "
          "majorité des incidents."),
        code("""#!/usr/bin/env bash
#
# sauvegarde.sh — sauvegarde quotidienne de l'application
# Usage : ./sauvegarde.sh <destination>
#
set -euo pipefail
IFS=$'\\n\\t'

# set -e : arrêt à la première erreur
# set -u : erreur sur variable non définie
# set -o pipefail : erreur dans un tube propagée
# IFS      : évite les découpages surprenants des noms de fichiers""", "bash",
             "Six lignes qui évitent des heures de débogage"),
        table(["Option", "Effet", "Sans elle"],
              [["`-e`", "Arrêt sur erreur", "Le script continue après un échec"],
               ["`-u`", "Erreur sur variable vide", "`rm -rf /$DOSSIER` devient `rm -rf /`"],
               ["`-o pipefail`", "Code de retour du tube", "Un échec intermédiaire est ignoré"],
               ["`-x`", "Trace d'exécution", "Utile en débogage uniquement"]],
              widths=[3.0, 4.6, 5.4], first_col_bold=True,
              caption="Quatre options et leur conséquence"),
        box("attention", "La variable vide qui efface un disque",
            "`rm -rf \"$DOSSIER/\"` avec `DOSSIER` vide supprime la racine. `set -u` et "
            "les guillemets autour de chaque variable sont des protections, pas des "
            "ornements."),

        h(2, "Variables et arguments"),
        p("Un script reçoit des arguments positionnels et des options. Les valeurs par "
          "défaut, la validation et l'aide intégrée distinguent un script personnel "
          "d'un outil utilisable par d'autres."),
        code("""nom="rapport"                 # affectation sans espaces
readonly VERSION="1.2.0"
declare -i compteur=0

echo "Argument 1 : ${1:-absent}"
echo "Nombre d'arguments : $#"
echo "Tous : $@"
echo "Nom du script : $0"

# Valeur par défaut et substitution
: "${DESTINATION:=/var/backups}"
echo "Destination : $DESTINATION"

# Longueur et sous-chaîne
chaine="abcdef"
echo "${#chaine}"        # 6
echo "${chaine:2:3}"     # cde
echo "${chaine%.*}"      # retire la plus courte extension
echo "${chaine##*/}"     # retire le plus long préfixe de chemin""", "bash",
             "Dix opérations sur les variables"),
        code("""#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: sauvegarde.sh [-d destination] [-r rétention] source

  -d  répertoire de destination (défaut : /var/backups)
  -r  nombre de jours conservés (défaut : 7)
  -h  affiche cette aide
EOF
}

while getopts ":d:r:h" option; do
  case "$option" in
    d) destination="$OPTARG" ;;
    r) retention="$OPTARG" ;;
    h) usage; exit 0 ;;
    :) echo "Option -$OPTARG requiert une valeur" >&2; exit 2 ;;
    \\?) echo "Option inconnue : -$OPTARG" >&2; usage >&2; exit 2 ;;
  esac
done

source_dir="${1:-}"
[[ -d "$source_dir" ]] || { echo "Source invalide : $source_dir" >&2; exit 1; }""",
             "bash", "Des options propres et une aide"),
        defn("Code de retour conventionnel", "0 pour un succès, 1 pour une erreur "
                                            "générique, 2 pour un usage incorrect, 126 "
                                            "pour un fichier non exécutable, 127 pour "
                                            "une commande introuvable."),

        h(2, "Structures de contrôle"),
        p("Bash possède les structures attendues, avec une syntaxe qui surprend. Les "
          "guillemets et les doubles crochets sont la principale source d'erreurs."),
        code("""# Condition : [[ ]] est plus sûr que [ ]
if [[ -f "$fichier" && -r "$fichier" ]]; then
  echo "fichier lisible"
elif [[ -d "$fichier" ]]; then
  echo "c'est un répertoire"
else
  echo "introuvable" >&2
  exit 1
fi

# Comparaisons numériques
[[ "$a" -gt "$b" ]]      # supérieur
[[ "$a" -eq "$b" ]]      # égal
[[ "$a" -ne "$b" ]]      # différent

# Comparaisons de chaînes
[[ "$a" == "$b" ]]
[[ -z "$a" ]]            # vide
[[ -n "$a" ]]            # non vide
[[ "$a" =~ ^[0-9]+$ ]]   # expression régulière""", "bash",
             "Conditions et tests"),
        code("""# Boucle sur des lignes, pas sur des mots
while IFS= read -r ligne; do
  echo "Traitement : $ligne"
done < liste.txt

# Boucle sur un tableau
serveurs=("web1" "web2" "db1")
for serveur in "${serveurs[@]}"; do
  echo "Vérification de $serveur"
done

# Boucle numérique
for i in {1..5}; do echo "Itération $i"; done

# Jusqu'à réussite
tentative=0
until curl -sf http://localhost:8080/health; do
  tentative=$((tentative + 1))
  [[ $tentative -ge 30 ]] && { echo "Échec" >&2; exit 1; }
  sleep 2
done""", "bash", "Quatre boucles différentes"),
        p("`for ligne in $(cat fichier)` découpe sur les espaces et casse sur les noms "
          "contenant des espaces. `while IFS= read -r` lit réellement ligne par ligne."),

        h(2, "Fonctions et réutilisation"),
        p("Une fonction regroupe une logique nommée. Elle renvoie un code de retour, et "
          "communique un résultat par `echo`, ce qui permet de l'utiliser dans une "
          "substitution de commande."),
        code("""log() {
  local niveau="$1"; shift
  printf '%s [%s] %s\\n' "$(date -Iseconds)" "$niveau" "$*" >&2
}

requiert() {
  command -v "$1" >/dev/null 2>&1 || {
    log "ERREUR" "commande requise absente : $1"
    return 127
  }
}

retry() {
  local essais="$1"; shift
  local n=0
  until "$@"; do
    n=$((n + 1))
    [[ $n -ge $essais ]] && return 1
    sleep $((2 ** n))
  done
}

requiert curl
retry 4 curl -sf https://exemple.fr/sante""", "bash",
             "Trois fonctions réutilisables"),
        box("pratique", "`local`, `shift` et `printf`",
            "`local` limite la portée d'une variable à la fonction ; `shift` consomme "
            "les arguments un à un ; `printf` gère les caractères spéciaux mieux "
            "qu'`echo`, dont le comportement varie selon le shell."),

        h(2, "Tester un script"),
        p("Un script qui touche à la production se teste comme du code : sur une copie, "
          "avec des cas limites, et sans effet de bord."),
        code("""# Vérification de syntaxe sans exécution
bash -n script.sh

# Trace d'exécution
bash -x script.sh 2>&1 | head -50

# Analyse statique
shellcheck script.sh

# Test avec un répertoire jetable
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
cp -r donnees "$tmp/"
./script.sh "$tmp/donnees\"""", "bash", "Quatre niveaux de test"),
        defn("`trap`", "Instruction qui associe une action à un signal ou à la sortie du "
                       "script. Indispensable pour supprimer les fichiers temporaires "
                       "même en cas d'interruption."),
        code("""cleanup() {
  rm -rf "$tmp"
  log "INFO" "Nettoyage terminé"
}
trap cleanup EXIT INT TERM

# Un verrou simple pour éviter deux exécutions simultanées
exec 9>/var/lock/sauvegarde.lock
flock -n 9 || { echo "Sauvegarde déjà en cours" >&2; exit 1; }""", "bash",
             "Nettoyage garanti et exécution unique"),
        table(["Situation", "Shell", "Langage généraliste"],
              [["Enchaîner des commandes", "Idéal", "Surdimensionné"],
               ["Manipuler des fichiers", "Idéal", "Possible"],
               ["Structures de données complexes", "Limité", "Idéal"],
               ["Calcul numérique intensif", "Inadapté", "Idéal"],
               ["Appels HTTP et JSON", "Maladroit", "Idéal"],
               ["Déploiement local", "Idéal", "Excessif"]],
              widths=[5.0, 3.4, 3.4], first_col_bold=True,
              caption="Quand choisir le shell"),
        p("Au-delà de cent lignes complexes, un script Python ou Go sera plus lisible, "
          "mieux testé et plus portable. Le shell excelle comme colle entre des outils, "
          "pas comme langage applicatif."),
        box("methode", "Charte d'un script d'équipe",
            items=["En-tête avec usage et description.",
                   "`set -euo pipefail` en deuxième ligne.",
                   "Toute variable citée entre guillemets.",
                   "Aide intégrée et codes de retour documentés.",
                   "`shellcheck` dans l'intégration continue."]),
    ],
    "keypoints": [
        "`set -euo pipefail` prévient les échecs silencieux.",
        "Les variables se citent toujours entre guillemets.",
        "Une valeur par défaut s'écrit `${VAR:-défaut}`.",
        "`[[ ]]` remplace `[ ]` pour les conditions.",
        "Lire un fichier avec `while IFS= read -r`.",
        "`trap` garantit le nettoyage même en cas d'interruption.",
        "`shellcheck` détecte les erreurs classiques.",
        "Le shell colle des outils ; il ne remplace pas un langage applicatif.",
    ],
    "bridge": "Les scripts automatisent une machine. Reste à versionner ce qu'ils "
              "produisent : le chapitre suivant approfondit Git.",
    "exercises": [
        ex("Écrire un script de déploiement",
           "Le script doit construire, publier et vérifier.",
           ["Vérifiez les prérequis.",
            "Arrêtez-vous à la première erreur.",
            "Prévoyez un retour arrière."],
           [("code", """#!/usr/bin/env bash
set -euo pipefail

requiert() { command -v "$1" >/dev/null || { echo "Manque : $1" >&2; exit 1; }; }
requiert rsync
requiert npm

VERSION="${1:?version requise, ex. v1.4.2}"
CIBLE="/var/www/site"

npm ci
npm run build

rsync -az --delete dist/ "deploy@serveur:$CIBLE.releases/$VERSION/"
ssh deploy@serveur "ln -sfn $CIBLE.releases/$VERSION $CIBLE.current"

if ! curl -sf https://exemple.fr/health; then
  echo "Échec de santé : retour arrière" >&2
  ssh deploy@serveur "ln -sfn $CIBLE.releases/previous $CIBLE.current"
  exit 1
fi"""),
            "La publication dans un répertoire versionné suivie d'un lien symbolique "
            "rend le retour arrière instantané.",
            "La vérification de santé est la dernière étape : elle valide le déploiement "
            "réel, pas seulement la construction."]),
        ex("Corriger un script dangereux",
           "Ce script de nettoyage s'exécute sur le serveur.",
           ["`rm -rf $DOSSIER/*`", "Aucun guillemet", "Aucune vérification"],
           ["Une variable vide transforme la commande en `rm -rf /*`.",
            "Les espaces dans les noms cassent le découpage.",
            ("code", """#!/usr/bin/env bash
set -euo pipefail

: "${DOSSIER:?variable DOSSIER requise}"

if [[ ! -d "$DOSSIER" ]]; then
  echo "Répertoire introuvable : $DOSSIER" >&2
  exit 1
fi

case "$DOSSIER" in
  /|/var|/home|/usr) echo "Cible interdite : $DOSSIER" >&2; exit 1 ;;
esac

find "$DOSSIER" -mindepth 1 -maxdepth 1 -print -delete""")],
           level="Sécurité"),
        ex("Tester avec `shellcheck`",
           "Passez vos scripts à l'analyseur et corrigez trois avertissements.",
           ["Installez `shellcheck`.",
            "Traitez les avertissements bloquants.",
            "Ajoutez-le à l'intégration continue."],
           [("bash", """# Installation
apt install shellcheck

# Analyse
shellcheck scripts/*.sh

# Intégration continue (GitHub Actions)
# - uses: ludeeus/action-shellcheck@master"""),
            "`SC2086` (guillemets manquants) et `SC2181` (test de `$?`) sont les deux "
            "avertissements les plus fréquents.",
            "Corriger les avertissements au fur et à mesure évite qu'ils s'accumulent "
            "et deviennent impossibles à traiter."],
           level="Qualité"),
    ],
    "quiz": [
        quiz("Que fait `set -u` ?",
             ["Affiche les commandes", "Échoue sur variable non définie",
              "Ignore les erreurs", "Active le mode verbeux"],
             1,
             "Une variable non définie provoque une erreur au lieu d'être vide."),
        quiz("Pourquoi citer les variables entre guillemets ?",
             ["Pour la lisibilité", "Pour préserver les espaces et les caractères spéciaux",
              "Pour accélérer", "Ce n'est pas nécessaire"],
             1,
             "Sans guillemets, le shell découpe la valeur sur les espaces."),
        quiz("Quelle boucle lit un fichier ligne par ligne ?",
             ["`for x in $(cat f)`", "`while IFS= read -r ligne`",
              "`for x in f`", "`until read f`"],
             1,
             "`IFS=` et `-r` préservent les espaces et les antislashs."),
        quiz("À quoi sert `trap` ?",
             ["À intercepter les erreurs de syntaxe", "À exécuter du code à la sortie",
              "À créer une boucle", "À paralléliser"],
             1,
             "Il associe une action à un signal ou à la fin du script."),
        quiz("Quand préférer Python au shell ?",
             ["Pour lancer `rsync`", "Pour manipuler du JSON et des structures complexes",
              "Pour copier des fichiers", "Pour un alias"],
             1,
             "Le shell est une colle entre outils, pas un langage de structures de "
             "données."),
    ],
}
