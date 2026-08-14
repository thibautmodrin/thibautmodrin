# Les pièges propres aux projets data et ML

Un agent est très bon sur le code qui a une réponse vérifiable localement. Il est structurellement
faible sur ce qui dépend des données réelles, du contexte métier et du temps. Ces onze pièges reviennent
constamment ; les connaître suffit le plus souvent à les éviter.

## 1. Les colonnes inventées

Un agent qui n'a pas accès aux données déduit les noms de colonnes du contexte, et se trompe avec
aplomb. Le code s'exécute jusqu'au `KeyError`, ou pire, remplit des valeurs par défaut.

**Parade** — fournir explicitement le schéma : `df.dtypes`, l'en-tête du CSV, ou un extrait anonymisé
dans `data/samples/`. Et demander : « n'utilise que des colonnes présentes dans ce schéma ; si une
information te manque, dis-le au lieu de la supposer ».

## 2. Le leakage introduit en refactorant

C'est le piège le plus coûteux, parce qu'il ne casse rien : il **améliore** les métriques. Un agent qui
« nettoie » un pipeline peut déplacer un `fit` avant le découpage, ou calculer une moyenne sur
l'ensemble complet. Le résultat paraît meilleur, il est faux.

**Parade** — tout changement touchant à la préparation ou au découpage se relit ligne à ligne, avec le
prompt de vérification de leakage. Une métrique qui s'améliore sans raison expliquée est un signal
d'alerte, pas une bonne nouvelle.

## 3. Le seuil qui revient à 0,5

Un seuil métier calibré est une décision, pas un détail d'implémentation. Un agent qui réécrit une
fonction de prédiction rétablit volontiers le comportement « standard » de la bibliothèque, c'est-à-dire
`predict()` avec son seuil implicite.

**Parade** — le seuil et son critère vivent dans la configuration et dans les artefacts, jamais en dur
dans un appel. Un test vérifie que le seuil appliqué est bien celui retenu.

## 4. Le découpage aléatoire sur des données temporelles

`train_test_split` avec `shuffle=True` est le réflexe par défaut de tous les exemples de la
documentation. Sur des données temporelles, il fait apprendre le futur et invalide toute l'évaluation.

**Parade** — nommer la contrainte dans la demande : « le découpage est temporel, la validation est
postérieure à l'entraînement ». Vérifier ce point à chaque modification du protocole d'évaluation.

## 5. L'accuracy sur un événement rare

Sur une prévalence inférieure à 1 %, une accuracy de 99 % correspond à un modèle qui ne prédit jamais
l'événement. Un agent qui « ajoute des métriques » place l'accuracy en tête parce que c'est la
convention.

**Parade** — dire la prévalence et le coût d'erreur dès le cadrage, et faire justifier la métrique
avant de l'implémenter. Une métrique sans son seuil associé n'est pas interprétable.

## 6. Les données de test fabriquées

Faute de fixture, un agent invente un jeu de données qui satisfait le test. Le test passe et ne
démontre rien, parce que les données ne ressemblent pas au réel : pas de valeurs manquantes, pas de
classe minoritaire, pas de cas limite.

**Parade** — imposer que les fixtures contiennent explicitement les cas pénibles : valeur manquante,
classe absente, doublon, entrée vide, valeur hors plage.

## 7. La dépendance ajoutée en silence

Un `import` d'une bibliothèque absente de `requirements.txt`, et la CI casse chez le suivant — ou pire,
passe en local et casse dans le conteneur.

**Parade** — le hook `beforeShellExecution` demande confirmation sur toute installation, et
`/revue-pr` vérifie la symétrie entre les imports et les fichiers de dépendances. À contrôler
systématiquement quand un import apparaît dans un diff.

## 8. Le pipeline non idempotent

Un agent écrit volontiers en mode ajout (`mode="a"`, `if_exists="append"`). Relancé deux fois après un
échec, le pipeline double les lignes sans rien signaler.

**Parade** — chaque étape est rejouable, et le nombre de lignes attendu est vérifié après chaque
transformation. Un écart doit produire une exception, pas un avertissement.

## 9. La donnée brute modifiée en place

`data/raw/` est la seule chose qu'on ne peut pas régénérer. Un script qui écrit dedans, même par
inadvertance, détruit la référence.

**Parade** — le hook refuse les écritures dans les répertoires de données, et le modèle
`.cursorignore` les soustrait à l'agent. Le principe reste : les sorties vont ailleurs, toujours.

## 10. La documentation trop belle pour être vraie

Un agent chargé de rédiger un README comble les trous par du plausible : un chiffre de performance
approximatif, une limite passée sous silence, une architecture décrite comme plus complète qu'elle ne
l'est. Dans un livrable de certification, c'est un piège direct à la soutenance.

**Parade** — exiger que chaque chiffre soit cité depuis un fichier du dépôt, et qu'un `TODO` remplace
toute information manquante. Puis passer `/oral` : les questions générées révèlent immédiatement ce
que la documentation survend.

## 11. Le disclaimer supprimé au nettoyage

Sur un projet clinique ou industriel, les mentions de cadre d'usage (aide à la décision, humain dans la
boucle, absence de valeur réglementaire) ne sont pas du décor : elles délimitent la responsabilité.
Elles disparaissent facilement lors d'un « allègement » de la documentation ou de l'interface.

**Parade** — c'est un point explicite du contrat et de la commande `/revue-pr`. À vérifier dans tout
diff qui touche un README ou une interface utilisateur.

## Le test qui résume tout

Avant de merger, deux questions :

1. **Qu'est-ce qui prouve que ça marche ?** Une commande, une sortie, une métrique. Pas une
   affirmation.
2. **Est-ce que je saurais l'expliquer à quelqu'un qui n'a pas vu le code ?**

Si l'une des deux réponses manque, le changement n'est pas prêt — indépendamment de sa qualité
apparente.
