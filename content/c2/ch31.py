from bookkit.dsl import (box, code, defn, ex, fig, h, ol, p, quiz, table, ul)

CH = {
    "title": "Ansible : configuration et idempotence",
    "subtitle": "Décrire l'état d'une machine et l'appliquer autant de fois que "
                "nécessaire, sans effet secondaire.",
    "duration": "3 h 15",
    "level": "Intermédiaire",
    "prereq": "chapitre 70",
    "objectives": [
        "Écrire un inventaire et un playbook.",
        "Comprendre l'idempotence des modules.",
        "Utiliser les variables, les rôles et les modèles.",
        "Gérer les secrets avec un coffre.",
        "Vérifier une exécution sans la subir.",
    ],
    "blocks": [
        h(2, "Un inventaire, un playbook"),
        p("Ansible se connecte en SSH, sans agent installé sur les cibles. Un inventaire "
          "liste les hôtes ; un playbook décrit les tâches à appliquer. Chaque module est "
          "idempotent : le rejouer ne change rien si l'état est déjà correct."),
        code("""# inventaire.ini
[web]
web1.exemple.fr
web2.exemple.fr

[db]
db1.exemple.fr

[prod:children]
web
db

[prod:vars]
timezone=Africa/Porto-Novo""", "ini", "Un inventaire simple"),
        code("""# playbook.yml
---
- name: Configurer les serveurs web
  hosts: web
  become: true
  vars:
    paquets: [nginx, chrony, ufw]

  tasks:
    - name: Installer les paquets
      ansible.builtin.apt:
        name: "{{ paquets }}"
        state: present
        update_cache: true

    - name: Déployer la configuration Nginx
      ansible.builtin.template:
        src: templates/site.conf.j2
        dest: /etc/nginx/sites-available/site.conf
        mode: "0644"
      notify: Recharger nginx

    - name: Activer le site
      ansible.builtin.file:
        src: /etc/nginx/sites-available/site.conf
        dest: /etc/nginx/sites-enabled/site.conf
        state: link

  handlers:
    - name: Recharger nginx
      ansible.builtin.service:
        name: nginx
        state: reloaded""", "yaml", "Un playbook complet"),
        table(["Élément", "Rôle", "Remarque"],
              [["`hosts`", "Cible", "Groupe d'inventaire"],
               ["`become`", "Élévation", "Équivalent de `sudo`"],
               ["`tasks`", "Tâches ordonnées", "Chacune doit être idempotente"],
               ["`handlers`", "Actions différées", "Déclenchées par `notify`"],
               ["`vars`", "Variables", "Surchargées par groupe ou extra"],
               ["`roles`", "Organisation réutilisable", "Structure normalisée"]],
              widths=[3.4, 4.8, 4.6], first_col_bold=True,
              caption="Six éléments d'un playbook"),
        defn("Idempotence", "Propriété d'une tâche qui ne modifie rien si l'état désiré "
                            "est déjà atteint. Un module bien utilisé indique `ok` au "
                            "second passage, pas `changed`."),

        h(2, "Les modules qui comptent"),
        p("Ansible fournit des centaines de modules. Cinq familles couvrent l'essentiel "
          "d'une configuration de serveur."),
        table(["Module", "Usage", "Piège"],
              [["`apt` / `dnf`", "Paquets", "`state: latest` rend non reproductible"],
               ["`template` / `copy`", "Fichiers", "Droits à préciser"],
               ["`service` / `systemd`", "Services", "`enabled` distinct de `state`"],
               ["`user` / `group`", "Comptes", "Mot de passe hashé"],
               ["`lineinfile` / `blockinfile`", "Édition de fichier", "À éviter si un template suffit"],
               ["`command` / `shell`", "Exécution brute", "Non idempotent par défaut"]],
              widths=[5.4, 4.2, 4.0], first_col_bold=True,
              caption="Six modules courants"),
        box("attention", "`command` casse l'idempotence",
            "`ansible.builtin.command` s'exécute à chaque passage. Utilisez un module "
            "dédié, ou ajoutez `creates:` ou `changed_when:` pour conditionner "
            "l'exécution et le compte rendu."),
        code("""# Vérifier qu'une tâche n'a pas déjà été faite
- name: Extraire l'archive
  ansible.builtin.command:
    cmd: tar -xzf /tmp/app.tgz -C /opt
    creates: /opt/app/bin/serveur

# Ne pas signaler un changement quand rien n'a changé
- name: Vérifier la version
  ansible.builtin.command: /opt/app/bin/serveur --version
  register: version
  changed_when: false""", "yaml", "Deux garde-fous"),

        h(2, "Variables et modèles"),
        p("Les variables se hiérarchisent : rôle, groupe, hôte, ligne de commande. La "
          "priorité est stricte et source de confusion : documentez vos conventions."),
        code("""# group_vars/prod.yml
env: production
domaine: exemple.fr
replicas: 3
log_level: info

# host_vars/web1.yml
ansible_host: 203.0.113.11

# Utilisation dans un modèle Jinja2
server {
    listen 443 ssl;
    server_name {{ domaine }};
    access_log /var/log/nginx/{{ env }}.access.log;
{% for up in upstreams %}
    # {{ up }}
{% endfor %}
}""", "yaml", "Variables hiérarchisées"),
        table(["Niveau", "Fichier", "Priorité"],
              [["Rôle", "`roles/x/defaults/main.yml`", "La plus faible"],
               ["Groupe", "`group_vars/all.yml`", "Faible"],
               ["Groupe spécifique", "`group_vars/prod.yml`", "Moyenne"],
               ["Hôte", "`host_vars/web1.yml`", "Forte"],
               ["Ligne de commande", "`-e`", "La plus forte"]],
              widths=[4.2, 5.4, 3.4], first_col_bold=True,
              caption="Cinq niveaux de priorité"),
        code("""# Structure d'un rôle
roles/nginx/
├── defaults/main.yml
├── handlers/main.yml
├── tasks/main.yml
├── templates/site.conf.j2
└── vars/main.yml

# Utilisation
- hosts: web
  roles:
    - nginx
  # ou
  tasks:
    - ansible.builtin.include_role:
        name: nginx""", "text", "Un rôle réutilisable"),
        p("Un rôle se documente par ses `defaults` : ce sont les valeurs que l'appelant "
          "peut surcharger. Les `vars` internes sont réservées aux constantes du rôle."),

        h(2, "Secrets"),
        p("Ansible Vault chiffre des fichiers ou des valeurs entières. La clé de coffre "
          "ne doit jamais être versionnée ni stockée à côté du code."),
        code("""# Chiffrer un fichier
ansible-vault encrypt group_vars/prod/vault.yml

# Éditer et voir
ansible-vault edit group_vars/prod/vault.yml
ansible-vault view group_vars/prod/vault.yml

# Chiffrer une valeur isolée
ansible-vault encrypt_string 'motdepasse' --name 'db_password'

# Exécution avec la clé
ansible-playbook playbook.yml --ask-vault-pass
ansible-playbook playbook.yml --vault-password-file ~/.vault_pass""", "bash",
             "Six commandes"),
        box("attention", "La clé de coffre est le vrai secret",
            "Chiffrer un fichier sans protéger la clé revient à mettre une serrure dont "
            "la clé est scotchée sur la porte. Stockez la clé dans un coffre central ou "
            "un gestionnaire de secrets, et distribuez-la séparément."),

        h(2, "Vérifier avant d'appliquer"),
        p("Ansible offre trois niveaux de vérification : liste des tâches, simulation, "
          "et exécution partielle. Les utiliser systématiquement évite les mauvaises "
          "surprises."),
        code("""# Lister ce qui s'exécuterait
ansible-playbook playbook.yml --list-tasks
ansible-playbook playbook.yml --list-hosts

# Simulation (les modules qui le supportent)
ansible-playbook playbook.yml --check --diff

# Limiter à un hôte ou un groupe
ansible-playbook playbook.yml --limit web1

# Mode verbeux pour comprendre une tâche
ansible-playbook playbook.yml --limit web1 -vvv""", "bash",
             "Cinq commandes de vérification"),
        defn("`--check`", "Mode simulation : les modules annoncent ce qu'ils feraient sans "
                          "modifier le système. Certains modules ne le supportent pas et "
                          "sont ignorés : vérifiez la sortie."),
        table(["Symptôme", "Cause", "Vérification"],
              [["`changed` à chaque passage", "Module non idempotent", "`changed_when`"],
               ["Tâche ignorée", "Condition fausse", "`-vv`"],
               ["Connexion refusée", "Inventaire ou clé", "`ansible -m ping`"],
               ["Permission refusée", "`become` absent", "`-K`"],
               ["Handler non exécuté", "Jamais notifié", "Ordre des tâches"]],
              widths=[4.6, 4.4, 4.4], first_col_bold=True,
              caption="Cinq symptômes"),
        code("""# Tester la connexion et l'inventaire
ansible all -i inventaire.ini -m ping
ansible-inventory -i inventaire.ini --list
ansible web -i inventaire.ini -m ansible.builtin.setup -a "filter=ansible_distribution\"""",
             "bash", "Trois diagnostics"),
        box("methode", "Avant un playbook en production",
            items=["`--list-tasks` sur le groupe ciblé.",
                   "`--check --diff` sur un hôte représentatif.",
                   "Exécution `--limit` sur un seul serveur.",
                   "Extension progressive au reste du groupe.",
                   "Journaux conservés pour chaque exécution."]),
    ],
    "keypoints": [
        "Ansible se connecte en SSH, sans agent.",
        "Chaque module doit être idempotent.",
        "`command` n'est pas idempotent sans `creates` ou `changed_when`.",
        "Les variables se hiérarchisent, avec des priorités strictes.",
        "Un rôle expose ses `defaults` comme interface.",
        "`enabled` et `state` sont deux réglages distincts d'un service.",
        "Ansible Vault chiffre les secrets, mais pas la clé.",
        "`--check --diff` avant `--limit` avant le groupe entier.",
    ],
    "bridge": "Ansible configure les machines. Le chapitre suivant compare cette "
              "approche à Chef et Puppet, puis choisit.",
    "exercises": [
        ex("Configurer un serveur web",
           "Nginx doit être installé, configuré et démarré.",
           ["Installez le paquet.",
            "Déployez le modèle.",
            "Rechargez via un handler."],
           [("yaml", """---
- hosts: web
  become: true
  tasks:
    - name: Installer nginx
      ansible.builtin.apt:
        name: nginx
        state: present
        update_cache: true

    - name: Déployer la configuration
      ansible.builtin.template:
        src: templates/site.conf.j2
        dest: /etc/nginx/sites-available/site.conf
        mode: "0644"
      notify: Recharger nginx

    - name: Activer le site
      ansible.builtin.file:
        src: /etc/nginx/sites-available/site.conf
        dest: /etc/nginx/sites-enabled/site.conf
        state: link
      notify: Recharger nginx

    - name: Démarrer nginx
      ansible.builtin.service:
        name: nginx
        state: started
        enabled: true

  handlers:
    - name: Recharger nginx
      ansible.builtin.service:
        name: nginx
        state: reloaded"""),
            "Le handler ne s'exécute qu'une fois, même si plusieurs tâches le notifient.",
            "Au second passage, aucune tâche ne doit être `changed` : c'est la preuve de "
            "l'idempotence."]),
        ex("Utiliser Vault",
           "Un mot de passe de base doit être chiffré dans le dépôt.",
           ["Créez un fichier chiffré.",
            "Référencez la variable.",
            "Exécutez avec la clé."],
           [("bash", """ansible-vault create group_vars/prod/vault.yml
# db_password: "motdepasse"

# Utilisation
# - name: Créer la base
#   community.postgresql.postgresql_user:
#     name: app
#     password: "{{ db_password }}"

ansible-playbook playbook.yml --vault-password-file ~/.vault_pass --check --diff"""),
            "Le fichier chiffré est versionné sans risque ; la clé reste hors du dépôt.",
            "`--check` montre la tâche sans appliquer la modification."]),
        ex("Rendre une tâche idempotente",
           "Une tâche `command` s'exécute et signale un changement à chaque passage.",
           ["Ajoutez une condition.",
            "Désactivez le compte rendu.",
            "Vérifiez deux exécutions."],
           [("yaml", """- name: Initialiser l'application
  ansible.builtin.command:
    cmd: /opt/app/bin/init --force
    creates: /opt/app/.initialise

- name: Lire la version
  ansible.builtin.command: /opt/app/bin/serveur --version
  register: version
  changed_when: false

- name: Afficher la version
  ansible.builtin.debug:
    msg: "Version installée : {{ version.stdout }}\""""),
            "`creates` empêche l'exécution si le fichier existe déjà.",
            "`changed_when: false` corrige le compte rendu sans empêcher l'exécution."],
           level="Qualité"),
    ],
    "quiz": [
        quiz("Pourquoi Ansible ne nécessite-t-il pas d'agent ?",
             ["Il utilise SSH", "Il utilise un démon", "Il utilise le cloud",
              "Il utilise Docker"],
             0,
             "La connexion se fait par SSH et Python sur la cible."),
        quiz("Que signifie l'idempotence pour une tâche ?",
             ["Elle s'exécute vite", "Elle ne change rien si l'état est déjà correct",
              "Elle est facultative", "Elle s'exécute toujours"],
             1,
             "Le second passage doit rapporter `ok` et non `changed`."),
        quiz("Quel niveau de variable est le plus fort ?",
             ["`defaults` du rôle", "`group_vars`", "`host_vars`", "`-e` en ligne de commande"],
             3,
             "Les variables passées en ligne de commande ont la priorité maximale."),
        quiz("Que fait Ansible Vault ?",
             ["Chiffre les fichiers de secrets", "Gère les utilisateurs",
              "Configure le pare-feu", "Installe des paquets"],
             0,
             "Il chiffre des fichiers ou des valeurs avec une clé externe."),
        quiz("Quel mode simule une exécution ?",
             ["`--diff` seul", "`--check`", "`--limit`", "`-vvv`"],
             1,
             "`--check` annonce les changements sans les appliquer."),
    ],
}
