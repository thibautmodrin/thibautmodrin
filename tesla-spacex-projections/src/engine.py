"""Projections Tesla et SpaceX 2026-2035.

Principe : bottom-up (volumes × prix) puis marges par activité.
Le scénario « objectifs » n'est pas une prévision : c'est la trajectoire
d'entreprise à comparer au scénario de base.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import pandas as pd

from src.cybercab import UnitEconomics, project_cybercab
from src.load import assumptions, spacex_history, tesla_history, years as horizon_years


def _lerp(start: float, end: float, steps: int) -> list[float]:
    if steps <= 1:
        return [end]
    return [start + (end - start) * i / (steps - 1) for i in range(steps)]


def _grow(start: float, cagr: float, n: int) -> list[float]:
    return [start * ((1 + cagr) ** i) for i in range(n)]


@dataclass
class TeslaYear:
    year: int
    retail_deliveries: float
    asp_auto: float
    revenue_auto_b: float
    storage_gwh: float
    revenue_energy_b: float
    revenue_services_b: float
    revenue_robotaxi_b: float
    revenue_cybercab_hw_b: float
    revenue_optimus_b: float
    revenue_total_b: float
    gross_profit_b: float
    gross_margin: float
    operating_income_b: float
    operating_margin: float
    adj_ebitda_b: float
    adj_ebitda_margin: float
    fsd_subs_m: float
    fsd_memo_revenue_b: float
    cybercab_production: float
    robotaxi_fleet: float
    network_fleet: float
    optimus_units: float
    paid_miles_per_cab: float
    price_per_mile: float
    cost_per_mile: float
    cab_roi: float | None
    cab_payback: float | None
    cab_contrib_per_veh: float


@dataclass
class SpaceXYear:
    year: int
    starlink_subs_m: float
    starlink_arpu_month: float
    revenue_connectivity_b: float
    revenue_launch_b: float
    revenue_ai_b: float
    revenue_total_b: float
    oi_connectivity_b: float
    oi_launch_b: float
    oi_ai_b: float
    operating_income_b: float
    operating_margin: float


@dataclass
class Projection:
    scenario: str
    tesla: list[TeslaYear]
    spacex: list[SpaceXYear]
    cybercab: list[UnitEconomics]
    notes: list[str] = field(default_factory=list)

    def tesla_frame(self) -> pd.DataFrame:
        return pd.DataFrame([t.__dict__ for t in self.tesla])

    def spacex_frame(self) -> pd.DataFrame:
        return pd.DataFrame([s.__dict__ for s in self.spacex])

    def cybercab_frame(self) -> pd.DataFrame:
        return pd.DataFrame([c.__dict__ for c in self.cybercab])


def _fsd_path(years: list[int], start_m: float, y2030: float, y2035: float) -> list[float]:
    i2030 = years.index(2030)
    first = _lerp(start_m, y2030, i2030 + 1)
    rest = _lerp(y2030, y2035, len(years) - i2030)[1:]
    return first + rest


def project_tesla(scenario: str, overrides: dict[str, Any] | None = None) -> tuple[list[TeslaYear], list[UnitEconomics]]:
    cfg = assumptions()
    years = horizon_years()
    sc = cfg["scenarios"][scenario]
    tesla_sc = dict(sc["tesla"])
    cab_sc = dict(sc["cybercab"])
    seed = cfg["tesla_2026_seed"]
    shared = cfg["cybercab_shared"]

    if overrides:
        tesla_sc.update({k: v for k, v in overrides.items() if k in tesla_sc})
        cab_sc.update({k: v for k, v in overrides.items() if k in cab_sc})

    n = len(years)
    i2030 = years.index(2030)

    retail_to_2030 = _grow(seed["retail_deliveries"], tesla_sc["retail_cagr_to_2030"], i2030 + 1)
    retail_after = [
        retail_to_2030[-1] * ((1 + tesla_sc["retail_cagr_2031_2035"]) ** k)
        for k in range(1, n - i2030)
    ]
    retail = retail_to_2030 + retail_after
    asp = _grow(seed["asp_auto"], tesla_sc["asp_auto_cagr"], n)

    storage_to_2030 = _grow(seed["storage_gwh"], tesla_sc["storage_cagr_to_2030"], i2030 + 1)
    storage_after = [
        storage_to_2030[-1] * ((1 + tesla_sc["storage_cagr_2031_2035"]) ** k)
        for k in range(1, n - i2030)
    ]
    storage = storage_to_2030 + storage_after
    energy_asp = _grow(seed["asp_energy_per_gwh"], tesla_sc["energy_asp_cagr"], n)
    services = _grow(seed["services_ex_robotaxi_b"], tesla_sc["services_cagr"], n)
    fsd = _fsd_path(years, seed["fsd_subs_eoy_m"], tesla_sc["fsd_subs_2030_m"], tesla_sc["fsd_subs_2035_m"])

    cab_rows = project_cybercab(
        years=years,
        production=list(map(float, cab_sc["production"])),
        tesla_owned_share=list(map(float, cab_sc["tesla_owned_share"])),
        utilization=list(map(float, cab_sc["utilization"])),
        price_per_mile=list(map(float, cab_sc["price_per_mile"])),
        cost_per_mile=list(map(float, cab_sc["cost_per_mile"])),
        capex_per_vehicle=float(cab_sc["capex_per_vehicle"]),
        retire_rate=float(cab_sc["retire_rate"]),
        hours_per_day=float(shared["hours_available_per_day"]),
        avg_speed_mph=float(shared["avg_speed_mph"]),
        network_take_rate=float(shared["network_take_rate"]),
        hardware_asp=float(cab_sc["capex_per_vehicle"]) * 1.15,
        legacy_start=float(seed["legacy_robotaxi_fleet_eoy"]),
        legacy_peak=float(cab_sc["legacy_robotaxi_peak"]),
        legacy_peak_year=int(cab_sc["legacy_peak_year"]),
        first_year_commercial_share=float(seed["cybercab_in_commercial_eoy_share_of_production"]),
    )

    out: list[TeslaYear] = []
    for i, year in enumerate(years):
        cab = cab_rows[i]
        auto_b = retail[i] * asp[i] / 1e9 + cab.hardware_revenue_b
        energy_b = storage[i] * energy_asp[i] / 1e9
        optimus_b = tesla_sc["optimus_units"][i] * tesla_sc["optimus_asp"] / 1e9
        robotaxi_b = cab.fleet_revenue_b
        services_b = services[i]
        total = auto_b + energy_b + services_b + robotaxi_b + optimus_b

        gp = (
            auto_b * tesla_sc["auto_gm"][i]
            + energy_b * tesla_sc["energy_gm"][i]
            + services_b * tesla_sc["services_gm"][i]
            + cab.fleet_gross_profit_b
            + optimus_b * tesla_sc["optimus_gm"]
        )
        opex = tesla_sc["opex_to_sales"][i] * total
        oi = gp - opex
        ebitda = oi + tesla_sc["da_and_sbc_b"][i]
        fsd_rev = fsd[i] * tesla_sc["fsd_arpu_month"] * 12 / 1000  # M subs * $/mois * 12 / 1000 = Md$

        out.append(
            TeslaYear(
                year=year,
                retail_deliveries=retail[i],
                asp_auto=asp[i],
                revenue_auto_b=auto_b,
                storage_gwh=storage[i],
                revenue_energy_b=energy_b,
                revenue_services_b=services_b,
                revenue_robotaxi_b=robotaxi_b,
                revenue_cybercab_hw_b=cab.hardware_revenue_b,
                revenue_optimus_b=optimus_b,
                revenue_total_b=total,
                gross_profit_b=gp,
                gross_margin=gp / total if total else 0.0,
                operating_income_b=oi,
                operating_margin=oi / total if total else 0.0,
                adj_ebitda_b=ebitda,
                adj_ebitda_margin=ebitda / total if total else 0.0,
                fsd_subs_m=fsd[i],
                fsd_memo_revenue_b=fsd_rev,
                cybercab_production=cab.production,
                robotaxi_fleet=cab.tesla_owned_fleet_eoy,
                network_fleet=cab.network_fleet_eoy,
                optimus_units=tesla_sc["optimus_units"][i],
                paid_miles_per_cab=cab.paid_miles_per_vehicle,
                price_per_mile=cab.price_per_mile,
                cost_per_mile=cab.cost_per_mile,
                cab_roi=cab.simple_roi,
                cab_payback=cab.payback_years,
                cab_contrib_per_veh=cab.contribution_per_vehicle,
            )
        )
    return out, cab_rows


def project_spacex(scenario: str) -> list[SpaceXYear]:
    cfg = assumptions()
    years = horizon_years()
    sc = cfg["scenarios"][scenario]["spacex"]
    out: list[SpaceXYear] = []
    for i, year in enumerate(years):
        subs = sc["starlink_subs_eoy_m"][i]
        arpu = sc["starlink_arpu_month"][i]
        # Approximation : abonnés EOY × ARPU. Légèrement haut vs moyenne annuelle
        # en forte croissance ; acceptable pour un modèle de jalons.
        conn = subs * arpu * 12 / 1000
        launch = sc["launch_revenue_b"][i]
        ai = sc["ai_revenue_b"][i]
        total = conn + launch + ai
        oi_c = conn * sc["connectivity_oi_margin"][i]
        oi_l = launch * sc["launch_oi_margin"][i]
        oi_a = ai * sc["ai_oi_margin"][i]
        oi = oi_c + oi_l + oi_a
        out.append(
            SpaceXYear(
                year=year,
                starlink_subs_m=subs,
                starlink_arpu_month=arpu,
                revenue_connectivity_b=conn,
                revenue_launch_b=launch,
                revenue_ai_b=ai,
                revenue_total_b=total,
                oi_connectivity_b=oi_c,
                oi_launch_b=oi_l,
                oi_ai_b=oi_a,
                operating_income_b=oi,
                operating_margin=oi / total if total else 0.0,
            )
        )
    return out


def project(scenario: str, overrides: dict[str, Any] | None = None) -> Projection:
    tesla, cab = project_tesla(scenario, overrides)
    spacex = project_spacex(scenario)
    label = assumptions()["scenarios"][scenario]["narrative"].strip()
    return Projection(scenario=scenario, tesla=tesla, spacex=spacex, cybercab=cab, notes=[label])


def history_tesla_frame() -> pd.DataFrame:
    rows = tesla_history()["annual"]
    return pd.DataFrame(rows)


def history_spacex_frame() -> pd.DataFrame:
    rows = spacex_history()["annual"]
    return pd.DataFrame(rows)
