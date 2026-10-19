from bookkit.dsl import (box, code, defn, ex, fig, h, ol, p, quiz, table, ul)

CH = {
    "title": "Publications, versions et traçabilité",
    "subtitle": "Nommer, signer et publier un artefact pour savoir exactement ce qui "
                "tourne en production.",
    "duration": "2 h 45",
    "level": "Intermédiaire",
    "prereq": "chapitre 74",
    "objectives": [
        "Appliquer une version sémantique sans ambiguïté.",
        "Publier une image et un paquet avec métadonnées.",
        "Signer et vérifier un artefact.",
        "Écrire des notes de version utiles.",
        "Retrouver la provenance d'un incident.",
    ],
    "blocks": [
        h(2, "Versionner"),
        p("Une version est un contrat. La version sémantique `MAJEUR.MINEUR.CORRECTIF` "
          "annonce la compatibilité : rompre ce contrat casse les dépendants."),
        table(["Partie", "Incrément", "Signification"],
              [["`1.4.2` → `1.5.0`", "Mineur", "Ajout compatible"],
               ["`1.4.2` → `1.4.3`", "Correctif", "Correction compatible"],
               ["`1.4.2` → `2.0.0`", "Majeur", "Rupture de compatibilité"],
               ["`0.x.y`", "Instable", "Aucune garantie"]],
              widths=[4.4, 3.4, 5.4], first_col_bold=True,
              caption="Quatre incréments"),
        defn("Rupture de compatibilité", "Changement qui oblige un dépendant à modifier "
                                         "son code : suppression d'une fonction, "
                                         "changement de type, modification de comportement "
                                         "par défaut."),
        code("""# Étiquettes mobiles et immuables
git tag -a v1.4.2 -m "Version 1.4.2"
git push origin v1.4.2

# Ne jamais déplacer une étiquette publiée
# Une correction = une nouvelle version

# Lister les étiquettes et leur date
git for-each-ref --sort=-creatordate \\
  --format='%(refname:short) %(creatordate:short)' refs/tags | head -5""",
             "bash", "Trois commandes"),
        box("attention", "Une étiquette déplacée fabrique des fantômes",
            "Si `v1.4.2` désigne deux contenus différents selon la date, aucune "
            "investigation ne peut aboutir. Une version publiée est immuable ; toute "
            "correction produit `v1.4.3`."),

        h(2, "Publier"),
        p("Un registre stocke des artefacts nommés et versionnés. La publication doit "
          "être reproductible et traçable : l'artefact porte son commit source et le "
          "pipeline qui l'a produit."),
        code("""# Publier une image avec plusieurs étiquettes
docker build \\
  --label org.opencontainers.image.revision="$(git rev-parse HEAD)" \\
  --label org.opencontainers.image.version="1.4.2" \\
  --label org.opencontainers.image.source="https://github.com/org/app" \\
  -t registry.exemple.fr/app:1.4.2 \\
  -t registry.exemple.fr/app:1.4 \\
  -t registry.exemple.fr/app:latest .

docker push registry.exemple.fr/app:1.4.2
docker push registry.exemple.fr/app:1.4
docker push registry.exemple.fr/app:latest""", "bash", "Trois étiquettes"),
        table(["Étiquette", "Usage", "Risque"],
              [["`1.4.2`", "Déploiement de production", "Aucun"],
               ["`1.4`", "Suivre les correctifs", "Change sans préavis"],
               ["`latest`", "Démonstration", "Impossible à reproduire"],
               ["empreinte", "Audit et promotion", "Aucun"]],
              widths=[4.0, 5.0, 4.4], first_col_bold=True,
              caption="Quatre étiquettes"),
        code("""# Vérifier les métadonnées réellement publiées
docker buildx imagetools inspect registry.exemple.fr/app:1.4.2

# Comparer deux images par leurs couches
docker image inspect app:1.4.2 --format '{{.RootFS.Layers}}'

# Rechercher les vulnérabilités de l'image publiée
trivy image --severity HIGH,CRITICAL registry.exemple.fr/app:1.4.2""",
             "bash", "Trois vérifications"),
        box("pratique", "Ne déployez jamais `latest`",
            "`latest` ne dit rien sur le contenu. En cas d'incident, il est impossible de "
            "savoir ce qui tournait la veille. Déployez une version ou une empreinte."),

        h(2, "Signer et vérifier"),
        p("La signature relie un artefact à une identité. Elle ne prouve pas que le "
          "logiciel est sûr, mais elle prouve qu'il vient bien de celui qui l'a signé et "
          "qu'il n'a pas été modifié."),
        code("""# Signature d'une image avec cosign
cosign generate-key-pair
cosign sign --key cosign.key registry.exemple.fr/app:1.4.2

# Vérification avant déploiement
cosign verify --key cosign.pub registry.exemple.fr/app:1.4.2

# Signature sans clé, liée à l'identité de la CI (OIDC)
cosign sign registry.exemple.fr/app:1.4.2
cosign verify \\
  --certificate-identity-regexp 'https://github.com/org/app/.github/workflows/.*' \\
  --certificate-oidc-issuer https://token.actions.githubusercontent.com \\
  registry.exemple.fr/app:1.4.2""", "bash", "Deux modèles de signature"),
        table(["Élément", "Ce qu'il prouve", "Ce qu'il ne prouve pas"],
              [["Signature", "Origine et intégrité", "Absence de vulnérabilité"],
               ["Attestation de provenance", "Comment l'artefact a été construit", "Qualité du code"],
               ["Analyse de vulnérabilités", "Absence de failles connues", "Absence de failles inconnues"],
               ["Revue de code", "Relecture humaine", "Absence d'erreur"]],
              widths=[4.6, 4.4, 4.4], first_col_bold=True,
              caption="Quatre preuves et leurs limites"),
        defn("Attestation de provenance", "Document signé décrivant la construction : "
                                          "dépôt source, commit, pipeline, dépendances. Il "
                                          "répond à la question « d'où vient ce binaire ? »."),
        code("""# Vérifier la provenance d'une image
gh attestation verify oci://registry.exemple.fr/app:1.4.2 \\
  --repo org/app

# Refuser une image dont la provenance est inconnue
if ! cosign verify --key cosign.pub "$IMAGE" >/dev/null 2>&1; then
  echo "image non signée, déploiement refusé" >&2
  exit 1
fi""", "bash", "Deux contrôles"),

        h(2, "Notes de version"),
        p("Une note de version s'adresse à ceux qui utilisent le logiciel, pas à ceux qui "
          "l'ont écrit. Elle décrit les changements visibles, les migrations nécessaires "
          "et les corrections de sécurité."),
        code("""## 1.4.2 — 2026-10-19

### Correction
- Le cache des sessions n'expire plus prématurément (#4821).

### Sécurité
- Mise à jour de `libxml2` vers 2.12.7 (CVE-2026-12345).

### Migration
Aucune action requise.

---

## 1.5.0 — 2026-11-03

### Ajout
- Export CSV des rapports (#4902).

### Déprécié
- `GET /api/v1/rapports` sera supprimé en 2.0. Utilisez `GET /api/v2/rapports`.

### Migration
Remplacez les appels à `/api/v1/rapports` avant la version 2.0.""",
             "markdown", "Deux notes de version"),
        code("""# Générer la liste des changements depuis la dernière étiquette
git log --oneline v1.4.1..v1.4.2

# Vérifier qu'aucun commit n'est oublié
git log --format='%h %s' v1.4.1..HEAD --no-merges

# Regrouper par type de commit
git log --format='%s' v1.4.1..HEAD | grep -E '^(feat|fix|security)' | sort""",
             "bash", "Trois commandes"),
        box("methode", "Ce qui rend une publication fiable",
            items=["Une version immuable, jamais réutilisée.",
                   "Une provenance signée et vérifiable.",
                   "Un inventaire des composants (SBOM).",
                   "Des notes orientées utilisateur.",
                   "Une politique de conservation des artefacts."]),

        h(2, "Retrouver la provenance"),
        p("Lors d'un incident, la question n'est pas « qui a écrit cette ligne ? » mais "
          "« quel artefact tourne, avec quelles dépendances, et depuis quand ? »"),
        fig("flow", "Remonter d'un incident à une source",
            ["Alerte en production",
             "Empreinte de l'image déployée",
             "Attestation de provenance",
             "Commit source",
             "Demande de fusion et revue",
             "Dépendances et vulnérabilités"],
            height=250),
        code("""# Quel artefact tourne réellement ?
kubectl get deployment app -n production \\
  -o jsonpath='{.spec.template.spec.containers[0].image}'

# Quel commit a produit cet artefact ?
crane config "$IMAGE" | jq -r '.config.Labels["org.opencontainers.image.revision"]'

# Depuis quand cette version est-elle déployée ?
kubectl rollout history deployment/app -n production""", "bash",
             "Trois réponses"),
        table(["Question", "Source", "Remarque"],
              [["Quelle version ?", "Étiquette de l'artefact", "Souvent absente"],
               ["Quel commit ?", "Métadonnée d'image", "À renseigner à la construction"],
               ["Quel pipeline ?", "Attestation", "Signée"],
               ["Quelles dépendances ?", "SBOM", "À générer à chaque publication"],
               ["Depuis quand ?", "Historique de déploiement", "Conservé par l'orchestrateur"]],
              widths=[4.4, 4.6, 4.4], first_col_bold=True,
              caption="Cinq questions d'audit"),
        box("attention", "Un SBOM non conservé ne sert à rien",
            "Générer un inventaire de composants au moment de la construction est inutile "
            "s'il est écrasé à la publication suivante. Archivez-le avec l'artefact, pour "
            "au moins la durée de vie de la version en production."),
    ],
    "keypoints": [
        "Une version publiée est immuable.",
        "La version sémantique annonce la compatibilité.",
        "Un artefact porte son commit source.",
        "Les étiquettes mobiles compliquent les enquêtes.",
        "Signer prouve l'origine, pas l'innocuité.",
        "L'attestation de provenance décrit la construction.",
        "Les notes de version s'adressent aux utilisateurs.",
        "Le SBOM doit être conservé avec l'artefact.",
    ],
    "bridge": "Les artefacts sont publiés et signés. Le chapitre suivant fait converger "
              "l'état du cluster vers le dépôt : GitOps.",
    "exercises": [
        ex("Préparer une publication",
           "Une version 1.4.2 doit être publiée avec traçabilité.",
           ["Étiquetez le commit.",
            "Construisez avec métadonnées.",
            "Publiez avec vérification."],
           [("bash", """git tag -a v1.4.2 -m "Version 1.4.2"
git push origin v1.4.2

docker build \\
  --label org.opencontainers.image.revision="$(git rev-parse HEAD)" \\
  --label org.opencontainers.image.version="1.4.2" \\
  -t registry.exemple.fr/app:1.4.2 .

docker push registry.exemple.fr/app:1.4.2
cosign sign --key cosign.key registry.exemple.fr/app:1.4.2
cosign verify --key cosign.pub registry.exemple.fr/app:1.4.2"""),
            "L'étiquette Git et l'étiquette d'image portent la même version : la "
            "correspondance est vérifiable.",
            "La signature est créée après la publication : elle porte sur l'artefact "
            "publié, pas sur l'image locale."]),
        ex("Écrire une note de version",
           "Une version ajoute un export, déprécie une route et corrige une faille.",
           ["Séparez les sections.",
            "Indiquez la migration.",
            "Citez le numéro de faille."],
           [("markdown", """## 1.5.0 — 2026-11-03

### Ajout
- Export CSV des rapports (#4902).

### Déprécié
- `GET /api/v1/rapports` : suppression prévue en 2.0.

### Sécurité
- Mise à jour de `libxml2` (CVE-2026-12345).

### Migration
Remplacez `/api/v1/rapports` par `/api/v2/rapports` avant la 2.0."""),
            "La section migration est celle que les utilisateurs cherchent en premier.",
            "Un numéro de faille permet à un lecteur de vérifier l'exposition de son "
            "propre système."]),
        ex("Auditer un déploiement",
           "Un incident survient ; il faut identifier l'artefact exact.",
           ["Lisez l'image du déploiement.",
            "Extrayez le commit.",
            "Retrouvez le pipeline."],
           [("bash", """IMAGE=$(kubectl get deployment app -n production \\
  -o jsonpath='{.spec.template.spec.containers[0].image}')
echo "$IMAGE"

crane config "$IMAGE" | jq -r '.config.Labels["org.opencontainers.image.revision"]'

gh attestation verify "oci://$IMAGE" --repo org/app --format json | jq '.verificationResult'"""),
            "L'empreinte est plus fiable que l'étiquette : elle identifie le contenu.",
            "L'attestation relie l'artefact au workflow qui l'a produit."],
           level="Diagnostic"),
    ],
    "quiz": [
        quiz("Quel incrément pour une correction compatible ?",
             ["Majeur", "Mineur", "Correctif", "Aucun"],
             2,
             "Le correctif ne casse pas la compatibilité."),
        quiz("Pourquoi ne pas déployer `latest` ?",
             ["Trop lourd", "Le contenu n'est pas identifiable",
              "Trop lent", "Non signé"],
             1,
             "`latest` peut pointer vers un contenu différent à chaque instant."),
        quiz("Que prouve une signature d'image ?",
             ["L'absence de faille", "L'origine et l'intégrité",
              "La qualité du code", "La conformité RGPD"],
             1,
             "La signature ne dit rien de la sécurité du contenu."),
        quiz("Que contient un SBOM ?",
             ["Les journaux", "L'inventaire des composants",
              "Les secrets", "Les tests"],
             1,
             "Il liste les composants et leurs versions."),
        quiz("Une étiquette publiée peut-elle être déplacée ?",
             ["Oui, toujours", "Oui, en cas d'urgence", "Non", "Seulement sur `main`"],
             2,
             "Déplacer une étiquette rend toute enquête impossible."),
    ],
}
