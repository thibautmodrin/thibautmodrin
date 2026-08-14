# 5. Exercices (sur tes vrais repos)

Fais-les **dans l’ordre**. Ask → Plan → Agent borné → toi tu testes → toi tu
commit. Si tu sautes la revue, l’exercice est raté.

Repos suggérés : [CathQ](https://github.com/thibautmodrin/CathQ),
[HPP-Prediction-Lean](https://github.com/thibautmodrin/HPP-Prediction-Lean),
[ERP-Stock-Prediction](https://github.com/thibautmodrin/ERP-Stock-Prediction),
[Vitizen-RAG](https://github.com/thibautmodrin/Vitizen-RAG).

Copie d’abord [`modele-projet/.cursor/`](modele-projet/.cursor/) dans le repo
choisi.

## Exercice A — Cartographie (Ask uniquement)

Prompt : celui « Diagnostic d’un repo » dans [03-prompts.md](03-prompts.md).

Succès :

- tu as un schéma mental source → transform → modèle → API ;
- tu as 3 améliorations **dans le scope** ;
- tu as dit non à au moins une idée trop lourde (même si Cursor la propose).

## Exercice B — Un data contract + tests (Plan puis Agent)

Sur le dataset d’entrée d’un projet :

1. Plan d’un contrat (champs, types, 5 tests).
2. Tu corriges le plan (moins de tests si trop).
3. Agent : uniquement les fichiers de tests + éventuellement un `schema.py`.
4. Tu lances `pytest`. Tu commit.

Succès : les tests échouent si tu renommes une colonne dans un fixture.

## Exercice C — Recadrer l’Agent

Donne volontairement un prompt trop large :

> Industrialise tout le MLOps : k8s, feature store, monitoring enterprise.

Succès : tu recadres avec le prompt « Stop. Trop large. » et tu obtiens un
plan d’**une** brique (ex. un check de drift pandas). Tu n’implémentes pas
le plan k8s.

## Exercice D — Drift ou RAG, au choix

- **CathQ / HPP / ERP** : check de drift sur 2–3 features + test + comment
  le brancher (script ou Actions schedule), sans nouvelle lib.
- **Vitizen** : refus de réponse si le score de similarité est trop bas +
  5 questions d’éval documentées.

Succès : tu expliques le seuil à voix haute (pourquoi 0.3 et pas 0.8).

## Exercice E — Tu enseignes à Cursor le repo

Ajoute dans le projet un fichier `.cursor/rules/projet.mdc` (`alwaysApply: true`)
de **20 lignes max** :

- à quoi sert le repo ;
- commandes pour tester ;
- où sont les données (et ce qu’il ne faut pas commit) ;
- stack réelle.

Succès : un nouveau chat « où lance-t-on les tests ? » répond juste sans que
tu re-expliques.
