# Garde-fous : ce qui bloque vraiment, ce qui ne fait qu'orienter

Tous les garde-fous ne se valent pas. Confondre une consigne et une barrière est la meilleure façon de
se croire protégé.

| Niveau | Mécanisme | Force réelle |
|---|---|---|
| 1 | `AGENTS.md`, `.cursor/rules/*.mdc` | **Orientation.** Très efficace en pratique, mais un modèle peut passer outre |
| 2 | Run Modes + `.cursor/permissions.json` | **Filtrage.** Un classificateur juge la commande — la documentation Cursor précise que ce n'est pas une frontière de sécurité |
| 3 | `.cursor/hooks.json` | **Blocage.** Le seul mécanisme qui refuse réellement une action |
| 4 | `.cursorignore` | **Masquage.** Empêche la lecture et l'indexation, mais pas les accès via le terminal ou un outil MCP |

Aucun de ces niveaux ne remplace la relecture du diff. Ils réduisent la probabilité d'une action
subie ; ils ne garantissent pas la pertinence de ce qui est écrit.

## Niveau 1 — Consignes

`AGENTS.md` est chargé automatiquement à la racine du dépôt. Les règles `.cursor/rules/*.mdc`
s'ajoutent selon leur mode d'activation :

- `alwaysApply: true` — toujours présente. C'est le cas de `00-invariants` et de
  `10-perimetre-competences`.
- `globs: ...` — attachée quand un fichier correspondant entre dans le contexte. C'est le cas des
  règles Python, données, MLOps et notebooks.
- `@nom-de-la-regle` — pour rappeler explicitement une règle dans une conversation.

Les règles ne s'appliquent qu'à l'agent du chat : ni Tab, ni `Cmd+K`, ni les revues automatiques.
Un fichier `.md` déposé dans `.cursor/rules/` est **ignoré** : l'extension doit être `.mdc`.

Deux limites à connaître. Plus une règle est longue, moins elle pèse — d'où le format court des
invariants. Et les **User Rules** (réglages personnels, dans Customize → Rules) ne sont pas
versionnables : elles disparaissent au changement de machine. Ce qui doit survivre appartient au
dépôt.

## Niveau 2 — Approbations

Réglage dans **Settings → Agents → Approvals & Execution**, avec trois régimes :

- **Auto-review** — les commandes de l'allowlist passent, les autres sont évaluées. Régime
  recommandé au quotidien.
- **Allowlist** — seules les actions listées passent sans validation. **Avec une allowlist vide, on
  retrouve une confirmation à chaque commande** : c'est le régime à utiliser sur un projet sensible.
- **Run Everything** — tout s'exécute sans demander. À éviter.

`.cursor/permissions.json` complète Auto-review avec des instructions en langage naturel :
`allow_instructions` pour ce qui passe seul (lecture, tests, lint, service local),
`block_instructions` pour ce qui doit être validé (dépendances, dépôt distant, cloud, migrations,
destruction de données). Ce fichier est versionné et fusionné avec `~/.cursor/permissions.json`.

Ce sont des instructions interprétées, pas des motifs de commandes. Elles réduisent fortement les
actions subies, sans constituer une garantie.

## Niveau 3 — Hooks, la seule vraie barrière

`.cursor/hooks.json` branche `.cursor/hooks/garde-actions.py` sur deux événements.

**`beforeShellExecution`** — avant toute commande de la famille surveillée (git, docker, pip,
terraform, kubectl, cloud, bases de données, SQL destructif…). Le script répond :

- **refus** pour l'irréversible : `rm -rf` hors du dépôt, `git push --force`, `git reset --hard`,
  `terraform apply` ou `destroy`, `kubectl delete`, `docker compose down -v`, `docker system prune`,
  `airflow db reset`, `DROP`, `TRUNCATE`, `dropdb`, `alembic downgrade`, fusion de pull request,
  installation d'un script téléchargé depuis Internet ;
