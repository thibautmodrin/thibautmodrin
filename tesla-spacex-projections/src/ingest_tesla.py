"""Ingestion Tesla Q3 2026 uniquement.

Télécharge l'Update deck officiel. Si Tesla IR renvoie une page HTML (print
pas encore sorti), on n'invente rien. L'écriture YAML exige une revue :
champs requis présents, trimestre = Q3-2026, pas déjà dans actuals.
"""

from __future__ import annotations

import argparse
import io
import re
from dataclasses import asdict, dataclass, field
from datetime import date
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import yaml

from src.load import DATA, actuals, clear_data_cache

USER_AGENT = "tesla-spacex-projections/1.0 (research; Tesla Q3 ingest)"
DEFAULT_URL = "https://assets-ir.tesla.com/tesla-contents/IR/TSLA-Q3-2026-Update.pdf"
TARGET_QUARTER = "Q3-2026"
REQUIRED = ("revenue_b", "deliveries", "storage_gwh")

# Lignes du Financial / Operational Summary (dernière colonne = trimestre courant).
ROW_PATTERNS = {
    "revenue_b": r"^Total revenues\b",
    "revenue_auto_b": r"^Total automotive revenues\b",
    "revenue_energy_b": r"^Energy generation and storage revenue\b",
    "revenue_services_b": r"^Services and other revenue\b",
    "ocf_b": r"^Net cash provided by operating activities\b",
    "capex_b": r"^Capital expenditures\b",
    "fcf_b": r"^Free cash flow\b",
    "cash_b": r"^Cash, cash equivalents and short-term investments\b",
    "deliveries": r"^Total deliveries\b",
    "storage_gwh": r"^Storage deployed \(GWh\)",
    "fsd_subs_m": r"^Active FSD Subscriptions",
    "cumulative_deliveries_m": r"^Cumulative deliveries",
}

MILLION_USD_KEYS = {
    "revenue_b",
    "revenue_auto_b",
    "revenue_energy_b",
    "revenue_services_b",
    "ocf_b",
    "capex_b",
    "fcf_b",
    "cash_b",
}


@dataclass
class IngestResult:
    status: str
    url: str
    message: str
    quarter: str | None = None
    fields: dict[str, Any] = field(default_factory=dict)
    missing: list[str] = field(default_factory=list)
    preview: list[dict[str, Any]] = field(default_factory=list)
    cybercab_commercial: bool | None = None
    content_type: str | None = None

    def can_apply(self) -> bool:
        return self.status == "parsed" and not self.missing and self.quarter == TARGET_QUARTER


def _http_get(url: str, timeout: int = 45) -> tuple[int, str, bytes]:
    req = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(req, timeout=timeout) as resp:
        content_type = (resp.headers.get("Content-Type") or "").split(";")[0].strip().lower()
        return int(resp.status), content_type, resp.read()


def fetch_update_pdf(url: str = DEFAULT_URL) -> IngestResult:
    try:
        status, content_type, body = _http_get(url)
    except HTTPError as exc:
        if exc.code == 404:
            return IngestResult(
                status="not_published",
                url=url,
                message="Le PDF Q3 n'est pas en ligne (404). On n'invente pas le trimestre.",
                content_type=None,
            )
        return IngestResult(status="error", url=url, message=f"HTTP {exc.code}: {exc.reason}")
    except URLError as exc:
        return IngestResult(status="error", url=url, message=f"Réseau : {exc.reason}")

    if "pdf" not in (content_type or "") and not body.startswith(b"%PDF"):
        return IngestResult(
            status="not_published",
            url=url,
            message=(
                "Tesla IR a renvoyé une page HTML, pas un PDF. "
                "Le Q3 2026 Update n'est probablement pas encore publié."
            ),
            content_type=content_type,
        )
    if status != 200:
        return IngestResult(status="error", url=url, message=f"HTTP {status}", content_type=content_type)

    try:
        text = _pdf_text(body)
    except Exception as exc:  # noqa: BLE001 — on refuse d'écrire si le parseur casse
        return IngestResult(
            status="error",
            url=url,
            message=f"Lecture PDF impossible : {exc}",
            content_type=content_type,
        )
    parsed = parse_update_text(text)
    parsed.url = url
    parsed.content_type = content_type
    if parsed.status == "parsed":
        parsed.preview = _preview_rows(parsed)
        if parsed.quarter != TARGET_QUARTER:
            parsed.status = "wrong_quarter"
            parsed.message = (
                f"Document identifié comme {parsed.quarter}, pas {TARGET_QUARTER}. "
                "Cette ingestion ne traite que Tesla Q3 2026."
            )
    return parsed


