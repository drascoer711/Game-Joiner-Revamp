# Game Joiner Revamp

A cleaner, more maintainable Discord automation and datacenter intelligence project built for Roblox infrastructure monitoring and moderation tooling.

## What this project does

- Tracks Roblox infrastructure datacenters and live server activity
- Monitors for datacenter and host-region changes
- Exposes a lightweight Discord command system for moderation, reporting, and lookups
- Keeps secrets and runtime configuration in environment variables instead of hardcoded values

## Quick start

1. Copy `.env.example` to `.env` and fill in the required values.
2. Install dependencies:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -U pip
   pip install -e .
   ```
3. Run the bot:
   ```bash
   python -m game_joiner
   ```

## Environment variables

See `.env.example` for the complete list. At minimum, set:

- `DISCORD_BOT_TOKEN`
- `DATACENTER_ALERT_WEBHOOK_URL`
- `APP_OWNER_ID`
- `REQUIRED_ROLE_ID`

## Project structure

```text
game_joiner/
  __init__.py
  __main__.py
  bot.py
  cli.py
  config.py
  logging_setup.py
  storage.py
  services/
    __init__.py
    roblox.py
    monitoring.py
```

## Architecture goals

- configuration is validated early and fails loudly
- runtime state is stored in JSON files, not embedded in code
- monitoring logic is separated from bot command logic
- network calls are isolated in service modules
- secrets stay outside source control

## Security

See `SECURITY.md` for the secret-handling policy and webhook rotation guidance.
