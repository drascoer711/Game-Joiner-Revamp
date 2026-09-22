from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_json(path: str | Path, default: Any = None) -> Any:
    p = Path(path)
    if not p.exists():
        return default
    try:
        with p.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except (json.JSONDecodeError, OSError):
        return default


def save_json(path: str | Path, value: Any) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8") as handle:
        json.dump(value, handle, indent=2, ensure_ascii=False)
        handle.write("\n")


def normalize_city(name: str) -> str:
    if not name:
        return ""
    import re
    import unicodedata

    normalized = unicodedata.normalize("NFKD", name)
    normalized = "".join(ch for ch in normalized if not unicodedata.combining(ch))
    normalized = normalized.lower()
    normalized = re.sub(r"[^\w\s]", " ", normalized)
    return re.sub(r"\s+", " ", normalized).strip()


def make_dcid(city: str, ip: str) -> str:
    import re

    safe_city = re.sub(r"[^\w]", "_", (city or "UNKNOWN").strip().upper()) if city else "UNKNOWN"
    safe_ip = re.sub(r"[^0-9A-Fa-f:.]", "", ip or "").replace(".", "_").replace(":", "_")
    return f"{safe_city}_{safe_ip or 'UNKNOWN'}"
