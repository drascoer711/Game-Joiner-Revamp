from __future__ import annotations

import asyncio
import logging

from game_joiner.config import load_settings
from game_joiner.logging_setup import configure_logging
from game_joiner.bot import GameJoinerBot, build_tree


logger = logging.getLogger("game_joiner")


async def main() -> None:
    configure_logging()
    settings = load_settings()
    bot = GameJoinerBot(settings)
    build_tree(bot)
    try:
        await bot.start(settings.discord_bot_token)
    except KeyboardInterrupt:
        logger.info("Shutting down gracefully.")
        await bot.close()


if __name__ == "__main__":
    asyncio.run(main())
