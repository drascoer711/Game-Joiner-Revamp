from __future__ import annotations

import asyncio
import logging
from typing import Any

import discord
from discord import app_commands
from discord.ext import commands

from game_joiner.config import load_settings
from game_joiner.services.monitoring import DatacenterRegistry, TARGET_PLACE_IDS, send_discord_alert
from game_joiner.services.roblox import fetch_all_active_servers, resolve_server_ip_and_region

logger = logging.getLogger("game_joiner.bot")


class RequiredRoleError(app_commands.CheckFailure):
    pass


class GameJoinerBot(commands.Bot):
    def __init__(self, settings: Any):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        super().__init__(command_prefix="!", intents=intents)
        self.settings = settings
        self.registry = DatacenterRegistry(settings)

    async def setup_hook(self) -> None:
        if self.settings.discord_guild_id:
            guild = discord.Object(id=int(self.settings.discord_guild_id))
            self.tree.copy_global_to(guild=guild)
        try:
            synced = await self.tree.sync(guild=guild if self.settings.discord_guild_id else None)
            logger.info("Synced %d commands to Discord", len(synced))
        except Exception as exc:  # pragma: no cover
            logger.warning("Failed to sync commands: %s", exc)

    async def on_ready(self) -> None:
        logger.info("Bot online as %s", self.user)


async def check_access(interaction: discord.Interaction) -> bool:
    settings = load_settings()
    if settings.app_owner_id and interaction.user.id == settings.app_owner_id:
        return True
    if settings.required_role_id and any(role.id == settings.required_role_id for role in getattr(interaction.user, "roles", [])):
        return True
    raise RequiredRoleError("You need the required bot access role to use this command.")


async def create_bot() -> GameJoinerBot:
    settings = load_settings()
    bot = GameJoinerBot(settings)
    return bot


def build_tree(bot: GameJoinerBot) -> None:
    @bot.tree.command(name="stats", description="Show tracked infrastructure statistics.")
    @app_commands.check(check_access)
    async def stats(interaction: discord.Interaction):
        tracked = bot.registry.get_tracked()
        embed = discord.Embed(title="Infrastructure Stats", color=0x5865F2)
        embed.add_field(name="Tracked datacenters", value=str(len(tracked)), inline=True)
        embed.add_field(name="Unique cities", value=str(len({v.get('city', 'Unknown') for v in tracked.values()})), inline=True)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @bot.tree.command(name="processdc", description="Register a datacenter manually.")
    @app_commands.describe(city="Datacenter city", ip="Public infrastructure IP")
    @app_commands.check(check_access)
    async def processdc(interaction: discord.Interaction, city: str, ip: str):
        registered, dcid = bot.registry.register(city.strip(), ip.strip(), source="manual")
        title = "Datacenter Registered" if registered else "Already Known"
        description = f"Registered **{city}** as `{dcid}`." if registered else f"`{dcid}` is already present in the index."
        embed = discord.Embed(title=title, description=description, color=0x57F287 if registered else 0xFEE75C)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @bot.tree.command(name="findnewhost", description="Scan for newer infrastructure regions.")
    @app_commands.check(check_access)
    async def findnewhost(interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True, thinking=True)
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
            found: list[str] = []
            for place_id in TARGET_PLACE_IDS[:2]:
                servers = await fetch_all_active_servers(place_id, session, max_pages=2)
                for server in servers[:10]:
                    job_id = server.get("id")
                    if not job_id:
                        continue
                    region = await resolve_server_ip_and_region(session, place_id, job_id)
                    if not region:
                        continue
                    city = region["city"]
                    ip = region["ip"]
                    registered, dcid = bot.registry.register(city, ip, source="scan")
                    if registered:
                        found.append(dcid)
            summary = f"Found {len(found)} new datacenter node(s)." if found else "No new datacenter nodes were discovered in this scan." 
            await interaction.followup.send(summary, ephemeral=True)


async def start_bot() -> GameJoinerBot:
    settings = load_settings()
    bot = await create_bot()
    build_tree(bot)
    await bot.start(settings.discord_bot_token)
    return bot


if __name__ == "__main__":
    import asyncio
    import aiohttp

    asyncio.run(start_bot())
