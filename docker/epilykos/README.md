# ⚡ Epilykos: solar & battery dashboard

| | |
|---|---|
| Dashboard (public on the tailnet) | `https://energy.tailc33d1b.ts.net` |
| Settings / Editor (password) | `/settings` · `/editor` |
| LAN | `http://192.168.3.201:3040` |

Real-time energy dashboard by [ashipaek0/epilykos](https://github.com/ashipaek0/epilykos) (GPL-3.0): flow diagram, gauges, battery runtime, solar forecast, prices & savings, prepaid meter tracking, notifications. Installs on a phone as an app (PWA).

## Deploy

```bash
cd /opt/homelab && git pull
cd docker/epilykos
bash setup-env.sh        # prints the admin password once: save it
docker compose up -d
```

Disable key expiry for the **energy** machine in Tailscale.

## First-run setup (`/setup`)

1. Enter the admin password from setup-env.sh.
2. **Data source → Inverter dongle → Felicity (TCP)**: host `192.168.3.119`, port `53970`.
3. Battery: **LiFePO4, 25.6 V, 200 Ah (5.12 kWh)**, reserve 20%. Solar: **2.2 kWp**. Inverter: **3 kW**.
4. Prices: grid **₦209.50/kWh + 7.5% VAT** (≈ ₦225.21), generator ₦750/kWh, currency NGN.
5. Forecast: location Lagos (Surulere).

## Notes

- Runs alongside `felicity-exporter` (Grafana, Home Assistant, n8n). Both poll the dongle; if Epilykos
  shows connection errors, switch its source to **REST API** with `http://192.168.3.201:9878/json`.
- Bluetooth, USB serial and Tuya options from upstream are not enabled (not needed here).
- Pin a version (`EPILYKOS_TAG`) once you've settled on a release.
