---
name: revue-pr
description: Relire mes changements avant ouverture de pull request, comme un relecteur exigeant
---

Relis mes changements en cours avant que j'ouvre la pull request. Commence par lire le diff réel
(`git status`, `git diff`, et `git diff --stat` pour la vue d'ensemble). Tu ne corriges rien de ta
propre initiative : tu signales, je décide.

Vérifie, dans cet ordre :

1. **Un seul sujet.** Le diff traite-t-il une seule chose ? Signale tout changement opportuniste
   (renommage, reformatage, refactoring) qui devrait partir dans une pull request séparée.
2. **Rien de perdu.** Une fonctionnalité, un test, une validation, un seuil, une mention de cadre
   d'usage ou une option de configuration a-t-il disparu ? C'est le point le plus important.
3. **Rien de fuité.** Secret, jeton, mot de passe, URL interne, chemin absolu de ma machine, donnée
   personnelle, sortie de notebook volumineuse, fichier de données ou artefact committé par erreur.
4. **Cohérence avec le dépôt.** Conventions de nommage, structure, style d'erreur et de log
   respectés. Les endroits symétriques ont-ils été mis à jour (documentation, `.env.example`,
   `requirements.txt`, tests, README) ?
5. **Vérifiabilité.** Existe-t-il un test qui échouerait sans ce changement ? Sinon, lequel écrire ?
   Quelle commande exécuter pour prouver que ça marche ?
6. **Effets de bord.** Contrat d'API modifié, migration nécessaire, artefact à régénérer, impact sur
   le temps de CI, changement de comportement par défaut.
7. **Périmètre.** Le diff introduit-il une brique `[à apprendre]` ou `[hors périmètre]` que je
   n'aurais pas validée explicitement ?

Rends trois listes courtes et hiérarchisées : **bloquant**, **à corriger avant merge**,
**remarque**. Pas de compliment de politesse. Si rien n'est bloquant, dis-le en une phrase.

Termine par un titre de pull request et une description en français : contexte, ce qui change,
comment vérifier, ce qui reste hors périmètre. Ne crée ni commit ni pull request sans que je le
demande.
