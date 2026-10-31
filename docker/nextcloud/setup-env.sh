#!/bin/bash
# Creates .env for Nextcloud (random DB + admin passwords) and its data folder.
set -e
cd "$(dirname "$0")"
[ -f .env ] && { echo ".env already exists. Not overwriting (it holds your passwords)."; exit 1; }

MEDIA_ENV=../media-stack/.env
if [ -f "$MEDIA_ENV" ] && grep -q "^TS_AUTHKEY=tskey-" "$MEDIA_ENV"; then
  TSKEY=$(grep "^TS_AUTHKEY=" "$MEDIA_ENV" | cut -d= -f2-)
  echo "Reusing Tailscale auth key from the media stack."
else
  read -rsp "Tailscale auth key: " TSKEY; echo
fi

ADMIN_PW=$(openssl rand -base64 18 | tr -d '/+=' | cut -c1-20)

cat > .env <<ENV
TZ=Africa/Lagos
CONFIG_ROOT=/opt/stacks
DATA_ROOT=/srv/data
TS_TAILNET=tailc33d1b.ts.net
TS_AUTHKEY=${TSKEY}
POSTGRES_PASSWORD=$(openssl rand -hex 24)
NEXTCLOUD_ADMIN_USER=admin
NEXTCLOUD_ADMIN_PASSWORD=${ADMIN_PW}
ENV
chmod 600 .env

# Nextcloud's data folder must belong to www-data (uid 33)
mkdir -p /srv/data/nextcloud
chown -R 33:33 /srv/data/nextcloud
chmod 770 /srv/data/nextcloud

echo ".env created. Your Nextcloud login:"
echo "  username: admin"
echo "  password: ${ADMIN_PW}"
echo "Save this password in your Passwords app now."
