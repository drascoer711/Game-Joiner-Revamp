from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any


def _get_env(name: str, default: str = "") -> str:
    value = os.getenv(name, default)
    return value.strip() if isinstance(value, str) else default


def _get_int_env(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None or raw == "":
        return default
    try:
        return int(raw)
    except ValueError:
        return default


@dataclass(frozen=True)
class Settings:
    discord_bot_token: str
    datacenter_alert_webhook_url: str
    vercel_site_url: str = "https://website2-umber-zeta.vercel.app/"
    app_owner_id: int = 0
    owner_id: int = 0
    required_role_id: int = 0
    discord_guild_id: str = ""
    all_logs_channel_id: int = 0
    verify_log_channel_id: int = 0
    port: int = 10000
    sio_app_port: int = 10000
    known_datacenters_file: str = "known_datacenters.json"
    dc_subscriptions_file: str = "dc_subscriptions.json"
    dc_bookmarks_file: str = "dc_bookmarks.json"
    dc_geo_cache_file: str = "dc_geo_cache.json"
    tracked_nodes_file: str = "tracked_datacenters.json"

    @property
    def is_configured(self) -> bool:
        return bool(self.discord_bot_token)


def load_settings() -> Settings:
    token = _get_env("DISCORD_BOT_TOKEN")
    if not token:
        raise RuntimeError("DISCORD_BOT_TOKEN is missing from environment variables.")

    settings = Settings(
        discord_bot_token=token,
        datacenter_alert_webhook_url=_get_env("DATACENTER_ALERT_WEBHOOK_URL", _get_env("WEBHOOK_URL", "")),
        vercel_site_url=_get_env("VERCEL_SITE_URL", "https://website2-umber-zeta.vercel.app/"),
        app_owner_id=_get_int_env("APP_OWNER_ID", 0),
        owner_id=_get_int_env("OWNER_ID", 0),
        required_role_id=_get_int_env("REQUIRED_ROLE_ID", 0),
        discord_guild_id=_get_env("DISCORD_GUILD_ID", ""),
        all_logs_channel_id=_get_int_env("ALL_LOGS_CHANNEL_ID", 0),
        verify_log_channel_id=_get_int_env("VERIFY_LOG_CHANNEL_ID", 0),
        port=_get_int_env("PORT", 10000),
        sio_app_port=_get_int_env("SIO_APP_PORT", 10000),
        known_datacenters_file=_get_env("KNOWN_DATACENTERS_FILE", "known_datacenters.json"),
        dc_subscriptions_file=_get_env("DC_SUBSCRIPTIONS_FILE", "dc_subscriptions.json"),
        dc_bookmarks_file=_get_env("DC_BOOKMARKS_FILE", "dc_bookmarks.json"),
        dc_geo_cache_file=_get_env("DC_GEO_CACHE_FILE", "dc_geo_cache.json"),
        tracked_nodes_file=_get_env("TRACKED_NODES_FILE", "tracked_datacenters.json"),
    )

    if not settings.datacenter_alert_webhook_url:
        raise RuntimeError("DATACENTER_ALERT_WEBHOOK_URL is missing from environment variables.")

    return settings


def ensure_working_directory(root: str | None = None) -> Path:
    base_dir = Path(root) if root else Path.cwd()
    base_dir.mkdir(parents=True, exist_ok=True)
    return base_dir
