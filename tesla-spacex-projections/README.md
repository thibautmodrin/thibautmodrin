# Tesla × SpaceX — projections de CA, marges et suivi des objectifs

Application Streamlit (étape 1) : modèle **bottom-up** 2026-2035, trois scénarios,
et suivi des jalons officiels (plan CEO Tesla 2025, cibles Starlink / Musk).

Ce n'est pas un conseil en investissement. Le scénario *Objectifs* est la
trajectoire d'entreprise, pas la prévision centrale.

## Lancer

```bash
cd tesla-spacex-projections
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest
streamlit run app.py
```

## Ce qui est modélisé

| Bloc | Méthode | Ancrage |
| --- | --- | --- |
| Tesla auto retail | livraisons × ASP | Q2 2026 Update, FY 2021-2025 |
| Énergie | GWh × ASP/GWh | 46,7 GWh et 12,8 Md$ en 2025 |
| Robotaxi / Cybercab | flotte × miles payants × $/mile | production démarrée, pas encore en flotte commerciale |
| Optimus | unités × ASP | SOP 2026 interne, jalon CEO 1 M |
| SpaceX Starlink | abonnés × ARPU | S-1 2025 + 12 M d'abonnés mi-2026 |
| SpaceX launch / IA | séries scénarisées | Q2 2026 segmenté ; IA = principal écart vers 1 000 Md$ |

## Structure

```
data/          historique, hypothèses, jalons, sources (YAML)
src/           moteur, économie unitaire Cybercab, KPIs
tests/         formules et cohérences
app.py         interface Streamlit
```

## Étapes suivantes

1. Recalage trimestriel (script d'ingestion des Update decks)
2. Monte-Carlo sur utilisation, prix/mile, régulation
3. Capex / FCF et comparaison au consensus Street
4. Même niveau de détail unitaire pour Optimus et Starship
