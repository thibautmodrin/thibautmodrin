---
name: hors-perimetre
description: Instruire l'ajout d'une technologie hors de mon périmètre — gain réel, coût d'entrée, alternative, plan d'apprentissage
---

J'envisage d'introduire une technologie qui sort de mon périmètre habituel. Instruis le dossier. Tu
ne modifies **aucun fichier** et tu n'installes rien.

1. **À quoi ça sert vraiment**, en trois phrases, sans le discours marketing de l'outil. Quel
   problème précis il résout, et pour quelle taille de système il a été conçu.
2. **Le gain sur *ce* dépôt**, pas en théorie : quel fichier deviendrait plus simple, quelle
   opération manuelle disparaîtrait, quel risque serait couvert. Si tu ne trouves pas de gain
   concret dans le code existant, dis-le franchement — c'est la réponse la plus utile.
3. **Le coût d'entrée**, honnêtement : concepts à maîtriser, dépendances et services ajoutés,
   surcoût de démarrage et de CI, ce qui casse quand ça tombe en panne, et ce qu'il faudra savoir
   déboguer seul.
4. **L'alternative dans mon périmètre** : comment obtenir 80 % du bénéfice avec ce que je maîtrise
   déjà. Compare les deux options sur le résultat visible pour l'utilisateur du projet.
5. **Le test de la soutenance** : les trois questions qu'un jury poserait si cet outil apparaît dans
   mon architecture. Si je ne peux pas y répondre après une prise en main courte, l'outil me
   fragilise au lieu de me valoriser.
6. **Ta recommandation, tranchée** : on adopte, on reporte, ou on renonce — et le motif principal.
7. **Si on adopte** : le plus petit périmètre d'introduction possible, réversible, dans un lot isolé
   — et ce que je dois avoir compris *avant* d'écrire la première ligne.

Ne présente pas l'adoption comme allant de soi parce que « c'est le standard de l'industrie ». Le
critère est ce que je peux exploiter, déboguer et défendre seul.
