"""
Prometheus exporter for a Felicity inverter (tested on IVEM3024) via its
WiFi dongle's local TCP/JSON protocol on port 53970. No cloud involved.

Protocol (as used by github.com/fabiomatavelli/ha-felicity-solar-local):
send the ASCII command "wifilocalMonitor:get dev real infor", read one JSON object.

Scaling was verified against the FSolar app:
  voltages x0.1 (battery x0.001), currents x0.1, SOC x0.01, frequency x0.01,
  temperatures x0.1, battery power negative = discharging.

Endpoints:  /metrics  (Prometheus)     /json  (scaled values, for Home Assistant)
"""
import json
import logging
import os
import socket
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from prometheus_client import CONTENT_TYPE_LATEST, Gauge, generate_latest

HOST = os.environ.get("INVERTER_HOST", "192.168.3.119")
PORT = int(os.environ.get("INVERTER_PORT", "53970"))
POLL_SECONDS = int(os.environ.get("POLL_SECONDS", "15"))
LISTEN_PORT = int(os.environ.get("EXPORTER_PORT", "9878"))
QUERY = b"wifilocalMonitor:get dev real infor"
# Battery facts the inverter doesn't report (set in .env)
BATTERY_CAPACITY_WH = float(os.environ.get("BATTERY_CAPACITY_WH", "5120"))
BATTERY_RESERVE_PERCENT = float(os.environ.get("BATTERY_RESERVE_PERCENT", "20"))
INVERTER_OVERHEAD_W = float(os.environ.get("INVERTER_OVERHEAD_W", "100"))
# Electricity price, for valuing solar and costing grid use (EKEDC Band A by default)
TARIFF_NGN_PER_KWH = float(os.environ.get("TARIFF_NGN_PER_KWH", "209.50"))
TARIFF_VAT_PERCENT = float(os.environ.get("TARIFF_VAT_PERCENT", "7.5"))
STATE_FILE = os.environ.get("STATE_FILE", "/state/energy.json")
MAX_GAP_SECONDS = 120   # don't count energy across long polling gaps

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("felicity-exporter")

G = {
    "up": Gauge("felicity_up", "1 if the last poll of the inverter succeeded"),
    "last_success": Gauge("felicity_last_success_timestamp_seconds", "Unix time of last successful poll"),
    "pv_voltage": Gauge("felicity_pv_voltage_volts", "Solar input voltage"),
    "pv_current": Gauge("felicity_pv_current_amps", "Solar input current"),
    "pv_power": Gauge("felicity_pv_power_watts", "Solar input power"),
    "bat_voltage": Gauge("felicity_battery_voltage_volts", "Battery voltage"),
    "bat_current": Gauge("felicity_battery_current_amps", "Battery current (negative = discharging)"),
    "bat_power": Gauge("felicity_battery_power_watts", "Battery power (negative = discharging, positive = charging)"),
    "bat_soc": Gauge("felicity_battery_soc_percent", "Battery state of charge"),
    "bat_temp": Gauge("felicity_battery_temperature_celsius", "Battery temperature"),
    "out_voltage": Gauge("felicity_output_voltage_volts", "AC output voltage"),
    "out_current": Gauge("felicity_output_current_amps", "AC output current"),
    "out_freq": Gauge("felicity_output_frequency_hertz", "AC output frequency"),
    "load_power": Gauge("felicity_load_power_watts", "House load (AC output active power)"),
    "load_va": Gauge("felicity_load_apparent_power_va", "AC output apparent power"),
    "grid_voltage": Gauge("felicity_grid_voltage_volts", "Grid input voltage (0 = grid off)"),
    "grid_present": Gauge("felicity_grid_present", "1 if grid power is present, else 0"),
    "bus_voltage": Gauge("felicity_bus_voltage_volts", "Internal DC bus voltage"),
    "temp": Gauge("felicity_temperature_celsius", "Inverter internal temperatures", ["sensor"]),
    "warn": Gauge("felicity_warning_code", "Warning code (0 = none)"),
    "fault": Gauge("felicity_fault_code", "Fault code (0 = none)"),
    "work_mode": Gauge("felicity_work_mode", "Raw work mode code"),
    "load_percent_raw": Gauge("felicity_load_percent_raw", "Raw lPerc field (meaning unconfirmed)"),
    "cfg_capacity": Gauge("felicity_battery_capacity_wh", "Configured usable battery capacity (Wh)"),
    "cfg_reserve": Gauge("felicity_battery_reserve_percent", "Configured SOC at which the inverter stops discharging"),
    "cfg_overhead": Gauge("felicity_inverter_overhead_watts", "Configured inverter self-consumption (W)"),
    "grid_power": Gauge("felicity_grid_power_watts", "Grid input power (ACin[3][0])"),
    "tariff": Gauge("felicity_tariff_ngn_per_kwh", "Electricity price incl. VAT (NGN per kWh)"),
    "pv_kwh": Gauge("felicity_pv_energy_kwh_total", "Solar energy produced since tracking began (kWh)"),
    "load_kwh": Gauge("felicity_load_energy_kwh_total", "House energy used since tracking began (kWh)"),
    "grid_kwh": Gauge("felicity_grid_energy_kwh_total", "Grid energy imported since tracking began (kWh)"),
    "tracking_start": Gauge("felicity_energy_tracking_start_timestamp_seconds", "When energy tracking began"),
}
G["cfg_capacity"].set(BATTERY_CAPACITY_WH)
G["cfg_reserve"].set(BATTERY_RESERVE_PERCENT)
G["cfg_overhead"].set(INVERTER_OVERHEAD_W)
G["tariff"].set(round(TARIFF_NGN_PER_KWH * (1 + TARIFF_VAT_PERCENT / 100), 2))


