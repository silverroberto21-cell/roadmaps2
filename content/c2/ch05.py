from bookkit.dsl import (box, code, defn, ex, fig, h, ol, p, quiz, table, ul)

CH = {
    "title": "Git avancé : branches, rebasage et récupération",
    "subtitle": "Comprendre le graphe plutôt que mémoriser des commandes, et savoir "
                "réparer une erreur coûteuse.",
    "duration": "3 h 15",
    "level": "Intermédiaire",
    "prereq": "chapitre 44",
    "objectives": [
        "Lire un graphe de commits et interpréter les références.",
        "Choisir entre fusion et rebasage.",
        "Réécrire un historique local sans risque.",
        "Récupérer un commit perdu.",
        "Résoudre un conflit méthodiquement.",
    ],
    "blocks": [
        h(2, "Le graphe avant les commandes"),
        p("Git ne stocke pas des différences, mais des instantanés reliés par des "
          "parentés. Une branche n'est qu'une étiquette mobile sur un commit ; `HEAD` "
          "indique l'étiquette courante."),
        fig("tree", "Un dépôt, ses références",
            ("HEAD → main → a1b2c3", [("main", ["a1b2c3 (courant)", "9f8e7d (parent)"]),
                                      ("feature", ["4c5d6e"]),
                                      ("tag v1.4", ["9f8e7d"])]),
            height=235),
        code("""# Lire l'historique comme un graphe
git log --oneline --graph --decorate --all
git log --oneline main..feature        # commits de feature absents de main
git log --oneline feature..main        # l'inverse
git log --oneline --no-merges --since="2 weeks ago"
git show --stat HEAD
git blame -L 20,40 fichier.js""", "bash", "Six lectures du graphe"),
        table(["Référence", "Signification"],
              [["`HEAD`", "Commit courant"],
               ["`HEAD~1`", "Premier parent du commit courant"],
               ["`HEAD^2`", "Deuxième parent (commit de fusion)"],
               ["`main@{yesterday}`", "Position de la branche hier"],
               ["`@{u}`", "Branche de suivi distante"],
               ["`abc123`", "Commit par empreinte"]],
              widths=[4.6, 7.4], first_col_bold=True,
              caption="Six façons de désigner un commit"),
        defn("Référence détachée", "État où `HEAD` pointe directement sur un commit au "
                                   "lieu d'une branche. Les commits créés dans cet état "
                                   "ne sont accessibles par aucune branche et peuvent "
                                   "être perdus."),

        h(2, "Fusion ou rebasage"),
        p("Les deux intègrent une branche, avec des conséquences opposées sur "
          "l'historique. Le choix dépend de ce que l'historique doit raconter."),
        code("""# Fusion : préserve l'historique réel, crée un commit de fusion
git switch main
git merge --no-ff feature/menu

# Rebasage : rejoue les commits sur une nouvelle base
git switch feature/menu
git rebase main

# Rebasage interactif : nettoyer avant de proposer
git rebase -i main
# pick   a1b2c3 Ajoute le bouton
# squash 4d5e6f Corrige la typo
# reword 7a8b9c Message à reformuler""", "bash", "Deux stratégies"),
        table(["Critère", "Fusion", "Rebasage"],
              [["Historique", "Fidèle, avec bifurcations", "Linéaire, réécrit"],
               ["Sécurité", "Ne réécrit rien", "Réécrit les commits"],
               ["Branche partagée", "Recommandé", "À éviter"],
               ["Branche locale", "Possible", "Recommandé"],
               ["Résolution de conflit", "Une fois", "À chaque commit rejoué"]],
              widths=[4.0, 4.2, 3.8], first_col_bold=True,
              caption="Cinq critères de choix"),
        box("attention", "Ne rebasez jamais une branche publique",
            "Réécrire des commits déjà poussés et utilisés par d'autres crée des "
            "divergences que chacun devra résoudre à la main. La règle simple : rebaser "
            "son travail local, fusionner le travail partagé."),
        code("""# Rebasage avec filet de sécurité
git branch sauvegarde-avant-rebase
git rebase main

# Si le résultat ne convient pas
git rebase --abort
git reset --hard sauvegarde-avant-rebase""", "bash",
             "Un aller-retour toujours possible"),

        h(2, "Résoudre un conflit"),
        p("Un conflit n'est pas une erreur : Git signale qu'il ne peut pas décider seul. "
          "La résolution consiste à produire l'état voulu, puis à l'enregistrer."),
        code("""git merge feature/menu
# CONFLICT (content): Merge conflict in src/menu.js

# Le fichier contient :
# <<<<<<< HEAD
# const ouvrir = () => panneau.classList.add("ouvert");
# =======
# const ouvrir = () => panneau.hidden = false;
# >>>>>>> feature/menu

# 1. Comprendre les deux intentions
git log --oneline HEAD...feature/menu -- src/menu.js

# 2. Produire la version correcte, sans marqueurs
# 3. Vérifier
git diff
git add src/menu.js

# 4. Terminer
git merge --continue""", "bash", "Une résolution méthodique"),
        table(["Commande", "Effet", "Quand"],
              [["`git merge --abort`", "Annule la fusion", "Conflit trop large"],
               ["`git checkout --ours f`", "Garde la version locale", "Fichier généré"],
               ["`git checkout --theirs f`", "Garde la version entrante", "Idem"],
               ["`git mergetool`", "Ouvre un outil visuel", "Conflits nombreux"],
               ["`git rerere`", "Mémorise les résolutions", "Rebasages répétés"]],
              widths=[4.4, 4.4, 3.4], first_col_bold=True,
              caption="Cinq outils de conflit"),
        box("pratique", "Réduire les conflits",
            "Des commits petits, des branches courtes et des fichiers découpés par "
            "responsabilité réduisent mécaniquement les conflits. Un fichier de mille "
            "lignes modifié par trois personnes produit des conflits quotidiens."),

        h(2, "Réparer"),
        p("Git conserve presque tout. La récupération repose sur le journal des "
          "références, qui enregistre chaque déplacement de `HEAD`."),
        code("""# J'ai réinitialisé et perdu un commit
git reflog
# a1b2c3 HEAD@{3}: commit: Ajoute la validation

git branch sauvetage a1b2c3
git switch sauvetage

# J'ai supprimé une branche non fusionnée
git reflog --all | grep feature/menu
git branch feature/menu <sha>

# Annuler un commit poussé, sans réécrire
git revert <sha>""", "bash", "Trois récupérations"),
        code("""# Annulations locales, du plus doux au plus radical
git restore fichier.js              # annule les modifications non préparées
git restore --staged fichier.js     # désindexe
git commit --amend                  # corrige le dernier commit (local)
git reset --soft HEAD~1             # défait le commit, garde les changements préparés
git reset --mixed HEAD~1            # défait et désindexe
git reset --hard HEAD~1             # détruit les changements""", "bash",
             "Six niveaux d'annulation"),
        defn("`git reflog`", "Journal local des déplacements de référence, conservé "
                             "environ 90 jours. C'est le filet de sécurité de Git : tout "
                             "commit ayant existé y figure."),

        h(2, "Nettoyer avant de partager"),
        p("Un historique lisible s'obtient en réorganisant ses propres commits avant de "
          "les proposer. Trois opérations couvrent la majorité des cas."),
        code("""# Réordonner, fusionner, renommer, supprimer
git rebase -i HEAD~5

# Diviser un commit trop gros
git reset HEAD~1
git add -p
git commit -m "Extrait la validation du formulaire"
git add .
git commit -m "Ajoute le style des messages d'erreur"

# Chercher le commit qui a introduit un bogue
git bisect start
git bisect bad
git bisect good v1.3.0
# ... git bisect good|bad jusqu'à identification
git bisect reset""", "bash", "Trois opérations de nettoyage"),
        box("methode", "Avant de demander une fusion",
            items=["`git log --oneline main..HEAD` : les commits sont-ils cohérents ?",
                   "`git diff main...HEAD` : le contenu est-il complet ?",
                   "Les tests passent-ils après un rebasage ?",
                   "La branche est-elle à jour avec `main` ?"]),
    ],
    "keypoints": [
        "Git stocke des instantanés reliés par des parentés, pas des différences.",
        "Une branche est une étiquette mobile sur un commit.",
        "Fusion pour l'historique partagé, rebasage pour le travail local.",
        "Ne jamais rebaser une branche publique.",
        "Un conflit se résout en comprenant les deux intentions.",
        "`git reflog` permet de retrouver un commit perdu.",
        "`git revert` annule sans réécrire l'historique.",
        "Le rebasage interactif nettoie avant de partager.",
    ],
    "bridge": "Git fonctionne en local. Le chapitre suivant l'ouvre sur la collaboration : "
              "forges, revues et automatisation.",
    "exercises": [
        ex("Nettoyer une branche",
           "Quatre commits de travail doivent devenir un commit cohérent.",
           ["Nommez la branche de secours.",
            "Fusionnez les commits.",
            "Reformulez le message."],
           [("code", """git branch sauvegarde
git rebase -i main

# pick a1b2c3 WIP
# squash 4d5e6f Correction
# squash 7a8b9c Encore une correction
# squash 0c1d2e Tests

# Message final :
# Ajoute le filtre des programmes avec tests
# - filtres accessibles au clavier
# - compteur annoncé
# - trois tests unitaires"""),
            "La branche de secours permet de revenir à l'état initial sans effort.",
            "Le message final décrit le résultat, pas la suite des tentatives."]),
        ex("Récupérer un commit perdu",
           "Un `reset --hard` a supprimé le travail de la journée.",
           ["Consultez le reflog.",
            "Identifiez le commit.",
            "Recréez une branche."],
           [("code", """git reflog
# 9f8e7d HEAD@{2}: reset: moving to HEAD~1
# a1b2c3 HEAD@{3}: commit: Ajoute la validation

git branch travail-retrouve a1b2c3
git switch travail-retrouve
git log --oneline -3"""),
            "Le reflog conserve les positions successives de `HEAD` pendant environ "
            "90 jours.",
            "Travailler sur une nouvelle branche avant de décider de réintégrer évite de "
            "perdre à nouveau l'état."]),
        ex("Résoudre un conflit de fusion",
           "Deux branches modifient la même fonction de validation.",
           ["Lisez l'intention de chaque version.",
            "Produisez une version qui satisfait les deux.",
            "Vérifiez par un test."],
           [("code", """#!/usr/bin/env bash
set -euo pipefail
git merge feature/validation

# Inspecter les deux versions du fichier
git show HEAD:src/validation.js
git show feature/validation:src/validation.js

# Après résolution manuelle et test
git add src/validation.js
git commit --no-edit"""),
            "Comparer les deux versions complètes aide plus que lire les marqueurs "
            "extraits.",
            "Un test lancé après résolution prouve que la combinaison fonctionne, pas "
            "seulement qu'elle compile."],
           level="Collaboration"),
    ],
    "quiz": [
        quiz("Qu'est-ce qu'une branche Git ?",
             ["Une copie des fichiers", "Une étiquette sur un commit",
              "Un dossier", "Un serveur"],
             1,
             "Une branche est une référence mobile vers un commit."),
        quiz("Quand le rebasage est-il déconseillé ?",
             ["Sur une branche locale", "Sur une branche publique partagée",
              "Avant une fusion", "Après un commit"],
             1,
             "Réécrire un historique partagé crée des divergences pour tous."),
        quiz("Quelle commande retrouve un commit perdu ?",
             ["`git log`", "`git reflog`", "`git fsck`", "`git status`"],
             1,
             "Le reflog conserve les déplacements de référence."),
        quiz("Que fait `git revert` ?",
             ["Réécrit l'historique", "Crée un commit qui annule un précédent",
              "Supprime une branche", "Réinitialise le dépôt"],
             1,
             "Il produit un nouveau commit inverse, sans toucher à l'historique."),
        quiz("Que fait `git reset --hard` ?",
             ["Garde les modifications", "Détruit les modifications",
              "Pousse les commits", "Crée une branche"],
             1,
             "L'option `--hard` réinitialise l'arbre de travail et l'index."),
    ],
}
