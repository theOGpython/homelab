"""
Prometheus exporter for the Huawei 5G ODU (Airtel, model H362-383).

Every POLL_SECONDS it logs into the ODU's local web API, reads traffic,
monthly/daily usage, signal and status counters, then logs out. Prometheus
scrapes the latest values from http://<container>:9877/metrics.

Config (environment variables):
  ODU_URL        e.g. http://192.168.8.1/
  ODU_USERNAME   default: admin
  ODU_PASSWORD   required
  POLL_SECONDS   default: 60
  EXPORTER_PORT  default: 9877
"""
import logging
import os
import re
import time

from huawei_lte_api.Client import Client
from huawei_lte_api.Connection import Connection
from prometheus_client import Gauge, start_http_server

ODU_URL = os.environ["ODU_URL"]
ODU_USERNAME = os.environ.get("ODU_USERNAME", "admin")
ODU_PASSWORD = os.environ["ODU_PASSWORD"]
POLL_SECONDS = int(os.environ.get("POLL_SECONDS", "60"))
EXPORTER_PORT = int(os.environ.get("EXPORTER_PORT", "9877"))

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("odu-exporter")

# API field -> (metric name, help text)
TRAFFIC_FIELDS = {
    "TotalDownload": ("odu_total_download_bytes", "Lifetime bytes downloaded (counter-like)"),
    "TotalUpload": ("odu_total_upload_bytes", "Lifetime bytes uploaded (counter-like)"),
    "TotalConnectTime": ("odu_total_connect_seconds", "Lifetime connected time"),
    "CurrentDownload": ("odu_session_download_bytes", "Bytes downloaded since last reconnect"),
    "CurrentUpload": ("odu_session_upload_bytes", "Bytes uploaded since last reconnect"),
    "CurrentConnectTime": ("odu_session_connect_seconds", "Seconds since last reconnect"),
    "CurrentDownloadRate": ("odu_download_rate_bytes", "Current download speed, bytes/second"),
    "CurrentUploadRate": ("odu_upload_rate_bytes", "Current upload speed, bytes/second"),
}
MONTH_FIELDS = {
    "CurrentDayUsed": ("odu_day_used_bytes", "Bytes used today (ODU's own daily counter)"),
    "CurrentDayDuration": ("odu_day_connect_seconds", "Seconds connected today"),
    "CurrentMonthDownload": ("odu_month_download_bytes", "Bytes downloaded this billing period"),
    "CurrentMonthUpload": ("odu_month_upload_bytes", "Bytes uploaded this billing period"),
    "MonthDuration": ("odu_month_connect_seconds", "Seconds connected this billing period"),
}

GAUGES = {
    field: Gauge(name, help_text)
    for field, (name, help_text) in {**TRAFFIC_FIELDS, **MONTH_FIELDS}.items()
}
SIGNAL = Gauge("odu_signal", "Raw numeric signal values reported by the ODU", ["metric"])
STATUS = Gauge("odu_status", "Raw numeric status values reported by the ODU", ["field"])
UP = Gauge("odu_up", "1 if the last poll of the ODU succeeded, else 0")
LAST_SUCCESS = Gauge("odu_last_success_timestamp_seconds", "Unix time of last successful poll")
POLL_DURATION = Gauge("odu_poll_duration_seconds", "How long the last poll took")

NUMBER = re.compile(r"^\s*(-?\d+(?:\.\d+)?)\s*[A-Za-z%]*\s*$")  # "-95dBm" -> -95; IPs/text ignored


def to_number(value):
    if value is None:
        return None
    match = NUMBER.match(str(value))
    return float(match.group(1)) if match else None


def set_fields(data, mapping):
    for field in mapping:
        number = to_number(data.get(field))
        if number is not None:
            GAUGES[field].set(number)


def set_labelled(gauge, data):
    """Export every numeric value in a dict, labelled by its key (model-agnostic)."""
    for key, value in (data or {}).items():
        number = to_number(value)
        if number is not None:
            gauge.labels(key.lower()).set(number)


def poll():
    started = time.monotonic()
    with Connection(ODU_URL, username=ODU_USERNAME, password=ODU_PASSWORD, timeout=15) as conn:
        client = Client(conn)
        set_fields(client.monitoring.traffic_statistics(), TRAFFIC_FIELDS)
        set_fields(client.monitoring.month_statistics(), MONTH_FIELDS)

        # Optional extras: not every firmware exposes these, so never fail the poll on them.
        for gauge, call in ((SIGNAL, client.device.signal), (STATUS, client.monitoring.status)):
            try:
                set_labelled(gauge, call())
            except Exception as exc:  # noqa: BLE001
                log.debug("Optional call %s failed: %s", call.__name__, exc)

    POLL_DURATION.set(time.monotonic() - started)
    LAST_SUCCESS.set(time.time())
    UP.set(1)


def main():
    start_http_server(EXPORTER_PORT)
    log.info("Exporter listening on :%d, polling %s every %ds", EXPORTER_PORT, ODU_URL, POLL_SECONDS)
    while True:
        try:
            poll()
        except Exception as exc:  # noqa: BLE001
            UP.set(0)
            log.warning("Poll failed: %s", exc)
        time.sleep(POLL_SECONDS)


if __name__ == "__main__":
    main()
