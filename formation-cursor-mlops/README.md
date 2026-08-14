# Kit : rester maître avec un assistant Cursor (Data Engineer / MLOps)

Ce dossier te forme à utiliser Cursor comme **pair junior**, pas comme pilote automatique.

Tu restes le décideur. L’IA propose, explique, puis n’agit **que** si tu valides. Les actions restent dans le périmètre Jedha / junior MLOps calé sur tes projets (CathQ, FastAPI, Docker, MLflow, Airflow, RAG).

## Mise en place (15 min)

1. Copie le contenu de [`USER_RULE.md`](USER_RULE.md) dans Cursor : **Customize → Rules → User Rules**.  
   C’est la pièce la plus importante : elle s’applique **à tous tes dépôts**.
2. Dans un projet de travail, copie `.cursor/rules/` et `.cursor/commands/` (voir [`copier-dans-un-projet.md`](copier-dans-un-projet.md)).
3. Lis dans l’ordre :
   - [`01-methode.md`](01-methode.md) — Plan → GO → code → revue
   - [`04-modes-cursor.md`](04-modes-cursor.md) — Ask / Plan / Agent
   - [`02-perimetre.md`](02-perimetre.md) — ce que tu maîtrises vs hors scope
   - [`03-prompts.md`](03-prompts.md) — phrases à coller
   - [`05-checklist-revue.md`](05-checklist-revue.md) — comment relire sans te faire dépasser
   - [`06-premiere-session.md`](06-premiere-session.md) — 45 min d’entraînement

Commandes slash (dans un repo qui contient `.cursor/commands/`) : `/plan-avant-code`, `/go-implementer`, `/revue-humain`.

## Règle d’or

Si tu ne peux pas **expliquer** un changement à un collègue Jedha, tu ne le merges pas. L’IA accélère ; toi tu assumes.
