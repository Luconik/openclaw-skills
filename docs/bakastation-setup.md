# OpenClaw — Installation sur Bakastation

> Agent IA local piloté via Discord, tournant sur Fedora 43 bare metal avec Ollama + GPU NVIDIA.

## Architecture

```
Discord (#homelab, #mist-alerts)
        │
        ▼
openclaw-gateway (systemd user service)
        │
        ├── Ollama (gemma4:e4b, RTX 3060 12GB, 100% GPU)
        ├── Skill Mist     → ~/.openclaw/workspace/skills/mist/
        ├── Skill Proxmox  → ~/.openclaw/workspace/skills/proxmox/
        ├── Skill Central  → ~/.openclaw/workspace/skills/central/
        └── SOUL.md        → ~/.openclaw/workspace/SOUL.md
```

## Prérequis

- Fedora 43 bare metal
- NVIDIA RTX 3060 12GB (driver 570, CUDA 12.8)
- Ollama ≥ 0.20.3 natif
- Node.js v24+
- Python 3.14+
- Discord Bot Token

## Installation Ollama avec support GPU

```bash
# Installer Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Configurer le service systemd avec support GPU
sudo systemctl edit ollama
```

Contenu du override :

```ini
[Service]
Environment="LD_LIBRARY_PATH=/usr/lib64:/usr/local/lib/ollama/cuda_v13"
Environment="OLLAMA_GPU_LAYERS=999"
Environment="OLLAMA_KEEP_ALIVE=-1"
Environment="OLLAMA_NUM_PARALLEL=2"
Environment="OLLAMA_FLASH_ATTENTION=1"
Environment="OLLAMA_MODELS=/mnt/ollama"
Environment="OLLAMA_HOST=0.0.0.0:11434"
```

```bash
sudo systemctl daemon-reload && sudo systemctl restart ollama

# Vérifier que le GPU est bien utilisé
ollama run gemma4:e4b "test" --verbose 2>&1 | grep -E "layers|GPU"
# Attendu : offloaded 43/43 layers to GPU
```

## Installation OpenClaw

```bash
# Installer openclaw-gateway
npm install -g openclaw-gateway

# Créer le service systemd utilisateur
mkdir -p ~/.config/systemd/user/openclaw-gateway.service.d

# Créer le fichier de service
cat > ~/.config/systemd/user/openclaw-gateway.service << 'EOF'
[Unit]
Description=OpenClaw Gateway
After=network-online.target

[Service]
ExecStart=/usr/local/bin/openclaw-gateway
Restart=on-failure
RestartSec=5

[Install]
WantedBy=default.target
EOF

systemctl --user daemon-reload
systemctl --user enable --now openclaw-gateway
```

## Configuration openclaw.json

Fichier : `~/.openclaw/openclaw.json`

```json
{
  "model": "ollama/gemma4:e4b",
  "ollama": {
    "baseUrl": "http://127.0.0.1:11434"
  },
  "auth": {
    "mode": "none"
  },
  "gateway": {
    "allowTailscale": true,
    "trustedProxies": ["127.0.0.1"],
    "controlUi": {
      "allowInsecureAuth": true
    }
  },
  "session": {
    "reset": {
      "idleMinutes": 30
    }
  },
  "discord": {
    "token": "VOTRE_BOT_TOKEN",
    "allowedChannels": ["homelab", "mist-alerts"]
  },
  "skills": {
    "install": {
      "nodeManager": "npm"
    },
    "entries": {
      "mist": {
        "enabled": true,
        "env": {
          "MIST_API_TOKEN": "VOTRE_TOKEN_MIST"
        }
      },
      "proxmox": {
        "enabled": true,
        "env": {}
      },
      "central": {
        "enabled": true,
        "env": {
          "CENTRAL_CLIENT_ID": "VOTRE_CLIENT_ID",
          "CENTRAL_CLIENT_SECRET": "VOTRE_CLIENT_SECRET",
          "CENTRAL_CLASSIC_TOKEN": "VOTRE_TOKEN_CLASSIC",
          "CENTRAL_CLASSIC_REFRESH": "VOTRE_REFRESH_TOKEN",
          "CENTRAL_CLASSIC_BASE": "https://apigw-eucentral2.central.arubanetworks.com",
          "CENTRAL_BASE_URL": "https://de2.api.central.arubanetworks.com",
          "CENTRAL_GL_CLIENT_ID": "VOTRE_GL_CLIENT_ID",
          "CENTRAL_GL_CLIENT_SECRET": "VOTRE_GL_CLIENT_SECRET"
        }
      }
    }
  }
}
```

## SOUL.md

Fichier : `~/.openclaw/workspace/SOUL.md`

Ce fichier définit la personnalité et les capacités de l'agent. Il référence les skills disponibles et leurs commandes. Voir le README de chaque skill pour la syntaxe complète.

Exemple minimal :

```markdown
Tu réponds TOUJOURS en français, sans exception.
Tu es BakaOpenClaw, l'assistant IA de Nico sur Discord.
Tu gères l'infrastructure homelab (Proxmox, n8n) et le réseau (Mist, Aruba Central).

## Skills disponibles
**Aruba Central** :
python3 ~/.openclaw/workspace/skills/central/central.py [stats|aps|switches|clients|sites|alerts|groups]

**Juniper Mist** :
python3 ~/.openclaw/workspace/skills/mist/mist.py [sites|devices|stats|events|clients]

## Règles
- Exécute les commandes sans demander de clarification
- Actions destructives : demander confirmation explicite
- Format Discord : résumé court + détails en bloc de code
```

## Gestion du service

```bash
# Statut
systemctl --user status openclaw-gateway

# Redémarrer (après modification openclaw.json ou SOUL.md)
systemctl --user restart openclaw-gateway

# Logs en temps réel
journalctl --user -u openclaw-gateway -f

# Logs dans /tmp
tail -f /tmp/openclaw/openclaw-$(date +%Y-%m-%d).log
```

## Vérification GPU Ollama

```bash
# Pendant une génération, dans un second terminal
nvidia-smi dmon -s pucvmt -d 1
# Colonnes attendues : sm ~90%, mem ~76%, fb ~9845MB, pwr ~163W
```

## Performances observées

| Métrique | Valeur |
|----------|--------|
| Modèle | gemma4:e4b (9.6GB Q4_K_M) |
| GPU layers | 43/43 |
| eval rate | ~75 t/s |
| prompt eval rate | ~1289 t/s |
| VRAM utilisée | ~9.8 GB / 12 GB |
