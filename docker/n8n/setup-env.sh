#!/bin/bash
# Creates .env for n8n. Generates strong secrets automatically and reuses the
# Tailscale auth key from the media stack if present. .env is gitignored.
set -e
cd "$(dirname "$0")"

if [ -f .env ]; then
  echo ".env already exists. Not overwriting (it holds your encryption key)."
  echo "Delete it manually only if you're starting from scratch."
  exit 1
fi

MEDIA_ENV=../media-stack/.env
if [ -f "$MEDIA_ENV" ] && grep -q '^TS_AUTHKEY=tskey-' "$MEDIA_ENV"; then
  TSKEY=$(grep '^TS_AUTHKEY=' "$MEDIA_ENV" | cut -d= -f2-)
  echo "Reusing Tailscale auth key from the media stack."
else
  read -rsp "Tailscale auth key: " TSKEY; echo
fi

read -rp "Tailnet name [tailc33d1b.ts.net]: " TAILNET; TAILNET=${TAILNET:-tailc33d1b.ts.net}

cat > .env <<ENV
TZ=Africa/Lagos
CONFIG_ROOT=/opt/stacks
TS_TAILNET=${TAILNET}
TS_AUTHKEY=${TSKEY}
POSTGRES_PASSWORD=$(openssl rand -hex 24)
N8N_ENCRYPTION_KEY=$(openssl rand -hex 32)
ENV

chmod 600 .env
echo ".env created:"
sed -E 's/^(TS_AUTHKEY|POSTGRES_PASSWORD|N8N_ENCRYPTION_KEY)=.*/\1=***set***/' .env
echo
echo "IMPORTANT: back up N8N_ENCRYPTION_KEY somewhere safe (e.g. your password manager):"
echo "  grep N8N_ENCRYPTION_KEY $(pwd)/.env"
