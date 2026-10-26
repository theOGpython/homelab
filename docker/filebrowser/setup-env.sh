#!/bin/bash
# Creates .env for FileBrowser Quantum and prepares folders. .env is gitignored.
set -e
cd "$(dirname "$0")"

if [ -f .env ]; then
  echo ".env already exists. Not overwriting."
  exit 1
fi

MEDIA_ENV=../media-stack/.env
if [ -f "$MEDIA_ENV" ] && grep -q '^TS_AUTHKEY=tskey-' "$MEDIA_ENV"; then
  TSKEY=$(grep '^TS_AUTHKEY=' "$MEDIA_ENV" | cut -d= -f2-)
  echo "Reusing Tailscale auth key from the media stack."
else
  read -rsp "Tailscale auth key: " TSKEY; echo
fi

ADMIN_PW=$(openssl rand -base64 18 | tr -d '/+=' | cut -c1-20)

cat > .env <<ENV
TZ=Africa/Lagos
CONFIG_ROOT=/opt/stacks
DATA_ROOT=/srv/data
TS_AUTHKEY=${TSKEY}
FILEBROWSER_ADMIN_PASSWORD=${ADMIN_PW}
ENV
chmod 600 .env

# Data folder must belong to uid 1000 (the container user)
mkdir -p /opt/stacks/filebrowser
chown -R 1000:1000 /opt/stacks/filebrowser
# Music folders for Jellyfin + Lidarr
mkdir -p /srv/data/media/music /srv/data/torrents/music
chown 1000:1000 /srv/data/media/music /srv/data/torrents/music

echo ".env created. Your FileBrowser login:"
echo "  username: admin"
echo "  password: ${ADMIN_PW}"
echo "Save this password in your Passwords app now."
