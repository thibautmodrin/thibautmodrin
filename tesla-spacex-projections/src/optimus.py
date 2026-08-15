"""Économie unitaire Optimus.

Le GAAP ne compte que les robots vendus à l'extérieur. Les unités internes
(usine, Academy) sont un capex + une économie de main-d'œuvre, pas du CA.
"""

from __future__ import annotations

from dataclasses import dataclass

from src.cybercab import payback_years, simple_roi


HOURS_PER_YEAR = 365.0


@dataclass(frozen=True)
class OptimusYear:
    year: int
    produced: float
    internal_units: float
    external_units: float
    cumulative_delivered: float
    revenue_gaap_b: float
    gross_profit_gaap_b: float
    capex_internal_b: float
    hours_per_internal: float
    savings_per_internal: float
    savings_b: float
    simple_roi: float | None
    payback_years: float | None


def project_optimus(
    years: list[int],
    produced: list[float],
    internal_share: list[float],
    asp: float,
    gross_margin: float,
    capex_per_unit: float,
    utilization: list[float],
    hours_per_day: float,
    wage_per_hour: float,
    opex_per_hour: float,
) -> list[OptimusYear]:
    n = len(years)
    if len(produced) != n or len(internal_share) != n or len(utilization) != n:
        raise ValueError("séries Optimus : même longueur que years")

    cumulative = 0.0
    rows: list[OptimusYear] = []
    for i, year in enumerate(years):
        units = float(produced[i])
        internal = units * float(internal_share[i])
        external = units - internal
        cumulative += units
        hours = float(utilization[i]) * hours_per_day * HOURS_PER_YEAR
        savings_each = hours * (wage_per_hour - opex_per_hour)
        rev = external * asp / 1e9
        gp = rev * gross_margin
        capex_int = internal * capex_per_unit / 1e9
        rows.append(
            OptimusYear(
                year=year,
                produced=units,
                internal_units=internal,
                external_units=external,
                cumulative_delivered=cumulative,
                revenue_gaap_b=rev,
                gross_profit_gaap_b=gp,
                capex_internal_b=capex_int,
                hours_per_internal=hours,
                savings_per_internal=savings_each,
                savings_b=internal * savings_each / 1e9,
                simple_roi=simple_roi(savings_each, capex_per_unit),
                payback_years=payback_years(savings_each, capex_per_unit),
            )
        )
    return rows
