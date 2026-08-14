# Modes Cursor : lequel pour ne pas perdre la main

| Mode | Quand | Risque de perte de contrôle |
|---|---|---|
| **Ask** | Comprendre un fichier, une erreur, un concept | Faible : lecture seule |
| **Plan** | Concevoir une feature, un DAG, une CI | Faible : pas d’écriture |
| **Agent** | Après GO, petits pas | Élevé si tu n’as pas cadré |
| **Cloud Agent** | Tâche longue déjà spécifiée (tests, docs, PR) | Élevé : spécifie Plan→GO dans le brief |

## Recette quotidienne

1. **Ask** : « montre-moi le flux actuel de X, cite les fichiers »
2. **Plan** (ou Agent + `plan d’abord`) : options dans le périmètre
3. Tu choisis
4. **Agent** : `GO option N`, une étape
5. Tu relis le diff (checklist [`05-checklist-revue.md`](05-checklist-revue.md))
6. Tu lances **toi-même** la commande de vérif

## @ mentions utiles

- `@fichier` : force le contexte, évite les inventions
- `@docs` / README : l’IA s’aligne sur ce que TU as déjà écrit
- Règles projet : elles rappellent maîtrise humaine + périmètre

## Commandes slash de ce kit

Dans un repo où tu as copié `.cursor/commands/` :

- `/plan-avant-code` — impose le plan, interdit l’implémentation
- `/go-implementer` — n’autorise que le dernier plan validé
- `/revue-humain` — audit « est-ce que je maîtrise encore ? »

## Pièges fréquents

- Laisser Agent tourner sur « améliore le projet » → usine à gaz
- Accepter un nouvel outil « c’est le standard industrie » → tu ne sauras pas opérer
- Cloud Agent sans brief Plan→GO → commits que tu ne comprends pas
- Copier-coller un DAG Airflow d’internet → secrets, connexions, opérateurs inconnus

Contre-mesure : une phrase de contrainte dans **chaque** prompt (`Pas de nouvel outil. Attends GO.`).
