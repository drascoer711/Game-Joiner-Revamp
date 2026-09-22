from __future__ import annotations

import asyncio
import logging
from typing import Any

import aiohttp

from game_joiner.storage import make_dcid, normalize_city

logger = logging.getLogger("game_joiner.services.roblox")


async def fetch_all_active_servers(
    place_id: int,
    session: aiohttp.ClientSession,
    max_pages: int = 10,
) -> list[dict[str, Any]]:
    url = f"https://games.roblox.com/v1/games/{place_id}/servers/Public?limit=100"
    cursor = ""
    all_servers: list[dict[str, Any]] = []
    pages = 0

    while pages < max_pages:
        paginated_url = f"{url}&cursor={cursor}" if cursor else url
        headers = {"User-Agent": "Mozilla/5.0"}
        try:
            async with session.get(paginated_url, headers=headers) as response:
                if response.status != 200:
                    logger.warning("Roblox server list returned HTTP %s for place %s", response.status, place_id)
                    break
                data = await response.json()
                all_servers.extend(data.get("data", []))
                cursor = data.get("nextPageCursor")
                pages += 1
                if not cursor:
                    break
        except Exception as exc:  # pragma: no cover
            logger.warning("Failed fetching servers for place %s: %s", place_id, exc)
            break

    return all_servers


async def resolve_server_ip_and_region(
    session: aiohttp.ClientSession,
    place_id: int,
    job_id: str,
) -> dict[str, Any] | None:
    join_url = "https://gamejoin.roblox.com/v1/join-game-instance"
    payload = {"placeId": place_id, "gameId": job_id}

    try:
        headers = {"Origin": "https://www.roblox.com"}
        async with session.post(join_url, json=payload, headers=headers) as response:
            if response.status != 200:
                return None
            data = await response.json()

        join_script = data.get("joinScript", {}) or {}
        server_address = (
            join_script.get("ClientServerHost")
            or join_script.get("MachineAddress")
            or data.get("serverAddress")
        )

        clean_ip = clean_host(server_address)
        if not clean_ip:
            return None

        async with session.get(f"http://ip-api.com/json/{clean_ip}") as geo_response:
            if geo_response.status != 200:
                return None
            geo_data = await geo_response.json()

        if geo_data.get("status") != "success":
            return None

        city = geo_data.get("city") or "Unknown City"
        return {
            "ip": clean_ip,
            "city": city,
            "country": geo_data.get("country", "Unknown Country"),
            "isp": geo_data.get("isp", "Unknown Host"),
            "lat": geo_data.get("lat"),
            "lon": geo_data.get("lon"),
            "dcid": make_dcid(city, clean_ip),
            "normalized_city": normalize_city(city),
        }
    except Exception as exc:  # pragma: no cover
        logger.warning("Failed resolving server region for %s: %s", job_id, exc)
        return None


def clean_host(value: str | None) -> str | None:
    if not value:
        return None

    candidate = str(value).strip()
    if "//" in candidate:
        from urllib.parse import urlparse

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


def normalize_city(value: str) -> str:
    import re
    import unicodedata

    if not value:
        return ""
    text = unicodedata.normalize("NFKD", value)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()
