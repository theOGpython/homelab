# 📄 Stirling PDF: private PDF toolkit

| | |
|---|---|
| Tailnet | `https://pdf.tailc33d1b.ts.net` |
| LAN | `http://192.168.3.201:8095` |

Merge, split, compress, OCR, convert, sign, redact: files are processed on this server and never leave the home network.

## Deploy

```bash
cd /opt/homelab && git pull
cd docker/stirling-pdf
bash setup-env.sh
docker compose up -d
```

The image is large (well over 1 GB); check space first with `df -h /`. Disable key expiry for the **pdf** machine in Tailscale.

## Notes

- No login by default: it's only reachable on the LAN and tailnet.
- Memory is capped at 1.5 GB so a big conversion can't starve other services. Raise `mem_limit` if large OCR jobs fail.
