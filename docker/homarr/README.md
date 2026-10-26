# 🏠 Homarr: homelab dashboard

| | |
|---|---|
| Tailnet | `https://home.tailc33d1b.ts.net` |
| LAN | `http://192.168.3.201:7575` |

## Deploy

```bash
cd /opt/homelab && git pull
cd docker/homarr
bash setup-env.sh
docker compose up -d
```

Disable key expiry for the **home** machine in the Tailscale admin console.

## Adding apps

For each app, use the **Tailscale URL as the link** (works from anywhere) and the **LAN URL for integrations** (what Homarr itself connects to):

| App | Link (Tailscale) | Integration URL (LAN) |
|---|---|---|
| Jellyfin | `https://jellyfin.tailc33d1b.ts.net` | `http://192.168.3.201:8096` |
| Seerr | `https://requests.tailc33d1b.ts.net` | `http://192.168.3.201:5055` |
| Sonarr | `https://arr.tailc33d1b.ts.net:8989` | `http://192.168.3.201:8989` |
| Radarr | `https://arr.tailc33d1b.ts.net:7878` | `http://192.168.3.201:7878` |
| Prowlarr | `https://arr.tailc33d1b.ts.net:9696` | `http://192.168.3.201:9696` |
| qBittorrent | `https://arr.tailc33d1b.ts.net:8080` | `http://192.168.3.201:8080` |
| Bazarr | `https://arr.tailc33d1b.ts.net:6767` | n/a |
| Audiobookshelf | `https://books.tailc33d1b.ts.net` | n/a |
| Grafana | `https://grafana.tailc33d1b.ts.net` | n/a |
| n8n | `https://n8n.tailc33d1b.ts.net` | n/a |
| Proxmox | `https://pve.tailc33d1b.ts.net` | `https://192.168.3.200:8006` |

## Notes

- **Back up `SECRET_ENCRYPTION_KEY`.** It encrypts the API keys saved in integrations.
- **Docker integration is off** by default. Mounting the Docker socket gives Homarr full control of every container. Uncomment the line in `compose.yaml` only if you want container status/controls on the dashboard.
- For the Proxmox integration, create a **read-only API token**: Datacenter → Permissions → API Tokens → Add (user `root@pam`, token ID `homarr`, keep *Privilege Separation* ticked). Then Datacenter → Permissions → Add → **API Token Permission**: path `/`, token `root@pam!homarr`, role **PVEAuditor**.
