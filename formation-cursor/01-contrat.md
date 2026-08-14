# 1. Contrat : tu restes maître

Cursor est fort pour **accélérer** ce que tu sais déjà cadrer. Il est dangereux
quand tu lui laisses choisir l’architecture, les libs et le périmètre.

## Division du travail

| Toi | Cursor |
| --- | --- |
| Besoin métier, contraintes, « done » | Plan technique dans le scope |
| Choix d’archi (Compose vs k8s, batch vs stream) | Détail d’implémentation une fois choisi |
| Validation du diff et des tests | Code, boilerplate, debug, relecture |
| Responsabilité prod / données / RGPD | Rappels et checklists, pas de décision cachée |

Si tu ne peux pas expliquer un fichier qu’il a écrit, **tu ne le merges pas**.
Tu demandes une version plus simple, ou tu le fais réécrire en ta présence
(Ask : « explique-moi ce bloc ligne par ligne »).

## Les 4 phrases qui te protègent

Colle-les en bas de presque chaque prompt :

1. `Propose, n'implémente pas.`
2. `Reste dans mon scope Jedha DE/MLOps (Python, Docker Compose, Actions, pytest).`
3. `Ne touche que les fichiers X, Y.`
4. `Pas de nouvelle dépendance sans me demander.`

## Ce que « dans mon scope » veut dire

**Dans le scope** = tu pourrais le refaire en 1–2 jours avec tes notes Jedha,
et le maintenir seul.

Exemples OK :

- endpoint FastAPI + schéma Pydantic + test pytest ;
- `Dockerfile` + `compose` pour API + MLflow local ;
- job GitHub Actions : lint + pytest + build image ;
- DAG Airflow qui lance un script Python déjà existant ;
- check de drift (PSI / stats descriptives) écrit en pandas ;
- pipeline RAG : chunk → embed → Chroma → query FastAPI.

Exemples **hors scope par défaut** (Cursor doit t’alerter) :

- cluster Kubernetes + Helm + ingress + HPA ;
- Terraform pour 3 comptes AWS ;
- Kafka + Spark Structured Streaming ;
- fine-tune d’un LLM sur GPU.

Ce n’est pas « interdit pour toujours ». C’est **interdit tant que tu n’as pas
choisi d’apprendre ça**, avec un plan pédagogique, pas un copier-coller opaque.

## Signal d’alarme

Arrête et recadre si Cursor :

- ajoute 4 nouveaux outils pour un besoin simple ;
- réécrit tout le repo ;
- introduit une lib que tu n’as jamais utilisée ;
- « industrialise » un notebook en plateforme complète ;
- commit tout seul, ou cache un `.env`.

Recadrage type :

> Stop. Reprends le plan. Une seule brique. Stack actuelle du repo.
> Explique chaque fichier. Attends mon go.
