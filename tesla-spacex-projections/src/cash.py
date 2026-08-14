"""Capex et free cash flow Tesla.

FCF = OCF − capex. OCF ≈ EBITDA adj. × taux de conversion.
Le capex flotte (Cybercab Tesla-owned) est cash à la production, pas au déploiement.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CashYear:
    year: int
    capex_core_b: float
    capex_fleet_b: float
    capex_optimus_b: float
    capex_total_b: float
    ocf_b: float
    fcf_b: float
    cash_eoy_b: float


def project_cash(
    years: list[int],
    adj_ebitda_b: list[float],
    capex_core_b: list[float],
    fleet_units_produced_owned: list[float],
    capex_per_vehicle: float,
    optimus_internal_capex_b: list[float],
    ocf_conversion: float,
    cash_start_b: float,
    capex_2026_floor_b: float | None = 25.0,
) -> list[CashYear]:
    if ocf_conversion < 0:
        raise ValueError("ocf_conversion must be >= 0")
    cash = cash_start_b
    rows: list[CashYear] = []
    for i, year in enumerate(years):
        fleet_capex = fleet_units_produced_owned[i] * capex_per_vehicle / 1e9
        total = capex_core_b[i] + fleet_capex + optimus_internal_capex_b[i]
        if year == 2026 and capex_2026_floor_b is not None:
            total = max(total, capex_2026_floor_b)
        ocf = adj_ebitda_b[i] * ocf_conversion
        fcf = ocf - total
        cash = cash + fcf
        rows.append(
            CashYear(
                year=year,
                capex_core_b=capex_core_b[i],
                capex_fleet_b=fleet_capex,
                capex_optimus_b=optimus_internal_capex_b[i],
                capex_total_b=total,
                ocf_b=ocf,
                fcf_b=fcf,
                cash_eoy_b=cash,
            )
        )
    return rows
