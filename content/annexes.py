"""Annexes du volume : mémentos, glossaire, sources, registre de pagination."""
from __future__ import annotations

from bookkit.dsl import h, p, pb, table, ul


def build_annexes(pages: dict) -> list[dict]:
    blocks: list[dict] = []
    blocks += _memento_html()
    blocks += _memento_devops()
    blocks += _glossaire()
    blocks += _registre(pages)
    return blocks


def _memento_html() -> list[dict]:
    return [
        h(1, "Annexe A — Mémento des balises HTML"),
        p("Ce mémento regroupe les balises utilisées dans le volume. La colonne "
          "« Usage » indique le contexte recommandé ; une balise mal employée nuit "
          "autant qu'une balise absente.", "lead"),
        table(["Balise", "Rôle", "Usage typique"],
              [["`<!doctype html>`", "Déclare le mode standard HTML5", "Première ligne du document"],
               ["`<html lang>`", "Racine du document, langue", "`lang=\"fr\"`"],
               ["`<head>`", "Métadonnées", "Titre, encodage, feuilles de style"],
               ["`<meta charset>`", "Encodage des caractères", "`utf-8` en premier"],
               ["`<meta name=viewport>`", "Adaptation mobile", "`width=device-width`"],
               ["`<title>`", "Titre de l'onglet et du résultat de recherche", "Unique par page"],
               ["`<link rel=stylesheet>`", "Feuille de style externe", "Dans le `head`"],
               ["`<style>`", "Styles internes", "Prototypage uniquement"],
               ["`<script>`", "Script", "`defer` ou `type=module`"],
               ["`<body>`", "Contenu visible", "Un seul par document"],
               ["`<header>`", "En-tête de page ou de section", "Logo, navigation"],
               ["`<nav>`", "Navigation principale", "Un ou deux par page"],
               ["`<main>`", "Contenu principal", "Un seul, unique"],
               ["`<article>`", "Contenu autonome", "Article, fiche produit"],
               ["`<section>`", "Section thématique", "Toujours titrée"],
               ["`<aside>`", "Contenu connexe", "Encadré, note latérale"],
               ["`<footer>`", "Pied de page ou de section", "Mentions, liens secondaires"],
               ["`<h1>` à `<h6>`", "Hiérarchie des titres", "Un `h1` par page"],
               ["`<p>`", "Paragraphe", "Texte courant"],
               ["`<ul>` / `<ol>`", "Listes non ordonnée / ordonnée", "Navigation, étapes"],
               ["`<dl>`", "Liste de définitions", "Glossaire"],
               ["`<a href>`", "Lien", "Navigation interne ou externe"],
               ["`<strong>`", "Importance", "Alerte, mot clé"],
               ["`<em>`", "Accent d'insistance", "Nuance de sens"],
               ["`<figure>` / `<figcaption>`", "Illustration et sa légende", "Image, schéma, code"],
               ["`<img alt>`", "Image et texte alternatif", "`alt` obligatoire"],
               ["`<picture>`", "Image responsive", "Formats multiples"],
               ["`<video>` / `<audio>`", "Média", "`controls`, sous-titres"],
               ["`<table>`", "Données tabulaires", "Jamais pour la mise en page"],
               ["`<caption>`", "Titre du tableau", "Premier enfant"],
               ["`<th scope>`", "En-tête de cellule", "`col` ou `row`"],
               ["`<form>`", "Formulaire", "`action`, `method`"],
               ["`<label for>`", "Étiquette de champ", "Toujours associée"],
               ["`<input type>`", "Champ de saisie", "`email`, `number`, `date`…"],
               ["`<select>` / `<option>`", "Liste déroulante", "Avec `label`"],
               ["`<textarea>`", "Zone de texte multiligne", "Message, commentaire"],
               ["`<button type>`", "Bouton", "`submit`, `button`, `reset`"],
               ["`<fieldset>` / `<legend>`", "Groupe de champs", "Formulaires longs"],
               ["`<details>` / `<summary>`", "Contenu repliable", "FAQ, aides"],
               ["`<dialog>`", "Boîte de dialogue native", "Modales accessibles"]],
              widths=[2.6, 4.0, 4.4], first_col_bold=False),
        pb(),
    ]


