---
name: audit-mlops
description: État des lieux MLOps du dépôt, avec priorités classées selon mon périmètre de compétences
---

Fais l'état des lieux MLOps de ce dépôt. Tu **ne modifies rien** : tu produis un diagnostic et des
priorités. Tu t'appuies sur ce que tu lis réellement, en citant les fichiers.

Passe en revue, dans cet ordre :

1. **Reproductibilité** — le projet démarre-t-il en une commande ? Versions pinnées ? Aléa fixé ?
   Variables d'environnement documentées ?
2. **Données** — la donnée brute est-elle protégée en écriture ? Les entrées sont-elles validées ?
   Le volume attendu est-il contrôlé ? Y a-t-il un risque de leakage ?
3. **Entraînement et traçabilité** — ce qui est tracé, ce qui manque pour rejouer un résultat, la
   présence du seuil de décision et de son critère.
4. **Mise à disposition** — contrat d'API validé, point de santé, chargement du modèle,
   identification de la version servie.
5. **Tests et CI** — ce qui est réellement couvert, et le test manquant dont l'absence coûterait le
   plus cher.
6. **Monitoring et cycle de vie** — dérive surveillée, seuil d'action, condition de réentraînement,
   procédure de rollback écrite.
7. **Sécurité et conformité** — secrets, données personnelles, mentions de cadre d'usage.

Rends un tableau des écarts avec, pour chaque ligne : le constat (fichier), l'impact concret si ça
reste en l'état, l'effort, et l'étiquette de périmètre (`[acquis]`, `[à apprendre]`,
`[hors périmètre]`).

Termine par **les trois actions à faire en premier**, toutes dans les étiquettes `[acquis]` ou
`[à apprendre]`, chacune tenant dans une pull request. Les écarts qui exigeraient une brique
`[hors périmètre]` sont listés à part, avec l'alternative simple correspondante.

N'ajoute aucun outil au dépôt dans le cadre de cet audit, même par « bonne pratique ».
