# 🎧 ReadMeABook: audiobook requests → Audiobookshelf

| | |
|---|---|
| Tailnet | `https://audiobooks.tailc33d1b.ts.net` |
| LAN | `http://192.168.3.201:3050` |
| Library | `/srv/data/media/audiobooks` (Audiobookshelf) |

"Radarr/Sonarr + Overseerr for audiobooks": browse an Audible-backed catalog, request, and RMAB
searches Prowlarr, downloads with qBittorrent, then copies clean, tagged books into Audiobookshelf.
Replaces the two Bookshelf instances. LazyLibrarian stays for ebooks.

## Deploy
```bash
cd /opt/homelab && git pull
cd docker/readmeabook && bash setup-env.sh && docker compose up -d
docker compose logs -f readmeabook      # first start initialises its database
```
Disable key expiry for the **audiobooks** machine in Tailscale.

## Setup wizard (first visit)
| Step | Value |
|---|---|
| Admin account | your own username + password |
| Media server | **Audiobookshelf**: `http://192.168.3.201:13378` + an Audiobookshelf API key; library: your audiobooks library |
| Library path | `/data/media/audiobooks` |
| Prowlarr | `http://192.168.3.201:9696` + Prowlarr API key; tick indexers that carry audiobooks |
| Download client | **qBittorrent** `http://192.168.3.201:8080`, your login; category `audiobooks`, save path `/data/torrents/audiobooks` |
| Audible region | United Kingdom or United States (English stores match best) |
| Ebooks | leave off (LazyLibrarian handles ebooks) |

Use `/path-helper` in RMAB if it can't see finished downloads.

## Telegram
Settings → API → create an `rmab_` token → `RMAB_TOKEN=` in `docker/n8n/.env`, recreate n8n,
import `audiobooks-ready.json` (messages when a book is ready or a request fails).
