#!/usr/bin/env python3
"""
Aruba Central Skill — OpenClaw
Hybride : Classic Central REST (monitoring) + New Central REST (config)
Auth : OAuth2 refresh_token (Classic) + GreenLake SSO (New Central)
"""

import os, sys, json, argparse, time
from pathlib import Path
import requests
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

# ── Classic Central ───────────────────────────────────────────────────────────
CLASSIC_BASE  = os.getenv("CENTRAL_CLASSIC_BASE", "https://apigw-<your-cluster>.central.arubanetworks.com")
CLASSIC_ID    = os.getenv("CENTRAL_CLIENT_ID")
CLASSIC_SECRET= os.getenv("CENTRAL_CLIENT_SECRET")
CLASSIC_CACHE = Path(__file__).parent / ".classic_token.json"

# ── New Central (config) ──────────────────────────────────────────────────────
NEW_BASE      = os.getenv("CENTRAL_BASE_URL", "https://<your-cluster>.api.central.arubanetworks.com")
GL_CLIENT_ID  = os.getenv("CENTRAL_GL_CLIENT_ID")
GL_CLIENT_SEC = os.getenv("CENTRAL_GL_CLIENT_SECRET")
GL_CACHE      = Path(__file__).parent / ".gl_token.json"

# ── Auth Classic ──────────────────────────────────────────────────────────────

def get_classic_token() -> str:
    if CLASSIC_CACHE.exists():
        cache = json.loads(CLASSIC_CACHE.read_text())
        if cache.get("expires_at", 0) > time.time() + 60:
            return cache["access_token"]
        refresh = cache.get("refresh_token")
        if refresh:
            resp = requests.post(
                f"{CLASSIC_BASE}/oauth2/token",
                params={"client_id": CLASSIC_ID, "client_secret": CLASSIC_SECRET},
                data={"grant_type": "refresh_token", "refresh_token": refresh},
                timeout=10
            )
            if resp.ok:
                data = resp.json()
                data["expires_at"] = time.time() + data.get("expires_in", 7200) - 60
                CLASSIC_CACHE.write_text(json.dumps(data))
                return data["access_token"]
    static = os.getenv("CENTRAL_CLASSIC_TOKEN")
    static_refresh = os.getenv("CENTRAL_CLASSIC_REFRESH")
    if static:
        cache = {
            "access_token": static,
            "refresh_token": static_refresh,
            "expires_at": time.time() + 7200 - 60
        }
        CLASSIC_CACHE.write_text(json.dumps(cache))
        return static
    raise Exception("No Classic token available. Add CENTRAL_CLASSIC_TOKEN to .env")

# ── Auth GreenLake (New Central) ──────────────────────────────────────────────

def get_gl_token() -> str:
    if GL_CACHE.exists():
        cache = json.loads(GL_CACHE.read_text())
        if cache.get("expires_at", 0) > time.time() + 60:
            return cache["access_token"]
    resp = requests.post(
        "https://sso.common.cloud.hpe.com/as/token.oauth2",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "grant_type": "client_credentials",
            "client_id": GL_CLIENT_ID,
            "client_secret": GL_CLIENT_SEC,
        },
        timeout=10
    )
    resp.raise_for_status()
    data = resp.json()
    data["expires_at"] = time.time() + data.get("expires_in", 7200) - 60
    GL_CACHE.write_text(json.dumps(data))
    return data["access_token"]

# ── API helpers ───────────────────────────────────────────────────────────────

def classic_api(path: str, params: dict = None):
    headers = {"Authorization": f"Bearer {get_classic_token()}"}
    r = requests.get(f"{CLASSIC_BASE}{path}", headers=headers, params=params, timeout=15)
    r.raise_for_status()
    return r.json()

def new_api(path: str, params: dict = None):
    headers = {"Authorization": f"Bearer {get_gl_token()}"}
    r = requests.get(f"{NEW_BASE}{path}", headers=headers, params=params, timeout=15)
    r.raise_for_status()
    return r.json()

# ── Commands ──────────────────────────────────────────────────────────────────

def cmd_aps(args):
    params = {"calculate_total": True, "limit": 1000}
    if args.site:
        params["site"] = args.site
    data = classic_api("/monitoring/v2/aps", params)
    aps = data.get("aps", [])
    if args.search:
        s = args.search.lower()
        aps = [a for a in aps if s in a.get("name","").lower()
               or s in a.get("ip_address","").lower()
               or s in a.get("macaddr","").lower()]
    results = [{
        "name": a.get("name"),
        "model": a.get("model"),
        "status": a.get("status"),
        "ip": a.get("ip_address"),
        "mac": a.get("macaddr"),
        "group": a.get("group_name"),
        "site": a.get("site"),
        "firmware": a.get("firmware_version"),
        "clients": a.get("client_count", 0),
        "uptime": a.get("uptime"),
        "down_reason": a.get("down_reason"),
    } for a in aps]
    print(json.dumps(results, indent=2, ensure_ascii=False))

