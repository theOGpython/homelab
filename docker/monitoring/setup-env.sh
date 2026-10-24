#!/bin/bash
# Creates .env for the monitoring stack. Secrets are typed in hidden and never
# appear on screen or in shell history. .env is gitignored.
set -e
cd "$(dirname "$0")"

if [ -f .env ]; then
  read -rp ".env already exists. Overwrite? (y/N) " ans
  [ "$ans" = "y" ] || exit 0
fi

read -rp  "ODU address (e.g. 192.168.8.1): " ODU_IP
read -rp  "ODU username [admin]: " ODU_USER; ODU_USER=${ODU_USER:-admin}
read -rsp "ODU password: " ODU_PASS; echo
read -rsp "Tailscale auth key: " TSKEY; echo
read -rsp "Choose a Grafana admin password: " GFPASS; echo

cat > .env <<ENV
TZ=Africa/Lagos
CONFIG_ROOT=/opt/stacks
PROM_RETENTION=2y

ODU_URL=http://${ODU_IP}/
ODU_USERNAME=${ODU_USER}
ODU_PASSWORD=${ODU_PASS}

TS_AUTHKEY=${TSKEY}
GRAFANA_ADMIN_PASSWORD=${GFPASS}
ENV

chmod 600 .env
echo ".env created:"
sed -E 's/^(ODU_PASSWORD|TS_AUTHKEY|GRAFANA_ADMIN_PASSWORD)=.*/\1=***set***/' .env
