from bookkit.dsl import (box, code, defn, ex, fig, h, ol, p, quiz, table, ul)

CH = {
    "title": "Images, vidéos et audio",
    "subtitle": "Un média est lourd, lent et souvent invisible pour qui ne le voit "
                "pas. Le traiter correctement est un choix de qualité.",
    "duration": "2 h 30",
    "level": "Débutant",
    "prereq": "chapitre 5",
    "objectives": [
        "Choisir un format d'image adapté à chaque usage.",
        "Écrire un texte alternatif utile, ni absent ni décoratif.",
        "Servir des images adaptées à la taille et à la densité d'écran.",
        "Intégrer vidéos et audio avec sous-titres et contrôles.",
        "Réduire le poids sans dégrader la perception de qualité.",
    ],
    "blocks": [
        h(2, "Choisir un format"),
        p("Le format d'image détermine le poids, la netteté et la transparence. Un "
          "mauvais choix coûte des mégaoctets, donc des secondes, donc des visiteurs."),
        table(["Format", "Type", "Transparence", "Usage recommandé"],
              [["JPEG", "Raster, avec pertes", "Non", "Photos, dégradés"],
               ["PNG", "Raster, sans pertes", "Oui", "Captures, logos simples"],
               ["WebP", "Raster, avec ou sans pertes", "Oui", "Format par défaut du Web moderne"],
               ["AVIF", "Raster, très efficace", "Oui", "Photos, si le support est suffisant"],
               ["SVG", "Vectoriel", "Oui", "Icônes, logos, schémas"],
               ["GIF", "Raster animé", "Oui (1 bit)", "À éviter : préférer MP4 ou WebM"]],
              widths=[1.6, 3.6, 2.0, 4.2], first_col_bold=True,
              caption="Six formats d'image et leur domaine d'élection"),
        p("La règle pratique : **photographie → WebP ou AVIF**, **logo et icône → SVG**, "
          "**capture d'interface → WebP ou PNG**. Le JPEG reste un repli universel, "
          "mais il est désormais dépassé en efficacité."),
        defn("Image raster", "Image composée d'une grille de pixels. Elle perd en "
                             "netteté lorsqu'on l'agrandit."),
        defn("Image vectorielle", "Image décrite par des formes mathématiques. Elle "
                                  "reste nette à toute taille et pèse souvent moins de "
                                  "dix kilo-octets."),
        fig("compare", "Raster ou vectoriel ?",
            ("RASTER (JPEG, WebP)", ["Photo, texture, dégradé", "Poids lié aux pixels",
                                     "Flou à l'agrandissement"],
             "VECTORIEL (SVG)", ["Logo, icône, schéma", "Poids lié à la complexité",
                                 "Nette à toute taille"]),
            height=200),

        h(2, "La balise img et son texte alternatif"),
        p("`img` est une balise orpheline : elle n'a pas de contenu, donc pas de "
          "balise fermante. Deux attributs sont indispensables : `src` et `alt`."),
        code("""<img src="images/atelier.webp"
     alt="Trois personnes devant un tableau blanc couvert de schémas"
     width="1200" height="800"
     loading="lazy" decoding="async">""", "html", "Une image correctement déclarée"),
        p("L'attribut `alt` n'est pas une décoration : c'est **le contenu de l'image "
          "pour qui ne la voit pas**. Il remplit trois fonctions : lu par les "
          "lecteurs d'écran, affiché si l'image ne charge pas, indexé par les moteurs "
          "de recherche."),
        table(["Situation", "Valeur de `alt`", "Exemple"],
              [["Image informative", "Description factuelle", "« Graphique : +18 % de visites en mars »"],
               ["Image décorative", "Chaîne vide", "`alt=\"\"`"],
               ["Image-lien", "Décrit la destination", "« Retour à l'accueil »"],
               ["Image complexe", "Résumé court + description longue", "Voir ci-dessous"],
               ["Logo accompagné du nom", "Chaîne vide", "Le texte voisin suffit"]],
              widths=[2.8, 4.2, 4.6], first_col_bold=True,
              caption="Cinq situations, cinq textes alternatifs"),
        box("attention", "Les mauvais `alt`",
            items=["`alt=\"image\"`, `alt=\"photo\"` : n'apportent aucune information.",
                   "Recopier le nom du fichier : `alt=\"IMG_2043.jpg\"`.",
                   "Un `alt` identique pour toutes les images d'une galerie.",
                   "Oublier `alt` sur une image-lien : le lien devient sans nom."]),
        p("Pour un graphique complexe, l'`alt` donne la conclusion et une description "
          "longue — tableau de données, paragraphe — porte le détail :"),
        code("""<figure>
  <img src="graphique-ventes.svg"
       alt="Ventes trimestrielles : progression de 12 % entre 2025 et 2026."
       width="800" height="450">
  <figcaption>Ventes 2025-2026 (source : service commercial).</figcaption>
</figure>

<details>
  <summary>Voir les données du graphique</summary>
  <table>...</table>
</details>""", "html", "Une image complexe, résumée puis détaillée"),

        h(2, "Dimensions, réserve d'espace et décalage de mise en page"),
        p("Indiquer `width` et `height` permet au navigateur de réserver l'espace "
          "avant le chargement. Sans ces attributs, le contenu saute au moment où "
          "l'image arrive : c'est le **décalage cumulatif de mise en page** (CLS), un "
          "des indicateurs de qualité d'expérience mesurés par Google."),
        fig("flow", "Sans dimensions, la page saute",
            ["Le texte s'affiche, l'image n'est pas chargée",
             "Le navigateur ignore ses dimensions",
             "L'image arrive et pousse le contenu vers le bas",
             "L'utilisateur perd sa position de lecture"],
            height=245),
        code("""/* L'image s'adapte sans déformer et sans dépasser son conteneur */
img {
  max-width: 100%;
  height: auto;
  aspect-ratio: attr(width) / attr(height);
}""", "css", "Un redimensionnement sûr"),
        p("Les attributs `width` et `height` expriment des proportions, pas une taille "
          "finale imposée en CSS. Les écrire en pixels d'origine permet au navigateur "
          "de calculer le rapport et de réserver la bonne hauteur, quelle que soit la "
          "largeur finale."),

        h(2, "Réponses adaptatives : srcset et picture"),
        p("Un téléphone n'a pas besoin d'une image de 2400 pixels. `srcset` indique "
          "plusieurs versions et laisse le navigateur choisir selon la largeur "
          "d'affichage et la densité de l'écran."),
        code("""<img src="images/hero-800.webp"
     srcset="images/hero-480.webp   480w,
             images/hero-800.webp   800w,
             images/hero-1200.webp 1200w,
             images/hero-1600.webp 1600w"
     sizes="(max-width: 600px) 100vw,
            (max-width: 1200px) 50vw,
            800px"
     alt="Atelier de formation, vue d'ensemble"
     width="1600" height="900" loading="lazy">""", "html",
             "Quatre versions, une seule balise : le navigateur choisit"),
        p("`sizes` décrit la largeur d'affichage prévue ; le navigateur croise cette "
          "information avec la densité de l'écran et choisit le fichier le plus léger "
          "qui reste net. Aucun JavaScript n'est nécessaire."),
        p("L'élément `picture` va plus loin : il permet de servir un format différent "
          "selon le support, ou une image recadrée différemment selon l'orientation."),
        code("""<picture>
  <source type="image/avif" srcset="hero.avif">
  <source type="image/webp" srcset="hero.webp">
  <img src="hero.jpg" alt="Atelier de formation, vue d'ensemble"
       width="1600" height="900">
</picture>

<picture>
  <source media="(min-width: 900px)" srcset="paysage-large.webp">
  <img src="paysage-carre.webp" alt="Vallée au lever du jour">
</picture>""", "html", "Deux usages de `picture` : format et cadrage"),
        code("""<link rel="preload" as="image" href="hero.avif"
      imagesrcset="hero-800.avif 800w, hero-1600.avif 1600w"
      imagesizes="100vw">""", "html", "Précharger l'image principale sans bloquer"),
        box("pratique", "Le chargement paresseux",
            "`loading=\"lazy\"` retarde le chargement des images situées hors écran. "
            "Ne l'appliquez jamais à l'image principale : elle retarderait le "
            "rendu. Sur une page d'articles, en revanche, c'est un gain immédiat."),

        h(2, "Vidéo et audio"),
        p("Les éléments `video` et `audio` remplacent les plugins depuis HTML5. Ils "
          "acceptent plusieurs sources ; le navigateur choisit la première qu'il "
          "sait lire. Sans sous-titres, une vidéo reste inaccessible à une partie du "
          "public — et souvent illisible en environnement bruyant."),
        code("""<figure>
  <video controls width="960" height="540" poster="apercu.webp"
         preload="metadata" playsinline>
    <source src="demo.webm" type="video/webm">
    <source src="demo.mp4"  type="video/mp4">
    <track kind="subtitles" src="sous-titres/fr.vtt"
           srclang="fr" label="Français" default>
    <p>Votre navigateur ne prend pas en charge la vidéo.
       <a href="demo.mp4">Télécharger la vidéo</a>.</p>
  </video>
  <figcaption>Démonstration de l'éditeur de code (2 min 14).</figcaption>
</figure>""", "html", "Une vidéo accessible, avec repli et sous-titres"),
        table(["Attribut", "Effet", "Recommandation"],
              [["`controls`", "Affiche les commandes natives", "Toujours présent"],
               ["`preload`", "Quantité de données téléchargées d'avance", "`metadata` par défaut"],
               ["`poster`", "Image affichée avant lecture", "Une image légère"],
               ["`playsinline`", "Lecture dans la page sur mobile", "Indispensable"],
               ["`muted`", "Démarre sans son", "Requis pour l'autoplay"],
               ["`loop`", "Lecture en boucle", "Décoration uniquement"],
               ["`track`", "Sous-titres, légendes, descriptions", "Au moins `kind=subtitles`"]],
              widths=[2.4, 5.0, 4.2], first_col_bold=True,
              caption="Sept attributs des médias et leur usage"),
        p("Une vidéo décorative en lecture automatique doit être silencieuse, courte "
          "et légère ; elle doit aussi pouvoir être mise en pause. Une vidéo de "
          "contenu doit fournir des sous-titres synchronisés au format WebVTT."),
        code("""WEBVTT

00:00:00.000 --> 00:00:03.200
Bienvenue dans ce tutoriel HTML.

00:00:03.200 --> 00:00:07.500
Commencez par créer un fichier index.html.""", "text",
             "Un fichier de sous-titres WebVTT minimal"),

        h(2, "Optimiser sans dégrader"),
        p("Optimiser une image, c'est réduire son poids jusqu'au seuil où l'œil ne "
          "perçoit plus de différence. Quatre leviers, dans l'ordre d'efficacité : "
          "dimensions correctes, format moderne, compression réglée, chargement "
          "différé."),
        table(["Levier", "Gain typique", "Outil"],
              [["Redimensionner à la taille d'affichage", "50 à 80 %", "Sharp, ImageMagick"],
               ["Passer au WebP ou AVIF", "25 à 50 %", "cwebp, avifenc, Squoosh"],
               ["Régler la qualité à 75-85", "10 à 30 %", "Squoosh, sharp"],
               ["Charger en différé", "Variable", "`loading=\"lazy\"`"],
               ["Servir via un CDN d'images", "Variable", "Cloudinary, imgix, Netlify"]],
              widths=[4.2, 2.8, 4.4], caption="Cinq leviers d'optimisation, du plus au moins rentable"),
        code("""# Convertir un dossier d'images en WebP, qualité 80
$ for f in images/*.{jpg,png}; do
    cwebp -q 80 "$f" -o "${f%.*}.webp"
  done

# Vérifier les gains
$ du -sh images/""", "bash", "Une conversion par lot en ligne de commande"),
        box("methode", "Vérifier avant de publier",
            items=["Chaque image a-t-elle un `alt` justifié ?",
                   "Chaque image a-t-elle `width` et `height` ?",
                   "Les images hors écran sont-elles en `lazy` ?",
                   "Les vidéos ont-elles des sous-titres ?",
                   "Le poids total de la page reste-t-il sous 1,5 Mo ?"]),
    ],
    "keypoints": [
        "Le format se choisit selon l'usage : photo, logo, capture, animation.",
        "`alt` décrit le contenu, jamais le fichier ni le format.",
        "Une image décorative a un `alt` vide, pas un `alt` absent.",
        "`width` et `height` réservent l'espace et évitent les sauts de page.",
        "`srcset` et `picture` évitent d'envoyer 2400 pixels à un téléphone.",
        "Une vidéo sans sous-titres exclut une partie du public.",
        "Optimiser, c'est réduire le poids sous le seuil de perception.",
    ],
    "bridge": "Les médias sont en place. Le chapitre suivant traite les données "
              "structurées : tableaux, et tout ce qui fait la différence entre un "
              "tableau de données et une grille dessinée.",
    "exercises": [
        ex("Rendre une galerie accessible",
           "Voici une galerie de trois images, sans texte alternatif correct.",
           ["Rédigez un `alt` adapté à chaque image.",
            "Ajoutez les dimensions et le chargement différé.",
            "Enveloppez chaque image dans une `figure` avec sa légende."],
           [("code", """<figure>
  <img src="images/atelier-1.webp"
       alt="Groupe de six apprenants devant un écran de code."
       width="1200" height="800" loading="lazy">
  <figcaption>Première séance : découverte de l'éditeur.</figcaption>
</figure>
<figure>
  <img src="images/atelier-2.webp"
       alt="Schéma du modèle de boîte dessiné au tableau."
       width="1200" height="800" loading="lazy">
  <figcaption>Deuxième séance : le modèle de boîte.</figcaption>
</figure>"""),
            "Un bon `alt` décrit ce qui est utile à comprendre : le nombre de "
            "personnes, l'action, le sujet. Il évite les détails décoratifs et les "
            "formules creuses.",
            "La légende (`figcaption`) apporte un contexte différent : la date, le "
            "lieu, l'étape du cours. Elle ne remplace pas l'`alt`, elle le complète."]),
        ex("Construire un média adaptatif",
           "Vous disposez d'une image de 1600 × 900 pixels utilisée en bandeau.",
           ["Générez trois tailles et deux formats.",
            "Écrivez la balise `img` avec `srcset` et `sizes`.",
            "Expliquez quel fichier sera chargé sur un téléphone de 390 pixels de large."],
           ["Avec `cwebp -q 80 -resize 800 0 hero.jpg -o hero-800.webp`, on produit "
            "des variantes de 480, 800 et 1600 pixels de large en WebP et en JPEG de "
            "repli.",
            "`srcset` liste les largeurs en `w` ; `sizes` indique que sur un écran de "
            "moins de 600 pixels, l'image occupe 100 % de la largeur.",
            "Sur un téléphone de 390 pixels, le navigateur choisit la variante de "
            "480 pixels (la plus proche au-dessus de la largeur nécessaire). Avec un "
            "écran à densité double, il peut choisir 800 pixels pour rester net."]),
        ex("Auditer une page média",
           "Choisissez une page d'accueil riche en images.",
           ["Relevez le poids total des images et la plus lourde.",
            "Vérifiez la présence des attributs `alt`, `width`, `height`, `loading`.",
            "Proposez trois corrections chiffrées."],
           ["Le panneau Réseau, filtré sur « Img », donne la taille transférée de "
            "chaque image et le total. Une page non optimisée dépasse souvent 3 Mo.",
            "Les manques les plus fréquents : `alt` absents sur les images "
            "décoratives (ils devraient être vides), dimensions absentes sur les "
            "vignettes, `lazy` oublié sur les images situées en bas de page.",
            "Trois corrections typiques : conversion en WebP (-35 %), "
            "redimensionnement des vignettes (-60 % sur ces fichiers), ajout de "
            "`loading=\"lazy\"` sur les vingt dernières images (suppression du "
            "téléchargement initial)."],
           level="Analyse"),
    ],
    "quiz": [
        quiz("Quel format privilégier pour un logo ?",
             ["JPEG", "PNG", "SVG", "GIF"],
             2,
             "Un logo est un dessin de formes simples : le SVG reste net à toute "
             "taille et pèse généralement moins qu'un PNG équivalent."),
        quiz("Que doit contenir l'attribut `alt` d'une image purement décorative ?",
             ["Une description détaillée", "Une chaîne vide", "Le nom du fichier", "Rien : l'attribut doit être absent"],
             1,
             "`alt=\"\"` indique aux technologies d'assistance d'ignorer l'image. "
             "L'absence d'attribut, au contraire, laisse le lecteur d'écran annoncer "
             "le nom du fichier."),
        quiz("À quoi servent les attributs `width` et `height` sur une image ?",
             ["À imposer la taille finale en pixels",
              "À réserver l'espace et éviter les décalages de mise en page",
              "À accélérer le téléchargement",
              "À activer le chargement différé"],
             1,
             "Le navigateur en déduit le rapport d'aspect et réserve la place avant "
             "le chargement ; le CSS peut ensuite adapter la taille réelle."),
        quiz("Quel attribut retarde le chargement d'une image hors écran ?",
             ["`defer`", "`async`", "`loading=\"lazy\"`", "`preload`"],
             2,
             "`loading=\"lazy\"` est l'attribut natif de chargement différé des images "
             "et des iframes."),
        quiz("Pourquoi les sous-titres d'une vidéo sont-ils indispensables ?",
             ["Pour améliorer le référencement uniquement",
              "Pour rendre la vidéo accessible aux personnes sourdes et en environnement bruyant",
              "Pour réduire le poids de la vidéo",
              "Pour empêcher le téléchargement"],
             1,
             "Les sous-titres sont une exigence d'accessibilité et un confort "
             "d'usage : de nombreuses personnes regardent sans son."),
    ],
}
