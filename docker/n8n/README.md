# ⚙️ n8n: workflow automation

| | |
|---|---|
| Tailnet | `https://n8n.tailc33d1b.ts.net` |
| LAN | `http://192.168.3.201:5678` (login works best via the Tailscale HTTPS address) |

## Deploy

```bash
cd /opt/homelab && git pull
cd docker/n8n
bash setup-env.sh
docker compose up -d
```

Then disable key expiry for the **n8n** machine in the Tailscale admin console, open the Tailnet URL, and create the owner account.

## Important

- **Back up `N8N_ENCRYPTION_KEY`** (in `.env`) to your password manager. n8n encrypts every saved credential with it. If it's lost, all saved logins and API keys in your workflows are unrecoverable.
- **Webhooks are private.** The URL is only reachable from your tailnet. Services on the internet (e.g. Telegram, GitHub) can't call it. Polling triggers and schedules work fine. Public webhooks can be added later via Cloudflare Tunnel or Tailscale Funnel on a specific path.
- Data lives in Docker named volumes `n8n_n8n-data` and `n8n_postgres-data`.

## Reaching the other homelab services from n8n

n8n is on its own Docker network, so use the LXC's LAN address:

| Service | URL from inside n8n |
|---|---|
| Prometheus (ODU data) | `http://192.168.3.201:9090` |
| Sonarr / Radarr | `http://192.168.3.201:8989` / `:7878` |
| Jellyfin | `http://192.168.3.201:8096` |
| qBittorrent | `http://192.168.3.201:8080` |
