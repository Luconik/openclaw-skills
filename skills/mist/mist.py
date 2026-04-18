#!/usr/bin/env python3
import os
from pathlib import Path
_env = Path(__file__).parent / ".env"
if _env.exists():
    for _l in _env.read_text().splitlines():
        if "=" in _l and not _l.startswith("#"):
            k, v = _l.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())
import sys
import json
import argparse
import urllib.request
import urllib.error

API_TOKEN = os.environ.get("MIST_API_TOKEN", "")
DEFAULT_SITE_ID = os.environ.get("MIST_SITE_ID", "ca6b9086-6166-4aa6-be91-e91a8a985216")
BASE_API = "https://api.eu.mist.com/api/v1"


def api(method, path, body=None):
    url = BASE_API + path
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", f"Token {API_TOKEN}")
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        print(f"Error {e.code}: {e.read().decode()}")
        sys.exit(1)


def site_url(site_id):
    return f"/sites/{site_id}"


def cmd_sites():
    # Récupère l'org_id depuis le token
    me = api("GET", "/self")
    org_id = None
    if isinstance(me, dict):
        # Chercher dans les privilèges
        for priv in me.get("privileges", []):
            if priv.get("scope") == "org":
                org_id = priv.get("org_id")
                break
        if not org_id:
            org_id = me.get("org_id")

    if not org_id:
        print("❌ Could not determine org_id from token")
        sys.exit(1)

    sites = api("GET", f"/orgs/{org_id}/sites")
    if not sites:
        print("No sites found.")
        return
    for s in sites:
        print(f"Site: {s.get('name','?')} | ID: {s.get('id','?')} | "
              f"Country: {s.get('country_code','?')}")


def cmd_devices(site_id, device_type="all"):
    data = api("GET", f"{site_url(site_id)}/devices?type={device_type}")
    if not data:
        print("No devices found.")
        return
    for d in data:
        status = d.get("status", "unknown")
        print(f"[{status.upper()}] {d.get('name','?')} | {d.get('type','?')} | "
              f"{d.get('model','?')} | ID: {d.get('id','?')} | "
              f"MAC: {d.get('mac','?')} | IP: {d.get('ip','?')}")


def cmd_stats(site_id, device_id):
    data = api("GET", f"{site_url(site_id)}/stats/devices/{device_id}")
    print(json.dumps(data, indent=2))


def cmd_events(site_id, duration=60):
    data = api("GET", f"{site_url(site_id)}/events/fast?duration={duration}m")
    events = data.get("results", data) if isinstance(data, dict) else data
    for e in (events or [])[:20]:
        print(f"[{e.get('timestamp','')}] {e.get('type','?')} — "
              f"{e.get('ap_name', e.get('device_name','?'))}: {e.get('text','')}")


def cmd_wlans(site_id):
    data = api("GET", f"{site_url(site_id)}/wlans")
    if not data:
        print("No WLANs found.")
        return
    for w in data:
        print(f"SSID: {w.get('ssid','?')} | ID: {w.get('id','?')} | "
              f"Enabled: {w.get('enabled','?')} | Auth: {w.get('auth',{}).get('type','?')}")


def cmd_clients(site_id):
    data = api("GET", f"{site_url(site_id)}/stats/clients")
    clients = data.get("results", data) if isinstance(data, dict) else data
    if not clients:
        print("No clients connected.")
        return
    for c in clients:
        print(f"MAC: {c.get('mac','?')} | Host: {c.get('hostname','?')} | "
              f"AP: {c.get('ap_mac','?')} | SSID: {c.get('ssid','?')} | "
              f"RSSI: {c.get('rssi','?')} | IP: {c.get('ip','?')}")


def cmd_reboot(site_id, ap_id):
    api("POST", f"{site_url(site_id)}/devices/{ap_id}/reboot")
    print(f"✅ Reboot initiated for AP {ap_id}")


def cmd_bounce(site_id, switch_id, port_id):
    api("POST", f"{site_url(site_id)}/stats/devices/{switch_id}/bounce_port",
        {"port_id": port_id})
    print(f"✅ Port {port_id} bounced on switch {switch_id}")


def cmd_update_wlan(site_id, wlan_id, payload_str):
    payload = json.loads(payload_str)
    api("PUT", f"{site_url(site_id)}/wlans/{wlan_id}", payload)
    print(f"✅ WLAN {wlan_id} updated")


if __name__ == "__main__":
    if not API_TOKEN:
        print("❌ MIST_API_TOKEN not set")
        sys.exit(1)

    parser = argparse.ArgumentParser(description="Juniper Mist CLI")
    parser.add_argument("command", help="Command to run")
    parser.add_argument("extra", nargs="*", help="Command arguments")
    parser.add_argument("--site", default=DEFAULT_SITE_ID, help="Mist site ID")
    parser.add_argument("--type", choices=["ap", "switch", "all"],
                        default="all", dest="device_type",
                        help="Device type filter (for devices command)")
    args = parser.parse_args()

    site = args.site
    extra = args.extra
    cmd = args.command

    if cmd == "sites":
        cmd_sites()
    elif cmd == "devices":
        cmd_devices(site, args.device_type)
    elif cmd == "stats":
        if not extra:
            print("Usage: mist.py stats <device_id> [--site <site_id>]")
            sys.exit(1)
        cmd_stats(site, extra[0])
    elif cmd == "events":
        cmd_events(site, extra[0] if extra else 60)
    elif cmd == "wlans":
        cmd_wlans(site)
    elif cmd == "clients":
        cmd_clients(site)
    elif cmd == "reboot":
        if not extra:
            print("Usage: mist.py reboot <ap_id> [--site <site_id>]")
            sys.exit(1)
        cmd_reboot(site, extra[0])
    elif cmd == "bounce":
        if len(extra) < 2:
            print("Usage: mist.py bounce <switch_id> <port_id> [--site <site_id>]")
            sys.exit(1)
        cmd_bounce(site, extra[0], extra[1])
    elif cmd == "update-wlan":
        if len(extra) < 2:
            print("Usage: mist.py update-wlan <wlan_id> '<json>' [--site <site_id>]")
            sys.exit(1)
        cmd_update_wlan(site, extra[0], extra[1])
    else:
        print(f"Unknown command: {cmd}")
        print("Available: sites, devices, stats, events, wlans, clients, reboot, bounce, update-wlan")
        sys.exit(1)