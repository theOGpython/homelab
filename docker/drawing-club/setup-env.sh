#!/bin/bash
# Creates .env for Drawing Club and the drawings folder. .env is gitignored.
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
mkdir -p /srv/data/drawings
chown -R 1000:1000 /srv/data/drawings
echo ".env created and drawings folder ready."
