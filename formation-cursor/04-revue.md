# 4. Revue : comment garder la maîtrise

Un Agent qui « marche » n’est pas un Agent **compris**. La revue est le vrai
geste MLOps : tu es le dernier contrôle avant que du code touche des données.

## Checklist (2 minutes par PR / diff)

Coche mentalement. Si une case est non, tu n’acceptes pas.

- [ ] Je peux dire l’objectif métier en une phrase.
- [ ] Je liste les fichiers touchés (pas de surprise hors périmètre).
- [ ] Pas de nouvelle dépendance, ou je l’ai validée.
- [ ] Pas de secret, token, `.env`, dump patient / client.
- [ ] Le comportement existant n’est pas cassé « en passant ».
- [ ] Il y a un test ou une commande de vérif que **j’ai lancée**.
- [ ] Je sais expliquer le choix (pourquoi Compose, pourquoi ce seuil, pourquoi ce schéma).
- [ ] Rien de k8s / Terraform / Kafka si ce n’était pas demandé.

## Comment relire un diff Python / pipeline

1. **Entrées / sorties** : quelle donnée entre, quelle donnée sort, où elle est écrite.
2. **Schéma** : types, nulls, colonnes ajoutées ou renommées.
3. **Échec** : que se passe-t-il si le fichier source est vide ou mal typé ?
4. **Idempotence** : relancer le job écrase-t-il la prod ?
5. **PII** : logs, traces MLflow, exceptions qui imprimeraient une ligne brute.

## Commandes que tu lances (pas l’agent)

Adapte au repo, mais l’habitude est à toi :

```bash
# tests
pytest -q

# lint si déjà configuré
ruff check .

# image
docker compose build
docker compose up --abort-on-container-exit

# API smoke
curl -s localhost:8000/health
```

Si tu ne lances pas les tests, tu as délégué la vérité à l’IA. Ce n’est plus
ton scope.

## Questions d’entretien à te poser sur CHAQUE changement

- Où est le data contract ?
- Comment je détecte un drift ou une rupture de schéma ?
- Comment je rollback le modèle / le job ?
- Qu’est-ce qui est reproductible (seed, `requirements`, image digest) ?
- Qui a le droit de voir ces données (RGPD) ?

Si Cursor a écrit le code mais que tu réponds à ces questions, **c’est toi
qui as fait le travail d’ingénieur**.

## Taille des changements

Refuse les diffs > ~200 lignes d’un coup, sauf boilerplate évident
(YAML CI calqué sur un autre job). Demande :

> Découpe en 2 PR : (1) tests + contrat (2) job/API.
