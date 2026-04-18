---
name: mist
description: Manage Juniper Mist wireless infrastructure. List sites, devices, clients, WLANs, get stats, view events, reboot APs, bounce switch ports, and update WLANs via the Mist Cloud API.
version: 1.2.0
metadata:
  openclaw:
    emoji: "📡"
    requires:
      env:
        - MIST_API_TOKEN
      bins:
        - python3
    primaryEnv: MIST_API_TOKEN
---

# Juniper Mist Skill

Manage Juniper Mist wireless infrastructure via the Mist Cloud API (api.eu.mist.com).

## Usage

```bash
python3 {baseDir}/mist.py <command> [args] [--site <site_id>] [--type <ap|switch|all>]
```

If no `--site` is provided, uses `MIST_SITE_ID` env var as default.

## Available Commands

### List available sites
```bash
python3 {baseDir}/mist.py sites
```
Returns: site name, site ID. **Call this if the user doesn't know the site ID.**

### List devices (APs and/or switches)
```bash
python3 {baseDir}/mist.py devices [--site <site_id>] [--type ap|switch|all]
```
Returns: ID, name, model, status, MAC, IP.
**Always call this first to get device IDs needed for other commands.**

### Get device stats
```bash
python3 {baseDir}/mist.py stats <device_id> [--site <site_id>]
```
Returns: uptime, clients, firmware, channel, TX/RX.

### Get site events
```bash
python3 {baseDir}/mist.py events [duration_minutes] [--site <site_id>]
```
Returns: recent AP down/up, interference events. Default: 60 min.

### List WLANs
```bash
python3 {baseDir}/mist.py wlans [--site <site_id>]
```
Returns: WLAN ID, SSID, enabled status, auth type.

### List connected clients
```bash
python3 {baseDir}/mist.py clients [--site <site_id>]
```
Returns: MAC, hostname, AP, SSID, RSSI, IP.

### Reboot AP — DESTRUCTIVE, confirm before executing
```bash
python3 {baseDir}/mist.py reboot <ap_id> [--site <site_id>]
```

### Bounce switch port — DESTRUCTIVE, confirm before executing
```bash
python3 {baseDir}/mist.py bounce <switch_id> <port_id> [--site <site_id>]
```
Port format: ge-0/0/1

### Update WLAN — DESTRUCTIVE, confirm before executing
```bash
python3 {baseDir}/mist.py update-wlan <wlan_id> '<json_payload>' [--site <site_id>]
```
Example: `'{"enabled": false}'`

## Rules

1. **NEVER assume device IDs** — always run `devices` first.
2. **Unknown site ID** — run `sites` to list available sites before asking the user.
3. **Destructive actions** (reboot, bounce, update-wlan) require explicit user confirmation.
4. **Format output** for Discord: short summary + technical details in code block.
5. **Always respond in the user's language.**
6. **EU endpoint only** — always use `api.eu.mist.com`, never `api.mist.com`.