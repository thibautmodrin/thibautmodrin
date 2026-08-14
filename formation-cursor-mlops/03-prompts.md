# Prompts à coller (tu restes aux commandes)

Adapte le nom du repo et l’objectif. Garde les phrases en gras : ce sont les freins.

## Démarrage d’une tâche

```text
Lis d’abord le code existant. Ne change rien.

Contexte : [repo / dossier]
Objectif : [1 phrase]
Contraintes : rester dans mon stack Jedha (Python, pandas, sklearn/XGBoost, FastAPI, Docker, MLflow, Airflow, pytest, GHA). Pas de nouvel outil.
Succès : [commande ou comportement attendu]

**Plan d’abord. Attends mon GO.** Options : 1 recommandée + 1 plus simple. Signale tout hors périmètre.
```

## Recadrer si elle code trop vite

```text
Stop. Annule l’élan d’implémentation. Plan uniquement.
Dis-moi : fichiers touchés, ce que je dois savoir maintenir, risques, option plus simple.
```

## Recadrer si elle sort du stack

```text
Hors scope. Reviens à ce que je maîtrise déjà (voir formation-cursor-mlops/02-perimetre.md).
Propose le pont : même besoin, outils IN seulement.
```

## Demander l’explication avant le code

```text
Explique-moi comme un formateur Jedha :
- pourquoi cette étape existe dans un pipeline MLOps
- ce qui casse si on s’en passe
- comment je debug si ça échoue
Ne code pas encore.
```

## Autoriser un petit pas

```text
GO sur l’option 2 uniquement.
Ne touche pas aux fichiers hors plan.
Ajoute ou adapte les tests existants.
À la fin : résumé de ce que je dois relire, et la commande pour vérifier.
```

## Revue de ton propre travail (après un diff)

```text
Ne code pas. Fais une revue junior-lead :
- est-ce que je peux expliquer chaque fichier modifié ?
- y a-t-il un outil ou un pattern que je n’ai pas validé ?
- y a-t-il de la magie (config opaque, extraire un zip, télécharger un modèle sans pin) ?
- que tester à la main en 5 minutes ?
```

## Tâches types Data Engineer / MLOps

**Qualité / contrat de données**

```text
Plan : ajouter des contrôles de schéma sur [table/fichier] avec pytest ou Great Expectations déjà dans le repo.
Pas de nouvelle lib. Attends GO.
```

**API modèle**

```text
Plan : endpoint FastAPI /predict aligné sur le payload existant, validation Pydantic, test httpx.
Pas de changement de modèle. Attends GO.
```

**CI**

```text
Plan : GitHub Action qui lance lint + pytest sur Python 3.11.
Pas de deploy auto. Attends GO.
```

**Drift / réentraînement**

```text
Plan : rendre explicite le if drift → retrain dans le DAG Airflow existant.
Une métrique simple, un log clair, un test du graphe. Pas de K8s. Attends GO.
```

**RAG**

```text
Plan : ingest → chunk → embeddings → Chroma → query FastAPI, réponses sourcées.
Pas d’agent, pas de fine-tune. Attends GO.
```
