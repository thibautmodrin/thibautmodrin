"""Classification Tesla / SpaceX et filtrage du bruit."""

from __future__ import annotations

import re

TESLA_RE = re.compile(
    r"\b(tesla|tsla|cybertruck|cybercab|optimus|roadster|robotaxi|"
    r"gigafactory|supercharger|megapack|powerwall|model [3sxy]|fsd|"
    r"full self[- ]driving|unboxed)\b",
    re.I,
)
SPACEX_RE = re.compile(
    r"\b(spacex|spcx|starship|starlink|falcon ?9|falcon heavy|starbase|"
    r"super heavy|raptor|crew dragon|dragon capsule|starlink)\b",
    re.I,
)
NOISE_RE = re.compile(
    r"tesla coil|nikola tesla|\btesla motors?\b club|museum of discovery",
    re.I,
)


def classify_company(title: str, text: str = "", hinted: str = "") -> str | None:
    if is_noise(title, text):
        return None
    blob = f"{title} {text}"
    tesla = bool(TESLA_RE.search(blob))
    spacex = bool(SPACEX_RE.search(blob))
    if tesla and spacex:
        return "both"
    if tesla:
        return "tesla"
    if spacex:
        return "spacex"
    if hinted in {"tesla", "spacex", "both"}:
        return hinted
    return None


def is_noise(title: str, text: str = "") -> bool:
    blob = f"{title} {text}"
    if not NOISE_RE.search(blob):
        return False
    if re.search(r"\b(tsla|cybertruck|cybercab|model [3sxy]|robotaxi|gigafactory)\b", blob, re.I):
        return False
    return True
