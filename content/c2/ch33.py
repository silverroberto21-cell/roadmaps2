from bookkit.dsl import (box, code, defn, ex, fig, h, ol, p, quiz, table, ul)

CH = {
    "title": "CI/CD : principes et structure d'un pipeline",
    "subtitle": "Automatiser de la première ligne de code à la production, avec des "
                "étapes rapides, fiables et observables.",
    "duration": "3 h 15",
    "level": "Intermédiaire",
    "prereq": "chapitre 72",
    "objectives": [
        "Distinguer intégration, livraison et déploiement continus.",
        "Concevoir les étapes d'un pipeline efficace.",
        "Ordonner les contrôles du plus rapide au plus lent.",
        "Construire un artefact unique et le promouvoir.",
        "Diagnostiquer un pipeline lent ou instable.",
    ],
    "blocks": [
        h(2, "Trois mots, trois engagements"),
        p("Intégration continue, livraison continue et déploiement continu désignent des "
          "pratiques différentes. Les confondre conduit à promettre plus que ce que "
          "l'équipe peut tenir."),
        table(["Pratique", "Ce qui est automatisé", "Décision humaine"],
              [["Intégration continue", "Fusion et vérification fréquentes", "Aucune"],
               ["Livraison continue", "Tout jusqu'à l'artefact prêt", "Déployer ou non"],
               ["Déploiement continu", "Tout, jusqu'en production", "Aucune, sauf incident"]],
              widths=[4.6, 5.0, 4.0], first_col_bold=True,
              caption="Trois pratiques"),
        defn("Pipeline", "Enchaînement automatisé d'étapes déclenché par un changement : "
                         "construction, tests, analyse, publication, déploiement."),
        code("""# Un pipeline minimal mais complet
stages:
  - lint        # 30 s
  - test        # 2 min
  - build       # 1 min
  - scan        # 1 min
  - deploy      # 2 min""", "yaml", "Cinq étapes"),

        h(2, "Le trajet d'un changement"),
        p("Chaque étape doit réduire un risque identifiable. Une étape qui ne peut jamais "
          "échouer est une étape décorative : elle donne une fausse assurance."),
        fig("flow", "Du commit à la production",
            ["Commit sur une branche",
             "Vérification de format et d'analyse statique",
             "Tests unitaires et d'intégration",
             "Construction de l'artefact",
             "Analyse de sécurité",
             "Publication dans le registre",
             "Déploiement en recette puis en production"],
            height=280),
        table(["Étape", "Risque couvert", "Durée cible"],
              [["Format et lint", "Incohérence de style", "< 1 min"],
               ["Compilation", "Erreur de syntaxe", "< 2 min"],
               ["Tests unitaires", "Régression logique", "< 3 min"],
               ["Tests d'intégration", "Incompatibilité entre composants", "< 10 min"],
               ["Construction d'image", "Artefact non reproductible", "< 5 min"],
               ["Analyse de vulnérabilités", "Dépendance dangereuse", "< 3 min"],
               ["Déploiement", "Configuration invalide", "< 5 min"]],
              widths=[5.0, 4.6, 3.0], first_col_bold=True,
              caption="Sept étapes et leurs cibles"),
        box("pratique", "Échouer vite",
            "Un pipeline de dix minutes dont la première minute détecte 80 % des erreurs "
            "vaut mieux qu'un pipeline de trois minutes qui échoue à la fin. Placez les "
            "contrôles rapides en premier."),
        code("""# Cache des dépendances : gain typique de 30 à 60 s par exécution
cache:
  key:
    files: [package-lock.json]
  paths:
    - node_modules/

# Parallélisation des tests indépendants
test:
  parallel: 4""", "yaml", "Deux optimisations"),

        h(2, "Artefact unique"),
        p("Construire une fois, promouvoir partout. Reconstruire pour chaque "
          "environnement annule la garantie que l'artefact testé est celui déployé."),
        fig("compare", "Deux approches de promotion",
            ("RECONSTRUIRE", ["Un artefact par environnement", "Tests non représentatifs",
                              "Dérive possible"],
             "PROMOUVOIR", ["Un artefact identifié", "Tests représentatifs",
                            "Traçabilité complète"]),
            height=210),
        code("""# Le même digest traverse les environnements
docker build -t registry.exemple.fr/app:1.4.2 .
docker push registry.exemple.fr/app:1.4.2
DIGEST=$(docker inspect --format '{{index .RepoDigests 0}}' app:1.4.2)

# Recette
kubectl set image deployment/app app=$DIGEST -n recette
kubectl rollout status deployment/app -n recette

# Production : exactement le même digest
kubectl set image deployment/app app=$DIGEST -n production""", "bash",
             "Une promotion par empreinte"),
        defn("Empreinte (digest)", "Identifiant de contenu immuable. Promouvoir par "
                                   "empreinte garantit que l'image testée est exactement "
                                   "celle qui sera exécutée."),
        code("""# Vérifier ce qui tourne réellement
kubectl get deployment app -n production \\
  -o jsonpath='{.spec.template.spec.containers[0].image}'

# Vérifier la correspondance avec la version annoncée
kubectl get pods -n production -o jsonpath='{.items[*].status.containerStatuses[*].imageID}'""",
             "bash", "Deux vérifications"),

        h(2, "Déclencheurs"),
        p("Un pipeline se déclenche sur des événements. Le choix des déclencheurs "
          "détermine le coût et la pertinence des vérifications."),
        table(["Déclencheur", "Usage", "Coût"],
              [["Chaque commit sur une branche", "Vérification rapide", "Élevé"],
               ["Demande de fusion", "Vérification complète", "Moyen"],
               ["Fusion sur `main`", "Construction et publication", "Faible"],
               ["Étiquette de version", "Publication officielle", "Très faible"],
               ["Planification", "Analyse de sécurité", "Faible"]],
              widths=[5.4, 5.0, 3.2], first_col_bold=True,
              caption="Cinq déclencheurs"),
        code("""# GitHub Actions
on:
  pull_request:
  push:
    branches: [main]
    tags: ["v*"]
  schedule:
    - cron: "0 3 * * 1"

# Ne pas lancer deux pipelines identiques
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true""", "yaml", "Des déclencheurs maîtrisés"),
        box("attention", "Annuler les exécutions obsolètes",
            "Sur une branche active, plusieurs pipelines se chevauchent. Sans "
            "`concurrency`, les ressources sont gaspillées et les résultats peuvent "
            "sembler contradictoires."),

        h(2, "Pipelines instables"),
        p("Un test qui échoue une fois sur dix détruit la confiance dans le pipeline. "
          "L'équipe finit par relancer sans lire, ce qui annule tout le bénéfice."),
        table(["Symptôme", "Cause", "Correction"],
              [["Échec intermittent", "Test dépendant du temps ou de l'ordre", "Isoler, horloge fixe"],
               ["Lenteur croissante", "Cache inopérant", "Clé de cache stable"],
               ["Étape ignorée", "Condition trop large", "Restreindre le déclencheur"],
               ["Échec aléatoire réseau", "Dépendance externe", "Simuler ou réessayer"],
               ["Absence de résultat", "Quota de workers", "Vérifier la file"]],
              widths=[4.2, 5.0, 4.6], first_col_bold=True,
              caption="Cinq symptômes"),
        code("""# Mesurer la durée par étape
# Dans GitHub Actions, chaque étape a une durée visible dans l'interface.
# Objectif : 80 % des pipelines sous 10 minutes.

# Identifier les étapes les plus lentes
gh run list --limit 20 --json name,conclusion,createdAt,updatedAt

# Un test instable se répare ou se supprime, il ne se réessaie pas indéfiniment""",
             "bash", "Deux mesures"),
        box("methode", "Concevoir un pipeline",
            items=["Lister les risques à couvrir, puis les étapes correspondantes.",
                   "Placer les contrôles rapides en premier.",
                   "Construire une seule fois et promouvoir l'artefact.",
                   "Rendre les échecs exploitables : message clair, journal accessible.",
                   "Mesurer la durée et viser moins de dix minutes."]),
    ],
    "keypoints": [
        "Intégration, livraison et déploiement continus sont trois engagements distincts.",
        "Chaque étape doit réduire un risque identifiable.",
        "Les contrôles rapides passent en premier.",
        "On construit une fois et on promeut l'artefact.",
        "L'empreinte d'image garantit l'identité de l'artefact.",
        "Le cache et la parallélisation réduisent la durée.",
        "Un pipeline instable détruit la confiance.",
        "Un test intermittent se répare, il ne se relance pas indéfiniment.",
    ],
    "bridge": "Les principes sont posés. Le chapitre suivant les met en œuvre dans "
              "GitHub Actions et GitLab CI.",
    "exercises": [
        ex("Concevoir un pipeline",
           "Une application Node doit être testée, construite et publiée.",
           ["Ordonnez les étapes.",
            "Estimez les durées.",
            "Précisez les déclencheurs."],
           [("yaml", """stages: [lint, test, build, security, publish]

lint:        # 30 s, chaque commit
test:        # 3 min, chaque demande de fusion
build:       # 2 min, après test
security:    # 1 min, après build
publish:     # 1 min, seulement sur étiquette v*"""),
            "La publication n'a lieu que sur une étiquette : aucune image "
            "intermédiaire n'est publiée.",
            "Les étapes rapides en premier donnent un retour en moins d'une minute."]),
        ex("Réduire la durée d'un pipeline",
           "Le pipeline dure 24 minutes.",
           ["Mesurez chaque étape.",
            "Ajoutez un cache.",
            "Parallélisez les tests."],
           [("yaml", """# Avant : 24 min
# install 6 min (sans cache)
# test    12 min (séquentiel)
# build   4 min
# deploy  2 min

# Après : 9 min
# install 1 min (cache node_modules)
# test    4 min (4 workers)
# build   3 min
# deploy  1 min"""),
            "Le cache des dépendances est le gain le plus simple et le plus sûr.",
            "La parallélisation des tests dépend de leur indépendance : vérifiez qu'ils "
            "ne partagent pas d'état."]),
        ex("Diagnostiquer un test intermittent",
           "Un test échoue une fois sur dix, sans modification de code.",
           ["Reproduisez localement.",
            "Cherchez une dépendance au temps.",
            "Corrigez la cause."],
           [("code", """// Fragile : dépend de l'heure réelle
expect(formaterDate(new Date())).toBe("aujourd'hui");

// Robuste : horloge injectée
const horloge = () => new Date("2026-10-19T12:00:00Z");
expect(formaterRelatif(dateMoinsUnJour, horloge)).toBe("hier");

// Autre cause fréquente : ordre d'exécution et état partagé
beforeEach(() => { base = creerBaseEnMemoire(); });"""),
            "Un test qui dépend de l'horloge échoue autour de minuit ou lors des "
            "changements d'heure.",
            "L'état partagé entre tests produit des échecs dépendant de l'ordre "
            "d'exécution : réinitialisez avant chaque test."],
           level="Qualité"),
    ],
    "quiz": [
        quiz("Que garantit le déploiement continu ?",
             ["Tout est testé", "Chaque changement validé part en production automatiquement",
              "Aucun test", "Une revue manuelle"],
             1,
             "La décision humaine est supprimée, les contrôles automatisés la remplacent."),
        quiz("Pourquoi placer les contrôles rapides en premier ?",
             ["Pour la lisibilité", "Pour obtenir un retour plus tôt",
              "Pour économiser du cache", "Ce n'est pas utile"],
             1,
             "Un échec rapide évite d'attendre des étapes longues inutiles."),
        quiz("Que garantit une promotion par empreinte ?",
             ["Un déploiement plus rapide", "L'identité exacte de l'artefact testé",
              "Un cache plus efficace", "Une image plus petite"],
             1,
             "L'empreinte identifie le contenu, contrairement à une étiquette mobile."),
        quiz("Que faire d'un test intermittent ?",
             ["Le relancer", "Le supprimer", "Le réparer ou l'isoler",
              "Augmenter le délai"],
             2,
             "Un test instable détruit la confiance dans tout le pipeline."),
        quiz("Que fait `concurrency` avec `cancel-in-progress` ?",
             ["Bloque les commits", "Annule les exécutions obsolètes",
              "Réduit la mémoire", "Signe les artefacts"],
             1,
             "Seule la dernière exécution d'une branche est conservée."),
    ],
}
