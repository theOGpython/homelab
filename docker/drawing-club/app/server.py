"""
Drawing Club: tiny web server (Python standard library only).

Serves the app (public/index.html) and stores saved drawings as PNG files.

  GET    /                      the app
  GET    /api/drawings          list saved drawings (newest first)
  POST   /api/drawings          save {animal, image: "data:image/png;base64,..."}
  DELETE /api/drawings/<file>   delete one drawing
  GET    /drawings/<file>       a saved drawing
  GET    /healthz               health check
"""
import base64
import json
import mimetypes
import os
import re
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse

DRAWINGS = Path(os.environ.get("DATA_DIR", "/data")) / "drawings"
PUBLIC = Path(__file__).parent / "public"
PORT = int(os.environ.get("PORT", "8000"))
MAX_PNG_BYTES = 8 * 1024 * 1024
NAME_RE = re.compile(r"^\d{13}_[a-z-]{1,30}\.png$")
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
DATA_URL_PREFIX = "data:image/png;base64,"


def entry(name):
    stamp, animal = name[:-4].split("_", 1)
    return {"file": name, "url": f"/drawings/{name}", "animal": animal, "created": int(stamp)}


class Handler(BaseHTTPRequestHandler):
    server_version = "DrawingClub/1.0"

    def log_message(self, fmt, *args):
        print(f"{self.address_string()} {fmt % args}", flush=True)

    # ---- helpers ----
    def _send(self, code, body, ctype, cache="no-store"):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", cache)
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(body)

    def _json(self, code, obj):
        self._send(code, json.dumps(obj).encode(), "application/json")

    def _path(self):
        return unquote(urlparse(self.path).path)

    # ---- routes ----
    def do_GET(self):
        path = self._path()
        if path in ("/", "/index.html"):
            return self._send(200, (PUBLIC / "index.html").read_bytes(), "text/html; charset=utf-8", "no-cache")
        if path == "/healthz":
            return self._json(200, {"ok": True})
        if path == "/api/drawings":
            names = sorted((p.name for p in DRAWINGS.glob("*.png") if NAME_RE.match(p.name)), reverse=True)
            return self._json(200, [entry(n) for n in names])
        if path.startswith("/drawings/"):
            name = path[len("/drawings/"):]
            file = DRAWINGS / name
            if NAME_RE.match(name) and file.is_file():
                return self._send(200, file.read_bytes(), "image/png", "public, max-age=31536000, immutable")
        self._json(404, {"error": "Not found"})

    def do_POST(self):
        if self._path() != "/api/drawings":
            return self._json(404, {"error": "Not found"})
        length = int(self.headers.get("Content-Length") or 0)
        if length <= 0 or length > MAX_PNG_BYTES * 2:
            return self._json(413, {"error": "Drawing is too large to save"})
        try:
            payload = json.loads(self.rfile.read(length))
            image = str(payload.get("image", ""))
            if not image.startswith(DATA_URL_PREFIX):
                raise ValueError("not a PNG")
            raw = base64.b64decode(image[len(DATA_URL_PREFIX):], validate=True)
            if not raw.startswith(PNG_SIGNATURE) or len(raw) > MAX_PNG_BYTES:
                raise ValueError("bad PNG")
        except (ValueError, json.JSONDecodeError):
            return self._json(400, {"error": "That didn't look like a drawing"})
        animal = re.sub(r"[^a-z-]", "", str(payload.get("animal", "free")).lower())[:30] or "free"
        name = f"{int(time.time() * 1000)}_{animal}.png"
        tmp = DRAWINGS / f".{name}.tmp"
        tmp.write_bytes(raw)
        tmp.rename(DRAWINGS / name)
        self._json(201, entry(name))

    def do_DELETE(self):
        path = self._path()
        prefix = "/api/drawings/"
        name = path[len(prefix):] if path.startswith(prefix) else ""
        file = DRAWINGS / name
        if not NAME_RE.match(name) or not file.is_file():
            return self._json(404, {"error": "Drawing not found"})
        file.unlink()
        self._json(200, {"deleted": name})


if __name__ == "__main__":
    DRAWINGS.mkdir(parents=True, exist_ok=True)
    print(f"Drawing Club listening on :{PORT}, saving to {DRAWINGS}", flush=True)
    ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
