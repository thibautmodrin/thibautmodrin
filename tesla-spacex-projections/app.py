"""Application Streamlit — projections Tesla / SpaceX et suivi des objectifs."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src.engine import history_spacex_frame, history_tesla_frame, project
from src.kpis import spacex_kpis, tesla_kpis
from src.load import assumptions, goals, sources
from src.montecarlo import delay_sensitivity, simulate
from src.overrides import scale_to_anchor
from src.rebase import published_quarters, spacex_ytd, tesla_2026_bridge

st.set_page_config(
    page_title="Tesla × SpaceX — projections & jalons",
    page_icon="🚀",
    layout="wide",
)

TESLA = "#CC0000"
SPACEX = "#005288"
BASE = "#2563eb"
CONS = "#64748b"
OBJ = "#d97706"
HIST = "#0f172a"

SCENARIO_COLORS = {
    "conservateur": CONS,
    "base": BASE,
    "objectifs": OBJ,
}


def fmt_md(value: float, digits: int = 1) -> str:
    return f"{value:,.{digits}f}".replace(",", " ").replace(".", ",") + " Md$"


def fmt_pct(value: float) -> str:
    return f"{value * 100:.1f} %".replace(".", ",")


def fmt_int(value: float) -> str:
    return f"{value:,.0f}".replace(",", " ")


def fmt_num(value: float, digits: int = 1) -> str:
    return f"{value:,.{digits}f}".replace(",", " ").replace(".", ",")


def apply_overrides(scenario: str, production_2030, price, cost, util, starlink_2030, start_year: int):
    cfg = assumptions()["scenarios"][scenario]
    cab = dict(cfg["cybercab"])
    sx = dict(cfg["spacex"])
    years = list(range(2026, 2036))
    i2030 = years.index(2030)
    overrides = {
        "production": scale_to_anchor(list(map(float, cab["production"])), production_2030, i2030),
        "price_per_mile": scale_to_anchor(list(map(float, cab["price_per_mile"])), price, i2030, floor=0.15, cap=2.5),
        "cost_per_mile": scale_to_anchor(list(map(float, cab["cost_per_mile"])), cost, i2030, floor=0.12, cap=1.2),
        "utilization": scale_to_anchor(list(map(float, cab["utilization"])), util, i2030, cap=0.7),
        "commercial_start_year": int(start_year),
    }
    return overrides, scale_to_anchor(list(map(float, sx["starlink_subs_eoy_m"])), starlink_2030, i2030)


def line_chart(title: str, series: dict[str, tuple[list, list]], ylabel: str, color_map: dict | None = None) -> go.Figure:
    fig = go.Figure()
    for name, (xs, ys) in series.items():
        color = (color_map or {}).get(name)
        fig.add_trace(
            go.Scatter(
                x=xs,
                y=ys,
                name=name,
                mode="lines+markers",
                line=dict(color=color, width=2.4),
                marker=dict(size=6),
            )
        )
    fig.update_layout(
        title=title,
        yaxis_title=ylabel,
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        margin=dict(l=10, r=10, t=60, b=10),
        height=380,
        hovermode="x unified",
        template="plotly_white",
    )
    return fig


def stacked_bar(title: str, years: list[int], stacks: dict[str, list], colors: list[str]) -> go.Figure:
    fig = go.Figure()
    for (name, values), color in zip(stacks.items(), colors):
        fig.add_trace(go.Bar(x=years, y=values, name=name, marker_color=color))
    fig.update_layout(
        barmode="stack",
        title=title,
        yaxis_title="Md$",
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        margin=dict(l=10, r=10, t=60, b=10),
        height=400,
        template="plotly_white",
    )
    return fig


def kpi_card(col, label: str, value: str, delta: str | None = None):
    col.metric(label, value, delta)


@st.cache_data(show_spinner=False)
def run_scenario(name: str) -> dict:
    proj = project(name)
    return {
        "tesla": proj.tesla_frame(),
        "spacex": proj.spacex_frame(),
        "cybercab": proj.cybercab_frame(),
        "optimus": proj.optimus_frame(),
        "launch": proj.launch_frame(),
        "narrative": proj.notes[0] if proj.notes else "",
        "tesla_kpis": [k.__dict__ for k in tesla_kpis(proj)],
        "spacex_kpis": [k.__dict__ for k in spacex_kpis(proj)],
        "bridge": tesla_2026_bridge(proj).__dict__,
    }


def project_with_overrides(scenario: str, cab_overrides: dict, starlink_path: list[float] | None):
    from src.load import assumptions as load_assumptions

    proj = project(scenario, cab_overrides)
    spacex_rows = proj.spacex
    if starlink_path is not None:
        sx_cfg = load_assumptions()["scenarios"][scenario]["spacex"]
        for i, row in enumerate(spacex_rows):
            row.starlink_subs_m = starlink_path[i]
            row.revenue_connectivity_b = starlink_path[i] * sx_cfg["starlink_arpu_month"][i] * 12 / 1000
            row.oi_connectivity_b = row.revenue_connectivity_b * sx_cfg["connectivity_oi_margin"][i]
            row.revenue_total_b = row.revenue_connectivity_b + row.revenue_launch_b + row.revenue_ai_b
            row.operating_income_b = row.oi_connectivity_b + row.oi_launch_b + row.oi_ai_b
            row.operating_margin = row.operating_income_b / row.revenue_total_b if row.revenue_total_b else 0
    return {
        "tesla": proj.tesla_frame(),
        "spacex": proj.spacex_frame(),
        "cybercab": proj.cybercab_frame(),
        "optimus": proj.optimus_frame(),
        "launch": proj.launch_frame(),
        "narrative": load_assumptions()["scenarios"][scenario]["narrative"].strip(),
        "tesla_kpis": [k.__dict__ for k in tesla_kpis(proj)],
        "spacex_kpis": [k.__dict__ for k in spacex_kpis(proj)],
        "bridge": tesla_2026_bridge(proj).__dict__,
    }


def main() -> None:
    cfg = assumptions()
    scenarios = list(cfg["scenarios"].keys())

    st.title("Tesla × SpaceX — CA, marges et jalons")
    st.caption(
        "Étape 2 · bottom-up 2026-2035 · recalage YTD · Monte-Carlo régulation/prix/utilisation · "
        "capex/FCF · Optimus et Starship unitaires · données au 14 août 2026."
    )

    with st.sidebar:
        st.header("Scénario")
        scenario = st.radio(
            "Récit",
            scenarios,
            index=1,
            format_func=lambda s: cfg["scenarios"][s]["label"],
        )
        st.info(cfg["scenarios"][scenario]["narrative"].strip())
        st.divider()
        st.subheader("Levier n°1 — entrée commerciale")
        cab0 = cfg["scenarios"][scenario]["cybercab"]
        start_year = st.select_slider(
            "Année où le Cybercab entre en flotte payante",
            options=[2026, 2027, 2028, 2029],
            value=int(cab0["commercial_start_year"]),
        )
        st.caption("En juillet 2026 le Cybercab n'est pas en flotte commerciale. Le scénario de base part sur 2027.")
        st.divider()
        st.subheader("Sensibilités (ancrage 2030)")
        st.caption("Les sliders déforment la S-curve du scénario choisi, sans réécrire l'historique.")
        sx0 = cfg["scenarios"][scenario]["spacex"]
        prod_2030 = st.slider("Production Cybercab 2030", 50_000, 4_000_000, int(cab0["production"][4]), 50_000)
        price_2030 = st.slider("Prix / mile 2030 ($)", 0.20, 1.50, float(cab0["price_per_mile"][4]), 0.05)
        cost_2030 = st.slider("Coût / mile 2030 ($)", 0.15, 0.90, float(cab0["cost_per_mile"][4]), 0.01)
        util_2030 = st.slider("Utilisation payante 2030", 0.15, 0.70, float(cab0["utilization"][4]), 0.01)
        sl_2030 = st.slider("Abonnés Starlink 2030 (M)", 15.0, 150.0, float(sx0["starlink_subs_eoy_m"][4]), 1.0)
        compare = st.checkbox("Comparer les 3 scénarios (ignore les sliders)", value=True)

    cab_over, sl_path = apply_overrides(scenario, prod_2030, price_2030, cost_2030, util_2030, sl_2030, start_year)
    active = project_with_overrides(scenario, cab_over, sl_path)
    all_sc = {name: run_scenario(name) for name in scenarios}

    tabs = st.tabs(
        [
            "Méthode",
            "Tableau de bord",
            "Recalage 2026",
            "Tesla",
            "Cybercab & ROI",
            "Incertitude",
            "Cash",
            "SpaceX",
            "Objectifs vs modèle",
            "Sources",
        ]
    )

    with tabs[0]:
        render_method()
    with tabs[1]:
        render_dashboard(active, all_sc, compare)
    with tabs[2]:
        render_rebase(active)
    with tabs[3]:
        render_tesla(active, all_sc, compare)
    with tabs[4]:
        render_cybercab(active)
    with tabs[5]:
        render_uncertainty(scenario)
    with tabs[6]:
        render_cash(active, all_sc, compare)
    with tabs[7]:
        render_spacex(active, all_sc, compare)
    with tabs[8]:
        render_goals(active)
    with tabs[9]:
        render_sources()


def render_method() -> None:
    st.markdown(
        """
