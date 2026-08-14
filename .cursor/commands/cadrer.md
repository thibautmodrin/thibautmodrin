---
name: cadrer
description: Cadrer une demande et produire un plan validable, sans écrire de code
---

Tu ne modifies **aucun fichier** pendant cette commande. Objectif : transformer ma demande en un
plan que je puisse valider, refuser ou amender.

Procédure :

1. **Lis le dépôt avant de répondre.** Repère les fichiers concernés, les conventions en place, ce
   qui existe déjà et couvre peut-être le besoin. Cite les chemins et les lignes qui motivent ton
   analyse.
2. **Reformule ma demande en une phrase.** Si ma formulation est ambiguë, dis en quoi.
3. **Pose les questions bloquantes**, au maximum trois, et seulement celles dont la réponse change
   le plan. Si une hypothèse raisonnable suffit, annonce-la comme hypothèse.
4. **Produis le bloc de proposition** au format défini dans `AGENTS.md` : objectif, constat, plan
   numéroté avec les fichiers touchés, périmètre étiqueté, coût, alternative écartée, vérification,
   retour arrière.
5. **Signale ce que la demande implique et que je n'ai peut-être pas vu** : contrat d'API modifié,
   migration nécessaire, test à réécrire, impact sur la CI, donnée à régénérer.
6. **Découpe en lots livrables séparément**, du plus petit qui apporte déjà de la valeur au plus
   large, en indiquant où s'arrêter si je manque de temps.

Termine par la question exacte à laquelle je dois répondre pour que tu démarres. N'enchaîne pas sur
l'implémentation sans mon accord, même si le plan te paraît évident.
