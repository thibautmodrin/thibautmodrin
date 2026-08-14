# Réutiliser ce kit dans un vrai projet

Le dépôt profil GitHub n’est pas ton lieu de travail. Pour CathQ, un pipeline client, un RAG :

## 1. Règle utilisateur (une fois pour toutes)

Colle [`USER_RULE.md`](USER_RULE.md) dans Cursor → Customize → Rules.

## 2. Fichiers à copier dans le repo de travail

```text
.cursor/rules/00-maitrise-humaine.mdc
.cursor/rules/10-perimetre-competences.mdc
.cursor/rules/20-data-engineer-mlops.mdc
.cursor/commands/plan-avant-code.md
.cursor/commands/go-implementer.md
.cursor/commands/revue-humain.md
```

Optionnel : copie `formation-cursor-mlops/02-perimetre.md` à la racine du projet sous `docs/perimetre-competences.md` et mets à jour les chemins `@` dans les règles si besoin.

## 3. Premier message dans le nouveau repo

```text
Lis README + structure. Ne change rien.
Confirme le stack réel du repo vs mon périmètre Jedha.
Liste 3 risques si on over-engineer.
Ensuite attends mon objectif.
```

## 4. Faire évoluer le périmètre

Quand tu as vraiment opéré un outil (pas juste un tuto) : passe-le de PONT → IN dans `02-perimetre.md` **et** dans la User Rule. Sinon l’IA restera trop timide, ou trop audacieuse.
