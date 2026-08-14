# Travailler avec un agent IA sans lui laisser le volant

Ce dossier est le mode d'emploi côté humain du contrat défini dans [`AGENTS.md`](../../AGENTS.md).
Objectif : gagner du temps sur des tâches de data engineering et de MLOps **sans** accumuler du code
que je ne saurais pas défendre, ni laisser un outil décider de mon architecture à ma place.

## Le principe en une phrase

> L'agent est un ingénieur junior très rapide, très cultivé, sans mémoire d'un jour sur l'autre et
> sans enjeu à ma place. C'est moi qui décide du périmètre, lui qui produit et justifie.

Un agent laissé libre a un biais constant : il ajoute. Une dépendance, une abstraction, un outil « de
l'état de l'art ». Sur un projet de certification ou une mission, ce biais coûte cher : il produit du
code défendable par personne. Tout le dispositif de ce dépôt sert à inverser ce biais.

## Parcours de lecture

| Étape | Document | Ce que j'y trouve |
|---|---|---|
| 1 | [`01-mode-operatoire.md`](01-mode-operatoire.md) | La boucle de travail, les modes Cursor, comment reprendre le contrôle |
| 2 | [`02-bibliotheque-prompts.md`](02-bibliotheque-prompts.md) | Quoi demander, dans quels termes, avec des exemples data / MLOps |
| 3 | [`03-garde-fous.md`](03-garde-fous.md) | Ce qui bloque réellement une action, et ce qui n'est qu'une consigne |
| 4 | [`04-pieges-data-ml.md`](04-pieges-data-ml.md) | Les erreurs qu'un agent commet spécifiquement sur les projets ML |
| 5 | [`05-installer-dans-un-projet.md`](05-installer-dans-un-projet.md) | Déployer ce kit dans un autre dépôt |

## Ce que contient le kit

```text
AGENTS.md                              contrat de collaboration, chargé automatiquement
.cursor/rules/00-invariants.mdc        invariants durs, actifs en permanence
.cursor/rules/10-perimetre-...mdc      référentiel de compétences — le fichier à tenir à jour
.cursor/rules/20-python-qualite.mdc    conventions, activées sur les fichiers .py
.cursor/rules/30-donnees-et-...mdc     pipelines, DAGs Airflow, SQL, validation
.cursor/rules/40-mlops-...mdc          Docker, CI, MLflow, services, monitoring
.cursor/rules/50-notebooks.mdc         notebooks
.cursor/commands/*.md                  sept commandes `/` réutilisables
.cursor/permissions.json               ce qui passe seul et ce qui demande une validation
.cursor/hooks.json + hooks/            garde-fou qui bloque réellement les actions destructrices
docs/assistant/                        ce mode d'emploi
docs/assistant/modeles/cursorignore    modèle de fichiers à soustraire à l'agent
scripts/installer-kit.sh               installation du kit dans un autre dépôt
```

## Les trois réflexes à garder

**Le périmètre est un fichier, pas une intention.**
[`.cursor/rules/10-perimetre-competences.mdc`](../../.cursor/rules/10-perimetre-competences.mdc)
est la référence que l'agent lit à chaque session. Quand j'apprends un outil, je le déplace de
`[à apprendre]` vers `[acquis]`. Quand je constate qu'un outil me coûte plus qu'il me rapporte, je le
descends. Un référentiel jamais mis à jour redevient du décor en quelques semaines.

**« Ok » valide un plan, pas une direction.**
Le moment où l'on perd la main n'est pas celui où l'agent propose quelque chose d'énorme : c'est
celui où l'on répond « vas-y » à un plan qu'on n'a pas lu. Si je n'ai pas lu le plan, je ne l'ai pas
validé.

**Ce que je ne peux pas expliquer, je ne le garde pas.**
C'est le seul critère qui résiste au temps. Il ne dépend ni de la mode technique, ni de la qualité de
l'agent. Utiliser `/expliquer` puis `/oral` avant de merger coûte quelques minutes et évite la seule
situation vraiment coûteuse : découvrir devant un jury ou un client que le code est le mien sans que
le raisonnement le soit.
