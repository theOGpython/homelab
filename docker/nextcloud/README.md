# ☁️ Nextcloud: files, calendar, contacts

| | |
|---|---|
| Tailnet | `https://cloud.tailc33d1b.ts.net` (use this one) |
| LAN | `http://192.168.3.201:8091` (troubleshooting only) |
| Files | `/srv/data/nextcloud` (owned by uid 33) |

## Deploy

```bash
cd /opt/homelab && git pull
cd docker/nextcloud
bash setup-env.sh          # prints the admin password: save it
docker compose up -d
docker compose logs -f nextcloud   # first start installs Nextcloud: wait for "apache2 -D FOREGROUND"
```

Disable key expiry for the **cloud** machine in Tailscale.

## After first login

- **Administration settings → Overview:** fix any warnings shown.
- **Administration settings → Basic settings → Background jobs:** select **Cron** (the `nc-cron` container runs them).
- Phone: install the **Nextcloud** app; server `https://cloud.tailc33d1b.ts.net`.

## Upgrades: read before changing the version

Nextcloud can only upgrade **one major version at a time** (33 → 34 → 35). To upgrade, change `33-apache` to `34-apache` in `compose.yaml`, then `docker compose pull && docker compose up -d`. Never skip a major version.

## Notes

- Use the Tailscale address: Nextcloud is set to generate `https://cloud...` links, so the plain LAN address may misbehave.
- For photos, keep using **Immich**; Nextcloud is best for documents, file sync, calendar, and contacts.
- Never edit files in `/srv/data/nextcloud` directly; Nextcloud tracks them in its database.
