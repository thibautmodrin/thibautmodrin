"""Monte-Carlo sur les leviers Cybercab (régulation, utilisation, prix, coût).

Les tirages déforment la S-curve du scénario de base. Seed fixe → reproductible.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from src.engine import project
from src.load import assumptions, years
from src.overrides import scale_to_anchor


@dataclass(frozen=True)
class McSummary:
    n: int
    seed: int
    labels: list[str]
    p10: dict[str, float]
    p50: dict[str, float]
    p90: dict[str, float]
    start_year_counts: dict[int, int]
    samples: dict[str, list[float]]


def _clip(value: float, lo: float, hi: float) -> float:
    return float(min(max(value, lo), hi))


def simulate(scenario: str = "base", n: int = 400, seed: int = 42) -> McSummary:
    cfg = assumptions()
    cab0 = cfg["scenarios"][scenario]["cybercab"]
    yrs = years()
    i2030 = yrs.index(2030)
    rng = np.random.default_rng(seed)

    mc = cfg["montecarlo"]
    start_years = [int(y) for y in mc["start_years"]]
    start_probs = np.array(mc["start_year_probs"], dtype=float)
    start_probs = start_probs / start_probs.sum()

    keys = [
        "tesla_ca_2030",
        "robotaxi_ca_2030",
        "fleet_2030",
        "roi_2030",
        "fcf_2030",
        "tesla_ca_2027",
        "robotaxi_ca_2027",
    ]
    bucket = {k: [] for k in keys}
    start_counts: dict[int, int] = {y: 0 for y in start_years}

    prod0 = list(map(float, cab0["production"]))
    price0 = list(map(float, cab0["price_per_mile"]))
    cost0 = list(map(float, cab0["cost_per_mile"]))
    util0 = list(map(float, cab0["utilization"]))

    for _ in range(n):
        start = int(rng.choice(start_years, p=start_probs))
        start_counts[start] += 1
        prod_scale = float(rng.lognormal(mean=0.0, sigma=mc["production_log_sigma"]))
        util_2030 = _clip(float(rng.normal(mc["util_2030_mean"], mc["util_2030_sd"])), 0.12, 0.68)
        price_2030 = _clip(float(rng.normal(mc["price_2030_mean"], mc["price_2030_sd"])), 0.18, 1.40)
        cost_2030 = _clip(float(rng.normal(mc["cost_2030_mean"], mc["cost_2030_sd"])), 0.14, 0.95)
        if cost_2030 >= price_2030:
            cost_2030 = price_2030 * 0.85

        overrides = {
            "production": [p * prod_scale for p in prod0],
            "utilization": scale_to_anchor(util0, util_2030, i2030, floor=0.10, cap=0.70),
            "price_per_mile": scale_to_anchor(price0, price_2030, i2030, floor=0.15, cap=2.0),
            "cost_per_mile": scale_to_anchor(cost0, cost_2030, i2030, floor=0.12, cap=1.1),
            "commercial_start_year": start,
        }
        proj = project(scenario, overrides)
        t27 = next(r for r in proj.tesla if r.year == 2027)
        t30 = next(r for r in proj.tesla if r.year == 2030)
        bucket["tesla_ca_2030"].append(t30.revenue_total_b)
        bucket["robotaxi_ca_2030"].append(t30.revenue_robotaxi_b)
        bucket["fleet_2030"].append(t30.robotaxi_fleet)
        bucket["roi_2030"].append(t30.cab_roi or 0.0)
        bucket["fcf_2030"].append(t30.fcf_b)
        bucket["tesla_ca_2027"].append(t27.revenue_total_b)
        bucket["robotaxi_ca_2027"].append(t27.revenue_robotaxi_b)

    def pct(arr: list[float], q: float) -> float:
        return float(np.percentile(arr, q))

    return McSummary(
        n=n,
        seed=seed,
        labels=keys,
        p10={k: pct(bucket[k], 10) for k in keys},
        p50={k: pct(bucket[k], 50) for k in keys},
        p90={k: pct(bucket[k], 90) for k in keys},
        start_year_counts=start_counts,
        samples=bucket,
    )


def delay_sensitivity(scenario: str = "base") -> list[dict]:
    """Un levier à la fois : année d'entrée commerciale, reste du scénario inchangé."""
    rows = []
    for start in (2026, 2027, 2028, 2029):
        proj = project(scenario, {"commercial_start_year": start})
        t30 = next(r for r in proj.tesla if r.year == 2030)
        t27 = next(r for r in proj.tesla if r.year == 2027)
        rows.append(
            {
                "start_year": start,
                "robotaxi_2027": t27.revenue_robotaxi_b,
                "robotaxi_2030": t30.revenue_robotaxi_b,
                "fleet_2030": t30.robotaxi_fleet,
                "tesla_ca_2030": t30.revenue_total_b,
                "fcf_2030": t30.fcf_b,
            }
        )
    return rows
