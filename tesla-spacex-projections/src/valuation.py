"""Cours implicite Tesla / SpaceX.

Le prix n'est pas un CAGR. Formule :

    EV = w × (EBITDA × EV/EBITDA) + (1 − w) × (CA × EV/S)
    si EBITDA ≤ 0 → 100 % EV/S
    equity = EV + cash net
    prix = equity / actions
    actions_t = actions_0 × (1 + dilution)^(t − 2026)

Les multiples et la dilution sont des hypothèses de scénario.
Ce n'est pas un conseil en investissement.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd

from src.load import goals, valuation as load_valuation


@dataclass
class ValuationYear:
    year: int
    revenue_b: float
    ebitda_b: float
    cash_eoy_b: float
    net_cash_b: float
    ev_s: float
    ev_ebitda: float | None
    w_ebitda: float
    ev_b: float
    equity_b: float
    shares_b: float
    price: float
    market_cap_t: float
    implied_ev_s: float
    implied_ev_ebitda: float | None


def lerp_knots(years: list[int], knots: dict[int, float]) -> list[float]:
    keyed = {int(k): float(v) for k, v in knots.items()}
    keys = sorted(keyed)
    if not keys:
        raise ValueError("knots must not be empty")
    out: list[float] = []
    for year in years:
        if year <= keys[0]:
            out.append(keyed[keys[0]])
            continue
        if year >= keys[-1]:
            out.append(keyed[keys[-1]])
            continue
        for left, right in zip(keys, keys[1:]):
            if left <= year <= right:
                span = right - left
                t = 0.0 if span == 0 else (year - left) / span
                out.append(keyed[left] + t * (keyed[right] - keyed[left]))
                break
    return out


def blend_ev(
    revenue_b: float,
    ebitda_b: float,
    ev_s: float,
    ev_ebitda: float | None,
    w_ebitda: float,
) -> float:
    sales_ev = revenue_b * ev_s
    if ebitda_b <= 0 or ev_ebitda is None:
        return sales_ev
    weight = min(max(w_ebitda, 0.0), 1.0)
    return weight * (ebitda_b * ev_ebitda) + (1.0 - weight) * sales_ev


def shares_outstanding(shares0_b: float, dilution: float, year: int, start_year: int = 2026) -> float:
    return shares0_b * ((1.0 + dilution) ** (year - start_year))


def price_for_market_cap(target_t: float, shares_b: float) -> float:
    if shares_b <= 0:
        raise ValueError("shares_b must be > 0")
    return target_t * 1000.0 / shares_b


def cagr(start: float, end: float, periods: float) -> float | None:
    if start <= 0 or end <= 0 or periods <= 0:
        return None
    return (end / start) ** (1.0 / periods) - 1.0


def _company_path(
    years: list[int],
    revenue_b: list[float],
    ebitda_b: list[float],
    cash_eoy_b: list[float],
    net_cash_b: list[float],
    ev_s: list[float],
    ev_ebitda: list[float] | None,
    w_ebitda: list[float],
    shares0_b: float,
    dilution: float,
) -> list[ValuationYear]:
    rows: list[ValuationYear] = []
    for i, year in enumerate(years):
        ebitda = ebitda_b[i]
        multiple_eb = None if ev_ebitda is None else ev_ebitda[i]
        ev = blend_ev(revenue_b[i], ebitda, ev_s[i], multiple_eb, w_ebitda[i])
        equity = ev + net_cash_b[i]
        shares = shares_outstanding(shares0_b, dilution, year)
        price = equity / shares if shares else 0.0
        implied_eb = (ev / ebitda) if ebitda > 0 else None
        rows.append(
            ValuationYear(
                year=year,
                revenue_b=revenue_b[i],
                ebitda_b=ebitda,
                cash_eoy_b=cash_eoy_b[i],
                net_cash_b=net_cash_b[i],
                ev_s=ev_s[i],
                ev_ebitda=multiple_eb,
                w_ebitda=w_ebitda[i] if ebitda > 0 else 0.0,
                ev_b=ev,
                equity_b=equity,
                shares_b=shares,
                price=price,
                market_cap_t=equity / 1000.0,
                implied_ev_s=ev / revenue_b[i] if revenue_b[i] else 0.0,
                implied_ev_ebitda=implied_eb,
            )
        )
    return rows


def project_valuation(
    tesla_df: pd.DataFrame,
    spacex_df: pd.DataFrame,
    scenario: str,
    tesla_ev_ebitda_path: list[float] | None = None,
    tesla_ev_s_path: list[float] | None = None,
    spacex_ev_s_path: list[float] | None = None,
    cfg: dict[str, Any] | None = None,
) -> tuple[list[ValuationYear], list[ValuationYear]]:
    cfg = cfg or load_valuation()
    years = [int(y) for y in tesla_df["year"].tolist()]
    tesla_cfg = cfg["tesla"]
    tesla_sc = tesla_cfg["scenarios"][scenario]
    w_path = lerp_knots(years, cfg["w_ebitda_knots"])
    tesla_ev_s = tesla_ev_s_path or list(map(float, tesla_sc["ev_s"]))
    tesla_ev_eb = tesla_ev_ebitda_path or list(map(float, tesla_sc["ev_ebitda"]))
    cash = tesla_df["cash_eoy_b"].tolist()
    debt = float(tesla_cfg["gross_debt_b"])
    tesla_rows = _company_path(
        years=years,
        revenue_b=tesla_df["revenue_total_b"].tolist(),
        ebitda_b=tesla_df["adj_ebitda_b"].tolist(),
        cash_eoy_b=cash,
        net_cash_b=[c - debt for c in cash],
        ev_s=tesla_ev_s,
        ev_ebitda=tesla_ev_eb,
        w_ebitda=w_path,
        shares0_b=float(tesla_cfg["shares_b"]),
        dilution=float(tesla_sc["dilution"]),
    )

    sx_cfg = cfg["spacex"]
    sx_sc = sx_cfg["scenarios"][scenario]
    sx_years = [int(y) for y in spacex_df["year"].tolist()]
    sx_cash = [float(sx_cfg["net_cash_b"])] * len(sx_years)
    sx_w = [float(sx_cfg.get("w_ebitda", 0.0))] * len(sx_years)
    spacex_rows = _company_path(
        years=sx_years,
        revenue_b=spacex_df["revenue_total_b"].tolist(),
        ebitda_b=spacex_df["operating_income_b"].tolist(),
        cash_eoy_b=sx_cash,
        net_cash_b=sx_cash,
        ev_s=spacex_ev_s_path or list(map(float, sx_sc["ev_s"])),
        ev_ebitda=None,
        w_ebitda=sx_w,
        shares0_b=float(sx_cfg["shares_b"]),
        dilution=float(sx_sc["dilution"]),
    )
    return tesla_rows, spacex_rows


def valuation_frames(
    tesla_df: pd.DataFrame,
    spacex_df: pd.DataFrame,
    scenario: str,
    **overrides,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    tesla_rows, spacex_rows = project_valuation(tesla_df, spacex_df, scenario, **overrides)
    return (
        pd.DataFrame([r.__dict__ for r in tesla_rows]),
        pd.DataFrame([s.__dict__ for s in spacex_rows]),
    )


def tesla_award_prices(shares_b: float) -> list[tuple[float, float]]:
    """Prix par action correspondant aux jalons de capitalisation du CEO award."""
    targets = [float(t) for t in goals()["tesla_ceo_award_2025"]["market_cap_t"]]
    return [(target, price_for_market_cap(target, shares_b)) for target in targets]
