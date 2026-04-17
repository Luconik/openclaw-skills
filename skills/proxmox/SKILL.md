---
name: proxmox
description: Monitor and manage Proxmox VE infrastructure via API. List VMs, containers, node status, storage across multiple nodes.
version: 1.1.0
metadata:
  openclaw:
    emoji: "🖥️"
    requires:
      env:
        - PVE_TOKEN
        - PVE1_TOKEN
        - PVE2_TOKEN
      bins:
        - python3
---

# Proxmox Skill

Monitor and manage Proxmox VE infrastructure via API.
Réponds toujours en français.

## Configuration

Node IPs are configured via environment variables (see `.env.example`).

## Execution

```bash
python3 {baseDir}/proxmox.py <command> [pve1|pve2] [vmid]
```

**Default: pve1** if no node specified.

## Commands

- `nodes` — cluster status (all nodes)
- `vms <node>` — list QEMU VMs
- `containers <node>` — list LXC containers
- `status <node>` — detailed node status
- `storage <node>` — storage status
- `vm <node> <vmid>` — specific VM status

## Examples

- "Quelles VMs tournent ?" → `python3 {baseDir}/proxmox.py vms pve1`
- "Conteneurs sur pve2 ?" → `python3 {baseDir}/proxmox.py containers pve2`
- "État du stockage pve1 ?" → `python3 {baseDir}/proxmox.py storage pve1`
- "État de la VM 101 ?" → `python3 {baseDir}/proxmox.py vm pve1 101`

## Rules

1. Si le node n'est pas précisé, utiliser pve1 par défaut.
2. Pour lister tous les nodes, utiliser `nodes pve1`.
3. Format Discord : résumé court + détails en bloc de code.
