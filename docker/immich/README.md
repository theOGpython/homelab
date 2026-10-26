# 📸 Immich: family photo backup

| | |
|---|---|
| Tailnet | `https://photos.tailc33d1b.ts.net` |
| LAN | `http://192.168.3.201:2283` |
| Photos | `/srv/photos/library` (own 100 GB disk, `mp1`) |
| Database | `/opt/stacks/immich/postgres` (system disk) |

## Before deploying (Proxmox, container 201)

1. **Resources → Add → Mount Point**: `local-lvm`, **100 GB**, path `/srv/photos`
2. **Resources → Memory**: 10240 MB
3. **Resources → Cores**: 4 (if the CPU has 4)

## Deploy

```bash
cd /opt/homelab && git pull
cd docker/immich
bash setup-env.sh
docker compose up -d
```

Disable key expiry for the **photos** machine in the Tailscale admin console.

## First-run settings

- Create the admin account at `http://192.168.3.201:2283`.
- **Administration → Settings → Video Transcoding → Hardware Acceleration → Quick Sync**, then save.
- Machine learning runs on the CPU. The first scan of a large library keeps the CPU busy for hours; that's normal.

## iPhone app

Server URL: `https://photos.tailc33d1b.ts.net`. In the app's **Settings → Networking**, enable automatic URL switching: use `http://192.168.3.201:2283` when on the home Wi-Fi, so big backups go over the LAN and never through the internet.

## ⚠️ Important

- **Don't delete photos from your phone** until Proxmox backups of `/srv/photos` are running. Immich must not hold the only copy.
- **Read the release notes before every update.** Immich sometimes requires manual steps between versions. `IMMICH_VERSION` in `.env` controls the version.
- Never edit files in `/srv/photos/library` by hand; Immich tracks them in its database.
