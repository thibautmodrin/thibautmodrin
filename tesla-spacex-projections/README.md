# Tesla × SpaceX — projections de CA, marges, jalons et cours

Application Streamlit : modèle **bottom-up** 2026-2035, trois scénarios,
suivi des jalons officiels, recalage trimestriel, Monte-Carlo, capex/FCF,
économie unitaire Cybercab / Optimus / Starship, **cours implicite**.

Ce n'est pas un conseil en investissement. Le scénario *Objectifs* est la
trajectoire d'entreprise, pas la prévision centrale. Le cours n'est pas un
CAGR : EV = fondamentaux × multiples, puis equity / actions diluées.

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
| Robotaxi / Cybercab | flotte × miles payants × $/mile, **entrée commerciale datée** | production démarrée, pas encore en flotte (base = 2027) |
| Optimus | vendus = CA GAAP ; internes = économie de main-d'œuvre | SOP 2026 interne, jalon CEO 1 M |
| Capex / FCF | OCF ≈ EBITDA × 0,92 ; capex cœur + flotte + Optimus | guidage 2026 > 25 Md$ |
| SpaceX Starlink | abonnés × ARPU | S-1 2025 + 12 M d'abonnés mi-2026 |
| SpaceX launch | Falcon externe + Starship externe + other | vols internes Starlink exclus du CA |
| Cours Tesla / SpaceX | EV = w × EBITDA × EV/EBITDA + (1−w) × CA × EV/S, puis / actions diluées | clôture 13 août 2026 ; multiples en compression |
| Incertitude | Monte-Carlo (année d'entrée, util, prix, coût, volumes) | seed fixe |

## Recalage trimestriel

Mettre à jour `data/actuals.yaml` et `data/tesla_history.yaml` au prochain print.
Ne pas interpoler un trimestre non publié. L'onglet *Recalage 2026* montre le pont H1 réel → FY.

## Structure

```
data/          historique, actuals, hypothèses, jalons, valorisation, sources
src/           moteur, Cybercab, Optimus, Starship, cash, MC, cours, recalage
tests/         formules et cohérences (étapes 1-3)
app.py         interface Streamlit
```
