from src.kpis import spacex_kpis, tesla_kpis
from src.engine import project


def test_kpi_progress_bounded():
    proj = project("base")
    for kpi in tesla_kpis(proj) + spacex_kpis(proj):
        assert 0 <= kpi.progress <= 1
        assert kpi.target > 0


def test_vehicles_cumulative_current_from_q2():
    kpi = next(k for k in tesla_kpis(project("base")) if k.id == "vehicles_cumulative")
    assert kpi.current == 9_700_000
    assert kpi.target == 20_000_000
