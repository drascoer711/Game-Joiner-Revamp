# Security and secrets

Keep all live secrets and webhook URLs in environment variables only.

## Required policy

- Never commit a real `.env` file.
- Never hardcode tokens, webhooks, or Discord IDs in source files.
- Rotate any webhook URL that is ever pasted into a chat, issue, or ticket.
- Use `.env.example` as the approved template for local setup.

## Recommended setup

Copy `.env.example` to `.env` and populate the values on your local machine or platform host only.

## Discord webhook guidance

If a webhook URL is exposed in chat or logs, treat it as compromised and create a new one immediately.

Use environment variables such as:

- `DATACENTER_ALERT_WEBHOOK_URL`
- `DISCORD_BOT_TOKEN`
