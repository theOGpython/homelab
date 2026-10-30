# 🧭 Homepage: config-as-code dashboard

| | |
|---|---|
| Tailnet | `https://homepage.tailc33d1b.ts.net` |
| LAN | `http://192.168.3.201:3010` |

The whole dashboard is defined in `config/*.yaml` (versioned in Git). Secrets live in `homepage.secret` (gitignored) and are referenced as `{{HOMEPAGE_VAR_...}}`.

## Deploy

```bash
cd /opt/homelab && git pull
cd docker/homepage
bash setup-env.sh
nano homepage.secret      # paste API keys (can be done gradually)
docker compose up -d
```

Disable key expiry for the **homepage** machine in Tailscale.

## Where each key comes from

| Variable | Where to find it |
|---|---|
| `JELLYFIN_KEY` | Jellyfin → Dashboard → API Keys → + |
| `SEERR_KEY` | Seerr → Settings → General → API Key |
| `AUDIOBOOKSHELF_KEY` | Audiobookshelf → Settings → Users → your user → API token |
| `IMMICH_KEY` | Immich → Account Settings → API Keys → New |
| `SONARR/RADARR/LIDARR/PROWLARR/BAZARR_KEY` | each app → Settings → General → API Key |
| `QBIT_USER/PASS` | your qBittorrent login |
| `CALIBRE_USER/PASS` | your Calibre-Web login |
| `HASS_TOKEN` | Home Assistant → your profile → Security → Long-lived access tokens |
| `PROXMOX_TOKEN_ID/SECRET` | Proxmox → Datacenter → Permissions → API Tokens (read-only `PVEAuditor`, ID like `root@pam!homepage`) |
| `KUMA_SLUG` | the slug of an Uptime Kuma status page |

After editing secrets: `docker compose up -d --force-recreate homepage`.
After editing YAML in Git: `git pull` (Homepage reloads config automatically).

## Notes

- If the page shows a **host validation** error, the address you used must be listed in `HOMEPAGE_ALLOWED_HOSTS` in `compose.yaml`.
- Edit `config/widgets.yaml` to set your own weather coordinates.
- Homepage writes logs to `config/logs/` on the server; that folder isn't committed.
