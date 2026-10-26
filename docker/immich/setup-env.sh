#!/bin/bash
# Creates .env for Immich: random database password, reuses the Tailscale key
# from the media stack. .env is gitignored.
set -e
cd "$(dirname "$0")"

if [ -f .env ]; then
  echo ".env already exists. Not overwriting (it holds your database password)."
  exit 1
fi

MEDIA_ENV=../media-stack/.env
if [ -f "$MEDIA_ENV" ] && grep -q '^TS_AUTHKEY=tskey-' "$MEDIA_ENV"; then
  TSKEY=$(grep '^TS_AUTHKEY=' "$MEDIA_ENV" | cut -d= -f2-)
  echo "Reusing Tailscale auth key from the media stack."
else
  read -rsp "Tailscale auth key: " TSKEY; echo
fi

cat > .env <<ENV
TZ=Africa/Lagos
CONFIG_ROOT=/opt/stacks
TS_AUTHKEY=${TSKEY}

# Immich (official settings)
IMMICH_VERSION=v3
UPLOAD_LOCATION=/srv/photos/library
DB_DATA_LOCATION=/opt/stacks/immich/postgres
DB_PASSWORD=$(openssl rand -hex 16)
DB_USERNAME=postgres
DB_DATABASE_NAME=immich
ENV

chmod 600 .env
mkdir -p /srv/photos/library /opt/stacks/immich/postgres
echo ".env created:"
sed -E 's/^(TS_AUTHKEY|DB_PASSWORD)=.*/\1=***set***/' .env
