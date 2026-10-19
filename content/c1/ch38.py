from bookkit.dsl import (box, code, defn, ex, fig, h, ol, p, quiz, table, ul)

CH = {
    "title": "Composants web et système de design",
    "subtitle": "Construire une bibliothèque d'éléments réutilisables, documentés et "
                "partagés entre plusieurs projets.",
    "duration": "3 h 15",
    "level": "Avancé",
    "prereq": "chapitre 37",
    "objectives": [
        "Créer un élément personnalisé avec cycle de vie.",
        "Isoler styles et structure avec le shadow DOM.",
        "Exposer une API d'attributs et d'événements claire.",
        "Construire un système de jetons de design.",
        "Documenter et maintenir une bibliothèque de composants.",
    ],
    "blocks": [
        h(2, "Trois technologies, un composant"),
        p("Les composants web reposent sur trois standards : les éléments personnalisés, "
          "le shadow DOM et les modèles HTML. Ensemble, ils permettent de créer une "
          "balise comme `<carte-produit>` qui fonctionne dans n'importe quel projet."),
        table(["Standard", "Rôle", "Maturité"],
              [["Custom Elements", "Définir une balise et son cycle de vie", "Stable"],
               ["Shadow DOM", "Isoler structure et styles", "Stable"],
               ["`<template>`", "Conserver un fragment inerte", "Stable"],
               ["Slots", "Projeter du contenu", "Stable"],
               ["Attributs réactifs", "Synchroniser propriétés et attributs", "Manuel"]],
              widths=[3.6, 5.4, 3.0], first_col_bold=True,
              caption="Cinq briques et leur statut"),
        code("""<template id="modele-carte">
  <style>
    :host { display: block; border: 1px solid #e8edf1; border-radius: 8px; }
    :host([est-active]) { border-color: #e0a21b; }
    .corps { padding: 1rem; }
  </style>
  <div class="corps"><slot></slot></div>
</template>

<script type="module">
  class CarteProduit extends HTMLElement {
    static observedAttributes = ["titre", "est-active"];
    #racine;
    #titre;

    constructor() {
      super();
      this.#racine = this.attachShadow({ mode: "open" });
      this.#racine.append(document.getElementById("modele-carte").content.cloneNode(true));
      this.#titre = document.createElement("h3");
      this.#racine.querySelector(".corps").prepend(this.#titre);
    }

    connectedCallback() { this.setAttribute("role", "group"); }

    attributeChangedCallback(nom, ancien, nouveau) {
      if (nom === "titre") this.#titre.textContent = nouveau ?? "";
    }
  }

  customElements.define("carte-produit", CarteProduit);
</script>""", "html", "Un composant complet en quinze lignes utiles"),

        h(2, "Le cycle de vie"),
        p("Un élément personnalisé traverse quatre étapes. Chacune correspond à un "
          "moment précis où l'on peut agir sans casser le rendu."),
        table(["Méthode", "Moment", "Usage typique"],
              [["`constructor`", "Création", "Attacher le shadow DOM"],
               ["`connectedCallback`", "Insertion dans le document", "Écouteurs, chargement"],
               ["`disconnectedCallback`", "Retrait du document", "Nettoyage, annulation"],
               ["`attributeChangedCallback`", "Attribut observé modifié", "Mise à jour ciblée"],
               ["`adoptedCallback`", "Changement de document", "Rare"]],
              widths=[4.4, 4.4, 3.2], first_col_bold=True,
              caption="Cinq points d'accroche"),
        box("attention", "`connectedCallback` peut s'exécuter plusieurs fois",
            "Un élément déplacé dans le DOM est retiré puis réinséré : `disconnected` "
            "puis `connected` se déclenchent à nouveau. Les écouteurs doivent donc être "
            "retirés proprement, sinon ils s'accumulent."),
        code("""class Compteur extends HTMLElement {
  #valeur = 0;
  #abandon = null;

  connectedCallback() {
    this.#abandon = new AbortController();
    this.addEventListener("click", () => this.#incrementer(),
      { signal: this.#abandon.signal });
  }

  disconnectedCallback() {
    this.#abandon.abort();     // retire tous les écouteurs d'un coup
  }

  #incrementer() {
    this.#valeur += 1;
    this.dispatchEvent(new CustomEvent("compteur:changement", {
      bubbles: true, detail: { valeur: this.#valeur },
    }));
  }
}""", "js", "Un nettoyage fiable via `AbortController`"),

        h(2, "API d'un composant"),
        p("Un composant utile expose une interface stable : des attributs pour la "
          "configuration déclarative, des propriétés pour l'usage programmatique, et "
          "des événements pour communiquer."),
        code("""<carte-produit titre="Chaise haute" prix="89" devise="EUR" est-active>
  <p>Structure en frêne massif, assise rembourrée.</p>
  <a slot="action" href="/produit/12">Voir le détail</a>
</carte-produit>""", "html", "Un usage déclaratif lisible"),
        code("""class CarteProduit extends HTMLElement {
  static observedAttributes = ["titre", "prix", "devise", "est-active"];

  get prix() { return Number(this.getAttribute("prix") ?? 0); }
  set prix(valeur) { this.setAttribute("prix", String(valeur)); }

  attributeChangedCallback(nom) {
    if (["titre", "prix", "devise"].includes(nom)) this.#rendre();
  }

  #rendre() {
    const montant = new Intl.NumberFormat("fr-FR", {
      style: "currency", currency: this.getAttribute("devise") ?? "EUR",
    }).format(this.prix);
    this.#racine.querySelector(".prix").textContent = montant;
  }
}""", "js", "Attributs et propriétés synchronisés"),
        table(["Élément", "Public", "Usage"],
              [["Attributs", "Auteur HTML", "Configuration déclarative"],
               ["Propriétés", "Code", "Mise à jour programmatique"],
               ["Événements", "Consommateur", "Notification"],
               ["Slots", "Auteur HTML", "Contenu projeté"],
               ["Parties (`part`)", "CSS externe", "Personnalisation contrôlée"]],
              widths=[3.4, 4.0, 4.6], first_col_bold=True,
              caption="Cinq éléments d'interface"),
        defn("Shadow DOM", "Arbre de nœuds attaché à un élément, isolé du document "
                           "principal : les styles internes n'en sortent pas, les styles "
                           "externes n'y entrent pas, sauf via `::part` ou des "
                           "propriétés personnalisées."),

        h(2, "Système de jetons"),
        p("Un système de design ne commence pas par des composants, mais par des "
          "décisions nommées : couleurs, espacements, typographie, rayons, durées. Ces "
          "jetons traversent le shadow DOM, contrairement aux sélecteurs."),
        code(""":root {
  /* Primitives : valeurs brutes */
  --couleur-navy-700: #0f2e4c;
  --couleur-ambre-500: #e0a21b;
  --espace-100: 4px;
  --espace-200: 8px;
  --espace-400: 16px;
  --rayon-m: 8px;

  /* Sémantiques : rôle dans l'interface */
  --couleur-texte: var(--couleur-navy-700);
  --couleur-accent: var(--couleur-ambre-500);
  --espace-bloc: var(--espace-400);
  --bordure-carte: 1px solid #e8edf1;
}

[data-theme="sombre"] {
  --couleur-texte: #e8edf1;
  --bordure-carte: 1px solid #1b2c3d;
}""", "css", "Deux niveaux de jetons"),
        table(["Niveau", "Exemple", "Qui l'utilise"],
              [["Primitive", "`--couleur-navy-700`", "Le système uniquement"],
               ["Sémantique", "`--couleur-texte`", "Les composants"],
               ["Composant", "`--carte-padding`", "Le composant et ses surcharges"]],
              widths=[3.4, 4.8, 3.8], first_col_bold=True,
              caption="Trois niveaux de jetons"),
        box("pratique", "Les jetons traversent le shadow DOM",
            "Les propriétés personnalisées sont héritées : un composant peut lire "
            "`var(--couleur-texte)` même enfermé dans un shadow DOM. C'est le mécanisme "
            "de thème recommandé."),
        code("""/* Personnalisation contrôlée depuis l'extérieur */
carte-produit::part(prix) {
  font-weight: 700;
  color: var(--couleur-accent);
}

/* Dans le composant */
/* <span part="prix" class="prix"></span> */""", "css",
             "Une porte de sortie explicite"),

        h(2, "Documenter la bibliothèque"),
        p("Un composant non documenté est un composant que personne n'utilise "
          "correctement. La documentation minimale décrit l'usage, les attributs, les "
          "événements et les règles d'accessibilité."),
        code("""## `<carte-produit>`

Présente un produit dans une liste.

### Attributs
| Nom          | Type    | Défaut | Description          |
|--------------|---------|--------|----------------------|
| `titre`      | chaîne  | —      | Nom du produit       |
| `prix`       | nombre  | `0`    | Prix en unités       |
| `devise`     | chaîne  | `EUR`  | Code ISO 4217        |
| `est-active` | booléen | absent | Met la carte en avant|

### Slots
- `action` : lien ou bouton d'action.

### Événements
- `carte:selection` : émis au clic sur l'action.

### Accessibilité
Le titre est un `h3`. Le conteneur porte `role="group"` et le nom
accessible provient du titre.""", "markdown", "Une fiche de composant"),
        fig("flow", "Le cycle de vie d'un composant",
            ["Spécification et maquette",
             "Jetons et variantes",
             "Implémentation et tests",
             "Documentation et exemples",
             "Publication et versionnement",
             "Dépréciation des anciennes versions"],
            height=265),
        box("methode", "Trois questions avant de créer un composant",
            items=["Est-il utilisé au moins trois fois ?",
                   "Sa sémantique HTML est-elle correcte sans JavaScript ?",
                   "Que se passe-t-il s'il est utilisé dans un contexte imprévu ?"]),
    ],
    "keypoints": [
        "Un composant web combine élément personnalisé, shadow DOM et modèle.",
        "`connectedCallback` peut s'exécuter plusieurs fois.",
        "Les écouteurs se retirent au démontage, idéalement via `AbortController`.",
        "Les attributs configurent, les propriétés mettent à jour, les événements notifient.",
        "Les propriétés personnalisées traversent le shadow DOM.",
        "`::part` offre une personnalisation contrôlée.",
        "Un composant se documente comme une API publique.",
    ],
    "bridge": "Les composants se partagent. Le chapitre suivant traite de ce qui circule "
              "entre les langues et les cultures : l'internationalisation.",
    "exercises": [
        ex("Créer un bouton personnalisé",
           "Concevez `<bouton-action>` avec variantes et état de chargement.",
           ["Attribut `variante` et `desactive`.",
            "Slot pour le contenu.",
            "État de chargement annoncé."],
           [("code", """class BoutonAction extends HTMLElement {
  static observedAttributes = ["variante", "charge", "desactive"];

  constructor() {
    super();
    this.attachShadow({ mode: "open" }).innerHTML = `
      <style>
        :host { display: inline-block; }
        button {
          font: inherit; padding: .6rem 1.1rem; border-radius: 8px;
          border: 1px solid transparent; cursor: pointer;
        }
        :host([variante="principal"]) button { background: var(--accent, #e0a21b); }
        :host([variante="secondaire"]) button { border-color: currentColor; background: none; }
        button:disabled { opacity: .6; cursor: progress; }
      </style>
      <button part="bouton"><slot></slot></button>`;

    this.#bouton = this.shadowRoot.querySelector("button");
  }

  #bouton;

  connectedCallback() {
    this.#bouton.addEventListener("click", () => {
      if (this.hasAttribute("charge")) return;
      this.dispatchEvent(new CustomEvent("action", { bubbles: true }));
    });
  }

  attributeChangedCallback(nom) {
    if (nom === "charge") {
      this.#bouton.setAttribute("aria-busy", String(this.hasAttribute("charge")));
    }
    if (nom === "desactive") {
      this.#bouton.disabled = this.hasAttribute("desactive");
    }
  }
}
customElements.define("bouton-action", BoutonAction);"""),
            "Le `<button>` interne conserve le comportement clavier natif.",
            "`part=\"bouton\"` permet de personnaliser l'apparence depuis la page "
            "hôte."]),
        ex("Construire une échelle de jetons",
           "Définissez une échelle d'espacement et de couleurs sémantiques.",
           ["Primitives numériques.",
            "Alias sémantiques.",
            "Variante sombre complète."],
           [("code", """:root {
  --espace-1: .25rem;  --espace-2: .5rem;  --espace-3: 1rem;
  --espace-4: 2rem;    --espace-5: 4rem;

  --couleur-fond: #ffffff;
  --couleur-surface: #f7f9fa;
  --couleur-texte: #1f2933;
  --couleur-texte-doux: #5b6770;
  --couleur-accent: #0f2e4c;
  --couleur-danger: #a63a32;
}

[data-theme="sombre"] {
  --couleur-fond: #0b1622;
  --couleur-surface: #12202e;
  --couleur-texte: #e8edf1;
  --couleur-texte-doux: #a7b4c0;
  --couleur-accent: #e0a21b;
}"""),
            "Les composants ne connaissent que les alias sémantiques : changer de thème "
            "ne demande aucune modification de leur code.",
            "L'échelle géométrique (`1, 2, 3, 4, 5`) produit un rythme régulier, là où "
            "des valeurs arbitraires produisent un espacement incohérent."]),
        ex("Documenter un composant",
           "Rédigez la fiche de `<carte-produit>`.",
           ["Attributs avec types et défauts.",
            "Événements émis.",
            "Contraintes d'accessibilité."],
           [("markdown", """## `<carte-produit>`

### Attributs
| Nom | Type | Défaut | Description |
|-----|------|--------|-------------|
| `titre` | chaîne | — | Nom affiché en `h3` |
| `prix` | nombre | `0` | Prix hors taxes |
| `devise` | chaîne | `EUR` | Code ISO 4217 |
| `est-active` | booléen | absent | Bordure accentuée |

### Slots
- défaut : description
- `action` : lien vers la fiche produit

### Événements
- `carte:selection` : `detail.id`, émis au clic sur l'action

### Accessibilité
- Le titre alimente le nom accessible du groupe.
- L'état actif ne doit pas être la seule indication visuelle."""),
            "Un tableau d'attributs évite les allers-retours dans le code source.",
            "La section accessibilité fixe les obligations du composant et de ses "
            "utilisateurs."],
           level="Documentation"),
    ],
    "quiz": [
        quiz("Quel standard isole les styles d'un composant ?",
             ["Le shadow DOM", "Les couches de cascade", "Les attributs `data-*`", "Les media queries"],
             0,
             "Le shadow DOM crée un sous-arbre dont les styles sont confinés."),
        quiz("Que se passe-t-il quand un élément est déplacé dans le DOM ?",
             ["Rien", "`disconnected` puis `connected` se déclenchent",
              "`constructor` est rappelé", "L'élément est détruit"],
             1,
             "Le déplacement implique un retrait puis une réinsertion."),
        quiz("Quel mécanisme traverse le shadow DOM ?",
             ["Les sélecteurs de classe", "Les propriétés personnalisées",
              "Les media queries", "Les identifiants"],
             1,
             "Les propriétés CSS personnalisées sont héritées à travers la frontière."),
        quiz("À quoi sert `::part` ?",
             ["À créer un slot", "À exposer un élément interne au style externe",
              "À définir un attribut", "À charger un module"],
             1,
             "Il ouvre une porte de personnalisation contrôlée."),
        quiz("Combien de niveaux de jetons distingue-t-on couramment ?",
             ["Un", "Deux ou trois", "Dix", "Aucun"],
             1,
             "Primitives, sémantiques et parfois jetons de composant."),
    ],
}
