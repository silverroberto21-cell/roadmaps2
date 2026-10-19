from bookkit.dsl import (box, code, defn, ex, fig, h, ol, p, quiz, table, ul)

CH = {
    "title": "Terraform : décrire l'infrastructure",
    "subtitle": "Rendre l'infrastructure lisible, versionnée et reproductible grâce à un "
                "état géré.",
    "duration": "3 h 30",
    "level": "Intermédiaire",
    "prereq": "chapitre 68",
    "objectives": [
        "Écrire et organiser des fichiers Terraform.",
        "Comprendre le rôle de l'état et du verrou.",
        "Utiliser variables, sorties et modules.",
        "Lire un plan avant d'appliquer.",
        "Éviter les pièges de destruction.",
    ],
    "blocks": [
        h(2, "Le cycle en trois temps"),
        p("Terraform compare la configuration écrite, l'état enregistré et la réalité du "
          "fournisseur. Il en déduit un plan, puis l'applique. Cette comparaison est ce "
          "qui rend l'outil prévisible."),
        fig("flow", "Le cycle Terraform",
            ["Configuration `.tf`",
             "`terraform init` : fournisseurs et modules",
             "`terraform plan` : écart avec l'état",
             "Relecture humaine du plan",
             "`terraform apply` : exécution",
             "État mis à jour et verrouillé"],
            height=255),
        code("""terraform init
terraform validate
terraform fmt -recursive
terraform plan -out=tfplan
terraform apply tfplan
terraform state list
terraform output""", "bash", "Sept commandes de base"),
        table(["Fichier", "Contenu", "Remarque"],
              [["`main.tf`", "Ressources", "Point d'entrée"],
               ["`variables.tf`", "Entrées", "Types et valeurs par défaut"],
               ["`outputs.tf`", "Sorties", "Utilisées par d'autres modules"],
               ["`versions.tf`", "Contraintes de versions", "Fichier verrou généré"],
               ["`terraform.tfvars`", "Valeurs", "Souvent non versionné"]],
              widths=[4.2, 4.6, 4.6], first_col_bold=True,
              caption="Cinq fichiers typiques"),

        h(2, "L'état"),
        p("L'état associe chaque ressource écrite à un identifiant réel chez le "
          "fournisseur. Il contient parfois des valeurs sensibles et doit être stocké "
          "dans un back-end partagé et verrouillé."),
        code("""# Back-end distant avec verrouillage
terraform {
  required_version = ">= 1.8"
  backend "s3" {
    bucket         = "mon-terraform-state"
    key            = "production/network/terraform.tfstate"
    region         = "eu-west-3"
    dynamodb_table = "terraform-locks"
    encrypt        = true
  }
}""", "hcl", "Un back-end partagé"),
        table(["Back-end", "Verrou", "Usage"],
              [["Local", "Aucun", "Apprentissage"],
               ["S3 + DynamoDB", "Oui", "AWS"],
               ["Azure Storage", "Oui", "Azure"],
               ["Google Cloud Storage", "Oui", "GCP"],
               ["Terraform Cloud", "Oui", "Équipe multi-cloud"]],
              widths=[4.4, 3.4, 5.6], first_col_bold=True,
              caption="Cinq back-ends"),
        box("attention", "Ne versionnez jamais l'état",
            "L'état contient des identifiants et parfois des secrets en clair. Il se "
            "stocke dans un compartiment chiffré, avec accès restreint et versionnement "
            "activé. Le fichier local ne doit jamais entrer dans le dépôt."),
        code("""# .gitignore
.terraform/
*.tfstate
*.tfstate.backup
*.tfplan
terraform.tfvars
crash.log

# Récupérer un état perdu
# 1. Restaurer la version précédente du back-end
# 2. Vérifier avec `terraform plan` qu'aucune ressource n'est recréée""", "text",
             "Un `.gitignore` indispensable"),

        h(2, "Variables, sorties et modules"),
        p("Une configuration lisible nomme ses entrées, décrit ses sorties et isole les "
          "ressources réutilisables dans des modules. C'est ce qui distingue un script "
          "d'une infrastructure maintenable."),
        code("""# variables.tf
variable "environnement" {
  description = "Nom de l'environnement (dev, staging, prod)"
  type        = string
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environnement)
    error_message = "Environnement invalide."
  }
}

variable "instance_type" {
  type    = string
  default = "t3.micro"
}""", "hcl", "Des variables validées"),
        code("""# main.tf
resource "aws_instance" "app" {
  ami           = data.aws_ami.ubuntu.id
  instance_type = var.instance_type
  subnet_id     = module.reseau.sous_reseau_prive_id

  tags = {
    Projet        = "demo"
    Environnement = var.environnement
  }

  lifecycle {
    prevent_destroy = true
    ignore_changes  = [ami]
  }
}""", "hcl", "Une ressource protégée"),
        code("""# outputs.tf
output "adresse_publique" {
  description = "Adresse de l'instance applicative"
  value       = aws_instance.app.public_ip
}

output "mot_de_passe" {
  value     = aws_db_instance.main.password
  sensitive = true
}""", "hcl", "Deux sorties, dont une sensible"),
        table(["Élément", "Rôle", "Piège"],
              [["`module`", "Réutiliser un ensemble", "Version à épingler"],
               ["`data`", "Lire l'existant", "Résultat qui varie"],
               ["`locals`", "Valeurs calculées", "Ne pas abuser des expressions"],
               ["`depends_on`", "Forcer l'ordre", "Souvent inutile"],
               ["`lifecycle`", "Protéger une ressource", "Peut bloquer une suppression légitime"]],
              widths=[3.6, 4.8, 5.0], first_col_bold=True,
              caption="Cinq éléments du langage"),

        h(2, "Lire un plan"),
        p("Le plan est le document le plus important de Terraform : il annonce ce qui "
          "sera créé, modifié ou détruit. Une destruction inattendue signale toujours un "
          "problème à comprendre avant d'appliquer."),
        code("""terraform plan -out=tfplan

# Plan: 2 to add, 1 to change, 0 to destroy.

#  # aws_instance.app will be updated in-place
#  ~ resource "aws_instance" "app" {
#      ~ instance_type = "t3.micro" -> "t3.small"
#    }
#
#  # aws_db_instance.main must be replaced
# -/+ resource "aws_db_instance" "main" {
#      ~ engine_version = "16.1" -> "16.3" # forces replacement
#    }""", "text", "Un plan avec remplacement"),
        table(["Symbole", "Signification", "Action"],
              [["`+`", "Création", "Vérifier le coût"],
               ["`~`", "Modification sur place", "Sans interruption"],
               ["`-`", "Destruction", "Comprendre pourquoi"],
               ["`-/+`", "Remplacement", "Vérifier la disponibilité"],
               ["`<=`", "Lecture de données", "Sans effet"]],
              widths=[2.6, 5.4, 5.0], first_col_bold=True,
              caption="Cinq symboles du plan"),
        defn("Remplacement", "Destruction puis création d'une ressource, souvent "
                             "déclenchée par un attribut immuable. Sur une base de "
                             "données, cela signifie une perte si aucune protection "
                             "n'est en place."),
        code("""# Protéger une ressource critique
resource "aws_db_instance" "main" {
  # ...
  deletion_protection = true
  lifecycle {
    prevent_destroy = true
  }
}

# Supprimer réellement après décision explicite
# 1. Retirer `prevent_destroy`
# 2. Appliquer
# 3. Désactiver `deletion_protection`
# 4. Appliquer la suppression""", "hcl", "Deux protections et une procédure"),

        h(2, "Organiser à l'échelle"),
        p("Une configuration unique pour toute l'entreprise devient impossible à "
          "appliquer : le plan dure des heures et le risque augmente. Le découpage par "
          "cycle de vie est la solution."),
        table(["Découpage", "Avantage", "Inconvénient"],
              [["Par environnement", "Isolation", "Duplication"],
               ["Par couche (réseau, données, applicatif)", "Plans courts", "Dépendances entre états"],
               ["Par domaine", "Autonomie des équipes", "Coordination"],
               ["Tout dans un état", "Simplicité initiale", "Risque et lenteur"]],
              widths=[5.0, 4.4, 4.2], first_col_bold=True,
              caption="Quatre découpages"),
        code("""# Référencer un autre état
data "terraform_remote_state" "reseau" {
  backend = "s3"
  config = {
    bucket = "mon-terraform-state"
    key    = "production/network/terraform.tfstate"
    region = "eu-west-3"
  }
}

resource "aws_instance" "app" {
  subnet_id = data.terraform_remote_state.reseau.outputs.sous_reseau_id
}""", "hcl", "Deux états liés"),
        box("methode", "Discipline Terraform",
            items=["`plan` relu avant chaque `apply`, sans exception.",
                   "Un état par environnement et par couche.",
                   "Modules épinglés par version.",
                   "`prevent_destroy` sur les données critiques.",
                   "Aucun secret dans les fichiers `.tf`."]),
    ],
    "keypoints": [
        "Terraform compare configuration, état et réalité.",
        "L'état doit être distant, chiffré et verrouillé.",
        "L'état contient des données sensibles : jamais dans Git.",
        "Les variables se typent et se valident.",
        "Un module se versionne.",
        "Le plan annonce créations, modifications et destructions.",
        "Un remplacement détruit avant de créer.",
        "`prevent_destroy` protège les ressources critiques.",
    ],
    "bridge": "Terraform décrit l'infrastructure dans un langage dédié. Le chapitre "
              "suivant montre l'approche par langage de programmation : Pulumi.",
    "exercises": [
        ex("Écrire une ressource protégée",
           "Une base de données ne doit jamais être détruite par erreur.",
           ["Ajoutez `deletion_protection`.",
            "Ajoutez `prevent_destroy`.",
            "Vérifiez le plan."],
           [("hcl", """resource "aws_db_instance" "main" {
  identifier          = "app-${var.environnement}"
  engine              = "postgres"
  engine_version      = "16.3"
  instance_class      = "db.t3.micro"
  allocated_storage   = 20
  deletion_protection = true

  lifecycle {
    prevent_destroy = true
    ignore_changes  = [password]
  }
}"""),
            "`ignore_changes` évite un remplacement quand le mot de passe est géré "
            "ailleurs.",
            "Toute tentative de destruction échoue à l'application, pas au plan : lisez "
            "le plan pour anticiper."]),
        ex("Lire un plan dangereux",
           "Le plan annonce la destruction de trois ressources.",
           ["Identifiez les ressources.",
            "Cherchez la cause.",
            "Corrigez avant d'appliquer."],
           [("text", """# Plan: 1 to add, 0 to change, 3 to destroy.

#  # aws_instance.app must be replaced
# -/+ resource "aws_instance" "app" {
#        ami = "ami-0a1b2c3d" -> "ami-9f8e7d6c" # forces replacement
#    }

# Cause : l'AMI est un attribut immuable.
# Correction : accepter un remplacement contrôlé, ou figer l'AMI
# et planifier la migration avec un temps d'arrêt connu."""),
            "Un attribut immuable provoque un remplacement : c'est le cas de l'AMI, du "
            "type de sous-réseau, du nom d'identification.",
            "Trois destructions simultanées sur des ressources liées peuvent provoquer "
            "une indisponibilité : découpez en plusieurs applications."],
           level="Diagnostic"),
        ex("Structurer plusieurs environnements",
           "Trois environnements doivent partager le même code.",
           ["Créez un module.",
            "Un état par environnement.",
            "Des valeurs par environnement."],
           [("text", """infra/
├── modules/
│   └── application/
│       ├── main.tf
│       ├── variables.tf
│       └── outputs.tf
├── environnements/
│   ├── dev/
│   │   ├── main.tf      # module "app" { source = "../../modules/application" }
│   │   └── backend.tf   # key = "dev/terraform.tfstate"
│   ├── staging/
│   └── production/"""),
            "Chaque environnement a son propre état : une erreur en développement ne "
            "peut pas détruire la production.",
            "Le module commun garantit que les trois environnements restent cohérents."],
           level="Architecture"),
    ],
    "quiz": [
        quiz("Que contient l'état Terraform ?",
             ["Le code source", "L'association entre configuration et ressources réelles",
              "Les secrets uniquement", "Les journaux"],
             1,
             "Il mémorise l'identifiant réel de chaque ressource créée."),
        quiz("Pourquoi verrouiller l'état ?",
             ["Pour accélérer", "Pour éviter deux applications simultanées",
              "Pour chiffrer", "Pour versionner"],
             1,
             "Deux `apply` concurrents corrompent l'état et créent des doublons."),
        quiz("Que signifie `-/+` dans un plan ?",
             ["Création", "Modification", "Remplacement", "Suppression"],
             2,
             "La ressource est détruite puis recréée."),
        quiz("Où stocker un mot de passe utilisé par Terraform ?",
             ["Dans `variables.tf`", "Dans un gestionnaire de secrets",
              "Dans l'état", "Dans un commentaire"],
             1,
             "Les valeurs sensibles se référencent depuis un coffre, jamais en clair."),
        quiz("Que fait `prevent_destroy` ?",
             ["Accélère la destruction", "Bloque la destruction planifiée",
              "Sauvegarde l'état", "Supprime l'état"],
             1,
             "L'application échoue si la ressource doit être détruite."),
    ],
}
