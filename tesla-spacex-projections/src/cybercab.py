"""Économie unitaire Cybercab / robotaxi.

Toutes les formules sont déterministes et testées. Aucun CAGR magique :
flotte × miles payants × prix/mile, moins coût/mile, rapporté au capex.
"""

from __future__ import annotations

from dataclasses import dataclass


HOURS_PER_YEAR_FACTOR = 365.0


@dataclass(frozen=True)
class UnitEconomics:
    year: int
    fleet_avg: float
    utilization: float
    paid_miles_per_vehicle: float
    price_per_mile: float
    cost_per_mile: float
    revenue_per_vehicle: float
    opex_per_vehicle: float
    contribution_per_vehicle: float
    contribution_margin: float
    capex_per_vehicle: float
    simple_roi: float | None
    payback_years: float | None
    fleet_revenue_b: float
    fleet_gross_profit_b: float
    tesla_owned_fleet_eoy: float
    network_fleet_eoy: float
    production: float
    sold_units: float
    hardware_revenue_b: float


def paid_miles_per_vehicle(
    utilization: float,
    hours_per_day: float,
    avg_speed_mph: float,
) -> float:
    """Miles payants / véhicule / an.

    utilization = part du temps disponible avec un client payant
    (le deadhead est déjà hors de ce ratio).
    """
    if utilization < 0 or utilization > 1:
        raise ValueError("utilization must be in [0, 1]")
    return utilization * hours_per_day * HOURS_PER_YEAR_FACTOR * avg_speed_mph


def simple_roi(contribution: float, capex: float) -> float | None:
    if capex <= 0:
        return None
    return contribution / capex


def payback_years(contribution: float, capex: float) -> float | None:
    if contribution <= 0 or capex <= 0:
        return None
    return capex / contribution


def legacy_robotaxi_path(
    years: list[int],
    start_fleet: float,
    peak: float,
    peak_year: int,
    retire_after_peak: float = 0.35,
) -> dict[int, float]:
    """Flotte Model Y/3 robotaxi : rampe jusqu'à un pic, puis remplacement Cybercab."""
    out: dict[int, float] = {}
    for year in years:
        if year <= peak_year:
            span = max(peak_year - years[0], 1)
            t = (year - years[0]) / span
            out[year] = start_fleet + t * (peak - start_fleet)
        else:
            prev = out[year - 1]
            out[year] = max(prev * (1 - retire_after_peak), 0.0)
    return out


def project_cybercab(
    years: list[int],
    production: list[float],
    tesla_owned_share: list[float],
    utilization: list[float],
    price_per_mile: list[float],
    cost_per_mile: list[float],
    capex_per_vehicle: float,
    retire_rate: float,
    hours_per_day: float,
    avg_speed_mph: float,
    network_take_rate: float,
    hardware_asp: float,
    legacy_start: float,
    legacy_peak: float,
    legacy_peak_year: int,
    first_year_commercial_share: float,
) -> list[UnitEconomics]:
    n = len(years)
    for series in (production, tesla_owned_share, utilization, price_per_mile, cost_per_mile):
        if len(series) != n:
            raise ValueError("toutes les séries Cybercab doivent avoir len(years)")

    legacy = legacy_robotaxi_path(years, legacy_start, legacy_peak, legacy_peak_year)
    owned = 0.0
    network = 0.0
    rows: list[UnitEconomics] = []

    for i, year in enumerate(years):
        produced = float(production[i])
        owned_share = float(tesla_owned_share[i])
        new_owned = produced * owned_share
        new_sold = produced * (1 - owned_share)

        # 2026 : production démarre, très peu entre en flotte commerciale.
        if i == 0:
            new_owned *= first_year_commercial_share
            new_sold *= first_year_commercial_share

        owned = owned * (1 - retire_rate) + new_owned
        network = network * (1 - retire_rate) + new_sold
        tesla_fleet = owned + legacy[year]
        fleet_avg = tesla_fleet  # approximation EOY ≈ moyenne en rampe rapide

        miles = paid_miles_per_vehicle(utilization[i], hours_per_day, avg_speed_mph)
        rev_veh = miles * price_per_mile[i]
        opex_veh = miles * cost_per_mile[i]
        contrib = rev_veh - opex_veh
        margin = (contrib / rev_veh) if rev_veh else 0.0

        owned_rev = tesla_fleet * rev_veh
        network_rev = network * rev_veh * network_take_rate
        fleet_rev = (owned_rev + network_rev) / 1e9
        fleet_gp = (
            tesla_fleet * contrib + network * (rev_veh * network_take_rate - 0)
        ) / 1e9
        # Pour le réseau, Tesla encaisse le take rate ; le coût d'exploitation
        # est surtout chez le propriétaire. On ne retranche pas le cost/mile Tesla-side.

        hw_rev = produced * (1.0 - owned_share) * hardware_asp / 1e9

        rows.append(
            UnitEconomics(
                year=year,
                fleet_avg=fleet_avg,
                utilization=utilization[i],
                paid_miles_per_vehicle=miles,
                price_per_mile=price_per_mile[i],
                cost_per_mile=cost_per_mile[i],
                revenue_per_vehicle=rev_veh,
                opex_per_vehicle=opex_veh,
                contribution_per_vehicle=contrib,
                contribution_margin=margin,
                capex_per_vehicle=capex_per_vehicle,
                simple_roi=simple_roi(contrib, capex_per_vehicle),
                payback_years=payback_years(contrib, capex_per_vehicle),
                fleet_revenue_b=fleet_rev,
                fleet_gross_profit_b=fleet_gp,
                tesla_owned_fleet_eoy=tesla_fleet,
                network_fleet_eoy=network,
                production=produced,
                sold_units=produced * (1 - owned_share),
                hardware_revenue_b=hw_rev,
            )
        )
    return rows
