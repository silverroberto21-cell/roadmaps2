from bookkit.dsl import (box, code, defn, ex, fig, h, ol, p, quiz, table, ul)

CH = {
    "title": "Pulumi : l'infrastructure en langage de programmation",
    "subtitle": "Choisir quand un vrai langage apporte plus qu'un langage dédié, et "
                "l'utiliser sans perdre le contrôle.",
    "duration": "2 h 45",
    "level": "Avancé",
    "prereq": "chapitre 69",
    "objectives": [
        "Comparer Pulumi et Terraform sans dogmatisme.",
        "Écrire un programme d'infrastructure lisible.",
        "Réutiliser des fonctions et des boucles.",
        "Gérer l'état et les secrets.",
        "Tester une configuration d'infrastructure.",
    ],
    "blocks": [
        h(2, "Même modèle, autre langage"),
        p("Pulumi repose sur le même principe que Terraform : un état, un plan, une "
          "application. La différence est le langage : TypeScript, Python, Go, C# au lieu "
          "d'un DSL déclaratif."),
        table(["Aspect", "Terraform (HCL)", "Pulumi"],
              [["Langage", "Dédié, déclaratif", "Généraliste"],
               ["Logique conditionnelle", "Limitée", "Complète"],
               ["Boucles", "`for_each`, `count`", "Boucles natives"],
               ["Tests", "Outils tiers", "Tests natifs du langage"],
               ["Écosystème", "Très large", "Large, en croissance"],
               ["Courbe d'apprentissage", "Faible si HCL connu", "Faible si le langage est connu"]],
              widths=[4.0, 4.4, 4.6], first_col_bold=True,
              caption="Six différences"),
        defn("Langage dédié", "Langage conçu pour un domaine précis. Il limite les "
                             "possibilités pour rendre les configurations prévisibles, ce "
                             "qui est un avantage ou une contrainte selon le besoin."),
        code("""# Installation et premier projet
pulumi new typescript --name infra-demo

# Commandes essentielles
pulumi preview       # équivalent de plan
pulumi up            # appliquer, avec confirmation
pulumi destroy       # supprimer
pulumi stack ls
pulumi config set environnement production""", "bash", "Six commandes"),
        fig("flow", "Le cycle Pulumi",
            ["Programme TypeScript ou Python",
             "`pulumi preview` : calcul du diff",
             "Confirmation humaine",
             "`pulumi up` : ressources créées",
             "État stocké (Pulumi Cloud ou back-end)",
             "`pulumi destroy` pour supprimer"],
            height=250),

        h(2, "Écrire un programme"),
        p("Un programme décrit des ressources et leurs dépendances par les références "
          "entre objets. La sortie d'une ressource alimente l'entrée d'une autre, ce qui "
          "construit le graphe d'exécution."),
        code("""import * as aws from "@pulumi/aws";

const config = new pulumi.Config();
const environnement = config.require("environnement");

const vpc = new aws.ec2.Vpc("vpc", {
  cidrBlock: "10.0.0.0/16",
  tags: { Projet: "demo", Environnement: environnement },
});

const sousReseau = new aws.ec2.Subnet("app", {
  vpcId: vpc.id,
  cidrBlock: "10.0.1.0/24",
  availabilityZone: "eu-west-3a",
  tags: { Projet: "demo", Environnement: environnement },
});

const groupe = new aws.ec2.SecurityGroup("app", {
  vpcId: vpc.id,
  ingress: [{ protocol: "tcp", fromPort: 443, toPort: 443, cidrBlocks: ["0.0.0.0/0"] }],
  egress: [{ protocol: "-1", fromPort: 0, toPort: 0, cidrBlocks: ["0.0.0.0/0"] }],
});

export const vpcId = vpc.id;
export const sousReseauId = sousReseau.id;""", "ts", "Une infrastructure complète"),
        table(["Concept", "Terraform", "Pulumi"],
              [["Variable", "`variable`", "`pulumi.Config`"],
               ["Sortie", "`output`", "`export const`"],
               ["Module", "`module`", "Fonction ou paquet"],
               ["Boucle", "`for_each`", "Boucle du langage"],
               ["Condition", "`count`", "`if`"],
               ["Secret", "`sensitive = true`", "`pulumi.secret()`"]],
              widths=[3.6, 4.6, 4.8], first_col_bold=True,
              caption="Six équivalences"),

        h(2, "Ce que le langage apporte"),
        p("Un langage généraliste permet d'exprimer des règles complexes sans contorsion. "
          "Il permet aussi d'écrire du code illisible : la discipline reste nécessaire."),
        code("""// Une boucle et une règle métier, sans astuce de DSL
const environnements = ["dev", "staging", "prod"] as const;

const instances = Object.fromEntries(
  environnements.map((env) => [
    env,
    new aws.ec2.Instance(`app-${env}`, {
      ami: "ami-0123456789abcdef0",
      instanceType: env === "prod" ? "t3.small" : "t3.micro",
      subnetId: sousReseau.id,
      tags: { Environnement: env, Projet: "demo" },
    }),
  ])
);

export const adresses = Object.fromEntries(
  Object.entries(instances).map(([env, i]) => [env, i.publicIp])
);""", "ts", "Une logique exprimée naturellement"),
        code("""// Validation d'entrée avant toute création
const environnement = config.require("environnement");
if (!["dev", "staging", "prod"].includes(environnement)) {
  throw new Error(`Environnement invalide : ${environnement}`);
}

// Règle de sécurité vérifiée par le type et par le code
const portsAutorises = environnement === "prod" ? [443] : [443, 8080];""", "ts",
             "Des garde-fous explicites"),
        box("attention", "Une infrastructure n'est pas une application",
            "Un langage généraliste invite à écrire des abstractions élaborées. Or une "
            "infrastructure doit rester lisible par quelqu'un qui ne connaît pas le "
            "programme : privilégiez les fonctions courtes et les noms explicites."),

        h(2, "État et secrets"),
        p("Pulumi stocke l'état sur Pulumi Cloud par défaut, ou dans un back-end "
          "autogéré. Les secrets sont chiffrés dans l'état et dans les sorties."),
        code("""# Back-end autogéré compatible S3
pulumi login s3://mon-pulumi-state

# Secrets chiffrés par le fournisseur de chiffrement
pulumi config set --secret dbPassword 'motdepasse'
pulumi config get --show-secrets dbPassword

# Utilisation dans le programme
const mdp = config.requireSecret("dbPassword");
new aws.rds.Instance("db", { password: mdp, /* ... */ });""", "bash",
             "Trois commandes"),
        table(["Élément", "Stockage", "Chiffrement"],
              [["État", "Pulumi Cloud ou back-end", "Oui"],
               ["Configuration", "Fichier ou back-end", "Secrets chiffrés"],
               ["Sorties", "État", "Selon `secret`"],
               ["Journaux", "Pulumi Cloud", "Selon configuration"]],
              widths=[4.0, 5.0, 4.4], first_col_bold=True,
              caption="Quatre emplacements"),

        h(2, "Tester"),
        p("Parce que l'infrastructure est du code, elle se teste avec les outils du "
          "langage. Les tests d'unité valident les décisions, un test d'intégration "
          "vérifie le déploiement réel dans un environnement jetable."),
        code("""import { describe, it, expect } from "vitest";
import { typeRessource } from "./infra";

describe("taille des instances", () => {
  it("utilise une petite instance en développement", () => {
    expect(typeRessource("dev")).toBe("t3.micro");
  });

  it("utilise une instance plus grande en production", () => {
    expect(typeRessource("prod")).toBe("t3.small");
  });
});""", "ts", "Deux tests utiles"),
        code("""# Test d'intégration dans une pile jetable
pulumi stack init test-$(date +%s)
pulumi up --yes --skip-preview
pulumi destroy --yes
pulumi stack rm --yes""", "bash", "Un cycle complet jetable"),
        table(["Niveau", "Coût", "Détecte"],
              [["Unité", "Nul", "Règles et calculs"],
               ["Preview", "Faible", "Erreurs de configuration"],
               ["Intégration", "Élevé", "Problèmes réels de déploiement"],
               ["Manuel", "Variable", "Cas imprévus"]],
              widths=[3.6, 4.0, 5.2], first_col_bold=True,
              caption="Quatre niveaux de test"),
        box("methode", "Terraform ou Pulumi",
            items=["Le langage de l'équipe est-il un langage généraliste maîtrisé ?",
                   "Y a-t-il des règles métier complexes à exprimer ?",
                   "L'équipe préfère-t-elle un DSL limité ou un langage complet ?",
                   "Les outils existants (politiques, modules) sont-ils réutilisables ?",
                   "Qui maintiendra la configuration dans deux ans ?"]),
    ],
    "keypoints": [
        "Pulumi suit le même cycle que Terraform, avec un langage généraliste.",
        "Les références entre objets construisent le graphe de dépendances.",
        "Config et exports remplacent variables et sorties.",
        "Le langage permet des boucles et des conditions naturelles.",
        "Un langage complet n'exempte pas de lisibilité.",
        "Les secrets sont chiffrés dans l'état.",
        "L'infrastructure se teste comme du code.",
        "Un test d'intégration sur pile jetable est la preuve la plus forte.",
    ],
    "bridge": "L'infrastructure est décrite. Le chapitre suivant configure ce qui est "
              "déjà en place : Ansible.",
    "exercises": [
        ex("Décrire un réseau en TypeScript",
           "Un VPC et deux sous-réseaux doivent être créés.",
           ["Utilisez une boucle.",
            "Étiquetez chaque ressource.",
            "Exportez les identifiants."],
           [("ts", """const zones = ["eu-west-3a", "eu-west-3b"];

const sousReseaux = zones.map((zone, i) =>
  new aws.ec2.Subnet(`subnet-${i}`, {
    vpcId: vpc.id,
    cidrBlock: `10.0.${i + 1}.0/24`,
    availabilityZone: zone,
    tags: { Projet: "demo", Environnement: environnement, Zone: zone },
  })
);

export const sousReseauIds = sousReseaux.map((s) => s.id);"""),
            "Une boucle remplace `count` et rend le lien entre zone et CIDR explicite.",
            "Les sorties exportées servent aux autres piles ou aux applications."]),
        ex("Ajouter une règle métier",
           "Le nombre d'instances dépend de l'environnement.",
           ["Définissez une table.",
            "Validez l'environnement.",
            "Testez la fonction."],
           [("ts", """const dimensionnement = {
  dev:     { type: "t3.micro",  replicas: 1 },
  staging: { type: "t3.small",  replicas: 2 },
  prod:    { type: "t3.small",  replicas: 3 },
} as const;

export function dimensionner(env: string) {
  const plan = dimensionnement[env as keyof typeof dimensionnement];
  if (!plan) throw new Error(`Environnement inconnu : ${env}`);
  return plan;
}"""),
            "La table centralise les décisions : une seule ligne à modifier pour ajuster "
            "un environnement.",
            "L'erreur explicite évite une valeur par défaut dangereuse en production."]),
        ex("Tester avant de déployer",
           "Une règle interdit les ports 22 ouverts à tous en production.",
           ["Écrivez un test sur la fonction de règles.",
            "Ajoutez un contrôle dans la CI.",
            "Vérifiez le cas contraire."],
           [("ts", """import { reglesSecurite } from "./infra";

it("n'ouvre pas SSH en production", () => {
  const regles = reglesSecurite("prod");
  expect(regles.some((r) => r.fromPort === 22)).toBe(false);
});

it("autorise SSH en développement", () => {
  const regles = reglesSecurite("dev");
  expect(regles.some((r) => r.fromPort === 22)).toBe(true);
});"""),
            "Un test qui échoue bloque la CI et empêche la création de la règle.",
            "Tester aussi le cas où l'ouverture est légitime évite de bloquer les "
            "environnements de développement."],
           level="Sécurité"),
    ],
    "quiz": [
        quiz("Quel langage peut-on utiliser avec Pulumi ?",
             ["Uniquement YAML", "TypeScript, Python, Go, C#", "Uniquement HCL", "Uniquement Go"],
             1,
             "Pulumi propose plusieurs langages généralistes."),
        quiz("Quel est l'équivalent de `terraform plan` ?",
             ["`pulumi up`", "`pulumi preview`", "`pulumi destroy`", "`pulumi config`"],
             1,
             "`preview` calcule le diff sans appliquer."),
        quiz("Où sont stockés les secrets Pulumi ?",
             ["En clair dans le code", "Chiffrés dans l'état",
              "Dans un fichier `.env`", "Dans les journaux"],
             1,
             "La configuration secrète est chiffrée avec le fournisseur de chiffrement."),
        quiz("Quel risque introduit un langage généraliste ?",
             ["Moins de tests", "Des abstractions illisibles",
              "Moins de fournisseurs", "Aucun"],
             1,
             "La liberté d'écrire du code complexe doit être maîtrisée."),
    ],
}
