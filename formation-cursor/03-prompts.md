# 3. Prompts métier (copie-colle)

Remplace les `[crochets]`. Garde les 4 phrases de garde-fou.

## Diagnostic d’un repo (Ask)

```
Mode Ask. Ne modifie rien.
Repo : Data Engineer / MLOps junior Jedha.
Cartographie :
1. flux de données (sources → transform → modèle/API)
2. points de défaillance (schéma, drift, CI, secrets)
3. ce qui est déjà industriel vs prototype
4. 3 améliorations DANS mon scope (Python, Compose, Actions, pytest), classées par impact / effort
N'évoque k8s / Terraform / Kafka que comme piste hors scope.
```

## Plan d’une feature (Plan)

```
Propose, n'implémente pas.
Objectif métier : [ex. alerter si le taux de valeurs manquantes dépasse 5 % en inférence]
Contraintes :
- stack actuelle du repo uniquement
- Docker Compose + GitHub Actions + pytest
- pas de nouvelle dépendance
- RGPD : pas de log de données personnelles
Livrable :
- plan 5 puces
- fichiers à créer/modifier
- risques
- hors-scope
- ce que je dois valider
```

## Implémentation bornée (Agent)

```
Implémente UNIQUEMENT le plan validé ci-dessous.
Périmètre fichiers : [liste]
Ne pas : nouvelles libs, refactor, autres features, commit.
Ensuite : résume en 8 lignes ce que je dois savoir pour le défendre en revue.
Commandes de vérif que je lance moi-même.
```

## Debug

```
Mode Ask d'abord.
Voici l'erreur (traceback) :
[colle]
Voici ce que j'ai lancé : [commande]
Hypothèses classées du plus probable au moins probable.
Pour chaque hypothèse : comment JE la vérifie (commande).
Ne patch pas tant que je n'ai pas choisi l'hypothèse.
```

## Qualité data / data contract

```
Propose un contrat de données pour [table/dataset] :
- champs, types, nullabilité
- 5 tests pytest ou dbt tests équivalents
- ce qui casse si le schéma source évolue
Reste simple (pas de framework lourd). Plan seulement.
```

## Pipeline / Airflow / job

```
J'ai déjà le script [chemin].
Propose un DAG Airflow (ou un workflow Actions si un cron CI suffit) qui :
- lance ce script
- échoue proprement
- n'écrase pas les sorties (partition date)
Compare Airflow vs GitHub Actions scheduled pour CE cas.
Recommande le plus simple. Plan seulement.
```

## MLOps (modèle déjà entraîné)

```
Le modèle est dans [chemin]. L'API est [chemin].
Objectif : tracking MLflow local + sauvegarde du run_id dans l'API + un test
qui vérifie que le modèle charge.
Pas de registry cloud, pas de k8s.
Plan, puis j'approuve.
```

## Drift / monitoring

```
Features d'entrée : [liste].
Propose un check de drift simple (stats + seuil), un job batch, un test.
Pas d'Evidently / WhyLabs sauf si déjà dans le repo.
Explique PSI ou l'alternative en 5 lignes niveau Jedha.
Plan seulement.
```

## RAG (Vitizen-style)

```
Stack : Chroma + FastAPI + [LLM].
Objectif : [ex. citer les sources, refuser si score trop bas].
Contraintes : pas de fine-tune, pas de k8s, secrets hors git.
Plan d'évaluation (5 questions gold + critère de réussite).
N'implémente pas l'indexation complète sans mon go.
```

## Revue de diff (après Agent)

```
Mode Ask. Voici le diff / les fichiers [liste].
Pour chaque fichier : à quoi il sert, risque, est-ce dans mon scope.
Signale toute lib nouvelle, tout secret, tout hors-périmètre.
Questions que l'on me poserait en entretien sur ce diff.
```

## Recadrage (quand il s’emballe)

```
Stop. Trop large.
Repars de zéro avec UNE brique : [brique].
Fichiers autorisés : [liste].
Stack : celle du repo. Pas de nouvelle lib.
Plan de 5 puces, puis tu attends.
```
