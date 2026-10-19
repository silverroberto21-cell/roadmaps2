"""Métadonnées du cours 2 et plan des parties."""

COURSE = {
    "title": "DevOps, cloud et fiabilité",
    "short": "De la culture DevOps à la production : Linux, réseaux, conteneurs, "
             "Kubernetes, cloud, infrastructure as code, CI/CD, GitOps, observabilité "
             "et ingénierie de fiabilité.",
    "short_header": "DevOps, cloud et fiabilité",
    "level": "Intermédiaire à confirmé",
    "subtitle": "Concevoir, livrer et exploiter des systèmes logiciels fiables, "
                "automatisés et observables.",
    "description": [
        "Ce cours suit l'intégralité de la feuille de route DevOps fournie par "
        "l'éditeur : systèmes d'exploitation, terminal, gestion de versions, "
        "réseaux, serveurs web, conteneurs, fournisseurs cloud, serverless, "
        "provisionnement, gestion de configuration, CI/CD, secrets, supervision, "
        "orchestration, GitOps, service mesh et patrons de conception cloud. "
        "Il ajoute ce que la feuille de route suppose sans le nommer : messagerie, "
        "tests de charge, reprise après sinistre, coûts, plateforme interne et "
        "sécurité de la chaîne logicielle.",
        "Il ne se contente pas d'énumérer des outils. Chaque chapitre explique le "
        "problème que l'outil résout, le modèle mental sous-jacent, puis la mise en "
        "œuvre concrète. Les exercices simulent des incidents réels : service qui ne "
        "démarre pas, certificat expiré, pipeline bloqué, fuite de secret.",
        "Le cours suppose une aisance de base avec un terminal et un langage de "
        "programmation. Les rappels nécessaires sont fournis aux chapitres 46 à 53.",
    ],
    "contains": [
        "48 chapitres couvrant les quinze domaines de la feuille de route DevOps.",
        "Des centaines de commandes commentées : Linux, Git, Docker, kubectl, Terraform, Ansible.",
        "Des schémas d'architecture : réseau, Kubernetes, pipelines, observabilité.",
        "Des exercices d'incident, des quiz de diagnostic et des études de cas.",
        "Un projet final : plateforme complète, du commit à la production.",
    ],
    "method": [
        "Travaillez dans une machine virtuelle ou un conteneur jetable.",
        "Tapez les commandes une par une et lisez leur sortie avant de continuer.",
        "Pour chaque outil, notez le problème résolu avant d'apprendre la syntaxe.",
        "Automatisez dès la deuxième utilisation manuelle d'une procédure.",
        "Documentez chaque incident : symptôme, hypothèse, test, correctif.",
    ],
    "parts": [
        {
            "id": "c2p1",
            "label": "Partie I",
            "title": "Culture DevOps et systèmes",
            "description": "Comprendre la culture, mesurer la performance, maîtriser "
                           "Linux, le shell, les éditeurs et Git.",
            "chapters": [f"content.c2.ch{n:02d}" for n in range(1, 9)],
        },
        {
            "id": "c2p2",
            "label": "Partie II",
            "title": "Réseaux, protocoles et serveurs",
            "description": "Du modèle OSI aux serveurs web : DNS, HTTP, TLS, SSH, "
                           "proxy, répartition de charge et messagerie.",
            "chapters": [f"content.c2.ch{n:02d}" for n in range(9, 17)],
        },
        {
            "id": "c2p3",
            "label": "Partie III",
            "title": "Conteneurs et orchestration",
            "description": "Docker, images reproductibles, réseaux, Compose, "
                           "Kubernetes, Helm et service mesh.",
            "chapters": [f"content.c2.ch{n:02d}" for n in range(17, 24)],
        },
        {
            "id": "c2p4",
            "label": "Partie IV",
            "title": "Cloud, provisionnement et configuration",
            "description": "Modèles de service, AWS, Azure, Google Cloud, serverless, "
                           "Terraform, Pulumi, Ansible, Chef et Puppet.",
            "chapters": [f"content.c2.ch{n:02d}" for n in range(24, 33)],
        },
        {
            "id": "c2p5",
            "label": "Partie V",
            "title": "Livraison, sécurité et exploitation",
            "description": "CI/CD, GitHub Actions, publications et traçabilité, GitOps, "
                           "gestion des secrets, observabilité et ingénierie de fiabilité.",
            "chapters": [f"content.c2.ch{n:02d}" for n in range(33, 40)],
        },
        {
            "id": "c2p6",
            "label": "Partie VI",
            "title": "Systèmes distribués et industrialisation",
            "description": "Messagerie, tests de charge, reprise après sinistre, coûts, "
                           "plateforme interne, sécurité de la chaîne logicielle, "
                           "durcissement et journalisation.",
            "chapters": [f"content.c2.ch{n:02d}" for n in range(41, 49)],
        },
        {
            "id": "c2p7",
            "label": "Partie VII",
            "title": "Mise en pratique",
            "description": "Un projet complet qui rassemble l'ensemble des compétences "
                           "du cours, du commit à la production.",
            "chapters": ["content.c2.ch40"],
        },
    ],
}
