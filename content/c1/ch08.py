from bookkit.dsl import (box, code, defn, ex, fig, h, ol, p, quiz, table, ul)

CH = {
    "title": "Formulaires HTML",
    "subtitle": "Le point de contact entre l'utilisateur et le système : le lieu où "
                "l'accessibilité et la sécurité se jouent vraiment.",
    "duration": "3 h 00",
    "level": "Débutant",
    "prereq": "chapitre 7",
    "objectives": [
        "Construire un formulaire accessible avec étiquettes et groupes de champs.",
        "Choisir le bon type de champ pour chaque donnée attendue.",
        "Utiliser la validation native sans en faire une barrière.",
        "Soigner les messages d'erreur et les états de chargement.",
        "Comprendre pourquoi la validation serveur reste indispensable.",
    ],
    "blocks": [
        h(2, "Anatomie d'un formulaire"),
        p("Un formulaire est un ensemble de champs dont les valeurs sont envoyées à un "
          "serveur. Sans JavaScript, il fonctionne déjà : c'est le socle sur lequel "
          "on ajoute ensuite du confort. Trois attributs suffisent à le décrire."),
        code("""<form action="/contact" method="post">
  <label for="nom">Nom</label>
  <input id="nom" name="nom" type="text" autocomplete="name" required>
  <button type="submit">Envoyer</button>
</form>""", "html", "Le plus petit formulaire utile"),
        table(["Attribut", "Rôle", "Valeurs"],
              [["`action`", "URL de traitement", "`/contact`, `/api/message`"],
               ["`method`", "Méthode HTTP", "`get` (données dans l'URL) ou `post`"],
               ["`enctype`", "Encodage du corps", "`multipart/form-data` pour les fichiers"],
               ["`novalidate`", "Désactiver la validation native", "Usage rare, contrôlé"],
               ["`autocomplete`", "Aide au remplissage", "`on` ou `off`"]],
              widths=[2.6, 4.0, 4.6], first_col_bold=True,
              caption="Les attributs de l'élément form"),
        p("`GET` place les données dans l'URL : adapté aux recherches et aux filtres, "
          "que l'on peut mettre en favori. `POST` place les données dans le corps : "
          "obligatoire pour toute écriture, toute donnée sensible et tout envoi de "
          "fichier."),

        h(2, "Étiquettes : la règle non négociable"),
        p("Chaque champ doit posséder une étiquette associée. Sans elle, un lecteur "
          "d'écran annonce « champ de saisie » sans indiquer quoi saisir, et le clic "
          "sur le texte ne place pas le curseur dans le champ."),
        code("""<!-- Association explicite : recommandée -->
<label for="email">Adresse électronique</label>
<input id="email" name="email" type="email" autocomplete="email" required>

<!-- Champ enveloppé : correct aussi -->
<label>
  Code postal
  <input name="cp" type="text" inputmode="numeric" autocomplete="postal-code">
</label>""", "html", "Deux façons correctes d'associer une étiquette"),
        p("Le texte de l'étiquette doit être visible. Un `placeholder` n'est pas une "
          "étiquette : il disparaît à la saisie, il est souvent gris et peu contrasté, "
          "et il n'est pas toujours annoncé de manière fiable."),
        box("attention", "Les cinq erreurs d'étiquette",
            items=["Un `placeholder` utilisé à la place d'un `<label>`.",
                   "Une étiquette qui contient le champ mais pointe aussi ailleurs.",
                   "Des étiquettes identiques pour des champs différents (« Nom » deux fois).",
                   "Une étiquette masquée sans texte alternatif accessible.",
                   "Un astérisque seul pour signaler un champ obligatoire."]),

        h(2, "Choisir le bon champ"),
        p("Le type de champ pilote le clavier virtuel sur mobile, la validation "
          "native et l'aide à la saisie. `text` par défaut est presque toujours un "
          "aveu de paresse."),
        table(["Type", "Donnée attendue", "Clavier mobile"],
              [["`email`", "Adresse électronique", "Avec @"],
               ["`tel`", "Numéro de téléphone", "Pavé numérique"],
               ["`url`", "Adresse web", "Avec / et .com"],
               ["`number`", "Nombre", "Pavé numérique"],
               ["`date`", "Date", "Sélecteur natif"],
               ["`search`", "Recherche", "Avec bouton d'effacement"],
               ["`password`", "Mot de passe", "Masqué"],
               ["`checkbox`", "Choix multiple", "Case à cocher"],
               ["`radio`", "Choix unique", "Bouton radio"],
               ["`file`", "Fichier", "Sélecteur de fichiers"]],
              widths=[2.2, 4.6, 4.4], first_col_bold=True,
              caption="Dix types de champs et le clavier qu'ils déclenchent"),
        code("""<form action="/inscription" method="post" novalidate>
  <fieldset>
    <legend>Vos coordonnées</legend>

    <label for="prenom">Prénom</label>
    <input id="prenom" name="prenom" type="text" autocomplete="given-name" required>

    <label for="naissance">Date de naissance</label>
    <input id="naissance" name="naissance" type="date" autocomplete="bday">

    <label for="tel">Téléphone</label>
    <input id="tel" name="tel" type="tel" inputmode="tel"
           autocomplete="tel" pattern="[0-9+ ]{8,15}">
  </fieldset>

  <fieldset>
    <legend>Votre besoin</legend>
    <label><input type="radio" name="besoin" value="site"> Un site vitrine</label>
    <label><input type="radio" name="besoin" value="app"> Une application</label>
  </fieldset>

  <button type="submit">Envoyer</button>
</form>""", "html", "Un formulaire complet, groupé et étiqueté"),
        p("`fieldset` et `legend` regroupent des champs qui appartiennent à une même "
          "question. Pour un groupe de boutons radio, le `legend` joue le rôle de "
          "question et chaque `label` celui de réponse : c'est la seule structure "
          "correctement annoncée par les lecteurs d'écran."),

        h(2, "Validation native"),
        p("HTML5 valide les champs avant l'envoi : champ requis vide, adresse "
          "électronique mal formée, nombre hors bornes. Cette validation améliore le "
          "confort, mais elle est **contournable** et ne remplace jamais le contrôle "
          "serveur."),
        code("""<input type="email" required>
<input type="number" min="1" max="99" step="1">
<input type="text" minlength="3" maxlength="40">
<input type="text" pattern="[A-Za-z0-9_-]{3,16}">
<input type="date" min="2026-01-01" max="2026-12-31">""", "html",
             "Cinq contraintes déclaratives"),
        fig("flow", "Le parcours de validation d'un formulaire",
            ["L'utilisateur remplit les champs",
             "Le navigateur valide selon les attributs HTML",
             "Le navigateur envoie les données au serveur",
             "Le serveur revalide et applique les règles métier",
             "Le serveur répond : succès ou erreurs détaillées"],
            height=255),
        p("Le message d'erreur natif est court et localisé par le navigateur. Pour un "
          "message rédigé, on utilise l'API de contrainte en JavaScript — nous y "
          "reviendrons au chapitre 28. En HTML pur, `title` peut compléter un "
          "`pattern`, mais son affichage reste inégal."),
        box("attention", "La validation native ne sécurise rien",
            "Un utilisateur peut désactiver JavaScript, modifier le HTML ou envoyer "
            "une requête forgée. La validation côté serveur est la seule barrière "
            "fiable ; celle du navigateur est une aide à la saisie."),

        h(2, "Erreurs, aide et états"),
        p("Un bon formulaire prévient l'erreur plutôt que de la signaler. Trois "
          "moyens : indiquer le format attendu avant la saisie, accepter les formats "
          "variés (espaces dans un numéro), et ne demander que le strict nécessaire."),
        code("""<div class="champ">
  <label for="mdp">Mot de passe</label>
  <input id="mdp" name="mdp" type="password" required
         aria-describedby="mdp-aide mdp-erreur"
         aria-invalid="true">
  <p id="mdp-aide" class="aide">Au moins 12 caractères, dont un chiffre.</p>
  <p id="mdp-erreur" class="erreur" role="alert">
    Le mot de passe doit contenir au moins 12 caractères.
  </p>
</div>""", "html", "Aide, erreur et association explicite"),
        table(["Élément", "Fonction", "Remarque"],
              [["`aria-describedby`", "Relie une aide ou une erreur", "Peut pointer plusieurs identifiants"],
               ["`aria-invalid`", "Signale un champ en erreur", "À mettre à jour dynamiquement"],
               ["`role=\"alert\"`", "Annonce immédiate", "À réserver aux erreurs"],
               ["`aria-live=\"polite\"`", "Annonce différée", "Messages de succès"],
               ["`aria-busy`", "Indique un traitement en cours", "Sur la zone concernée"]],
              widths=[3.4, 4.4, 4.2], first_col_bold=True,
              caption="Cinq attributs pour un formulaire qui se comprend"),
        p("Le message d'erreur doit dire **ce qui ne va pas** et **comment corriger**. "
          "« Erreur de saisie » ne sert à rien ; « Le code postal doit comporter cinq "
          "chiffres » permet de corriger immédiatement."),
        code(""".champ { display: grid; gap: .35rem; margin-bottom: 1.25rem; }
.aide { color: #5b6770; font-size: .875rem; }
.erreur { color: #a63a32; font-size: .875rem; }
input[aria-invalid="true"] { border-color: #a63a32; border-width: 2px; }
[required] > label::after { content: " *"; color: #a63a32; }""", "css",
             "Une présentation qui ne repose pas sur la couleur seule"),

        h(2, "Au-delà du HTML : ce que le serveur doit faire"),
        p("Le formulaire envoie des données non fiables par définition. Le serveur "
          "doit les valider, les normaliser et les protéger avant de les stocker ou "
          "de les afficher."),
        ul("**Valider** chaque champ selon les mêmes règles, sans faire confiance au client.",
           "**Normaliser** : supprimer les espaces superflus, mettre en minuscules les "
           "adresses électroniques, convertir les dates au format ISO.",
           "**Limiter** la taille des envois et le nombre de tentatives.",
           "**Échapper** les valeurs affichées pour éviter les injections.",
           "**Protéger** les formulaires par un jeton anti-CSRF et, si nécessaire, "
           "par un captcha discret."),
        defn("CSRF", "Cross-Site Request Forgery : un site malveillant déclenche une "
                     "requête authentifiée sur un autre site, à l'insu de l'utilisateur. "
                     "Un jeton unique par session bloque cette attaque."),
        box("methode", "Check-list avant publication",
            items=["Chaque champ a une étiquette visible.",
                   "Les champs obligatoires sont signalés par du texte, pas seulement par une couleur.",
                   "Les messages d'erreur indiquent la correction attendue.",
                   "Le formulaire se remplit entièrement au clavier.",
                   "Les données sont validées une seconde fois côté serveur.",
                   "L'envoi affiche un état de chargement, puis un message de succès."]),
    ],
    "keypoints": [
        "Un formulaire fonctionne sans JavaScript : c'est le socle.",
        "Chaque champ a une étiquette visible, jamais un simple placeholder.",
        "Le type de champ détermine le clavier et la validation native.",
        "`fieldset` et `legend` structurent les groupes de questions.",
        "La validation native aide l'utilisateur, elle ne sécurise rien.",
        "Un message d'erreur dit quoi corriger, pas seulement qu'il y a une erreur.",
        "Le serveur revalide, normalise et protège systématiquement.",
    ],
    "bridge": "Le HTML est complet. Il est temps de lui donner une apparence : "
              "le chapitre suivant introduit CSS, la cascade et les premiers styles.",
    "exercises": [
        ex("Formulaire de contact accessible",
           "Construisez un formulaire de contact avec nom, adresse électronique, "
           "sujet et message.",
           ["Ajoutez les étiquettes, les types adaptés et l'autocomplétion.",
            "Rendez l'adresse électronique et le message obligatoires.",
            "Ajoutez une aide sous le champ message indiquant la longueur maximale."],
           [("code", """<form action="/contact" method="post">
  <fieldset>
    <legend>Votre message</legend>

    <label for="nom">Nom</label>
    <input id="nom" name="nom" type="text" autocomplete="name" required>

    <label for="email">Adresse électronique</label>
    <input id="email" name="email" type="email" autocomplete="email" required>

    <label for="sujet">Sujet</label>
    <select id="sujet" name="sujet">
      <option value="info">Demande d'information</option>
      <option value="bug">Signaler un problème</option>
      <option value="autre">Autre</option>
    </select>

    <label for="message">Message</label>
    <textarea id="message" name="message" rows="6" maxlength="2000"
              required aria-describedby="message-aide"></textarea>
    <p id="message-aide">2 000 caractères maximum.</p>
  </fieldset>
  <button type="submit">Envoyer le message</button>
</form>"""),
            "L'attribut `autocomplete` accélère la saisie et améliore l'accessibilité "
            "cognitive. Les valeurs normalisées (`name`, `email`) ne sont pas "
            "arbitraires : elles sont reconnues par les navigateurs.",
            "L'aide est reliée par `aria-describedby`. Elle est annoncée avec le "
            "champ, sans être confondue avec l'étiquette."]),
        ex("Auditer un formulaire défaillant",
           "Voici un formulaire réel. Repérez six défauts et corrigez-les.",
           ["`<input type=\"text\" placeholder=\"Votre email\">`",
            "`<label>Nom</label><input name=\"nom\">`",
            "`<input type=\"text\" name=\"age\">` pour un âge",
            "`<input type=\"text\" name=\"tel\">` pour un téléphone",
            "`<button>OK</button>` sans type",
            "Un message d'erreur « Champ invalide »"],
           ["Le `placeholder` ne remplace pas une étiquette : ajoutez `label for`.",
            "L'étiquette n'est pas associée : il manque `for` et `id`.",
            "Un âge est un nombre : `type=\"number\"` avec `min` et `max`.",
            "Un téléphone est un `type=\"tel\"` avec `inputmode` adapté.",
            "Un `button` sans type vaut `submit` : précisez `type=\"submit\"`.",
            "« Champ invalide » n'aide pas : indiquez la règle et la correction."],
           level="Diagnostic"),
        ex("Écrire la validation serveur correspondante",
           "Rédigez en pseudo-code les contrôles serveur du formulaire précédent.",
           ["Listez les règles par champ.",
            "Indiquez l'ordre des contrôles.",
            "Précisez ce qui est renvoyé à l'utilisateur en cas d'échec."],
           ["Règles : nom non vide, 2 à 80 caractères ; adresse électronique conforme "
            "et domaine résolvable (facultatif) ; sujet parmi une liste fermée ; "
            "message de 10 à 2 000 caractères.",
            "Ordre : vérifier la méthode et le jeton anti-CSRF, limiter la taille, "
            "normaliser, valider champ par champ, puis traiter.",
            "En cas d'échec : réponse 422 avec la liste des champs fautifs et un "
            "message par champ ; les valeurs saisies sont conservées pour ne pas "
            "obliger à tout retaper."],
           level="Conception"),
    ],
    "quiz": [
        quiz("Quel est le rôle de `<label for=\"x\">` ?",
             ["Colorer le champ", "Associer un texte au champ `id=\"x\"`", "Valider le champ", "Envoyer le formulaire"],
             1,
             "L'attribut `for` relie l'étiquette au champ d'identifiant correspondant, "
             "ce qui permet l'annonce par les lecteurs d'écran et le clic sur le texte."),
        quiz("Quel type de champ déclenche un clavier numérique sur mobile pour un âge ?",
             ["`text`", "`tel`", "`number`", "`range`"],
             2,
             "`number` déclenche le pavé numérique et active les bornes `min` et `max`."),
        quiz("Pourquoi la validation HTML seule est-elle insuffisante ?",
             ["Elle est trop lente",
              "Elle peut être contournée par une requête forgée",
              "Elle ne fonctionne pas sur mobile",
              "Elle nécessite JavaScript"],
             1,
             "Le client est sous le contrôle de l'utilisateur : toute donnée envoyée "
             "doit être revalidée côté serveur."),
        quiz("Quel attribut relie une aide à un champ ?",
             ["`aria-label`", "`aria-describedby`", "`title`", "`placeholder`"],
             1,
             "`aria-describedby` pointe vers l'identifiant du texte d'aide ou d'erreur, "
             "qui est alors annoncé avec le champ."),
        quiz("Quelle méthode HTTP utiliser pour envoyer un mot de passe ?",
             ["`GET`", "`POST`", "`PUT`", "`HEAD`"],
             1,
             "`GET` place les données dans l'URL, où elles sont visibles dans "
             "l'historique et les journaux. `POST` place les données dans le corps."),
    ],
}