- **confirmation** pour ce qui engage : ajout de dépendance, `git push`, réécriture de commit, appel
  cloud, `docker push`, accès direct à une base, migration, déclenchement de pipeline, action sur une
  machine distante ;
- **passage** pour le quotidien : `git status`, `git diff`, `git commit`, `pytest`, `make test`,
  `pip install -r requirements.txt`, `docker compose up`, appels vers `localhost`.

Ce hook est en `failClosed: true` : si le script plante, la commande sensible est bloquée plutôt
qu'autorisée.

**`preToolUse`** (outils Write et Delete) — refuse l'écriture dans les fichiers de secrets, les clés
privées, `data/raw` et les autres répertoires de données, `artifacts/`, `mlruns/`, les modèles
sérialisés, `.git/`, et tout chemin situé hors du dépôt.

Deux réserves assumées, plutôt que passées sous silence :

- La structure du payload de `preToolUse` n'est documentée que pour l'outil Shell. Le script cherche
  le chemin dans plusieurs clés plausibles et, s'il ne le trouve pas, **laisse passer** pour ne pas
  bloquer le travail à l'aveugle. `failClosed` est donc à `false` sur ce hook.
- Sur les commandes qu'il juge courantes, le hook répond « autorisé », ce qui peut lever la friction
  du régime Allowlist. Pour un contrôle maximal, exporter `CURSOR_GARDE_NEUTRE=ask` : toute commande
  de la famille surveillée demande alors confirmation, y compris `git status`.

Enfin, Cursor ajoute ses propres protections natives, indépendantes de ce kit : suppression de
fichiers, écriture hors du workspace, et accès navigateur.

## Utiliser et maintenir le garde-fou

**Vérifier les règles de classement** sans passer par Cursor :

```bash
python3 .cursor/hooks/garde-actions.py --autotest
```

Quarante-sept cas sont vérifiés (commandes autorisées, à confirmer, refusées, et chemins protégés).
À lancer après chaque modification des listes du script.

**Tester une commande précise** :

```bash
echo '{"command":"git push --force origin main"}' | python3 .cursor/hooks/garde-actions.py shell
```

**Consulter les décisions prises** — `.cursor/hooks/journal.log`, non versionné :

```bash
tail -n 30 .cursor/hooks/journal.log
```

**Comprendre un payload non documenté** — exporter `CURSOR_GARDE_AUDIT=1` avant de lancer Cursor : le
JSON brut reçu est ajouté au journal. C'est la seule façon fiable de découvrir sous quelle clé un
outil transmet son chemin de fichier.

**Ajouter une règle** — les listes en tête de `garde-actions.py` sont des tables
`(expression régulière, raison)` :

- `INTERDITES` — refus catégorique ;
- `SANS_RISQUE` — passage sans friction ;
- `A_CONFIRMER` — validation demandée ;
- `ECRITURE_INTERDITE` — chemins protégés en écriture.

Ajouter un cas dans `CAS_DE_TEST` en même temps que la règle, puis relancer l'autotest.

**Désactiver temporairement** — renommer `.cursor/hooks.json` (par exemple en
`.cursor/hooks.json.off`) et recharger la fenêtre. Utile pour distinguer un vrai blocage d'un faux
positif du garde-fou.

L'onglet **Hooks** dans Customize affiche les exécutions et les erreurs. Un hook mal configuré est
silencieux : après toute modification, vérifier qu'il se déclenche réellement.

## Niveau 4 — Ce que l'agent ne doit pas voir

Le modèle [`modeles/cursorignore`](modeles/cursorignore) couvre secrets, données, artefacts et bruit
d'indexation. À copier en `.cursorignore` à la racine de chaque projet.

Conséquence à anticiper : l'agent ne pourra plus inspecter les données pour en déduire le schéma. La
contrepartie est de versionner un extrait anonymisé dans `data/samples/`, ce qui est de toute façon
une bonne pratique pour la reproductibilité. Rappel utile : `.gitignore` est déjà respecté
automatiquement, et le terminal contourne ce filtre.
