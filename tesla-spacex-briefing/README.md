# Tesla × SpaceX — briefing quotidien

Application Streamlit : scan des news Tesla et SpaceX (presse + X si jeton),
synthèse de ce qui a été dit par les voix qui ont du poids (direction,
investisseurs, relais), **calendrier des briefings** conservé 30 jours.

Ce n'est pas un conseil en investissement. Les titres restent dans la langue
d'origine ; l'interface et les synthèses sont en français.

## Lancer

```bash
cd tesla-spacex-briefing
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest
python -m src.cli scan
streamlit run app.py
```

Le premier scan rattrape ~7 jours de Google News pour remplir le calendrier.
Les scans suivants ne prennent que la journée (flux `when:1d` + médias).

## Ce qui est collecté

| Source | Rôle |
| --- | --- |
| Google News Tesla / SpaceX (EN + FR) | Filet large, classé par jour de publication |
| Electrek, Teslarati, SpaceNews | Médias spécialisés |
| X (optionnel) | Posts des comptes de la watchlist, 7 derniers jours |

X n'est interrogé que si un Bearer Token est fourni. Trois endroits, dans cet ordre :

1. **Dans l'appli** (tablette / Chrome) : barre latérale → coller le jeton → *Enregistrer la clé*, puis *Scanner les news maintenant*.
2. **Fichier local** `tesla-spacex-briefing/.streamlit/secrets.toml` (ignoré par git) :

```toml
X_BEARER_TOKEN = "AAAA..."
```

   Copier `.streamlit/secrets.toml.example` et coller le jeton du
   [Developer Portal X](https://developer.x.com/en/portal/dashboard)
   (projet → Keys and tokens → Bearer Token).

3. **Variable d'environnement** `X_BEARER_TOKEN` (ou `TWITTER_BEARER_TOKEN`).

Sans jeton, le briefing s'appuie sur la presse et les citations rapportées
(« Musk a déclaré… », « Cathie Wood said… »).

## Voix suivies

Fichier `data/watchlist.yaml` : Elon Musk, comptes officiels Tesla/SpaceX,
cadres (von Holzhausen, Shotwell, Taneja…), investisseurs (ARK, Gerber,
Gary Black…), relais (Sawyer Merritt, Whole Mars Blog, Eric Berger…).

Chaque item est pesé. Un post du CEO pèse plus qu'une dépêche générique.

## Calendrier

Les rapports sont stockés dans `data/briefing.db` (SQLite). Au-delà de
`retention_days` (30 par défaut dans `data/sources.yaml`), les jours trop
anciens sont élagués. L'UI affiche un mois, les jours avec briefing sont
marqués, un clic ouvre Tesla / SpaceX / paroles / fil brut.

```bash
python -m src.cli scan           # collecter + synthétiser
python -m src.cli dates          # jours archivés
python -m src.cli show --date 2026-08-14
python -m src.cli prune --days 30
```

## Structure

```
data/          watchlist, sources RSS, base SQLite
src/           RSS, X, classement, synthèse, calendrier, CLI
tests/         parseur, clustering, watchlist, rétention
app.py         interface Streamlit
```