### Pourquoi Streamlit

Un tableur cacherait les formules. Ici chaque chiffre de 2026-2035 sort d'un
moteur Python testé : volumes × prix, puis marges par activité. Les sliders
ne font que déformer une S-curve déjà documentée.

### Règles de rigueur

1. **Séparer les types de chiffres** — fait SEC / earnings, estimation S-1 ou presse, hypothèse de scénario.
2. **Bottom-up, pas un CAGR sur le CA total** — Tesla = retail × ASP + GWh × prix + services + robotaxi (flotte × miles × $/mile) + Optimus **vendu**. SpaceX = abonnés × ARPU + Falcon externe + Starship externe + IA.
3. **Trois récits, un seul ancrage historique** — le scénario *Objectifs* est la trajectoire Musk / plan CEO, **pas** la prévision centrale.
4. **Ne pas double-compter** — FSD déjà dans l'auto ; robots internes ≠ CA GAAP ; vols Starlink internes ≠ CA launch.
5. **2026 est une année mixte** — H1 réel + H2 projeté. Le recalage n'invente pas Q3/Q4.
6. **Le levier n°1 est réglementaire** — l'année d'entrée du Cybercab en flotte payante change 2027 beaucoup plus que 2030 (le backlog rattrape).

### Étape 2 ajoutée

