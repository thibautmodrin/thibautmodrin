"""Recalage de l'année en cours : réalisé YTD vs FY projeté.

Quand Q3/Q4 sort, on met à jour data/actuals.yaml — le moteur n'invente
pas le trimestre publié. Le reste de l'année = run-rate du dernier trimestre.
"""

from __future__ import annotations

from dataclasses import dataclass

from src.engine import Projection
from src.load import actuals
from src.tesla_seed import last_published_2026, remaining_label, remaining_quarters, ytd_totals


@dataclass(frozen=True)
class TeslaBridge:
    as_of: str
    last_quarter: str
    remaining_label: str
    remaining_quarters: int
    ytd_revenue_b: float
    ytd_deliveries: float
    ytd_storage_gwh: float
    ytd_ocf_b: float
    ytd_capex_b: float
    ytd_fcf_b: float
    h1_revenue_b: float
    h1_deliveries: float
    h1_storage_gwh: float
    h1_ocf_b: float
    h1_capex_b: float
    h1_fcf_b: float
    fy_revenue_b: float
    fy_deliveries: float
    fy_storage_gwh: float
    fy_capex_b: float
    fy_fcf_b: float
    remaining_implied_revenue_b: float
    remaining_implied_deliveries: float
    remaining_implied_fcf_b: float
    ytd_share_of_fy_revenue: float
    h2_implied_revenue_b: float
    h2_implied_deliveries: float
    h2_implied_fcf_b: float
    h1_share_of_fy_revenue: float
    next_print: str
    checklist: list[str]
    rebase_rule: str


def tesla_2026_bridge(proj: Projection) -> TeslaBridge:
    act = actuals()["tesla_2026"]
    fy = next(r for r in proj.tesla if r.year == 2026)
    ytd = ytd_totals(2026)
    n_rem = remaining_quarters(2026)
    last = last_published_2026()
    last_q = str(act.get("last_quarter") or (last["_q"] if last else ""))
    ytd_rev = float(ytd["revenue_b"] or act["h1_revenue_b"])
    ytd_del = float(ytd["deliveries"] or act["h1_deliveries"])
    ytd_gwh = float(ytd["storage_gwh"] or act["h1_storage_gwh"])
    ytd_ocf = float(ytd["ocf_b"] or act["h1_ocf_b"])
    ytd_capex = float(ytd["capex_b"] or act["h1_capex_b"])
    ytd_fcf = float(ytd["fcf_b"] or act["h1_fcf_b"])
    rem_rev = fy.revenue_total_b - ytd_rev
    rem_del = fy.retail_deliveries - ytd_del
    rem_fcf = fy.fcf_b - ytd_fcf
    share = ytd_rev / fy.revenue_total_b if fy.revenue_total_b else 0.0
    return TeslaBridge(
        as_of=str(act["as_of"]),
        last_quarter=last_q,
        remaining_label=remaining_label(n_rem),
        remaining_quarters=n_rem,
        ytd_revenue_b=ytd_rev,
        ytd_deliveries=ytd_del,
        ytd_storage_gwh=ytd_gwh,
        ytd_ocf_b=ytd_ocf,
        ytd_capex_b=ytd_capex,
        ytd_fcf_b=ytd_fcf,
        h1_revenue_b=float(act["h1_revenue_b"]),
        h1_deliveries=float(act["h1_deliveries"]),
        h1_storage_gwh=float(act["h1_storage_gwh"]),
        h1_ocf_b=float(act["h1_ocf_b"]),
        h1_capex_b=float(act["h1_capex_b"]),
        h1_fcf_b=float(act["h1_fcf_b"]),
        fy_revenue_b=fy.revenue_total_b,
        fy_deliveries=fy.retail_deliveries,
        fy_storage_gwh=fy.storage_gwh,
        fy_capex_b=fy.capex_total_b,
        fy_fcf_b=fy.fcf_b,
        remaining_implied_revenue_b=rem_rev,
        remaining_implied_deliveries=rem_del,
        remaining_implied_fcf_b=rem_fcf,
        ytd_share_of_fy_revenue=share,
        h2_implied_revenue_b=rem_rev,
        h2_implied_deliveries=rem_del,
        h2_implied_fcf_b=rem_fcf,
        h1_share_of_fy_revenue=share,
        next_print=str(act["next_print"]),
        checklist=list(act["checklist"]),
        rebase_rule="YTD publié + run-rate du dernier trimestre × trimestres restants. 2027-2035 inchangés.",
    )


def published_quarters() -> list[dict]:
    return list(actuals()["tesla_quarters"])


def spacex_ytd() -> dict:
    return dict(actuals()["spacex_2026"])
