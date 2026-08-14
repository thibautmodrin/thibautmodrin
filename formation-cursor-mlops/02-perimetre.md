# Périmètre de compétences (à tenir à jour)

Profil de référence : **junior Data / ML Engineer**, parcours Jedha Fullstack puis Lead, projet MLOps type CathQ.

Modifie ce fichier quand tu apprends un outil pour de vrai (pas juste « vu en cours »). L’assistant s’aligne dessus.

Légende :

- **IN** : il peut proposer et, après GO, implémenter
- **PONT** : il explique avec tes briques actuelles ; n’implémente que si tu dis explicitement « je veux apprendre X »
- **OUT** : il n’implémente pas ; 5 lignes max d’explication si tu demandes

## IN — tu dois pouvoir relire et maintenir

| Domaine | Outils / pratiques |
|---|---|
| Langage | Python 3.10+, scripts, packages `src/`, `pyproject.toml` |
| Data wrangling | pandas, numpy, SQL, SQLAlchemy |
| ML | scikit-learn, XGBoost, métriques métier, seuils, human-in-the-loop |
| Qualité data | pytest, contrôles de schéma, Great Expectations (niveau projet) |
| Tracking | MLflow (runs, params, metrics, artifacts, model registry simple) |
| Serving | FastAPI, Pydantic, Streamlit |
| Conteneurs | Dockerfile, docker-compose, `.env.example` |
| Orchestration | DAGs Airflow **simples** (local / docker-compose) |
| CI | GitHub Actions (lint, tests, smoke) |
| Cloud Jedha | S3 + boto3, RDS basique — pas d’org AWS complète |
| Big data cours | Spark DataFrames / Spark SQL sur un use case pédagogique |
| GenAI projet | RAG simple (ingest → embeddings → Chroma → FastAPI), prompts sourcés |
| Git | branches, PR, Makefile, pas de force-push sur main |

Principes IN :

- pipelines batch lisibles (raw → clean → features → train → eval → serve)
- monitoring drift **simple** (PSI / stats, pas une usine)
- rollback : version de modèle + config, pas un service mesh
- secrets hors git, `.env.example` seulement

## PONT — apprendre avec un filet, jamais par surprise

| Sujet | Pont depuis ce que tu sais déjà |
|---|---|
| dbt | SQL + tests de qualité que tu fais déjà à la main |
| DVC | Git + artifacts MLflow : versionner data/modèle sans nouveau cloud |
| Evidently | tes scripts de drift CathQ, en plus joli |
| dbt + Airbyte | pandas/ETL + Airflow : ingestion/transform industrialisés |
| Terraform 1 fichier | docker-compose : déclarer 2-3 ressources, pas un compte AWS |
| Hugging Face Spaces | Docker + FastAPI que tu déploies déjà en local |
| Kubernetes concepts | Docker : « plusieurs conteneurs + redémarrage », sans cluster |
| Delta Lake / Iceberg | Parquet + S3 que tu connais |

Règle PONT : une page d’explication + un mini-exemple **optionnel**. Zéro migration du projet tant que tu n’as pas écrit `GO j’apprends X`.

## OUT — pas d’implémentation

- Kubernetes prod (Helm, operators, Ingress, autoscaling)
- Terraform / CDK « plateforme » (VPCs, IAM org, multi-compte)
- Kafka, Flink, Spark Streaming, event-driven complexe
- Feature stores (Feast, Tecton), SageMaker Pipelines, Vertex AI
- Fine-tuning GPU / distributed training
- Agents LangGraph complexes, LLMOps multi-modèles avec budgets prod
- Refonte totale « on passe sur Databricks / Snowflake / Prefect Cloud »
- Tout ce que tu ne pourrais pas debugger seul la semaine suivante

Si une option OUT semble « la vraie solution entreprise », l’assistant la nomme en une phrase puis **revient à une option IN**.

## Garde-fous métier (non négociables)

- Pas de données personnelles réelles dans les notebooks / git
- Modèle = aide à la décision, pas dispositif médical / décision automatique opaque
- Coûts cloud : pas de GPU, pas de cluster, pas d’instance 24/7 sans ton OK
- Pas d’écrasement de l’existant « pour faire plus propre » hors demande
