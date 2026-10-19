"""Pages liminaires du volume : titre, mentions, mode d'emploi, parcours."""
from __future__ import annotations

from bookkit.dsl import box, h, ol, p, pb, table, ul


def _title_page(logo: str) -> list[dict]:
    return [
        {"t": "logo", "path": logo, "width": 3.2, "align": "left"},
        p("BIBLIOTHÈQUE TECHNIQUE · ESPRITROPIC COMMUNITY", "small"),
        {"t": "vspace", "h": 40},
        {"t": "bigtitle", "text": "Développement web\n& DevOps"},
        {"t": "vspace", "h": 10},
        {"t": "rule"},
        p("Manuel complet : HTML5, CSS3, JavaScript, Linux, conteneurs, cloud et fiabilité",
          "lead"),
        p("Deux cours autonomes, quatre-vingt-treize chapitres, des centaines d'exercices "
          "corrigés, de schémas et de tableaux de synthèse."),
        {"t": "vspace", "h": 70},
        table(["Volume", "Contenu", "Public"],
              [["Cours 1", "Développement web front-end — 45 chapitres",
                "Débutant à intermédiaire"],
               ["Cours 2", "DevOps, cloud et fiabilité — 48 chapitres",
                "Intermédiaire à confirmé"]],
              widths=[1.2, 4.0, 2.2], first_col_bold=True),
        {"t": "vspace", "h": 60},
        p("**IcaBot**", "body"),
        {"t": "smallcaps", "text": "Agent d'ESPRITROPIC COMMUNITY"},
        p("Édition 2026 · Volume unique · espritropic.rf.gd", "small"),
        pb(),
    ]


def _credits() -> list[dict]:
    return [
        h(1, "Mentions légales et crédits"),
        p("**Éditeur.** ESPRITROPIC COMMUNITY — YKABAUTH. Site : https://espritropic.rf.gd"),
        p("**Auteur.** IcaBot, agent d'ESPRITROPIC COMMUNITY. Direction éditoriale : "
          "YKABAUTH."),
        p("**Collection.** Bibliothèque technique Espritropic."),
        p("**Édition.** Première édition, 2026. Volume unique, format A4."),
        p("**Texte.** Les deux cours ont été rédigés spécifiquement pour cette édition "
          "à partir des ressources documentaires déposées par l'éditeur. La graphie "
          "définitive de la signature « IcaBot » reste modifiable par l'éditeur."),
        p("**ISBN et dépôt légal.** Aucun numéro ISBN ni déclaration de dépôt légal "
          "n'ont été fournis avec les ressources éditoriales au moment de la "
          "fabrication de ce volume. Ces mentions doivent être complétées par "
          "l'éditeur avant toute diffusion commerciale."),
        p("**Licence d'utilisation.** Ce volume est destiné aux lecteurs de la "
          "collection Espritropic. Toute reproduction intégrale ou partielle à des "
          "fins commerciales est soumise à l'autorisation écrite de l'éditeur. "
          "Les extraits courts accompagnés de la mention de source sont autorisés "
          "à des fins pédagogiques."),
        h(3, "Crédits documentaires"),
        p("Ce volume s'appuie sur deux ressources fournies par l'éditeur, "
          "explicitement citées ici."),
        p("**1. Feuille de route DevOps.** Infographie « DevOps Roadmap: Learn to become "
          "a DevOps Engineer or SRE », publiée par roadmap.sh, fournie au format PDF "
          "et utilisée comme plan du cours 2. Les intitulés de compétences de la "
          "feuille de route sont repris ; le texte pédagogique, les exemples, les "
          "exercices et les corrigés sont originaux. roadmap.sh est un projet "
          "communautaire indépendant, sans lien avec ESPRITROPIC COMMUNITY."),
        p("**2. Référence HTML5 et CSS3.** Ouvrage « Apprenez à créer votre site web "
          "avec HTML5 et CSS3 » de Mathieu Nebra (M@teo21), diffusé par le Site du "
          "Zéro / Sup'Internet sous licence Creative Commons, fourni au format PDF et "
          "utilisé comme référence de progression et de structuration du cours 1. "
          "Aucun passage n'est reproduit : la progression a été reconstruite, "
          "augmentée et actualisée (HTML5 vivant, CSS moderne, JavaScript)."),
        p("**3. Identité visuelle.** Logo « <R> » d'Espritropic Community, fourni en "
          "deux variantes monochromes (noir et blanc) sur fond transparent."),
        p("**4. Typographie.** Times New Roman, Arial et Courier New (Microsoft) pour "
          "la composition ; polices métriquement compatibles recommandées en cas "
          "d'absence : Liberation Serif, Liberation Sans et Liberation Mono."),
        h(3, "Marques et avertissements"),
        p("Les noms de produits cités (HTML, CSS, JavaScript, Linux, Docker, Kubernetes, "
          "Terraform, Ansible, AWS, Azure, Google Cloud, GitHub, GitLab, etc.) sont des "
          "marques ou des noms commerciaux de leurs détenteurs respectifs. Ils sont "
          "utilisés ici à des fins d'identification et de description technique, sans "
          "affiliation ni parrainage."),
        p("Les commandes, extraits de configuration et procédures ont été rédigés pour "
          "être exacts au moment de la rédaction. Les logiciels évoluent : vérifiez "
          "toujours la documentation officielle de la version que vous utilisez. "
          "Les manipulations système et cloud peuvent entraîner des coûts ou des "
          "interruptions de service ; testez en environnement isolé."),
        pb(),
    ]


