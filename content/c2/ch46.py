from bookkit.dsl import (box, code, defn, ex, fig, h, ol, p, quiz, table, ul)

CH = {
    "title": "Sécurité de la chaîne logicielle",
    "subtitle": "Garantir que ce qui est déployé provient bien du code relu, avec des "
                "dépendances connues.",
    "duration": "3 h 15",
    "level": "Avancé",
    "prereq": "chapitres 74 à 76",
    "objectives": [
        "Cartographier les maillons de la chaîne.",
        "Inventorier les dépendances avec un SBOM.",
        "Vérifier l'origine et l'intégrité d'un artefact.",
        "Appliquer des politiques d'admission.",
        "Réagir à une vulnérabilité publiée.",
    ],
    "blocks": [
        h(2, "La chaîne et ses maillons"),
        p("Entre la ligne de code et le conteneur en production, un artefact traverse le "
          "dépôt, l'intégration continue, un registre et un cluster. Chaque maillon peut "
          "être compromis ou mal configuré."),
        fig("flow", "Les maillons d'une chaîne logicielle",
            ["Code source et revue",
             "Dépendances tierces et verrouillage",
             "Construction reproductible",
             "Signature de l'artefact",
             "Registre et analyse",
             "Admission dans le cluster"],
            height=250),
        table(["Maillon", "Risque", "Contrôle"],
              [["Code", "Contribution malveillante", "Revue obligatoire"],
               ["Dépendances", "Paquet compromis", "Verrou, provenance"],
               ["Construction", "Environnement altéré", "Runner isolé, reproductibilité"],
               ["Registre", "Étiquette modifiée", "Immuabilité, signature"],
               ["Cluster", "Image inconnue", "Politique d'admission"]],
              widths=[4.2, 5.0, 4.8], first_col_bold=True,
              caption="Cinq maillons"),
        defn("SBOM", "Inventaire logiciel des composants d'un artefact : bibliothèques, "
                     "versions, licences et dépendances transitives. Il permet de savoir en "
                     "quelques minutes si une faille publiée vous concerne."),
        box("attention", "Une dépendance est du code exécuté",
            "Ajouter une bibliothèque revient à exécuter le code d'un inconnu avec vos "
            "droits. Le verrouillage des versions et la vérification de la provenance ne "
            "sont pas des formalités."),

        h(2, "Inventorier"),
        p("Le SBOM se génère à la construction, se signe et s'archive avec l'artefact. "
          "Sans archivage, il ne sert qu'au moment où l'on y pense."),
        code("""# SBOM au format CycloneDX, généré à la construction
syft registry.exemple.fr/app:1.4.2 -o cyclonedx-json > app-1.4.2.sbom.json

# Analyse des vulnérabilités à partir du SBOM
grype sbom:app-1.4.2.sbom.json --fail-on high

# Archivage avec l'artefact
cosign attach sbom --sbom app-1.4.2.sbom.json \\
  registry.exemple.fr/app:1.4.2

# Vérification ultérieure
cosign download sbom registry.exemple.fr/app:1.4.2 | jq '.components | length'""",
             "bash", "Quatre commandes"),
        table(["Format", "Usage", "Écosystème"],
              [["CycloneDX", "Sécurité et conformité", "Large"],
               ["SPDX", "Licences et conformité", "Industrie"],
               ["`package-lock.json`", "Dépendances d'un projet Node", "Node"],
               ["`go.sum`", "Empreintes des modules", "Go"]],
              widths=[4.4, 5.4, 4.2], first_col_bold=True,
              caption="Quatre formats"),
        code("""# Vérifier un composant précis dans tous les artefacts
for img in $(crane ls registry.exemple.fr/app); do
  cosign download sbom "registry.exemple.fr/app:$img" 2>/dev/null \\
    | jq -r --arg p "log4j-core" \\
      '.components[] | select(.name==$p) | "\\($img) \\(.version)"'
done""", "bash", "Une recherche ciblée"),

        h(2, "Vérifier l'origine"),
        p("La signature répond à « qui a produit cet artefact ». L'attestation de "
          "provenance répond à « comment il a été produit ». Les deux ensemble permettent "
          "une politique d'admission sérieuse."),
        code("""# Attestation de provenance SLSA niveau 3 (GitHub Actions)
- name: Générer la provenance
  uses: actions/attest-build-provenance@v2
  with:
    subject-name: ghcr.io/org/app
    subject-digest: sha256:${{ steps.build.outputs.digest }}

# Vérification côté déploiement
gh attestation verify oci://ghcr.io/org/app@sha256:abc123 \\
  --repo org/app --signer-workflow org/app/.github/workflows/livraison.yml""",
             "yaml", "Une provenance vérifiable"),
        table(["Niveau", "Signification", "Difficulté"],
              [["Signature", "Artefact produit par une identité", "Faible"],
               ["Provenance", "Décrit le processus de construction", "Moyenne"],
               ["Construction isolée", "Runner éphémère, pas d'accès aux secrets", "Moyenne"],
               ["Reproductibilité", "Même source, même binaire", "Élevée"]],
              widths=[4.4, 6.0, 3.6], first_col_bold=True,
              caption="Quatre niveaux de garantie"),
        box("pratique", "Épinglez par empreinte, pas par étiquette",
            "Une politique d'admission qui vérifie `app:1.4.2` peut être trompée par une "
            "étiquette redéployée. Vérifiez l'empreinte signée, puis déployez cette "
            "empreinte."),

        h(2, "Appliquer une politique"),
        p("Une politique d'admission refuse ce qui ne respecte pas les règles : image non "
          "signée, registre inconnu, conteneur privilégié, absence de limites de "
          "ressources."),
        code("""# Politique Kyverno : images signées uniquement
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: images-signees
spec:
  validationFailureAction: Enforce
  rules:
    - name: verifier-signature
      match:
        any:
          - resources:
              kinds: [Pod]
      verifyImages:
        - imageReferences: ["registry.exemple.fr/*"]
          attestors:
            - entries:
                - keys:
                    publicKeys: |-
                      -----BEGIN PUBLIC KEY-----
                      ...
                      -----END PUBLIC KEY-----""", "yaml", "Une politique stricte"),
        code("""# Test de la politique : une image non signée doit être refusée
kubectl run test --image=registry.exemple.fr/app:non-signee -n production
# Error from server: admission webhook "mutate.kyverno.svc" denied the request

# Une image signée doit passer
kubectl run test --image=registry.exemple.fr/app:1.4.2 -n production
# pod/test created""", "bash", "Une vérification"),
        table(["Règle", "Refuse", "Mode de déploiement"],
              [["Signature obligatoire", "Images non signées", "`Enforce`"],
               ["Registre autorisé", "Images publiques", "`Enforce`"],
               ["Pas de privilège", "`privileged: true`", "`Enforce`"],
               ["Limites obligatoires", "Pods sans requests", "`Audit` puis `Enforce`"]],
              widths=[4.6, 5.0, 4.4], first_col_bold=True,
              caption="Quatre règles"),
        box("attention", "Commencez en mode audit",
            "Une politique en `Enforce` dès le premier jour bloque des déploiements "
            "légitimes et pousse les équipes à contourner. Passez en `Audit`, corrigez, "
            "puis basculez règle par règle."),

        h(2, "Réagir à une vulnérabilité"),
        p("Une faille critique est publiée dans une bibliothèque très répandue. La "
          "question n'est pas « faut-il corriger ? » mais « où est-elle, et depuis quand ? »"),
        ol("**Localiser** : interroger les SBOM archivés, pas les dépôts.",
           "**Qualifier** : la fonction vulnérable est-elle réellement appelée ?",
           "**Corriger** : reconstruire avec une version corrigée, republier, redéployer.",
           "**Vérifier** : analyse après reconstruction, signature et provenance.",
           "**Consigner** : versions concernées, fenêtre d'exposition, décision."),
        code("""# 1. Localiser
grype sbom:app-1.4.2.sbom.json | grep -i "CVE-2026-12345"

# 2. Corriger la dépendance
npm audit fix --package-lock-only
npm ci && npm test

# 3. Republier avec une nouvelle version
docker build -t registry.exemple.fr/app:1.4.3 .
trivy image --exit-code 1 --severity CRITICAL registry.exemple.fr/app:1.4.3

# 4. Consigner la fenêtre d'exposition
# version 1.4.0 → 1.4.2, déployée du 2026-09-02 au 2026-10-19""", "bash",
             "Quatre étapes"),
        table(["Décision", "Condition", "Action"],
              [["Corriger immédiatement", "Fonction vulnérable exposée", "Correctif sous 24 h"],
               ["Planifier", "Dépendance transitive non atteignable", "Prochaine version"],
               ["Accepter", "Composant non chargé à l'exécution", "Documenter et réévaluer"],
               ["Retirer", "Composant inutile", "Supprimer la dépendance"]],
              widths=[4.6, 5.4, 4.0], first_col_bold=True,
              caption="Quatre décisions"),
        box("methode", "Sécuriser la chaîne",
            items=["Verrouiller les dépendances et vérifier leur provenance.",
                   "Générer un SBOM à chaque construction et l'archiver.",
                   "Signer les artefacts et attester la provenance.",
                   "Refuser à l'admission ce qui n'est pas signé.",
                   "Savoir localiser une faille en minutes, pas en jours."]),
    ],
    "keypoints": [
        "La chaîne va du commit à l'admission dans le cluster.",
        "Une dépendance est du code exécuté avec vos droits.",
        "Le SBOM inventorie les composants d'un artefact.",
        "Un SBOM non archivé ne sert à rien lors d'une alerte.",
        "La signature prouve l'origine, la provenance décrit la construction.",
        "Une politique d'admission refuse les artefacts non conformes.",
        "On déploie une empreinte, pas une étiquette.",
        "Une politique s'active d'abord en audit.",
    ],
    "bridge": "La chaîne est sécurisée. Le chapitre suivant met tout en pratique dans un "
              "projet complet.",
    "exercises": [
        ex("Générer et archiver un SBOM",
           "Chaque version publiée doit être inventoriée.",
           ["Générez le SBOM.",
            "Attachez-le à l'image.",
            "Vérifiez sa présence."],
           [("bash", """syft registry.exemple.fr/app:1.4.2 -o cyclonedx-json > app.sbom.json
cosign attach sbom --sbom app.sbom.json registry.exemple.fr/app:1.4.2
cosign download sbom registry.exemple.fr/app:1.4.2 | jq '.components | length'"""),
            "Le SBOM se génère à partir de l'image publiée, pas du dépôt : c'est elle qui "
            "sera exécutée.",
            "L'archivage avec l'artefact garantit qu'il reste disponible pendant toute "
            "la durée de vie de la version."]),
        ex("Écrire une politique d'admission",
           "Seules les images signées du registre interne sont autorisées.",
           ["Ciblez le registre.",
            "Vérifiez la signature.",
            "Activez en audit."],
           [("yaml", """apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata: { name: registre-interne }
spec:
  validationFailureAction: Audit     # puis Enforce
  rules:
    - name: images-du-registre
      match:
        any: [{ resources: { kinds: [Pod] } }]
      validate:
        message: "Seules les images de registry.exemple.fr sont autorisées."
        pattern:
          spec:
            containers:
              - image: "registry.exemple.fr/*\""""),
            "Le mode audit produit des rapports sans bloquer : c'est la phase "
            "d'observation.",
            "La règle porte sur la référence complète, préfixe compris."],
           level="Sécurité"),
        ex("Traiter une alerte de vulnérabilité",
           "Une CVE critique touche une bibliothèque présente dans six images.",
           ["Localisez les images.",
            "Évaluez l'exposition.",
            "Corrigez et consignez."],
           [("markdown", """1. Interrogation des SBOM : 6 images concernées (1.3.x, 1.4.0-1.4.2)
2. Exposition : la fonction vulnérable sert au décodage d'images téléversées
   → chemin atteignable depuis Internet
3. Décision : correction immédiate
4. Reconstruction en 1.4.3, signature, publication
5. Déploiement progressif, vérification des journaux
6. Consignation : fenêtre du 2026-09-02 au 2026-10-19, analyse publiée"""),
            "La question de l'atteignabilité décide de l'urgence réelle.",
            "La fenêtre d'exposition est une information obligatoire pour l'analyse."],
           level="Incident"),
    ],
    "quiz": [
        quiz("Qu'est-ce qu'un SBOM ?",
             ["Un certificat", "Un inventaire de composants", "Une signature",
              "Un registre"],
             1,
             "Il liste les bibliothèques et leurs versions."),
        quiz("Que prouve une attestation de provenance ?",
             ["L'absence de faille", "Comment l'artefact a été construit",
              "La qualité du code", "La conformité RGPD"],
             1,
             "Elle décrit le dépôt, le commit et le pipeline."),
        quiz("Pourquoi déployer une empreinte plutôt qu'une étiquette ?",
             ["C'est plus court", "L'étiquette peut être redéployée",
              "C'est plus rapide", "Pour le cache"],
             1,
             "L'empreinte identifie un contenu immuable."),
        quiz("Par quel mode commencer une politique d'admission ?",
             ["`Enforce`", "`Audit`", "`Disabled`", "`Warn` uniquement"],
             1,
             "L'audit révèle les écarts sans bloquer les livraisons."),
        quiz("Première étape face à une CVE critique ?",
             ["Reconstruire tout", "Localiser les artefacts concernés",
              "Attendre", "Désactiver les alertes"],
             1,
             "Les SBOM permettent de savoir quelles versions sont touchées."),
    ],
}
