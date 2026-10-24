# 📶 Monitoring: home internet usage

Tracks household data usage, speed, and 5G signal from the Airtel ODU (Huawei H362-383).

```
Huawei ODU ──(local API, every 60s)──▶ odu-exporter ──▶ Prometheus ──▶ Grafana
```

| Service | LAN | Tailnet |
|---|---|---|
| Grafana | `http://192.168.3.201:3000` | `https://grafana.<tailnet>.ts.net` |
| Prometheus | `http://192.168.3.201:9090` | (LAN/subnet router only) |
| Exporter metrics | inside Docker only (`odu-exporter:9877`) | none |

Polling happens entirely on the home network, so it uses **no internet data**.

## Deploy

```bash
cd /opt/homelab && git pull
cd docker/monitoring
./setup-env.sh                 # asks for ODU address/password, Tailscale key, Grafana password
docker compose up -d --build
```

Then disable key expiry for the new **grafana** machine in the Tailscale admin console.

## Check it's working

| Check | How |
|---|---|
| Exporter can log into the ODU | `docker compose logs odu-exporter --tail 20` (no "Poll failed" lines) |
| Prometheus is collecting | `http://192.168.3.201:9090/targets`: `odu` job is **UP** |
| Dashboard | Grafana → **Home Internet (Airtel ODU)** |

## Dashboard panels

- **Used today / This billing period**: the ODU's own counters (should match its web page)
- **Daily usage (30 days)** and **Hourly usage (48h)**: calculated from lifetime counters, so history survives ODU reboots and counter resets
- **Throughput**: live download/upload speed
- **5G / 4G signal**: RSRP (strength) and SINR (quality)
- **ODU reachable**: gaps show power cuts, ODU reboots, or the exporter being locked out

## Notes

- The ODU allows limited login sessions. While someone is logged into its web page, polls may fail briefly. That shows as a dip in "ODU reachable", and no data is lost: the lifetime counters catch up on the next successful poll.
- Daily bars are UTC days, i.e. 1am–1am Lagos time.
- Data lives in Docker named volumes (`monitoring_prometheus-data`, `monitoring_grafana-data`) inside the docker LXC, so it's covered by LXC backups.
- Dashboard edits made in the UI are kept, but the JSON in this repo is the source of truth. Export changes back to `grafana/dashboards/home-internet.json` to version them.
