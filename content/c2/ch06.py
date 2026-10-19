from bookkit.dsl import (box, code, defn, ex, fig, h, ol, p, quiz, table, ul)

CH = {
    "title": "Forges, revues et collaboration",
    "subtitle": "Organiser le travail à plusieurs : dépôts, demandes de fusion, "
                "automatisation et règles de contribution.",
    "duration": "3 h 00",
    "level": "Intermédiaire",
    "prereq": "chapitre 45",
    "objectives": [
        "Configurer un dépôt distant et ses protections.",
        "Choisir une stratégie de branches adaptée à l'équipe.",
        "Conduire une revue de code utile.",
        "Automatiser les vérifications d'une demande de fusion.",
        "Rédiger des règles de contribution claires.",
    ],
    "blocks": [
        h(2, "Deux familles de forges"),
        p("Une forge héberge des dépôts et ajoute la collaboration : revues, tickets, "
          "intégration continue, gestion des droits. Les principales sont GitHub, "
          "GitLab, Bitbucket et Gitea. Le vocabulaire diffère, les concepts sont "
          "identiques."),
        table(["Concept", "GitHub", "GitLab", "Gitea"],
              [["Proposition de changement", "Pull Request", "Merge Request", "Pull Request"],
               ["Pipeline", "Actions", "CI/CD", "Actions"],
               ["Registre d'images", "GHCR", "Registry", "Packages"],
               ["Tickets", "Issues", "Issues", "Issues"],
               ["Wiki", "Wiki", "Wiki", "Wiki"]],
              widths=[4.0, 3.4, 3.4, 3.2], first_col_bold=True,
              caption="Cinq concepts et leur nom selon la forge"),
        code("""# Dépôt distant
git remote -v
git remote add origin git@github.com:organisation/projet.git
git remote set-url origin git@github.com:organisation/nouveau.git

# Branche de suivi
git push -u origin feature/menu
git branch -vv
git fetch --prune origin""", "bash", "Quatre commandes de configuration"),
        box("pratique", "SSH plutôt que HTTPS",
            "Une clé SSH évite de saisir un jeton à chaque envoi. Générez une paire "
            "dédiée par machine, protégez la clé privée par une phrase secrète et "
            "ajoutez uniquement la clé publique à la forge."),

        h(2, "Stratégies de branches"),
        p("Trois modèles dominent. Le choix dépend du rythme de livraison, du nombre de "
          "contributeurs et du besoin de versions maintenues."),
        table(["Modèle", "Principe", "Adapté à"],
              [["GitHub Flow", "`main` toujours déployable, branches courtes",
                "Livraison continue"],
               ["Git Flow", "`develop`, `release/*`, `hotfix/*`", "Versions planifiées"],
               ["Trunk-based", "Commits fréquents sur `main`, drapeaux de fonctionnalité",
                "Équipes matures"]],
              widths=[3.4, 6.2, 4.0], first_col_bold=True,
              caption="Trois modèles de branches"),
        fig("flow", "GitHub Flow en cinq étapes",
            ["Branche courte depuis main",
             "Commits petits et testés",
             "Demande de fusion",
             "Revue et intégration continue",
             "Fusion puis suppression de la branche"],
            height=250),
        code("""# Une branche par intention, nommée clairement
git switch -c feat/menu-clavier
git switch -c fix/contraste-bouton
git switch -c chore/maj-dependances

# Durée de vie cible : moins de trois jours
# Une branche de trois semaines est un conflit en attente""", "bash",
             "Nommer et borner les branches"),
        p("Le modèle importe moins que la discipline : une branche qui vit trop longtemps "
          "diverge, et sa fusion devient un événement risqué plutôt qu'une routine."),

        h(2, "La demande de fusion"),
        p("Une demande de fusion bien rédigée réduit le temps de revue et documente la "
          "décision. Quatre éléments suffisent."),
        code("""## Objectif
Permettre l'ouverture du menu au clavier et annoncer son état.

## Changements
- `aria-expanded` mis à jour à l'ouverture et à la fermeture
- Échap referme et rend le focus au bouton
- Trois tests de composant ajoutés

## Vérifications
- [x] `npm run lint`
- [x] `npm test`
- [x] parcours clavier manuel
- [x] Lighthouse accessibilité ≥ 95

## Captures
<!-- avant / après sur mobile et bureau -->

Closes #42""", "markdown", "Une demande de fusion complète"),
        table(["Section", "Rôle", "Erreur fréquente"],
              [["Objectif", "Pourquoi", "Absent"],
               ["Changements", "Quoi", "Liste du diff recopiée"],
               ["Vérifications", "Preuves", "Cases cochées sans test"],
               ["Références", "Traçabilité", "Aucun ticket lié"],
               ["Captures", "Preuve visuelle", "Absentes pour un changement d'interface"]],
              widths=[3.2, 4.4, 5.0], first_col_bold=True,
              caption="Cinq sections et leurs pièges"),
        code("""# Préparer une demande de fusion propre
git fetch origin
git rebase origin/main          # ou git merge origin/main
npm run lint && npm test
git push --force-with-lease origin feature/menu""", "bash",
             "Trois vérifications avant de pousser"),
        defn("`force-with-lease`", "Variante de `--force` qui refuse l'envoi si la "
                                     "branche distante a changé depuis votre dernier "
                                     "`fetch`. Elle évite d'écraser le travail d'autrui."),

        h(2, "Conduire une revue"),
        p("La revue est un dialogue technique, pas un contrôle hiérarchique. Son but est "
          "de réduire le risque et de partager la connaissance."),
        code("""**Bloquant** — `innerHTML` reçoit une donnée d'API. Risque d'injection.
Utiliser `textContent` ou construire les nœuds.

**Question** — Que se passe-t-il si l'utilisateur clique deux fois rapidement ?
Le bouton est-il désactivé pendant l'envoi ?

**Suggestion** — `donnees` pourrait s'appeler `commandes` : le nom actuel
ne dit pas de quoi il s'agit.

**Nit** — Ligne 42 : espace avant la parenthèse (non bloquant).""", "markdown",
             "Quatre niveaux de commentaire"),
        table(["Niveau", "Signification", "Effet"],
              [["Bloquant", "À corriger avant fusion", "Blocage"],
               ["Question", "Demande de clarification", "Discussion"],
               ["Suggestion", "Amélioration possible", "Libre"],
               ["Nit", "Détail de forme", "Ignorable"]],
              widths=[3.4, 6.2, 3.6], first_col_bold=True,
              caption="Quatre niveaux de retour"),
        box("pratique", "Revue en moins de 400 lignes",
            "Au-delà de 400 lignes modifiées, la capacité de détection d'un relecteur "
            "s'effondre. Découpez la demande en plusieurs si nécessaire, ou limitez la "
            "revue aux fichiers critiques et automatisez le reste."),
        table(["Automatisable", "Humain"],
              [["Formatage, indentation", "Conception et découpage"],
               ["Erreurs de type", "Nommage et lisibilité"],
               ["Tests qui échouent", "Pertinence des tests"],
               ["Fautes de frappe", "Sécurité et cas limites"],
               ["Dépendances vulnérables", "Cohérence avec l'architecture"]],
              widths=[5.6, 6.4], first_col_bold=True,
              caption="Ce que chacun traite"),

        h(2, "Protéger la branche principale"),
        p("Les protections transforment les règles d'équipe en contraintes techniques. "
          "Elles évitent les erreurs de bonne foi, pas seulement les abus."),
        code("""# Règles typiques sur main
- Interdire le push direct
- Exiger une demande de fusion
- Exiger une approbation
- Exiger que la CI passe
- Exiger une branche à jour
- Interdire la fusion si un fil de discussion est non résolu
- Interdire le force-push et la suppression""", "text",
             "Sept règles de protection"),
        code("""# Vérification locale des conventions
npx commitlint --from origin/main
# Exemple de règle : type(scope): description
# feat(menu): ajoute la navigation clavier""", "bash",
             "Faire respecter les conventions par l'outil"),
        box("methode", "Règles de contribution minimales",
            items=["Comment installer et lancer les tests.",
                   "Format des messages de commit.",
                   "Une branche par intention, nommée explicitement.",
                   "Ce qu'une demande de fusion doit contenir.",
                   "Qui relit et sous quel délai."]),
    ],
    "keypoints": [
        "Une forge ajoute revues, tickets et automatisation au dépôt Git.",
        "GitHub Flow convient à la livraison continue.",
        "Une branche doit vivre quelques jours, pas quelques semaines.",
        "Une demande de fusion expose objectif, changements et vérifications.",
        "`--force-with-lease` évite d'écraser les commits d'autrui.",
        "Les niveaux de commentaire clarifient ce qui bloque.",
        "Ce qui est automatisable ne doit pas être relu à la main.",
        "Les protections de branche traduisent les règles en contraintes.",
    ],
    "bridge": "Le code se partage et se révise. Il faut encore une machine pour "
              "l'exécuter : le chapitre suivant prépare des serveurs reproductibles.",
    "exercises": [
        ex("Rédiger une demande de fusion",
           "Votre branche ajoute un filtre de recherche accessible.",
           ["Décrivez l'objectif en une phrase.",
            "Listez les changements vérifiables.",
            "Cochez les preuves."],
           [("markdown", """## Objectif
Filtrer les programmes sans rechargement, au clavier comme à la souris.

## Changements
- Boutons de filtre avec `aria-pressed`
- Compteur de résultats en `aria-live="polite"`
- Test de composant sur le clic et le clavier

## Vérifications
- [x] lint et tests
- [x] parcours clavier
- [x] contraste vérifié en thème sombre
- [x] dégradation sans JavaScript : la liste complète reste affichée

Closes #57"""),
            "La mention de la dégradation sans JavaScript évite une question de revue "
            "prévisible.",
            "La référence au ticket relie la décision à son contexte."]),
        ex("Configurer des protections",
           "Une équipe de cinq personnes travaille sur `main`.",
           ["Interdisez le push direct.",
            "Exigez CI et revue.",
            "Définissez la conduite en cas d'urgence."],
           [("markdown", """## Règles sur `main`
- push direct interdit
- 1 approbation obligatoire
- CI verte obligatoire
- branche à jour avec `main`
- force-push interdit

## Procédure d'urgence (incident en production)
1. Ouvrir une branche `hotfix/...`
2. Demander une revue en binôme, même rapide
3. Fusionner avec la même CI
4. Si le délai est incompatible : contournement documenté dans le ticket,
   puis rattrapage sous 24 h"""),
            "Une procédure d'urgence écrite évite que chacun improvise au pire moment.",
            "Le rattrapage sous 24 heures empêche que l'exception devienne la règle."],
           level="Organisation"),
        ex("Relire une demande de fusion",
           "Un contributeur propose 600 lignes modifiées dans un seul fichier.",
           ["Identifiez le risque principal.",
            "Proposez un découpage.",
            "Listez ce que la CI peut vérifier."],
           ["Un fichier unique de 600 lignes modifié rend la revue superficielle et la "
            "résolution de conflit probable.",
            "Découper en trois demandes : extraction du module, ajout du comportement, "
            "puis tests.",
            "La CI vérifie format, types, tests et dépendances ; la revue se concentre "
            "sur la conception et les cas limites."],
           level="Revue"),
    ],
    "quiz": [
        quiz("Quelle stratégie garde `main` toujours déployable ?",
             ["Git Flow", "GitHub Flow", "Aucune", "Release trains"],
             1,
             "GitHub Flow repose sur des branches courtes et une intégration continue."),
        quiz("Que garantit `--force-with-lease` ?",
             ["Un envoi plus rapide", "Ne pas écraser des commits distants inconnus",
              "Un historique linéaire", "Une signature"],
             1,
             "Il refuse si la branche distante a changé depuis votre dernier `fetch`."),
        quiz("Quel niveau de commentaire bloque une fusion ?",
             ["Nit", "Suggestion", "Question", "Bloquant"],
             3,
             "Le niveau bloquant signale ce qui doit être corrigé avant fusion."),
        quiz("Pourquoi automatiser le formatage ?",
             ["Pour accélérer Git", "Pour concentrer la revue sur le fond",
              "Pour réduire la taille du dépôt", "Pour éviter les conflits"],
             1,
             "Le style n'a pas besoin d'être discuté à chaque revue."),
        quiz("Que doit contenir une demande de fusion ?",
             ["Uniquement le diff", "Objectif, changements, vérifications",
              "Les noms des relecteurs", "Un résumé du ticket"],
             1,
             "Ces trois sections permettent une revue efficace et documentée."),
    ],
}
