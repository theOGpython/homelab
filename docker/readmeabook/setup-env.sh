#!/bin/bash
# Creates .env for ReadMeABook and its folders. .env is gitignored.
set -e
cd "$(dirname "$0")"
[ -f .env ] && { echo ".env already exists. Not overwriting."; exit 1; }
MEDIA_ENV=../media-stack/.env
if [ -f "$MEDIA_ENV" ] && grep -q "^TS_AUTHKEY=tskey-" "$MEDIA_ENV"; then
  TSKEY=$(grep "^TS_AUTHKEY=" "$MEDIA_ENV" | cut -d= -f2-); echo "Reusing Tailscale auth key from the media stack."
else
  read -rsp "Tailscale auth key: " TSKEY; echo
fi
cat > .env <<ENV
CONFIG_ROOT=/opt/stacks
DATA_ROOT=/srv/data
TS_TAILNET=tailc33d1b.ts.net
TS_AUTHKEY=${TSKEY}
# Pin a release once settled (check ghcr.io/kikootwo/readmeabook for exact tag names)
RMAB_TAG=latest
ENV
chmod 600 .env
mkdir -p /opt/stacks/readmeabook/{config,cache,pgdata,redis} /srv/data/torrents/audiobooks
chown -R 1000:1000 /opt/stacks/readmeabook/config /opt/stacks/readmeabook/cache /opt/stacks/readmeabook/redis /srv/data/torrents/audiobooks
echo ".env created. Next: docker compose up -d, then open https://audiobooks.tailc33d1b.ts.net for the setup wizard."