# ---- energy totals, integrated from power readings and saved to disk ----
def load_energy():
    try:
        with open(STATE_FILE) as f:
            e = json.load(f)
        return {k: float(e.get(k, 0)) for k in ("pv_wh", "load_wh", "grid_wh")} | {"since": float(e.get("since", time.time()))}
    except (OSError, ValueError):
        return {"pv_wh": 0.0, "load_wh": 0.0, "grid_wh": 0.0, "since": time.time()}


def save_energy(e):
    try:
        os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
        tmp = STATE_FILE + ".tmp"
        with open(tmp, "w") as f:
            json.dump(e, f)
        os.replace(tmp, STATE_FILE)
    except OSError as exc:
        log.warning("Could not save energy totals: %s", exc)


energy = load_energy()
last_sample = {"t": None, "pv": None, "load": None, "grid": None}


def publish_energy():
    G["pv_kwh"].set(round(energy["pv_wh"] / 1000, 4))
    G["load_kwh"].set(round(energy["load_wh"] / 1000, 4))
    G["grid_kwh"].set(round(energy["grid_wh"] / 1000, 4))
    G["tracking_start"].set(energy["since"])


def accumulate(now, pv, load, grid):
    """Trapezoid integration of power (W) into energy (Wh) between polls."""
    prev = last_sample
    if prev["t"] is not None and 0 < now - prev["t"] <= MAX_GAP_SECONDS:
        hours = (now - prev["t"]) / 3600
        for key, cur, old in (("pv_wh", pv, prev["pv"]), ("load_wh", load, prev["load"]), ("grid_wh", grid, prev["grid"])):
            if cur is not None and old is not None:
                energy[key] += max((cur + old) / 2, 0) * hours
    last_sample.update(t=now, pv=pv, load=load, grid=grid)
    save_energy(energy)
    publish_energy()


publish_energy()

latest = {}
lock = threading.Lock()


def first(data, key, row, col=0):
    """Safely read data[key][row][col]; returns None if missing."""
    try:
        value = data[key][row][col]
        return None if value is None else float(value)
    except (KeyError, IndexError, TypeError, ValueError):
        return None


def scale(value, factor):
    return None if value is None else round(value * factor, 3)


def query():
    with socket.create_connection((HOST, PORT), timeout=8) as s:
        s.sendall(QUERY)
        s.settimeout(8)
        buf = b""
        while b"}" not in buf:
            chunk = s.recv(4096)
            if not chunk:
                break
            buf += chunk
        try:
            s.sendall(b".")  # acknowledgement
        except OSError:
            pass
    if b"}" not in buf:
        raise ValueError("incomplete response")
    return json.loads(buf[: buf.index(b"}") + 1])


