"""Synthèse extractive quotidienne : sujets + paroles des voix."""

from __future__ import annotations

import re
from collections import defaultdict

from .models import Cluster, DailyReport, Item, Quote, Voice
from .store import now_iso
from .watchlist import voice_by_id

STOP = {
    "the", "a", "an", "and", "or", "of", "to", "in", "on", "for", "with", "as",
    "is", "are", "be", "by", "at", "from", "that", "this", "its", "it", "after",
    "over", "into", "about", "new", "says", "said", "will", "just", "than",
    "tesla", "spacex", "stock", "shares",
}
HOOKS = {
    "roadster", "robotaxi", "cybercab", "cybertruck", "optimus", "starship",
    "starlink", "gigafactory", "fsd", "supercharger", "megapack", "falcon",
    "starbase", "model", "catch",
}
SAID_RE = re.compile(
    r"(?P<who>[A-Z][\w.'’\-]+(?:\s+[A-Z][\w.'’\-]+){0,3})\s+"
    r"(?:said|says|told|wrote|posted|tweeted|warned|called|announced|explained|"
    r"a déclaré|a dit|a prévenu|a annoncé)\s+"
    r"(?P<body>.+?)(?:[.!?]|$)",
    re.S,
)


def build_report(day: str, items: list[Item], voices: tuple[Voice, ...]) -> DailyReport:
    tesla_items = [i for i in items if i.company in {"tesla", "both"}]
    spacex_items = [i for i in items if i.company in {"spacex", "both"}]
    tesla_clusters = cluster_items(tesla_items, "tesla")
    spacex_clusters = cluster_items(spacex_items, "spacex")
    quotes = extract_quotes(items, voices)
    return DailyReport(
        date=day,
        generated_at=now_iso(),
        tesla_headline=_headline(tesla_clusters, "Tesla : journée calme"),
        tesla_summary=summarize_company("Tesla", tesla_clusters, tesla_items, quotes),
        spacex_headline=_headline(spacex_clusters, "SpaceX : journée calme"),
        spacex_summary=summarize_company("SpaceX", spacex_clusters, spacex_items, quotes),
        quotes=quotes[:20],
        clusters=tesla_clusters[:6] + spacex_clusters[:6],
        item_count=len(items),
        tesla_count=len(tesla_items),
        spacex_count=len(spacex_items),
        voice_count=len({q.voice_id for q in quotes}),
    )


def cluster_items(items: list[Item], company: str, threshold: float = 0.28) -> list[Cluster]:
    remaining = sorted(items, key=lambda i: (-i.weight, i.published_at))
    clusters: list[Cluster] = []
    used: set[str] = set()
    for seed in remaining:
        if seed.id in used:
            continue
        members = [seed]
        used.add(seed.id)
        seed_tokens = tokens(seed.title)
        for other in remaining:
            if other.id in used:
                continue
            if similar_titles(seed_tokens, tokens(other.title), threshold):
                members.append(other)
                used.add(other.id)
        members.sort(key=lambda i: (-i.weight, i.published_at))
        top = members[0]
        sources = list(dict.fromkeys(m.source_name for m in members))
        clusters.append(
            Cluster(
                company=company,
                title=top.title,
                summary=_cluster_blurb(members),
                item_ids=[m.id for m in members],
                sources=sources[:8],
                weight=max(m.weight for m in members) + min(len(members), 8),
            )
        )
    clusters.sort(key=lambda c: (-c.weight, -len(c.item_ids)))
    return clusters


def summarize_company(name: str, clusters: list[Cluster], items: list[Item], quotes: list[Quote]) -> str:
    if not items:
        return f"Aucune information retenue pour {name} ce jour-là."
    lines = [
        f"{name} : {len(items)} éléments retenus, {len(clusters)} sujet(s) distinct(s)."
    ]
    for idx, cluster in enumerate(clusters[:4], start=1):
        n = len(cluster.item_ids)
        src = ", ".join(cluster.sources[:3])
        lines.append(f"{idx}. {cluster.title} ({n} source{'s' if n > 1 else ''} : {src}).")
        if cluster.summary:
            lines.append(f"   {cluster.summary}")
    related = [
        q
        for q in quotes
        if name.lower() in q.role.lower()
        or name.lower() in q.text.lower()
        or (name == "Tesla" and q.category in {"tesla_exec", "investor", "voice"})
        or (name == "SpaceX" and q.category in {"spacex_exec"})
    ]
    if related:
        q = related[0]
        lines.append(f"Parole retenue — {q.name} ({q.role}) : « {q.text} »")
    return "\n".join(lines)


