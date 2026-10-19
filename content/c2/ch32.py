from bookkit.dsl import (box, code, defn, ex, fig, h, ol, p, quiz, table, ul)

CH = {
    "title": "Gestion de configuration : Chef, Puppet et stratégies",
    "subtitle": "Comparer les approches, choisir selon le contexte et éviter les "
                "migrations inutiles.",
    "duration": "2 h 45",
    "level": "Avancé",
    "prereq": "chapitre 71",
    "objectives": [
        "Situer Chef, Puppet, Salt et Ansible.",
        "Comprendre les modèles push et pull.",
        "Écrire une ressource Puppet et une recette Chef.",
        "Évaluer la dette d'une migration.",
        "Choisir une stratégie de gestion de configuration.",
    ],
    "blocks": [
        h(2, "Deux modèles d'exécution"),
        p("Ansible pousse la configuration depuis un poste de contrôle. Puppet et Chef "
          "font l'inverse : un agent sur la machine tire sa configuration d'un serveur "
          "et l'applique périodiquement."),
        fig("compare", "Deux modèles d'application",
            ("PUSH (ANSIBLE)", ["Exécution à la demande", "Sans agent",
                                "Ordre explicite"],
             "PULL (PUPPET, CHEF)", ["Application périodique", "Agent installé",
                                     "Convergence continue"]),
            height=215),
        table(["Critère", "Push", "Pull"],
              [["Installation", "Sans agent", "Agent à déployer"],
               ["Convergence", "À la demande", "Périodique"],
               ["Échelle", "Limitée par le lanceur", "Bonne sur grands parcs"],
               ["Dérive", "Possible entre deux exécutions", "Corrigée automatiquement"],
               ["Débogage", "Direct", "Par journaux d'agent"]],
              widths=[3.6, 4.6, 4.8], first_col_bold=True,
              caption="Cinq différences"),
        defn("Convergence", "Propriété d'un système qui ramène en continu la machine à "
                            "l'état décrit, même si quelqu'un l'a modifiée manuellement. "
                            "Le pull converge sans intervention."),

        h(2, "Puppet"),
        p("Puppet décrit des ressources dans un langage déclaratif. Chaque ressource "
          "exprime un état, et le catalogue est compilé sur le serveur avant d'être "
          "appliqué par l'agent."),
        code("""# site.pp
node 'web1.exemple.fr' {
  class { 'nginx':
    manage_repo => true,
  }

  nginx::resource::server { 'exemple.fr':
    listen_port => 443,
    ssl         => true,
    ssl_cert    => '/etc/letsencrypt/live/exemple.fr/fullchain.pem',
    ssl_key     => '/etc/letsencrypt/live/exemple.fr/privkey.pem',
    proxy       => 'http://127.0.0.1:3000',
  }

  package { 'chrony':
    ensure => installed,
  }

  service { 'chrony':
    ensure  => running,
    enable  => true,
    require => Package['chrony'],
  }
}""", "puppet", "Un nœud décrit"),
        table(["Concept", "Puppet", "Chef", "Ansible"],
              [["Unité de code", "Ressource", "Recette", "Tâche"],
               ["Réutilisation", "Classe et module", "Recette et livre", "Rôle"],
               ["Inventaire", "Console ou ENC", "Serveur Chef", "Fichier d'inventaire"],
               ["Exécution", "Agent pull", "Agent pull", "Push SSH"],
               ["Langage", "DSL Puppet", "Ruby", "YAML"]],
              widths=[3.6, 3.6, 3.6, 3.6], first_col_bold=True,
              caption="Cinq concepts comparés"),
        box("attention", "Le langage déclaratif n'interdit pas l'ordre implicite",
            "Puppet applique les ressources dans un ordre déterminé par les "
            "dépendances. Sans `require`, `before` ou `notify`, l'ordre peut surprendre : "
            "déclarez explicitement les relations."),

        h(2, "Chef"),
        p("Chef utilise Ruby pour décrire des recettes. Cette liberté permet des "
          "abstractions puissantes, au prix d'une courbe d'apprentissage plus élevée et "
          "d'un risque de code difficile à relire."),
        code("""# recipes/default.rb
package 'nginx' do
  action :install
end

template '/etc/nginx/sites-available/site.conf' do
  source 'site.conf.erb'
  owner  'root'
  group  'root'
  mode   '0644'
  variables(
    domaine: node['site']['domaine'],
    upstream: node['site']['upstream']
  )
  notifies :reload, 'service[nginx]', :delayed
end

service 'nginx' do
  action [:enable, :start]
end""", "ruby", "Une recette Chef"),
        table(["Avantage", "Inconvénient"],
              [["Écosystème mature", "Agent et serveur à exploiter"],
               ["Convergence continue", "Complexité de débogage"],
               ["Gestion fine des dépendances", "Langage à maîtriser"],
               ["Adapté aux grands parcs", "Surdimensionné pour dix serveurs"]],
              widths=[6.0, 6.0], first_col_bold=True,
              caption="Deux colonnes, un bilan"),
        defn("Livre de recettes", "Ensemble de recettes Chef et de leurs dépendances, "
                                  "versionné et publié. Il joue le rôle du module ou du "
                                  "rôle Ansible."),

        h(2, "Choisir sans dogme"),
        p("Le choix dépend du parc, de l'équipe et de l'existant. Une migration coûte "
          "souvent plus cher que le gain attendu, surtout si l'outil actuel fonctionne."),
        table(["Contexte", "Choix raisonnable", "Raison"],
              [["Moins de cinquante serveurs", "Ansible", "Sans agent, rapide à adopter"],
               ["Parc hétérogène ancien", "Conserver l'outil en place", "Coût de migration"],
               ["Convergence permanente exigée", "Puppet ou Chef", "Agents et rapports"],
               ["Équipe Ruby", "Chef", "Compétences existantes"],
               ["Infrastructure conteneurisée", "Images + IaC", "Moins de configuration système"]],
              widths=[5.0, 4.6, 4.4], first_col_bold=True,
              caption="Cinq contextes"),
        code("""# Ce qui compte plus que l'outil
- Toute la configuration est versionnée
- Une machine se reconstruit depuis zéro
- Les secrets sont externalisés
- Les changements passent par une revue
- L'état réel est vérifié régulièrement""", "text", "Cinq invariants"),
        p("Une organisation qui applique ces cinq règles obtient l'essentiel du bénéfice, "
          "quel que soit l'outil. Une organisation qui ne les applique pas n'en tirera "
          "rien, même avec l'outil le plus récent."),

        h(2, "Migrations"),
        p("Remplacer un outil de gestion de configuration est un projet, pas une tâche. "
          "Trois précautions évitent les régressions silencieuses."),
        ol("**Inventorier** ce que l'outil actuel gère réellement, y compris les exceptions.",
           "**Migrer par périmètre** : un service, puis un groupe, jamais tout à la fois.",
           "**Comparer l'état obtenu** avec l'état attendu, machine par machine."),
        code("""# Comparer deux machines avant et après migration
ssh web1 'dpkg -l | sort' > web1-avant.txt
ssh web1 'systemctl list-unit-files --state=enabled' >> web1-avant.txt

# Après migration
ssh web1 'dpkg -l | sort' > web1-apres.txt
ssh web1 'systemctl list-unit-files --state=enabled' >> web1-apres.txt

diff web1-avant.txt web1-apres.txt""", "bash", "Une comparaison concrète"),
        table(["Risque", "Symptôme", "Prévention"],
              [["Configuration oubliée", "Service absent après reconstruction", "Inventaire exhaustif"],
               ["Ordre modifié", "Échec au démarrage", "Dépendances explicites"],
               ["Secret non migré", "Authentification refusée", "Test par service"],
               ["Double gestion", "Modifications écrasées", "Une seule source de vérité"]],
              widths=[4.4, 5.2, 4.4], first_col_bold=True,
              caption="Quatre risques de migration"),
        box("pratique", "La reconstruction est le vrai test",
            "Une machine configurée par l'outil doit pouvoir être détruite et reconstruite "
            "sans intervention manuelle. Tant que ce test échoue, la configuration n'est "
            "pas réellement codifiée."),
        box("methode", "Évaluer une migration",
            items=["Combien de temps la reconstruction manuelle prend-elle aujourd'hui ?",
                   "Quelles exceptions ne sont pas codifiées ?",
                   "Qui maîtrise l'outil cible ?",
                   "Quel est le coût d'une régression pendant la bascule ?",
                   "Peut-on migrer un service pilote sans risque ?"]),
    ],
    "keypoints": [
        "Le push exécute à la demande, le pull converge en continu.",
        "Puppet et Chef reposent sur un agent et un serveur.",
        "Le pull corrige la dérive entre deux exécutions.",
        "Puppet décrit des ressources, Chef écrit du Ruby.",
        "L'ordre des ressources doit être explicite.",
        "Le choix dépend du parc et de l'équipe, pas de la mode.",
        "La reconstruction sans intervention est le vrai test.",
        "Une migration se fait par périmètre, avec comparaison d'état.",
    ],
    "bridge": "La configuration est maîtrisée. La dernière partie assemble le tout : "
              "livraison, sécurité et exploitation.",
    "exercises": [
        ex("Traduire une tâche Ansible en ressource Puppet",
           "Installer Nginx, déployer un modèle et recharger le service.",
           ["Déclarez le paquet.",
            "Déclarez le fichier avec `notify`.",
            "Déclarez le service."],
           [("puppet", """package { 'nginx':
  ensure => installed,
}

file { '/etc/nginx/sites-available/site.conf':
  ensure  => file,
  content => template('site/site.conf.erb'),
  owner   => 'root',
  group   => 'root',
  mode    => '0644',
  require => Package['nginx'],
  notify  => Service['nginx'],
}

service { 'nginx':
  ensure  => running,
  enable  => true,
  require => Package['nginx'],
}"""),
            "`require` établit l'ordre, `notify` déclenche le rechargement après "
            "modification du fichier.",
            "Contrairement à Ansible, le service est déclaré une fois et le rechargement "
            "est géré par la notification."]),
        ex("Comparer deux modèles",
           "Une équipe hésite entre Ansible et Puppet pour 200 serveurs.",
           ["Listez les besoins réels.",
            "Évaluez les contraintes.",
            "Proposez une décision."],
           ["Besoins : conformité continue, inventaire fiable, rapports d'écart.",
            "Contraintes : équipe de trois personnes, pas d'expérience Puppet, "
            "applications conteneurisées.",
            "Décision : Ansible pour la configuration initiale, images conteneurisées "
            "pour les applications, réévaluation si le parc dépasse plusieurs centaines "
            "de machines hétérogènes."],
           level="Architecture"),
        ex("Préparer une migration",
           "Un parc de trente serveurs passe de scripts maison à Ansible.",
           ["Inventoriez l'existant.",
            "Migrez un serveur pilote.",
            "Comparez l'état."],
           [("bash", """# Inventaire des paquets et services d'un serveur
ssh web1 'dpkg -l | awk "{print \\$2}" | sort' > web1-paquets.txt
ssh web1 'systemctl list-unit-files --state=enabled --no-legend' > web1-services.txt

# Après migration, comparer
diff web1-paquets.txt web1-paquets-apres.txt
diff web1-services.txt web1-services-apres.txt"""),
            "La comparaison révèle les paquets installés manuellement et jamais "
            "documentés.",
            "Le serveur pilote doit être reconstructible avant de généraliser."],
           level="Migration"),
    ],
    "quiz": [
        quiz("Quel modèle utilise un agent qui tire sa configuration ?",
             ["Push", "Pull", "Les deux", "Aucun"],
             1,
             "Puppet et Chef reposent sur un agent en mode pull."),
        quiz("Quel est l'avantage principal du pull ?",
             ["Moins de sécurité", "Correction continue de la dérive",
              "Aucune installation", "Plus rapide à écrire"],
             1,
             "L'agent réapplique l'état périodiquement, même après modification manuelle."),
        quiz("Quel langage utilise Chef ?",
             ["YAML", "Ruby", "HCL", "Go"],
             1,
             "Les recettes Chef sont écrites en Ruby."),
        quiz("Quel test prouve qu'une configuration est réellement codifiée ?",
             ["Le lint passe", "La machine se reconstruit sans intervention",
              "Le playbook est long", "L'agent répond"],
             1,
             "La reconstruction depuis zéro est la preuve décisive."),
    ],
}
