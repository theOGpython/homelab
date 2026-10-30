#!/bin/bash
# Creates .env (Tailscale) and homepage.secret (API keys template).
# Both are gitignored (.env and *.secret).
set -e
cd "$(dirname "$0")"
[ -f .env ] && { echo ".env already exists. Not overwriting."; exit 1; }

MEDIA_ENV=../media-stack/.env
if [ -f "$MEDIA_ENV" ] && grep -q "^TS_AUTHKEY=tskey-" "$MEDIA_ENV"; then
  TSKEY=$(grep "^TS_AUTHKEY=" "$MEDIA_ENV" | cut -d= -f2-)
  echo "Reusing Tailscale auth key from the media stack."
else
  read -rsp "Tailscale auth key: " TSKEY; echo
fi

cat > .env <<ENV
TZ=Africa/Lagos
CONFIG_ROOT=/opt/stacks
TS_TAILNET=tailc33d1b.ts.net
TS_AUTHKEY=${TSKEY}
ENV
chmod 600 .env

if [ ! -f homepage.secret ]; then
cat > homepage.secret <<'SECRETS'
# Fill these in, then: docker compose up -d --force-recreate homepage
# Widgets with an empty value just show an error until filled.
HOMEPAGE_VAR_JELLYFIN_KEY=
HOMEPAGE_VAR_SEERR_KEY=
HOMEPAGE_VAR_AUDIOBOOKSHELF_KEY=
HOMEPAGE_VAR_IMMICH_KEY=
HOMEPAGE_VAR_CALIBRE_USER=
HOMEPAGE_VAR_CALIBRE_PASS=
HOMEPAGE_VAR_SONARR_KEY=
HOMEPAGE_VAR_RADARR_KEY=
HOMEPAGE_VAR_LIDARR_KEY=
HOMEPAGE_VAR_PROWLARR_KEY=
HOMEPAGE_VAR_BAZARR_KEY=
HOMEPAGE_VAR_QBIT_USER=
HOMEPAGE_VAR_QBIT_PASS=
HOMEPAGE_VAR_HASS_TOKEN=
HOMEPAGE_VAR_PROXMOX_TOKEN_ID=
HOMEPAGE_VAR_PROXMOX_TOKEN_SECRET=
HOMEPAGE_VAR_KUMA_SLUG=
SECRETS
chmod 600 homepage.secret
fi
echo ".env and homepage.secret created. Next: nano homepage.secret"
