"""Cadence Starship + Falcon externe.

Le launch interne (déploiement Starlink) n'est pas du CA. Seuls les vols
externes et le « other » (Dragon, Starshield, HLS) comptent au chiffre d'affaires.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class LaunchYear:
    year: int
    falcon_external: float
    starship_flights: float
    starship_external: float
    starship_price_m: float
    starship_cost_m: float
    revenue_falcon_b: float
    revenue_starship_b: float
    revenue_other_b: float
    revenue_launch_b: float
    contrib_per_starship_m: float
    starship_gross_profit_b: float


def project_launch(
    years: list[int],
    falcon_external: list[float],
    falcon_price_m: float,
    launch_other_b: list[float],
    starship_flights: list[float],
    starship_external_share: list[float],
    starship_price_m: list[float],
    starship_cost_m: list[float],
) -> list[LaunchYear]:
    n = len(years)
    series = (
        falcon_external,
        launch_other_b,
        starship_flights,
        starship_external_share,
        starship_price_m,
        starship_cost_m,
    )
    if any(len(s) != n for s in series):
        raise ValueError("séries Starship : même longueur que years")

    rows: list[LaunchYear] = []
    for i, year in enumerate(years):
        share = float(starship_external_share[i])
        if not 0 <= share <= 1:
            raise ValueError("starship_external_share in [0, 1]")
        flights = float(starship_flights[i])
        external = flights * share
        price = float(starship_price_m[i])
        cost = float(starship_cost_m[i])
        falcon_b = float(falcon_external[i]) * falcon_price_m / 1000.0
        starship_b = external * price / 1000.0
        other = float(launch_other_b[i])
        rows.append(
            LaunchYear(
                year=year,
                falcon_external=float(falcon_external[i]),
                starship_flights=flights,
                starship_external=external,
                starship_price_m=price,
                starship_cost_m=cost,
                revenue_falcon_b=falcon_b,
                revenue_starship_b=starship_b,
                revenue_other_b=other,
                revenue_launch_b=falcon_b + starship_b + other,
                contrib_per_starship_m=price - cost,
                starship_gross_profit_b=external * (price - cost) / 1000.0,
            )
        )
    return rows
