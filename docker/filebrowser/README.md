# 📁 FileBrowser Quantum: upload files to the media library

| | |
|---|---|
| Tailnet | `https://files.tailc33d1b.ts.net` |
| LAN | `http://192.168.3.201:8099` |
| Serves | `/srv/data/media` only (movies, tv, music, audiobooks, podcasts) |

## Deploy

```bash
cd /opt/homelab && git pull
cd docker/filebrowser
bash setup-env.sh          # prints the admin password: save it
docker compose up -d
```

Disable key expiry for the **files** machine in the Tailscale admin console.

## Using it

- Drag folders from Finder into the right library folder (e.g. `music/Artist/Album`).
- Then rescan the library in Jellyfin or Audiobookshelf (or wait for the scheduled scan).
- Files uploaded here are owned by uid 1000, like the rest of the media.

## Notes

- **Immich photos are not exposed here on purpose.** Immich tracks its files in a database; editing them by hand breaks it.
- Pinned to Quantum's **1.x stable** line (`gtstef/filebrowser:1-stable`). Version 2.0 changes the config format; follow the official migration guide before switching.
- Quantum validates `config.yaml` strictly. If the container won't start after an edit, check `docker compose logs filebrowser`.
