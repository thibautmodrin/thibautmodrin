"""Modèles du briefing quotidien."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class Voice:
    id: str
    handle: str
    name: str
    aliases: tuple[str, ...]
    role: str
    category: str
    companies: tuple[str, ...]
    weight: int


@dataclass
class Item:
    id: str
    date: str
    company: str
    source_kind: str
    source_name: str
    title: str
    text: str
    url: str
    published_at: str
    author: str = ""
    author_handle: str = ""
    voice_id: str = ""
    weight: int = 10

    def to_row(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Quote:
    voice_id: str
    name: str
    role: str
    category: str
    text: str
    source_name: str
    url: str
    weight: int


@dataclass
class Cluster:
    company: str
    title: str
    summary: str
    item_ids: list[str] = field(default_factory=list)
    sources: list[str] = field(default_factory=list)
    weight: int = 0


@dataclass
class DailyReport:
    date: str
    generated_at: str
    tesla_headline: str
    tesla_summary: str
    spacex_headline: str
    spacex_summary: str
    quotes: list[Quote]
    clusters: list[Cluster]
    item_count: int
    tesla_count: int
    spacex_count: int
    voice_count: int
