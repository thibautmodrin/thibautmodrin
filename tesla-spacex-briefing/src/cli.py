"""Ligne de commande : scanner, reconstruire, élaguer."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.ingest import rebuild_day, scan
from src.store import connect, get_report, prune, report_dates


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Briefing quotidien Tesla × SpaceX")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_scan = sub.add_parser("scan", help="Collecter les flux et écrire les rapports")
    p_scan.add_argument("--backfill", action="store_true", help="Forcer le rattrapage 7 jours")
    p_scan.add_argument("--no-backfill", action="store_true")

    p_show = sub.add_parser("show", help="Afficher un rapport déjà stocké")
    p_show.add_argument("--date", required=True)

    p_rebuild = sub.add_parser("rebuild", help="Regénérer la synthèse d'un jour")
    p_rebuild.add_argument("--date", required=True)

    p_prune = sub.add_parser("prune", help="Supprimer les jours hors rétention")
    p_prune.add_argument("--days", type=int, default=30)

    sub.add_parser("dates", help="Lister les jours archivés")

    args = parser.parse_args(argv)
    if args.cmd == "scan":
        backfill = True if args.backfill else False if args.no_backfill else None
        result = scan(backfill=backfill)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    if args.cmd == "show":
        conn = connect()
        report = get_report(conn, args.date)
        conn.close()
        if report is None:
            print(f"Pas de rapport pour {args.date}", file=sys.stderr)
            return 1
        print(report.tesla_headline)
        print(report.tesla_summary)
        print()
        print(report.spacex_headline)
        print(report.spacex_summary)
        return 0
    if args.cmd == "rebuild":
        report = rebuild_day(args.date)
        if report is None:
            print(f"Pas d'items pour {args.date}", file=sys.stderr)
            return 1
        print(f"Rapport {report.date} : {report.item_count} items")
        return 0
    if args.cmd == "prune":
        conn = connect()
        n = prune(conn, args.days)
        conn.close()
        print(f"Items supprimés : {n}")
        return 0
    if args.cmd == "dates":
        conn = connect()
        print("\n".join(report_dates(conn)))
        conn.close()
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
