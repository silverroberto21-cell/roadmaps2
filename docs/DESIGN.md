# Charte graphique et modèle de mise en page

## Identité

| Élément | Valeur | Justification |
|---|---|---|
| Éditeur | ESPRITROPIC COMMUNITY | `Informations éditoriale.md` |
| Signataire | YKABAUTH | idem |
| Site | https://espritropic.rf.gd | idem |
| Logo | monogramme `<R>`, variantes noire et blanche | fichiers PNG du dépôt |
| Collection | « Bibliothèque technique Espritropic » | intitulé éditorial de la collection |

Le logo fourni est monochrome (noir ou blanc, fond transparent). La palette est donc
construite autour de deux couleurs d'accent compatibles avec un logo noir et blanc,
et non inventées à partir d'un logo coloré.

## Palette

| Rôle | Nom | Hex | Usage |
|---|---|---|---|
| Primaire | Bleu encre | `#0F2E4C` | couvertures, bandeaux de partie, titres de niveau 1 |
| Primaire clair | Bleu ardoise | `#274B6D` | sous-titres, en-têtes de tableaux |
| Accent | Ambre | `#E0A21B` | filets, numéros de chapitre, encadrés « À retenir » |
| Accent clair | Sable | `#FBF3E2` | fond des encadrés d'objectifs et de définitions |
| Neutre foncé | Graphite | `#1F2933` | corps de texte |
| Neutre moyen | Gris | `#5B6770` | légendes, notes, métadonnées |
| Neutre clair | Brume | `#E8EDF1` | fond des tableaux (lignes alternées), fond du code |
| Succès | Vert | `#2F7D5B` | encadrés « bonne pratique » |
| Alerte | Rouge brique | `#A63A32` | encadrés « attention », erreurs fréquentes |

## Typographie

| Usage | Police | Corps | Interligne | Style Word |
|---|---|---|---|---|
| Corps de texte | Times New Roman | 11 pt | exact 16,2 pt | `Corps` |
| Titre de chapitre | Arial | 22 pt gras | exact 26 pt | `Titre 1` |
| Titre de section | Arial | 14 pt gras | exact 19 pt | `Titre 2` |
| Sous-section | Arial | 11,5 pt gras | exact 15,5 pt | `Titre 3` |
| Sous-sous-section | Arial | 10,5 pt gras italique | exact 14 pt | `Titre 4` |
| Code | Courier New | 9 pt | exact 11,8 pt | `Code` |
| Légendes | Arial | 8,5 pt italique | exact 11 pt | `Légende` |
| Tableaux | Arial | 9,5 pt | exact 13 pt | `Tableau` |

Times New Roman, Arial et Courier New sont des polices « métriquement compatibles »
avec Liberation Serif, Liberation Sans et Liberation Mono : la pagination reste stable
sur les postes où les polices Microsoft ne sont pas installées.

## Mise en page

- Format A4 portrait, marges : haut 2,4 cm, bas 2,2 cm, gauche 2,5 cm, droite 2,2 cm.
- Zone de texte : 16,3 × 25,1 cm (462 × 711,5 pt).
- En-tête : titre du cours à gauche, titre de partie à droite, filet ambre.
- Pied de page : mention éditoriale à gauche, pagination continue à droite.
- Tous les styles sont des **styles natifs Word** nommés, liés à la table des matières
  automatique (champs `TOC`, `PAGEREF`, numérotation de pages).
- Pagination continue unique de la couverture à la dernière annexe.