def _pdf_text(body: bytes) -> str:
    from pypdf import PdfReader

    reader = PdfReader(io.BytesIO(body))
    pages = []
    for page in reader.pages[:8]:
        pages.append(page.extract_text() or "")
    return "\n".join(pages)


def _strip_yoy(line: str) -> str:
    return re.sub(r"[-+]?\d+(?:\.\d+)?\s*%\s*$", "", line.strip())


def _row_numbers(line: str) -> list[float]:
    line = _strip_yoy(line)
    nums: list[float] = []
    for match in re.finditer(
        r"\(([0-9]{1,3}(?:,[0-9]{3})*(?:\.[0-9]+)?)\)|(-?[0-9]{1,3}(?:,[0-9]{3})*(?:\.[0-9]+)?)",
        line,
    ):
        if match.group(1) is not None:
            nums.append(-float(match.group(1).replace(",", "")))
        else:
            raw = match.group(2)
            if raw is None:
                continue
            nums.append(float(raw.replace(",", "")))
    return nums


def _find_line(text: str, pattern: str) -> str | None:
    cre = re.compile(pattern, re.IGNORECASE)
    for raw in text.splitlines():
        line = " ".join(raw.split())
        if cre.search(line):
            return line
    return None


def parse_update_text(text: str) -> IngestResult:
    header = re.search(r"Q([1-4])\s+(20\d{2})\s+Update", text)
    if not header:
        return IngestResult(
            status="error",
            url="",
            message="Impossible d'identifier le trimestre (titre « Qn 20xx Update » absent).",
        )
    quarter = f"Q{header.group(1)}-{header.group(2)}"
    qtr, year = quarter.split("-")
    fields: dict[str, Any] = {"quarter": quarter, "source": f"tesla_{qtr.lower()}_{year}"}
    for key, pattern in ROW_PATTERNS.items():
        line = _find_line(text, pattern)
        if line is None:
            continue
        nums = _row_numbers(line)
        if not nums:
            continue
        value = nums[-1]
        if key in MILLION_USD_KEYS:
            value = value / 1000.0
            if key == "capex_b":
                value = abs(value)
        fields[key] = value

    if fields.get("revenue_auto_b") and fields.get("deliveries"):
        fields["asp_auto"] = round(fields["revenue_auto_b"] * 1e9 / fields["deliveries"])

    commercial = _cybercab_commercial(text)
    missing = [k for k in REQUIRED if k not in fields]
    if missing:
        return IngestResult(
            status="incomplete",
            url="",
            quarter=quarter,
            fields=fields,
            missing=missing,
            cybercab_commercial=commercial,
            message="Champs requis absents du PDF : " + ", ".join(missing),
        )
    return IngestResult(
        status="parsed",
        url="",
        quarter=quarter,
        fields=fields,
        missing=[],
        cybercab_commercial=commercial,
        message=f"{quarter} lu : CA {fields['revenue_b']:.3f} Md$, {int(fields['deliveries']):,} livraisons.".replace(",", " "),
    )


def _cybercab_commercial(text: str) -> bool | None:
    found_production = False
    for match in re.finditer(r".{0,100}Cybercab.{0,100}", text, flags=re.IGNORECASE | re.DOTALL):
        snippet = re.sub(r"\s+", " ", match.group(0)).lower()
        if "commercial" in snippet and ("fleet" in snippet or "operation" in snippet or "service" in snippet):
            if "not" in snippet or "pas encore" in snippet:
                return False
            return True
        if "began production" in snippet or "start of production" in snippet or "started production" in snippet:
            found_production = True
    if found_production:
        return False
    return None


