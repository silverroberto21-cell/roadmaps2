from bookkit.dsl import (box, code, defn, ex, fig, h, ol, p, quiz, table, ul)

CH = {
    "title": "Stockage, état et persistance",
    "subtitle": "Conserver des préférences entre deux visites et organiser les données "
                "d'une interface sans les disperser.",
    "duration": "2 h 45",
    "level": "Intermédiaire",
    "prereq": "chapitre 30",
    "objectives": [
        "Choisir entre `localStorage`, `sessionStorage`, IndexedDB et cookies.",
        "Sérialiser et versionner des données persistées.",
        "Organiser l'état d'une interface en un lieu unique.",
        "Synchroniser plusieurs onglets.",
        "Respecter la vie privée et les limites de stockage.",
    ],
    "blocks": [
        h(2, "Quatre mécanismes, quatre usages"),
        p("Le navigateur offre plusieurs espaces de stockage. Aucun n'est universel : "
          "chacun a une durée, une capacité et des règles d'accès différentes."),
        table(["Mécanisme", "Capacité", "Durée", "Accès"],
              [["`localStorage`", "5 à 10 Mo", "Jusqu'à suppression", "Synchrone, JS"],
               ["`sessionStorage`", "5 à 10 Mo", "Onglet ouvert", "Synchrone, JS"],
               ["IndexedDB", "Centaines de Mo", "Jusqu'à suppression", "Asynchrone, JS"],
               ["Cookie", "4 Ko", "Selon `Expires`", "Envoyé au serveur"],
               ["Cache API", "Variable", "Jusqu'à suppression", "Service worker"]],
              widths=[3.2, 3.0, 3.4, 3.6], first_col_bold=True,
              caption="Cinq mécanismes de stockage"),
        code("""// localStorage : préférences durables
localStorage.setItem("theme", "sombre");
const theme = localStorage.getItem("theme");     // "sombre" ou null
localStorage.removeItem("theme");
localStorage.clear();                            // tout effacer

// sessionStorage : état d'un parcours
sessionStorage.setItem("etape", "2");

// Cookie : transmis automatiquement au serveur
document.cookie = "langue=fr; path=/; max-age=31536000; SameSite=Lax";""",
             "js", "Trois API, trois portées"),
        defn("Quota", "Limite d'espace allouée à une origine. Elle dépend du navigateur "
                      "et de l'espace disque. Un dépassement lève une exception "
                      "`QuotaExceededError`."),

        h(2, "Sérialiser avec précaution"),
        p("`localStorage` ne stocke que des chaînes. Il faut donc sérialiser les "
          "objets, et surtout prévoir le cas d'une donnée absente, corrompue ou "
          "incompatible avec la version actuelle du code."),
        code("""function lire(cle, defaut) {
  try {
    const brut = localStorage.getItem(cle);
    if (brut === null) return defaut;
    const enveloppe = JSON.parse(brut);
    if (enveloppe.version !== VERSION) {
      localStorage.removeItem(cle);      // migration impossible
      return defaut;
    }
    return enveloppe.valeur;
  } catch {
    return defaut;                        // JSON corrompu
  }
}

function ecrire(cle, valeur) {
  try {
    localStorage.setItem(cle, JSON.stringify({ version: VERSION, valeur }));
  } catch (e) {
    if (e.name === "QuotaExceededError") console.warn("Stockage plein");
  }
}""", "js", "Une lecture qui ne casse jamais l'interface"),
        box("attention", "Ne faites jamais confiance au stockage",
            "L'utilisateur peut modifier `localStorage` depuis la console. Une valeur "
            "relue doit être validée comme n'importe quelle donnée externe : type, "
            "longueur, plage autorisée."),
        code("""// Validation d'une préférence relue
const THEMES = new Set(["clair", "sombre", "auto"]);
function appliquerTheme(valeur) {
  const theme = THEMES.has(valeur) ? valeur : "auto";
  document.documentElement.dataset.theme = theme;
}""", "js", "Une liste blanche plutôt qu'une confiance"),

        h(2, "Un état unique et prévisible"),
        p("Quand plusieurs zones de l'interface dépendent de la même donnée, la "
          "dupliquer dans le DOM produit des incohérences. Un objet d'état unique, "
          "modifié par des fonctions, puis rendu, évite ces dérives."),
        fig("flow", "Un cycle d'état simple",
            ["État : objet en mémoire",
             "Action : l'utilisateur agit",
             "Réduction : l'état est remplacé",
             "Rendu : l'interface est mise à jour",
             "Persistance : l'état est sauvegardé"],
            height=245),
        code("""const etat = {
  filtres: { theme: "tous", recherche: "" },
  articles: [],
  chargement: false,
};

function definirFiltre(cle, valeur) {
  etat.filtres[cle] = valeur;
  rendre();
  persister();
}

function rendre() {
  const visibles = etat.articles.filter(a =>
    etat.filtres.theme === "tous" || a.theme === etat.filtres.theme
  );
  liste.replaceChildren(...visibles.map(carteArticle));
}""", "js", "Un état, un rendu"),
        table(["Type d'état", "Où", "Exemple"],
              [["Préférence durable", "`localStorage`", "Thème, langue"],
               ["État de session", "`sessionStorage`", "Étape d'un tunnel"],
               ["Données volumineuses", "IndexedDB", "Brouillons hors ligne"],
               ["État éphémère", "Mémoire", "Menu ouvert, recherche"],
               ["État d'URL", "Adresse", "Filtres partageables"]],
              widths=[3.6, 3.6, 4.6], first_col_bold=True,
              caption="Cinq natures d'état et leur emplacement"),
        box("pratique", "L'URL est un état",
            "Placer les filtres dans la chaîne de requête rend une vue partageable et "
            "compatible avec le bouton Retour. C'est souvent le meilleur choix pour "
            "une liste filtrée."),

        h(2, "Synchroniser les onglets"),
        p("L'événement `storage` se déclenche dans les autres onglets de la même "
          "origine lorsqu'une valeur change. C'est le moyen le plus simple de garder "
          "les sessions cohérentes."),
        code("""window.addEventListener("storage", (evenement) => {
  if (evenement.key === "theme") {
    appliquerTheme(evenement.newValue);
  }
  if (evenement.key === "deconnexion") {
    window.location.reload();
  }
});

// Se déclenche dans les autres onglets, jamais dans celui qui écrit""", "js",
             "Un thème synchronisé partout"),
        p("Pour des données plus complexes, `BroadcastChannel` transmet des messages "
          "structurés entre onglets, sans passer par le stockage."),
        code("""const canal = new BroadcastChannel("panier");
canal.postMessage({ type: "ajout", articleId: 42 });

canal.addEventListener("message", (e) => {
  if (e.data.type === "ajout") mettreAJourPanier(e.data.articleId);
});""", "js", "Un canal direct entre onglets"),

        h(2, "IndexedDB en pratique"),
        p("IndexedDB stocke des objets structurés, y compris des fichiers. Son API est "
          "asynchrone et verbeuse ; on l'utilise via une petite enveloppe ou une "
          "bibliothèque."),
        code("""function ouvrirBase() {
  return new Promise((resoudre, rejeter) => {
    const requete = indexedDB.open("mon-site", 2);
    requete.onupgradeneeded = () => {
      const base = requete.result;
      if (!base.objectStoreNames.contains("brouillons")) {
        base.createObjectStore("brouillons", { keyPath: "id" });
      }
    };
    requete.onsuccess = () => resoudre(requete.result);
    requete.onerror = () => rejeter(requete.error);
  });
}

async function sauver(brouillon) {
  const base = await ouvrirBase();
  const tx = base.transaction("brouillons", "readwrite");
  tx.objectStore("brouillons").put(brouillon);
  return new Promise((ok, ko) => {
    tx.oncomplete = ok;
    tx.onerror = () => ko(tx.error);
  });
}""", "js", "Une base minimale, versionnée"),
        p("La version de la base déclenche `onupgradeneeded` : c'est là que se "
          "définissent les migrations. Une base qui change de structure sans migration "
          "perd ses données ou provoque une erreur."),

        h(2, "Vie privée et consentement"),
        p("Un stockage local n'est pas neutre : il permet de reconnaître un visiteur. "
          "En Europe, les traceurs non essentiels exigent un consentement préalable."),
        table(["Usage", "Consentement", "Justification"],
              [["Thème choisi", "Non", "Préférence fonctionnelle"],
               ["Panier d'achat", "Non", "Nécessaire au service"],
               ["Mesure d'audience anonyme", "Selon le régime", "Souvent exemptée"],
               ["Publicité ciblée", "Oui", "Traceur"],
               ["Profil comportemental", "Oui", "Traceur"]],
              widths=[4.0, 3.2, 4.6], first_col_bold=True,
              caption="Cinq usages et leur régime de consentement"),
        box("methode", "Trois règles de persistance",
            items=["Stocker le moins possible, le moins longtemps possible.",
                   "Valider toute valeur relue, comme une entrée utilisateur.",
                   "Prévoir la suppression : un bouton « effacer mes données »."]),
    ],
    "keypoints": [
        "`localStorage` est synchrone, limité et ne stocke que des chaînes.",
        "`sessionStorage` disparaît à la fermeture de l'onglet.",
        "IndexedDB gère de gros volumes d'objets structurés.",
        "Un cookie est renvoyé au serveur à chaque requête.",
        "Les données relues doivent être validées et versionnées.",
        "L'URL est un bon emplacement pour un état partageable.",
        "L'événement `storage` synchronise les onglets.",
    ],
    "bridge": "Le cours a couvert le langage et l'interaction. La dernière partie "
              "traite de la qualité : déboguer, mesurer et publier.",
    "exercises": [
        ex("Persister un thème",
           "Le thème choisi doit survivre au rechargement et se synchroniser entre "
           "onglets.",
           ["Lisez la préférence au démarrage.",
            "Écrivez-la au changement.",
            "Écoutez l'événement `storage`."],
           [("code", """const CLE = "theme";
const VALEURS = ["clair", "sombre", "auto"];

function appliquer(valeur) {
  const theme = VALEURS.includes(valeur) ? valeur : "auto";
  document.documentElement.dataset.theme = theme;
  return theme;
}

appliquer(localStorage.getItem(CLE));

selecteur.addEventListener("change", () => {
  localStorage.setItem(CLE, selecteur.value);
  appliquer(selecteur.value);
});

window.addEventListener("storage", e => {
  if (e.key === CLE) {
    selecteur.value = appliquer(e.newValue);
  }
});"""),
            "La liste blanche empêche une valeur corrompue de casser le rendu.",
            "L'écouteur `storage` ne se déclenche pas dans l'onglet qui écrit : pas de "
            "boucle infinie."]),
        ex("Centraliser l'état d'une liste",
           "La recherche, le filtre et la pagination sont dispersés dans le DOM.",
           ["Définissez un objet d'état.",
            "Écrivez une fonction de rendu unique.",
            "Synchronisez l'URL."],
           [("code", """const etat = { recherche: "", theme: "tous", page: 1 };

function rendre() {
  const params = new URLSearchParams(etat);
  history.replaceState(null, "", `?${params}`);
  const visibles = filtrer(articles, etat);
  liste.replaceChildren(...visibles.map(carte));
  compteur.textContent = `${visibles.length} résultat(s)`;
}

champ.addEventListener("input", () => {
  etat.recherche = champ.value;
  etat.page = 1;
  rendre();
});"""),
            "`history.replaceState` met l'URL à jour sans ajouter d'entrée à "
            "l'historique.",
            "Le rendu lit toujours l'état : aucune donnée n'est dupliquée dans des "
            "attributs."]),
        ex("Repérer une fuite de stockage",
           "Le stockage se remplit après quelques jours d'utilisation.",
           ["Listez les clés écrites.",
            "Identifiez celles qui ne sont jamais supprimées.",
            "Ajoutez une purge et une limite."],
           [("code", """function purger(prefixe, joursMax) {
  const limite = Date.now() - joursMax * 86400000;
  for (let i = 0; i < localStorage.length; i += 1) {
    const cle = localStorage.key(i);
    if (!cle.startsWith(prefixe)) continue;
    try {
      const { date } = JSON.parse(localStorage.getItem(cle));
      if (!date || date < limite) localStorage.removeItem(cle);
    } catch {
      localStorage.removeItem(cle);
    }
  }
}"""),
            "Chaque entrée porte une date d'écriture, ce qui permet une purge par "
            "ancienneté.",
            "Les entrées illisibles sont supprimées : elles ne servent plus à rien et "
            "occupent le quota."],
           level="Diagnostic"),
    ],
    "quiz": [
        quiz("Quelle API stocke des objets structurés en grande quantité ?",
             ["`localStorage`", "`sessionStorage`", "IndexedDB", "Cookie"],
             2,
             "IndexedDB accepte des objets et des fichiers, avec une capacité bien "
             "supérieure."),
        quiz("Que stocke `localStorage` ?",
             ["Des objets", "Des chaînes uniquement", "Des fichiers", "Des fonctions"],
             1,
             "Toute valeur est convertie en chaîne : il faut sérialiser les objets."),
        quiz("Quand `sessionStorage` est-il vidé ?",
             ["À chaque rechargement", "À la fermeture de l'onglet",
              "Jamais", "Toutes les heures"],
             1,
             "Les données survivent au rechargement mais pas à la fermeture de l'onglet."),
        quiz("Quel événement signale une modification depuis un autre onglet ?",
             ["`change`", "`storage`", "`input`", "`message`"],
             1,
             "`storage` se déclenche dans les autres onglets de la même origine."),
        quiz("Pourquoi valider une valeur relue du stockage ?",
             ["Pour accélérer", "Parce qu'elle peut être corrompue ou modifiée",
              "Pour économiser l'espace", "Ce n'est pas nécessaire"],
             1,
             "Le stockage local est accessible et modifiable par l'utilisateur."),
    ],
}