def _about() -> list[dict]:
    return [
        h(1, "À propos de cette édition"),
        p("Ce volume rassemble, dans un seul fichier Word, l'intégralité des cours "
          "issus des ressources documentaires de l'éditeur. Il ne s'agit pas d'un "
          "recueil d'articles ni d'une compilation de notes : chaque chapitre a été "
          "conçu comme une séquence pédagogique complète, avec objectifs, cours, "
          "exemples, exercices et corrigés.", "lead"),
        h(3, "Deux domaines, un volume"),
        p("Les documents fournis décrivent deux parcours distincts, qui ne se "
          "recouvrent pas. D'un côté, un ouvrage de référence consacré à la création "
          "de sites web avec HTML5 et CSS3, qui couvre les fondations du front-end. "
          "De l'autre, une feuille de route DevOps qui recense les compétences "
          "attendues d'un ingénieur DevOps ou d'un site reliability engineer (SRE)."),
        p("Réunir ces deux parcours dans un même volume répond à une réalité "
          "professionnelle simple : un développeur front-end travaille aujourd'hui "
          "avec Git, des pipelines, des environnements conteneurisés et des "
          "plateformes cloud. À l'inverse, un ingénieur DevOps doit comprendre le "
          "cycle de vie d'une application web, ses contraintes de performance et "
          "d'accessibilité. Les deux cours restent néanmoins autonomes : chacun "
          "possède son introduction, sa progression, ses exercices et son projet "
          "final."),
        h(3, "Comment le plan a été construit"),
        p("Le plan du cours 1 suit la progression du document de référence "
          "(bases de HTML5, mise en forme CSS, mise en page, fonctionnalités "
          "évoluées, annexes), en l'actualisant : HTML5 vivant, CSS Grid, Flexbox, "
          "unités fluides, container queries, accessibilité, JavaScript moderne, "
          "performance, sécurité front-end et déploiement."),
        p("Le plan du cours 2 reprend l'intégralité des quinze domaines de la "
          "feuille de route DevOps : langages, systèmes d'exploitation, terminal, "
          "gestion de versions, serveurs et réseaux, conteneurs, fournisseurs cloud, "
          "serverless, provisionnement, gestion de configuration, CI/CD, secrets, "
          "supervision, orchestration, GitOps, service mesh et patrons de conception "
          "cloud. Chaque nœud de la feuille de route est traité dans au moins une "
          "section d'un chapitre."),
        h(3, "Public et prérequis"),
        p("Le volume s'adresse à trois publics : les débutants complets qui suivent "
          "le cours 1 dans l'ordre ; les développeurs autodidactes qui souhaitent "
          "consolider leurs bases et combler leurs angles morts ; les "
          "professionnels de l'exploitation et du développement qui veulent relier "
          "les deux mondes. Aucun diplôme n'est requis. Une familiarité avec "
          "l'ordinateur, les fichiers et un navigateur suffit pour commencer."),
        h(3, "Ce que ce volume n'est pas"),
        p("Ce volume n'est ni une documentation de référence exhaustive des langages, "
          "ni un catalogue de recettes. Il privilégie la compréhension durable : "
          "chaque notion est expliquée, illustrée, mise en pratique, puis vérifiée. "
          "Les API changent ; les principes restent. C'est pourquoi les chapitres "
          "insistent sur les modèles mentaux (comment un navigateur rend une page, "
          "comment un paquet circule, comment un conteneur isole un processus) "
          "autant que sur les commandes."),
        h(3, "Fabrication du volume"),
        p("Le volume a été composé avec des styles natifs Word : chaque niveau de "
          "titre, chaque légende, chaque bloc de code et chaque tableau utilise un "
          "style nommé. La table des matières générale est un champ automatique : "
          "elle peut être mise à jour par le lecteur (clic droit sur le sommaire, "
          "« Mettre à jour les champs »). La pagination est continue de la "
          "couverture à la dernière annexe."),
        p("Les schémas sont des illustrations originales produites pour cette "
          "édition. Les extraits de code sont volontairement courts et commentés : "
          "ils servent de modèle, pas de bibliothèque."),
        pb(),
    ]


