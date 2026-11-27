#!/bin/bash
# Creates .env for Pulse. .env is gitignored.
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
TS_AUTHKEY=${TSKEY}
# Pinned release; read the release notes before bumping
PULSE_IMAGE=rcourtman/pulse:v6.9.0
ENV
chmod 600 .env
echo ".env created. Next: docker compose up -d && docker exec pulse /app/pulse bootstrap-token"
