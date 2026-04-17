---
name: central
description: Manage HPE Aruba Central infrastructure. Monitor APs, switches, clients, sites, alerts via Classic Central REST API. Manage config groups via New Central REST API.
version: 2.0.0
metadata:
  openclaw:
    emoji: "🌐"
    requires:
      env:
        - CENTRAL_CLIENT_ID
        - CENTRAL_CLIENT_SECRET
        - CENTRAL_CLASSIC_TOKEN
      bins:
        - python3
    primaryEnv: CENTRAL_CLIENT_ID
---
# Aruba Central Skill (Hybride Classic + New Central)

Monitoring via Classic Central REST (`apigw-<cluster>.central.arubanetworks.com`).
Config via New Central REST (`<cluster>.api.central.arubanetworks.com`).

## Usage
```bash
python3 {baseDir}/central.py <command> [--site <name>] [--search <term>]
```

## Available Commands

### Stats globales
```bash
python3 {baseDir}/central.py stats
```
Returns: total APs, APs up/down, switches, clients.
**Appeler en premier pour un aperçu rapide.**

### Lister les APs
```bash
python3 {baseDir}/central.py aps [--site <name>] [--search <mac|ip|nom>]
```
Returns: nom, modèle, statut, IP, MAC, groupe, site, firmware, clients, down_reason.

### Lister les switches
```bash
python3 {baseDir}/central.py switches [--site <name>] [--search <nom|ip>]
```
Returns: nom, modèle, statut, IP, MAC, groupe, site, firmware.

### Lister les clients
```bash
python3 {baseDir}/central.py clients [--site <name>] [--search <mac|ip|nom>]
```
Returns: nom, MAC, IP, type, SSID, AP associé, site, signal.

### Lister les sites
```bash
python3 {baseDir}/central.py sites
```
Returns: id, nom, adresse, ville, pays, nombre de devices.

### Alertes / Notifications
```bash
python3 {baseDir}/central.py alerts
```
Returns: sévérité, type, device, site, description.

### Groupes de config (New Central)
```bash
python3 {baseDir}/central.py groups
```
Returns: groupes de configuration New Central avec deviceCount.

### Reboot un device — DESTRUCTIVE, confirmer avant
```bash
python3 {baseDir}/central.py reboot --serial <serial>
```

## Rules
1. **Toujours appeler `sites` si le nom de site est inconnu.**
2. **Actions destructives** (reboot) — confirmation explicite obligatoire.
3. **Format Discord** — résumé court + détails en bloc de code.
4. **Toujours répondre en français.**
5. **Monitoring = Classic Central** / **Config groups = New Central.**
6. **Token auto-renouvelé** via refresh_token Classic Central.