def _howto() -> list[dict]:
    return [
        h(1, "Comment utiliser ce document"),
        p("Ce document est un manuel, pas un roman. Il se lit avec un clavier, un "
          "éditeur de texte, un terminal et un navigateur ouverts. Les chapitres "
          "sont conçus pour être travaillés, pas seulement lus.", "lead"),
        h(3, "Organisation générale"),
        p("Le volume comporte quatre niveaux de structuration, identifiables par "
          "leur style de titre :"),
        ul("**Cours** — deux ensembles autonomes, présentés chacun par une page "
           "d'ouverture, un mode d'emploi et un sommaire détaillé.",
           "**Partie** — un regroupement thématique de cinq à huit chapitres, "
           "introduit par une page de partie.",
           "**Chapitre** — une séquence complète : objectifs, cours, exemples, "
           "exercices corrigés, quiz et synthèse.",
           "**Section et sous-section** — des unités de lecture de deux à six pages, "
           "numérotées (par exemple 12.3 ou 12.3.2)."),
        h(3, "Les rubriques récurrentes"),
        p("Chaque chapitre suit le même déroulé, ce qui permet de s'orienter "
          "rapidement dans un volume de cette taille."),
        table(["Rubrique", "Fonction", "Quand l'utiliser"],
              [["À l'issue de ce chapitre", "Objectifs mesurables", "Avant la lecture, pour cadrer l'effort"],
               ["Cours", "Explications, schémas, tableaux, exemples de code", "Lecture active, éditeur ouvert"],
               ["Encadrés", "Définitions, bonnes pratiques, pièges, notes", "Pendant la lecture"],
               ["Exercices d'application", "Mise en pratique progressive", "Après chaque section ou en fin de chapitre"],
               ["Corrigés détaillés", "Solution commentée et justifiée", "Après avoir cherché soi-même"],
               ["Quiz de vérification", "Contrôle des acquis", "Sans revenir au texte"],
               ["L'essentiel du chapitre", "Synthèse en cinq à huit points", "Avant de passer au chapitre suivant"]],
              widths=[2.2, 4.2, 3.4], first_col_bold=True),
        h(3, "Conventions typographiques"),
        table(["Convention", "Signification", "Exemple"],
              [["**Gras**", "Terme défini, notion clé, libellé d'interface", "**flux de mise en page**"],
               ["*Italique*", "Nuance, mot étranger, titre d'ouvrage", "*responsive design*"],
               ["`Police à chasse fixe`", "Élément de code, balise, propriété, commande", "`display: grid`"],
               ["Bloc grisé", "Extrait de code exécutable ou configuration", "voir listing 3.1"],
               ["Cadre ambre", "Objectifs, méthode, point de vigilance", "encadré ci-dessus"],
               ["Cadre vert", "Bonne pratique validée", "encadré « À retenir »"],
               ["Cadre rouge", "Erreur fréquente, risque de sécurité ou de perte de données", "encadré « Attention »"]],
              widths=[2.6, 5.2, 3.2], first_col_bold=True),
        h(3, "Travailler avec le fichier Word"),
        p("Le document est entièrement stylé. Pour modifier l'apparence de tous les "
          "titres d'un niveau, modifiez le style correspondant (onglet Accueil, "
          "galerie Styles, clic droit sur « Titre 1 », « Modifier ») : la table des "
          "matières et la navigation suivent automatiquement."),
        p("Pour régénérer la table des matières après une modification : cliquez "
          "dans le sommaire général, puis sur « Mettre à jour la table » ou "
          "appuyez sur F9. Choisissez « Mettre à jour toute la table » pour "
          "recalculer les numéros de page."),
        p("Le volet de navigation (Affichage, Volet de navigation) permet de circuler "
          "entre cours, parties, chapitres et sections. La recherche (Ctrl+F) "
          "fonctionne sur l'ensemble du volume."),
        h(3, "Environnement recommandé"),
        table(["Usage", "Recommandation"],
              [["Lecture", "Microsoft Word 2016 ou ultérieur, écran 13 pouces minimum"],
               ["Écriture de code", "Visual Studio Code, avec les extensions HTML, CSS et JavaScript"],
               ["Navigation", "Chrome, Firefox ou Edge, version à jour"],
               ["Terminal (cours 2)", "Bash sous Linux, macOS ou WSL sous Windows"],
               ["Machines virtuelles", "4 Go de RAM minimum, 20 Go d'espace disque libre"]],
              widths=[3.0, 6.0], first_col_bold=True),
        box("attention", "Sécurité et sauvegarde",
            "Les commandes du cours 2 modifient des systèmes. Avant toute manipulation "
            "sur une machine personnelle, sauvegardez vos données et travaillez dans "
            "une machine virtuelle ou un conteneur jetable. Ne copiez jamais une "
            "commande de suppression ou de réinitialisation sans en comprendre "
            "l'effet."),
        pb(),
    ]


