from __future__ import annotations

import asyncio
import logging
from typing import Any

from game_joiner.config import load_settings
from game_joiner.storage import load_json, save_json, make_dcid, normalize_city

logger = logging.getLogger("game_joiner.services.monitoring")


TARGET_PLACE_IDS = [920587237, 1818, 3237166, 4483381587]


class DatacenterRegistry:
    def __init__(self, settings: Any):
        self.settings = settings
        self._known = set(self._load_known())
        self._tracked = self._load_tracked()

    def _load_known(self) -> list[str]:
        data = load_json(self.settings.known_datacenters_file, [])
        return data if isinstance(data, list) else []

    def _load_tracked(self) -> dict[str, dict[str, Any]]:
        data = load_json(self.settings.tracked_nodes_file, {})
        return data if isinstance(data, dict) else {}

    def save(self) -> None:
        save_json(self.settings.known_datacenters_file, sorted(self._known))
        save_json(self.settings.tracked_nodes_file, self._tracked)

    def register(self, city: str, ip: str, source: str = "manual") -> tuple[bool, str | None]:
        if not city or not ip:
            return False, None
        dcid = make_dcid(city, ip)
        if dcid in self._known:
            return False, dcid

        self._known.add(dcid)
        self._tracked[dcid] = {
            "city": city,
            "location": city,
            "id": dcid,
            "ip": ip,
            "status": "online",
            "source": source,
        }
        self.save()
        return True, dcid

    def get_known(self) -> list[str]:
        return sorted(self._known)

    def get_tracked(self) -> dict[str, dict[str, Any]]:
        return dict(self._tracked)


async def monitor_datacenter_discoveries(registry: DatacenterRegistry, session_factory):
    settings = registry.settings
    while True:
        try:
            async with session_factory() as session:
                for place_id in TARGET_PLACE_IDS:
                    from game_joiner.services.roblox import fetch_all_active_servers, resolve_server_ip_and_region

                    servers = await fetch_all_active_servers(place_id, session, max_pages=3)
                    for server in servers:
                        job_id = server.get("id")
                        if not job_id:
                            continue
                        region = await resolve_server_ip_and_region(session, place_id, job_id)
                        if not region:
                            continue
                        city = region["city"]
                        ip = region["ip"]
                        normalized = normalize_city(city)
                        if normalized in {normalize_city(item.get("city", "")) for item in registry.get_tracked().values()}:
                            continue
                        registered, dcid = registry.register(city, ip, source="datacenter_scan")
                        if not registered:
                            continue
                        logger.info("Discovered datacenter %s in %s via %s", dcid, city, source)
                        await send_discord_alert(settings.datacenter_alert_webhook_url, {
                            "content": f"Datacenter discovered: {city} ({dcid})",
                        })
        except Exception as exc:  # pragma: no cover
            logger.warning("Datacenter monitoring loop failed: %s", exc)
        await asyncio.sleep(300)


async def send_discord_alert(webhook_url: str, payload: dict[str, Any]) -> bool:
    import aiohttp

    if not webhook_url:
        return False
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(webhook_url, json=payload) as response:
                return response.status < 400
    except Exception as exc:  # pragma: no cover
        logger.warning("Discord webhook failed: %s", exc)
        return False
