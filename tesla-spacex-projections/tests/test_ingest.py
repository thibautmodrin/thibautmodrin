"""Ingestion Tesla Q3 et graine 2026 = YTD + run-rate."""

from pathlib import Path
from unittest.mock import patch

import yaml

from src.engine import project
from src.ingest_tesla import IngestResult, _cybercab_commercial, apply_q3, parse_update_text
from src.load import assumptions, clear_data_cache
from src.rebase import tesla_2026_bridge
from src.tesla_seed import effective_2026_seed

FIXTURE = Path(__file__).parent / "fixtures" / "tesla_q2_2026_update.txt"


def test_parser_reads_q2_fixture_but_refuses_apply():
    result = parse_update_text(FIXTURE.read_text(encoding="utf-8"))
    assert result.status == "parsed"
    assert result.quarter == "Q2-2026"
    assert abs(result.fields["revenue_b"] - 28.236) < 1e-9
    assert int(result.fields["deliveries"]) == 480126
    assert abs(result.fields["storage_gwh"] - 13.5) < 1e-9
    assert abs(result.fields["fcf_b"] - (-1.092)) < 1e-9
    assert abs(result.fields["fsd_subs_m"] - 1.48) < 1e-9
    assert result.can_apply() is False


def test_parser_requires_update_title():
    result = parse_update_text("Total revenues 1 2 3 4 5 6%")
    assert result.status == "error"


def test_cybercab_commercial_from_production_sentence():
    assert _cybercab_commercial("Cybercab began production at Gigafactory Texas") is False
    assert (
        _cybercab_commercial("The Cybercab entered commercial fleet operations in Austin")
        is True
    )


def test_html_response_is_not_published():
    from src.ingest_tesla import fetch_update_pdf

    with patch("src.ingest_tesla._http_get", return_value=(200, "text/html", b"<!DOCTYPE html>Tesla IR")):
        result = fetch_update_pdf("https://example.test/q3.pdf")
    assert result.status == "not_published"


def test_apply_refuses_incomplete_and_wrong_quarter():
    incomplete = IngestResult(
        status="incomplete",
        url="",
        message="manque",
        quarter="Q3-2026",
        fields={"revenue_b": 1.0},
        missing=["deliveries"],
    )
    try:
        apply_q3(incomplete)
        raise AssertionError("should have refused")
    except ValueError:
        pass
    q2 = parse_update_text(FIXTURE.read_text(encoding="utf-8"))
    try:
        apply_q3(q2)
        raise AssertionError("Q2 document must not write Q3")
    except ValueError:
        pass


def test_apply_writes_q3_in_temp_data(tmp_path, monkeypatch):
    import src.ingest_tesla as ingest_mod
    import src.load as load_mod

    dest = tmp_path / "data"
    dest.mkdir()
    src = Path(__file__).resolve().parents[1] / "data"
    for name in ("actuals.yaml", "sources.yaml", "tesla_history.yaml"):
        dest.joinpath(name).write_text(src.joinpath(name).read_text(encoding="utf-8"), encoding="utf-8")
    monkeypatch.setattr(load_mod, "DATA", dest)
    monkeypatch.setattr(ingest_mod, "DATA", dest)
    load_mod.clear_data_cache()

    parsed = parse_update_text(FIXTURE.read_text(encoding="utf-8"))
    parsed.quarter = "Q3-2026"
    parsed.fields["quarter"] = "Q3-2026"
    parsed.status = "parsed"
    parsed.missing = []
    parsed.url = "https://example.test/TSLA-Q3-2026-Update.pdf"
    written = apply_q3(parsed)
    assert "data/actuals.yaml" in written["written"]
    data = yaml.safe_load((dest / "actuals.yaml").read_text(encoding="utf-8"))
    assert data["tesla_2026"]["last_quarter"] == "Q3"
    assert data["tesla_2026"]["next_print"] == "Q4"
    q3 = next(r for r in data["tesla_quarters"] if r["quarter"] == "Q3-2026")
    assert int(q3["deliveries"]) == 480126
    load_mod.clear_data_cache()
    clear_data_cache()


def test_2026_volumes_are_ytd_plus_last_quarter_run_rate():
    live = effective_2026_seed(assumptions()["tesla_2026_seed"])
    assert abs(live["retail_deliveries"] - (838149 + 2 * 480126)) < 1e-6
    assert abs(live["storage_gwh"] - (22.3 + 2 * 13.5)) < 1e-9
    y26 = next(r for r in project("base").tesla if r.year == 2026)
    assert abs(y26.retail_deliveries - live["retail_deliveries"]) < 1e-6


def test_2030_retail_stays_on_original_seed_path():
    y30 = next(r for r in project("base").tesla if r.year == 2030)
    expected = 1_780_000 * (1.06**4)
    assert abs(y30.retail_deliveries - expected) < 1e-6


def test_bridge_ytd_plus_remaining_equals_fy():
    bridge = tesla_2026_bridge(project("base"))
    assert abs(bridge.ytd_revenue_b + bridge.remaining_implied_revenue_b - bridge.fy_revenue_b) < 1e-9
    assert bridge.last_quarter == "Q2"
    assert bridge.remaining_quarters == 2
    assert abs(bridge.h1_revenue_b - 50.623) < 1e-9
