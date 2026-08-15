"""Tests étape 2 : délai commercial, cash, Optimus, Starship, MC, recalage."""

from src.cash import project_cash
from src.cybercab import paid_miles_per_vehicle
from src.engine import project
from src.montecarlo import delay_sensitivity, simulate
from src.optimus import project_optimus
from src.overrides import scale_to_anchor
from src.rebase import tesla_2026_bridge
from src.starship import project_launch


def test_base_commercial_start_is_2027():
    proj = project("base")
    y26 = next(r for r in proj.tesla if r.year == 2026)
    y27 = next(r for r in proj.tesla if r.year == 2027)
    # 2026 : Cybercab produit mais pas encore déployé (hors legacy Model Y).
    assert y26.cybercab_production > 0
    assert y26.revenue_robotaxi_b < 0.5
    assert y27.robotaxi_fleet > y26.robotaxi_fleet


def test_delay_reduces_near_term_robotaxi_not_2030_catchup():
    rows = delay_sensitivity("base")
    by_year = {r["start_year"]: r for r in rows}
    assert by_year[2026]["robotaxi_2027"] > by_year[2029]["robotaxi_2027"]
    # En 2030 le backlog a été déployé : l'écart se resserre.
    ratio = by_year[2029]["robotaxi_2030"] / by_year[2026]["robotaxi_2030"]
    assert ratio > 0.5


def test_2026_capex_respects_guidance_floor():
    for name in ("conservateur", "base", "objectifs"):
        row = next(r for r in project(name).tesla if r.year == 2026)
        assert row.capex_total_b >= 25.0 - 1e-9
        assert row.fcf_b < 0


def test_optimus_internal_is_not_gaap_revenue():
    proj = project("base")
    y26 = next(r for r in proj.tesla if r.year == 2026)
    assert y26.optimus_internal == y26.optimus_units
    assert y26.revenue_optimus_b == 0
    y30 = next(r for r in proj.tesla if r.year == 2030)
    assert y30.revenue_optimus_b > 0
    assert y30.optimus_savings_b > 0


def test_optimus_hours_formula():
    rows = project_optimus(
        years=[2026],
        produced=[1000],
        internal_share=[1.0],
        asp=20000,
        gross_margin=0.2,
        capex_per_unit=20000,
        utilization=[0.5],
        hours_per_day=16,
        wage_per_hour=30,
        opex_per_hour=10,
    )
    assert abs(rows[0].hours_per_internal - 0.5 * 16 * 365) < 1e-6
    assert abs(rows[0].savings_per_internal - 2920 * 20) < 1e-6
    assert rows[0].revenue_gaap_b == 0


def test_starship_internal_flights_are_not_revenue():
    rows = project_launch(
        years=[2026],
        falcon_external=[40],
        falcon_price_m=67,
        launch_other_b=[1.5],
        starship_flights=[20],
        starship_external_share=[0.0],
        starship_price_m=[100],
        starship_cost_m=[90],
    )
    assert rows[0].revenue_starship_b == 0
    assert abs(rows[0].revenue_falcon_b - 2.68) < 1e-9
    assert abs(rows[0].revenue_launch_b - 4.18) < 1e-9


def test_cash_identity():
    rows = project_cash(
        years=[2026, 2027],
        adj_ebitda_b=[10.0, 20.0],
        capex_core_b=[20.0, 10.0],
        fleet_units_produced_owned=[0.0, 0.0],
        capex_per_vehicle=22000,
        optimus_internal_capex_b=[0.0, 0.0],
        ocf_conversion=0.9,
        cash_start_b=40.0,
        capex_2026_floor_b=25.0,
    )
    assert rows[0].capex_total_b == 25.0
    assert abs(rows[0].ocf_b - 9.0) < 1e-9
    assert abs(rows[0].fcf_b - (9.0 - 25.0)) < 1e-9
    assert abs(rows[0].cash_eoy_b - (40.0 - 16.0)) < 1e-9
    assert rows[1].capex_total_b == 10.0


def test_scale_to_anchor():
    out = scale_to_anchor([1.0, 2.0, 4.0], 8.0, 2)
    assert out == [2.0, 4.0, 8.0]


def test_rebase_h2_is_implied_not_invented():
    bridge = tesla_2026_bridge(project("base"))
    assert abs(bridge.h1_revenue_b + bridge.h2_implied_revenue_b - bridge.fy_revenue_b) < 1e-9
    assert bridge.h1_revenue_b == 50.623
    assert bridge.last_quarter == "Q2"


def test_montecarlo_reproducible_and_ordered():
    a = simulate("base", n=40, seed=7)
    b = simulate("base", n=40, seed=7)
    assert a.p50["tesla_ca_2030"] == b.p50["tesla_ca_2030"]
    assert a.p10["robotaxi_ca_2030"] <= a.p50["robotaxi_ca_2030"] <= a.p90["robotaxi_ca_2030"]
    assert sum(a.start_year_counts.values()) == 40


def test_paid_miles_still_holds():
    assert abs(paid_miles_per_vehicle(0.40, 16, 18) - 42048) < 1e-6
