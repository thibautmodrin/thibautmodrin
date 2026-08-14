---
name: expliquer
description: Expliquer du code ou une décision technique pour que je puisse la reprendre et la défendre
---

Explique-moi le code ou la décision en contexte, avec un objectif précis : que je puisse le
**réécrire de mémoire** et le **défendre à l'oral**. Tu ne modifies aucun fichier.

Structure attendue :

1. **En une phrase** : ce que ça fait et pourquoi ça existe.
2. **Le déroulé** : ce qui entre, ce qui se passe, ce qui sort. Cite les lignes concernées.
3. **Le concept sous-jacent** : la notion à comprendre, expliquée sans jargon d'abord, puis avec le
   terme exact — pour que je sache le nommer correctement.
4. **Ce qui casse si on y touche** : les deux ou trois modifications qui produiraient un bug
   silencieux, et pourquoi.
5. **Comment le vérifier moi-même** : la commande, le test, ou la valeur à inspecter.
6. **La version plus simple** : est-ce que ce code pourrait être plus simple à qualité égale ? Si
   oui, laquelle, et qu'est-ce qu'on perdrait.

Deux exigences. Si une partie du code repose sur une brique `[à apprendre]` ou
`[hors périmètre]` de mon référentiel, dis-le explicitement plutôt que de l'expliquer comme une
évidence. Et si tu n'es pas certain du comportement réel, distingue clairement ce que tu as lu dans
le code de ce que tu supposes.