def _preview_rows(result: IngestResult) -> list[dict[str, Any]]:
    published = [r for r in actuals().get("tesla_quarters", []) if r.get("quarter") == TARGET_QUARTER]
    existing = published[0] if published else {}
    keys = [
        "revenue_b",
        "revenue_auto_b",
        "revenue_energy_b",
        "revenue_services_b",
        "deliveries",
        "storage_gwh",
        "ocf_b",
        "capex_b",
        "fcf_b",
        "fsd_subs_m",
        "cash_b",
        "cumulative_deliveries_m",
        "asp_auto",
    ]
    rows = []
    for key in keys:
        if key not in result.fields:
            continue
        rows.append(
            {
                "champ": key,
                "actuel": existing.get(key),
                "nouveau": result.fields[key],
            }
        )
    rows.append(
        {
            "champ": "cybercab_in_commercial_fleet",
            "actuel": actuals().get("tesla_2026", {}).get("cybercab_in_commercial_fleet"),
            "nouveau": result.cybercab_commercial,
        }
    )
    return rows


def apply_q3(result: IngestResult, *, force: bool = False) -> dict[str, Any]:
    if not force and not result.can_apply():
        raise ValueError(result.message or "Ingestion refusée : document incomplet ou trimestre incorrect.")
    if any(r.get("quarter") == TARGET_QUARTER for r in actuals()["tesla_quarters"]):
        raise ValueError(f"{TARGET_QUARTER} est déjà dans actuals.yaml. Pas d'écrasement silencieux.")

    data = actuals()
    row = {
        "quarter": TARGET_QUARTER,
        "revenue_b": round(float(result.fields["revenue_b"]), 3),
        "deliveries": int(result.fields["deliveries"]),
        "storage_gwh": float(result.fields["storage_gwh"]),
        "source": "tesla_q3_2026",
    }
    for key in (
        "revenue_auto_b",
        "revenue_energy_b",
        "revenue_services_b",
        "ocf_b",
        "capex_b",
        "fcf_b",
        "fsd_subs_m",
        "cash_b",
        "cumulative_deliveries_m",
        "asp_auto",
    ):
        if key in result.fields and result.fields[key] is not None:
            value = result.fields[key]
            row[key] = int(value) if key in {"asp_auto"} else round(float(value), 3) if isinstance(value, float) else value

    data["tesla_quarters"].append(row)
    meta = dict(data["tesla_2026"])
    meta["last_quarter"] = "Q3"
    meta["next_print"] = "Q4"
    meta["as_of"] = "2026-09-30"
    meta["source"] = "tesla_q3_2026"
    if result.cybercab_commercial is not None:
        meta["cybercab_in_commercial_fleet"] = bool(result.cybercab_commercial)
    q1q2 = [r for r in data["tesla_quarters"] if str(r["quarter"]).endswith("-2026") and r["quarter"] != TARGET_QUARTER]
    q3 = row
    ytd_rev = sum(float(r["revenue_b"]) for r in q1q2) + float(q3["revenue_b"])
    ytd_del = sum(float(r["deliveries"]) for r in q1q2) + float(q3["deliveries"])
    ytd_gwh = sum(float(r["storage_gwh"]) for r in q1q2) + float(q3["storage_gwh"])
    meta["ytd_revenue_b"] = round(ytd_rev, 3)
    meta["ytd_deliveries"] = int(ytd_del)
    meta["ytd_storage_gwh"] = round(ytd_gwh, 1)
    data["tesla_2026"] = meta
    data["as_of"] = date.today().isoformat()

    actuals_path = DATA / "actuals.yaml"
    header = (
        "# Trimestres publiés. Quand un trimestre sort, on ajoute une ligne ici —\n"
        "# on ne « complète » pas le trimestre par interpolation.\n"
        "# Q3 2026 : écrit par src/ingest_tesla.py après revue (faits seulement).\n\n"
    )
    actuals_path.write_text(header + yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8")

    _append_source(
        {
            "id": "tesla_q3_2026",
            "type": "fact",
            "title": "Tesla Q3 2026 Update",
            "url": result.url or DEFAULT_URL,
            "used_for": [
                "CA et mix T3",
                "livraisons, stockage, FSD",
                "OCF / capex / FCF / cash si présents",
                "recalage FY 2026 = YTD + run-rate Q3 pour Q4",
            ],
        }
    )
    _patch_history_snapshot(row, result)
    clear_data_cache()
    return {"written": ["data/actuals.yaml", "data/sources.yaml", "data/tesla_history.yaml"], "quarter": row}


def _append_source(item: dict[str, Any]) -> None:
    path = DATA / "sources.yaml"
    text = path.read_text(encoding="utf-8")
    if f"id: {item['id']}" in text:
        return
    lines = [
        f"  - id: {item['id']}",
        f"    type: {item['type']}",
        f"    title: {item['title']}",
    ]
    if item.get("url"):
        lines.append(f"    url: {item['url']}")
    lines.append("    used_for:")
    for used in item.get("used_for", []):
        lines.append(f"      - {used}")
    path.write_text(text.rstrip() + "\n" + "\n".join(lines) + "\n", encoding="utf-8")


def _patch_history_snapshot(row: dict[str, Any], result: IngestResult) -> None:
    path = DATA / "tesla_history.yaml"
    text = path.read_text(encoding="utf-8")
    if "snapshot_latest:" not in text:
        return
    head, tail = text.split("snapshot_latest:", 1)
    # tail starts after the key; keep structure, rewrite a few quantitative lines.
    lines = []
    for line in tail.splitlines(keepends=True):
        stripped = line.lstrip()
        if stripped.startswith("date:"):
            line = '  date: "2026-09-30"\n'
        elif stripped.startswith("label:"):
            line = '  label: "Q3 2026 (dernier trimestre publié)"\n'
        elif stripped.startswith("quarter_revenue:"):
            line = f"  quarter_revenue: {row['revenue_b']}\n"
        elif stripped.startswith("source:") and "tesla_q" in stripped:
            line = "  source: tesla_q3_2026\n"
        elif stripped.startswith("fsd_subs_m:") and row.get("fsd_subs_m") is not None:
            line = f"  fsd_subs_m: {row['fsd_subs_m']}\n"
        elif stripped.startswith("cumulative_deliveries_m:") and row.get("cumulative_deliveries_m") is not None:
            line = f"  cumulative_deliveries_m: {row['cumulative_deliveries_m']}\n"
        elif stripped.startswith("cybercab_in_commercial_fleet:") and result.cybercab_commercial is not None:
            line = f"  cybercab_in_commercial_fleet: {'true' if result.cybercab_commercial else 'false'}\n"
        elif stripped.startswith("cash_q2_b:") and row.get("cash_b") is not None:
            line = f"  cash_q3_b: {row['cash_b']}\n"
        lines.append(line)
    path.write_text(head + "snapshot_latest:" + "".join(lines), encoding="utf-8")


def probe_to_dict(result: IngestResult) -> dict[str, Any]:
    payload = asdict(result)
    payload["can_apply"] = result.can_apply()
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Ingestion Tesla Q3 2026 (faits seulement).")
    parser.add_argument("--url", default=DEFAULT_URL)
    parser.add_argument("--apply", action="store_true", help="Écrire les YAML si le parse est complet.")
    args = parser.parse_args(argv)
    result = fetch_update_pdf(args.url)
    print(result.status, result.message)
    if result.preview:
        for row in result.preview:
            print(f"  {row['champ']}: {row['actuel']} → {row['nouveau']}")
    if args.apply:
        written = apply_q3(result)
        print("écrit", written["written"])
    return 0 if result.status in {"parsed", "not_published"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
