# Première session (45 min) — tu t’entraînes à rester lead

Fais-la dans **Ask** ou avec `/plan-avant-code`. Objectif : muscler le réflexe GO / stop, pas produire un super repo.

## Exercice 1 — Cadrer (10 min)

Ouvre un de tes repos (CathQ de préférence). Colle :

```text
Ne change rien. Décris le flux actuel (données → modèle → API → monitoring) en citant les fichiers.
Dis-moi ce qui est déjà IN vs ce qui serait de l’over-engineering si on « industrialisait ».
```

**Réussite** : tu peux redire le flux sans lire la réponse. Si tu ne peux pas, redemande une explication plus courte.

## Exercice 2 — Refuser l’usine (15 min)

```text
Propose 3 façons d’améliorer le monitoring de drift.
Pour chaque : stack, ce que je dois opérer, coût, hors scope.
Plan seulement.
```

Ensuite tu réponds **uniquement** : `option la plus simple, explique le debug, ne code pas`.

**Réussite** : tu as écarté K8s / SaaS / nouvel outil sans te justifier longtemps. C’est toi qui recadres.

## Exercice 3 — Petit GO (20 min)

Choisis un changement minuscule (un test manquant, un `/health`, un README de commande). 

```text
Plan d’abord pour [X]. Une option. Attends GO.
```

Puis `GO`. Puis `/revue-humain`. Lance **toi-même** pytest ou curl.

**Réussite** : tu as relu chaque ligne du diff. Si une ligne est opaque, `explique cette ligne, ne rajoute rien`.

## Après la session

1. User Rule collée (sinon le kit ne te suit pas dans les autres repos)
2. Note 1 outil PONT que tu veux apprendre plus tard — ne le code pas aujourd’hui
3. Prochaine tâche pro : même protocole, même checklist
