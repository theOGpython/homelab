#!/bin/bash
# =============================================================================
# Update Docker stacks in CT 201: pull newer images, rebuild local images,
# recreate changed containers, remove old images. Data (volumes/folders) untouched.
#
#   bash /opt/homelab/scripts/update-stacks.sh              # all stacks
#   bash /opt/homelab/scripts/update-stacks.sh immich n8n   # only these
#
# Pinned versions (Immich v3, Nextcloud 33, Dawarich, ...) stay pinned: bump those
# by editing their files after reading the release notes.
# Take a snapshot first (Proxmox host):  pct snapshot 201 before-updates
# =============================================================================
set -u
ROOT=/opt/homelab/docker
MIN_FREE_GB=5
SKIP="${SKIP:-}"            # e.g. SKIP="octo dawarich" bash update-stacks.sh

free_gb() { df -BG --output=avail / | tail -1 | tr -dc '0-9'; }

if [ "$(free_gb)" -lt "$MIN_FREE_GB" ]; then
  echo "Only $(free_gb) GB free on / (need ${MIN_FREE_GB}). Free space first: docker image prune -a -f"; exit 1
fi

if [ $# -gt 0 ]; then STACKS="$*"; else STACKS=$(ls -1 "$ROOT"); fi

updated=(); unchanged=(); failed=()
for name in $STACKS; do
  dir="$ROOT/$name"
  [ -d "$dir" ] || { echo "skip $name (no such stack)"; continue; }
  found=false
  for f in compose.yaml docker-compose.yml docker-compose.yaml; do [ -f "$dir/$f" ] && found=true; done
  $found || continue
  [ -f "$dir/.env" ] || { echo "skip $name (not deployed: no .env)"; continue; }
  case " $SKIP " in *" $name "*) echo "skip $name (SKIP)"; continue;; esac

  echo; echo "=== $name ($(free_gb) GB free)"
  cd "$dir" || continue
  before=$(docker compose images -q 2>/dev/null | sort | tr '\n' ' ')
  if ! docker compose pull --ignore-buildable 2>&1 | grep -v -E "^\s*$" | tail -5; then failed+=("$name (pull)"); continue; fi
  if grep -q -E "^\s+build:" compose.yaml 2>/dev/null; then
    docker compose build --pull 2>&1 | tail -3 || { failed+=("$name (build)"); continue; }
  fi
  if ! docker compose up -d --remove-orphans 2>&1 | tail -5; then failed+=("$name (up)"); continue; fi
  after=$(docker compose images -q 2>/dev/null | sort | tr '\n' ' ')
  if [ "$before" != "$after" ]; then updated+=("$name"); else unchanged+=("$name"); fi
  docker image prune -f >/dev/null 2>&1          # drop the images just replaced
done

echo; echo "================ summary ($(free_gb) GB free)"
echo "updated:   ${updated[*]:-none}"
echo "unchanged: ${unchanged[*]:-none}"
echo "failed:    ${failed[*]:-none}"
[ ${#failed[@]} -eq 0 ] || exit 1
