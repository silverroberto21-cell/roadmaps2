from bookkit.dsl import (box, code, defn, ex, fig, h, ol, p, quiz, table, ul)

CH = {
    "title": "Formulaires et validation côté client",
    "subtitle": "Guider la saisie, signaler les erreurs au bon moment et ne jamais "
                "perdre le travail de l'utilisateur.",
    "duration": "2 h 45",
    "level": "Intermédiaire",
    "prereq": "chapitre 27",
    "objectives": [
        "Valider avec l'API de contrainte du navigateur.",
        "Écrire des messages d'erreur personnalisés et accessibles.",
        "Envoyer un formulaire sans rechargement de page.",
        "Gérer les états de chargement, de succès et d'échec.",
        "Préserver les données saisies en cas d'erreur.",
    ],
    "blocks": [
        h(2, "L'API de contrainte"),
        p("Chaque champ expose un objet `validity` qui décrit précisément ce qui ne va "
          "pas : valeur manquante, format incorrect, longueur insuffisante. C'est la "
          "base d'une validation fiable sans réinventer les règles."),
        code("""const champ = document.querySelector("#courriel");

champ.validity.valid          // tout va bien ?
champ.validity.valueMissing   // required non rempli
champ.validity.typeMismatch   // email mal formé
champ.validity.tooShort       // minlength non atteint
champ.validity.patternMismatch
champ.validationMessage       // message natif du navigateur""", "js",
             "Ce que le navigateur sait déjà vérifier"),
        table(["Attribut", "Contrainte", "Propriété de `validity`"],
              [["`required`", "Champ obligatoire", "`valueMissing`"],
               ["`type=email`", "Format d'adresse", "`typeMismatch`"],
               ["`minlength`", "Longueur minimale", "`tooShort`"],
               ["`maxlength`", "Longueur maximale", "`tooLong`"],
               ["`pattern`", "Expression régulière", "`patternMismatch`"],
               ["`min` / `max`", "Bornes numériques", "`rangeUnderflow` / `rangeOverflow`"],
               ["`step`", "Pas d'incrément", "`stepMismatch`"]],
              widths=[3.0, 4.2, 4.2], first_col_bold=True,
              caption="Sept attributs et la contrainte correspondante"),
        code("""formulaire.addEventListener("submit", (event) => {
  if (!formulaire.checkValidity()) {
    event.preventDefault();
    formulaire.reportValidity();   // affiche les messages natifs
  }
});""", "js", "La validation native, en trois lignes"),

        h(2, "Messages personnalisés"),
        p("Le message natif est court et localisé, mais souvent trop technique. Pour "
          "un message rédigé, on utilise `setCustomValidity` — en pensant à le remettre "
          "à zéro dès que la saisie devient valide, sinon le champ reste invalide pour "
          "toujours."),
        code("""function validerMotDePasse(champ) {
  const valeur = champ.value;
  let message = "";

  if (valeur.length === 0) message = "Le mot de passe est obligatoire.";
  else if (valeur.length < 12) message = "Le mot de passe doit comporter 12 caractères minimum.";
  else if (!/[0-9]/.test(valeur)) message = "Ajoutez au moins un chiffre.";
  else if (!/[A-Z]/.test(valeur)) message = "Ajoutez au moins une majuscule.";

  champ.setCustomValidity(message);
  const zoneErreur = document.querySelector("#mdp-erreur");
  zoneErreur.textContent = message;
  champ.setAttribute("aria-invalid", String(Boolean(message)));
  return message === "";
}

champ.addEventListener("input", () => validerMotDePasse(champ));""", "js",
             "Une validation qui explique la correction"),
        box("attention", "Le piège du message persistant",
            "Si vous appelez `setCustomValidity(\"erreur\")` sans jamais repasser à une "
            "chaîne vide, le champ reste invalide même après correction. Remettez "
            "toujours la validité à zéro dans chaque branche qui ne signale pas "
            "d'erreur."),
        p("Le moment du message compte autant que son contenu : signaler une erreur "
          "pendant la frappe est agressif, l'afficher à la sortie du champ est "
          "pédagogique."),
        table(["Moment", "Comportement", "Recommandation"],
              [["Pendant la frappe", "Erreur à chaque caractère", "À éviter"],
               ["À la sortie du champ (`blur`)", "Vérifie et signale", "Recommandé"],
               ["À l'envoi", "Résumé des erreurs", "Indispensable"],
               ["Après correction", "Efface l'erreur", "Obligatoire"]],
              widths=[3.4, 4.4, 3.8], first_col_bold=True,
              caption="Quatre moments de validation"),

        h(2, "Envoyer sans recharger la page"),
        p("`fetch` envoie les données en arrière-plan. Il faut gérer quatre états : "
          "envoi en cours, succès, échec réseau, échec de validation serveur."),
        code("""formulaire.addEventListener("submit", async (event) => {
  event.preventDefault();

  const bouton = formulaire.querySelector("button[type=submit]");
  bouton.disabled = true;
  bouton.setAttribute("aria-busy", "true");

  try {
    const reponse = await fetch("/api/contact", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(Object.fromEntries(new FormData(formulaire))),
    });

    if (!reponse.ok) {
      const erreurs = await reponse.json();
      afficherErreurs(erreurs);        // 422 : erreurs par champ
      return;
    }

    afficherSucces("Message envoyé.");
    formulaire.reset();
  } catch (erreur) {
    afficherErreurGlobale("Connexion impossible. Réessayez.");
  } finally {
    bouton.disabled = false;
    bouton.removeAttribute("aria-busy");
  }
});""", "js", "Un envoi asynchrone complet"),
        fig("flow", "Les états d'un envoi de formulaire",
            ["L'utilisateur soumet",
             "Le bouton passe en état de chargement",
             "La requête part et attend la réponse",
             "Succès : confirmation et réinitialisation",
             "Échec : erreurs affichées, données conservées"],
            height=255),
        defn("Code 422", "Réponse HTTP signifiant que la requête est bien formée mais "
                         "que les données sont invalides. Le corps contient souvent le "
                         "détail des erreurs par champ."),
        box("retenir", "Ne jamais effacer un formulaire en échec",
            "Un utilisateur qui a rempli dix champs et perd sa saisie à cause d'une "
            "erreur serveur ne reviendra pas. Conservez les valeurs, signalez les "
            "champs fautifs, et replacez le focus sur le premier d'entre eux."),

        h(2, "Erreurs et focus"),
        p("Après un échec, le focus doit conduire à l'erreur. Deux stratégies : "
          "déplacer le focus sur le résumé en tête de formulaire, ou sur le premier "
          "champ invalide."),
        code("""function afficherErreurs(erreurs) {
  const resume = document.querySelector("#resume-erreurs");
  resume.innerHTML = "";
  const liste = document.createElement("ul");

  for (const [champ, message] of Object.entries(erreurs)) {
    const li = document.createElement("li");
    const lien = document.createElement("a");
    lien.href = `#${champ}`;
    lien.textContent = message;
    li.append(lien);
    liste.append(li);

    const input = document.getElementById(champ);
    input.setAttribute("aria-invalid", "true");
    input.setAttribute("aria-describedby", `${champ}-erreur`);
  }

  resume.append(liste);
  resume.hidden = false;
  resume.focus();          // le résumé est focusable (tabindex="-1")
}""", "js", "Un résumé d'erreurs navigable"),
        p("Le résumé est annoncé par `role=\"alert\"`, ses liens conduisent aux champs, "
          "et le focus y est placé : l'utilisateur au lecteur d'écran entend "
          "immédiatement ce qui bloque."),

        h(2, "Cas particuliers"),
        p("Quelques champs demandent un traitement spécifique : fichiers, champs "
          "conditionnels, cases de consentement."),
        code("""// Aperçu d'une image avant envoi
fichier.addEventListener("change", () => {
  const fichierChoisi = fichier.files[0];
  if (!fichierChoisi) return;
  if (fichierChoisi.size > 2 * 1024 * 1024) {
    afficherErreur("L'image doit peser moins de 2 Mo.");
    fichier.value = "";
    return;
  }
  apercu.src = URL.createObjectURL(fichierChoisi);
});

// Champ conditionnel
typeAbonnement.addEventListener("change", () => {
  const entreprise = typeAbonnement.value === "entreprise";
  champSociete.hidden = !entreprise;
  champSociete.required = entreprise;
});""", "js", "Deux cas fréquents"),
        code("""<!-- Consentement explicite, jamais précoché -->
<label for="cgv">
  <input id="cgv" type="checkbox" name="cgv" required>
  J'accepte les conditions générales
</label>""", "html", "Une case de consentement conforme"),
        box("methode", "Check-list d'un formulaire professionnel",
            items=["Chaque champ a une étiquette visible et un type adapté.",
                   "Les erreurs sont annoncées et liées aux champs.",
                   "Les données sont conservées en cas d'échec.",
                   "Le bouton indique l'état de chargement.",
                   "La validation serveur existe et renvoie des messages exploitables."]),
    ],
    "keypoints": [
        "L'API `validity` décrit précisément pourquoi un champ est invalide.",
        "`setCustomValidity` doit toujours être réinitialisé.",
        "Valider à la sortie du champ plutôt qu'à chaque frappe.",
        "`fetch` impose de gérer quatre états distincts.",
        "Un formulaire en échec conserve les données saisies.",
        "Le résumé d'erreurs est annoncé et conduit aux champs.",
        "La validation serveur reste indispensable.",
    ],
    "bridge": "Le formulaire dialogue avec un serveur. Le chapitre suivant approfondit "
              "cette communication : asynchrone, promesses et API.",
    "exercises": [
        ex("Valider un mot de passe",
           "Écrivez une validation complète avec messages et annonce.",
           ["Contrôlez longueur, chiffre et majuscule.",
            "Affichez un message par règle non respectée.",
            "Mettez à jour `aria-invalid`."],
           [("code", """const regles = [
  { test: v => v.length >= 12, message: "12 caractères minimum." },
  { test: v => /[0-9]/.test(v), message: "Au moins un chiffre." },
  { test: v => /[A-Z]/.test(v), message: "Au moins une majuscule." },
];

function valider(champ, zone) {
  const manquantes = regles.filter(r => !r.test(champ.value)).map(r => r.message);
  zone.textContent = manquantes.join(" ");
  champ.setAttribute("aria-invalid", String(manquantes.length > 0));
  champ.setCustomValidity(manquantes.length ? manquantes.join(" ") : "");
  return manquantes.length === 0;
}"""),
            "Chaque règle est indépendante : l'utilisateur voit toutes les contraintes "
            "manquantes d'un coup, pas une par une.",
            "Le message reste dans une zone liée par `aria-describedby`, ce qui évite "
            "de perturber la saisie."]),
        ex("Soumettre un formulaire au serveur",
           "Envoyez les données en JSON et affichez le résultat.",
           ["Gérez l'état de chargement.",
            "Traitez les codes 200 et 422.",
            "Prévoyez une erreur réseau."],
           [("code", """async function envoyer(donnees) {
  const reponse = await fetch("/api/commande", {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify(donnees),
  });

  if (reponse.status === 422) {
    const { erreurs } = await reponse.json();
    throw new ValidationError(erreurs);
  }
  if (!reponse.ok) throw new Error(`Erreur serveur ${reponse.status}`);

  return reponse.json();
}"""),
            "Le code 422 est distinct d'une erreur serveur : il transporte des erreurs "
            "de validation exploitables champ par champ.",
            "Une erreur réseau (`TypeError`) n'a pas de statut : elle doit être "
            "distinguée d'une réponse HTTP en erreur."]),
        ex("Améliorer l'expérience d'erreur",
           "Un utilisateur a rempli huit champs et reçoit « erreur ».",
           ["Rédigez un résumé exploitable.",
            "Conservez les valeurs.",
            "Replacez le focus."],
           [("code", """<div id="resume-erreurs" role="alert" tabindex="-1" hidden>
  <p><strong>2 champs nécessitent une correction :</strong></p>
  <ul>
    <li><a href="#email">L'adresse électronique est incomplète.</a></li>
    <li><a href="#cp">Le code postal doit comporter cinq chiffres.</a></li>
  </ul>
</div>"""),
            "Le résumé indique le nombre d'erreurs et permet d'y accéder directement.",
            "Les valeurs restent dans les champs : aucune réinitialisation tant que "
            "l'envoi n'a pas réussi."],
           level="Accessibilité"),
    ],
    "quiz": [
        quiz("Quelle propriété indique qu'un champ obligatoire est vide ?",
             ["`validity.typeMismatch`", "`validity.valueMissing`", "`validity.tooShort`", "`validity.patternMismatch`"],
             1,
             "`valueMissing` correspond à l'attribut `required` non satisfait."),
        quiz("Que se passe-t-il si `setCustomValidity` n'est jamais réinitialisé ?",
             ["Rien", "Le champ reste invalide définitivement",
              "Le formulaire s'envoie deux fois", "Le message disparaît"],
             1,
             "Le message personnalisé persiste et bloque la validation même après "
             "correction."),
        quiz("Quand afficher une erreur de saisie ?",
             ["À chaque caractère", "À la sortie du champ ou à l'envoi",
              "Uniquement au rechargement", "Jamais"],
             1,
             "Signaler pendant la frappe est agressif ; à la sortie du champ, le "
             "message est utile."),
        quiz("Que signifie un code 422 ?",
             ["Succès", "Requête bien formée mais données invalides",
              "Erreur de connexion", "Redirection"],
             1,
             "422 Unprocessable Entity signale une validation échouée côté serveur."),
        quiz("Que faire des données saisies quand l'envoi échoue ?",
             ["Les effacer", "Les conserver", "Les chiffrer", "Les envoyer à nouveau automatiquement"],
             1,
             "Conserver la saisie évite à l'utilisateur de tout recommencer."),
    ],
}
