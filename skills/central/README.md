# Skill Aruba Central — OpenClaw

> Skill hybride Classic Central (monitoring) + New Central (config) pour OpenClaw.

## Vue d'ensemble

| API | Usage | Endpoint |
|-----|-------|----------|
| Classic Central REST | Monitoring (APs, switches, clients, alertes) | `apigw-<cluster>.central.arubanetworks.com` |
| New Central REST | Config (groupes, hiérarchie) | `<cluster>.api.central.arubanetworks.com` |
| New Central GraphQL | Monitoring temps réel | Session browser uniquement — non supporté |

> **Note :** New Central est en beta. Classic Central reste en production jusqu'en septembre 2025.

## Prérequis

```bash
pip3 install python-dotenv requests --break-system-packages
```

## Commandes

```bash
python3 central.py stats
python3 central.py aps [--site <n>] [--search <term>]
python3 central.py switches [--site <n>]
python3 central.py clients [--site <n>] [--search <term>]
python3 central.py sites
python3 central.py alerts
python3 central.py groups
python3 central.py reboot --serial <serial>
```

## Authentification

- Classic Central : refresh_token auto, bootstrap via CENTRAL_CLASSIC_TOKEN
- GreenLake : client_credentials auto, token 2h

## Limitations

- Monitoring New Central = GraphQL uniquement — non supporté
- Token Classic refresh_token expire en 30j — régénération manuelle si expiré
- Rate limiting Classic Central : 7 appels/seconde
