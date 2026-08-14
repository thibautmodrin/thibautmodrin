"""Déformation de S-curves sans réécrire l'historique."""

from __future__ import annotations


def scale_to_anchor(
    series: list[float],
    new_anchor: float,
    anchor_idx: int,
    floor: float | None = None,
    cap: float | None = None,
) -> list[float]:
    base = series[anchor_idx]
    factor = new_anchor / base if base else 1.0
    out = [v * factor for v in series]
    if floor is not None:
        out = [max(v, floor) for v in out]
    if cap is not None:
        out = [min(v, cap) for v in out]
    return out