def _plan(course_info: list[dict]) -> list[dict]:
    blocks = [
        h(1, "Plan de la collection"),
        p("Le volume contient deux cours complets. Le tableau ci-dessous en donne "
          "la structure, le volume de chapitres et le niveau visé.", "lead"),
    ]
    rows = []
    for c in course_info:
        rows.append([c["label"], c["title"], str(len(c["parts"])), str(c["chapters"]),
                     c["level"]])
    blocks.append(table(["Cours", "Intitulé", "Parties", "Chapitres", "Niveau"],
                        rows, widths=[1.0, 4.6, 1.1, 1.3, 1.9], first_col_bold=True))
    for c in course_info:
        blocks.append(h(3, c["title"]))
        blocks.append(p(c["short"]))
        rows = [[part["label"], part["title"], str(len(part["chapters"]))]
                for part in c["parts"]]
        blocks.append(table(["Partie", "Intitulé", "Chapitres"], rows,
                            widths=[1.2, 6.3, 1.5], first_col_bold=True))
    blocks.append(box("pratique", "Autonomie des cours",
                      "Les deux cours peuvent être lus séparément. Le cours 1 ne "
                      "suppose aucune connaissance du cours 2 ; le cours 2 signale "
                      "les rares passages qui font appel à des notions front-end."))
    blocks.append(pb())
    return blocks


def _bornes() -> dict[str, tuple[int, int]]:
    """Numéros de début et de fin de chaque partie, calculés depuis les plans."""
    from content.c1.course import COURSE as C1
    from content.c2.course import COURSE as C2

    bornes: dict[str, tuple[int, int]] = {}
    n = 0
    for course in (C1, C2):
        for part in course["parts"]:
            k = len(part["chapters"])
            bornes[part["id"]] = (n + 1, n + k)
            n += k
    return bornes


