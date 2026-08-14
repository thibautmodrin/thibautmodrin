"""Collecte optionnelle des posts X (API v2 recent search).

Sans jeton Bearer, le briefing s'appuie sur les flux RSS et les citations
dans la presse. Jeton : variable d'environnement, `.streamlit/secrets.toml`,
ou le champ de la barre latérale Streamlit.
"""

from __future__ import annotations

import hashlib
import json
import os
import tomllib
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from .classify import classify_company
from .models import Item, Voice
from .watchlist import match_voice

API = "https://api.x.com/2/tweets/search/recent"
SECRETS_PATH = Path(__file__).resolve().parent.parent / ".streamlit" / "secrets.toml"


def bearer_token(path: Path | None = None) -> str:
    for key in ("X_BEARER_TOKEN", "TWITTER_BEARER_TOKEN"):
        value = (os.environ.get(key) or "").strip()
        if value:
            return value
    data = _read_secrets(path or SECRETS_PATH)
    return str(data.get("X_BEARER_TOKEN") or data.get("TWITTER_BEARER_TOKEN") or "").strip()


def token_is_set(path: Path | None = None) -> bool:
    return bool(bearer_token(path))


def save_bearer_token(token: str, path: Path | None = None) -> Path:
    dest = Path(path or SECRETS_PATH)
    dest.parent.mkdir(parents=True, exist_ok=True)
    data = _read_secrets(dest)
    token = (token or "").strip()
    if token:
        data["X_BEARER_TOKEN"] = token
    else:
        data.pop("X_BEARER_TOKEN", None)
        data.pop("TWITTER_BEARER_TOKEN", None)
    dest.write_text(_dump_secrets(data), encoding="utf-8")
    os.chmod(dest, 0o600)
    return dest


def _read_secrets(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return dict(tomllib.loads(path.read_text(encoding="utf-8")))
    except (OSError, tomllib.TOMLDecodeError):
        return {}


def _dump_secrets(data: dict) -> str:
    lines = ["# Hors git. Developer Portal X → projet → Keys and tokens → Bearer Token."]
    for key, value in data.items():
        if not isinstance(value, str):
            continue
        escaped = value.replace("\\", "\\\\").replace('"', '\\"')
        lines.append(f'{key} = "{escaped}"')
    return "\n".join(lines) + "\n"


def watchlist_query(voices: tuple[Voice, ...], extra: str, limit: int = 12) -> str:
    handles = [v.handle for v in voices[:limit]]
    frm = " OR ".join(f"from:{h}" for h in handles)
    extra = extra.strip()
    if extra:
        return f"({frm}) {extra} -is:retweet"
    return f"({frm}) -is:retweet"


def fetch_x_posts(
    voices: tuple[Voice, ...],
    extra_query: str,
    user_agent: str,
    timeout: int,
    max_results: int = 50,
    token: str | None = None,
) -> tuple[list[Item], list[str]]:
    token = token if token is not None else bearer_token()
    if not token:
        return [], ["x: pas de jeton Bearer (X_BEARER_TOKEN) — RSS seulement"]
    query = watchlist_query(voices, extra_query)
    params = {
        "query": query,
        "max_results": str(min(max(10, max_results), 100)),
        "tweet.fields": "created_at,author_id,text,public_metrics",
        "expansions": "author_id",
        "user.fields": "name,username",
    }
    url = f"{API}?{urlencode(params)}"
    req = Request(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "User-Agent": user_agent,
        },
    )
    try:
        with urlopen(req, timeout=timeout) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:300]
        return [], [f"x: HTTP {exc.code} {detail}"]
    except (URLError, TimeoutError, OSError, json.JSONDecodeError) as exc:
        return [], [f"x: {exc}"]

    users = {u.get("id"): u for u in (payload.get("includes") or {}).get("users") or []}
    items: list[Item] = []
    for post in payload.get("data") or []:
        user = users.get(post.get("author_id") or "") or {}
        handle = user.get("username") or ""
        name = user.get("name") or handle
        text = (post.get("text") or "").strip()
        if not text:
            continue
        company = classify_company(text, text) or "both"
        created = post.get("created_at") or ""
        try:
            dt = datetime.fromisoformat(created.replace("Z", "+00:00")).astimezone(timezone.utc)
            published = dt.replace(microsecond=0).isoformat()
            day = dt.date().isoformat()
        except ValueError:
            continue
        voice = match_voice(name, handle, text, text, voices)
        post_id = str(post.get("id") or "")
        url_post = f"https://x.com/{handle}/status/{post_id}" if handle and post_id else ""
        items.append(
            Item(
                id=hashlib.sha256(f"x:{post_id or text}".encode("utf-8")).hexdigest()[:20],
                date=day,
                company=company,
                source_kind="x",
                source_name=f"X · @{handle}" if handle else "X",
                title=text.split("\n", 1)[0][:180],
                text=text,
                url=url_post,
                published_at=published,
                author=name,
                author_handle=handle,
                voice_id=voice.id if voice else "",
                weight=voice.weight if voice else 30,
            )
        )
    return items, []
