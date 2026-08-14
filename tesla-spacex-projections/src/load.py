"""Chargement des YAML de données."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"


def _read(name: str) -> dict[str, Any]:
    path = DATA / name
    with path.open(encoding="utf-8") as handle:
        return yaml.safe_load(handle)


@lru_cache(maxsize=8)
def tesla_history() -> dict[str, Any]:
    return _read("tesla_history.yaml")


@lru_cache(maxsize=8)
def spacex_history() -> dict[str, Any]:
    return _read("spacex_history.yaml")


@lru_cache(maxsize=8)
def assumptions() -> dict[str, Any]:
    return _read("assumptions.yaml")


@lru_cache(maxsize=8)
def goals() -> dict[str, Any]:
    return _read("goals.yaml")


@lru_cache(maxsize=8)
def sources() -> dict[str, Any]:
    return _read("sources.yaml")


@lru_cache(maxsize=8)
def actuals() -> dict[str, Any]:
    return _read("actuals.yaml")


def years() -> list[int]:
    horizon = assumptions()["horizon"]
    return list(range(int(horizon["start_year"]), int(horizon["end_year"]) + 1))