- Recalage YTD (pont H1 publié → FY)
- Monte-Carlo (400 tirages, seed fixe) sur année d'entrée, utilisation, prix/mile, coût/mile, échelle de production
- Capex (cœur + flotte + Optimus interne) et FCF, plancher 25 Md$ en 2026
- Optimus unitaire (interne = économie de main-d'œuvre) et Starship unitaire (vol externe seulement)

### Ce qui reste pour plus tard

- Ingestion automatique des PDF Update decks
- Capex / FCF SpaceX au même grain
- Monte-Carlo sur Starlink ARPU et cadence Starship
        """
    )
    left, right = st.columns(2)
    with left:
        st.subheader("Ancrage Tesla (faits)")
        hist = history_tesla_frame()
        show = hist[["year", "revenue_total", "gross_margin", "operating_margin", "adj_ebitda", "deliveries", "storage_gwh"]]
        show = show.rename(
            columns={
                "year": "Année",
                "revenue_total": "CA Md$",
                "gross_margin": "Marge brute",
                "operating_margin": "Marge op.",
                "adj_ebitda": "EBITDA adj. Md$",
                "deliveries": "Livraisons",
                "storage_gwh": "Stockage GWh",
            }
        )
        st.dataframe(show, hide_index=True, use_container_width=True)
    with right:
        st.subheader("Ancrage SpaceX (S-1 / earnings)")
        hist = history_spacex_frame()
        show = hist[["year", "revenue_total", "revenue_connectivity", "revenue_space", "starlink_subs_eoy_m"]]
        show = show.rename(
            columns={
                "year": "Année",
                "revenue_total": "CA Md$",
                "revenue_connectivity": "Starlink Md$",
                "revenue_space": "Launch Md$",
                "starlink_subs_eoy_m": "Abonnés M",
            }
        )
        st.dataframe(show, hide_index=True, use_container_width=True)
        st.caption("2023-2024 : confiance moyenne. 2025 : S-1. Mix 2026 non comparable (fusion xAI).")


def render_dashboard(active: dict, all_sc: dict, compare: bool) -> None:
    tesla = active["tesla"]
    spacex = active["spacex"]
    y2026 = tesla[tesla["year"] == 2026].iloc[0]
    y2030 = tesla[tesla["year"] == 2030].iloc[0]
    s2026 = spacex[spacex["year"] == 2026].iloc[0]
    s2030 = spacex[spacex["year"] == 2030].iloc[0]

    c1, c2, c3, c4 = st.columns(4)
    kpi_card(c1, "Tesla CA 2026", fmt_md(y2026["revenue_total_b"]), "année en cours")
    kpi_card(c2, "Tesla CA 2030", fmt_md(y2030["revenue_total_b"]), fmt_pct(y2030["gross_margin"]) + " marge brute")
    kpi_card(c3, "SpaceX CA 2026", fmt_md(s2026["revenue_total_b"]))
    kpi_card(c4, "SpaceX CA 2030", fmt_md(s2030["revenue_total_b"]), fmt_pct(s2030["operating_margin"]) + " marge op.")

    c5, c6, c7, c8 = st.columns(4)
    kpi_card(c5, "Flotte robotaxi 2030", fmt_int(y2030["robotaxi_fleet"]))
    kpi_card(c6, "ROI Cybercab 2030", fmt_pct(y2030["cab_roi"] or 0), "simple, Tesla-owned")
    kpi_card(c7, "Starlink abonnés 2030", fmt_num(s2030["starlink_subs_m"]) + " M")
    kpi_card(c8, "Tesla FCF 2026", fmt_md(y2026["fcf_b"]), "plancher capex 25 Md$")

    if compare:
        series = {}
        for name, pack in all_sc.items():
            df = pack["tesla"]
            series[assumptions()["scenarios"][name]["label"]] = (df["year"], df["revenue_total_b"])
        st.plotly_chart(
            line_chart("Tesla — CA total", series, "Md$", {assumptions()["scenarios"][n]["label"]: SCENARIO_COLORS[n] for n in all_sc}),
            use_container_width=True,
        )
        series = {}
        for name, pack in all_sc.items():
            df = pack["spacex"]
            series[assumptions()["scenarios"][name]["label"]] = (df["year"], df["revenue_total_b"])
        st.plotly_chart(
            line_chart("SpaceX — CA total", series, "Md$", {assumptions()["scenarios"][n]["label"]: SCENARIO_COLORS[n] for n in all_sc}),
            use_container_width=True,
        )
    else:
        st.plotly_chart(
            stacked_bar(
                "Tesla — CA par activité (scénario actif)",
                tesla["year"].tolist(),
                {
                    "Auto retail + Cybercab HW": tesla["revenue_auto_b"].tolist(),
                    "Énergie": tesla["revenue_energy_b"].tolist(),
                    "Services": tesla["revenue_services_b"].tolist(),
                    "Robotaxi": tesla["revenue_robotaxi_b"].tolist(),
                    "Optimus": tesla["revenue_optimus_b"].tolist(),
                },
                ["#111827", "#059669", "#6366f1", TESLA, "#f59e0b"],
            ),
            use_container_width=True,
        )
        st.plotly_chart(
            stacked_bar(
                "SpaceX — CA par activité (scénario actif)",
                spacex["year"].tolist(),
                {
                    "Starlink": spacex["revenue_connectivity_b"].tolist(),
                    "Launch": spacex["revenue_launch_b"].tolist(),
                    "IA / xAI": spacex["revenue_ai_b"].tolist(),
                },
                [SPACEX, "#0ea5e9", "#7c3aed"],
            ),
            use_container_width=True,
        )


def render_tesla(active: dict, all_sc: dict, compare: bool) -> None:
    tesla = active["tesla"]
    st.markdown("### Mix et marges")
    st.caption("Le FSD est un mémo (déjà dans l'auto / services). Robotaxi = miles payants × prix, flotte Tesla-owned + take rate réseau.")

    left, right = st.columns(2)
    with left:
        st.plotly_chart(
            stacked_bar(
                "CA Tesla par activité",
                tesla["year"].tolist(),
                {
                    "Auto": tesla["revenue_auto_b"].tolist(),
                    "Énergie": tesla["revenue_energy_b"].tolist(),
                    "Services": tesla["revenue_services_b"].tolist(),
                    "Robotaxi": tesla["revenue_robotaxi_b"].tolist(),
                    "Optimus": tesla["revenue_optimus_b"].tolist(),
                },
                ["#111827", "#059669", "#6366f1", TESLA, "#f59e0b"],
            ),
            use_container_width=True,
        )
    with right:
        fig = line_chart(
            "Marges Tesla",
            {
                "Marge brute": (tesla["year"], tesla["gross_margin"] * 100),
                "Marge opérationnelle": (tesla["year"], tesla["operating_margin"] * 100),
                "Marge EBITDA adj.": (tesla["year"], tesla["adj_ebitda_margin"] * 100),
            },
            "%",
            {"Marge brute": "#0f172a", "Marge opérationnelle": TESLA, "Marge EBITDA adj.": "#2563eb"},
        )
        st.plotly_chart(fig, use_container_width=True)

    if compare:
        series = {
            assumptions()["scenarios"][n]["label"]: (pack["tesla"]["year"], pack["tesla"]["adj_ebitda_b"])
            for n, pack in all_sc.items()
        }
        st.plotly_chart(
            line_chart(
                "Adjusted EBITDA Tesla vs jalons CEO",
                series,
                "Md$",
                {assumptions()["scenarios"][n]["label"]: SCENARIO_COLORS[n] for n in all_sc},
            ),
            use_container_width=True,
        )

    cols = [
        "year",
        "revenue_total_b",
        "revenue_auto_b",
        "revenue_energy_b",
        "revenue_robotaxi_b",
        "revenue_optimus_b",
        "gross_margin",
        "operating_margin",
        "adj_ebitda_b",
        "retail_deliveries",
        "storage_gwh",
        "fsd_subs_m",
        "robotaxi_fleet",
        "optimus_units",
        "fcf_b",
        "capex_total_b",
    ]
    table = tesla[cols].copy()
    table.columns = [
        "Année",
        "CA",
        "Auto",
        "Énergie",
        "Robotaxi",
        "Optimus GAAP",
        "Marge brute",
        "Marge op.",
        "EBITDA adj.",
        "Livraisons retail",
        "GWh",
        "FSD M",
        "Flotte robotaxi",
        "Optimus unités",
        "FCF",
        "Capex",
    ]
    st.dataframe(
        table.style.format(
            {
                "CA": "{:.1f}",
                "Auto": "{:.1f}",
                "Énergie": "{:.1f}",
                "Robotaxi": "{:.1f}",
                "Optimus GAAP": "{:.1f}",
                "Marge brute": "{:.1%}",
                "Marge op.": "{:.1%}",
                "EBITDA adj.": "{:.1f}",
                "Livraisons retail": "{:,.0f}",
                "GWh": "{:.0f}",
                "FSD M": "{:.2f}",
                "Flotte robotaxi": "{:,.0f}",
                "Optimus unités": "{:,.0f}",
                "FCF": "{:.1f}",
                "Capex": "{:.1f}",
            }
        ),
        hide_index=True,
        use_container_width=True,
    )
    st.markdown("### Optimus — GAAP vs économique")
    st.caption("Les robots internes (usine, Academy) ne sont pas du CA. Économie = heures × (salaire substitué − opex).")
    st.plotly_chart(
        line_chart(
            "Optimus : CA GAAP vs économies internes",
            {
                "CA GAAP (vendus)": (tesla["year"], tesla["revenue_optimus_b"]),
                "Économies internes": (tesla["year"], tesla["optimus_savings_b"]),
            },
            "Md$",
        ),
        use_container_width=True,
    )


def render_cybercab(active: dict) -> None:
    cab = active["cybercab"]
    tesla = active["tesla"]
    y = tesla[tesla["year"] == 2030].iloc[0]
    y26 = tesla[tesla["year"] == 2026].iloc[0]

    st.markdown(
        """
Le Cybercab n'est **pas encore** en flotte commerciale (juillet 2026 : essais salariés à Giga Texas).
Le scénario de base fait entrer les premiers exemplaires en **2027**. Un décalage à 2028-2029 casse 2027 ; 2030 rattrape via le backlog de production.
Le ROI ci-dessous est celui d'un véhicule **détenu par Tesla**, hors effet de levier.
        """
    )
    c1, c2, c3, c4 = st.columns(4)
    kpi_card(c1, "Production 2026", fmt_int(y26["cybercab_production"]))
    kpi_card(c2, "Flotte Tesla-owned 2030", fmt_int(y["robotaxi_fleet"]))
    kpi_card(c3, "Miles payants / cab 2030", fmt_int(y["paid_miles_per_cab"]))
    kpi_card(c4, "Payback 2030", f"{y['cab_payback']:.1f} ans" if y["cab_payback"] else "n/a")

    c5, c6, c7, c8 = st.columns(4)
    kpi_card(c5, "Prix / mile 2030", f"{y['price_per_mile']:.2f} $")
    kpi_card(c6, "Coût / mile 2030", f"{y['cost_per_mile']:.2f} $")
    kpi_card(c7, "Contribution / cab 2030", f"{fmt_int(y['cab_contrib_per_veh'])} $")
    kpi_card(c8, "ROI simple 2030", fmt_pct(y["cab_roi"] or 0))

    left, right = st.columns(2)
    with left:
        st.plotly_chart(
            line_chart(
                "Flotte et production",
                {
                    "Production annuelle": (cab["year"], cab["production"]),
                    "Flotte Tesla-owned": (cab["year"], cab["tesla_owned_fleet_eoy"]),
                    "Flotte réseau (vendue)": (cab["year"], cab["network_fleet_eoy"]),
                },
                "unités",
            ),
            use_container_width=True,
        )
    with right:
        st.plotly_chart(
            line_chart(
                "Prix, coût et ROI unitaire",
                {
                    "Prix $/mile": (cab["year"], cab["price_per_mile"]),
                    "Coût $/mile": (cab["year"], cab["cost_per_mile"]),
                    "ROI simple": (cab["year"], cab["simple_roi"].fillna(0)),
                },
                "$/mile ou ratio",
            ),
            use_container_width=True,
        )

    st.markdown("#### Formule")
    st.code(
        "miles_payants = utilisation × 16 h × 365 × 18 mph\n"
        "CA_véhicule = miles_payants × prix_mile\n"
        "contribution = CA_véhicule − miles_payants × coût_mile\n"
        "ROI_simple = contribution / capex\n"
        "payback = capex / contribution\n"
        "CA_robotaxi = flotte_Tesla × CA_véhicule + flotte_réseau × CA_véhicule × take_rate(30 %)",
        language="text",
    )
    st.caption(
        "Cible Musk 0,20 $/mile = borne du scénario Objectifs en 2030, pas une observation. "
        "Prix actuel Austin ~1,40 $/mile. Capex de base 22 k$ (25 k$ Musk, 18 k$ scénario objectifs)."
    )

    show = cab[
        [
            "year",
            "production",
            "tesla_owned_fleet_eoy",
            "paid_miles_per_vehicle",
            "price_per_mile",
            "cost_per_mile",
            "revenue_per_vehicle",
            "contribution_per_vehicle",
            "simple_roi",
            "payback_years",
            "fleet_revenue_b",
        ]
    ].copy()
    show.columns = [
        "Année",
        "Production",
        "Flotte Tesla",
        "Miles payants",
        "$/mile",
        "Coût/mile",
        "CA / cab",
        "Contribution",
        "ROI",
        "Payback ans",
        "CA flotte Md$",
    ]
    st.dataframe(
        show.style.format(
            {
                "Production": "{:,.0f}",
                "Flotte Tesla": "{:,.0f}",
                "Miles payants": "{:,.0f}",
                "$/mile": "{:.2f}",
                "Coût/mile": "{:.2f}",
                "CA / cab": "{:,.0f}",
                "Contribution": "{:,.0f}",
                "ROI": "{:.0%}",
                "Payback ans": "{:.1f}",
                "CA flotte Md$": "{:.1f}",
            }
        ),
        hide_index=True,
        use_container_width=True,
    )


def render_spacex(active: dict, all_sc: dict, compare: bool) -> None:
    spacex = active["spacex"]
    st.markdown(
        """
Starlink est le seul centre de profit clairement identifiable (marge d'exploitation Connectivity 2025 ≈ 39 %).
Les vols Starship internes (déploiement Starlink) **ne sont pas du CA**. Seuls Falcon externe, Starship externe, Dragon / Starshield / HLS comptent.
Le segment IA (xAI consolidé en 2026) reste le principal écart vers l'objectif 1 000 Md$.
        """
    )
    st.plotly_chart(
        stacked_bar(
            "CA SpaceX par activité",
            spacex["year"].tolist(),
            {
                "Starlink": spacex["revenue_connectivity_b"].tolist(),
                "Launch": spacex["revenue_launch_b"].tolist(),
                "IA / xAI": spacex["revenue_ai_b"].tolist(),
            },
            [SPACEX, "#0ea5e9", "#7c3aed"],
        ),
        use_container_width=True,
    )
    if compare:
        series = {
            assumptions()["scenarios"][n]["label"]: (pack["spacex"]["year"], pack["spacex"]["revenue_total_b"])
            for n, pack in all_sc.items()
        }
        fig = line_chart(
            "CA SpaceX vs objectif 1 000 Md$ (2030)",
            series,
            "Md$",
            {assumptions()["scenarios"][n]["label"]: SCENARIO_COLORS[n] for n in all_sc},
        )
        fig.add_hline(y=1000, line_dash="dash", line_color="#9f1239", annotation_text="Objectif Musk 2030")
        st.plotly_chart(fig, use_container_width=True)

    table = spacex[
        [
            "year",
            "starlink_subs_m",
            "starlink_arpu_month",
            "revenue_connectivity_b",
            "revenue_launch_b",
            "revenue_falcon_b",
            "revenue_starship_b",
            "starship_flights",
            "contrib_per_starship_m",
            "revenue_ai_b",
            "revenue_total_b",
            "operating_income_b",
            "operating_margin",
        ]
    ].copy()
    table.columns = [
        "Année",
        "Abonnés M",
        "ARPU $/mois",
        "Starlink",
        "Launch",
        "Falcon ext.",
        "Starship ext.",
        "Vols Starship",
        "Contrib. $/vol M",
        "IA",
        "CA",
        "EBIT",
        "Marge op.",
    ]
    st.dataframe(
        table.style.format(
            {
                "Abonnés M": "{:.1f}",
                "ARPU $/mois": "{:.0f}",
                "Starlink": "{:.1f}",
                "Launch": "{:.1f}",
                "Falcon ext.": "{:.1f}",
                "Starship ext.": "{:.1f}",
                "Vols Starship": "{:,.0f}",
                "Contrib. $/vol M": "{:.0f}",
                "IA": "{:.1f}",
                "CA": "{:.1f}",
                "EBIT": "{:.1f}",
                "Marge op.": "{:.0%}",
            }
        ),
        hide_index=True,
        use_container_width=True,
    )
    st.caption("Autorisation FAA Starbase : 25 vols/an. Au-delà, le modèle suppose d'autres sites — c'est une hypothèse, pas un fait.")


def render_rebase(active: dict) -> None:
    b = active["bridge"]
    st.markdown("### Pont H1 publié → FY 2026 projeté")
    st.caption(
        f"Dernier trimestre publié : **{b['last_quarter']}** (au {b['as_of']}). "
        f"Prochain print : **{b['next_print']}**. H2 n'est pas un fait — c'est l'implication du modèle."
    )
    c1, c2, c3, c4 = st.columns(4)
    kpi_card(c1, "CA H1 réel", fmt_md(b["h1_revenue_b"]))
    kpi_card(c2, "CA H2 implicite", fmt_md(b["h2_implied_revenue_b"]))
    kpi_card(c3, "CA FY projeté", fmt_md(b["fy_revenue_b"]), f"{b['h1_share_of_fy_revenue']*100:.0f} % déjà fait")
    kpi_card(c4, "FCF H2 implicite", fmt_md(b["h2_implied_fcf_b"]), "H1 FCF " + fmt_md(b["h1_fcf_b"]))

    c5, c6, c7, c8 = st.columns(4)
    kpi_card(c5, "Livraisons H1", fmt_int(b["h1_deliveries"]))
    kpi_card(c6, "Livraisons H2 implicites", fmt_int(b["h2_implied_deliveries"]))
    kpi_card(c7, "Capex H1 / FY", f"{fmt_md(b['h1_capex_b'])} / {fmt_md(b['fy_capex_b'])}")
    kpi_card(c8, "Stockage H1", f"{fmt_num(b['h1_storage_gwh'])} GWh")

    st.markdown("#### Trimestres Tesla déjà publiés")
    qdf = pd.DataFrame(published_quarters())
    st.dataframe(
        qdf.rename(
            columns={
                "quarter": "Trimestre",
                "revenue_b": "CA",
                "deliveries": "Livraisons",
                "storage_gwh": "GWh",
                "ocf_b": "OCF",
                "capex_b": "Capex",
                "fcf_b": "FCF",
                "source": "Source",
            }
        ),
        hide_index=True,
        use_container_width=True,
    )
    sx = spacex_ytd()
    st.markdown("#### SpaceX YTD")
    st.write(
        f"Q2 2026 : Starlink {fmt_md(sx['q2_connectivity_b'])} · Launch {fmt_md(sx['q2_space_b'])} · "
        f"IA {fmt_md(sx['q2_ai_b'])} · {fmt_num(sx['starlink_subs_m'])} M d'abonnés. {sx['note']}"
    )
    st.markdown("#### Checklist au prochain print (Q3)")
    for item in b["checklist"]:
        st.write(f"- {item}")
    st.info("Pour recaler : mettre à jour `data/actuals.yaml` et `data/tesla_history.yaml`. Ne pas interpoler un trimestre non publié.")


@st.cache_data(show_spinner=True)
def run_mc(scenario: str, n: int, seed: int) -> dict:
    summary = simulate(scenario, n=n, seed=seed)
    return {
        "n": summary.n,
        "p10": summary.p10,
        "p50": summary.p50,
        "p90": summary.p90,
        "start_year_counts": summary.start_year_counts,
        "samples": summary.samples,
    }


def render_uncertainty(scenario: str) -> None:
    st.markdown("### Monte-Carlo — leviers Cybercab")
    st.caption(
        "Tirages sur l'année d'entrée commerciale (2026 10 %, 2027 45 %, 2028 30 %, 2029 15 %), "
        "l'utilisation, le prix/mile, le coût/mile et l'échelle de production. Seed fixe = reproductible."
    )
    n = st.slider("Nombre de simulations", 100, 500, 300, 50)
    summary = run_mc(scenario, n, 42)
    labels = [
        ("robotaxi_ca_2027", "CA robotaxi 2027 (Md$)", True),
        ("robotaxi_ca_2030", "CA robotaxi 2030 (Md$)", True),
        ("fleet_2030", "Flotte 2030", False),
        ("roi_2030", "ROI Cybercab 2030", True),
        ("tesla_ca_2030", "CA Tesla 2030 (Md$)", True),
        ("fcf_2030", "FCF Tesla 2030 (Md$)", True),
    ]
    cols = st.columns(3)
    for i, (key, label, is_md) in enumerate(labels):
        p10, p50, p90 = summary["p10"][key], summary["p50"][key], summary["p90"][key]
        with cols[i % 3]:
            if key == "roi_2030":
                st.metric(label, fmt_pct(p50), f"P10 {fmt_pct(p10)} · P90 {fmt_pct(p90)}")
            elif key == "fleet_2030":
                st.metric(label, fmt_int(p50), f"P10 {fmt_int(p10)} · P90 {fmt_int(p90)}")
            else:
                st.metric(label, fmt_md(p50), f"P10 {fmt_md(p10)} · P90 {fmt_md(p90)}")

    fig = go.Figure()
    fig.add_trace(go.Histogram(x=summary["samples"]["robotaxi_ca_2030"], nbinsx=24, marker_color=TESLA, name="CA robotaxi 2030"))
    fig.update_layout(title=f"Distribution CA robotaxi 2030 ({summary['n']} tirages)", xaxis_title="Md$", height=360, template="plotly_white")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("#### Sensibilité : année d'entrée seule")
    delay = pd.DataFrame(delay_sensitivity(scenario))
    st.plotly_chart(
        line_chart(
            "CA robotaxi si on ne change que l'année d'entrée commerciale",
            {
                "2027": (delay["start_year"], delay["robotaxi_2027"]),
                "2030": (delay["start_year"], delay["robotaxi_2030"]),
            },
            "Md$",
        ),
        use_container_width=True,
    )
    st.caption("2027 est très sensible à la régulation. 2030 l'est peu : le backlog de production rattrape.")
    starts = summary["start_year_counts"]
    st.write("Tirages par année d'entrée : " + ", ".join(f"{y} → {c}" for y, c in sorted(starts.items())))


def render_cash(active: dict, all_sc: dict, compare: bool) -> None:
    tesla = active["tesla"]
    y26 = tesla[tesla["year"] == 2026].iloc[0]
    y30 = tesla[tesla["year"] == 2030].iloc[0]
    st.markdown("### Capex et free cash flow Tesla")
    st.caption("FCF = OCF − capex. OCF ≈ EBITDA adj. × 0,92. Capex flotte cash à la **production**, pas au déploiement. Plancher 2026 = 25 Md$ (guidage).")
    c1, c2, c3, c4 = st.columns(4)
    kpi_card(c1, "Capex 2026", fmt_md(y26["capex_total_b"]))
    kpi_card(c2, "FCF 2026", fmt_md(y26["fcf_b"]))
    kpi_card(c3, "Capex 2030", fmt_md(y30["capex_total_b"]))
    kpi_card(c4, "FCF 2030", fmt_md(y30["fcf_b"]))

    st.plotly_chart(
        stacked_bar(
            "Capex Tesla",
            tesla["year"].tolist(),
            {
                "Cœur (usines, AI, énergie)": tesla["capex_core_b"].tolist(),
                "Flotte Cybercab": tesla["capex_fleet_b"].tolist(),
                "Optimus interne": tesla["capex_optimus_b"].tolist(),
            },
            ["#111827", TESLA, "#f59e0b"],
        ),
        use_container_width=True,
    )
    if compare:
        series = {
            assumptions()["scenarios"][n]["label"]: (pack["tesla"]["year"], pack["tesla"]["fcf_b"])
            for n, pack in all_sc.items()
        }
        st.plotly_chart(
            line_chart("FCF Tesla", series, "Md$", {assumptions()["scenarios"][n]["label"]: SCENARIO_COLORS[n] for n in all_sc}),
            use_container_width=True,
        )
    else:
        st.plotly_chart(
            line_chart(
                "OCF vs capex vs FCF",
                {
                    "OCF": (tesla["year"], tesla["ocf_b"]),
                    "Capex": (tesla["year"], tesla["capex_total_b"]),
                    "FCF": (tesla["year"], tesla["fcf_b"]),
                },
                "Md$",
            ),
            use_container_width=True,
        )
    cash_tbl = tesla[["year", "adj_ebitda_b", "ocf_b", "capex_core_b", "capex_fleet_b", "capex_optimus_b", "capex_total_b", "fcf_b", "cash_eoy_b"]]
    cash_tbl = cash_tbl.rename(
        columns={
            "year": "Année",
            "adj_ebitda_b": "EBITDA adj.",
            "ocf_b": "OCF",
            "capex_core_b": "Capex cœur",
            "capex_fleet_b": "Capex flotte",
            "capex_optimus_b": "Capex Optimus",
            "capex_total_b": "Capex",
            "fcf_b": "FCF",
            "cash_eoy_b": "Cash fin d'année",
        }
    )
    st.dataframe(cash_tbl.style.format({c: "{:.1f}" for c in cash_tbl.columns if c != "Année"}), hide_index=True, use_container_width=True)


def _goal_row(item: dict) -> None:
    progress = item["progress"]
    hit = item["projected_year"]
    if hit:
        delta = f"atteint en {hit} dans ce scénario"
    else:
        delta = "non atteint d'ici 2035 dans ce scénario"
    st.markdown(f"**{item['label']}** · confiance {item['confidence']}")
    if item["unit"] == "usd_b":
        current_s, target_s = fmt_md(item["current"]), fmt_md(item["target"])
    else:
        current_s, target_s = fmt_int(item["current"]), fmt_int(item["target"])
    st.progress(min(max(progress, 0.0), 1.0), text=f"{current_s} / {target_s} · {delta}")
    if item.get("definition"):
        st.caption(item["definition"])


def render_goals(active: dict) -> None:
    st.markdown("### Plan CEO Tesla 2025 (12 jalons opérationnels)")
    st.caption("Source : Exhibit 4.4 / DEF 14A. Un jalon produit ne peut servir qu'une seule tranche.")
    product = [k for k in active["tesla_kpis"] if k["id"] in {"vehicles_cumulative", "fsd_active", "bots_delivered", "robotaxis_commercial"}]
    for item in product:
        _goal_row(item)

    st.markdown("### Adjusted EBITDA Tesla")
    ebitda = [k for k in active["tesla_kpis"] if k["id"].startswith("ebitda_")]
    cols = st.columns(3)
    for i, item in enumerate(ebitda):
        with cols[i % 3]:
            hit = f"→ {item['projected_year']}" if item["projected_year"] else "→ 2035+"
            st.metric(item["label"], hit, f"actuel {fmt_md(item['current'], 1)}")

    st.markdown("### SpaceX")
    for item in active["spacex_kpis"]:
        _goal_row(item)

    g = goals()
    st.markdown("### Autres cibles d'exploitation Tesla")
    for item in g["tesla_operating_targets"]:
        st.write(f"- **{item['label']}** : {item.get('target')} {item.get('unit', '')} — {item.get('note', item.get('source'))}")


def render_sources() -> None:
    data = sources()
    st.markdown(f"Registre arrêté au **{data['as_of']}**. Chaque série du modèle pointe vers un `id` ci-dessous.")
    for company, items in (("Tesla", data["tesla"]), ("SpaceX", data["spacex"])):
        st.subheader(company)
        for item in items:
            url = item.get("url")
            title = f"[{item['title']}]({url})" if url else item["title"]
            st.markdown(f"**`{item['id']}`** · `{item['type']}` — {title}")
            if item.get("note"):
                st.caption(item["note"])
            st.write("Utilisé pour : " + ", ".join(item.get("used_for", [])))


if __name__ == "__main__":
    main()
