from bookkit.dsl import (box, code, defn, ex, fig, h, ol, p, quiz, table, ul)

CH = {
    "title": "Versionner, construire et outiller son projet",
    "subtitle": "Git, gestionnaires de paquets et chaîne de construction : les outils "
                "qui transforment des fichiers en application livrable.",
    "duration": "3 h 00",
    "level": "Intermédiaire",
    "prereq": "chapitre 34",
    "objectives": [
        "Utiliser Git au quotidien avec des messages utiles.",
        "Structurer un dépôt et rédiger un `.gitignore`.",
        "Comprendre le rôle de `package.json` et du fichier de verrouillage.",
        "Distinguer développement et production dans une chaîne de construction.",
        "Automatiser les vérifications avant chaque envoi.",
    ],
    "blocks": [
        h(2, "Git : trois zones, quatre commandes"),
        p("Git conserve des instantanés. Trois zones coexistent : le répertoire de "
          "travail, l'index (les modifications préparées) et le dépôt (les commits)."),
        fig("flow", "Le trajet d'une modification",
            ["Répertoire de travail : vous éditez",
             "Index : `git add` prépare",
             "Dépôt local : `git commit` enregistre",
             "Dépôt distant : `git push` publie",
             "Récupération : `git pull` intègre"],
            height=245),
        code("""git status                     # état des trois zones
git add index.html styles.css  # préparer des fichiers précis
git add -p                     # préparer par morceaux
git commit -m "Ajoute la navigation principale"
git push origin main
git log --oneline --graph --decorate -10""", "bash",
             "Le cycle quotidien"),
        table(["Commande", "Rôle", "Quand"],
              [["`git switch -c nom`", "Créer une branche", "Nouvelle fonctionnalité"],
               ["`git switch nom`", "Changer de branche", "Retour au tronc"],
               ["`git merge nom`", "Fusionner", "Intégrer une branche"],
               ["`git rebase -i`", "Réécrire l'historique local", "Nettoyer avant envoi"],
               ["`git stash`", "Mettre de côté", "Changement d'urgence"],
               ["`git restore fichier`", "Annuler une modification", "Erreur locale"],
               ["`git diff`", "Comparer", "Avant de préparer"]],
              widths=[3.6, 5.0, 3.4], first_col_bold=True,
              caption="Sept commandes utiles"),
        defn("Commit", "Instantané immuable identifié par une empreinte. Il contient "
                       "l'état des fichiers, l'auteur, la date et le ou les parents."),
        box("pratique", "Un bon message de commit",
            "La première ligne résume l'action au présent, en moins de 72 caractères. "
            "Le corps explique le pourquoi, pas le comment : le diff montre déjà le "
            "comment."),
        code("""Ajoute la validation accessible du formulaire

Les erreurs sont désormais annoncées dans une zone role="alert"
et chaque champ reçoit aria-invalid. Le focus se déplace sur
le résumé après un échec.

Refs: #42""", "text", "Un message qui explique la décision"),

        h(2, "Structurer un dépôt"),
        p("Un dépôt lisible distingue les sources, les ressources, les tests et les "
          "fichiers générés. Ces derniers ne doivent jamais être versionnés."),
        code("""mon-site/
├── index.html
├── a-propos.html
├── assets/
│   ├── styles/
│   │   ├── base.css
│   │   ├── composants.css
│   │   └── pages.css
│   ├── scripts/
│   └── images/
├── .gitignore
├── .editorconfig
├── package.json
└── README.md""", "text", "Une arborescence lisible"),
        code("""# Dépendances et artefacts
node_modules/
dist/
build/

# Secrets et configuration locale
.env
.env.local

# Système et éditeurs
.DS_Store
Thumbs.db
.vscode/
.idea/

# Journaux
*.log
npm-debug.log*""", "text", "Un `.gitignore` de départ"),
        box("attention", "Un secret versionné est un secret compromis",
            "Même supprimé du fichier, il reste dans l'historique. Si un `.env` a été "
            "envoyé, révoquez la clé immédiatement, puis nettoyez l'historique."),
        code("""# Vérifier qu'un fichier n'est pas suivi
git ls-files | grep env

# Retirer un fichier du suivi sans le supprimer localement
git rm --cached .env""", "bash", "Deux vérifications de sécurité"),

        h(2, "`package.json` et verrouillage"),
        p("`package.json` décrit le projet et ses dépendances. Le fichier de "
          "verrouillage (`package-lock.json`) fige l'arbre exact, ce qui rend les "
          "installations reproductibles."),
        code("""{
  "name": "mon-site",
  "version": "1.0.0",
  "private": true,
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview",
    "test": "vitest run",
    "lint": "eslint ."
  },
  "devDependencies": {
    "vite": "^5.0.0",
    "vitest": "^1.0.0"
  }
}""", "json", "Un manifeste minimal"),
        table(["Champ", "Rôle", "Remarque"],
              [["`name`", "Nom du paquet", "Minuscules, tirets"],
               ["`private`", "Empêche la publication", "Indispensable pour un site"],
               ["`type`", "Système de modules", "`module` pour ESM"],
               ["`scripts`", "Commandes nommées", "Point d'entrée de l'automatisation"],
               ["`dependencies`", "Nécessaires à l'exécution", "Livrées"],
               ["`devDependencies`", "Outils de développement", "Non livrées"]],
              widths=[3.4, 4.6, 4.2], first_col_bold=True,
              caption="Six champs de `package.json`"),
        code("""npm install          # installe et met à jour le verrou
npm ci               # installe exactement le verrou (CI)
npm install -D vite  # dépendance de développement
npm run build        # exécute le script "build\"""", "bash",
             "Quatre commandes, quatre usages"),
        p("`npm ci` supprime `node_modules` et installe la version exacte du verrou. "
          "C'est la commande à utiliser dans une intégration continue, jamais "
          "`npm install`."),

        h(2, "Chaîne de construction"),
        p("Le navigateur ne comprend que HTML, CSS et JavaScript. La chaîne de "
          "construction transforme les sources : assemblage des modules, minification, "
          "optimisation des images, empreinte dans les noms."),
        code("""// vite.config.js
import { defineConfig } from "vite";

export default defineConfig({
  root: "src",
  build: {
    outDir: "../dist",
    emptyOutDir: true,
    sourcemap: true,
    assetsInlineLimit: 4096,
  },
  server: { port: 8080, open: true },
});""", "js", "Une configuration courte"),
        table(["Étape", "Entrée", "Sortie"],
              [["Développement", "Sources", "Serveur avec rechargement"],
               ["Construction", "Sources", "Fichiers optimisés"],
               ["Prévisualisation", "Fichiers construits", "Serveur local de contrôle"],
               ["Déploiement", "Fichiers construits", "Site en ligne"]],
              widths=[3.4, 4.4, 4.4], first_col_bold=True,
              caption="Quatre étapes, quatre rôles"),
        code("""# Ne jamais déployer les sources de développement
dist/
├── index.html
├── assets/
│   ├── index-3f2a91.js      # empreinte : cache long
│   └── index-8b41cd.css""", "text", "Ce que contient un dossier construit"),

        h(2, "Automatiser les vérifications"),
        p("Un crochet Git exécute un contrôle avant chaque commit ou chaque envoi. "
          "C'est le moment le moins coûteux pour attraper une erreur de format ou un "
          "test cassé."),
        code("""# .husky/pre-commit
npm run lint
npm run test -- --run""", "bash", "Deux vérifications avant chaque commit"),
        table(["Outil", "Rôle", "Configuration"],
              [["ESLint", "Erreurs et style", "`eslint.config.js`"],
               ["Prettier", "Formatage", "`.prettierrc`"],
               ["EditorConfig", "Indentation et fins de ligne", "`.editorconfig`"],
               ["Stylelint", "Qualité CSS", "`.stylelintrc`"],
               ["Husky", "Crochets Git", "`.husky/`"]],
              widths=[3.4, 5.4, 3.8], first_col_bold=True,
              caption="Cinq outils d'hygiène"),
        code("""// .editorconfig
root = true

[*]
charset = utf-8
indent_style = space
indent_size = 2
end_of_line = lf
insert_final_newline = true
trim_trailing_whitespace = true""", "text", "Un socle commun à toute l'équipe"),
        box("methode", "Avant chaque envoi",
            items=["`git status` : ai-je préparé les bons fichiers ?",
                   "`git diff --staged` : le contenu est-il conforme ?",
                   "Le message décrit-il le pourquoi ?",
                   "Les tests et le lint passent-ils ?"]),
    ],
    "keypoints": [
        "Git enregistre des instantanés en trois zones.",
        "Un message de commit explique le pourquoi.",
        "Les fichiers générés et les secrets ne se versionnent jamais.",
        "Le fichier de verrouillage garantit une installation reproductible.",
        "`npm ci` installe exactement le verrou.",
        "La construction produit des fichiers optimisés et versionnés par empreinte.",
        "Les crochets Git attrapent les erreurs au bon moment.",
    ],
    "bridge": "Tous les outils sont en place. Le dernier chapitre assemble le tout dans "
              "un projet complet, de la première ligne à la mise en ligne.",
    "exercises": [
        ex("Écrire un historique lisible",
           "Trois modifications sont mélangées dans le répertoire de travail.",
           ["Séparez en trois commits cohérents.",
            "Rédigez un message pour chacun.",
            "Vérifiez avec `git log`."],
           [("bash", """git add index.html
git commit -m "Corrige le titre de la page d'accueil"

git add assets/styles/base.css
git commit -m "Uniformise les espacements verticaux"

git add assets/scripts/menu.js
git commit -m "Rend le menu utilisable au clavier

Le bouton expose aria-expanded et Échap referme le menu."""),
            "Un commit par intention : la relecture et le retour arrière deviennent "
            "possibles.",
            "`git add -p` permet de préparer partiellement un fichier qui contient "
            "plusieurs modifications indépendantes."]),
        ex("Configurer un projet",
           "Créez `package.json`, `.gitignore` et un script de vérification.",
           ["Déclarez les scripts `dev`, `build`, `test`.",
            "Ignorez `node_modules` et `dist`.",
            "Ajoutez un crochet de pré-commit."],
           [("code", """{
  "name": "mon-site",
  "private": true,
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "test": "vitest run",
    "lint": "eslint .",
    "check": "npm run lint && npm run test"
  },
  "devDependencies": { "vite": "^5.0.0", "vitest": "^1.0.0" }
}"""),
            "Un script `check` unique sert à la fois localement et dans "
            "l'intégration continue.",
            "`private: true` empêche une publication accidentelle sur le registre "
            "public."]),
        ex("Préparer un déploiement",
           "Construisez le site et vérifiez le dossier produit.",
           ["Lancez la construction.",
            "Contrôlez les chemins relatifs.",
            "Vérifiez la taille des fichiers."],
           [("code", """npm run build
du -sh dist/*
find dist -name "*.map" -delete   # si les sources ne doivent pas être publiques

# Prévisualisation locale du résultat exact
npm run preview"""),
            "Le dossier `dist` ne doit contenir que ce qui est nécessaire au site : ni "
            "sources, ni cartes de sources si elles exposent du code.",
            "Un chemin absolu codé en dur casse le site s'il est servi depuis un "
            "sous-répertoire."],
           level="Mise en production"),
    ],
    "quiz": [
        quiz("Quelle commande prépare des fichiers pour le prochain commit ?",
             ["`git commit`", "`git add`", "`git push`", "`git status`"],
             1,
             "`git add` place les modifications dans l'index."),
        quiz("Pourquoi ne pas versionner `node_modules` ?",
             ["Il est trop volumineux et reproductible depuis le verrou",
              "Il contient des secrets", "Il est binaire", "Git l'interdit"],
             0,
             "Les dépendances se réinstallent à l'identique depuis le fichier de "
             "verrouillage."),
        quiz("Quelle commande installe exactement les versions du verrou ?",
             ["`npm install`", "`npm ci`", "`npm update`", "`npm audit`"],
             1,
             "`npm ci` respecte strictement le fichier de verrouillage, ce qui rend "
             "l'intégration continue reproductible."),
        quiz("Que produit une chaîne de construction ?",
             ["Les sources", "Des fichiers optimisés prêts à déployer",
              "Le fichier de verrouillage", "Les tests"],
             1,
             "Elle assemble, minifie et nomme les fichiers pour la production."),
        quiz("Quel est l'intérêt d'un crochet de pré-commit ?",
             ["Accélérer Git", "Bloquer un commit qui échoue aux vérifications",
              "Compresser les fichiers", "Signer les commits"],
             1,
             "Il exécute lint et tests avant l'enregistrement, au moment le moins "
             "coûteux."),
    ],
}
