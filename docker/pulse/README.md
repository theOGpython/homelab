# 📈 Pulse: Proxmox & Docker monitoring

| | |
|---|---|
| Tailnet | `https://pulse.tailc33d1b.ts.net` |
| LAN | `http://192.168.3.201:7655` |

Health, metric history, storage, backup coverage and Docker containers for the homelab,
with Telegram alerts. Pinned to `v6.9.0` (`PULSE_IMAGE` in `.env`).

## Deploy
```bash
cd /opt/homelab && git pull
cd docker/pulse && bash setup-env.sh && docker compose up -d
docker exec pulse /app/pulse bootstrap-token      # paste this into the first-run page
```
Disable key expiry for the **pulse** machine in Tailscale.

## Proxmox (read-only token), on the Proxmox host
```bash
pveum user add pulse-monitor@pve --comment "Pulse monitoring (read-only)"
pveum role add PulseMonitor -privs "Sys.Audit,VM.GuestAgent.Audit,Datastore.Audit"
pveum acl modify / --users pulse-monitor@pve --roles PVEAuditor
pveum acl modify / --users pulse-monitor@pve --roles PulseMonitor
pveum user token add pulse-monitor@pve pulse --privsep 0
```
Pulse → Settings → Proxmox → Add: `https://192.168.3.200:8006`, token ID `pulse-monitor@pve!pulse` + secret.

## Docker agent (CT 201)
Pulse → **Settings → Infrastructure → Install on a host** → copy the command (Pulse URL
`http://192.168.3.201:7655`) → run it in CT 201.

## Alerts (Telegram)
Settings → Alerts → Notifications → **Telegram** (bot token + chat ID from `docker/n8n/.env`).
Suggested thresholds: storage pool `local-lvm` warn 80% / critical 90%; CT 201 disk 85% / 95%;
backups older than 36 h (once nightly backups run).
