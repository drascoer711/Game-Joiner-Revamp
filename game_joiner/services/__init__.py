from __future__ import annotations

import re
from urllib.parse import urlparse


def public_game_url(place_id: int | str) -> str:
    return f"https://www.roblox.com/games/{place_id}"


def clean_host(value: str | None) -> str | None:
    if not value:
        return None

    candidate = str(value).strip()
    if "//" in candidate:
        parsed = urlparse(candidate)
        candidate = parsed.hostname or ""

    if candidate.startswith("[") and "]" in candidate:
        candidate = candidate[1:candidate.index("]")]

    if candidate.count(":") == 1:
        candidate = candidate.split(":", 1)[0]

    try:
        import ipaddress

        ipaddress.ip_address(candidate)
        return candidate
    except ValueError:
        return None


def normalize_city(name: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^\w\s]", " ", name.lower())).strip() if name else ""
