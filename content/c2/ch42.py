from bookkit.dsl import (box, code, defn, ex, fig, h, ol, p, quiz, table, ul)

CH = {
    "title": "Tests de charge et performance",
    "subtitle": "Mesurer ce qu'un système supporte avant que les utilisateurs ne le "
                "découvrent à vos frais.",
    "duration": "3 h 00",
    "level": "Avancé",
    "prereq": "chapitre 78",
    "objectives": [
        "Choisir un modèle de charge réaliste.",
        "Écrire un scénario avec k6.",
        "Interpréter latence, débit et saturation.",
        "Identifier le goulot d'étranglement.",
        "Fixer un budget de performance testable.",
    ],
    "blocks": [
        h(2, "Ce qu'on mesure vraiment"),
        p("Un test de charge ne mesure pas « la vitesse du site » : il mesure le "
          "comportement d'un système sous une charge donnée, avec un profil donné. Sans "
          "modèle de charge réaliste, le chiffre obtenu ne veut rien dire."),
        table(["Grandeur", "Définition", "Piège"],
              [["Débit", "Requêtes par seconde", "Confondre avec le nombre d'utilisateurs"],
               ["Latence", "Temps de réponse", "Moyenne qui cache la queue"],
               ["Saturation", "Utilisation d'une ressource", "Invisible avant la rupture"],
               ["Taux d'erreur", "Réponses en échec", "Ignorer les délais dépassés"]],
              widths=[3.6, 5.0, 4.8], first_col_bold=True,
              caption="Quatre grandeurs"),
        defn("Modèle de charge", "Description de la façon dont les utilisateurs arrivent et "
                                 "ce qu'ils font : proportion de lectures et d'écritures, "
                                 "pauses, parcours, pics. Il détermine la validité du test."),
        fig("tree", "Trois profils de charge",
            ("Profil de test", [
                ("Palier", ["Charge constante"]),
                ("Montée", ["Recherche du point de rupture"]),
                ("Pic", ["Résistance à un événement"]),
            ]),
            height=225),
        code("""# Profil de charge : 200 utilisateurs virtuels pendant 10 minutes
# avec une montée progressive sur 2 minutes
k6 run --vus 200 --duration 10m scenario.js

# Recherche du point de rupture : paliers croissants
k6 run --stage 2m:50 --stage 5m:200 --stage 5m:500 --stage 2m:0 rupture.js""",
             "bash", "Deux profils"),

        h(2, "Écrire un scénario"),
        p("Un scénario réalise un parcours, pas une requête isolée. Il vérifie le code de "
          "réponse, respecte des pauses et mesure des étapes nommées."),
        code("""import http from "k6/http";
import { check, sleep, group } from "k6";
import { Trend } from "k6/metrics";

const recherche = new Trend("duree_recherche");

export const options = {
  scenarios: {
    navigation: {
      executor: "ramping-vus",
      startVUs: 10,
      stages: [
        { duration: "2m", target: 100 },
        { duration: "5m", target: 100 },
        { duration: "1m", target: 0 },
      ],
    },
  },
  thresholds: {
    http_req_failed: ["rate<0.01"],          // moins de 1 % d'erreurs
    http_req_duration: ["p(95)<800"],        // 95 % sous 800 ms
    "duree_recherche": ["p(95)<300"],
  },
};

export default function () {
  group("accueil", () => {
    const r = http.get("https://recette.exemple.fr/");
    check(r, { "accueil 200": (res) => res.status === 200 });
  });

  group("recherche", () => {
    const debut = Date.now();
    const r = http.get("https://recette.exemple.fr/api/recherche?q=livre");
    recherche.add(Date.now() - debut);
    check(r, { "recherche 200": (res) => res.status === 200 });
  });

  sleep(Math.random() * 3 + 1);   // pause réaliste entre les actions
}""", "js", "Un scénario vérifié"),
        table(["Élément", "Rôle", "Erreur fréquente"],
              [["`stages`", "Profil de montée", "Pic instantané irréaliste"],
               ["`thresholds`", "Critère d'échec", "Aucun seuil"],
               ["`check`", "Vérification de réponse", "Ignorer les 500"],
               ["`sleep`", "Pause utilisateur", "Test qui sature artificiellement"],
               ["`group`", "Étapes nommées", "Tout dans une seule requête"]],
              widths=[3.8, 4.8, 4.8], first_col_bold=True,
              caption="Cinq éléments"),
        box("attention", "Ne testez pas la production sans prévenir",
            "Un test de charge sur un environnement partagé peut dégrader le service réel, "
            "déclencher des alertes et fausser la facturation. Utilisez un environnement "
            "dédié, avec les mêmes dimensions que la production."),

        h(2, "Lire les résultats"),
        p("La latence moyenne est trompeuse. Ce sont les percentiles et la saturation qui "
          "expliquent le comportement du système à l'approche de la rupture."),
        code("""     checks.........................: 100.00% ✓ 48213  ✗ 0
     http_req_duration..............: avg=210ms  min=18ms  p(90)=420ms
                                      p(95)=610ms  p(99)=1.42s  max=6.1s
     http_req_failed................: 0.07%   ✓ 34   ✗ 48179

   █ accueil

     http_req_duration..............: avg=95ms   p(95)=180ms
   █ recherche

     duree_recherche................: avg=310ms  p(95)=680ms   ✗ seuil 300ms""",
             "text", "Un rapport typique"),
        table(["Observation", "Interprétation", "Action"],
              [["p95 stable, p99 explose", "Quelques requêtes lentes", "Chercher la queue"],
               ["Débit plafonne", "Ressource saturée", "Profilage"],
               ["Erreurs à partir d'un seuil", "File d'attente pleine", "Limiter et protéger"],
               ["Latence croît linéairement", "Marge disponible", "Dimensionner"]],
              widths=[5.0, 4.6, 4.2], first_col_bold=True,
              caption="Quatre observations"),
        defn("Point de rupture", "Charge à partir de laquelle la latence augmente sans "
                                 "limite alors que le débit n'augmente plus. Le système "
                                 "sature et les files s'allongent."),

        h(2, "Trouver le goulot"),
        p("Un test de charge isolé ne dit pas quelle ressource sature. Il faut corréler "
          "les résultats avec la CPU, la mémoire, les connexions et les requêtes lentes "
          "côté base."),
        code("""# Pendant le test, observer la saturation
kubectl top pods -n production
kubectl get hpa -n production

# Requêtes lentes côté PostgreSQL
psql -c "SELECT pid, now() - query_start AS duree, state, left(query, 80)
         FROM pg_stat_activity
         WHERE state <> 'idle' ORDER BY duree DESC LIMIT 10;"

# Connexions actives et limites
psql -c "SELECT count(*) FROM pg_stat_activity;"
psql -c "SHOW max_connections;\"""", "bash", "Trois observations"),
        table(["Goulot", "Symptôme", "Correction"],
              [["CPU du service", "Latence qui suit la charge", "Optimiser ou ajouter des réplicas"],
               ["Pool de connexions", "Attentes avant la base", "Réduire ou regrouper"],
               ["Requête lente", "p99 élevé, CPU base saturé", "Index et plan"],
               ["Bande passante", "Débit plafonné", "Compression, cache"],
               ["Verrou applicatif", "Latence en escalier", "Découpler"]],
              widths=[4.4, 4.8, 4.6], first_col_bold=True,
              caption="Cinq goulots"),
        box("pratique", "Un pool trop grand sature la base",
            "Cent réplicas avec vingt connexions chacun font deux mille connexions : la "
            "base passe son temps à changer de contexte. Un regroupement de connexions "
            "(PgBouncer) ou un pool plus petit donne souvent de meilleurs résultats."),
        code("""# Profilage rapide d'un service Python
python -m cProfile -o sortie.prof serveur.py
python -c "import pstats; pstats.Stats('sortie.prof').sort_stats('cumtime').print_stats(15)"

# Profilage d'un service Node
node --cpu-prof serveur.js
# puis ouvrir le fichier .cpuprofile dans les outils de développement""",
             "bash", "Deux profileurs"),

        h(2, "Budget de performance"),
        p("Un budget transforme une intention en critère vérifiable. Il s'exprime en "
          "latence, en débit et en ressources, et se contrôle dans le pipeline."),
        table(["Indicateur", "Budget", "Vérification"],
              [["p95 page d'accueil", "< 800 ms", "Test de charge nocturne"],
               ["p95 recherche", "< 300 ms", "Seuil k6"],
               ["Débit soutenu", "> 300 req/s", "Palier de 30 min"],
               ["Erreurs", "< 0,5 %", "Seuil k6"],
               ["CPU en pointe", "< 70 %", "Tableau de bord"]],
              widths=[4.8, 4.0, 5.0], first_col_bold=True,
              caption="Cinq budgets"),
        code("""# Intégration continue : test court à chaque demande de fusion
k6 run --vus 20 --duration 2m --quiet scenario.js

# Test complet hebdomadaire sur l'environnement de recette
k6 run --out json=resultats.json scenario_complet.js

# Comparaison avec la semaine précédente
jq -r '.metrics.http_req_duration.values["p(95)"]' resultats.json""",
             "bash", "Trois exécutions"),
        box("methode", "Mener un test de charge",
            items=["Définir le parcours et les proportions réalistes.",
                   "Fixer des seuils avant de lancer.",
                   "Envoyer depuis une machine distincte du service.",
                   "Observer la saturation pendant l'exécution.",
                   "Comparer à une référence, pas à une impression."]),
    ],
    "keypoints": [
        "Un test de charge mesure un comportement sous un profil donné.",
        "La moyenne masque la queue de latence.",
        "Les seuils se fixent avant l'exécution.",
        "Le point de rupture sépare la montée en charge de la saturation.",
        "Le goulot se trouve en corrélant test et métriques système.",
        "Un pool de connexions trop grand dégrade la base.",
        "Un budget de performance se vérifie dans le pipeline.",
        "On compare les résultats à une référence stable.",
    ],
    "bridge": "Le système tient la charge. Le chapitre suivant organise la survie aux "
              "pannes réelles.",
    "exercises": [
        ex("Écrire un scénario avec seuils",
           "Le parcours d'accueil puis recherche doit tenir 100 utilisateurs.",
           ["Définissez les étapes.",
            "Ajoutez des pauses.",
            "Fixez deux seuils."],
           [("js", """export const options = {
  stages: [{ duration: "2m", target: 100 }, { duration: "5m", target: 100 }],
  thresholds: {
    http_req_failed: ["rate<0.01"],
    http_req_duration: ["p(95)<800"],
  },
};

export default function () {
  http.get("https://recette.exemple.fr/");
  sleep(1 + Math.random() * 2);
  http.get("https://recette.exemple.fr/api/recherche?q=livre");
  sleep(1 + Math.random() * 2);
}"""),
            "Sans pause, un utilisateur virtuel envoie des dizaines de requêtes par "
            "seconde : la charge n'est plus réaliste.",
            "Deux seuils suffisent : un sur les erreurs, un sur la latence."]),
        ex("Interpréter un point de rupture",
           "À 400 utilisateurs, le débit stagne et la latence triple.",
           ["Identifiez la ressource saturée.",
            "Vérifiez la file.",
            "Proposez une correction."],
           [("text", """Observations à 400 VU :
- débit : 250 req/s (identique à 300 VU)
- latence p95 : 2,4 s (contre 0,6 s à 300 VU)
- CPU du service : 62 %
- connexions PostgreSQL : 198 / 200
- attente moyenne avant connexion : 900 ms

Diagnostic : saturation du pool de connexions.
Correction : PgBouncer + pool de 40 connexions par réplica."""),
            "Un CPU à 62 % exclut la saturation processeur : le goulot est ailleurs.",
            "Le nombre de connexions proche du maximum et l'attente avant connexion "
            "désignent la base."],
           level="Diagnostic"),
        ex("Définir un budget",
           "L'équipe doit pouvoir refuser une livraison trop lente.",
           ["Choisissez trois indicateurs.",
            "Fixez des valeurs.",
            "Précisez la vérification."],
           [("text", """| Indicateur | Budget | Vérification |
| Latence p95 accueil | < 800 ms | test de charge en CI |
| Latence p95 recherche | < 300 ms | seuil k6 |
| Taux d'erreur | < 0,5 % | seuil k6 |

Une livraison qui dépasse un budget est bloquée jusqu'à correction
ou dérogation écrite du responsable produit."""),
            "Un budget sans mécanisme de refus n'est qu'une intention.",
            "Trois indicateurs bien choisis valent mieux que quinze mesures ignorées."],
           level="Architecture"),
    ],
    "quiz": [
        quiz("Pourquoi la moyenne de latence est-elle trompeuse ?",
             ["Elle est fausse", "Elle masque la queue de distribution",
              "Elle est trop lente", "Elle dépend du réseau"],
             1,
             "Le p95 et le p99 décrivent l'expérience réelle."),
        quiz("Quand fixer les seuils ?",
             ["Après le test", "Avant le test", "Jamais", "Selon la machine"],
             1,
             "Sinon le seuil s'adapte au résultat, ce qui annule le contrôle."),
        quiz("Que révèle un débit qui plafonne alors que la charge augmente ?",
             ["Une erreur de test", "Une saturation", "Un cache efficace",
              "Un réseau rapide"],
             1,
             "Le système n'absorbe plus la charge : les files s'allongent."),
        quiz("Quel effet d'un pool de connexions trop grand ?",
             ["Plus de débit garanti", "Saturation de la base",
              "Moins de mémoire", "Aucun"],
             1,
             "Le coût de changement de contexte dépasse le gain."),
        quiz("Où lancer un test de charge ?",
             ["En production sans prévenir", "Sur un environnement dédié",
              "Depuis le serveur testé", "Sur son poste uniquement"],
             1,
             "Il faut des dimensions comparables sans impacter le service réel."),
    ],
}
