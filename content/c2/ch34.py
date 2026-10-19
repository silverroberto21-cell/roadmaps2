from bookkit.dsl import (box, code, defn, ex, fig, h, ol, p, quiz, table, ul)

CH = {
    "title": "GitHub Actions et GitLab CI en pratique",
    "subtitle": "Écrire des pipelines lisibles, réutilisables et sûrs dans les deux "
                "forges les plus répandues.",
    "duration": "3 h 30",
    "level": "Intermédiaire",
    "prereq": "chapitre 73",
    "objectives": [
        "Structurer un workflow GitHub Actions.",
        "Écrire un pipeline GitLab CI avec ses étapes.",
        "Partager des modèles entre projets.",
        "Protéger les secrets et les déclencheurs.",
        "Transposer un pipeline d'une forge à l'autre.",
    ],
    "blocks": [
        h(2, "Anatomie d'un workflow"),
        p("GitHub Actions décrit un workflow dans un fichier YAML, composé de tâches "
          "(jobs) exécutées sur des machines (runners). Chaque tâche enchaîne des étapes "
          "(steps), qui appellent des actions réutilisables ou des commandes."),
        code("""name: CI

on:
  pull_request:
  push:
    branches: [main]

permissions:
  contents: read

jobs:
  build:
    runs-on: ubuntu-24.04
    timeout-minutes: 15

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: 22
          cache: npm

      - run: npm ci
      - run: npm run lint
      - run: npm test -- --reporter=verbose
      - run: npm run build

      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: rapport
          path: rapports/
          retention-days: 7""", "yaml", "Un workflow complet"),
        table(["Élément", "Rôle", "Remarque"],
              [["`on`", "Déclencheurs", "Événements et filtres"],
               ["`permissions`", "Droits du jeton", "Principe du moindre privilège"],
               ["`runs-on`", "Type de runner", "Version explicite"],
               ["`steps`", "Étapes séquentielles", "Une étape = une responsabilité"],
               ["`needs`", "Dépendances entre tâches", "Ordonnancement"],
               ["`if`", "Condition", "Évite les étapes inutiles"],
               ["`concurrency`", "File d'exécution", "Annule les obsolètes"]],
              widths=[3.6, 4.8, 4.6], first_col_bold=True,
              caption="Sept éléments"),
        box("attention", "Épinglez les actions par version",
            "`@v4` désigne une étiquette mobile ; `@main` désigne une branche. Pour un "
            "environnement critique, épinglez par empreinte de commit : une action "
            "compromise ne peut alors pas modifier votre pipeline."),
        code("""# Épinglage fort
- uses: actions/checkout@b4ffde65f46336ab88eb53be808477a3936bae11 # v4.1.1""",
             "yaml", "Une empreinte de commit"),

        h(2, "Tâches parallèles et matrice"),
        p("Une matrice exécute la même tâche pour plusieurs combinaisons de paramètres. "
          "C'est le moyen le plus court de tester plusieurs versions d'un langage."),
        code("""jobs:
  test:
    strategy:
      fail-fast: false
      matrix:
        node: [20, 22]
        os: [ubuntu-24.04]
        include:
          - node: 22
            os: windows-2025
    runs-on: ${{ matrix.os }}
    continue-on-error: ${{ matrix.node == 20 }}
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node }}
      - run: npm ci
      - run: npm test""", "yaml", "Une matrice"),
        table(["Option", "Effet", "Usage"],
              [["`fail-fast: false`", "Toutes les combinaisons vont au bout", "Diagnostic"],
               ["`continue-on-error`", "Échec non bloquant", "Version expérimentale"],
               ["`include`", "Ajoute une combinaison", "Cas particuliers"],
               ["`exclude`", "Retire une combinaison", "Version incompatible"],
               ["`max-parallel`", "Limite la concurrence", "Quota de runners"]],
              widths=[4.6, 4.8, 3.6], first_col_bold=True,
              caption="Cinq réglages de matrice"),

        h(2, "Cache et artefacts"),
        p("Le cache accélère ; l'artefact transporte. Les deux sont souvent confondus, "
          "alors qu'ils n'ont ni la même durée de vie ni la même garantie."),
        table(["Aspect", "Cache", "Artefact"],
              [["But", "Réutiliser des dépendances", "Transmettre un résultat"],
               ["Durée de vie", "Quelques jours", "Définie explicitement"],
               ["Garantie", "Peut être absent", "Doit être présent"],
               ["Partage", "Par clé", "Par nom et exécution"],
               ["Échec si absent", "Reconstruction lente", "Tâche bloquée"]],
              widths=[3.8, 4.4, 4.4], first_col_bold=True,
              caption="Cinq différences"),
        code("""# Clé de cache qui change avec le fichier de verrouillage
- uses: actions/cache@v4
  with:
    path: ~/.npm
    key: npm-${{ runner.os }}-${{ hashFiles('package-lock.json') }}
    restore-keys: |
      npm-${{ runner.os }}-

# Récupérer un artefact dans une autre tâche
- uses: actions/download-artifact@v4
  with:
    name: paquet
    path: dist/""", "yaml", "Deux usages distincts"),

        h(2, "GitLab CI"),
        p("GitLab CI décrit des étapes dans `.gitlab-ci.yml`. Les tâches sont des jobs, "
          "regroupés en stages exécutés dans l'ordre. Les runners sont fournis par "
          "l'instance ou par l'organisation."),
        code("""stages: [lint, test, build, deploy]

variables:
  NODE_VERSION: "22"
  npm_config_cache: "$CI_PROJECT_DIR/.npm"

default:
  image: node:22-alpine
  cache:
    key:
      files: [package-lock.json]
    paths: [.npm/]
  before_script:
    - npm ci --prefer-offline

lint:
  stage: lint
  script:
    - npm run lint

test:
  stage: test
  script:
    - npm test -- --coverage
  coverage: '/All files[^|]*\\|\\s+([\\d.]+)/'
  artifacts:
    when: always
    reports:
      junit: rapports/junit.xml
      coverage_report:
        coverage_format: cobertura
        path: rapports/coverage.xml""", "yaml", "Un pipeline GitLab",
             ),
        table(["Concept", "GitHub Actions", "GitLab CI"],
              [["Unité", "Workflow", "Pipeline"],
               ["Tâche", "Job", "Job"],
               ["Étape interne", "Step", "`script`"],
               ["Ordonnancement", "`needs`", "`stages`"],
               ["Modèle réutilisable", "Reusable workflow", "`include`"],
               ["Runner", "`runs-on`", "`tags`"],
               ["Secret", "`secrets`", "Variables protégées"]],
              widths=[3.8, 4.4, 4.4], first_col_bold=True,
              caption="Sept équivalences"),
        box("pratique", "Le pipeline doit être lisible sans documentation",
            "Un lecteur qui découvre le dépôt doit comprendre en une minute ce qui est "
            "vérifié, dans quel ordre, et ce qui part en production. Les noms de tâches "
            "et les commentaires servent à cela, pas la syntaxe exotique."),

        h(2, "Réutiliser"),
        p("La duplication de pipelines produit des divergences silencieuses. Les deux "
          "forges offrent des mécanismes de composition, à utiliser avant de copier un "
          "fichier."),
        code("""# .github/workflows/ci.yml
jobs:
  appel:
    uses: ./.github/workflows/tests.yml
    with:
      node: 22
    secrets: inherit

# .github/workflows/tests.yml
on:
  workflow_call:
    inputs:
      node:
        type: number
        required: true

jobs:
  test:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ inputs.node }}
      - run: npm ci && npm test""", "yaml", "Un workflow réutilisable"),
        code("""# .gitlab-ci.yml — composition par include
include:
  - local: .gitlab/ci/tests.yml
  - template: Security/SAST.gitlab-ci.yml

# .gitlab/ci/tests.yml
.test-template: &test
  stage: test
  script:
    - npm test

test:node22:
  <<: *test
  image: node:22-alpine""", "yaml", "Une composition GitLab"),
        table(["Besoin", "Solution GitHub", "Solution GitLab"],
              [["Logique commune", "Workflow réutilisable", "`include` local"],
               ["Petites étapes", "Action composite", "`before_script`"],
               ["Configuration d'équipe", "Repository rules", "CI/CD components"],
               ["Modèle officiel", "Marketplace", "Templates"]],
              widths=[4.4, 4.4, 4.4], first_col_bold=True,
              caption="Quatre besoins de réutilisation"),

        h(2, "Sécurité du pipeline"),
        p("Un pipeline exécute du code arbitraire avec des secrets. Chaque déclencheur "
          "supplémentaire est une surface d'attaque supplémentaire."),
        table(["Risque", "Scénario", "Protection"],
              [["Fuite de secret", "Script d'une demande de fusion", "Secrets indisponibles sur `pull_request`"],
               ["Action compromise", "Étiquette mobile détournée", "Épinglage par empreinte"],
               ["Jeton trop large", "`contents: write` par défaut", "`permissions` minimales"],
               ["Injection de commande", "Titre de branche dans un `run`", "Variables d'environnement"],
               ["Runner partagé", "Persistance entre exécutions", "Runner éphémère"]],
              widths=[4.2, 5.2, 4.4], first_col_bold=True,
              caption="Cinq risques"),
        code("""# Ne jamais interpoler une entrée utilisateur dans un script
# Dangereux :
- run: echo "Branche ${{ github.head_ref }}"

# Sûr :
- run: echo "Branche $BRANCHE"
  env:
    BRANCHE: ${{ github.head_ref }}

# Et vérifier la valeur si elle influence le comportement
- run: |
    case "$BRANCHE" in
      main|develop|feature/*) echo "ok" ;;
      *) echo "nom de branche refusé" >&2; exit 1 ;;
    esac""", "yaml", "Une injection évitée"),
        box("attention", "Les secrets ne sont pas visibles des contributions externes",
            "Sur une demande de fusion venant d'un dépôt forké, les secrets ne sont pas "
            "transmis. C'est voulu. Ne cherchez pas à contourner cette règle avec "
            "`pull_request_target` et un script exécutable issu de la contribution."),
        box("methode", "Checklist de pipeline",
            items=["`permissions: contents: read` par défaut.",
                   "Actions épinglées par version ou empreinte.",
                   "Aucune entrée utilisateur interpolée dans un `run`.",
                   "Secrets disponibles uniquement sur les branches protégées.",
                   "Durée maximale définie par tâche."]),
    ],
    "keypoints": [
        "Un workflow GitHub est un ensemble de tâches exécutées par des runners.",
        "`permissions` limite les droits du jeton d'exécution.",
        "Les actions se épinglent par version, ou par empreinte en critique.",
        "La matrice teste plusieurs combinaisons.",
        "Le cache accélère, l'artefact transporte.",
        "GitLab CI ordonne les jobs par étapes.",
        "Les workflows réutilisables et `include` évitent la duplication.",
        "Les secrets ne sont pas exposés aux contributions externes.",
    ],
    "bridge": "Le pipeline produit un artefact. Le chapitre suivant organise la "
              "publication des versions et la traçabilité.",
    "exercises": [
        ex("Écrire un workflow complet",
           "Un projet Node doit être vérifié et son rapport conservé.",
           ["Déclarez les déclencheurs.",
            "Limitez les permissions.",
            "Publiez le rapport même en cas d'échec."],
           [("yaml", """name: CI
on: [pull_request, push]

permissions:
  contents: read

jobs:
  verifier:
    runs-on: ubuntu-24.04
    timeout-minutes: 15
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 22
          cache: npm
      - run: npm ci
      - run: npm run lint
      - run: npm test -- --reporter=junit --output-file=rapports/junit.xml
      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: rapport-tests
          path: rapports/"""),
            "`if: always()` garantit que le rapport est publié même quand les tests "
            "échouent : c'est précisément là qu'il est utile.",
            "`timeout-minutes` évite qu'une tâche bloquée consomme le quota."]),
        ex("Transposer vers GitLab",
           "Le même contrôle doit tourner dans GitLab CI.",
           ["Déclarez les étapes.",
            "Configurez le cache.",
            "Publiez les rapports."],
           [("yaml", """stages: [lint, test]

default:
  image: node:22-alpine
  cache:
    key:
      files: [package-lock.json]
    paths: [.npm/]
  before_script:
    - npm ci --prefer-offline

lint:
  stage: lint
  script: npm run lint

test:
  stage: test
  script: npm test
  artifacts:
    when: always
    reports:
      junit: rapports/junit.xml"""),
            "Les rapports JUnit s'affichent directement dans l'interface de fusion.",
            "Le cache est partagé entre les jobs grâce à la même clé."]),
        ex("Corriger une injection de commande",
           "Un pipeline construit une image avec le nom de branche.",
           ["Repérez l'interpolation.",
            "Passez par une variable.",
            "Validez le nom."],
           [("yaml", """# Avant
# - run: docker build -t app:${{ github.head_ref }} .

# Après
- run: |
    nom=$(echo "$BRANCHE" | tr '/' '-' | tr -cd 'a-zA-Z0-9._-')
    test -n "$nom" || { echo "nom vide" >&2; exit 1; }
    docker build -t "app:$nom" .
  env:
    BRANCHE: ${{ github.head_ref }}"""),
            "Un nom de branche peut contenir des caractères qui cassent la commande.",
            "Filtrer et valider transforme une entrée hostile en valeur inoffensive."],
           level="Sécurité"),
    ],
    "quiz": [
        quiz("Que limite `permissions` ?",
             ["La durée du pipeline", "Les droits du jeton",
              "Le nombre de runners", "La taille du cache"],
             1,
             "Le jeton GITHUB_TOKEN n'a que les droits déclarés."),
        quiz("Quelle est la différence entre cache et artefact ?",
             ["Aucune", "Le cache peut être absent, l'artefact doit exister",
              "L'artefact est plus rapide", "Le cache est chiffré"],
             1,
             "Un cache manquant ralentit, un artefact manquant bloque."),
        quiz("Comment ordonne-t-on les jobs GitLab ?",
             ["Par `needs`", "Par `stages`", "Par ordre alphabétique", "Au hasard"],
             1,
             "Les jobs du même stage sont parallèles, les stages s'enchaînent."),
        quiz("Pourquoi ne pas interpoler un nom de branche dans `run` ?",
             ["Pour la lisibilité", "À cause du risque d'injection de commande",
              "Pour économiser du cache", "Ce n'est pas un problème"],
             1,
             "Une entrée utilisateur peut contenir des commandes arbitraires."),
        quiz("Comment tester plusieurs versions d'un langage ?",
             ["Avec un cache", "Avec une matrice", "Avec un artefact", "Avec un runner"],
             1,
             "La matrice génère une tâche par combinaison."),
    ],
}
