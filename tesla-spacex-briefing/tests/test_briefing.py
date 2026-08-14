from datetime import date
from pathlib import Path

from src.classify import classify_company, is_noise
from src.models import Item
from src.rss import parse_feed
from src.summarize import build_report, cluster_items, extract_quotes, jaccard, tokens
from src.watchlist import load_voices, match_voice
from src.monthcal import month_weeks, shift_month
from src.store import connect, get_report, items_for_date, prune, save_report, upsert_items
from src.x_client import bearer_token, save_bearer_token, watchlist_query

FIXTURES = Path(__file__).parent / "fixtures"


def test_noise_filters_tesla_coil():
    assert is_noise("The Museum of Discovery demonstrates their bipolar Tesla coil")
    assert classify_company("The Museum of Discovery demonstrates their bipolar Tesla coil") is None


def test_classify_roadster_and_starship():
    assert classify_company("Tesla flying Roadster demo at SpaceX Texas site") == "both"
    assert classify_company("Tesla assigns Model Y L delivery windows") == "tesla"
    assert classify_company("Starship static fire at Starbase") == "spacex"


def test_parse_tesla_feed_drops_coil_and_dates_items():
    raw = (FIXTURES / "tesla_rss.xml").read_bytes()
    items = parse_feed(raw, "Google News Tesla", "tesla")
    titles = [i.title for i in items]
    assert any("Roadster" in t for t in titles)
    assert all("coil" not in t.lower() for t in titles)
    days = {i.date for i in items}
    assert "2026-08-14" in days
    assert "2026-08-13" in days


def test_match_elon_and_cathie():
    voices = load_voices()
    musk = match_voice("", "", "Elon Musk said the demo could go wrong", "", voices)
    assert musk is not None and musk.id == "elonmusk"
    cathie = match_voice("", "", "Cathie Wood said Tesla robotaxis remain the core", "", voices)
    assert cathie is not None and cathie.id == "cathie"


def test_musk_headline_is_not_a_quote_without_speech():
    voices = load_voices()
    items = [
        Item(
            "h1",
            "2026-08-14",
            "spacex",
            "rss",
            "Example",
            "Elon Musk's SpaceX Stake Is Worth More Than $900 Billion",
            "",
            "https://example.com/stake",
            "2026-08-14T12:00:00+00:00",
        )
    ]
    assert extract_quotes(items, voices) == []


def test_said_becomes_a_quote():
    voices = load_voices()
    items = [
        Item(
            "h2",
            "2026-08-14",
            "tesla",
            "rss",
            "Electrek",
            "Tesla Roadster demo",
            "Elon Musk said the demonstration will be difficult to execute.",
            "https://example.com/demo",
            "2026-08-14T12:00:00+00:00",
        )
    ]
    quotes = extract_quotes(items, voices)
    assert any(q.voice_id == "elonmusk" and "difficult" in q.text for q in quotes)


def test_capitalized_says_in_headline():
    voices = load_voices()
    items = [
        Item(
            "h3",
            "2026-08-14",
            "spacex",
            "rss",
            "Motley Fool",
            "Elon Musk Says SpaceX Will Try to Catch a Returning Starship This Month",
            "",
            "https://example.com/catch",
            "2026-08-14T12:00:00+00:00",
        )
    ]
    quotes = extract_quotes(items, voices)
    assert any(q.voice_id == "elonmusk" and "Starship" in q.text for q in quotes)


def test_quotes_from_reported_speech():
    voices = load_voices()
    raw = (FIXTURES / "tesla_rss.xml").read_bytes()
    items = parse_feed(raw, "Google News Tesla", "tesla", voices)
    quotes = extract_quotes(items, voices)
    names = {q.name for q in quotes}
    assert "Elon Musk" in names
    assert "Cathie Wood" in names


def test_cluster_merges_similar_roadster_titles():
    items = [
        Item("1", "2026-08-14", "tesla", "rss", "Reuters", "Tesla to unveil redesigned Roadster", "", "", "2026-08-14T17:00:00+00:00", weight=35),
        Item("2", "2026-08-14", "tesla", "rss", "Electrek", "Tesla flying Roadster demo this month", "", "", "2026-08-14T15:00:00+00:00", weight=40),
        Item("3", "2026-08-14", "tesla", "rss", "Axios", "Tesla sought permit for robotaxis in Las Vegas", "", "", "2026-08-14T18:00:00+00:00", weight=20),
    ]
    clusters = cluster_items(items, "tesla", threshold=0.2)
    assert len(clusters) >= 2
    sizes = sorted(len(c.item_ids) for c in clusters)
    assert sizes[-1] >= 2


def test_jaccard_tokens():
    a = tokens("Tesla flying Roadster demo this month")
    b = tokens("Tesla Roadster demo could come this month")
    assert jaccard(a, b) > 0.3


def test_store_roundtrip(tmp_path):
    voices = load_voices()
    conn = connect(tmp_path / "t.db")
    tesla = parse_feed((FIXTURES / "tesla_rss.xml").read_bytes(), "Tesla", "tesla", voices)
    spacex = parse_feed((FIXTURES / "spacex_rss.xml").read_bytes(), "SpaceX", "spacex", voices)
    upsert_items(conn, tesla + spacex)
    day_items = items_for_date(conn, "2026-08-14")
    assert day_items
    report = build_report("2026-08-14", day_items, voices)
    save_report(conn, report)
    loaded = get_report(conn, "2026-08-14")
    assert loaded is not None
    assert loaded.tesla_count >= 1
    assert loaded.spacex_count >= 1
    assert "Roadster" in loaded.tesla_headline or "Roadster" in loaded.tesla_summary
    removed = prune(conn, retention_days=1, today=date(2026, 8, 14))
    assert removed >= 0
    conn.close()


def test_month_weeks_monday_first():
    weeks = month_weeks(2026, 8)
    assert weeks[0][5] is not None  # 1 Aug 2026 is Saturday
    y, m = shift_month(2026, 1, -1)
    assert (y, m) == (2025, 12)


def test_x_query_includes_watchlist():
    q = watchlist_query(load_voices(), "(Tesla OR SpaceX)")
    assert "from:elonmusk" in q
    assert "from:Tesla" in q
    assert "-is:retweet" in q


def test_bearer_token_from_secrets_file(monkeypatch, tmp_path):
    monkeypatch.delenv("X_BEARER_TOKEN", raising=False)
    monkeypatch.delenv("TWITTER_BEARER_TOKEN", raising=False)
    secrets = tmp_path / "secrets.toml"
    save_bearer_token("file-token-xyz", secrets)
    assert bearer_token(secrets) == "file-token-xyz"
    monkeypatch.setenv("X_BEARER_TOKEN", "env-token")
    assert bearer_token(secrets) == "env-token"
