# 2. Utiliser Cursor sans perdre la main

## Les trois modes (dans cet ordre)

### Ask (lecture seule)

Pour **comprendre** : un repo, un bug, un DAG, un Dockerfile.

Tu n’acceptes aucun diff. Idéal en début de journée, en onboarding, avant
un entretien sur un projet.

Exemple :

> Lis le repo. Résume le flux de données (brut → features → modèle → API).
> Quels fichiers je dois maîtriser en premier ? Ne propose pas de refactor.

### Plan (conception)

Pour **décider**. Cursor pose un plan ; toi tu coupes ce qui est trop gros.

Exemple :

> Objectif : ajouter un check de drift sur les features d’inférence.
> Contraintes : pandas + pytest, pas de nouvelle lib, pas de k8s.
> Livrable : plan uniquement, 5 puces, fichiers concernés, risques.

Tu modifies le plan à la main (« sans Evidently », « un seul fichier
`src/monitoring/drift.py` »), puis tu dis `implémente ce plan, rien d'autre`.

### Agent (écriture)

Pour **exécuter un plan déjà validé**, sur un **périmètre de fichiers**.

Mauvais : « mets le projet en prod MLOps ».  
Bon : « implémente `compute_psi` dans `src/monitoring/drift.py` + 3 tests
dans `tests/test_drift.py`. Ne touche à rien d’autre. »

## Chat vs Composer / Agent

- **Chat Ask** : questions, revue, explications.
- **Agent** : modifications. Toujours relire l’onglet Diff fichier par fichier.
- N’accepte pas un diff en bloc. Ouvre les fichiers, cherche ce que tu ne
  comprends pas, redemande.

## Contexte : ce que tu @ mentionnes

Plus le contexte est précis, moins il invente.

- `@fichier` plutôt que tout le repo ;
- `@docs` ou un README si le contrat data y est décrit ;
- colle un traceback plutôt que « ça marche pas ».

Évite de coller des secrets, des dumps patients, des `.env`.

## User Rules vs Project Rules

| | Où | Effet |
| --- | --- | --- |
| **User Rules** | Settings Cursor | Tous tes repos |
| **Project Rules** | `.cursor/rules/*.mdc` | Ce repo seulement |

Colle [`USER_RULES.md`](USER_RULES.md) une fois. Recopie
[`modele-projet/.cursor/`](modele-projet/.cursor/) dans CathQ, HPP, ERP, Vitizen
et tes futurs repos pro.

## Cloud Agent / « go and do it »

Un agent cloud peut commit / PR tout seul. Pour **apprendre et rester maître**,
préfère le Cursor local :

1. Ask / Plan ;
2. Agent borné ;
3. tu lances pytest / docker toi-même ;
4. tu commit toi-même.

Réserve l’agent autonome aux tâches que tu as déjà faites 3 fois à la main
(renommer, ajouter un test calqué sur l’existant).
