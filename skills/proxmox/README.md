# Skill Proxmox — OpenClaw

Monitor and manage Proxmox VE infrastructure via API.

## Prérequis

```bash
pip3 install requests --break-system-packages
```

## Configuration .env

```bash
cp .env.example .env
# Remplir PVE1_HOST, PVE1_TOKEN, PVE2_HOST, PVE2_TOKEN
```

Token format : `USER@REALM!TOKENID=UUID`
Créer dans Proxmox UI : Datacenter → Permissions → API Tokens

## Commandes

```bash
python3 proxmox.py nodes [pve1|pve2]
python3 proxmox.py vms pve1
python3 proxmox.py containers pve2
python3 proxmox.py status pve1
python3 proxmox.py storage pve1
python3 proxmox.py vm pve1 101
```

## Notes

- SSL auto-signé Proxmox : warnings désactivés via urllib3
- Default node : pve1 si non spécifié
- IPs configurées via variables d'environnement uniquement
