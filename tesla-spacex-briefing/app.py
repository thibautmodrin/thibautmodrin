"""Application Streamlit — briefing quotidien Tesla × SpaceX."""

from __future__ import annotations

import sys
from datetime import date, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st

from src.ingest import scan
from src.monthcal import WEEKDAYS, month_label, month_weeks, shift_month
from src.store import connect, get_report, items_for_date, report_dates
from src.watchlist import load_voices, voice_by_id
from src.x_client import bearer_token, save_bearer_token, token_is_set

st.set_page_config(
    page_title="Tesla × SpaceX — briefing",
    page_icon="🗓️",
    layout="wide",
)

TESLA = "#CC0000"
SPACEX = "#005288"

st.markdown(
    f"""
    <style>
      .block-container {{ padding-top: 1.2rem; }}
      h1, h2, h3 {{ letter-spacing: -0.02em; }}
      .tesla {{ color: {TESLA}; }}
      .spacex {{ color: {SPACEX}; }}
      .day-card {{ border: 1px solid #e2e8f0; border-radius: 12px; padding: 0.6rem 0.8rem; }}
    </style>
    """,
    unsafe_allow_html=True,
)


def _conn():
    return connect()


def _init_state():
    today = date.today()
    st.session_state.setdefault("year", today.year)
    st.session_state.setdefault("month", today.month)
    st.session_state.setdefault("day", today.isoformat())
    st.session_state.setdefault("last_scan", None)


