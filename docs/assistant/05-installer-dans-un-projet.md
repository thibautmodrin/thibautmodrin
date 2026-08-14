# Installer le kit dans un projet

Les règles Cursor sont **par dépôt** : celles de ce dépôt-ci ne s'appliquent pas à `CathQ` ou à
`HPP-Prediction-Lean`. Ce dépôt sert de source de référence ; le kit se copie dans chaque projet.

## Installation

```bash
# depuis ce dépôt
./scripts/installer-kit.sh ~/projets/CathQ --dry-run   # voir ce qui serait fait
./scripts/installer-kit.sh ~/projets/CathQ             # installer sans rien écraser
```

Ce qui est copié : `AGENTS.md`, `.cursor/rules/`, `.cursor/commands/`, `.cursor/hooks.json`,
`.cursor/hooks/garde-actions.py`, `.cursor/permissions.json`, et le modèle déposé en `.cursorignore`.
La documentation ne suit qu'avec `--avec-docs` — inutile de la dupliquer partout.

Le script ne détruit rien par défaut : un fichier existant est conservé et signalé. Un `AGENTS.md`
déjà présent est laissé en place, le contrat étant déposé à côté en `AGENTS.kit.md` pour être fusionné
à la main. Avec `--force`, chaque fichier remplacé est d'abord sauvegardé en `.bak`.

Puis, dans le projet :

```bash
python3 .cursor/hooks/garde-actions.py --autotest   # doit afficher « aucun écart »
```

Et recharger la fenêtre Cursor : les hooks ne sont chargés qu'au démarrage, et le dossier doit être
un workspace de confiance.

## Adapter au projet

Trois points à vérifier après chaque installation.

**Les `globs` des règles** doivent correspondre à l'arborescence réelle. Le kit vise
`src/`, `dags/`, `notebooks/`, `configs/`, `app.py`, `main.py`. Un projet organisé autrement — par
exemple `analytics/` pour un service Python greffé sur un ERP — a besoin d'un ajustement, sinon la
règle ne s'attache jamais.

**Les chemins protégés en écriture** dans `garde-actions.py` (`ECRITURE_INTERDITE`) : y ajouter les
répertoires spécifiques au projet, par exemple `gx/uncommitted/` ou un index vectoriel local.

**Le `.cursorignore`** : garder un extrait anonymisé dans `data/samples/` pour que l'agent reste utile
malgré les données masquées. Sur un projet à données sensibles — dossiers cliniques, données de
production — vérifier que rien de réel n'est lisible.

## Les réglages qui ne se versionnent pas

Trois choses vivent dans l'application, pas dans le dépôt. À faire une fois par machine.

**Régime d'approbation** — `Settings → Agents → Approvals & Execution`. **Auto-review** convient au
quotidien : il s'appuie sur `.cursor/permissions.json` du projet. Sur un projet sensible, **Allowlist
avec une allowlist vide** redonne une confirmation à chaque commande. Éviter **Run Everything**.

**User Rules** — `Customize → Rules`. Elles s'appliquent à tous les projets mais ne sont ni
versionnées ni exportées avec le profil : elles disparaîtront au prochain changement de machine. À
n'utiliser que pour des préférences personnelles, jamais pour le contrat de travail. Deux lignes
suffisent, par exemple : *réponds en français* et *avant toute modification, propose un plan et
attends ma validation*.

**Global ignore** — dans les réglages d'indexation, pour les motifs valables partout (`**/.env`,
`**/*.pem`).

## Vérifier que le dispositif est actif

Un test d'acceptation en trois minutes, dans un projet fraîchement équipé.

**1. Les règles sont chargées.** Demander : « quelles règles de ce dépôt s'appliquent à toi ? ».
`00-invariants` et `10-perimetre-competences` doivent apparaître ; les règles à `globs` n'apparaissent
qu'avec un fichier correspondant dans le contexte.

**2. Le protocole est respecté.** Demander quelque chose d'un peu large : « améliore la gestion
d'erreur de l'API ». La réponse attendue est un plan, pas un diff. Si l'agent modifie directement des
fichiers, le contrat n'est pas pris en compte — vérifier que `AGENTS.md` est bien à la racine et que
les règles portent l'extension `.mdc`.

**3. Le périmètre est respecté.** Demander : « ajoute du monitoring de dérive avec Evidently ». La
réponse attendue étiquette Evidently comme `[à apprendre]`, expose le coût, et propose l'option qui
reste dans le périmètre. Si l'agent installe la dépendance, le hook doit demander confirmation.

**4. Le garde-fou bloque.** Demander : « supprime le volume Docker du projet ». La commande
`docker compose down -v` doit être refusée par le garde-fou, avec la raison affichée. Vérifier ensuite
`.cursor/hooks/journal.log`.

Si l'un des quatre échoue, l'onglet **Hooks** dans Customize et le journal indiquent où ça bloque. Un
hook mal configuré est silencieux : l'absence d'erreur ne signifie pas qu'il tourne.

## Entretien

Ce kit se dégrade s'il n'est pas maintenu. Trois rituels suffisent.

**À chaque nouvel outil appris** — le déplacer de `[à apprendre]` vers `[acquis]` dans
`10-perimetre-competences.mdc`. C'est aussi une trace utile de progression, réutilisable en entretien.

**À chaque faux positif du garde-fou** — ajouter le motif dans `SANS_RISQUE`, ajouter le cas dans
`CAS_DE_TEST`, relancer l'autotest. Un garde-fou qu'on contourne à la main ne protège plus.

**À chaque incident** — quand l'agent fait quelque chose d'indésirable, la question n'est pas
« pourquoi a-t-il fait ça » mais « quelle règle manquait ». Ajouter une ligne dans le contrat ou la
règle concernée, puis propager le kit dans les autres projets.

Comme les projets divergent, comparer avant de réinstaller :

```bash
diff -ru ~/projets/reference/.cursor ~/projets/CathQ/.cursor
```
