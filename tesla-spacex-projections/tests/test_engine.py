"""Tests du moteur : formules Cybercab et cohérence des totaux."""

from src.cybercab import paid_miles_per_vehicle, payback_years, simple_roi
from src.engine import project
from src.load import assumptions, years


def test_paid_miles_formula():
    # 40 % × 16 h × 365 × 18 mph = 42 048
    assert abs(paid_miles_per_vehicle(0.40, 16, 18) - 42048) < 1e-6


def test_roi_and_payback():
    assert simple_roi(11000, 22000) == 0.5
    assert payback_years(11000, 22000) == 2
    assert payback_years(-1, 22000) is None


def test_base_scenario_has_ten_years():
    proj = project("base")
    assert [row.year for row in proj.tesla] == years()
    assert len(proj.spacex) == 10
    assert len(proj.cybercab) == 10


def test_tesla_revenue_is_sum_of_segments():
    for name in assumptions()["scenarios"]:
        proj = project(name)
        for row in proj.tesla:
            total = (
                row.revenue_auto_b
                + row.revenue_energy_b
                + row.revenue_services_b
                + row.revenue_robotaxi_b
                + row.revenue_optimus_b
            )
            assert abs(total - row.revenue_total_b) < 1e-9
            assert row.revenue_total_b > 0
            assert 0 <= row.gross_margin <= 0.85


def test_spacex_revenue_is_sum_of_segments():
    proj = project("base")
    for row in proj.spacex:
        total = row.revenue_connectivity_b + row.revenue_launch_b + row.revenue_ai_b
        assert abs(total - row.revenue_total_b) < 1e-9


def test_objectifs_above_base_in_2030():
    base = {r.year: r for r in project("base").tesla}
    obj = {r.year: r for r in project("objectifs").tesla}
    cons = {r.year: r for r in project("conservateur").tesla}
    assert obj[2030].revenue_total_b > base[2030].revenue_total_b
    assert base[2030].revenue_total_b > cons[2030].revenue_total_b
    assert obj[2030].robotaxi_fleet > base[2030].robotaxi_fleet


def test_2026_robotaxi_not_material_in_base():
    row = next(r for r in project("base").tesla if r.year == 2026)
    assert row.revenue_robotaxi_b < 1.0
    assert row.revenue_robotaxi_b / row.revenue_total_b < 0.02


def test_street_order_of_magnitude_robotaxi_2030_base():
    row = next(r for r in project("base").tesla if r.year == 2030)
    # Consensus Street ~42 Md$ ; on accepte une bande large 15-80 Md$.
    assert 15 < row.revenue_robotaxi_b < 80


def test_2026_anchored_to_published_run_rate():
    tesla = next(r for r in project("base").tesla if r.year == 2026)
    spacex = next(r for r in project("base").spacex if r.year == 2026)
    assert 95 < tesla.revenue_total_b < 120
    assert 25 < spacex.revenue_total_b < 45


def test_cybercab_cost_target_only_in_objectifs():
    obj = next(c for c in project("objectifs").cybercab if c.year == 2030)
    base = next(c for c in project("base").cybercab if c.year == 2030)
    assert obj.cost_per_mile <= 0.20
    assert base.cost_per_mile > 0.20
