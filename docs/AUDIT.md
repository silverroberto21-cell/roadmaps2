# Audit préalable des ressources — dépôt `silverroberto21-cell/roadmaps2`

Date de l'audit : 19 octobre 2026.
Branche de travail : `arena/08cf7007-roadmaps2` (commit de départ `e6a5996`).
Méthode : inventaire exhaustif du dépôt (`git ls-files`), inspection binaire des fichiers,
lecture intégrale des PDF (moteur PyMuPDF), extraction de la table des matières, contrôle des images.

## 1. Inventaire réel des fichiers

| # | Fichier | Type | Taille | Exploitable | Rôle identifié |
|---|---------|------|--------|-------------|----------------|
| 1 | `README.md` | Markdown | 11 o | Oui (vide de contenu : « # roadmaps2 ») | Aucun contenu éditorial |
| 2 | `Informations éditoriale.md` | Markdown | 97 o | Oui | Identité de l'éditeur |
| 3 | `devops.pdf` | PDF 1 page (726 × 2138 pt) | 331 Ko | Oui | **Roadmap DevOps** (infographie roadmap.sh) |
| 4 | `Apprenez_a_creer_votre_site_web_avec_HTM - Copie.pdf` | PDF 249 pages | 7,85 Mo | Oui | **Document de référence HTML5/CSS3** |
| 5 | `logo espritropic community noir sns fond.png` | PNG 1080×1080 RGBA | 44 Ko | Oui | Logo, variante noire (fond transparent) |
| 6 | `logo espritropic community blanc sns fond - Copie.png` | PNG 1080×1080 RGBA | 50 Ko | Oui | Logo, variante blanche (fond transparent) |

Aucun autre fichier (pas de dossier `assets`, `docs`, `src`, ni historique de contenu).
Aucune branche distante supplémentaire accessible ; le dépôt distant est privé et
l'API GitHub répond de façon intermittente (dépôt cloné localement, contenu identique).

## 2. Contrôle d'accessibilité et de lisibilité

- **Roadmap DevOps** : PDF sur une seule page, texte extractible (aucune couche image),
  métadonnées `DevOps Roadmap: Learn to become a DevOps Engineer or SRE`, producteur Chromium,
  créé le 05/09/2025. Les 130+ nœuds sont lisibles et ont été recensés intégralement (§3).
  Le PDF ne contient pas d'hyperliens actifs ni de descriptions : ce sont des **intitulés de
  compétences**, sans contenu pédagogique. Il s'agit donc d'un plan, non d'un cours.
- **PDF de référence HTML/CSS** : 249 pages, texte extractible (≈ 470 000 caractères,
  ≈ 67 500 mots), table des matières de 320 entrées. Auteur : Mathieu Nebra (M@teo21),
  édition 2012, licence Creative Commons, diffusé par le Site du Zéro / Sup'Internet.
  Utilisable comme **référence de structure et de progression**, pas comme texte à recopier.
- **Logos** : PNG RGBA 1080×1080, monogramme « &lt;R&gt; » d'Espritropic Community,
  variantes noir et blanc, fond transparent, netteté suffisante pour l'impression
  (300 dpi jusqu'à ≈ 9 cm).
- **Informations éditoriales** : éditeur `YKABAUTH de chez ESPRITROPIC COMMUNITY`,
  site `https://espritropic.rf.gd`.

## 3. Recensement exhaustif de la roadmap

### 3.1 Roadmap DevOps (`devops.pdf`) — 15 domaines, 137 compétences

1. **Langage de programmation** : Python, Ruby, Go, Rust, JavaScript / Node.js.
2. **Système d'exploitation** : Linux, Unix, Ubuntu/Debian, SUSE Linux, RHEL et dérivés,
   FreeBSD, OpenBSD, NetBSD, Windows.
3. **Connaissances du terminal** : surveillance des processus, surveillance des performances,
   outils réseau, manipulation de texte, Bash, PowerShell, Vim/Nano/Emacs, scripting.
4. **Systèmes de contrôle de version** : Git ; hébergement VCS : GitHub, GitLab, Bitbucket.
5. **« What is and how to setup X ? »** : proxy direct, pare-feu, Nginx, Tomcat, Apache,
   Caddy, IIS, serveur de cache, répartiteur de charge, proxy inverse.
6. **Conteneurs** : Docker, LXC.
7. **Fournisseurs cloud** : AWS, Azure, Google Cloud, DigitalOcean, Alibaba Cloud, Hetzner,
   Heroku, Contabo.
8. **Protocoles et réseau** : FTP/SFTP, DNS, HTTP, HTTPS, SSL/TLS, SSH, white/grey listing,
   SMTP, DMARC, IMAP, SPF, POP3S, domain keys, protocoles de messagerie, modèle OSI.
9. **Serverless** : Vercel, Cloudflare, Azure Functions, AWS Lambda, Netlify, GCP Functions.
10. **Provisionnement** : AWS CDK, CloudFormation, Pulumi, Terraform.
11. **Gestion de configuration** : Ansible, Chef, Puppet.
12. **Outils CI/CD** : GitHub Actions, GitLab CI, Jenkins, CircleCI, Octopus Deploy, TeamCity.
13. **Gestion des secrets** : Sealed Secrets, outils propres au cloud, Vault, SOPs.
14. **Surveillance de l'infrastructure** : Zabbix, Prometheus, Datadog, Grafana ;
    **gestion des logs** : Elastic Stack, Graylog, Splunk, Papertrail, Loki ;
    **surveillance applicative** : Jaeger, New Relic, Datadog, Prometheus, OpenTelemetry.
15. **Orchestration de conteneurs** : GKE/EKS/AKS, AWS ECS/Fargate, Docker Swarm, Kubernetes ;
    **gestion d'artefacts** : Artifactory, Nexus, CloudSmith ; **GitOps** : ArgoCD, FluxCD ;
    **service mesh** : Istio, Consul, Linkerd, Envoy ; **patrons de conception cloud** :
    disponibilité, gestion des données, conception et implémentation, gestion et supervision.

Légende de la roadmap : recommandation personnelle, option alternative (« pick this or purple »),
ordre non strict (apprentissage possible à tout moment).

### 3.2 Document de référence HTML/CSS — 5 parties, 23 chapitres, 320 entrées

- **Partie 1 — Les bases de HTML5** : fonctionnement des sites web ; première page web ;
  organisation du texte ; liens ; images.
- **Partie 2 — Mise en forme avec CSS** : mise en place du CSS ; formatage du texte ;
  couleur et fond ; bordures et ombres ; apparences dynamiques.
- **Partie 3 — Mise en page** : structurer sa page ; modèle des boîtes ; positionnement ;
  TP de création d'un site.
- **Partie 4 — Fonctionnalités évoluées** : tableaux ; formulaires ; vidéo et audio ;
  media queries ; aller plus loin.
- **Partie 5 — Annexes** : mise en ligne ; mémento HTML ; mémento CSS ; compatibilité navigateurs.

### 3.3 Rubriques et sous-rubriques

La roadmap DevOps ne comporte pas de sous-rubriques explicites : chaque nœud est une
compétence feuille. Le document HTML/CSS comporte des sous-rubriques (niveau 3 et 4),
intégralement extraites dans `docs/toc-reference-htmlcss.txt` (320 entrées) et exploitées
pour construire le plan du cours 1.

## 4. Ressources absentes ou inexploitables

| Ressource attendue | État | Conséquence |
|---|---|---|
| Charte graphique (document) | **Absente** | Palette et typographie déduites du logo monochrome ; charte documentée et appliquée de façon homogène (`docs/DESIGN.md`) |
| Nom complet / biographie de l'auteur | **Partiel** | Seul l'éditeur `YKABAUTH — ESPRITROPIC COMMUNITY` est fourni ; utilisé comme signature éditoriale |
| ISBN, dépôt légal, mention de copyright | **Absents** | Page de mentions légales rédigée sans données inventées ; champs signalés comme non fournis |
| Contenu rédactionnel des cours | **Absent** | Intégralité des cours à produire (la roadmap n'est qu'un plan) |
| Illustrations, captures d'écran | **Absentes** | Schémas originaux générés par le pipeline éditorial |
| Roadmap « front-end » ou « JavaScript » dédiée | **Absente** | Le cours 1 est construit sur le PDF de référence HTML/CSS, complété par JavaScript, accessibilité, performance et déploiement pour couvrir le parcours web complet |
| Informations de contact / réseaux sociaux | **Absentes** | Seul le site `https://espritropic.rf.gd` est mentionné |

## 5. Décision éditoriale structurante

La roadmap recouvre **deux domaines distincts et non superposables** :

1. **Développement web front-end** (document de référence HTML5/CSS3, 249 pages) ;
2. **DevOps / cloud / fiabilité** (roadmap DevOps, 137 compétences).

Le livrable est donc un **document Word unique** contenant **deux cours complets**, chacun
autonome et devant atteindre **au moins 350 pages dans le fichier final**. Aucun cours
supplémentaire n'est inventé : le nombre de cours est déterminé par les ressources réelles,
conformément à la consigne. La pagination est vérifiée par sections Word dédiées et par un
moteur de pagination calibré (voir `docs/PAGINATION.md`).
