#!/bin/bash
# Creates .env for Calibre-Web Automated and prepares folders. .env is gitignored.
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
DATA_ROOT=/srv/data
TS_AUTHKEY=${TSKEY}
ENV
chmod 600 .env

mkdir -p /opt/stacks/calibre/config /srv/data/media/books /srv/data/media/books-ingest
chown -R 1000:1000 /opt/stacks/calibre /srv/data/media/books /srv/data/media/books-ingest
echo ".env created and folders ready."
