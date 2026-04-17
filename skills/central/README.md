# openclaw-skills

> Collection de skills Python pour [OpenClaw](https://openclaw.ai) — agent IA local piloté via Discord.

Chaque skill expose des commandes en langage naturel pour interroger et piloter une infrastructure réseau ou IT sans ouvrir de console.

```
Discord : "@bakaopenclaw stats central"
    │
    ▼
OpenClaw (gemma4:e4b, RTX 3060)
    │
    ├── skill/central  → HPE Aruba Central REST API
    ├── skill/mist     → Juniper Mist Cloud API
    └── skill/proxmox  → Proxmox VE API
```

## Skills disponibles

| Skill | Version | Description |
|-------|---------|-------------|
| [central](./skills/central/) | v2.0 | HPE Aruba Central — monitoring APs, switches, clients + config groupes |
| [mist](./skills/mist/) | v1.2 | Juniper Mist — APs, switches, clients, WLANs, events |
| [proxmox](./skills/proxmox/) | v1.0 | Proxmox VE — VMs, containers, nodes, storage |

## Plateforme

Développé et testé sur **Bakastation** :

| Composant | Détail |
|-----------|--------|
| OS | Fedora 43 bare metal |
| CPU | Intel i9-10850K |
| RAM | 128 GB |
| GPU | NVIDIA RTX 3060 12GB (driver 570, CUDA 12.8) |
| LLM | gemma4:e4b via Ollama (43/43 layers GPU, ~75 t/s) |
| OpenClaw | openclaw-gateway (systemd user service) |

## Installation

### 1. Cloner le repo

```bash
git clone https://github.com/Luconik/openclaw-skills.git
cd openclaw-skills
```

### 2. Installer les dépendances Python

```bash
pip3 install python-dotenv requests --break-system-packages
```

### 3. Copier les skills dans OpenClaw

```bash
cp -r skills/central ~/.openclaw/workspace/skills/
cp -r skills/mist    ~/.openclaw/workspace/skills/
cp -r skills/proxmox ~/.openclaw/workspace/skills/
```

### 4. Configurer les credentials

Chaque skill dispose d'un `.env.example` à copier et remplir :

```bash
cp skills/central/.env.example skills/central/.env
# Éditer .env avec vos credentials
```

### 5. Mettre à jour le SOUL.md

Ajouter les skills dans `~/.openclaw/workspace/SOUL.md` en suivant les exemples dans chaque `SKILL.md`.

### 6. Redémarrer OpenClaw

```bash
systemctl --user restart openclaw-gateway
```

## Structure du repo

```
openclaw-skills/
├── README.md
├── skills/
│   ├── central/
│   │   ├── central.py       # Script principal
│   │   ├── SKILL.md         # Instructions OpenClaw
│   │   ├── .env.example     # Template credentials
│   │   └── README.md        # Documentation complète
│   ├── mist/
│   │   ├── mist.py
│   │   ├── SKILL.md
│   │   ├── .env.example
│   │   └── README.md
│   └── proxmox/
│       ├── proxmox.py
│       ├── SKILL.md
│       ├── .env.example
│       └── README.md
└── docs/
    └── bakastation-setup.md  # Installation OpenClaw sur Fedora 43
```

## Sécurité

- Les fichiers `.env` sont exclus du repo via `.gitignore`
- Ne jamais committer de tokens ou credentials
- Les `.env.example` contiennent uniquement des placeholders

## Liens

- [OpenClaw](https://openclaw.ai)
- [HPE Aruba Developer Hub](https://developer.arubanetworks.com)
- [Juniper Mist API](https://api.mist.com)
- [homelab-setup](https://github.com/Luconik/homelab-setup) — Infrastructure bakastation
- [netdevops](https://github.com/Luconik/netdevops) — Ansible, Terraform, Containerlab HPE Aruba

## Auteur

Nicolas Culetto — Channel Presales Consultant, HPE Aruba Networking  
[LinkedIn](https://linkedin.com/in/nicolasculetto) · [GitHub](https://github.com/Luconik)