def cmd_switches(args):
    params = {"calculate_total": True, "limit": 1000}
    if args.site:
        params["site"] = args.site
    data = classic_api("/monitoring/v1/switches", params)
    switches = data.get("switches", [])
    if args.search:
        s = args.search.lower()
        switches = [sw for sw in switches if s in sw.get("name","").lower()
                    or s in sw.get("ip_address","").lower()]
    results = [{
        "name": sw.get("name"),
        "model": sw.get("model"),
        "status": sw.get("status"),
        "ip": sw.get("ip_address"),
        "mac": sw.get("macaddr"),
        "group": sw.get("group_name"),
        "site": sw.get("site"),
        "firmware": sw.get("firmware_version"),
        "uptime": sw.get("uptime"),
    } for sw in switches]
    print(json.dumps(results, indent=2, ensure_ascii=False))

def cmd_clients(args):
    params = {"calculate_total": True, "limit": 1000}
    if args.site:
        params["site"] = args.site
    data = classic_api("/monitoring/v2/clients", params)
    clients = data.get("clients", [])
    if args.search:
        s = args.search.lower()
        clients = [c for c in clients if
                   s in c.get("macaddr","").lower() or
                   s in c.get("ip_address","").lower() or
                   s in c.get("name","").lower()]
    results = [{
        "name": c.get("name"),
        "mac": c.get("macaddr"),
        "ip": c.get("ip_address"),
        "type": c.get("client_type"),
        "ssid": c.get("network"),
        "ap": c.get("associated_device"),
        "site": c.get("site"),
        "signal": c.get("signal_db"),
    } for c in clients]
    print(json.dumps(results, indent=2, ensure_ascii=False))

def cmd_sites(args):
    data = classic_api("/central/v2/sites")
    sites = data.get("sites", [])
    results = [{
        "id": s.get("site_id"),
        "name": s.get("site_name"),
        "address": s.get("address"),
        "city": s.get("city"),
        "country": s.get("country"),
        "devices": s.get("associated_device_count", 0),
    } for s in sites]
    print(json.dumps(results, indent=2, ensure_ascii=False))

def cmd_alerts(args):
    params = {"calculate_total": True, "limit": 100}
    data = classic_api("/central/v1/notifications", params)
    alerts = data.get("notifications", [])
    results = [{
        "id": a.get("id"),
        "severity": a.get("severity"),
        "type": a.get("alert_type"),
        "device": a.get("device_id"),
        "site": a.get("site_name"),
        "description": a.get("description"),
        "timestamp": a.get("timestamp"),
    } for a in alerts]
    print(json.dumps(results, indent=2, ensure_ascii=False))

def cmd_groups(args):
    data = new_api("/network-config/v1/device-groups")
    print(json.dumps(data.get("items", []), indent=2, ensure_ascii=False))

def cmd_stats(args):
    ap_data  = classic_api("/monitoring/v2/aps",      {"calculate_total": True, "limit": 1000})
    sw_data  = classic_api("/monitoring/v1/switches",  {"calculate_total": True, "limit": 1000})
    cli_data = classic_api("/monitoring/v2/clients",   {"calculate_total": True, "limit": 1})
    aps  = ap_data.get("aps", [])
    up   = sum(1 for a in aps if a.get("status") == "Up")
    down = sum(1 for a in aps if a.get("status") == "Down")
    print(json.dumps({
        "total_aps":      ap_data.get("total", 0),
        "aps_up":         up,
        "aps_down":       down,
        "total_switches": sw_data.get("total", 0),
        "total_clients":  cli_data.get("total", 0),
    }, indent=2, ensure_ascii=False))

def cmd_reboot(args):
    if not args.serial:
        print(json.dumps({"error": "--serial required"})); return
    headers = {"Authorization": f"Bearer {get_classic_token()}",
               "Content-Type": "application/json"}
    r = requests.post(
        f"{CLASSIC_BASE}/device_management/v2/device/{args.serial}/action/reboot",
        headers=headers, timeout=15
    )
    r.raise_for_status()
    print(json.dumps(r.json(), indent=2, ensure_ascii=False))

# ── Main ──────────────────────────────────────────────────────────────────────

COMMANDS = {
    "aps":      cmd_aps,
    "switches": cmd_switches,
    "clients":  cmd_clients,
    "sites":    cmd_sites,
    "alerts":   cmd_alerts,
    "groups":   cmd_groups,
    "stats":    cmd_stats,
    "reboot":   cmd_reboot,
}

def main():
    parser = argparse.ArgumentParser(description="Aruba Central Skill (Classic+New)")
    parser.add_argument("command", choices=COMMANDS.keys())
    parser.add_argument("--site",   help="Filter by site name")
    parser.add_argument("--search", help="Search by name/MAC/IP")
    parser.add_argument("--serial", help="Device serial number (reboot)")
    args = parser.parse_args()

    if not all([CLASSIC_ID, CLASSIC_SECRET]):
        print(json.dumps({"error": "CENTRAL_CLIENT_ID/SECRET missing in .env"}))
        sys.exit(1)

    try:
        COMMANDS[args.command](args)
    except requests.HTTPError as e:
        print(json.dumps({"error": str(e), "response": e.response.text}))
        sys.exit(1)
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)

if __name__ == "__main__":
    main()
