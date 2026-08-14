"""Stockage SQLite des items et des rapports quotidiens."""

from __future__ import annotations

import json
import sqlite3
from datetime import date, datetime, timedelta
from pathlib import Path

from . import DATA
from .models import Cluster, DailyReport, Item, Quote

SCHEMA = """
CREATE TABLE IF NOT EXISTS items (
    id TEXT PRIMARY KEY,
    date TEXT NOT NULL,
    company TEXT NOT NULL,
    source_kind TEXT NOT NULL,
    source_name TEXT NOT NULL,
    title TEXT NOT NULL,
    text TEXT,
    url TEXT,
    published_at TEXT,
    author TEXT,
    author_handle TEXT,
    voice_id TEXT,
    weight INTEGER DEFAULT 10
);
CREATE INDEX IF NOT EXISTS idx_items_date ON items(date);
CREATE INDEX IF NOT EXISTS idx_items_company ON items(company);

CREATE TABLE IF NOT EXISTS reports (
    date TEXT PRIMARY KEY,
    generated_at TEXT NOT NULL,
    tesla_headline TEXT,
    tesla_summary TEXT,
    spacex_headline TEXT,
    spacex_summary TEXT,
    quotes_json TEXT,
    clusters_json TEXT,
    item_count INTEGER,
    tesla_count INTEGER,
    spacex_count INTEGER,
    voice_count INTEGER
);
"""


def connect(db_path: Path | None = None) -> sqlite3.Connection:
    path = Path(db_path or DATA / "briefing.db")
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    return conn


def upsert_items(conn: sqlite3.Connection, items: list[Item]) -> int:
    if not items:
        return 0
    rows = [
        (
            i.id,
            i.date,
            i.company,
            i.source_kind,
            i.source_name,
            i.title,
            i.text,
            i.url,
            i.published_at,
            i.author,
            i.author_handle,
            i.voice_id,
            i.weight,
        )
        for i in items
    ]
    conn.executemany(
        """
        INSERT INTO items (
            id, date, company, source_kind, source_name, title, text, url,
            published_at, author, author_handle, voice_id, weight
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            date=excluded.date,
            company=excluded.company,
            source_kind=excluded.source_kind,
            source_name=excluded.source_name,
            title=excluded.title,
            text=excluded.text,
            url=excluded.url,
            published_at=excluded.published_at,
            author=excluded.author,
            author_handle=excluded.author_handle,
            voice_id=excluded.voice_id,
            weight=excluded.weight
        """,
        rows,
    )
    conn.commit()
    return len(rows)


def items_for_date(conn: sqlite3.Connection, day: str) -> list[Item]:
    rows = conn.execute("SELECT * FROM items WHERE date = ? ORDER BY weight DESC, published_at DESC", (day,)).fetchall()
    return [_item(row) for row in rows]


def report_dates(conn: sqlite3.Connection) -> list[str]:
    rows = conn.execute("SELECT date FROM reports ORDER BY date").fetchall()
    return [r["date"] for r in rows]


def save_report(conn: sqlite3.Connection, report: DailyReport) -> None:
    conn.execute(
        """
        INSERT INTO reports (
            date, generated_at, tesla_headline, tesla_summary,
            spacex_headline, spacex_summary, quotes_json, clusters_json,
            item_count, tesla_count, spacex_count, voice_count
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(date) DO UPDATE SET
            generated_at=excluded.generated_at,
            tesla_headline=excluded.tesla_headline,
            tesla_summary=excluded.tesla_summary,
            spacex_headline=excluded.spacex_headline,
            spacex_summary=excluded.spacex_summary,
            quotes_json=excluded.quotes_json,
            clusters_json=excluded.clusters_json,
            item_count=excluded.item_count,
            tesla_count=excluded.tesla_count,
            spacex_count=excluded.spacex_count,
            voice_count=excluded.voice_count
        """,
        (
            report.date,
            report.generated_at,
            report.tesla_headline,
            report.tesla_summary,
            report.spacex_headline,
            report.spacex_summary,
            json.dumps([q.__dict__ for q in report.quotes], ensure_ascii=False),
            json.dumps([c.__dict__ for c in report.clusters], ensure_ascii=False),
            report.item_count,
            report.tesla_count,
            report.spacex_count,
            report.voice_count,
        ),
    )
    conn.commit()


def get_report(conn: sqlite3.Connection, day: str) -> DailyReport | None:
    row = conn.execute("SELECT * FROM reports WHERE date = ?", (day,)).fetchone()
    if row is None:
        return None
    quotes = [Quote(**q) for q in json.loads(row["quotes_json"] or "[]")]
    clusters = [Cluster(**c) for c in json.loads(row["clusters_json"] or "[]")]
    return DailyReport(
        date=row["date"],
        generated_at=row["generated_at"],
        tesla_headline=row["tesla_headline"] or "",
        tesla_summary=row["tesla_summary"] or "",
        spacex_headline=row["spacex_headline"] or "",
        spacex_summary=row["spacex_summary"] or "",
        quotes=quotes,
        clusters=clusters,
        item_count=int(row["item_count"] or 0),
        tesla_count=int(row["tesla_count"] or 0),
        spacex_count=int(row["spacex_count"] or 0),
        voice_count=int(row["voice_count"] or 0),
    )


def prune(conn: sqlite3.Connection, retention_days: int, today: date | None = None) -> int:
    cutoff = ((today or date.today()) - timedelta(days=retention_days)).isoformat()
    cur = conn.execute("DELETE FROM items WHERE date < ?", (cutoff,))
    conn.execute("DELETE FROM reports WHERE date < ?", (cutoff,))
    conn.commit()
    return cur.rowcount


def empty(conn: sqlite3.Connection) -> bool:
    row = conn.execute("SELECT COUNT(*) AS n FROM items").fetchone()
    return int(row["n"]) == 0


def _item(row: sqlite3.Row) -> Item:
    return Item(
        id=row["id"],
        date=row["date"],
        company=row["company"],
        source_kind=row["source_kind"],
        source_name=row["source_name"],
        title=row["title"],
        text=row["text"] or "",
        url=row["url"] or "",
        published_at=row["published_at"] or "",
        author=row["author"] or "",
        author_handle=row["author_handle"] or "",
        voice_id=row["voice_id"] or "",
        weight=int(row["weight"] or 10),
    )


def now_iso() -> str:
    return datetime.now().replace(microsecond=0).isoformat()