def _memento_devops() -> list[dict]:
    return [
        h(1, "Annexe B — Aide-mémoire DevOps"),
        p("Les commandes ci-dessous sont celles qui reviennent le plus souvent en "
          "exploitation. Chaque ligne est volontairement courte : la page de manuel "
          "reste la référence.", "lead"),
        h(3, "Système et processus"),
        table(["Commande", "Effet"],
              [["`uname -a`", "Version du noyau et architecture"],
               ["`df -h`", "Occupation des systèmes de fichiers"],
               ["`du -sh *`", "Taille des éléments du dossier courant"],
               ["`free -h`", "Mémoire disponible"],
               ["`ps aux`", "Processus en cours"],
               ["`top` / `htop`", "Activité en temps réel"],
               ["`systemctl status nginx`", "État d'un service"],
               ["`journalctl -u nginx -f`", "Journaux d'un service en direct"],
               ["`ss -tulpn`", "Ports en écoute"],
               ["`chmod 640 fichier`", "Droits lecture/écriture propriétaire, lecture groupe"],
               ["`chown user:group fichier`", "Changer propriétaire et groupe"],
               ["`tar -czf archive.tgz dossier/`", "Archiver et compresser"]],
              widths=[4.4, 6.4]),
        h(3, "Git"),
        table(["Commande", "Effet"],
              [["`git status`", "État de l'arbre de travail"],
               ["`git switch -c feature/x`", "Créer et basculer sur une branche"],
               ["`git rebase main`", "Rejouer les commits sur main"],
               ["`git log --oneline --graph`", "Historique compact"],
               ["`git diff --staged`", "Différences indexées"],
               ["`git restore --staged f`", "Retirer un fichier de l'index"],
               ["`git commit --amend`", "Corriger le dernier commit"],
               ["`git stash -u`", "Mettre de côté, fichiers non suivis inclus"],
               ["`git bisect start`", "Recherche binaire d'une régression"]],
              widths=[4.4, 6.4]),
        h(3, "Docker et Kubernetes"),
        table(["Commande", "Effet"],
              [["`docker build -t app:1.0 .`", "Construire une image"],
               ["`docker run -p 8080:80 app:1.0`", "Lancer un conteneur"],
               ["`docker logs -f ctn`", "Suivre les journaux"],
               ["`docker exec -it ctn sh`", "Ouvrir un shell dans le conteneur"],
               ["`docker compose up -d`", "Démarrer une pile"],
               ["`kubectl get pods -A`", "Lister les pods"],
               ["`kubectl describe pod p`", "Diagnostiquer un pod"],
               ["`kubectl logs -f p`", "Journaux d'un pod"],
               ["`kubectl rollout undo deploy/app`", "Revenir au déploiement précédent"],
               ["`kubectl port-forward svc/app 8080:80`", "Accéder à un service localement"]],
              widths=[4.8, 6.0]),
        h(3, "Terraform et Ansible"),
        table(["Commande", "Effet"],
              [["`terraform init`", "Initialiser le dossier et les providers"],
               ["`terraform plan -out p.tfplan`", "Prévisualiser les changements"],
               ["`terraform apply p.tfplan`", "Appliquer le plan"],
               ["`terraform state list`", "Lister les ressources suivies"],
               ["`terraform destroy`", "Détruire l'infrastructure"],
               ["`ansible all -m ping`", "Tester la connexion aux hôtes"],
               ["`ansible-playbook site.yml --check`", "Simulation"],
               ["`ansible-playbook site.yml --limit web`", "Exécution ciblée"]],
              widths=[4.8, 6.0]),
        pb(),
    ]


