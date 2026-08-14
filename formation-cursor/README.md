# Formation : utiliser Cursor en Data Engineer / MLOps

Objectif : que Cursor t’**assiste** (plan, code, debug, revue) sans jamais te
remplacer. Tu valides chaque action. Tout reste dans ton scope Jedha
(Data Engineer + MLOps), donc défendable en entretien et opérable en junior.

Temps : **45 minutes** pour la lecture + **2 exercices** sur un de tes repos.

## Parcours

| Étape | Fichier | Durée |
| --- | --- | --- |
| 1. Contrat (tu restes maître) | [01-contrat.md](01-contrat.md) | 8 min |
| 2. Modes Cursor (Ask / Plan / Agent) | [02-utiliser-cursor.md](02-utiliser-cursor.md) | 10 min |
| 3. Prompts métier prêts à copier | [03-prompts.md](03-prompts.md) | 10 min |
| 4. Revue des diffs (maîtrise) | [04-revue.md](04-revue.md) | 8 min |
| 5. Exercices sur tes projets | [05-exercices.md](05-exercices.md) | 15 min+ |
| Coller les règles globales | [USER_RULES.md](USER_RULES.md) | 3 min |

## Mise en place (obligatoire)

Sans ça, l’assistant n’est pas encadré sur tes **autres** repos (CathQ, HPP, etc.).

1. Ouvre Cursor → **Settings → Rules → User Rules**.
2. Colle **intégralement** le contenu de [`USER_RULES.md`](USER_RULES.md).
3. Dans **chaque projet de travail**, copie le dossier
   [`modele-projet/.cursor/`](modele-projet/.cursor/) à la racine du repo.
4. Travaille d’abord en **Ask** ou **Plan**. Passe en **Agent** seulement
   après un plan validé, avec un périmètre de fichiers.

Les règles de **ce** dépôt (`.cursor/rules/`) s’appliquent déjà ici. Elles ne
s’appliquent **pas** à tes autres GitHub tant que tu ne les y copies pas, ou
tant que les User Rules ne sont pas collées.

## Principe en une phrase

> Tu décris le **besoin métier** et les **contraintes**. Cursor propose un
> **plan dans ton stack**. Tu dis **go** (ou tu corriges le plan). Ensuite tu
> **relis le diff** et tu lances **toi-même** les commandes de vérif.
