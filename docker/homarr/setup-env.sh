#!/bin/bash
# Creates .env for Homarr. Generates the encryption key and reuses the
# Tailscale auth key from the media stack. .env is gitignored.
set -e
cd "$(dirname "$0")"

if [ -f .env ]; then
  echo ".env already exists. Not overwriting (it holds your encryption key)."
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
SECRET_ENCRYPTION_KEY=$(openssl rand -hex 32)
ENV

chmod 600 .env
echo ".env created:"
sed -E 's/^(TS_AUTHKEY|SECRET_ENCRYPTION_KEY)=.*/\1=***set***/' .env
echo
echo "Back up SECRET_ENCRYPTION_KEY to your password manager:"
echo "  grep SECRET_ENCRYPTION_KEY $(pwd)/.env"