def _plage(bornes: dict, ids: list[str]) -> str:
    debut = bornes[ids[0]][0]
    fin = bornes[ids[-1]][1]
    if debut == fin:
        return str(debut)
    return f"{debut} à {fin}"


def _paths() -> list[dict]:
    bornes = _bornes()
    return [
        h(1, "Parcours de progression"),
        p("Trois parcours sont proposés selon le point de départ et le temps "
          "disponible. Chaque parcours indique les chapitres à travailler et un "
          "rythme réaliste, à raison de six à huit heures par semaine.", "lead"),
        h(3, "Parcours A — Débuter en développement web (16 semaines)"),
        p("Ce parcours suit le cours 1 dans l'ordre, puis aborde les fondations du "
          "cours 2 utiles à la mise en ligne d'un site."),
        table(["Semaines", "Chapitres", "Objectif"],
              [["1–2", _plage(bornes, ["c1p1"]), "Comprendre le Web, écrire du HTML structuré"],
               ["3–4", _plage(bornes, ["c1p2"]), "CSS, typographie, couleurs"],
               ["5–6", _plage(bornes, ["c1p3"]), "Flexbox, Grid, responsive, accessibilité"],
               ["7–8", _plage(bornes, ["c1p4"]), "DOM, événements, asynchrone, état"],
               ["9", _plage(bornes, ["c1p5"]), "Débogage, performance, sécurité, mise en ligne"],
               ["10", _plage(bornes, ["c1p6"]), "CSS avancé, composants, i18n, maintenance"],
               ["11–12", _plage(bornes, ["c1p7"]), "PWA, SVG et canvas, polices, tests, tableaux"],
               ["13–14", _plage(bornes, ["c2p1"]), "Culture DevOps, Linux, shell"],
               ["15", _plage(bornes, ["c2p2"]), "Réseaux, DNS, HTTP, serveurs"],
               ["16", "révisions", "Synthèse, projet personnel, mise en ligne"]],
              widths=[1.6, 3.2, 5.2], first_col_bold=True),
        h(3, "Parcours B — Développeur confirmé (10 semaines)"),
        p("Ce parcours cible les développeurs qui maîtrisent déjà HTML et CSS et "
          "veulent consolider JavaScript, la qualité, la performance et la mise en "
          "production."),
        table(["Semaines", "Chapitres", "Objectif"],
              [["1", _plage(bornes, ["c1p3"]), "Mises en page modernes et accessibilité"],
               ["2–3", _plage(bornes, ["c1p4"]), "JavaScript, asynchrone, stockage"],
               ["4", _plage(bornes, ["c1p5"]), "Débogage, performance, livraison"],
               ["5", _plage(bornes, ["c1p6"]), "CSS avancé, composants, i18n"],
               ["6", _plage(bornes, ["c1p7"]), "PWA, dessin, typographie, tests"],
               ["7", _plage(bornes, ["c2p1"]), "Culture DevOps, Linux, Git"],
               ["8", _plage(bornes, ["c2p2"]), "Réseaux, HTTP, TLS, serveurs web"],
               ["9", _plage(bornes, ["c2p3"]), "Conteneurs et Kubernetes"],
               ["10", _plage(bornes, ["c2p4", "c2p5"]), "Cloud, IaC, CI/CD et GitOps"]],
              widths=[1.6, 3.2, 5.2], first_col_bold=True),
        h(3, "Parcours C — Devenir ingénieur DevOps (14 semaines)"),
        p("Ce parcours suppose une aisance de base avec un terminal et un langage "
          "de programmation. Il suit le cours 2, en s'appuyant sur les chapitres "
          "web pour les applications déployées."),
        table(["Semaines", "Chapitres", "Objectif"],
              [["1–2", _plage(bornes, ["c2p1"]), "Culture DevOps, Linux, terminal, Git"],
               ["3–4", _plage(bornes, ["c2p2"]), "Réseaux, DNS, HTTP, TLS, serveurs"],
               ["5", _plage(bornes, ["c2p3"]), "Docker, images, Compose, Kubernetes"],
               ["6–7", _plage(bornes, ["c2p4"]), "Cloud, serverless, Terraform, Ansible"],
               ["8–9", _plage(bornes, ["c2p5"]), "CI/CD, publications, GitOps, secrets"],
               ["10–11", _plage(bornes, ["c2p6"]), "Messagerie, charge, reprise, coûts, sécurité"],
               ["12", _plage(bornes, ["c2p7"]), "Projet final de bout en bout"],
               ["13", "révisions", "Observabilité, SRE, synthèse"],
               ["14", "entretien", "Portfolio, entretien technique, spécialisation"]],
              widths=[1.6, 3.2, 5.2], first_col_bold=True),
        box("methode", "Règle des trois passages",
            "Pour chaque chapitre : lisez une première fois sans coder pour saisir "
            "le modèle mental ; reprenez ensuite les exemples au clavier ; terminez "
            "par les exercices sans regarder le corrigé. La mémoire motrice du code "
            "ne s'acquiert qu'en écrivant."),
        pb(),
    ]