def extract_quotes(items: list[Item], voices: tuple[Voice, ...]) -> list[Quote]:
    by_id = voice_by_id(voices)
    found: list[Quote] = []
    seen: set[str] = set()
    for item in sorted(items, key=lambda i: -i.weight):
        if item.source_kind == "x" and item.voice_id and item.voice_id in by_id:
            voice = by_id[item.voice_id]
            key = f"{voice.id}:{item.text[:80]}"
            if key not in seen:
                seen.add(key)
                found.append(
                    Quote(
                        voice_id=voice.id,
                        name=voice.name,
                        role=voice.role,
                        category=voice.category,
                        text=_clip(item.text),
                        source_name=item.source_name,
                        url=item.url,
                        weight=voice.weight,
                    )
                )
            continue
        blob = f"{item.title}. {item.text}"
        for match in SAID_RE.finditer(blob):
            who = match.group("who").strip()
            body = _clip(match.group("body"))
            voice = _voice_from_who(who, item, voices)
            if voice is None or not body:
                continue
            key = f"{voice.id}:{body[:80]}"
            if key in seen:
                continue
            seen.add(key)
            found.append(
                Quote(
                    voice_id=voice.id,
                    name=voice.name,
                    role=voice.role,
                    category=voice.category,
                    text=body,
                    source_name=item.source_name,
                    url=item.url,
                    weight=voice.weight,
                )
            )
        if item.voice_id and item.voice_id in by_id and item.source_kind == "rss":
            voice = by_id[item.voice_id]
            if voice.category in {"tesla_exec", "spacex_exec", "investor", "official"}:
                key = f"{voice.id}:title:{item.title[:80]}"
                if key not in seen:
                    seen.add(key)
                    found.append(
                        Quote(
                            voice_id=voice.id,
                            name=voice.name,
                            role=voice.role,
                            category=voice.category,
                            text=_clip(item.title),
                            source_name=item.source_name,
                            url=item.url,
                            weight=max(voice.weight - 15, 20),
                        )
                    )
    found.sort(key=lambda q: -q.weight)
    return found


def tokens(text: str) -> set[str]:
    words = re.findall(r"[a-zA-Z0-9]{3,}", (text or "").lower())
    return {w for w in words if w not in STOP}


def jaccard(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    inter = len(a & b)
    union = len(a | b)
    return inter / union if union else 0.0


def similar_titles(a: set[str], b: set[str], threshold: float) -> bool:
    if jaccard(a, b) >= threshold:
        return True
    return bool(a & b & HOOKS)


def _headline(clusters: list[Cluster], fallback: str) -> str:
    if not clusters:
        return fallback
    return clusters[0].title


def _cluster_blurb(members: list[Item]) -> str:
    for member in members:
        text = member.text.strip()
        if len(text) > 80:
            return _clip(text, 280)
    return ""


def _clip(text: str, limit: int = 240) -> str:
    text = re.sub(r"\s+", " ", text).strip().strip("«»\"'")
    if len(text) <= limit:
        return text
    cut = text[:limit].rsplit(" ", 1)[0]
    return cut + "…"


def _voice_from_who(who: str, item: Item, voices: tuple[Voice, ...]) -> Voice | None:
    who_l = who.lower()
    best = None
    for voice in voices:
        aliases = (voice.name, voice.handle, *voice.aliases)
        if any(alias.lower() in who_l or who_l in alias.lower() for alias in aliases if len(alias) >= 4):
            if best is None or voice.weight > best.weight:
                best = voice
    if best:
        return best
    if item.voice_id:
        return next((v for v in voices if v.id == item.voice_id), None)
    return None
