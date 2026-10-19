from bookkit.dsl import (box, code, defn, ex, fig, h, ol, p, quiz, table, ul)

CH = {
    "title": "Applications web progressives",
    "subtitle": "Donner à un site l'installation, le hors-ligne et la rapidité d'une "
                "application native, sans quitter le Web.",
    "duration": "3 h 15",
    "level": "Avancé",
    "prereq": "chapitres 33 à 36",
    "objectives": [
        "Identifier ce qui distingue une PWA d'un site.",
        "Écrire un manifeste d'application.",
        "Mettre en cache les ressources avec un service worker.",
        "Gérer le hors-ligne et la mise à jour.",
        "Éviter les pièges de cache qui figent une version.",
    ],
    "blocks": [
        h(2, "Trois briques"),
        p("Une application web progressive n'est pas une technologie unique : c'est un "
          "site servi en HTTPS, décrit par un manifeste, et complété par un service worker "
          "qui s'interpose entre le réseau et la page."),
        fig("stack", "Les trois couches d'une PWA",
            ["Page et application (HTML, CSS, JavaScript)",
             "Manifeste : nom, icônes, couleurs, mode d'affichage",
             "Service worker : cache, hors-ligne, arrière-plan",
             "HTTPS obligatoire, y compris en développement local",
             "Installation par le navigateur ou le système",
             "Mise à jour contrôlée par l'application"],
            height=265),
        table(["Brique", "Rôle", "Sans elle"],
              [["HTTPS", "Sécuriser l'origine", "Aucune installation possible"],
               ["Manifeste", "Décrire l'application", "Pas d'icône ni de nom installé"],
               ["Service worker", "Intercepter les requêtes", "Aucun mode hors-ligne"],
               ["Icônes", "Identité visuelle", "Installation refusée"]],
              widths=[4.0, 4.6, 4.8], first_col_bold=True,
              caption="Quatre briques obligatoires"),
        defn("Service worker", "Script exécuté dans un contexte séparé, sans accès au DOM, "
                               "qui intercepte les requêtes réseau de son périmètre et "
                               "peut y répondre depuis un cache."),
        box("attention", "Un service worker survit à la fermeture de l'onglet",
            "Une fois installé, il continue d'intercepter les requêtes lors des visites "
            "suivantes. Un cache mal conçu peut servir une version ancienne pendant des "
            "semaines, y compris après correction du serveur."),

        h(2, "Le manifeste"),
        p("Le manifeste est un fichier JSON lié depuis chaque page. Il décrit le nom, les "
          "icônes, la couleur de thème et le mode d'affichage attendu à l'installation."),
        code("""{
  "name": "Carnet de recettes",
  "short_name": "Carnet",
  "description": "Vos recettes, même sans réseau.",
  "start_url": "/",
  "scope": "/",
  "display": "standalone",
  "background_color": "#FBF3E2",
  "theme_color": "#0F2E4C",
  "lang": "fr",
  "dir": "ltr",
  "icons": [
    { "src": "/icones/192.png", "sizes": "192x192", "type": "image/png" },
    { "src": "/icones/512.png", "sizes": "512x512", "type": "image/png" },
    { "src": "/icones/masque.png", "sizes": "512x512", "type": "image/png",
      "purpose": "maskable" }
  ],
  "shortcuts": [
    { "name": "Nouvelle recette", "url": "/nouvelle" }
  ]
}""", "json", "Un manifeste complet"),
        code("""<!-- Liaison depuis la page -->
<link rel="manifest" href="/manifeste.webmanifest">
<meta name="theme-color" content="#0F2E4C">
<link rel="apple-touch-icon" href="/icones/192.png">""", "html",
             "Trois lignes dans l'en-tête"),
        table(["Champ", "Effet", "Erreur fréquente"],
              [["`name`", "Nom installé", "Absent du manifeste"],
               ["`short_name`", "Nom sous l'icône", "Trop long, tronqué"],
               ["`start_url`", "Page d'ouverture", "Hors du périmètre"],
               ["`scope`", "Portée du service worker", "Trop large"],
               ["`display`", "Barre d'adresse masquée", "`browser` par défaut"],
               ["`purpose: maskable`", "Icône adaptée aux masques", "Bords rognés"]],
              widths=[4.4, 4.6, 4.4], first_col_bold=True,
              caption="Six champs à soigner"),
        box("pratique", "L'icône maskable évite les coins rognés",
            "Les systèmes appliquent un masque de forme variable. Une icône déclarée "
            "`maskable` doit garder son contenu dans un cercle de sécurité couvrant 80 % "
            "de la surface, sinon les bords sont coupés."),

        h(2, "Le cycle de vie du service worker"),
        p("Un service worker passe par installation, activation, puis contrôle des pages. "
          "Tant qu'une ancienne version est active, la nouvelle attend : c'est ce qui "
          "permet de ne pas casser une session en cours."),
        fig("flow", "Le cycle de vie",
            ["Enregistrement par la page",
             "Installation : mise en cache des ressources",
             "Activation : nettoyage des anciens caches",
             "Contrôle des pages ouvertes",
             "Interception des requêtes",
             "Mise à jour : nouvelle version en attente"],
            height=255),
        code("""// enregistrement.js — chargé par la page
if ("serviceWorker" in navigator) {
  window.addEventListener("load", async () => {
    const enregistrement = await navigator.serviceWorker.register("/sw.js", {
      scope: "/",
    });

    enregistrement.addEventListener("updatefound", () => {
      const nouveau = enregistrement.installing;
      nouveau.addEventListener("statechange", () => {
        if (nouveau.state === "installed" && navigator.serviceWorker.controller) {
          afficherBandeauMiseAJour();
        }
      });
    });
  });
}""", "js", "Un enregistrement prudent"),
        code("""// sw.js — installation et activation
const CACHE = "carnet-v3";
const RESSOURCES = ["/", "/styles.css", "/app.js", "/hors-ligne.html"];

self.addEventListener("install", (evenement) => {
  evenement.waitUntil(
    caches.open(CACHE).then((cache) => cache.addAll(RESSOURCES))
  );
});

self.addEventListener("activate", (evenement) => {
  evenement.waitUntil(
    caches.keys().then((noms) =>
      Promise.all(noms.filter((n) => n !== CACHE).map((n) => caches.delete(n)))
    )
  );
});""", "js", "Installation et nettoyage"),
        table(["État", "Signification", "Action possible"],
              [["`installing`", "Installation en cours", "Aucune"],
               ["`installed`", "Prêt mais en attente", "Proposer la mise à jour"],
               ["`activating`", "Nettoyage en cours", "Aucune"],
               ["`activated`", "Contrôle les pages", "Normal"],
               ["`redundant`", "Remplacé ou échoué", "Réenregistrer"]],
              widths=[3.8, 4.8, 5.0], first_col_bold=True,
              caption="Cinq états"),
        box("attention", "Ne sautez pas `skipWaiting` sans réfléchir",
            "`self.skipWaiting()` active immédiatement la nouvelle version. Une page "
            "ouverte peut alors charger des ressources d'une version différente de son "
            "HTML. Demandez confirmation à l'utilisateur avant de basculer."),

        h(2, "Stratégies de cache"),
        p("Chaque type de ressource appelle une stratégie distincte. Appliquer la même "
          "règle partout produit soit des versions figées, soit aucun hors-ligne."),
        table(["Stratégie", "Comportement", "Adaptée à"],
              [["Cache d'abord", "Cache, sinon réseau", "Polices, icônes, styles"],
               ["Réseau d'abord", "Réseau, sinon cache", "Pages éditoriales"],
               ["Réseau seul", "Jamais de cache", "Données personnelles"],
               ["Cache seul", "Cache, erreur sinon", "Ressources de version"],
               ["Périmé pendant revalidation", "Cache immédiat puis mise à jour", "Images"]],
              widths=[5.0, 5.0, 4.0], first_col_bold=True,
              caption="Cinq stratégies"),
        code("""// Interception avec stratégies différenciées
self.addEventListener("fetch", (evenement) => {
  const url = new URL(evenement.request.url);
  if (evenement.request.method !== "GET") return;

  // Données personnelles : jamais de cache
  if (url.pathname.startsWith("/api/")) return;

  // Ressources statiques : cache d'abord
  if (/\\.(css|js|png|svg|woff2)$/.test(url.pathname)) {
    evenement.respondWith(cacheDAbord(evenement.request));
    return;
  }

  // Pages : réseau d'abord, secours hors-ligne
  evenement.respondWith(reseauDAbord(evenement.request));
});

async function cacheDAbord(requete) {
  const cache = await caches.open(CACHE);
  const reponse = await cache.match(requete);
  return reponse ?? fetch(requete);
}

async function reseauDAbord(requete) {
  try {
    const reponse = await fetch(requete);
    const cache = await caches.open(CACHE);
    cache.put(requete, reponse.clone());
    return reponse;
  } catch {
    const cache = await caches.open(CACHE);
    return (await cache.match(requete)) ?? caches.match("/hors-ligne.html");
  }
}""", "js", "Deux stratégies côte à côte"),
        box("attention", "Ne mettez jamais en cache une réponse personnalisée",
            "Une page de compte mise en cache peut être servie à un autre utilisateur sur "
            "un appareil partagé. Les réponses authentifiées ne passent pas par le cache, "
            "ou sont isolées par utilisateur avec une durée très courte."),

        h(2, "Hors-ligne utile"),
        p("Le hors-ligne ne consiste pas à afficher une page d'erreur : il faut prévoir ce "
          "que l'utilisateur peut encore faire, et synchroniser son travail au retour du "
          "réseau."),
        code("""// File d'attente des écritures, rejouées au retour du réseau
const FILE = "file-attente";

async function enregistrerEcriture(requete) {
  const corps = await requete.clone().json();
  const file = await lireFile();
  file.push({ url: requete.url, methode: requete.method, corps, date: Date.now() });
  await ecrireFile(file);
}

self.addEventListener("sync", (evenement) => {
  if (evenement.tag === "synchroniser-ecritures") {
    evenement.waitUntil(rejouerFile());
  }
});

async function rejouerFile() {
  const file = await lireFile();
  const restantes = [];
  for (const item of file) {
    try {
      await fetch(item.url, {
        method: item.methode,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(item.corps),
      });
    } catch {
      restantes.push(item);
    }
  }
  await ecrireFile(restantes);
}""", "js", "Une file d'attente hors-ligne"),
        table(["Fonction", "Disponibilité", "Repli"],
              [["Consulter des fiches", "Partout", "Cache"],
               ["Créer une recette", "Hors-ligne", "File d'attente"],
               ["Rechercher", "En ligne", "Message explicite"],
               ["Synchroniser", "Au retour du réseau", "Rejeu automatique"]],
              widths=[4.6, 4.6, 4.8], first_col_bold=True,
              caption="Quatre fonctions et leurs replis"),
        defn("Synchronisation en arrière-plan", "API permettant de rejouer une requête "
                                                "différée lorsque le réseau revient, même "
                                                "si la page est fermée. Le support varie "
                                                "selon les navigateurs."),

        h(2, "Diagnostiquer"),
        p("Les problèmes de PWA viennent presque toujours du cache. Les outils de "
          "développement permettent de voir la version active, de la désinstaller et de "
          "simuler le hors-ligne."),
        table(["Symptôme", "Cause probable", "Vérification"],
              [["Version ancienne servie", "Cache non invalidé", "Application → Cache storage"],
               ["Aucune installation proposée", "Manifeste ou icônes", "Onglet Manifest"],
               ["Hors-ligne indisponible", "Ressources non mises en cache", "Onglet Network"],
               ["Mise à jour invisible", "Nouveau worker en attente", "skipWaiting"],
               ["Erreur au chargement", "Chemin absolu incorrect", "Scope du worker"]],
              widths=[4.6, 4.8, 4.4], first_col_bold=True,
              caption="Cinq symptômes"),
        code("""# Vérifier ce qui est réellement servi
curl -sI https://exemple.fr/ | grep -i "cache-control\\|etag"

# Versionner le cache à chaque livraison
# Le nom du cache change : les anciens sont supprimés à l'activation
const CACHE = `carnet-${VERSION}`;""", "bash", "Deux réflexes"),
        box("methode", "Checklist PWA",
            items=["HTTPS partout, y compris la préproduction.",
                   "Manifeste valide, icônes 192 et 512, une maskable.",
                   "Cache nommé par version, anciens supprimés.",
                   "Réseau d'abord pour les pages, cache d'abord pour les statiques.",
                   "Jamais de cache sur les réponses authentifiées.",
                   "Bandeau de mise à jour testé."]),
    ],
    "keypoints": [
        "Une PWA combine HTTPS, manifeste et service worker.",
        "Le service worker vit après la fermeture de l'onglet.",
        "Le cycle installé → en attente → actif évite de casser une session.",
        "Chaque type de ressource appelle sa propre stratégie de cache.",
        "Les réponses personnalisées ne se mettent pas en cache.",
        "Le hors-ligne utile prévoit une file d'attente des écritures.",
        "Une version de cache se nomme et se nettoie.",
        "Les outils du navigateur montrent le worker actif et les caches.",
    ],
    "bridge": "L'application fonctionne hors-ligne. Le chapitre suivant explore le dessin "
              "vectoriel et les graphiques dans la page.",
    "exercises": [
        ex("Écrire un manifeste",
           "L'application doit être installable sur mobile.",
           ["Déclarez nom et icônes.",
            "Choisissez le mode d'affichage.",
            "Ajoutez un raccourci."],
           [("json", """{
  "name": "Carnet de recettes",
  "short_name": "Carnet",
  "start_url": "/",
  "scope": "/",
  "display": "standalone",
  "background_color": "#FBF3E2",
  "theme_color": "#0F2E4C",
  "icons": [
    { "src": "/icones/192.png", "sizes": "192x192", "type": "image/png" },
    { "src": "/icones/512.png", "sizes": "512x512", "type": "image/png" },
    { "src": "/icones/masque.png", "sizes": "512x512", "type": "image/png",
      "purpose": "maskable" }
  ]
}"""),
            "`start_url` doit être dans le périmètre du service worker pour que "
            "l'installation soit proposée.",
            "L'icône maskable évite que le système rogne les coins de votre logo."]),
        ex("Mettre en place le hors-ligne",
           "Les fiches consultées doivent rester lisibles sans réseau.",
           ["Mettez en cache les ressources.",
            "Servez depuis le cache en cas d'échec.",
            "Affichez un message clair."],
           [("js", """self.addEventListener("fetch", (e) => {
  if (e.request.mode !== "navigate") return;
  e.respondWith((async () => {
    try {
      const r = await fetch(e.request);
      const c = await caches.open(CACHE);
      c.put(e.request, r.clone());
      return r;
    } catch {
      const c = await caches.open(CACHE);
      return (await c.match(e.request)) ?? c.match("/hors-ligne.html");
    }
  })());
});"""),
            "Ne traiter que `mode === \"navigate\"` évite d'interférer avec les appels "
            "d'API.",
            "La page de secours doit elle-même être mise en cache à l'installation."]),
        ex("Diagnostiquer un cache figé",
           "Les utilisateurs voient une version vieille de trois semaines.",
           ["Vérifiez le nom du cache.",
            "Inspectez le cycle de vie.",
            "Corrigez la stratégie."],
           [("js", """// Cause : cache constant + stratégie « cache d'abord » sur le HTML
const CACHE = "carnet";           // jamais changé

// Correction 1 : nommer le cache par version
const CACHE = `carnet-${VERSION}`;

// Correction 2 : réseau d'abord pour les navigations
// Correction 3 : activation qui supprime les anciens caches
self.addEventListener("activate", (e) => {
  e.waitUntil(caches.keys().then((noms) =>
    Promise.all(noms.filter((n) => n !== CACHE).map((n) => caches.delete(n)))));
});"""),
            "Un cache au nom fixe ne se distingue jamais de la version précédente.",
            "Le HTML doit être réseau d'abord : sinon une correction de contenu ne peut "
            "jamais atteindre les utilisateurs."],
           level="Diagnostic"),
    ],
    "quiz": [
        quiz("Quelle condition est indispensable à une PWA ?",
             ["Un framework", "HTTPS", "Un compte utilisateur", "Un serveur Node"],
             1,
             "Sans HTTPS, ni service worker ni installation."),
        quiz("Que fait `skipWaiting` ?",
             ["Active immédiatement le nouveau worker", "Supprime le cache",
              "Ferme les onglets", "Installe le manifeste"],
             1,
             "Il faut l'utiliser en connaissance de cause, après accord de l'utilisateur."),
        quiz("Quelle stratégie pour des polices ?",
             ["Réseau d'abord", "Cache d'abord", "Réseau seul", "Aucune"],
             1,
             "Les polices changent rarement et doivent charger vite."),
        quiz("Pourquoi ne pas cacher `/api/` ?",
             ["Trop volumineux", "Réponses personnalisées", "Trop lent", "Non compressé"],
             1,
             "Une réponse authentifiée mise en cache peut fuiter vers un autre profil."),
        quiz("Que se passe-t-il si le manifeste manque d'icônes 192 et 512 ?",
             ["Rien", "L'installation peut être refusée", "Le site ne charge plus",
              "Le cache est vidé"],
             1,
             "Les icônes font partie des critères d'installabilité."),
    ],
}