def _conventions() -> list[dict]:
    return [
        h(1, "Conventions, pictogrammes et sources"),
        p("Cette page récapitule les repères visuels utilisés dans le volume et "
          "précise la provenance des contenus.", "lead"),
        h(3, "Les six encadrés"),
        table(["Encadré", "Couleur", "Usage"],
              [["Définition", "Gris bleuté", "Terme technique introduit pour la première fois"],
               ["Objectifs", "Sable", "Compétences visées par le chapitre"],
               ["Méthode", "Sable", "Démarche, ordre des opérations, règle de travail"],
               ["Bonne pratique", "Vert", "Ce qu'il faut faire, et pourquoi"],
               ["Attention", "Rouge", "Risque, erreur fréquente, sécurité"],
               ["Note", "Gris", "Précision, contexte, nuance"]],
              widths=[2.2, 2.4, 6.0], first_col_bold=True),
        h(3, "Numérotation"),
        p("Les chapitres sont numérotés de 1 à 93 à l'échelle du volume : le cours 1 "
          "occupe les chapitres 1 à 45, le cours 2 les chapitres 46 à 93. Les figures, "
          "tableaux et listings sont numérotés par chapitre (par exemple figure 18.4). "
          "Les exercices et corrigés suivent la même règle (exercice 18.2, corrigé 18.2)."),
        h(3, "Exactitude et versions"),
        p("Les exemples privilégient les standards stables : HTML5 vivant, CSS "
          "niveau 3 et modules récents largement pris en charge, JavaScript "
          "ECMAScript 2020 et ultérieur, Bash, Docker, Kubernetes, Terraform, "
          "Ansible. Lorsqu'une fonctionnalité dépend d'une version, le texte le "
          "signale. En cas de doute, la documentation officielle fait foi."),
        h(3, "Sources"),
        p("Les deux ressources fournies par l'éditeur sont citées dans les mentions "
          "légales. Les autres informations techniques proviennent des "
          "spécifications et documentations publiques (WHATWG, W3C, MDN, OpenJS "
          "Foundation, Linux Foundation, CNCF, éditeurs cloud). Aucun contenu "
          "protégé n'a été reproduit."),
        h(3, "Signalement"),
        p("Les erreurs, ambiguïtés et suggestions peuvent être adressées à "
          "l'éditeur via le site https://espritropic.rf.gd, en précisant la page, "
          "le numéro de chapitre et la section concernée."),
        pb(),
    ]


def front_matter(course_info: list[dict], pages: dict, logo: str) -> list[dict]:
    blocks: list[dict] = []
    blocks += _title_page(logo)
    blocks += _credits()
    blocks += _about()
    blocks.append(h(1, "Sommaire général"))
    blocks.append(p("Le sommaire présente les deux cours, leurs parties et leurs "
                    "chapitres. Les numéros de page renvoient à la pagination "
                    "continue du volume ; ils se mettent à jour avec le champ "
                    "automatique (F9).", "lead"))
    blocks.append({"t": "__TOC__"})
    blocks.append(pb())
    blocks += _howto()
    blocks += _plan(course_info)
    blocks += _paths()
    blocks += _conventions()
    return blocks
