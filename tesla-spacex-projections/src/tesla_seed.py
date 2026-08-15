"""Graine Tesla 2026 = faits YTD + run-rate du dernier trimestre publié.

Les années 2027-2035 restent calées sur la graine d'assumptions.yaml :
un trimestre 2026 ne réécrit pas la S-curve 2030.
On n'invente pas un trimestre absent.
"""

from __future__ import annotations

from typing import Any

from src.load import actuals, tesla_history

QUARTER_INDEX = {"Q1": 1, "Q2": 2, "Q3": 3, "Q4": 4}
REMAINING_LABEL = {0: "FY clos", 1: "Q4", 2: "H2", 3: "Q2-Q4"}


def parse_quarter_label(label: str) -> tuple[str, int]:
    qtr, year_s = label.split("-")
    return qtr, int(year_s)


def quarters_for_year(year: int = 2026, rows: list[dict] | None = None) -> list[dict]:
    rows = rows if rows is not None else list(actuals()["tesla_quarters"])
    out = []
    for row in rows:
        qtr, yr = parse_quarter_label(str(row["quarter"]))
        if yr == year:
            out.append({**row, "_q": qtr, "_n": QUARTER_INDEX[qtr]})
    return sorted(out, key=lambda r: r["_n"])


def last_published_2026(rows: list[dict] | None = None) -> dict | None:
    published = quarters_for_year(2026, rows)
    return published[-1] if published else None


def ytd_totals(year: int = 2026, rows: list[dict] | None = None) -> dict[str, float]:
    published = quarters_for_year(year, rows)
    keys = (
        "revenue_b",
        "revenue_auto_b",
        "revenue_energy_b",
        "revenue_services_b",
        "deliveries",
        "storage_gwh",
        "ocf_b",
        "capex_b",
        "fcf_b",
    )
    tot = {k: 0.0 for k in keys}
    tot["n"] = float(len(published))
    for row in published:
        for k in keys:
            if k in row and row[k] is not None:
                tot[k] += float(row[k])
    return tot


def remaining_quarters(year: int = 2026, rows: list[dict] | None = None) -> int:
    return max(4 - int(ytd_totals(year, rows)["n"]), 0)


def remaining_label(n_remaining: int) -> str:
    return REMAINING_LABEL.get(n_remaining, f"{n_remaining} trimestres")


def _run_rate(last: dict, key: str) -> float | None:
    if key not in last or last[key] is None:
        return None
    return float(last[key])


def effective_2026_seed(seed: dict[str, Any], rows: list[dict] | None = None) -> dict[str, Any]:
    """FY 2026 volumes used by the engine: YTD + last-quarter × remaining.

    Fields we cannot observe quarterly stay on the original seed.
    """
    published = quarters_for_year(2026, rows)
    out = dict(seed)
    if not published:
        out["rebase_note"] = "aucun trimestre 2026 : graine brute"
        return out
    last = published[-1]
    n_rem = remaining_quarters(2026, rows)
    ytd = ytd_totals(2026, rows)

    deliveries_rr = _run_rate(last, "deliveries")
    if deliveries_rr is not None:
        out["retail_deliveries"] = ytd["deliveries"] + deliveries_rr * n_rem

    storage_rr = _run_rate(last, "storage_gwh")
    if storage_rr is not None:
        out["storage_gwh"] = ytd["storage_gwh"] + storage_rr * n_rem

    if all(r.get("revenue_services_b") is not None for r in published):
        services_rr = _run_rate(last, "revenue_services_b")
        if services_rr is not None:
            out["services_ex_robotaxi_b"] = ytd["revenue_services_b"] + services_rr * n_rem

    fy_del = float(out["retail_deliveries"])
    if fy_del > 0 and all(r.get("revenue_auto_b") is not None for r in published):
        auto_rr = _run_rate(last, "revenue_auto_b")
        if auto_rr is not None:
            fy_auto_b = ytd["revenue_auto_b"] + auto_rr * n_rem
            out["asp_auto"] = fy_auto_b * 1e9 / fy_del

    fsd = last.get("fsd_subs_m")
    if fsd is not None:
        # Point observé : on ne invente pas la croissance du trimestre restant.
        out["fsd_subs_eoy_m"] = float(fsd)

    out["rebase_note"] = (
        f"YTD {last['quarter']} + {n_rem}× run-rate {last['quarter']} "
        f"({remaining_label(n_rem)})"
    )
    return out


def tesla_live_snapshot() -> dict[str, Any]:
    """Snapshot KPI : faits YTD (actuals) + contexte qualitatif (history)."""
    snap = dict(tesla_history()["snapshot_latest"])
    ytd = ytd_totals()
    last = last_published_2026()
    if ytd["n"]:
        snap["ytd_deliveries"] = ytd["deliveries"]
        snap["ytd_revenue"] = ytd["revenue_b"]
        snap["ytd_storage_gwh"] = ytd["storage_gwh"]
        snap["h1_deliveries"] = snap.get("h1_deliveries", ytd["deliveries"])
    if last:
        snap["quarter_revenue"] = float(last["revenue_b"])
        if last.get("fsd_subs_m") is not None:
            snap["fsd_subs_m"] = float(last["fsd_subs_m"])
        if last.get("cumulative_deliveries_m") is not None:
            snap["cumulative_deliveries_m"] = float(last["cumulative_deliveries_m"])
        snap["label"] = f"{last['quarter']} (dernier trimestre publié)"
    return snap
