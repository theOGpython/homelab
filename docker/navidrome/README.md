# 🎵 Navidrome: music server

| | |
|---|---|
| Tailnet | `https://music.tailc33d1b.ts.net` |
| LAN | `http://192.168.3.201:4533` |
| Music | `/srv/data/media/music` (read-only; same folder as Jellyfin/Lidarr) |

## Deploy

```bash
cd /opt/homelab && git pull
cd docker/navidrome
bash setup-env.sh
docker compose up -d
```

Open the address and **create the admin account** (the first user becomes admin). Disable key expiry for the **music** machine in Tailscale.

## iPhone

Any Subsonic app works. **Amperfy** (free) supports offline downloads and CarPlay. Server: `https://music.tailc33d1b.ts.net`, with your Navidrome username and password.

Download albums on Wi-Fi to listen offline without using mobile data.

## Notes

- Library rescans hourly; trigger one manually from the activity icon (top right).
- Pinned to v0.64.2. Check release notes before bumping the version.
