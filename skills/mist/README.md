# Mist Skill for OpenClaw

Manage Juniper Mist wireless infrastructure via the Mist Cloud API.

## Requirements

- Python 3
- `requests` library : `pip3 install requests --break-system-packages`
- A Mist API token (generate from Mist Cloud UI → My Profile → API Tokens)

## Configuration

```bash
cp .env.example .env
# Fill in MIST_API_TOKEN
```

Token format : alphanumeric string from api.eu.mist.com

## Commands

```bash
python3 mist.py sites
python3 mist.py devices [--site <site_id>] [--type ap|switch|all]
python3 mist.py stats <device_id> [--site <site_id>]
python3 mist.py events [duration_minutes] [--site <site_id>]
python3 mist.py wlans [--site <site_id>]
python3 mist.py clients [--site <site_id>]
python3 mist.py reboot <device_id> [--site <site_id>]
python3 mist.py bounce <device_id> <port> [--site <site_id>]
python3 mist.py update-wlan <wlan_id> '<json>' [--site <site_id>]
```

## Notes

- EU endpoint only : `api.eu.mist.com`
- Destructive actions (reboot, bounce, update-wlan) require explicit confirmation
- Default site via `MIST_SITE_ID` env var if `--site` not specified
