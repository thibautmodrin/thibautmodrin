"""Recalage de l'année en cours : réalisé YTD vs FY projeté.

Quand Q3/Q4 sort, on met à jour data/actuals.yaml — le moteur n'invente
pas le trimestre publié.
"""

from __future__ import annotations

from dataclasses import dataclass

from src.engine import Projection
from src.load import actuals


@dataclass(frozen=True)
class TeslaBridge:
    as_of: str
    last_quarter: str
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
    h2_implied_revenue_b: float
    h2_implied_deliveries: float
    h2_implied_fcf_b: float
    h1_share_of_fy_revenue: float
    next_print: str
    checklist: list[str]


def tesla_2026_bridge(proj: Projection) -> TeslaBridge:
    act = actuals()["tesla_2026"]
    fy = next(r for r in proj.tesla if r.year == 2026)
    h1_rev = float(act["h1_revenue_b"])
    return TeslaBridge(
        as_of=str(act["as_of"]),
        last_quarter=str(act["last_quarter"]),
        h1_revenue_b=h1_rev,
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
        h2_implied_revenue_b=fy.revenue_total_b - h1_rev,
        h2_implied_deliveries=fy.retail_deliveries - float(act["h1_deliveries"]),
        h2_implied_fcf_b=fy.fcf_b - float(act["h1_fcf_b"]),
        h1_share_of_fy_revenue=h1_rev / fy.revenue_total_b if fy.revenue_total_b else 0.0,
        next_print=str(act["next_print"]),
        checklist=list(act["checklist"]),
    )


def published_quarters() -> list[dict]:
    return list(actuals()["tesla_quarters"])


def spacex_ytd() -> dict:
    return dict(actuals()["spacex_2026"])
