from bookkit.dsl import (box, code, defn, ex, fig, h, ol, p, quiz, table, ul)

CH = {
    "title": "Consommer une API web",
    "subtitle": "Lire et envoyer des données : format JSON, codes HTTP, erreurs réseau "
                "et bonnes pratiques d'intégration.",
    "duration": "3 h 00",
    "level": "Intermédiaire",
    "prereq": "chapitre 29",
    "objectives": [
        "Lire une documentation d'API et construire une requête correcte.",
        "Distinguer erreur réseau, erreur HTTP et erreur de données.",
        "Envoyer des données en JSON et en formulaire.",
        "Gérer l'authentification et ne jamais exposer de secret.",
        "Mettre en cache et limiter les appels.",
    ],
    "blocks": [
        h(2, "Anatomie d'une requête"),
        p("Une requête HTTP se compose d'une méthode, d'une URL, d'en-têtes et parfois "
          "d'un corps. Chaque partie a un rôle précis et une API mal documentée se "
          "comprend en observant ces éléments."),
        code("""POST /api/articles HTTP/1.1
Host: exemple.fr
Content-Type: application/json
Accept: application/json
Authorization: Bearer eyJhbGciOi...

{"titre": "CSS Grid", "publie": true}""", "http",
             "Une requête complète, ligne par ligne"),
        table(["Méthode", "Rôle", "Corps", "Idempotente"],
              [["`GET`", "Lire", "Non", "Oui"],
               ["`POST`", "Créer", "Oui", "Non"],
               ["`PUT`", "Remplacer", "Oui", "Oui"],
               ["`PATCH`", "Modifier partiellement", "Oui", "Selon l'implémentation"],
               ["`DELETE`", "Supprimer", "Parfois", "Oui"]],
              widths=[2.8, 4.4, 2.8, 3.4], first_col_bold=True,
              caption="Cinq méthodes et leurs conventions"),
        defn("Idempotente", "Se dit d'une opération dont la répétition produit le même "
                            "effet que l'exécution unique. Rejouer un `GET` est sans "
                            "danger ; rejouer un `POST` peut créer un doublon."),

        h(2, "Lire et interpréter les codes"),
        p("Le code de statut est le premier signal. Un `2xx` indique un succès, un "
          "`4xx` une erreur de la requête, un `5xx` une erreur du serveur."),
        table(["Code", "Signification", "Réaction attendue"],
              [["200", "Succès", "Lire le corps"],
               ["201", "Créé", "Lire l'en-tête `Location`"],
               ["204", "Succès sans contenu", "Ne pas lire le corps"],
               ["301 / 308", "Déplacé", "`fetch` suit automatiquement"],
               ["400", "Requête invalide", "Corriger l'envoi"],
               ["401", "Non authentifié", "Redemander une connexion"],
               ["403", "Interdit", "Ne pas réessayer"],
               ["404", "Introuvable", "Afficher un état vide"],
               ["409", "Conflit", "Fusionner ou prévenir"],
               ["422", "Validation échouée", "Afficher les erreurs par champ"],
               ["429", "Trop de requêtes", "Attendre, respecter `Retry-After`"],
               ["500 / 503", "Erreur serveur", "Réessayer avec prudence"]],
              widths=[2.8, 4.4, 4.6], first_col_bold=True,
              caption="Douze codes et la réaction attendue"),
        code("""async function appeler(url, options = {}) {
  const reponse = await fetch(url, options);

  if (reponse.status === 204) return null;

  const type = reponse.headers.get("content-type") || "";
  const estJson = type.includes("application/json");
  const corps = estJson ? await reponse.json() : await reponse.text();

  if (!reponse.ok) {
    const erreur = new Error(corps?.message || `HTTP ${reponse.status}`);
    erreur.status = reponse.status;
    erreur.corps = corps;
    throw erreur;
  }

  return corps;
}""", "js", "Une fonction d'appel qui distingue les cas"),
        box("attention", "`fetch` ne rejette pas sur un code 404",
            "Une promesse `fetch` est rejetée uniquement en cas d'erreur réseau. Un "
            "404 ou un 500 produit une réponse valide avec `ok` à `false`. Vérifier "
            "`reponse.ok` est donc obligatoire."),

        h(2, "Envoyer des données"),
        p("JSON est le format par défaut des API modernes. Le corps doit être "
          "sérialisé, et l'en-tête `Content-Type` doit correspondre, faute de quoi le "
          "serveur interprète mal la requête."),
        code("""const article = { titre: "Grid", contenu: "…", tags: ["css"] };

const reponse = await fetch("/api/articles", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    Accept: "application/json",
  },
  body: JSON.stringify(article),
});""", "js", "Un envoi JSON minimal"),
        code("""// Envoi de formulaire, y compris fichier
const donnees = new FormData(formulaire);
const r = await fetch("/api/upload", { method: "POST", body: donnees });
// Ne pas définir Content-Type : le navigateur ajoute la frontière multipart""",
             "js", "Un envoi multipart correct"),
        p("Ajouter manuellement `Content-Type: multipart/form-data` casse l'envoi : la "
          "frontière qui sépare les parties manque. Laissez le navigateur générer "
          "l'en-tête."),

        h(2, "Authentification et secrets"),
        p("Un site front-end ne peut pas garder un secret. Toute clé présente dans le "
          "code JavaScript est publique : elle est lisible dans l'onglet Réseau ou "
          "dans les sources."),
        fig("compare", "Deux façons d'appeler une API",
            ("DEPUIS LE NAVIGATEUR", ["Jeton temporaire", "Portée limitée",
                                      "Appel direct à l'API publique"],
             "DEPUIS UN SERVEUR", ["Clé secrète", "Portée étendue",
                                   "Le navigateur ne voit rien"]),
            height=200),
        table(["Mécanisme", "Où", "Durée", "Risque"],
              [["Cookie `HttpOnly`", "En-tête automatique", "Session", "Faible (CSRF à traiter)"],
               ["Jeton en mémoire", "Variable JS", "Onglet", "Faible (XSS)"],
               ["`localStorage`", "Stockage persistant", "Longue", "Élevé (XSS)"],
               ["Clé d'API", "Code JS", "Permanente", "Critique : ne jamais faire"]],
              widths=[3.6, 4.0, 2.8, 3.6], first_col_bold=True,
              caption="Quatre mécanismes et leur exposition"),
        box("retenir", "La règle du secret",
            "Si une valeur ne doit pas être connue de l'utilisateur, elle ne doit pas "
            "transiter par le navigateur. Un proxy côté serveur masque la clé et "
            "applique les contrôles d'accès."),

        h(2, "Erreurs réseau et résilience"),
        p("Trois familles d'échecs coexistent : la requête n'a pas abouti (réseau), "
          "elle a abouti avec un code d'erreur (HTTP), ou la réponse est inexploitable "
          "(format). Chacune mérite un message distinct."),
        code("""async function charger(url, essais = 3) {
  for (let i = 0; i < essais; i += 1) {
    try {
      const r = await fetch(url);
      if (r.status === 429) {
        const attente = Number(r.headers.get("Retry-After") || 2);
        await new Promise(r => setTimeout(r, attente * 1000));
        continue;
      }
      if (r.status >= 500) throw new Error("Serveur indisponible");
      if (!r.ok) throw new Error(`Erreur ${r.status}`);
      return await r.json();
    } catch (e) {
      if (i === essais - 1) throw e;
      await new Promise(r => setTimeout(r, 2 ** i * 500));
    }
  }
}""", "js", "Trois tentatives avec attente croissante"),
        p("La stratégie d'attente exponentielle évite d'aggraver une panne en envoyant "
          "des dizaines de requêtes simultanées. Ajoutez une variation aléatoire pour "
          "éviter que tous les clients réessaient au même instant."),

        h(2, "Cache et limitation"),
        p("Deux moyens simples réduisent la charge : le cache HTTP et un cache mémoire "
          "court côté client."),
        code("""// Cache HTTP : géré par le navigateur
fetch("/api/catalogue", { cache: "no-cache" });   // revalide
fetch("/api/logo.svg", { cache: "force-cache" }); // réutilise

// Cache mémoire applicatif
const cache = new Map();
async function catalogue() {
  if (cache.has("catalogue")) return cache.get("catalogue");
  const donnees = await charger("/api/catalogue");
  cache.set("catalogue", donnees);
  return donnees;
}""", "js", "Deux niveaux de cache"),
        table(["En-tête", "Effet", "Usage"],
              [["`Cache-Control: max-age=3600`", "Valide 1 heure", "Ressources stables"],
               ["`ETag`", "Revalidation par empreinte", "Contenus changeants"],
               ["`Last-Modified`", "Revalidation par date", "Secours"],
               ["`no-store`", "Jamais stocké", "Données sensibles"]],
              widths=[4.4, 4.0, 4.2], first_col_bold=True,
              caption="Quatre en-têtes de cache"),
        box("methode", "Intégrer une API en cinq étapes",
            items=["Lire la documentation et repérer l'authentification.",
                   "Tester chaque point d'entrée dans un client HTTP.",
                   "Écrire une fonction d'appel centrale.",
                   "Traiter les trois familles d'erreurs.",
                   "Mettre en cache ce qui change peu."]),
    ],
    "keypoints": [
        "Une requête se compose d'une méthode, d'une URL, d'en-têtes et d'un corps.",
        "`fetch` ne rejette que sur une erreur réseau.",
        "Un code 4xx se corrige côté client, un 5xx se réessaie avec prudence.",
        "`Content-Type` doit correspondre au corps envoyé.",
        "Aucun secret ne peut être stocké dans du code front-end.",
        "Les erreurs réseau, HTTP et de format se distinguent.",
        "Cache HTTP et cache mémoire réduisent la charge.",
    ],
    "bridge": "Les données circulent. Il reste à les conserver entre deux visites : le "
              "chapitre suivant traite du stockage et de l'état.",
    "exercises": [
        ex("Écrire un client d'API robuste",
           "Créez une fonction `api(chemin, options)` qui gère tout le cycle.",
           ["Vérifie `reponse.ok`.",
            "Distingue absence de contenu et JSON.",
            "Lève une erreur typée."],
           [("code", """class ErreurApi extends Error {
  constructor(message, statut, corps) {
    super(message);
    this.name = "ErreurApi";
    this.statut = statut;
    this.corps = corps;
  }
}

async function api(chemin, { methode = "GET", corps, ...reste } = {}) {
  const options = { method: methode, ...reste, headers: { Accept: "application/json" } };
  if (corps !== undefined) {
    options.headers["Content-Type"] = "application/json";
    options.body = JSON.stringify(corps);
  }

  let reponse;
  try {
    reponse = await fetch(chemin, options);
  } catch (e) {
    throw new ErreurApi("Réseau indisponible", 0, null);
  }
  if (reponse.status === 204) return null;
  const donnees = await reponse.json().catch(() => null);
  if (!reponse.ok) {
    throw new ErreurApi(donnees?.message ?? `HTTP ${reponse.status}`, reponse.status, donnees);
  }
  return donnees;
}"""),
            "Un statut 0 distingue clairement l'échec réseau de toute réponse HTTP.",
            "Le `.catch(() => null)` protège contre un corps vide ou non JSON sur une "
            "réponse d'erreur."]),
        ex("Afficher un état vide plutôt qu'une erreur",
           "Une recherche sans résultat renvoie un tableau vide.",
           ["Distinguez 404, tableau vide et erreur.",
            "Rédigez trois messages différents.",
            "Prévoyez une action dans chaque cas."],
           [("code", """function rendreEtat(resultats, erreur) {
  if (erreur) return { titre: "Service indisponible",
                       action: "Réessayer", classe: "etat--erreur" };
  if (!resultats.length) return { titre: "Aucun résultat",
                                  action: "Modifier la recherche", classe: "etat--vide" };
  return null;
}"""),
            "Un tableau vide n'est pas une erreur : l'utilisateur doit pouvoir agir.",
            "Un service indisponible propose de réessayer ; un résultat vide propose de "
            "changer la requête."]),
        ex("Protéger une clé d'API",
           "Le code contient `const CLE = \"sk_live_...\"` et appelle l'API directement.",
           ["Expliquez le risque.",
            "Proposez une architecture.",
            "Montrez l'échange avec un proxy."],
           [("code", """// Navigateur → votre serveur → API tierce
// Le navigateur n'envoie jamais la clé
const r = await fetch("/api/traduire", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ texte, langue: "en" }),
});

// Côté serveur (pseudo-code)
// const r = await fetch("https://api.tiers/v1/traduire", {
//   headers: { Authorization: `Bearer ${process.env.CLE_API}` },
// });"""),
            "La clé reste dans une variable d'environnement du serveur, jamais dans le "
            "paquet JavaScript.",
            "Le proxy applique aussi la limitation de débit et la validation, ce qui "
            "protège le compte de l'abus."],
           level="Sécurité"),
    ],
    "quiz": [
        quiz("`fetch` rejette-t-il la promesse sur un 404 ?",
             ["Oui", "Non, il faut vérifier `reponse.ok`", "Seulement en mode strict", "Uniquement pour une API"],
             1,
             "Seules les erreurs réseau provoquent un rejet ; un 404 est une réponse "
             "valide avec `ok: false`."),
        quiz("Que signifie le code 422 ?",
             ["Non authentifié", "Validation échouée", "Trop de requêtes", "Introuvable"],
             1,
             "La requête est bien formée mais les données sont invalides."),
        quiz("Quel en-tête indique le format du corps envoyé ?",
             ["`Accept`", "`Content-Type`", "`Authorization`", "`Cache-Control`"],
             1,
             "`Accept` décrit ce qu'on souhaite recevoir ; `Content-Type` décrit ce "
             "qu'on envoie."),
        quiz("Où stocker une clé d'API secrète dans une application front-end ?",
             ["Dans une variable JS", "Dans `localStorage`", "Nulle part : côté serveur",
              "Dans un commentaire"],
             2,
             "Tout code livré au navigateur est public : la clé doit rester sur un "
             "serveur."),
        quiz("Que faire face à un code 429 ?",
             ["Réessayer immédiatement", "Attendre en respectant `Retry-After`",
              "Changer de méthode", "Ignorer"],
             1,
             "Le serveur indique le délai à respecter avant un nouvel essai."),
    ],
}
