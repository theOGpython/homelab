#!/bin/bash
# Nightly snapshot of Proxmox config into this repo (runs on the Proxmox host via cron).
set -e
REPO=/root/homelab
cd "$REPO"

# Pick up anything pushed from other machines first (e.g. edits made on the Mac)
git pull --rebase --autostash --quiet

mkdir -p pve/lxc pve/qemu-server host

# Proxmox container/VM definitions (removed ones get removed here too)
rsync -a --delete /etc/pve/lxc/ pve/lxc/
rsync -a --delete /etc/pve/qemu-server/ pve/qemu-server/
cp /etc/pve/storage.cfg pve/ 2>/dev/null || true

# Host network config
cp /etc/network/interfaces /etc/hosts host/

git add -A
git diff --cached --quiet || git commit -m "Auto-sync $(date '+%Y-%m-%d %H:%M')"
git push --quiet
