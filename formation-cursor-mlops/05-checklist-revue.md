# Checklist de revue (5 minutes, obligatoire)

Avant merge / avant de dire que c’est bon.

## Compréhension

- [ ] Je peux raconter le changement en 4 phrases à un pair Jedha
- [ ] Je sais quel fichier fait quoi ; aucun fichier « mystère »
- [ ] Aucun nouvel outil / service / image Docker non validé au Plan

## Périmètre

- [ ] Stack IN uniquement (Python, FastAPI, Docker, MLflow, Airflow simple, GHA, etc.)
- [ ] Pas de Kubernetes, Terraform plateforme, Kafka, cloud GPU
- [ ] Pas de refacto hors demande
- [ ] L’existant demandé n’a pas disparu

## Qualité minimale MLOps

- [ ] Secrets absents du git (`.env` ignoré, `.env.example` à jour)
- [ ] Versions d’images / modèles pinnées si téléchargement
- [ ] Un test ou un smoke (`pytest`, `curl /health`, `make demo`)
- [ ] En cas d’échec, un log lisible (pas un traceback seul au milieu d’un DAG)

## Données et métier

- [ ] Pas de PII réelle
- [ ] Seuil / décision métier inchangé sauf demande
- [ ] Human-in-the-loop conservé si c’était le cadre (ex. HOLD_REVIEW)

## Si un item est rouge

Tu écris : `pas merge. corrige X seulement, ne rajoute rien.`
