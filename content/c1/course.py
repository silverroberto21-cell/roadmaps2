"""Métadonnées du cours 1 et plan des parties."""

COURSE = {
    "title": "Développement web front-end",
    "short": "HTML5, CSS3 et JavaScript, du premier fichier HTML à la mise en production. "
             "Un parcours progressif : structure du document, mise en forme, mises en page "
             "modernes, interactivité, accessibilité, performance et déploiement.",
    "short_header": "Développement web front-end",
    "level": "Débutant à intermédiaire",
    "subtitle": "Construire des interfaces web modernes, accessibles et performantes, "
                "avec les standards du Web.",
    "description": [
        "Ce cours part d'une page blanche. Il suppose seulement que vous savez "
        "utiliser un ordinateur, un clavier et un navigateur. À la fin, vous aurez "
        "construit un site complet, versionné, optimisé et publié.",
        "La progression suit celle d'un projet réel : on commence par comprendre "
        "comment le Web fonctionne, puis on écrit du HTML sémantique, on met en "
        "forme avec CSS, on compose des mises en page responsive, on ajoute de "
        "l'interactivité en JavaScript, avant de traiter la qualité, la performance, "
        "la sécurité et la mise en ligne.",
        "Chaque chapitre combine explications, schémas, tableaux de synthèse et "
        "exemples exécutables. Les exercices sont corrigés pas à pas et les quiz "
        "permettent de vérifier les acquis avant de continuer.",
    ],
    "contains": [
        "45 chapitres progressifs, du premier fichier HTML aux listes de données.",
        "Plus de 180 exemples de code commentés et directement réutilisables.",
        "Des tableaux de synthèse pour les balises, les propriétés CSS et les API JavaScript.",
        "Des exercices corrigés et des quiz à la fin de chaque chapitre.",
        "Un projet guidé de bout en bout au dernier chapitre.",
    ],
    "method": [
        "Travaillez avec un éditeur de texte et un navigateur ouverts en permanence.",
        "Recopiez chaque exemple au clavier : ne copiez-collez pas les premières semaines.",
        "Faites les exercices avant de lire les corrigés, même de manière incomplète.",
        "Après chaque chapitre, reformulez à voix haute ce que vous avez appris.",
        "Versionnez votre travail dès le chapitre 35, puis à chaque séance.",
    ],
    "parts": [
        {
            "id": "c1p1",
            "label": "Partie I",
            "title": "Les fondations du Web",
            "description": "Comprendre le fonctionnement du Web, préparer son "
                           "environnement et écrire ses premières pages HTML valides.",
            "chapters": [f"content.c1.ch{n:02d}" for n in range(1, 9)],
        },
        {
            "id": "c1p2",
            "label": "Partie II",
            "title": "CSS : mise en forme et design",
            "description": "Maîtriser la cascade, la typographie, les couleurs et le "
                           "modèle de boîte pour transformer un document en interface.",
            "chapters": [f"content.c1.ch{n:02d}" for n in range(9, 17)],
        },
        {
            "id": "c1p3",
            "label": "Partie III",
            "title": "Mise en page moderne et accessibilité",
            "description": "Composer avec Flexbox, Grid, le positionnement, les media "
                           "queries et les unités fluides, sans jamais sacrifier l'accès.",
            "chapters": [f"content.c1.ch{n:02d}" for n in range(17, 24)],
        },
        {
            "id": "c1p4",
            "label": "Partie IV",
            "title": "JavaScript et interactivité",
            "description": "Du langage aux interfaces réactives : DOM, événements, "
                           "formulaires, asynchrone, stockage et état.",
            "chapters": [f"content.c1.ch{n:02d}" for n in range(24, 32)],
        },
        {
            "id": "c1p5",
            "label": "Partie V",
            "title": "Qualité, performance et mise en production",
            "description": "Déboguer, mesurer, sécuriser, versionner et publier un site "
                           "professionnel, puis le maintenir dans le temps.",
            "chapters": [f"content.c1.ch{n:02d}" for n in range(32, 37)],
        },
        {
            "id": "c1p6",
            "label": "Partie VI",
            "title": "Approfondissements",
            "description": "Les fonctionnalités CSS contemporaines, les composants "
                           "réutilisables, le contenu multilingue et la maintenance "
                           "d'un projet dans la durée.",
            "chapters": [f"content.c1.ch{n:02d}" for n in range(37, 41)],
        },
        {
            "id": "c1p7",
            "label": "Partie VII",
            "title": "Le Web comme plateforme",
            "description": "Installer un site comme une application, le faire fonctionner "
                           "hors-ligne, dessiner avec SVG et canvas, soigner la "
                           "typographie et tester l'interface.",
            "chapters": [f"content.c1.ch{n:02d}" for n in range(41, 46)],
        },
    ],
}
