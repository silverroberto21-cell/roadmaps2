from bookkit.dsl import (box, code, defn, ex, fig, h, ol, p, quiz, table, ul)

CH = {
    "title": "Maintenir un site dans le temps",
    "subtitle": "Revue de code, documentation, dette technique et travail en équipe : "
                "ce qui distingue un projet livré d'un projet durable.",
    "duration": "2 h 45",
    "level": "Intermédiaire",
    "prereq": "chapitre 39",
    "objectives": [
        "Conduire une revue de code utile et bienveillante.",
        "Écrire une documentation qui vieillit bien.",
        "Identifier et traiter la dette technique.",
        "Organiser des branches et des versions.",
        "Transmettre un projet à un autre développeur.",
    ],
    "blocks": [
        h(2, "La revue de code"),
        p("Une revue de code vérifie trois choses : la correction, la lisibilité et la "
          "cohérence avec le reste du projet. Elle ne sert ni à imposer un style "
          "personnel ni à réécrire le travail à la place de l'auteur."),
        table(["Niveau", "Question", "Exemple"],
              [["Correction", "Le code fait-il ce qui est demandé ?", "Cas limites, erreurs"],
               ["Lisibilité", "Un tiers comprend-il l'intention ?", "Noms, découpage"],
               ["Cohérence", "Respecte-t-il les conventions ?", "Structure, nommage"],
               ["Sécurité", "Introduit-il une faille ?", "Injection, secret"],
               ["Testabilité", "Peut-on le vérifier ?", "Dépendances, pureté"]],
              widths=[3.4, 5.0, 4.2], first_col_bold=True,
              caption="Cinq niveaux de revue"),
        code("""# Un commentaire de revue utile

**Bloquant** — `innerHTML` reçoit directement `commentaire.texte`, qui vient
d'une API publique. Utilisez `textContent` ou construisez les nœuds.

**Question** — Cette fonction gère-t-elle le cas où la liste est vide ?
Je ne vois pas d'état affiché dans ce cas.

**Suggestion (non bloquant)** — `donnees` pourrait devenir `commandes` :
le nom actuel ne dit pas de quelles données il s'agit.""", "markdown",
             "Trois formulations, trois intentions"),
        p("Distinguer explicitement bloquant, question et suggestion évite les "
          "malentendus : l'auteur sait ce qui doit changer avant la fusion et ce qui "
          "relève du débat."),
        box("attention", "Revue et style automatique",
            "Les débats d'indentation ou de point-virgule n'ont pas leur place dans une "
            "revue. Un formateur automatique les règle une fois pour toutes ; la revue "
            "se concentre sur ce qu'aucun outil ne voit."),
        fig("flow", "Le parcours d'une contribution",
            ["Branche dédiée",
             "Commits atomiques",
             "Tests et lint locaux",
             "Demande de fusion",
             "Revue et corrections",
             "Fusion puis suppression de la branche"],
            height=265),

        h(2, "Documenter ce qui ne se lit pas dans le code"),
        p("Le code dit *comment*. La documentation doit dire *pourquoi* : les décisions, "
          "les contraintes, les compromis. Un commentaire qui paraphraserait le code "
          "n'ajoute rien."),
        code("""// Inutile : répète le code
// Incrémente le compteur
compteur += 1;

// Utile : explique une décision non évidente
// Le serveur limite les requêtes à 5 par seconde et ne renvoie pas
// d'en-tête Retry-After : on attend 250 ms pour rester sous la limite.
await pause(250);""", "js", "Deux commentaires, deux valeurs"),
        table(["Document", "Contenu", "Public"],
              [["`README.md`", "Installation, usage, structure", "Toute l'équipe"],
               ["`CONTRIBUTING.md`", "Conventions, processus", "Contributeurs"],
               ["`CHANGELOG.md`", "Versions et changements", "Utilisateurs"],
               ["`docs/decisions/`", "Décisions d'architecture", "Équipe technique"],
               ["Commentaires", "Intentions locales", "Lecteur du fichier"]],
              widths=[4.0, 5.0, 3.6], first_col_bold=True,
              caption="Cinq documents et leurs publics"),
        defn("Décision d'architecture", "Note courte qui expose un choix, les options "
                                        "écartées et ses conséquences. Elle évite qu'un "
                                        "nouveau venu défasse un choix sans en connaître "
                                        "les raisons."),
        code("""# 004 — Pas de cadre applicatif pour le site vitrine

Date : 2026-02-11

## Contexte
Trois pages, peu d'interactions, un seul développeur, hébergement statique.

## Décision
HTML, CSS et JavaScript natifs, sans cadre applicatif.

## Conséquences
- Bundle minimal, démarrage instantané.
- Pas de rendu déclaratif : les mises à jour du DOM sont manuelles.
- Migration à envisager si le nombre d'écrans dépasse la vingtaine.""", "markdown",
             "Une décision documentée en dix lignes"),

        h(2, "La dette technique"),
        p("La dette technique est un raccourci assumé ou subi qui rend les évolutions "
          "futures plus coûteuses. Elle n'est pas nécessairement une faute : un "
          "prototype livré vite peut être un bon compromis, à condition d'être "
          "explicite."),
        table(["Type", "Symptôme", "Traitement"],
              [["Code dupliqué", "Même correction à trois endroits", "Extraire un module"],
               ["Nommage flou", "Personne ne sait où chercher", "Renommer, documenter"],
               ["Dépendance obsolète", "Vulnérabilités, blocages", "Mettre à jour"],
               ["Absence de tests", "Peur de modifier", "Tests sur les zones stables"],
               ["Configuration implicite", "Marche chez une personne", "Automatiser"]],
              widths=[3.8, 4.8, 4.0], first_col_bold=True,
              caption="Cinq formes de dette"),
        code("""# Un registre de dette, dans le dépôt
| Zone | Dette | Impact | Coût estimé |
|------|-------|--------|-------------|
| `menu.js` | Deux implémentations du menu | Corrections doubles | 2 h |
| `styles/` | Trois valeurs d'espacement hors échelle | Incohérence visuelle | 1 h |
| `api.js` | Aucun test | Régression silencieuse | 4 h |""", "markdown",
             "Un tableau visible plutôt qu'une mémoire collective"),
        box("pratique", "La règle du boy-scout",
            "Laissez le fichier un peu plus propre que vous ne l'avez trouvé : un nom "
            "clarifié, un test ajouté, une fonction extraite. Ces petites améliorations "
            "coûtent peu et empêchent la dégradation."),

        h(2, "Branches, versions et livraisons"),
        p("Une organisation simple suffit à la plupart des projets : une branche "
          "principale stable, des branches courtes par contribution, et des étiquettes "
          "de version."),
        code("""main                 toujours livrable
├── feat/menu-clavier
├── fix/contraste-bouton
└── chore/maj-dependances

# Versionnement sémantique
v1.4.2
 │ │ └── correctif
 │ └──── ajout compatible
 └────── rupture de compatibilité""", "text", "Une organisation lisible"),
        table(["Type de changement", "Version", "Exemple"],
              [["Correctif compatible", "`1.4.2 → 1.4.3`", "Bug d'affichage"],
               ["Ajout compatible", "`1.4.3 → 1.5.0`", "Nouvelle page"],
               ["Rupture", "`1.5.0 → 2.0.0`", "Suppression d'une API"]],
              widths=[4.4, 4.0, 4.2], first_col_bold=True,
              caption="Trois types de changement"),
        code("""# Journal des versions
## [1.5.0] — 2026-04-02
### Ajouté
- Filtre des programmes avec compteur annoncé.
### Corrigé
- Contraste du bouton secondaire en thème sombre (AA).
### Modifié
- Le menu se ferme avec Échap et rend le focus au bouton.""", "markdown",
             "Un journal lisible par les utilisateurs"),
        p("Le journal des versions s'écrit pour ceux qui utilisent le logiciel, pas pour "
          "les développeurs. « Correction de divers problèmes » n'informe personne."),

        h(2, "Transmettre"),
        p("Un projet se transmet dans une situation de crise : un départ, une urgence, "
          "un changement d'équipe. La documentation doit permettre à quelqu'un qui n'a "
          "jamais vu le code de le lancer en moins d'une heure."),
        code("""# Vérification de reprise

- [ ] Un nouveau venu clone le dépôt et lance le site en moins de 30 min.
- [ ] Les variables d'environnement nécessaires sont listées.
- [ ] La procédure de déploiement est écrite et testée.
- [ ] Les accès (hébergement, domaine, analytics) sont inventoriés.
- [ ] Les décisions structurantes sont documentées.""", "markdown",
             "Une liste qui révèle les angles morts"),
        box("retenir", "Ce qui reste quand on part",
            "Ni vous ni votre mémoire ne serez disponibles. Ce qui reste, c'est le "
            "dépôt, la documentation, les tests et l'historique. Investissez dans ce "
            "qui reste."),
        fig("columns", "Quatre piliers de la maintenance",
            [("Documentation", ["README", "Décisions", "Journal"]),
             ("Tests", ["Unitaires", "Composants", "Parcours"]),
             ("Automatisation", ["Lint", "Construction", "Déploiement"]),
             ("Organisation", ["Branches", "Revues", "Versions"])],
            height=205),
        box("methode", "Une heure par mois",
            items=["Mettre à jour les dépendances et relancer les tests.",
                   "Relire le registre de dette et en traiter une ligne.",
                   "Vérifier que la documentation correspond encore au code.",
                   "Tester la procédure de déploiement depuis un environnement propre."]),
    ],
    "keypoints": [
        "Une revue vérifie correction, lisibilité, cohérence, sécurité et testabilité.",
        "Distinguez bloquant, question et suggestion.",
        "Le formateur automatique règle le style ; la revue traite le reste.",
        "La documentation explique le pourquoi, pas le comment.",
        "Une décision d'architecture note les options écartées.",
        "La dette technique se registre et se traite par petites touches.",
        "Un projet se transmet par le dépôt, les tests et la documentation.",
    ],
    "bridge": "Le cours 1 s'achève ici : du premier fichier HTML à un site maintenu. "
              "Le cours 2 prend le relais sur l'infrastructure, la livraison continue et "
              "l'exploitation.",
    "exercises": [
        ex("Conduire une revue",
           "Une demande de fusion ajoute un filtre de recherche en JavaScript.",
           ["Relevez un point bloquant.",
            "Posez une question ouverte.",
            "Formulez une suggestion non bloquante."],
           [("markdown", """**Bloquant** — La recherche est réinitialisée à chaque rendu :
`liste.innerHTML = ""` efface aussi les nœuds du message « aucun résultat ».
Utilisez `replaceChildren` avec les nœuds construits.

**Question** — Que se passe-t-il si l'utilisateur tape très vite ? Une
requête lente peut écraser une réponse plus récente. Un `AbortController`
est-il prévu ?

**Suggestion** — `filtrer()` mélange filtrage et rendu. Extraire la
fonction de filtrage la rendrait testable sans DOM."""),
            "Trois niveaux distincts permettent à l'auteur de prioriser sans deviner.",
            "La question ouverte laisse l'auteur expliquer un choix peut-être délibéré."]),
        ex("Rédiger une décision d'architecture",
           "L'équipe hésite entre stockage local et cookies pour un panier.",
           ["Exposez le contexte.",
            "Tranchez et justifiez.",
            "Listez les conséquences."],
           [("markdown", """# 007 — Panier dans `localStorage`

## Contexte
Panier non authentifié, moins de 50 articles, besoin de survie entre
deux visites, aucun traitement serveur avant la commande.

## Décision
`localStorage`, clé `panier.v1`, structure `{ version, lignes[] }`.

## Options écartées
- Cookie : 4 Ko insuffisants pour un panier moyen.
- IndexedDB : complexité inutile pour ce volume.
- Session serveur : impose une authentification dès le premier article.

## Conséquences
- Données visibles et modifiables par l'utilisateur : validation à la commande.
- Taille limitée : surveiller le quota et proposer un message clair.
- Migration prévue par le champ `version`."""),
            "Les options écartées évitent qu'un nouveau venu propose la même idée dans "
            "six mois.",
            "Les conséquences assument le coût du choix, y compris ses risques."],
           level="Documentation"),
        ex("Préparer une reprise de projet",
           "Vous quittez le projet dans deux semaines.",
           ["Listez ce qui n'est pas dans le code.",
            "Rédigez la procédure de déploiement.",
            "Faites relire par un tiers."],
           [("markdown", """## Procédure de déploiement

1. `npm ci && npm run build`
2. Vérifier `dist/` : pas de `.map`, pas de `.env`
3. `rsync -avz --delete dist/ deploy@serveur:/var/www/site/`
4. Vider le cache CDN : `curl -X POST https://cdn/.../purge`
5. Contrôler : page d'accueil, formulaire, en-têtes de sécurité
6. En cas d'échec : `git checkout v1.4.3 && npm run build` puis recommencer

## Accès
- Hébergement : coffre partagé, entrée « site-asso »
- Nom de domaine : registrar, compte de l'association
- Analytics : compte de l'association"""),
            "Les accès et la procédure sont les deux informations les plus souvent "
            "perdues lors d'un départ.",
            "La procédure de retour arrière est aussi importante que la procédure de "
            "déploiement."],
           level="Transmission"),
    ],
    "quiz": [
        quiz("Que doit vérifier en priorité une revue de code ?",
             ["Le style d'indentation", "La correction et la lisibilité",
              "La vitesse de frappe", "Le nombre de lignes"],
             1,
             "Correction, lisibilité, cohérence, sécurité et testabilité."),
        quiz("Quel type de commentaire est le plus utile ?",
             ["Celui qui paraphrase le code", "Celui qui explique une décision",
              "Celui qui commente chaque ligne", "Aucun"],
             1,
             "Le code dit comment ; le commentaire explique pourquoi."),
        quiz("Qu'est-ce que la dette technique ?",
             ["Un emprunt bancaire", "Un raccourci qui renchérit les évolutions",
              "Un bug non corrigé", "Une dépendance payante"],
             1,
             "Elle peut être assumée, à condition d'être explicite et suivie."),
        quiz("Que signifie `1.5.0 → 2.0.0` en versionnement sémantique ?",
             ["Un correctif", "Un ajout compatible", "Une rupture de compatibilité", "Une préversion"],
             2,
             "Le changement d'indicatif majeur signale une incompatibilité."),
        quiz("À quoi sert un document de décision d'architecture ?",
             ["À documenter le code ligne par ligne", "À conserver les raisons d'un choix",
              "À remplacer les tests", "À mesurer la performance"],
             1,
             "Il conserve le contexte et les options écartées, utiles des mois plus tard."),
    ],
}
