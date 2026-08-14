"""Scan des sources et génération des rapports du calendrier."""

from __future__ import annotations

from collections import defaultdict
from datetime import date

from .models import Item
from .rss import collect_rss, load_sources
from .store import connect, empty, items_for_date, prune, save_report, upsert_items
from .summarize import build_report
from .watchlist import load_voices
from .x_client import fetch_x_posts


def scan(db_path=None, backfill: bool | None = None) -> dict:
    sources = load_sources()
    voices = load_voices()
    conn = connect(db_path)
    do_backfill = empty(conn) if backfill is None else backfill
    feeds = list(sources.get("rss") or [])
    if do_backfill:
        feeds.extend(sources.get("backfill_rss") or [])
    items, errors = collect_rss(
        feeds,
        user_agent=sources.get("user_agent") or "TeslaSpaceXBriefing/1.0",
        timeout=int(sources.get("timeout_seconds") or 20),
        voices=voices,
    )
    x_cfg = sources.get("x") or {}
    if x_cfg.get("enabled", True):
        x_items, x_errors = fetch_x_posts(
            voices,
            extra_query=x_cfg.get("extra_query") or "",
            user_agent=sources.get("user_agent") or "TeslaSpaceXBriefing/1.0",
            timeout=int(sources.get("timeout_seconds") or 20),
            max_results=int(x_cfg.get("max_results") or 50),
        )
        items.extend(x_items)
        errors.extend(x_errors)
    upsert_items(conn, _dedupe(items))
    days = sorted({item.date for item in items})
    reports = 0
    for day in days:
        day_items = items_for_date(conn, day)
        if day_items:
            save_report(conn, build_report(day, day_items, voices))
            reports += 1
    removed = prune(conn, int(sources.get("retention_days") or 30))
    conn.close()
    return {
        "items": len(items),
        "days": days,
        "reports": reports,
        "backfill": do_backfill,
        "pruned": removed,
        "errors": errors,
    }


def rebuild_day(day: str, db_path=None):
    voices = load_voices()
    conn = connect(db_path)
    day_items = items_for_date(conn, day)
    if not day_items:
        conn.close()
        return None
    report = build_report(day, day_items, voices)
    save_report(conn, report)
    conn.close()
    return report


def today() -> str:
    return date.today().isoformat()


def _dedupe(items: list[Item]) -> list[Item]:
    by_id: dict[str, Item] = {}
    for item in items:
        prev = by_id.get(item.id)
        if prev is None or item.weight > prev.weight:
            by_id[item.id] = item
    # Titres quasi identiques le même jour : garder le plus lourd.
    groups: dict[tuple[str, str], list[Item]] = defaultdict(list)
    for item in by_id.values():
        key = (item.date, _norm_title(item.title))
        groups[key].append(item)
    kept: list[Item] = []
    for group in groups.values():
        group.sort(key=lambda i: (-i.weight, i.source_kind != "x"))
        kept.append(group[0])
    return kept


def _norm_title(title: str) -> str:
    tokens = [t for t in "".join(ch.lower() if ch.isalnum() else " " for ch in title).split() if len(t) > 2]
    return " ".join(tokens[:12])