def _glossaire() -> list[dict]:
    terms = [
        ("Accessibilité", "Qualité d'un service utilisable par tous, y compris avec "
                          "un lecteur d'écran, un clavier seul ou une vision réduite."),
        ("Artefact", "Fichier produit par une chaîne de construction : image, archive, "
                     "paquet, binaire."),
        ("Blue/green", "Déploiement de deux environnements identiques, la bascule du "
                       "trafic servant de mise en production et de retour arrière."),
        ("Cache", "Copie temporaire d'une donnée pour éviter de la recalculer ou de la "
                  "retélécharger."),
        ("CI/CD", "Intégration continue (tests à chaque commit) et livraison ou "
                  "déploiement continu (mise en production automatisée)."),
        ("Conteneur", "Isolation de processus partageant le noyau de l'hôte, avec "
                      "système de fichiers et réseau propres."),
        ("CORS", "Politique du navigateur autorisant ou refusant les requêtes "
                 "inter-origines."),
        ("DNS", "Système qui traduit les noms de domaine en adresses IP."),
        ("DORA", "Cadre de mesure de la performance de livraison : fréquence de "
                 "déploiement, délai de livraison, taux d'échec, délai de restauration."),
        ("GitOps", "Gestion de l'état d'un système par un dépôt Git déclaratif, "
                   "réconcilié automatiquement."),
        ("IaC", "Infrastructure as Code : décrire l'infrastructure dans des fichiers "
                "versionnés plutôt que par des actions manuelles."),
        ("Idempotence", "Propriété d'une opération qui produit le même résultat "
                        "qu'elle soit exécutée une ou plusieurs fois."),
        ("Ingress", "Point d'entrée HTTP d'un cluster Kubernetes, qui route vers les "
                    "services internes."),
        ("Latence", "Temps nécessaire à une requête pour aboutir."),
        ("Manifeste", "Fichier déclaratif décrivant l'état souhaité d'une ressource."),
        ("Observabilité", "Capacité à comprendre l'état interne d'un système à partir "
                          "de ses signaux : métriques, journaux, traces."),
        ("Orchestration", "Automatisation du déploiement, de la mise à l'échelle et "
                          "de la réparation de conteneurs."),
        ("Pipeline", "Enchaînement automatisé d'étapes : construction, test, analyse, "
                     "publication, déploiement."),
        ("Pod", "Plus petite unité déployable de Kubernetes, composée d'un ou plusieurs "
                "conteneurs partageant réseau et volumes."),
        ("Provisionnement", "Création des ressources d'infrastructure : machines, "
                            "réseaux, bases."),
        ("Registre", "Service de stockage et de distribution d'images de conteneurs."),
        ("Rollback", "Retour à une version antérieure connue comme fonctionnelle."),
        ("SLO", "Objectif de niveau de service, exprimé en pourcentage de réussite sur "
                "une fenêtre donnée."),
        ("SLI", "Indicateur mesuré qui sert à évaluer un SLO."),
        ("Secrets", "Informations sensibles : mots de passe, clés, jetons."),
        ("Service mesh", "Couche d'infrastructure gérant les communications entre "
                         "services : chiffrement, retries, observabilité."),
        ("Sidecar", "Conteneur auxiliaire partageant le pod du conteneur principal."),
        ("SRE", "Site Reliability Engineering : application de l'ingénierie logicielle "
                "à l'exploitation."),
        ("Stateless", "Se dit d'un service qui ne conserve aucun état entre deux "
                      "requêtes."),
        ("TLS", "Protocole de chiffrement des échanges réseau, à l'origine du S."),
        ("Trace", "Enregistrement du parcours d'une requête à travers plusieurs "
                  "services."),
        ("Versionnement sémantique", "Convention MAJEUR.MINEUR.CORRECTIF pour les "
                                     "numéros de version."),
        ("Zéro confiance", "Modèle de sécurité qui ne fait confiance à aucun réseau ni "
                           "aucun utilisateur par défaut."),
    ]
    blocks = [
        h(1, "Annexe C — Glossaire"),
        p("Les définitions ci-dessous sont celles employées dans le volume. Elles "
          "privilégient l'usage pratique sur l'exhaustivité théorique.", "lead"),
    ]
    rows = [[t, d] for t, d in terms]
    for i in range(0, len(rows), 14):
        blocks.append(table(["Terme", "Définition"], rows[i:i + 14],
                            widths=[2.6, 8.0], first_col_bold=True))
    blocks.append(pb())
    return blocks


def _registre(pages: dict) -> list[dict]:
    rows = []
    for key, label in [("course1", "Cours 1 — Développement web front-end"),
                       ("course2", "Cours 2 — DevOps, cloud et fiabilité"),
                       ("anx1", "Annexes")]:
        if key in pages:
            rows.append([label, str(pages[key])])
    return [
        h(1, "Annexe D — Registre de pagination"),
        p("Ce registre est produit automatiquement lors de la fabrication du volume. "
          "Il indique la page de départ de chaque cours et des annexes dans la "
          "pagination continue.", "lead"),
        table(["Section", "Page de départ"], rows, widths=[7.0, 3.0], first_col_bold=True),
        p("La pagination de Word peut varier de quelques pages selon les polices "
          "installées, la version du logiciel et les paramètres d'imprimante. Les "
          "mesures de contrôle et les conditions de vérification sont documentées "
          "dans le fichier `docs/PAGINATION.md` du dépôt."),
        p("Pour vérifier le nombre de pages d'un cours dans Word : placez le curseur "
          "au début du cours, notez le numéro affiché dans la barre d'état ; faites "
          "de même au début du cours suivant ; la différence donne le nombre de pages "
          "du cours, page de titre comprise."),
        pb(),
    ]