def decode(d):
    grid_v = scale(first(d, "ACin", 0), 0.1)
    v = {
        "pv_voltage": scale(first(d, "PV", 0), 0.1),
        "pv_current": scale(first(d, "PV", 1), 0.1),
        "pv_power": first(d, "PV", 2),
        "bat_voltage": scale(first(d, "Batt", 0), 0.001),
        "bat_current": scale(first(d, "Batt", 1), 0.1),
        "bat_power": first(d, "Batt", 2),
        "bat_soc": scale(first(d, "Batsoc", 0), 0.01),
        "bat_temp": float(d["BatTem"]) if d.get("BatTem") is not None else None,
        "out_voltage": scale(first(d, "ACout", 0), 0.1),
        "out_current": scale(first(d, "ACout", 1), 0.1),
        "out_freq": scale(first(d, "ACout", 2), 0.01),
        "load_power": first(d, "ACout", 3, 0),
        "load_va": first(d, "ACout", 3, 1),
        "grid_voltage": grid_v,
        "grid_present": None if grid_v is None else (1.0 if grid_v > 100 else 0.0),
        "grid_power": first(d, "ACin", 3, 0),
        "bus_voltage": scale(float(d["busVp"]), 0.1) if d.get("busVp") is not None else None,
        "warn": float(d.get("warn", 0)),
        "fault": float(d.get("fault", 0)),
        "work_mode": float(d["workM"]) if d.get("workM") is not None else None,
        "load_percent_raw": float(d["lPerc"]) if d.get("lPerc") is not None else None,
    }
    temps = [scale(t, 0.1) for t in (d.get("Temp") or [[]])[0] if t is not None]
    return v, temps


def poll_once():
    data = query()
    values, temps = decode(data)
    for key, value in values.items():
        if value is not None:
            G[key].set(value)
    for i, t in enumerate(temps, start=1):
        G["temp"].labels(f"t{i}").set(t)
    now = time.time()
    accumulate(now, values.get("pv_power"), values.get("load_power"), values.get("grid_power"))
    G["up"].set(1)
    G["last_success"].set(now)
    with lock:
        latest.clear()
        latest.update({k: v for k, v in values.items() if v is not None})
        latest.update({f"temp_{i}": t for i, t in enumerate(temps, start=1)})
        latest["capacity_wh"] = BATTERY_CAPACITY_WH
        latest["reserve_percent"] = BATTERY_RESERVE_PERCENT
        soc = values.get("bat_soc")
        if soc is not None:
            remaining = max(soc - BATTERY_RESERVE_PERCENT, 0) / 100 * BATTERY_CAPACITY_WH
            latest["energy_left_wh"] = round(remaining)
            bat = values.get("bat_power")
            if bat is not None and bat < -10:
                latest["runtime_hours"] = round(remaining / -bat, 2)
            load = values.get("load_power")
            if load is not None:
                latest["night_runtime_hours"] = round(remaining / (load + INVERTER_OVERHEAD_W), 2)
        latest["pv_energy_kwh_total"] = round(energy["pv_wh"] / 1000, 3)
        latest["load_energy_kwh_total"] = round(energy["load_wh"] / 1000, 3)
        latest["grid_energy_kwh_total"] = round(energy["grid_wh"] / 1000, 3)
        latest["tariff_ngn_per_kwh"] = round(TARIFF_NGN_PER_KWH * (1 + TARIFF_VAT_PERCENT / 100), 2)
        latest["updated"] = int(time.time())


def poller():
    while True:
        try:
            poll_once()
        except Exception as exc:  # noqa: BLE001
            G["up"].set(0)
            log.warning("Poll failed: %s", exc)
        time.sleep(POLL_SECONDS)


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def _send(self, code, body, ctype):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path.startswith("/metrics"):
            return self._send(200, generate_latest(), CONTENT_TYPE_LATEST)
        if self.path.startswith("/json"):
            with lock:
                body = json.dumps(latest).encode()
            return self._send(200, body, "application/json")
        self._send(404, b"not found", "text/plain")


if __name__ == "__main__":
    threading.Thread(target=poller, daemon=True).start()
    log.info("Polling %s:%d every %ds; serving on :%d", HOST, PORT, POLL_SECONDS, LISTEN_PORT)
    ThreadingHTTPServer(("0.0.0.0", LISTEN_PORT), Handler).serve_forever()
