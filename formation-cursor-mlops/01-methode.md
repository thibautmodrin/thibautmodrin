# Méthode : Plan → GO → code → revue

Objectif : l’IA ne te met jamais devant le fait accompli.

## Les 4 temps

```text
1. CADRER     tu décris le besoin, les contraintes, le critère de succès
2. PLANIFIER  l’IA propose 1 à 3 options dans TON stack (sans coder)
3. VALIDER    tu dis GO / option N / simplifie / hors sujet
4. EXÉCUTER   l’IA code par petits pas ; tu relis avant de merger
```

Sans le mot **GO** (ou équivalent : `ok`, `option 2`, `implémente`), rien n’est modifié.

## Ce que tu donnes à chaque demande

Un brief court suffit :

- **Contexte** : quel dépôt, quelle étape du pipeline (ingest, transform, train, serve, monitor)
- **But** : une phrase
- **Contraintes** : stack déjà en place, pas de nouvel outil, pas de cloud payant, etc.
- **Succès** : comment tu sauras que c’est bon (`pytest` vert, endpoint `/health`, DAG Airflow parse)
- **Hors scope** : ce que tu ne veux pas (Kubernetes, nouveau SaaS, refacto globale)

Exemple :

> CathQ. J’ai un drift détecté mais le réentraînement Airflow n’est pas clair.  
> But : documenter + corriger le DAG pour que je puisse l’expliquer à l’oral.  
> Contraintes : Python, Airflow local, MLflow déjà là. Pas de K8s.  
> Succès : `airflow dags list` montre le DAG, un test vérifie le trigger drift.  
> Mode : plan d’abord, attends mon GO.

## Ce que l’IA doit te rendre avant le GO

1. **Compréhension** : reformulation en 3 lignes
2. **Options** (1 à 3) : stack, fichiers touchés, ce que TU dois savoir maintenir
3. **Hors périmètre** : ce qu’elle a écarté et pourquoi
4. **Risques** : données, secrets, coût cloud, casse de l’existant
5. **Plan d’implémentation** : étapes numérotées, petites

Si ce bloc n’est pas là, tu réponds : `plan d’abord, ne code pas`.

## Tes réponses types

| Tu écris | Effet |
|---|---|
| `plan d’abord` | Interdit le code |
| `GO` / `ok option 2` | Autorise uniquement le plan validé |
| `simplifie` | Une option plus petite, même stack |
| `explique-moi X avant` | Pédagogie, toujours pas de code |
| `hors scope` | Elle recadre vers ce que tu sais déjà |
| `stop` | Elle s’arrête, résume l’état |

## Taille des changements

- Un objectif = une PR / un commit logique
- Pas de « tant qu’on y est » (nouveau framework, refacto, docs marketing)
- Si le plan dépasse ~10 fichiers : tu exiges un découpage

## Tu restes lead, l’IA est pair junior

Tu décides :

- l’architecture (même simple)
- l’ajout d’un outil
- tout ce qui touche prod, secrets, coût, données personnelles

L’IA peut :

- lire le code existant **avant** de proposer
- écrire le code du plan validé
- ajouter des tests dans le style du repo
- t’expliquer comme un formateur Jedha (pourquoi, pas seulement comment)
