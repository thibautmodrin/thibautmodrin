# Mode opératoire

## La boucle de travail

Quatre temps, toujours dans le même ordre. Le seul qui compte vraiment est le troisième.

**1. Cadrer — je décris le problème, pas la solution.**
Je donne le contexte métier, la contrainte, ce que j'ai déjà essayé. Je ne dis pas « ajoute Evidently »
mais « je veux savoir si la distribution des entrées a bougé depuis l'entraînement ». Décrire la
solution en même temps que le problème, c'est renoncer à l'analyse la plus utile de l'agent.

**2. Faire produire un plan — jamais du code directement.**
`/cadrer` sert exactement à ça. Un plan se lit en une minute, se refuse en une phrase. Cinq fichiers
modifiés se relisent en vingt minutes et se refusent difficilement, parce qu'on a déjà investi.

**3. Lire le plan avant de valider.** Les trois questions à se poser :
- **Est-ce que ça ajoute quelque chose que je ne maîtrise pas ?** Le plan doit l'annoncer avec une
  étiquette de périmètre. S'il ne le fait pas, c'est le premier signal d'alerte.
- **Est-ce que ça touche à autre chose que ma demande ?** Un correctif de bug qui modifie le
  `Dockerfile` mérite une question.
- **Est-ce que je saurais expliquer le résultat ?** Si la réponse est non, je demande la version
  simple avant, pas après.

**4. Exécuter par petits lots et vérifier soi-même.**
Un lot, une vérification, un commit. La vérification, c'est moi qui la lance : un agent qui affirme
« les tests passent » sans avoir montré la sortie n'a rien démontré.

## Quel mode Cursor pour quoi

| Mode | Ce qu'il peut faire | Quand l'utiliser |
|---|---|---|
| **Ask** | Lecture seule, aucune écriture | Comprendre un dépôt, se faire expliquer du code, préparer un oral |
| **Plan** | Lit, questionne, produit un plan éditable | Toute tâche non triviale — le mode par défaut à privilégier |
| **Agent** | Écrit, exécute, installe | Une fois le plan validé, pour l'exécution |
| **Debug** | Hypothèses, instrumentation par logs | Un bug dont je ne comprends pas la cause |

`Shift+Tab` fait tourner les modes, `Cmd/Ctrl+.` ouvre le menu. Le réflexe utile : **commencer en
Plan, basculer en Agent seulement après avoir lu le plan**. Le plan produit est un fichier markdown
qu'on peut sauvegarder dans le dépôt (« Save to workspace ») — pratique pour garder la trace d'un
arbitrage dans une pull request.

## Trois niveaux d'autonomie à choisir consciemment

Le bon niveau dépend du coût d'une erreur, pas de ma confiance dans l'outil.

**Autonomie large** — je décris, l'agent fait, je relis le diff. À réserver à ce qui est
intégralement réversible et vérifiable par un test : documentation, tests supplémentaires, refactoring
local sans changement de comportement, correction d'un message d'erreur.

**Autonomie encadrée** (le régime normal) — plan validé, exécution par lots, vérification à chaque
étape. Pour tout ce qui touche la logique métier, la préparation des données, les métriques, les
seuils, un service exposé.

**Autonomie nulle** — l'agent propose, je tape moi-même. Pour ce qui n'est pas réversible ou pas
vérifiable localement : migration de schéma, action cloud facturée, déploiement, réécriture
d'historique git, suppression de données. Faire produire la commande et l'exécuter soi-même prend dix
secondes de plus et supprime la catégorie d'incident la plus coûteuse.

## Reprendre le contrôle quand ça dérape

Les signaux qui doivent déclencher un arrêt :

- Le diff est plus large que la demande, ou touche des fichiers que je n'avais pas en tête.
- Une dépendance ou un outil apparaît sans avoir été discuté.
- Un test ou une validation a été modifié pour faire passer le changement.
- Je ne comprends plus pourquoi une partie du code existe.
- L'agent affirme avoir vérifié sans montrer de sortie de commande.
- Trois itérations sur le même bug sans progrès mesurable.

Quoi faire, dans l'ordre :

1. **Arrêter la génération** plutôt que de laisser finir « pour voir ».
2. **Demander l'état exact** : « liste les fichiers modifiés et ce que fait chaque changement, sans
   rien corriger ».
3. **Revenir en arrière sans état d'âme** : checkpoint Cursor, `git restore`, `git stash`. Un travail
   d'agent perdu coûte quelques minutes ; un dépôt dans un état incompris coûte une soirée.
4. **Recadrer plus étroitement** : un seul fichier, un seul comportement, un critère de réussite
   explicite.
5. **Si le blocage persiste, changer de mode** : passer en Debug pour instrumenter, ou en Ask pour
   comprendre avant de retoucher au code.

## Hygiène de session

- **Une session, un sujet.** Un contexte qui contient trois sujets produit des réponses qui mélangent
  les trois. Nouvelle tâche, nouvelle session.
- **Donner les bons fichiers en contexte** plutôt que d'espérer que l'agent les trouve : `@fichier`,
  `@dossier`, et `@nom-de-la-regle` pour rappeler une règle explicitement.
- **Ne pas laisser une erreur non corrigée** dans le contexte : elle sera reprise comme un exemple.
- **Commiter à chaque étape validée.** C'est le seul point de retour fiable, et ça rend chaque diff
  relisable.
- **Écrire l'arbitrage quelque part** (README, `docs/`, description de pull request) dès qu'il est
  pris. Un choix qui n'existe que dans un historique de chat est un choix perdu.
