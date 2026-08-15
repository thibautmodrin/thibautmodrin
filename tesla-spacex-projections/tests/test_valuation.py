"""Tests de la couche cours implicite (fondamentaux × multiples)."""

from src.engine import project
from src.kpis import tesla_market_kpis
from src.load import valuation
from src.valuation import (
    blend_ev,
    cagr,
    price_for_market_cap,
    project_valuation,
    shares_outstanding,
    valuation_frames,
)


def test_blend_ev_weights_ebitda_and_sales():
    # 40 % × (10 × 20) + 60 % × (100 × 5) = 80 + 300 = 380
    assert abs(blend_ev(100, 10, 5, 20, 0.4) - 380) < 1e-9


def test_blend_ev_falls_back_to_sales_when_ebitda_non_positive():
    assert blend_ev(100, 0, 12.7, 86, 0.7) == 1270
    assert blend_ev(100, -1, 12.7, 86, 0.7) == 1270
    assert blend_ev(100, 10, 12.7, None, 0.7) == 1270


def test_price_equals_equity_over_shares():
    proj = project("base")
    tesla, spacex = project_valuation(proj.tesla_frame(), proj.spacex_frame(), "base")
    for row in tesla + spacex:
        assert abs(row.price - row.equity_b / row.shares_b) < 1e-9
        assert abs(row.market_cap_t - row.equity_b / 1000) < 1e-9
        assert abs(row.equity_b - (row.ev_b + row.net_cash_b)) < 1e-9


def test_tesla_2026_implied_price_near_spot():
    proj = project("base")
    tesla, _ = project_valuation(proj.tesla_frame(), proj.spacex_frame(), "base")
    y26 = next(r for r in tesla if r.year == 2026)
    # Spot ~340 $ ; EOY 2026 un peu plus bas à cause du FCF négatif.
    assert 150 < y26.price < 600
    spot = valuation()["tesla"]["spot_price"]
    assert abs(y26.price - spot) / spot < 0.25


def test_objectifs_2030_price_above_base_above_conservateur():
    frames = {}
    for name in ("conservateur", "base", "objectifs"):
        proj = project(name)
        tesla, _ = project_valuation(proj.tesla_frame(), proj.spacex_frame(), name)
        frames[name] = next(r for r in tesla if r.year == 2030)
    assert frames["objectifs"].price > frames["base"].price
    assert frames["base"].price > frames["conservateur"].price


def test_two_trillion_milestone_around_500_dollars():
    shares = valuation()["tesla"]["shares_b"]
    price = price_for_market_cap(2.0, shares)
    assert 480 < price < 530


def test_dilution_increases_share_count():
    shares0 = 3.95
    assert abs(shares_outstanding(shares0, 0.008, 2026) - shares0) < 1e-12
    assert shares_outstanding(shares0, 0.008, 2030) > shares0
    assert shares_outstanding(shares0, 0.018, 2030) > shares_outstanding(shares0, 0.008, 2030)


def test_spacex_2026_implied_near_spot():
    proj = project("base")
    _, spacex = project_valuation(proj.tesla_frame(), proj.spacex_frame(), "base")
    y26 = next(r for r in spacex if r.year == 2026)
    spot = valuation()["spacex"]["spot_price"]
    assert 80 < y26.price < 220
    assert abs(y26.price - spot) / spot < 0.20


def test_cagr_and_frames():
    assert abs(cagr(100, 200, 1) - 1.0) < 1e-12
    assert cagr(-1, 10, 4) is None
    proj = project("base")
    tesla_df, spacex_df = valuation_frames(proj.tesla_frame(), proj.spacex_frame(), "base")
    assert list(tesla_df["year"]) == list(range(2026, 2036))
    assert len(spacex_df) == 10


def test_market_cap_kpis_use_spot_as_current():
    proj = project("base")
    tesla_df, _ = valuation_frames(proj.tesla_frame(), proj.spacex_frame(), "base")
    kpis = tesla_market_kpis(tesla_df)
    assert {k.id for k in kpis} == {"mcap_2t", "mcap_8.5t"}
    assert kpis[0].current == valuation()["tesla"]["market_cap_t"]
    assert 0 <= kpis[0].progress <= 1
