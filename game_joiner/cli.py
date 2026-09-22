from __future__ import annotations

import logging

from game_joiner.config import load_settings
from game_joiner.logging_setup import configure_logging

log = logging.getLogger("game_joiner.cli")


def main() -> None:
    configure_logging()
    settings = load_settings()
    log.info("Game Joiner initialized with bot token present: %s", bool(settings.discord_bot_token))
    print("Configuration loaded successfully.")
    print(f"Webhook configured: {bool(settings.datacenter_alert_webhook_url)}")


if __name__ == "__main__":
    main()
