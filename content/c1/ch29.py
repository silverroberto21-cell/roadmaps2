from bookkit.dsl import (box, code, defn, ex, fig, h, ol, p, quiz, table, ul)

CH = {
    "title": "Asynchrone : promesses et `async`/`await`",
    "subtitle": "Écrire du code qui attend sans bloquer, et gérer les erreurs au bon "
                "endroit.",
    "duration": "3 h 00",
    "level": "Intermédiaire",
    "prereq": "chapitre 28",
    "objectives": [
        "Expliquer la boucle d'événements et la pile d'appels.",
        "Créer et consommer des promesses.",
        "Utiliser `async`/`await` sans perdre la gestion d'erreurs.",
        "Lancer des opérations en parallèle.",
        "Éviter les attentes inutiles et les blocages.",
    ],
    "blocks": [
        h(2, "Pourquoi l'asynchrone existe"),
        p("JavaScript s'exécute sur un seul fil. Une opération lente exécutée de façon "
          "synchrone gèle l'interface : impossible de cliquer, de défiler ou même de "
          "voir un indicateur de chargement. L'asynchrone consiste à rendre la main au "
          "navigateur pendant l'attente."),
        defn("Boucle d'événements", "Mécanisme qui exécute le code synchrone, puis vide "
                                    "les files de tâches (promesses, minuteurs, "
                                    "événements) dès que la pile est libre."),
        fig("flow", "Le trajet d'une opération asynchrone",
            ["Appel de `fetch` : la requête part",
             "La fonction rend la main immédiatement",
             "Le navigateur continue d'afficher la page",
             "La réponse arrive : la promesse est résolue",
             "Le callback est placé dans la file de microtâches",
             "La boucle d'événements l'exécute"],
            height=265),
        code("""console.log("1");
setTimeout(() => console.log("3"), 0);
console.log("2");
// Affiche 1, 2, 3 : le minuteur passe après le code synchrone

console.log("A");
Promise.resolve().then(() => console.log("C"));
console.log("B");
// Affiche A, B, C : la microtâche passe avant le minuteur""", "js",
             "L'ordre d'exécution n'est pas l'ordre d'écriture"),

        h(2, "Trois états d'une promesse"),
        p("Une promesse représente une valeur future. Elle est **en attente**, puis "
          "**tenue** (résolue) ou **rejetée**. Une fois settled, son état ne change "
          "plus."),
        code("""const promesse = new Promise((resolve, reject) => {
  const reussite = true;
  if (reussite) resolve("valeur");
  else reject(new Error("échec"));
});

promesse
  .then(valeur => console.log("OK", valeur))
  .catch(erreur => console.error("KO", erreur.message))
  .finally(() => console.log("Terminé, succès ou échec"));""", "js",
             "Le squelette d'une promesse"),
        table(["Méthode", "Rôle", "Retour"],
              [["`then`", "Traite la valeur", "Nouvelle promesse"],
               ["`catch`", "Traite le rejet", "Nouvelle promesse"],
               ["`finally`", "Exécute dans tous les cas", "Promesse d'origine"],
               ["`Promise.all`", "Toutes, ou échec global", "Tableau de valeurs"],
               ["`Promise.allSettled`", "Toutes, succès et échecs", "Tableau de statuts"],
               ["`Promise.race`", "La première, succès ou échec", "Une valeur"],
               ["`Promise.any`", "La première réussie", "Une valeur"]],
              widths=[3.4, 4.6, 3.6], first_col_bold=True,
              caption="Sept méthodes de promesse"),
        code("""// Transformer en chaîne
fetch("/api/utilisateur")
  .then(r => r.json())
  .then(u => fetch(`/api/commandes/${u.id}`))
  .then(r => r.json())
  .then(commandes => afficher(commandes))
  .catch(erreur => afficherErreur(erreur));""", "js",
             "Une chaîne qui devient difficile à lire"),

        h(2, "`async`/`await`"),
        p("`async` transforme une fonction en fonction renvoyant une promesse. "
          "`await` suspend son exécution jusqu'à la résolution, sans bloquer le reste "
          "du programme. Le code se lit de haut en bas."),
        code("""async function chargerCommandes() {
  const reponse = await fetch("/api/utilisateur");
  const utilisateur = await reponse.json();
  const rep = await fetch(`/api/commandes/${utilisateur.id}`);
  return rep.json();
}

chargerCommandes()
  .then(commandes => afficher(commandes))
  .catch(erreur => afficherErreur(erreur));""", "js",
             "La même logique, linéaire"),
        code("""// Gestion d'erreurs explicite, comme du code synchrone
async function chargerCommandes() {
  try {
    const reponse = await fetch("/api/utilisateur");
    if (!reponse.ok) throw new Error(`HTTP ${reponse.status}`);
    const utilisateur = await reponse.json();
    return utilisateur;
  } catch (erreur) {
    console.error("Chargement impossible :", erreur.message);
    throw erreur;          // ne pas avaler l'erreur silencieusement
  }
}""", "js", "Un `try`/`catch` qui ne masque rien"),
        box("attention", "`await` oublié",
            "Oublier `await` renvoie une promesse là où l'on attend une valeur. Le code "
            "continue avec un objet `Promise` et échoue plus loin, avec un message qui "
            "ne désigne pas la vraie cause. En cas de doute, vérifiez le type retourné "
            "dans la console."),
        p("`await` ne peut s'utiliser que dans une fonction `async` ou au niveau "
          "supérieur d'un module (`type=\"module\"`). Il ne bloque pas le navigateur : "
          "il suspend uniquement la fonction en cours."),

        h(2, "Paralléliser ce qui peut l'être"),
        p("Deux requêtes indépendantes exécutées l'une après l'autre prennent la somme "
          "de leurs durées. Lancées ensemble, elles prennent la plus longue."),
        code("""// Séquentiel : 600 ms si chaque appel prend 300 ms
const profil = await chargerProfil();
const notifications = await chargerNotifications();

// Parallèle : environ 300 ms
const [profil2, notifications2] = await Promise.all([
  chargerProfil(),
  chargerNotifications(),
]);""", "js", "Un gain immédiat et gratuit"),
        code("""// Si un échec ne doit pas annuler les autres
const resultats = await Promise.allSettled([
  chargerProfil(),
  chargerNotifications(),
  chargerPreferences(),
]);

for (const r of resultats) {
  if (r.status === "fulfilled") afficher(r.value);
  else console.warn("Échec partiel :", r.reason.message);
}""", "js", "Tolérer les échecs partiels"),
        table(["Besoin", "Outil", "Comportement si un échec survient"],
              [["Tout ou rien", "`Promise.all`", "Rejet immédiat"],
               ["Tout tenter", "`Promise.allSettled`", "Aucun rejet global"],
               ["Le plus rapide", "`Promise.race`", "Le premier résultat, quel qu'il soit"],
               ["Le premier succès", "`Promise.any`", "Rejet seulement si tout échoue"]],
              widths=[3.2, 3.8, 5.0], first_col_bold=True,
              caption="Quatre stratégies de lancement"),

        h(2, "Annulation et délais"),
        p("Une requête peut être annulée avec un `AbortController`. C'est indispensable "
          "quand un utilisateur tape dans un champ de recherche : la réponse de la "
          "frappe précédente ne doit pas écraser la plus récente."),
        code("""const controleur = new AbortController();

fetch("/api/recherche?q=css", { signal: controleur.signal })
  .then(r => r.json())
  .then(console.log)
  .catch(e => {
    if (e.name === "AbortError") return;   // annulation volontaire
    throw e;
  });

// Plus tard, si l'utilisateur retape
controleur.abort();""", "js", "Annuler une requête devenue inutile"),
        code("""function avecDelai(promesse, ms) {
  return Promise.race([
    promesse,
    new Promise((_, rejeter) =>
      setTimeout(() => rejeter(new Error("Délai dépassé")), ms)
    ),
  ]);
}""", "js", "Un délai maximal, sans dépendance"),
        p("Attention : mettre un délai ne libère pas la requête réelle. Combinez-le "
          "avec un `AbortController` pour réellement arrêter le transfert."),

        h(2, "Éviter les pièges"),
        table(["Piège", "Symptôme", "Correction"],
              [["`await` dans une boucle", "Lenteur linéaire", "`Promise.all` sur les appels"],
               ["`async` dans `forEach`", "Aucune attente réelle", "`for...of` ou `map` + `all`"],
               ["`await` oublié", "`Promise` au lieu d'une valeur", "Vérifier les types"],
               ["`catch` vide", "Erreurs invisibles", "Journaliser ou propager"],
               ["Attente inutile", "Interface figée", "Afficher un état, rendre la main"]],
              widths=[3.6, 4.2, 4.2], first_col_bold=True,
              caption="Cinq pièges fréquents"),
        code("""// Ne fonctionne pas : forEach n'attend pas
elements.forEach(async (element) => {
  await traiter(element);
});
console.log("Terminé ?");   // s'affiche avant la fin

// Fonctionne : séquentiel ou parallèle, mais attendu
const resultats = await Promise.all(elements.map(e => traiter(e)));""", "js",
             "Le piège du `forEach` asynchrone"),
        box("methode", "Trois questions avant un appel réseau",
            items=["Que montre l'interface pendant l'attente ?",
                   "Que se passe-t-il si la réponse arrive après le départ de l'utilisateur ?",
                   "Que se passe-t-il si deux réponses arrivent dans le désordre ?"]),
    ],
    "keypoints": [
        "JavaScript est mono-thread : l'asynchrone évite de geler l'interface.",
        "Une promesse est en attente, tenue ou rejetée, et ne change plus ensuite.",
        "`async`/`await` rend le code asynchrone linéaire.",
        "`await` doit être protégé par `try`/`catch` ou propagé.",
        "`Promise.all` parallélise ; `allSettled` tolère les échecs.",
        "`AbortController` annule une requête obsolète.",
        "`forEach` n'attend pas les callbacks asynchrones.",
    ],
    "bridge": "Les principes sont posés. Le chapitre suivant les applique aux API "
              "distantes : requêtes, formats et gestion des erreurs réseau.",
    "exercises": [
        ex("Paralleliser trois chargements",
           "Trois ressources indépendantes sont chargées en séquence.",
           ["Identifiez le temps total actuel.",
            "Parallélisez avec `Promise.all`.",
            "Prévoyez un comportement si l'une échoue."],
           [("code", """async function chargerTableauDeBord() {
  const [profil, stats, messages] = await Promise.all([
    chargerProfil(),
    chargerStatistiques(),
    chargerMessages(),
  ]);
  return { profil, stats, messages };
}

// Variante tolérante aux pannes
async function chargerSouple() {
  const r = await Promise.allSettled([chargerProfil(), chargerStatistiques()]);
  return r.map(x => (x.status === "fulfilled" ? x.value : null));
}"""),
            "Trois appels de 300 ms passent de 900 ms à environ 300 ms.",
            "`allSettled` permet d'afficher ce qui a pu être chargé plutôt que rien du "
            "tout."]),
        ex("Annuler une recherche obsolète",
           "Un champ de recherche lance une requête à chaque frappe.",
           ["Stockez le contrôleur courant.",
            "Annulez la requête précédente.",
            "Ignorez les erreurs d'annulation."],
           [("code", """let controleur = null;

async function rechercher(terme) {
  controleur?.abort();
  controleur = new AbortController();

  try {
    const r = await fetch(`/api/recherche?q=${encodeURIComponent(terme)}`,
      { signal: controleur.signal });
    const resultats = await r.json();
    afficher(resultats);
  } catch (e) {
    if (e.name === "AbortError") return;
    console.error(e);
  }
}

champ.addEventListener("input", e => rechercher(e.target.value));"""),
            "Chaque frappe annule la précédente : seule la dernière réponse est "
            "affichée.",
            "`encodeURIComponent` empêche qu'un terme contenant `&` ou `?` casse l'URL."]),
        ex("Décomposer une chaîne maladroite",
           "Cette fonction enchaîne quatre appels et un `catch` global.",
           ["`fetch(a).then(r=>r.json()).then(x=>fetch(b)).then(r=>r.json()).then(afficher).catch(console.log)`",
            "Ajoutez des messages d'erreur distincts.",
            "Conservez le résultat intermédiaire."],
           [("code", """async function charger() {
  let profil;
  try {
    const r1 = await fetch("/api/profil");
    if (!r1.ok) throw new Error(`Profil indisponible (${r1.status})`);
    profil = await r1.json();
  } catch (e) {
    throw new Error(`Impossible de charger le profil : ${e.message}`);
  }

  try {
    const r2 = await fetch(`/api/commandes/${profil.id}`);
    if (!r2.ok) throw new Error(`Commandes indisponibles (${r2.status})`);
    return await r2.json();
  } catch (e) {
    throw new Error(`Impossible de charger les commandes : ${e.message}`);
  }
}"""),
            "Des messages d'erreur distincts indiquent quelle étape a échoué.",
            "Le `try` englobe la lecture du JSON autant que la requête : les deux "
            "peuvent échouer."],
           level="Refactorisation"),
    ],
    "quiz": [
        quiz("Que renvoie une fonction déclarée `async` ?",
             ["Une valeur", "Une promesse", "Un callback", "`undefined`"],
             1,
             "Une fonction `async` renvoie toujours une promesse, résolue avec la valeur "
             "de retour."),
        quiz("Quelle méthode attend toutes les promesses mais échoue au premier rejet ?",
             ["`Promise.race`", "`Promise.all`", "`Promise.allSettled`", "`Promise.any`"],
             1,
             "`Promise.all` rejette dès qu'une des promesses est rejetée."),
        quiz("Que fait `await` sur le fil principal du navigateur ?",
             ["Il le bloque", "Il suspend seulement la fonction",
              "Il redémarre la page", "Il annule la requête"],
             1,
             "`await` suspend la fonction asynchrone et rend la main à la boucle "
             "d'événements."),
        quiz("Pourquoi `forEach` ne fonctionne-t-il pas avec `async` ?",
             ["Il est déprécié", "Il n'attend pas les callbacks",
              "Il ne renvoie rien", "Il est synchrone"],
             1,
             "`forEach` ignore les promesses renvoyées : utilisez `for...of` ou "
             "`Promise.all` sur un `map`."),
        quiz("À quoi sert `AbortController` ?",
             ["À compresser une requête", "À annuler une requête",
              "À mettre en cache", "À réessayer"],
             1,
             "Il permet d'interrompre un `fetch` via son signal."),
    ],
}
