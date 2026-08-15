"""Chargement des YAML de données.

Le cache est invalidé si le fichier change (mtime + taille), pour que
l'ingestion Q3 soit visible sans redémarrer le process.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"


def _stat_key(name: str) -> tuple[int, int]:
    path = DATA / name
    st = path.stat()
    return (st.st_mtime_ns, st.st_size)


@lru_cache(maxsize=32)
def _read_cached(name: str, mtime_ns: int, size: int) -> dict[str, Any]:
    path = DATA / name
    with path.open(encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def _read(name: str) -> dict[str, Any]:
    mtime_ns, size = _stat_key(name)
    return _read_cached(name, mtime_ns, size)


def data_fingerprint() -> str:
    parts = []
    for path in sorted(DATA.glob("*.yaml")):
        st = path.stat()
        parts.append(f"{path.name}:{st.st_mtime_ns}:{st.st_size}")
    return "|".join(parts)


def clear_data_cache() -> None:
    _read_cached.cache_clear()


def tesla_history() -> dict[str, Any]:
    return _read("tesla_history.yaml")


def spacex_history() -> dict[str, Any]:
    return _read("spacex_history.yaml")


def assumptions() -> dict[str, Any]:
    return _read("assumptions.yaml")


def goals() -> dict[str, Any]:
    return _read("goals.yaml")


def sources() -> dict[str, Any]:
    return _read("sources.yaml")


def actuals() -> dict[str, Any]:
    return _read("actuals.yaml")


def valuation() -> dict[str, Any]:
    return _read("valuation.yaml")


def years() -> list[int]:
    horizon = assumptions()["horizon"]
    return list(range(int(horizon["start_year"]), int(horizon["end_year"]) + 1))
