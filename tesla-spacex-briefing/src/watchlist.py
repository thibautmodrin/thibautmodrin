"""Watchlist des voix qui ont du poids."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import yaml

from . import DATA
from .models import Voice


@lru_cache(maxsize=4)
def load_voices(path: str | None = None) -> tuple[Voice, ...]:
    raw = yaml.safe_load(Path(path or DATA / "watchlist.yaml").read_text(encoding="utf-8"))
    voices = []
    for row in raw["voices"]:
        voices.append(
            Voice(
                id=row["id"],
                handle=row["handle"].lstrip("@"),
                name=row["name"],
                aliases=tuple(row.get("aliases") or []),
                role=row["role"],
                category=row["category"],
                companies=tuple(row.get("companies") or []),
                weight=int(row["weight"]),
            )
        )
    return tuple(sorted(voices, key=lambda v: (-v.weight, v.name)))


def voice_by_id(voices: tuple[Voice, ...] | None = None) -> dict[str, Voice]:
    return {v.id: v for v in (voices or load_voices())}


GENERIC_ALIASES = {"tesla", "spacex", "tesla inc", "tesla, inc.", "space exploration technologies"}


def match_voice(author: str, handle: str, title: str, text: str, voices: tuple[Voice, ...] | None = None) -> Voice | None:
    """Associe un item à la voix la plus lourde citée ou auteur."""
    voices = voices or load_voices()
    blob = " ".join(part for part in (author, handle, title, text) if part).lower()
    handle_l = (handle or "").lstrip("@").lower()
    author_l = (author or "").lower()

    best: Voice | None = None
    for voice in voices:
        hit = False
        if handle_l and voice.handle.lower() == handle_l:
            hit = True
        elif author_l and (voice.name.lower() in author_l or voice.handle.lower() in author_l):
            hit = True
        elif voice.category in {"official", "journalist"}:
            continue
        else:
            for alias in (voice.name, *voice.aliases, voice.handle):
                token = alias.lower()
                if len(token) < 4 or token in GENERIC_ALIASES:
                    continue
                if token in blob:
                    hit = True
                    break
        if hit and (best is None or voice.weight > best.weight):
            best = voice
    return best
