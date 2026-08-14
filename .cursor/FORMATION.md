# Te servir de Cursor sans perdre la main

Objectif : l'IA accélère ton travail de data engineer / MLOps, toi tu restes celui qui comprend, décide et assume.

Ces fichiers ne changent pas ton README GitHub. Ils servent à Cursor.

## 1. Le contrat

Tu es le responsable. L'agent propose, explique, puis attend.

Sans `GO` (ou `implémente` / `fais cette étape`), il ne doit pas modifier le code.

Tu n'acceptes une action que si tu peux :

- la relire ;
- l'expliquer à un recruteur ou un collègue ;
- la déboguer si elle casse lundi matin.

Si tu ne peux pas, ce n'est pas encore dans ton scope. Demande une version plus simple.

## 2. Où coller les règles (important)

Les règles de ce dépôt ne s'appliquent **qu'ici** (profil GitHub). Pour tes vrais projets (`HPP-Prediction-Lean`, `CathQ`, etc.) :

1. Ouvre Cursor → **Customize → Rules → User Rules**.
2. Colle le contenu de [`USER_RULES_A_COPIER.md`](USER_RULES_A_COPIER.md).
3. Dans chaque repo métier, copie aussi le dossier `.cursor/rules/` si tu veux le même comportement projet par projet.

Sans ça, l'agent retombera dans le mode « j'implémente tout tout de suite ».

## 3. Les 3 modes Cursor (desktop)

| Mode | Quand | Ce qui se passe |
|---|---|---|
| **Ask** | Comprendre un fichier, un DAG, une erreur | Réponses, pas d'édits |
| **Plan** | Nouvelle brique MLOps, choix d'archi | Plan à valider |
| **Agent** | Après GO, une étape bornée | Il code, tu relis le diff |

Cloud Agent (cursor.com/agents) agit tout seul : commence toujours par *« propose un plan, n'implémente pas »* tant que tu n'as pas validé.

## 4. Recette d'une bonne consigne

Copie-colle et remplis :

```text
Contexte : [projet + ce qui existe déjà]
Objectif métier : [ce que ça doit changer pour l'utilisateur / la donnée]
Contrainte : reste dans mon stack Jedha (Python, Docker, FastAPI, dbt/Airflow/MLflow selon le cas)
Livrable : PLAN seulement. Liste les fichiers, les risques, ce que je dois valider.
N'implémente rien tant que je n'ai pas écrit GO.
```

Ensuite, étape par étape :

```text
GO pour l'étape 2 seulement (le DAG Airflow).
Ne touche pas au Dockerfile ni à la CI.
Explique-moi chaque fichier modifié et comment je teste en local.
```

## 5. Prompts prêts à l'emploi

### Comprendre sans rien casser

```text
Explique ce fichier comme à un data engineer Jedha.
Quel est le contrat de données ? Où ça peut casser en prod ?
Ne modifie rien.
```

### Review MLOps

```text
Review ce pipeline (entraînement → registry → API).
Points : reproductibilité, fuite de données, secrets, drift, CI.
Reste dans Docker + MLflow + FastAPI. Pas de Kubernetes.
Ne code pas. Donne un plan d'amélioration par priorité.
```

### Qualité de données

```text
Propose des tests de qualité (schéma, nulls, volumes) branchés sur la CI GitHub.
Montre un exemple dbt test OU pytest, au choix le plus proche de ce repo.
PLAN seulement.
```

### Drift / monitoring

```text
Je veux détecter un data drift sur [colonnes].
Solution junior : script Python + métrique simple + alerte log/MLflow.
Pas de plateforme cloud. PLAN, puis j'écrirai GO.
```

### Debug

```text
Voici l'erreur / le log.
Reproduis si possible, donne la cause, propose UN correctif minimal.
Attends mon GO avant de patcher.
```

## 6. Tes leviers de contrôle

- **Borne le périmètre** : « seulement `train.py` », « pas de nouveau dossier ».
- **Interdis la stack hors Jedha** : « pas de K8s, pas de Terraform, pas de nouvel outil ».
- **Exige la vérif** : « commande exacte pour tester en local ».
- **Relis le diff** fichier par fichier. Si tu ne comprends pas une ligne, demande *« explique cette fonction, ne change rien »*.
- **Refuse le « pendant que j'y suis »** : une étape = un GO.

## 7. Périmètre Jedha (rappel)

**Data engineer :** gouvernance / RGPD, Spark SQL, ELT, dbt, Airflow, lakehouse, tests + CI, pipelines vers le ML / RAG.

**MLOps :** Docker, MLflow, GitHub Actions, FastAPI, monitoring / réentraînement, eval LLM légère, coûts et conformité (principes).

**Hors scope par défaut :** Kubernetes, Terraform complexe, Kafka prod, fine-tuning GPU, feature store, serving type KServe.

L'agent doit proposer l'équivalent simple (Compose, Actions, MLflow local) plutôt que l'outil « senior ».

## 8. Signal que ça dérape

L'agent :

- crée 12 fichiers alors que tu as demandé un plan ;
- ajoute Prefect / Kedro / SageMaker alors que tu as MLflow ;
- « améliore » des fichiers hors sujet ;
- ne dit pas comment tester.

Réponse type :

```text
Stop. Repars du protocole : PLAN uniquement, scope Jedha, fichiers listés.
N'implémente rien. Montre-moi ce que tu allais faire.
```
