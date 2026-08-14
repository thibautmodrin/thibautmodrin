"""Suivi des jalons (CEO award Tesla + cibles SpaceX)."""

from __future__ import annotations

from dataclasses import dataclass

from src.engine import Projection
from src.load import goals, tesla_history, valuation as load_valuation


@dataclass
class KpiStatus:
    id: str
    company: str
    label: str
    current: float
    target: float
    unit: str
    progress: float
    projected_year: int | None
    projected_value: float | None
    confidence: str
    definition: str = ""


def _year_hit(values: list[tuple[int, float]], target: float) -> tuple[int | None, float | None]:
    for year, value in values:
        if value >= target:
            return year, value
    last_year, last_val = values[-1]
    return None, last_val


def tesla_kpis(proj: Projection) -> list[KpiStatus]:
    g = goals()["tesla_ceo_award_2025"]
    hist = tesla_history()["snapshot_latest"]
    tesla = proj.tesla
    start_cumul = hist["cumulative_deliveries_m"] * 1_000_000
    # Les livraisons 2026-N s'ajoutent au cumul H1 2026. On évite de double-compter
    # H1 en prenant le FY 2026 entier comme flux de l'année (approximation).
    cumul = start_cumul
    cumul_path: list[tuple[int, float]] = []
    for row in tesla:
        # 2026 : on part du cumul Q2 et on ajoute ~H2 + Cybercab flotte nouvelle.
        if row.year == 2026:
            h2_retail = max(row.retail_deliveries - hist["h1_deliveries"], 0)
            cumul = start_cumul + h2_retail + row.cybercab_production
        else:
            cumul += row.retail_deliveries + row.cybercab_production
        cumul_path.append((row.year, cumul))

    fsd_path = [(r.year, r.fsd_subs_m * 1_000_000) for r in tesla]
    bots_path = []
    running_bots = 0.0
    for r in tesla:
        running_bots += r.optimus_units
        bots_path.append((r.year, running_bots))
    taxi_path = [(r.year, r.robotaxi_fleet) for r in tesla]
    ebitda_path = [(r.year, r.adj_ebitda_b) for r in tesla]

    mapping = {
        "vehicles_cumulative": (cumul_path, start_cumul, "medium"),
        "fsd_active": (fsd_path, hist["fsd_subs_m"] * 1_000_000, "high"),
        "bots_delivered": (bots_path, 0.0, "low"),
        "robotaxis_commercial": (taxi_path, float(hist["robotaxi_fleet_estimate"]), "low"),
    }

    out: list[KpiStatus] = []
    for item in g["product"]:
        path, current, conf = mapping[item["id"]]
        year, value = _year_hit(path, float(item["target"]))
        out.append(
            KpiStatus(
                id=item["id"],
                company="Tesla",
                label=item["label"],
                current=float(item.get("current", current)),
                target=float(item["target"]),
                unit=item["unit"],
                progress=min(float(item.get("current", current)) / float(item["target"]), 1.0),
                projected_year=year,
                projected_value=value,
                confidence=item.get("current_confidence", conf),
                definition=item.get("definition", "").strip(),
            )
        )

    ebitda_targets = g["ebitda"]
    current_ebitda = 14.596  # FY 2025, dernier exercice clos
    for item in ebitda_targets:
        year, value = _year_hit(ebitda_path, float(item["target_b"]))
        out.append(
            KpiStatus(
                id=item["id"],
                company="Tesla",
                label=item["label"],
                current=current_ebitda,
                target=float(item["target_b"]),
                unit="usd_b",
                progress=min(current_ebitda / float(item["target_b"]), 1.0),
                projected_year=year,
                projected_value=value,
                confidence="medium",
                definition="Adjusted EBITDA Tesla, défini dans les Update decks.",
            )
        )
    return out


def tesla_market_kpis(rows) -> list[KpiStatus]:
    """Jalons de capitalisation du CEO award, évalués sur le cours implicite."""
    if hasattr(rows, "itertuples"):
        path = [(int(r.year), float(r.market_cap_t)) for r in rows.itertuples()]
    else:
        path = [(r.year, r.market_cap_t) for r in rows]
    current = float(load_valuation()["tesla"]["market_cap_t"])
    out: list[KpiStatus] = []
    for target in (2.0, 8.5):
        year, value = _year_hit(path, target)
        out.append(
            KpiStatus(
                id=f"mcap_{target:g}t",
                company="Tesla",
                label=f"Capitalisation {target:g} T$",
                current=current,
                target=target,
                unit="usd_t",
                progress=min(current / target, 1.0),
                projected_year=year,
                projected_value=value,
                confidence="low",
                definition=(
                    "Jalon de market cap du CEO award 2025. "
                    "Le cours implicite = EV (CA × EV/S et EBITDA × EV/EBITDA) + cash net, "
                    "divisé par les actions diluées. Les multiples sont des hypothèses."
                ),
            )
        )
    return out


def spacex_kpis(proj: Projection) -> list[KpiStatus]:
    g = goals()["spacex_targets"]
    sx = proj.spacex
    out: list[KpiStatus] = []

    subs_path = [(r.year, r.starlink_subs_m * 1_000_000) for r in sx]
    rev_path = [(r.year, r.revenue_total_b) for r in sx]
    arr_2026 = next(r.revenue_total_b for r in sx if r.year == 2026)

    for item in g:
        if item["id"] == "starlink_subs_near":
            year, value = _year_hit(subs_path, float(item["target"]))
            out.append(
                KpiStatus(
                    id=item["id"],
                    company="SpaceX",
                    label=item["label"],
                    current=float(item["current"]),
                    target=float(item["target"]),
                    unit=item["unit"],
                    progress=min(float(item["current"]) / float(item["target"]), 1.0),
                    projected_year=year,
                    projected_value=value,
                    confidence="medium",
                    definition=item.get("note", ""),
                )
            )
        elif item["id"] == "arr_100b_2026":
            out.append(
                KpiStatus(
                    id=item["id"],
                    company="SpaceX",
                    label=item["label"],
                    current=arr_2026,
                    target=float(item["target_b"]),
                    unit="usd_b",
                    progress=min(arr_2026 / float(item["target_b"]), 1.0),
                    projected_year=2026 if arr_2026 >= item["target_b"] else None,
                    projected_value=arr_2026,
                    confidence="low",
                    definition="Commentaire Musk, pas un guidage audité. Proxy = CA FY 2026 du modèle.",
                )
            )
        elif item["id"] == "revenue_1t_2030":
            year, value = _year_hit(rev_path, float(item["target_b"]))
            current = sx[0].revenue_total_b
            out.append(
                KpiStatus(
                    id=item["id"],
                    company="SpaceX",
                    label=item["label"],
                    current=current,
                    target=float(item["target_b"]),
                    unit="usd_b",
                    progress=min(current / float(item["target_b"]), 1.0),
                    projected_year=year,
                    projected_value=value,
                    confidence="low",
                    definition=item.get("note", ""),
                )
            )
    return out
