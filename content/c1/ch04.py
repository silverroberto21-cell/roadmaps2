from bookkit.dsl import (box, code, defn, ex, fig, h, ol, p, quiz, table, ul)

CH = {
    "title": "Texte, listes et sémantique",
    "subtitle": "Choisir la balise juste : la compétence qui distingue un document "
                "solide d'une suite de paragraphes.",
    "duration": "2 h 30",
    "level": "Débutant",
    "prereq": "chapitre 3",
    "objectives": [
        "Structurer un texte long avec titres, paragraphes et listes.",
        "Distinguer les balises de sens des balises de présentation.",
        "Employer correctement citations, abréviations, dates et code en ligne.",
        "Maîtriser les caractères spéciaux et les entités HTML.",
        "Relire un document et justifier chaque choix de balise.",
    ],
    "blocks": [
        h(2, "Le texte avant la forme"),
        p("Le contenu textuel représente l'essentiel d'une page web. Avant de penser "
          "taille, couleur ou graisse, il faut répondre à une question : **quelle est "
          "la nature de ce fragment de texte ?** Un titre, une liste, une citation, "
          "un terme technique, une date, une abréviation n'ont pas le même sens. "
          "HTML fournit une balise pour chacun."),
        p("Cette rigueur n'est pas un exercice de style. Elle produit des documents "
          "exploitables par les moteurs de recherche, lisibles par les lecteurs "
          "d'écran, exportables vers d'autres formats et maintenables par d'autres "
          "développeurs. Un texte balisé avec soin se met en forme plus facilement "
          "qu'un texte anonyme."),
        fig("tree", "Deux façons de baliser le même contenu",
            ("Un article", [("Avec sens", ["h1", "p", "ul", "blockquote", "time"]),
                            ("Avec présentation", ["div class=title", "div",
                                                   "div class=list", "div", "span"])]),
            height=215, note="Les deux rendus peuvent être identiques ; seule la "
                             "première version reste compréhensible par une machine."),

        h(2, "Titres et paragraphes"),
        p("Les six niveaux de titre forment un plan. Un document commence par un "
          "`h1`, puis descend d'un niveau à la fois. Sauter un niveau est possible "
          "techniquement, mais brise la navigation assistée et brouille la structure "
          "logique."),
        table(["Élément", "Usage", "À éviter"],
              [["`h1`", "Titre du document, unique", "Plusieurs `h1` concurrents"],
               ["`h2`", "Grande section", "Utiliser `h2` pour un sous-titre de carte"],
               ["`h3`", "Sous-section", "Descendre à `h5` pour « faire plus petit »"],
               ["`p`", "Paragraphe de texte courant", "Empiler des `p` pour créer de l'espace"],
               ["`br`", "Retour à la ligne au sein d'un même paragraphe", "Simuler des paragraphes"],
               ["`hr`", "Séparation thématique entre sections", "Dessiner une ligne décorative"]],
              widths=[1.6, 4.6, 4.8], first_col_bold=True,
              caption="Titres, paragraphes et séparateurs"),
        p("La balise `br` est la plus mal utilisée du langage. Elle sert à l'intérieur "
          "d'un poème, d'une adresse postale ou d'un titre sur deux lignes — jamais à "
          "créer de l'espace vertical. Pour cela, il existe les marges CSS."),
        code("""<!-- Correct : une adresse postale -->
<address>
  12 rue des Lilas<br>
  75011 Paris<br>
  France
</address>

<!-- Incorrect : des paragraphes simulés -->
<p>Premier paragraphe<br><br></p>
<p>Deuxième paragraphe</p>""", "html", "`br` appartient au contenu, pas à la mise en page"),

        h(2, "Mise en valeur : sens ou apparence ?"),
        p("HTML distingue deux familles. Les éléments **sémantiques** expriment une "
          "intention : `strong` signale une importance, `em` une insistance. Les "
          "éléments **de présentation historique** — `b`, `i`, `u` — décrivent une "
          "apparence sans sens précis ; ils restent valides, mais doivent rester "
          "marginaux."),
        table(["Élément", "Sens", "Rendu par défaut", "Quand l'utiliser"],
              [["`strong`", "Importance forte", "Gras", "Avertissement, mot clé décisif"],
               ["`em`", "Insistance", "Italique", "Nuance de sens, accent d'intonation"],
               ["`b`", "Attention sans importance", "Gras", "Nom de produit dans une interface"],
               ["`i`", "Terme étranger, voix", "Italique", "Mot latin, pensée, nom d'œuvre"],
               ["`mark`", "Pertinence dans un contexte", "Fond jaune", "Résultat de recherche"],
               ["`small`", "Mention secondaire", "Plus petit", "Mentions légales, notes"],
               ["`u`", "Annotation non textuelle", "Souligné", "Faute signalée, nom propre chinois"]],
              widths=[1.5, 3.4, 2.6, 4.0], first_col_bold=True,
              caption="Sept éléments de mise en valeur et leur sens réel"),
        p("Un lecteur d'écran peut annoncer une emphase : « important : ... » ou "
          "« insiste : ... ». Cette information disparaît si vous utilisez une classe "
          "CSS pour obtenir du gras. Le sens doit être porté par le HTML, l'apparence "
          "par le CSS."),
        code("""<p>
  Le mot de passe doit contenir <strong>au moins douze caractères</strong>.
  Cette règle <em>n'est pas une recommandation</em> : elle est obligatoire.
</p>
<p>
  La formule E = mc<sup>2</sup> utilise l'<abbr title="exposant">exp.</abbr> 2.
  L'eau bout à 100 °C à pression atmosphérique.
</p>""", "html", "Emphase, exposant et abréviation dans un texte courant"),

        h(2, "Listes : trois structures distinctes"),
        p("Trois types de listes répondent à trois besoins. Les confondre est une "
          "erreur fréquente : une liste de définitions rendue avec des puces perd son "
          "sens, et une liste ordonnée sans numéros cache une séquence."),
        table(["Élément", "Structure", "Exemple d'usage"],
              [["`ul`", "Collection sans ordre", "Menus, avantages, ingrédients"],
               ["`ol`", "Séquence ordonnée", "Étapes, classement, instructions"],
               ["`dl`", "Termes et définitions", "Glossaire, spécifications, FAQ"]],
              widths=[1.4, 4.0, 5.6], first_col_bold=True,
              caption="Choisir le bon type de liste"),
        code("""<ul>
  <li>HTML</li>
  <li>CSS</li>
</ul>

<ol>
  <li>Ouvrir le terminal.</li>
  <li>Lancer le serveur local.</li>
  <li>Ouvrir la page dans le navigateur.</li>
</ol>

<dl>
  <dt>DOM</dt>
  <dd>Représentation arborescente du document.</dd>
  <dt>CSSOM</dt>
  <dd>Représentation des styles calculés.</dd>
</dl>""", "html", "Les trois listes, chacune avec sa sémantique"),
        p("Les listes s'imbriquent : une `ol` peut contenir une `ul` dans un `li`. "
          "En revanche, aucun autre élément ne doit être placé directement entre "
          "`ul` et `li` : le validateur le signale, et les lecteurs d'écran "
          "annoncent alors un nombre d'éléments erroné."),
        box("attention", "La navigation est une liste",
            "Un menu est une liste de liens. Utilisez `nav > ul > li > a` plutôt "
            "qu'une suite d'ancres séparées par des barres verticales. Les "
            "technologies d'assistance annoncent alors « liste de 6 éléments », ce "
            "qui aide à se repérer."),

        h(2, "Citations, code et données techniques"),
        p("Un texte professionnel cite ses sources, nomme ses fichiers et distingue "
          "le code du commentaire. HTML fournit des éléments dédiés, souvent ignorés "
          "au profit de simples italiques."),
        table(["Élément", "Contenu", "Note"],
              [["`blockquote`", "Citation longue, en bloc", "Attribut `cite` pour l'URL source"],
               ["`q`", "Citation courte, en ligne", "Les guillemets sont ajoutés par le navigateur"],
               ["`cite`", "Titre d'une œuvre", "Pas le nom de l'auteur"],
               ["`code`", "Fragment de code", "À combiner avec `pre` pour un bloc"],
               ["`pre`", "Texte préformaté", "Conserve espaces et retours à la ligne"],
               ["`kbd`", "Touche ou saisie clavier", "`Ctrl` + `S`"],
               ["`samp`", "Sortie d'un programme", "Message d'erreur"],
               ["`var`", "Variable mathématique ou de code", "`x`, `userId`"],
               ["`time`", "Date ou durée", "Attribut `datetime` normalisé"],
               ["`abbr`", "Abréviation", "Attribut `title` pour la forme complète"]],
              widths=[2.0, 4.2, 5.2], first_col_bold=True,
              caption="Dix éléments pour un texte technique précis"),
        code("""<p>Comme le rappelle la spécification,
  <q cite="https://html.spec.whatwg.org/">le langage HTML décrit la structure</q>.</p>

<blockquote cite="https://www.w3.org/TR/wcag21/">
  <p>Le contenu doit être perceptible, utilisable, compréhensible et robuste.</p>
</blockquote>

<p>Exécutez <kbd>npm run build</kbd> : la sortie affiche <samp>Build complete</samp>.</p>

<p>Le paramètre <var>timeout</var> vaut 30 secondes par défaut.</p>

<p>Publié le <time datetime="2026-10-19">19 octobre 2026</time>.</p>""", "html",
             "Citations, code et dates dans un texte éditorial"),

        h(2, "Caractères spéciaux et entités"),
        p("Trois caractères ont une signification particulière en HTML : `<` ouvre une "
          "balise, `>` la ferme, `&` introduit une entité. Pour les afficher "
          "littéralement, on utilise des entités nommées ou numériques."),
        table(["Caractère", "Entité", "Écriture"],
              [["<", "`&lt;`", "`&lt;div&gt;`"],
               [">", "`&gt;`", "`&gt;`"],
               ["&", "`&amp;`", "`&amp;`"],
               ["«", "`&laquo;`", "`&laquo;`"],
               ["»", "`&raquo;`", "`&raquo;`"],
               ["—", "`&mdash;`", "`&mdash;`"],
               ["espace insécable", "`&nbsp;`", "`12&nbsp;kg`"],
               ["©", "`&copy;`", "`&copy;`"]],
              widths=[2.6, 3.0, 4.4], caption="Les entités les plus courantes"),
        p("En UTF-8, la plupart des caractères accentués peuvent être saisis "
          "directement. Les entités restent utiles pour les caractères ambigus et "
          "pour l'espace insécable, qui empêche une coupure malencontreuse entre un "
          "nombre et son unité, ou avant les deux-points en français."),
        box("pratique", "Typographie française",
            items=["Espace insécable avant `:`, `;`, `!`, `?` et à l'intérieur des guillemets « ... ».",
                   "Tiret cadratin `—` pour l'incise, trait d'union pour les mots composés.",
                   "Points de suspension : trois points, pas six.",
                   "Les unités prennent une espace insécable : `12&nbsp;kg`, `20&nbsp;°C`."]),

        h(2, "Relire et justifier"),
        p("La relecture sémantique consiste à parcourir le document en se demandant, "
          "pour chaque élément : « pourquoi cette balise plutôt qu'une autre ? ». Si "
          "la réponse est « pour qu'elle ressemble à ceci », la balise est probablement "
          "mal choisie."),
        code("""<!-- Avant : une suite de div -->
<div class="title">Nos services</div>
<div class="item"><span class="num">1.</span> Audit</div>
<div class="item"><span class="num">2.</span> Conception</div>

<!-- Après : une structure qui se lit -->
<section aria-labelledby="services">
  <h2 id="services">Nos services</h2>
  <ol>
    <li>Audit</li>
    <li>Conception</li>
  </ol>
</section>""", "html", "La même page, avant et après la refonte sémantique"),
        p("La version de droite est plus courte, plus lisible, et n'a besoin d'aucune "
          "classe pour être comprise. Elle se met en forme avec deux sélecteurs au "
          "lieu de six."),
    ],
    "keypoints": [
        "Chaque fragment de texte a une nature ; HTML fournit une balise pour l'exprimer.",
        "La hiérarchie des titres est un plan, pas un jeu de tailles.",
        "`br` sert au contenu (poème, adresse), jamais à l'espacement.",
        "`strong` et `em` portent du sens ; `b` et `i` ne portent qu'une apparence.",
        "Trois listes : `ul`, `ol`, `dl` — chacune a un usage distinct.",
        "Citations, code, dates et abréviations ont des éléments dédiés.",
        "Un document se relit en justifiant chaque balise.",
    ],
    "bridge": "Le texte est structuré. Reste à le relier : les liens constituent "
              "l'architecture d'un site et la principale voie de navigation.",
    "exercises": [
        ex("Baliser une recette",
           "Voici une recette en texte brut. Structurez-la en HTML sémantique.",
           ["Titre « Tarte aux pommes », temps de préparation, liste des ingrédients.",
            "Étapes numérotées, note de conservation, astuce facultative.",
            "Ajoutez une abréviation et une durée balisée avec `time`."],
           [("code", """<article>
  <h1>Tarte aux pommes</h1>
  <p>Temps de préparation : <time datetime="PT25M">25 minutes</time>
     · Cuisson : <time datetime="PT40M">40 minutes</time></p>
  <h2>Ingrédients</h2>
  <ul>
    <li>3 pommes</li>
    <li>1 pâte brisée</li>
    <li>50 g de sucre</li>
  </ul>
  <h2>Préparation</h2>
  <ol>
    <li>Préchauffer le four à 180 °C.</li>
    <li>Étaler la pâte dans le moule.</li>
    <li>Disposer les pommes et saupoudrer de sucre.</li>
    <li>Enfourner 40 minutes.</li>
  </ol>
  <p><small>À conserver deux jours au réfrigérateur.</small></p>
</article>"""),
            "La recette est un contenu autonome : `article` convient. Les temps de "
            "préparation et de cuisson sont des durées, d'où l'usage de `time` avec "
            "une valeur ISO 8601 (`PT25M` pour 25 minutes).",
            "La note de conservation est secondaire : `small` est approprié. Une "
            "astuce facultative pourrait être placée dans un `aside` à l'intérieur de "
            "l'article, ce qui la distingue du déroulé principal."]),
        ex("Corriger une page truffée d'erreurs sémantiques",
           "Ce fragment contient six erreurs de sens. Identifiez-les et corrigez-les.",
           ["`<div class=\"h1\">Mon titre</div>`",
            "`<p>Première ligne<br><br>Deuxième paragraphe</p>`",
            "`<b>Avertissement :</b> ne pas supprimer ce fichier.`</p>`",
            "`<i>Le Petit Prince</i> est un livre de <i>Saint-Exupéry</i>.`</p>`",
            "`<ul><li>Étape 1</li><li>Étape 2</li></ul>` pour une procédure",
            "`<p>Prix : 12 kg</p>` sans espace insécable"],
           ["Un `div` ne peut pas remplacer un titre : la page perd son plan.",
            "`<br><br>` simule un paragraphe ; il faut deux `p`.",
            "`b` ne signale pas une importance ; `strong` le fait.",
            "Le titre d'une œuvre se balise `cite`, le nom de l'auteur reste en texte "
            "simple (`Saint-Exupéry` n'est pas une œuvre).",
            "Une procédure est ordonnée : `ol`.",
            "« 12 kg » doit rester insécable : `12&nbsp;kg`."],
           level="Diagnostic"),
        ex("Rédiger une fiche technique",
           "Créez la fiche d'un produit logiciel : nom, version, prérequis, "
           "installation, avertissement.",
           ["Utilisez une liste de définitions pour les caractéristiques.",
            "Placez la commande d'installation dans un bloc de code.",
            "Signalez un avertissement de sécurité avec l'élément approprié."],
           [("code", """<article>
  <h1>Analyseur de journaux 2.4</h1>
  <dl>
    <dt>Version</dt><dd>2.4.1</dd>
    <dt>Licence</dt><dd>MIT</dd>
    <dt>Prérequis</dt><dd>Python 3.11 ou ultérieur</dd>
  </dl>
  <h2>Installation</h2>
  <pre><code>python3 -m pip install journalier==2.4.1</code></pre>
  <p><strong>Attention :</strong> la commande <code>journalier purge</code>
     supprime définitivement les archives de plus de trente jours.</p>
</article>"""),
            "La liste de définitions associe chaque caractéristique à sa valeur, ce "
            "qui est plus précis qu'une liste à puces.",
            "Le bloc `pre > code` conserve la mise en forme et signale la nature du "
            "contenu. Un lecteur d'écran peut alors annoncer « code ».",
            "L'avertissement utilise `strong` parce qu'il s'agit d'une information "
            "dont l'ignorance a des conséquences graves : c'est du sens, non du gras "
            "décoratif."]),
    ],
    "quiz": [
        quiz("Quelle balise crée un nouveau paragraphe ?",
             ["`<br>`", "`<p>`", "`<div>`", "`<span>`"],
             1,
             "`p` délimite un paragraphe. `br` ne fait qu'un retour à la ligne dans "
             "le même paragraphe ; `div` et `span` sont des conteneurs génériques."),
        quiz("Quelle différence sépare `strong` de `b` ?",
             ["Aucune, les deux sont identiques",
              "`strong` exprime une importance sémantique, `b` une mise en évidence visuelle",
              "`b` est obsolète",
              "`strong` ne peut pas être mis en forme"],
             1,
             "`strong` porte une information d'importance exploitée par les "
             "technologies d'assistance ; `b` attire l'attention sans plus de sens."),
        quiz("Quelle liste utiliser pour une recette étape par étape ?",
             ["`ul`", "`ol`", "`dl`", "`menu`"],
             1,
             "Les étapes ont un ordre : `ol`. `dl` sert aux couples terme/définition, "
             "`ul` aux collections sans ordre."),
        quiz("Comment afficher littéralement `<div>` dans une page ?",
             ["`<div>`", "`&lt;div&gt;`", "`<code><div></code>`", "`\\<div\\>`"],
             1,
             "Les chevrons doivent être échappés en entités : `&lt;` et `&gt;`. "
             "Sinon le navigateur interprète une balise au lieu d'afficher le texte."),
        quiz("Quel élément balise le titre d'une œuvre ?",
             ["`i`", "`cite`", "`q`", "`em`"],
             1,
             "`cite` identifie le titre d'une œuvre. `i` est une présentation, `q` "
             "une citation courte, `em` une insistance."),
    ],
}
