# Game Joiner Revamp

A cleaner, more maintainable Discord + Roblox infrastructure monitoring toolkit.

## Highlights

- environment-driven configuration
- datacenter tracking and scan workflows
- modular service structure
- detection-first monitoring logic
- security-conscious configuration and webhook handling

## Quick start

1. Copy `.env.example` to `.env`.
2. Fill in the required values.
3. Create a virtual environment and install dependencies.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -e .
```

4. Start the bot:

```bash
python -m game_joiner
```

## Environment variables

See `.env.example` for the required values. At minimum, configure:

- `DISCORD_BOT_TOKEN`
- `DATACENTER_ALERT_WEBHOOK_URL`
- `APP_OWNER_ID`
- `REQUIRED_ROLE_ID`

## Project layout

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
    monitoring.py
    roblox.py
```

## Security

This project never stores live secrets in source code. See `SECURITY.md` for the webhook-rotation and `.env` guidance.