def main() -> None:
    _init_state()
    voices = load_voices()
    conn = _conn()
    days_with_report = set(report_dates(conn))

    st.title("Tesla × SpaceX — briefing quotidien")
    st.caption(
        "Veille presse + X (si jeton) sur Tesla et SpaceX. Synthèse par jour, "
        "paroles des voix qui ont du poids, calendrier conservé plusieurs semaines."
    )

    with st.sidebar:
        st.header("Clé Bearer X")
        st.caption(
            "Developer Portal X → projet → **Keys and tokens** → Bearer Token. "
            "Sans clé, le scan reste sur la presse."
        )
        if token_is_set():
            st.success("Une clé est déjà enregistrée sur le serveur.")
        else:
            st.warning("Aucune clé pour l’instant.")
        pasted = st.text_input(
            "Coller le Bearer Token",
            type="password",
            placeholder="AAAAAAAA…",
            help="Le jeton n’est pas envoyé dans git. Enregistre-le ici ou dans .streamlit/secrets.toml.",
        )
        if st.button("Enregistrer la clé"):
            if pasted.strip():
                save_bearer_token(pasted.strip())
                st.success("Clé enregistrée. Tu peux scanner.")
                st.rerun()
            else:
                st.error("Colle d’abord le jeton.")

    top = st.columns([1.4, 1, 1, 1.2])
    with top[0]:
        if st.button("Scanner les news maintenant", type="primary"):
            with st.spinner("Collecte des flux RSS et des posts X…"):
                result = scan(token=pasted.strip() or None)
            st.session_state.last_scan = result
            if result.get("days"):
                st.session_state.day = max(result["days"])
            st.rerun()
    with top[1]:
        if st.button("Mois précédent"):
            y, m = shift_month(st.session_state.year, st.session_state.month, -1)
            st.session_state.year, st.session_state.month = y, m
            st.rerun()
    with top[2]:
        if st.button("Mois suivant"):
            y, m = shift_month(st.session_state.year, st.session_state.month, 1)
            st.session_state.year, st.session_state.month = y, m
            st.rerun()
    with top[3]:
        st.markdown(f"**{month_label(st.session_state.year, st.session_state.month)}**")
        if st.session_state.last_scan:
            err_n = len(st.session_state.last_scan.get("errors") or [])
            st.caption(
                f"Dernier scan : {st.session_state.last_scan['items']} items, "
                f"{st.session_state.last_scan['reports']} jours"
                + (f", {err_n} avertissement(s)" if err_n else "")
            )
            x_errs = [
                err for err in (st.session_state.last_scan.get("errors") or []) if err.startswith("x:")
            ]
            if x_errs:
                st.caption("X : " + x_errs[0][:180])

    _calendar(days_with_report)
    day = st.session_state.day
    report = get_report(conn, day)
    items = items_for_date(conn, day)

    st.divider()
    st.subheader(_human_day(day))

    if report is None:
        st.info("Pas encore de briefing pour ce jour. Lance un scan, ou choisis un jour marqué dans le calendrier.")
        conn.close()
        return

    kpis = st.columns(4)
    kpis[0].metric("Éléments", report.item_count)
    kpis[1].metric("Tesla", report.tesla_count)
    kpis[2].metric("SpaceX", report.spacex_count)
    kpis[3].metric("Voix", report.voice_count)

    left, right = st.columns(2)
    with left:
        st.markdown(f"### <span class='tesla'>Tesla</span>", unsafe_allow_html=True)
        st.markdown(f"**{report.tesla_headline}**")
        st.text(report.tesla_summary)
    with right:
        st.markdown(f"### <span class='spacex'>SpaceX</span>", unsafe_allow_html=True)
        st.markdown(f"**{report.spacex_headline}**")
        st.text(report.spacex_summary)

    st.markdown("### Ce qui a été dit")
    if not report.quotes:
        st.write("Aucune citation attribuée à la watchlist pour ce jour (direction, investisseurs, relais).")
    else:
        by_cat = {}
        labels = {
            "tesla_exec": "Chez Tesla",
            "spacex_exec": "Chez SpaceX",
            "official": "Comptes officiels",
            "investor": "Investisseurs",
            "voice": "Voix suivies",
            "journalist": "Médias de référence",
        }
        for quote in report.quotes:
            by_cat.setdefault(quote.category, []).append(quote)
        for cat in ("official", "tesla_exec", "spacex_exec", "investor", "voice", "journalist"):
            group = by_cat.get(cat) or []
            if not group:
                continue
            st.markdown(f"**{labels[cat]}**")
            for quote in group:
                handle = ""
                voice = voice_by_id(voices).get(quote.voice_id)
                if voice:
                    handle = f" · @{voice.handle}"
                st.markdown(
                    f"- **{quote.name}** ({quote.role}{handle}) — « {quote.text} » "
                    + (f"[source]({quote.url})" if quote.url else f"({quote.source_name})")
                )

    st.markdown("### Sujets du jour")
    for cluster in report.clusters:
        tag = "Tesla" if cluster.company == "tesla" else "SpaceX"
        with st.expander(f"{tag} · {cluster.title} ({len(cluster.item_ids)} source(s))"):
            if cluster.summary:
                st.write(cluster.summary)
            st.caption(" · ".join(cluster.sources))

    with st.expander(f"Fil brut ({len(items)} items)"):
        for item in items:
            who = item.author or item.source_name
            prefix = "X" if item.source_kind == "x" else item.source_name
            st.markdown(f"- [{prefix}] **{who}** — [{item.title}]({item.url})" if item.url else f"- **{who}** — {item.title}")

    conn.close()


def _calendar(days_with_report: set[str]) -> None:
    weeks = month_weeks(st.session_state.year, st.session_state.month)
    header = st.columns(7)
    for i, name in enumerate(WEEKDAYS):
        header[i].markdown(f"**{name}**")
    today = date.today().isoformat()
    for week in weeks:
        cols = st.columns(7)
        for i, day in enumerate(week):
            if day is None:
                cols[i].write("")
                continue
            iso = day.isoformat()
            mark = "●" if iso in days_with_report else " "
            label = f"{day.day} {mark}"
            if iso == today:
                label = f"[{day.day}] {mark}"
            if cols[i].button(label, key=f"cal-{iso}", use_container_width=True):
                st.session_state.day = iso
                st.rerun()


def _human_day(iso: str) -> str:
    dt = datetime.strptime(iso, "%Y-%m-%d")
    jours = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
    mois = [
        "",
        "janvier",
        "février",
        "mars",
        "avril",
        "mai",
        "juin",
        "juillet",
        "août",
        "septembre",
        "octobre",
        "novembre",
        "décembre",
    ]
    return f"{jours[dt.weekday()]} {dt.day} {mois[dt.month]} {dt.year}"


if __name__ == "__main__":
    main()
