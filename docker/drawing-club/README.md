# 🖍️ Drawing Club

Step-by-step animal drawing for kids: follow a tutorial, draw it on a tablet/phone/computer, and keep the drawings.

| | |
|---|---|
| Tailnet | `https://draw.tailc33d1b.ts.net` |
| LAN | `http://192.168.3.201:8097` |
| Saved drawings | `/srv/data/drawings` (PNG files) |

## Deploy

```bash
cd /opt/homelab && git pull
cd docker/drawing-club
bash setup-env.sh
docker compose up -d --build
```

Disable key expiry for the **draw** machine in Tailscale. On a tablet or phone, open the address in Safari → **Share → Add to Home Screen** so it opens like an app.

## What's inside

- **11 original tutorials** in three levels (Easy peasy, A bit trickier, Big challenge): snake, spider, owl, mouse, cat, elephant, frog, ladybug, rabbit, pig, giraffe. Each step adds one shape, drawn in orange so it's clear what's new.
- **Drawing canvas:** finger, stylus or mouse; 8 crayons, 3 line sizes, eraser, undo; optional light guide outline to trace.
- **Free drawing** with a blank page.
- **My drawings:** saved on the server, viewable from any device.

## Adding an animal

Tutorials live in `app/public/index.html` in the `ANIMALS` list. Each step is a sentence plus shapes on a 300 × 300 grid:
`E(cx, cy, rx, ry)` oval, `C(cx, cy, r)` circle, `D(cx, cy, r)` filled dot, `P('path')` line/curve, `L(x1, y1, x2, y2)` straight line. Add `'scene'` as the last argument for background items (drawn in green).

After editing: `git pull` then `docker compose up -d --build`.

## Notes

- Tutorials are original drawings made for this app; no third-party images are used.
- Private to your tailnet. To share publicly later, the app is static enough to also run on Cloudflare Pages (without the gallery).
