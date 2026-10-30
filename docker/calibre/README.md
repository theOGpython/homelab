# 📚 Calibre-Web Automated: ebook library

| | |
|---|---|
| Tailnet | `https://ebooks.tailc33d1b.ts.net` |
| LAN | `http://192.168.3.201:8083` |
| Library | `/srv/data/media/books` |
| Ingest (drop zone) | `/srv/data/media/books-ingest` |

## Deploy

```bash
cd /opt/homelab && git pull
cd docker/calibre
bash setup-env.sh
docker compose up -d
```

Disable key expiry for the **ebooks** machine in Tailscale.

## First login

Default login is **admin / admin123**. Change it immediately: avatar → **Admin** → edit the admin user.

## Adding books

Upload EPUB/PDF/MOBI files into **books-ingest** using FileBrowser (`https://files.tailc33d1b.ts.net` → Media → books-ingest). CWA imports them within moments, fetches metadata and covers, and **deletes the uploaded copy** after importing. Settings for auto-convert (e.g. everything to EPUB) are on the **CWA Settings** page.

Never add or edit files directly in `books/`: it's a Calibre library with its own database.

## Reading on iPhone/iPad

Use the built-in web reader, or any OPDS reading app with: `https://ebooks.tailc33d1b.ts.net/opds` (log in with your CWA account).
