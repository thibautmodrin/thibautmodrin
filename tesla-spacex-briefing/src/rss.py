"""Ingestion RSS (Google News et médias spécialisés)."""

from __future__ import annotations

import hashlib
import re
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from html import unescape
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import feedparser
import yaml

from . import DATA
from .classify import classify_company, is_noise
from .models import Item
from .watchlist import load_voices, match_voice

TAG_RE = re.compile(r"<[^>]+>")
SOURCE_SUFFIX_RE = re.compile(r"\s+[-–—]\s+[^-–—]+$")


def load_sources(path: str | None = None) -> dict:
    return yaml.safe_load(Path(path or DATA / "sources.yaml").read_text(encoding="utf-8"))


def fetch_url(url: str, user_agent: str, timeout: int) -> bytes:
    req = Request(url, headers={"User-Agent": user_agent, "Accept": "application/rss+xml, application/xml, text/xml"})
    with urlopen(req, timeout=timeout) as resp:
        return resp.read()


def parse_feed(raw: bytes | str, source_name: str, hinted: str, voices=None) -> list[Item]:
    parsed = feedparser.parse(raw)
    voices = voices or load_voices()
    items: list[Item] = []
    for entry in parsed.entries:
        title = clean_text(entry.get("title") or "")
        if not title:
            continue
        text = clean_text(entry.get("summary") or entry.get("description") or "")
        if is_noise(title, text):
            continue
        company = classify_company(title, text, hinted=hinted)
        if company is None:
            continue
        url = (entry.get("link") or "").strip()
        published = _published(entry)
        day = published[:10] if published else ""
        if not day:
            continue
        author = clean_text(entry.get("author") or "")
        source = _entry_source(entry) or source_name
        handle = ""
        voice = match_voice(author or source, handle, title, text, voices)
        weight = 12
        if voice:
            weight = max(voice.weight, 40)
        elif source.lower() in {"reuters", "bloomberg", "the information"}:
            weight = 35
        item_id = hashlib.sha256((url or title).encode("utf-8")).hexdigest()[:20]
        items.append(
            Item(
                id=item_id,
                date=day,
                company=company,
                source_kind="rss",
                source_name=source,
                title=SOURCE_SUFFIX_RE.sub("", title).strip() or title,
                text=text[:2000],
                url=url,
                published_at=published,
                author=author or source,
                author_handle=handle,
                voice_id=voice.id if voice else "",
                weight=weight,
            )
        )
    return items


def collect_rss(feeds: list[dict], user_agent: str, timeout: int, voices=None) -> tuple[list[Item], list[str]]:
    voices = voices or load_voices()
    collected: dict[str, Item] = {}
    errors: list[str] = []
    for feed in feeds:
        try:
            raw = fetch_url(feed["url"], user_agent, timeout)
            for item in parse_feed(raw, feed["name"], feed.get("company") or "both", voices):
                prev = collected.get(item.id)
                if prev is None or item.weight > prev.weight:
                    collected[item.id] = item
        except (HTTPError, URLError, TimeoutError, OSError) as exc:
            errors.append(f"{feed['id']}: {exc}")
    return list(collected.values()), errors


def clean_text(value: str) -> str:
    value = unescape(TAG_RE.sub(" ", value or ""))
    return re.sub(r"\s+", " ", value).strip()


def _entry_source(entry: dict) -> str:
    source = entry.get("source")
    if isinstance(source, dict):
        return clean_text(source.get("title") or "")
    if isinstance(source, str):
        return clean_text(source)
    return ""


def _published(entry: dict) -> str:
    for key in ("published", "updated", "created"):
        raw = entry.get(key)
        if not raw:
            continue
        try:
            dt = parsedate_to_datetime(raw)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.astimezone(timezone.utc).replace(microsecond=0).isoformat()
        except (TypeError, ValueError, OverflowError):
            continue
    parsed = entry.get("published_parsed") or entry.get("updated_parsed")
    if parsed:
        dt = datetime(*parsed[:6], tzinfo=timezone.utc)
        return dt.replace(microsecond=0).isoformat()
    return ""
