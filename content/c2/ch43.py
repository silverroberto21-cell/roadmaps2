from bookkit.dsl import (box, code, defn, ex, fig, h, ol, p, quiz, table, ul)

CH = {
    "title": "Résilience : sauvegardes et reprise après sinistre",
    "subtitle": "Préparer le jour où une région entière, une base ou une équipe "
                "disparaît.",
    "duration": "3 h 15",
    "level": "Avancé",
    "prereq": "chapitre 79",
    "objectives": [
        "Définir RTO et RPO pour un service.",
        "Choisir une stratégie de sauvegarde vérifiable.",
        "Concevoir une reprise progressive.",
        "Tester un plan sans provoquer l'incident.",
        "Éviter les fausses assurances.",
    ],
    "blocks": [
        h(2, "Deux nombres à décider"),
        p("Le RTO est la durée d'indisponibilité acceptable ; le RPO est la quantité de "
          "données qu'on accepte de perdre. Ces deux valeurs se décident avec le métier, "
          "pas avec l'équipe technique seule."),
        table(["Notion", "Question posée", "Exemple"],
              [["RTO", "Combien de temps sans service ?", "2 heures"],
               ["RPO", "Combien de données perdues ?", "15 minutes"],
               ["MTTR", "Temps moyen de rétablissement", "Mesuré"],
               ["MTBF", "Temps moyen entre pannes", "Mesuré"]],
              widths=[3.4, 5.4, 4.6], first_col_bold=True,
              caption="Quatre notions"),
        defn("Reprise après sinistre", "Ensemble des moyens qui permettent de rétablir un "
                                       "service après la perte d'un site, d'une région ou "
                                       "d'un composant majeur."),
        fig("compare", "Deux architectures de reprise",
            ("SAUVEGARDE + RESTAURATION", ["Coût faible", "RTO de plusieurs heures",
                                           "Restauration à tester"],
             "SITE SECONDAIRE ACTIF", ["Coût élevé", "RTO de quelques minutes",
                                       "Bascule à répéter"]),
            height=215),
        code("""# Ce que le métier doit écrire avant tout choix technique
# Service : prise de commande
# RTO : 2 h      (au-delà, la journée commerciale est perdue)
# RPO : 15 min   (au-delà, les commandes doivent être ressaisies)
# Fenêtre de bascule autorisée : dimanche 02:00-05:00
# Décideur de bascule : astreinte + responsable produit""", "text",
             "Un cadrage écrit"),

        h(2, "Sauvegardes"),
        p("Une sauvegarde non testée n'est pas une sauvegarde : c'est une intention. Trois "
          "propriétés comptent : la copie existe, elle est restaurable, et la restauration "
          "a été mesurée."),
        table(["Type", "Protège de", "Ne protège pas de"],
              [["Instantané de volume", "Erreur disque", "Suppression logique"],
               ["Sauvegarde logique (`pg_dump`)", "Erreur de données", "Perte de site"],
               ["Journal en continu (WAL)", "Perte des dernières minutes", "Corruption logique"],
               ["Réplique hors site", "Perte de région", "Suppression propagée"]],
              widths=[5.4, 4.2, 4.4], first_col_bold=True,
              caption="Quatre protections"),
        code("""# Sauvegarde logique quotidienne, conservée hors du cluster
pg_dump --format=custom --no-owner --file=/sauvegardes/app-$(date +%F).dump \\
  "$DATABASE_URL"

# Vérification immédiate : la sauvegarde se restaure-t-elle ?
createdb verif_$(date +%F)
pg_restore --dbname=verif_$(date +%F) --no-owner /sauvegardes/app-$(date +%F).dump
psql -d verif_$(date +%F) -c "SELECT count(*) FROM commandes;"

# Rétention : 7 quotidiennes, 4 hebdomadaires, 12 mensuelles
aws s3 ls s3://sauvegardes/app/ | tail""", "bash", "Une sauvegarde vérifiée"),
        box("attention", "Une réplication n'est pas une sauvegarde",
            "Une suppression exécutée sur la base primaire est répliquée en quelques "
            "millisecondes sur le réplica. Sans copie immuable ou différée, la donnée "
            "disparaît partout en même temps."),
        defn("Copie immuable", "Sauvegarde protégée en écriture pour une durée déterminée "
                               "(verrou de conformité). Elle ne peut être supprimée, même "
                               "par un compte administrateur, avant l'échéance."),
        code("""# Verrou d'objet S3 : protège contre la suppression et le chiffrement malveillant
aws s3api put-object-lock-configuration \\
  --bucket sauvegardes-app \\
  --object-lock-configuration '{
    "ObjectLockEnabled": "Enabled",
    "Rule": {"DefaultRetention": {"Mode": "COMPLIANCE", "Days": 35}}
  }'""", "bash", "Une copie immuable"),

        h(2, "Reprise progressive"),
        p("On ne bascule pas un système entier d'un coup : on rétablit par ordre de "
          "dépendance, en commençant par ce qui ne dépend de rien."),
        fig("stack", "Ordre de rétablissement",
            ["1. Réseau, DNS et certificats",
             "2. Identité et secrets",
             "3. Base de données restaurée",
             "4. Services applicatifs sans état",
             "5. Files et traitements différés",
             "6. Vérifications fonctionnelles et ouverture du trafic"],
            height=265),
        code("""# Plan de bascule résumé (extrait d'un runbook)
## Phase 1 — Isolements (10 min)
1. Mettre le service en maintenance (page statique servie par le CDN)
2. Bloquer les écritures applicatives

## Phase 2 — Données (45 min)
3. Restaurer la dernière sauvegarde vérifiée dans la région secondaire
4. Rejouer les journaux jusqu'à l'instant de bascule
5. Contrôler les compteurs métier (commandes du jour, total encaissé)

## Phase 3 — Services (30 min)
6. Déployer depuis le dépôt Git sur le cluster secondaire
7. Vérifier readiness, migrations, files

## Phase 4 — Trafic (10 min)
8. Basculer le DNS avec un TTL court
9. Surveiller erreurs et latence pendant 30 min
10. Consigner l'heure de bascule et les écarts constatés""", "text",
             "Un runbook de bascule"),
        table(["Étape", "Durée cible", "Point de contrôle"],
              [["Isolement", "10 min", "Aucune écriture"],
               ["Restauration", "45 min", "Compteurs cohérents"],
               ["Déploiement", "30 min", "Pods prêts"],
               ["Bascule DNS", "10 min", "Erreurs < 1 %"]],
              widths=[4.2, 4.2, 5.6], first_col_bold=True,
              caption="Quatre étapes chiffrées"),

        h(2, "Tester sans provoquer l'incident"),
        p("Un plan non testé contient toujours une erreur : un secret oublié, un domaine "
          "non délégué, une version d'image absente du registre secondaire. Les exercices "
          "de reprise révèlent ces trous avant qu'ils ne coûtent cher."),
        code("""# Exercice de restauration, sans impact sur la production
# 1. Créer un environnement isolé
terraform workspace new test-reprise
terraform apply -var="region=eu-west-1"

# 2. Restaurer la sauvegarde de la veille
pg_restore --dbname="$DSN_TEST" /sauvegardes/app-2026-10-18.dump

# 3. Déployer la version courante et vérifier
kubectl --context secondaire rollout status deployment/api

# 4. Mesurer et consigner
echo "RTO mesuré : $(date -d @$(( $(date +%s) - DEBUT )) +%M min)\"""",
             "bash", "Un exercice mesuré"),
        table(["Exercice", "Fréquence", "Ce qu'il révèle"],
              [["Restauration de base", "Mensuelle", "Sauvegarde inutilisable"],
               ["Bascule complète", "Trimestrielle", "Dépendances oubliées"],
               ["Perte d'une zone", "Trimestrielle", "Quorum et réplication"],
               ["Perte d'un opérateur", "Semestrielle", "Documentation insuffisante"]],
              widths=[4.6, 4.0, 5.4], first_col_bold=True,
              caption="Quatre exercices"),
        box("pratique", "Chronométrez toujours",
            "Un exercice sans mesure ne prouve rien. Notez l'heure de départ, chaque étape "
            "et l'heure de retour à la normale. Le RTO réel est la seule valeur utile."),
        box("attention", "Les secrets font partie de la reprise",
            "Une base restaurée sans ses clés de chiffrement est une base illisible. Les "
            "clés, certificats et jetons doivent être récupérables indépendamment du site "
            "principal."),

        h(2, "Ce qui échoue le plus souvent"),
        p("Les causes d'échec de reprise sont rarement techniques : ce sont des hypothèses "
          "non vérifiées sur l'état des dépendances externes."),
        table(["Fausse assurance", "Réalité", "Parade"],
              [["« Les sauvegardes sont automatiques »", "Personne ne les restaure", "Test mensuel"],
               ["« Le DNS bascule vite »", "TTL à 24 h", "TTL court vérifié"],
               ["« La région secondaire est prête »", "Quotas insuffisants", "Exercice réel"],
               ["« L'équipe connaît la procédure »", "Un seul expert", "Rotation et runbook"]],
              widths=[5.2, 4.2, 4.6], first_col_bold=True,
              caption="Quatre fausses assurances"),
        code("""# Contrôles automatisés à programmer
# 1. La dernière sauvegarde date de moins de 24 h
aws s3 ls s3://sauvegardes-app/ | sort | tail -1

# 2. Le quota de la région secondaire couvre la production
aws service-quotas get-service-quota --service-code ec2 \\
  --quota-code L-1216C47A --region eu-west-1

# 3. Le certificat de secours est valide
openssl x509 -enddate -noout -in secours.pem""", "bash", "Trois contrôles"),
        box("methode", "Préparer une reprise",
            items=["Faire écrire RTO et RPO par le métier.",
                   "Sauvegarder, puis restaurer pour vérifier.",
                   "Conserver une copie immuable hors site.",
                   "Rédiger un runbook avec durées et décideurs.",
                   "Chronométrer un exercice au moins chaque trimestre."]),
    ],
    "keypoints": [
        "RTO décrit la durée, RPO la perte de données.",
        "Une sauvegarde non restaurée n'est pas une sauvegarde.",
        "La réplication ne protège pas d'une suppression logique.",
        "Une copie immuable résiste à la suppression et au chiffrement.",
        "La reprise suit l'ordre des dépendances.",
        "Les secrets font partie du plan de reprise.",
        "Un exercice non chronométré ne prouve rien.",
        "Les échecs viennent souvent des dépendances externes.",
    ],
    "bridge": "Le système survit aux pannes. Le chapitre suivant maîtrise ce qu'elles "
              "coûtent.",
    "exercises": [
        ex("Définir RTO et RPO",
           "Un service de réservation doit rester utilisable en haute saison.",
           ["Interrogez le métier.",
            "Chiffrez les deux valeurs.",
            "Déduisez l'architecture."],
           [("text", """RTO : 1 h (au-delà, les clients appellent)
RPO : 5 min (au-delà, des réservations sont perdues)

Conséquence : sauvegarde continue des journaux + réplique chaude
dans une seconde zone + bascule DNS automatisée.
Une simple sauvegarde quotidienne ne suffit pas."""),
            "Un RPO de cinq minutes interdit la sauvegarde nocturne seule.",
            "Le RTO impose une réplique déjà prête, pas une reconstruction à froid."]),
        ex("Vérifier une sauvegarde",
           "Une sauvegarde quotidienne existe depuis un an.",
           ["Restaurez-la ailleurs.",
            "Comparez les compteurs.",
            "Consignez le résultat."],
           [("bash", """latest=$(aws s3 ls s3://sauvegardes-app/ | sort | tail -1 | awk '{print $4}')
aws s3 cp "s3://sauvegardes-app/$latest" /tmp/restauration.dump

createdb verif
pg_restore --dbname=verif --no-owner /tmp/restauration.dump
psql -d verif -c "SELECT count(*), max(creee_le) FROM commandes;"

# Comparer avec la production
psql "$DATABASE_URL" -c "SELECT count(*), max(creee_le) FROM commandes;\""""),
            "Le nombre de lignes et la date du dernier enregistrement donnent une idée "
            "du RPO réel.",
            "Une restauration qui échoue doit être traitée comme un incident."],
           level="Fiabilité"),
        ex("Préparer un exercice",
           "La direction demande une preuve de reprise annuelle.",
           ["Écrivez le scénario.",
            "Fixez les mesures.",
            "Prévoyez le compte rendu."],
           [("markdown", """## Exercice de reprise — 2026-11-14
Scénario : perte de la zone eu-west-3a
Durée maximale : 3 h
Mesures : heure de détection, heure de bascule, heure de retour à la normale
Participants : astreinte, responsable produit, un observateur

Livrables :
- chronologie horodatée
- écarts entre le runbook et la réalité
- trois actions correctives avec propriétaire et date"""),
            "Un observateur extérieur note les faits sans participer : c'est la seule "
            "façon d'obtenir une chronologie fiable.",
            "Les écarts entre runbook et réalité sont le vrai résultat de l'exercice."],
           level="Exploitation"),
    ],
    "quiz": [
        quiz("Que mesure le RPO ?",
             ["La durée d'indisponibilité", "La perte de données acceptable",
              "Le débit", "Le coût"],
             1,
             "C'est la fenêtre de données que l'on accepte de perdre."),
        quiz("Pourquoi une réplication ne suffit-elle pas ?",
             ["Trop lente", "Elle propage les suppressions",
              "Trop chère", "Elle ne fonctionne pas"],
             1,
             "La suppression est répliquée comme le reste."),
        quiz("À quoi sert un verrou d'objet ?",
             ["Accélérer la restauration", "Empêcher la suppression d'une sauvegarde",
              "Chiffrer les données", "Compresser"],
             1,
             "Il rend la copie immuable pendant la durée choisie."),
        quiz("Quel est l'ordre de reprise ?",
             ["Applications puis réseau", "Réseau, identité, données, services",
              "Données puis DNS", "Au hasard"],
             1,
             "Chaque couche dépend de la précédente."),
        quiz("Que prouve un exercice de reprise ?",
             ["Que le plan est parfait", "Le RTO réel et les écarts du plan",
              "Que rien ne peut échouer", "La conformité"],
             1,
             "Il révèle les dépendances oubliées et le temps effectif."),
    ],
}
