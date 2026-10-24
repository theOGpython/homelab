#!/bin/bash
set -e
REPO=/root/homelab
mkdir -p $REPO/pve/lxc $REPO/pve/qemu-server $REPO/host

# Proxmox container/VM definitions (removed ones get removed here too)
rsync -a --delete /etc/pve/lxc/ $REPO/pve/lxc/
rsync -a --delete /etc/pve/qemu-server/ $REPO/pve/qemu-server/
cp /etc/pve/storage.cfg $REPO/pve/ 2>/dev/null || true

# Host network config
cp /etc/network/interfaces /etc/hosts $REPO/host/

cd $REPO
git add -A
git diff --cached --quiet || git commit -m "Auto-sync $(date '+%Y-%m-%d %H:%M')"
git push
