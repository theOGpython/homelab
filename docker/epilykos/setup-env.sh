#!/bin/bash
# Creates .env for Epilykos (random admin password, printed once) and its data folder.
set -e
cd "$(dirname "$0")"
[ -f .env ] && { echo ".env already exists. Not overwriting."; exit 1; }
MEDIA_ENV=../media-stack/.env
if [ -f "$MEDIA_ENV" ] && grep -q "^TS_AUTHKEY=tskey-" "$MEDIA_ENV"; then
  TSKEY=$(grep "^TS_AUTHKEY=" "$MEDIA_ENV" | cut -d= -f2-); echo "Reusing Tailscale auth key from the media stack."
else
  read -rsp "Tailscale auth key: " TSKEY; echo
fi
PW=$(openssl rand -hex 12)      # hex: no "$" characters to escape
cat > .env <<ENV
CONFIG_ROOT=/opt/stacks
TS_AUTHKEY=${TSKEY}
SETTINGS_PASSWORD=${PW}
# Pin a release once you've tried it, e.g. EPILYKOS_TAG=1.3.5 (check Docker Hub for exact tag names)
EPILYKOS_TAG=latest
ENV
chmod 600 .env
mkdir -p /opt/stacks/epilykos && chown -R 1000:1000 /opt/stacks/epilykos
echo
echo "Epilykos admin password (Settings / setup wizard): ${PW}"
echo "Save it in your Passwords app. To change it later, edit .env and run: docker compose up -d"
