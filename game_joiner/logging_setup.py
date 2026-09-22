from __future__ import annotations

import logging

logger = logging.getLogger("game_joiner")


def configure_logging(level: int = 20) -> None:
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


__all__ = ["logger", "configure_logging"]
