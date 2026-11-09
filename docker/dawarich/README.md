# 🗺️ Dawarich: location history

| | |
|---|---|
| Tailnet | `https://map.tailc33d1b.ts.net` |
| LAN | `http://192.168.3.201:3020` |

Self-hosted alternative to Google Maps Timeline: points, routes, trips, visits, stats, and photos on the map (via Immich).

## Deploy

```bash
cd /opt/homelab && git pull
cd docker/dawarich
bash setup-env.sh
docker compose up -d
docker compose logs -f dawarich_app     # first start runs database setup; wait until it settles
```

Disable key expiry for the **map** machine in Tailscale.

## First login

Sign in with the default account **demo@dawarich.app / password**, then immediately change the email and password (Settings → Account).

## Phone tracking

- Install the **Dawarich** app (iOS) or use **OwnTracks** / **Overland**.
- Server: `https://map.tailc33d1b.ts.net`; API key: Dawarich → Settings → API key.
- The phone must reach the server: keep **Tailscale connected** on the phone (enable *On Demand* in the Tailscale app).

## Immich (photos on the map)

Settings → Integrations → Immich: URL `http://192.168.3.201:2283` and an Immich API key.

## Importing past history

Google Timeline: export from the Google Maps app on your phone (Timeline settings → Export), then Dawarich → Imports. Large imports are processed in the background and can take a while on this server.

## Notes

- Pinned to **1.22.0**. Dawarich changes quickly: read release notes and back up before upgrading.
- Memory is capped at 2 GB. If big imports fail, raise `memory` in `compose.yaml`.
- Data lives in Docker named volumes (`dawarich_*`), covered by CT 201 backups.
