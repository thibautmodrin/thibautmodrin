# Bibliothèque de prompts

Les sept commandes du dépôt couvrent les demandes récurrentes. En dessous, des formulations prêtes à
l'emploi pour les situations de data engineering et de MLOps, avec le principe qui les rend efficaces.

## Les commandes disponibles

À taper dans le chat, elles s'invoquent avec `/` :

| Commande | Usage |
|---|---|
| `/cadrer` | Transformer une demande floue en plan validable, sans une ligne de code |
| `/expliquer` | Comprendre un code au point de pouvoir le réécrire et le défendre |
| `/oral` | Préparer la soutenance d'un choix technique, questions de jury incluses |
| `/audit-mlops` | État des lieux du dépôt, priorités classées selon mon périmètre |
| `/hors-perimetre` | Instruire l'ajout d'un outil que je ne maîtrise pas : gain réel, coût, alternative |
| `/simplifier` | Débusquer la sur-ingénierie et proposer la version défendable |
| `/revue-pr` | Relire mes changements avant d'ouvrir une pull request |

## Ce qui fait la différence dans une formulation

**Donner le critère de réussite.** « Améliore la préparation des données » n'a pas de fin. « Fais que
`prepare_data.py` échoue explicitement si une colonne attendue manque, avec un test qui le prouve » a
un critère vérifiable.

**Interdire explicitement ce qu'on ne veut pas.** Un agent optimise ce qu'on lui demande, pas ce qu'on
suppose évident. « Sans ajouter de dépendance » et « sans toucher au `Dockerfile` » économisent une
itération complète.

**Demander l'alternative écartée.** C'est le prompt le plus rentable de tous : il révèle si la
solution proposée est un choix ou un réflexe. « Quelle est la version plus simple, et qu'est-ce qu'on
perd en la choisissant ? »

**Demander de citer le code.** Un agent qui doit citer des chemins et des lignes invente beaucoup
moins qu'un agent qui raisonne dans le vide.

## Cadrage d'un besoin

```text
Contexte métier : <le problème, l'utilisateur, la décision à prendre>
Contrainte : <délai, données disponibles, environnement de déploiement>
Ce que j'ai déjà : <fichiers concernés>
Ne propose pas de solution technique tout de suite. Commence par me dire quelles décisions
doivent être prises, dans quel ordre, et laquelle est irréversible.
```

## Préparation de données

```text
Lis @src/prepare_data.py et @src/config.py.
Liste les hypothèses implicites de ce script sur les données d'entrée (colonnes, types, plages,
unicité, valeurs manquantes) — sans rien modifier.
Pour chacune : ce qui se passe aujourd'hui si l'hypothèse est violée, et si l'échec est silencieux
ou bruyant. Classe par gravité. Les échecs silencieux d'abord.
```

## Vérification de leakage

```text
Lis @src/train.py et @src/prepare_data.py.
Cherche uniquement les fuites de données : transformation ajustée avant le découpage, variable
connue seulement après le moment de la prédiction, découpage aléatoire sur des données
temporelles, agrégat calculé sur l'ensemble complet.
Pour chaque suspicion : la ligne, pourquoi c'est une fuite, et comment le prouver
expérimentalement. Ne corrige rien.
```

C'est le prompt à passer avant toute soutenance. Le leakage est l'erreur qui invalide un résultat sans
faire échouer un test.

## Métriques et seuil de décision

```text
Ma cible est déséquilibrée (<prévalence>). Le coût d'un faux négatif est <...>, celui d'un faux
positif est <...>.
Explique quelle métrique traduit ce coût, et pourquoi les autres induiraient en erreur ici.
Puis dis-moi comment choisir le seuil de décision, quel critère écrire dans le code, et ce qu'il
faut tracer dans les artefacts pour que le choix soit défendable dans six mois.
Ne modifie aucun fichier.
```

## Débogage d'un pipeline

```text
Symptôme : <ce que j'observe, avec le message exact ou la valeur inattendue>
Attendu : <ce que je devrais observer>
Contexte : @<fichiers>
Donne-moi trois hypothèses classées par probabilité, et pour chacune la vérification la moins
coûteuse qui permet de l'écarter. Je lance les vérifications moi-même. Ne corrige rien avant
qu'on ait identifié la cause.
```

Faire produire des hypothèses plutôt qu'un correctif évite le pire scénario du débogage assisté :
plusieurs corrections empilées sur un symptôme mal compris.

## Test à écrire

```text
Lis @src/<module>.py.
Quel est le test qui, s'il existait, m'aurait alerté le plus tôt sur une régression réelle ?
Un seul test, pas une suite. Explique ce qu'il vérifie et ce qu'il ne vérifie pas.
Utilise pytest et un jeu de données synthétique en fixture, sans accès réseau ni donnée réelle.
```

## Revue de sécurité et de confidentialité

```text
Passe en revue ce dépôt sur un seul angle : ce qui ne devrait pas y être.
Secret ou jeton en clair, valeur réelle dans .env.example, donnée personnelle ou identifiante,
chemin absolu de ma machine, URL interne, sortie de notebook contenant des données, fichier de
données ou artefact committé par erreur.
Cite chaque fichier et chaque ligne. Ne corrige rien : je veux d'abord la liste complète.
```

## Documentation orientée soutenance

```text
Écris la section « <titre> » du README à partir du code réel, en français.
Contraintes : les chiffres viennent des artefacts du dépôt (cite le fichier source), les limites
sont énoncées explicitement, aucune affirmation que le code ne démontre pas.
Si une information te manque, laisse un marqueur TODO plutôt que de l'inventer.
```

La dernière phrase est essentielle : sans elle, un agent comble les trous par du plausible, et le
plausible dans un livrable de certification est un piège.

## Prompt de reprise en main

À garder sous la main pour les moments où la session part en vrille :

```text
Arrête-toi. Ne modifie plus rien.
Liste les fichiers que tu as modifiés depuis le début, avec en une ligne ce que fait chaque
changement et s'il faisait partie de ce que j'avais validé.
Dis-moi ensuite ce que tu recommandes de garder, et ce qu'il vaut mieux annuler.
```
