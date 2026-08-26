import base64
import hashlib
import hmac
import json
import os
import time
import urllib.error
import urllib.request
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


API_BASE = "https://api.switch-bot.com/v1.1"
LISTEN_HOST = os.environ.get("SWITCHBOT_EXPORTER_HOST", "0.0.0.0")
LISTEN_PORT = int(os.environ.get("SWITCHBOT_EXPORTER_PORT", "8000"))
CACHE_SECONDS = int(os.environ.get("SWITCHBOT_CACHE_SECONDS", "300"))
DEVICE_IDS = [
    device_id.strip()
    for device_id in os.environ.get("SWITCHBOT_DEVICE_IDS", "").split(",")
    if device_id.strip()
]

cache = {
    "expires_at": 0,
    "metrics": "",
}


def switchbot_headers():
    token = os.environ.get("SWITCHBOT_TOKEN", "")
    secret = os.environ.get("SWITCHBOT_SECRET", "")
    if not token or not secret:
        raise RuntimeError("SWITCHBOT_TOKEN and SWITCHBOT_SECRET are required")

    nonce = str(uuid.uuid4())
    timestamp = str(int(round(time.time() * 1000)))
    message = f"{token}{timestamp}{nonce}".encode("utf-8")
    digest = hmac.new(secret.encode("utf-8"), msg=message, digestmod=hashlib.sha256).digest()
    sign = base64.b64encode(digest).decode("utf-8")

    return {
        "Authorization": token,
        "sign": sign,
        "nonce": nonce,
        "t": timestamp,
        "Content-Type": "application/json",
    }


def switchbot_get(path):
    request = urllib.request.Request(f"{API_BASE}{path}", headers=switchbot_headers())
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            payload = response.read().decode("utf-8")
    except urllib.error.HTTPError as error:
        body = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"SwitchBot API returned HTTP {error.code}: {body}") from error

    data = json.loads(payload)
    if data.get("statusCode") != 100:
        raise RuntimeError(f"SwitchBot API returned error: {payload}")
    return data.get("body", {})


def discover_meter_pro_co2_devices():
    body = switchbot_get("/devices")
    devices = body.get("deviceList", [])
    return [
        device
        for device in devices
        if device.get("deviceType") in ("MeterPro(CO2)", "Meter Pro CO2")
    ]


def device_status(device_id):
    return switchbot_get(f"/devices/{device_id}/status")


def metric_name(device):
    name = device.get("deviceName") or device.get("deviceId") or "unknown"
    return name.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")


def emit_metric(lines, name, value, labels):
    if value is None:
        return
    label_text = ",".join(f'{key}="{val}"' for key, val in labels.items())
    lines.append(f"{name}{{{label_text}}} {value}")


def build_metrics():
    devices = []
    if DEVICE_IDS:
        devices = [{"deviceId": device_id, "deviceName": device_id} for device_id in DEVICE_IDS]
    else:
        devices = discover_meter_pro_co2_devices()

    lines = [
        "# HELP switchbot_co2_ppm SwitchBot CO2 concentration in ppm.",
        "# TYPE switchbot_co2_ppm gauge",
        "# HELP switchbot_temperature_celsius SwitchBot temperature in Celsius.",
        "# TYPE switchbot_temperature_celsius gauge",
        "# HELP switchbot_humidity_percent SwitchBot relative humidity percent.",
        "# TYPE switchbot_humidity_percent gauge",
        "# HELP switchbot_battery_percent SwitchBot battery percent.",
        "# TYPE switchbot_battery_percent gauge",
        "# HELP switchbot_device_up SwitchBot device status fetch result.",
        "# TYPE switchbot_device_up gauge",
    ]

    for device in devices:
        device_id = device.get("deviceId")
        labels = {
            "device_id": metric_name({"deviceName": device_id}),
            "device_name": metric_name(device),
        }

        try:
            status = device_status(device_id)
        except Exception:
            emit_metric(lines, "switchbot_device_up", 0, labels)
            continue

        emit_metric(lines, "switchbot_device_up", 1, labels)
        emit_metric(lines, "switchbot_co2_ppm", status.get("CO2"), labels)
        emit_metric(lines, "switchbot_temperature_celsius", status.get("temperature"), labels)
        emit_metric(lines, "switchbot_humidity_percent", status.get("humidity"), labels)
        emit_metric(lines, "switchbot_battery_percent", status.get("battery"), labels)

    return "\n".join(lines) + "\n"


def cached_metrics():
    now = time.time()
    if cache["metrics"] and cache["expires_at"] > now:
        return cache["metrics"]

    metrics = build_metrics()
    cache["metrics"] = metrics
    cache["expires_at"] = now + CACHE_SECONDS
    return metrics


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/healthz":
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"ok\n")
            return

        if self.path != "/metrics":
            self.send_response(404)
            self.end_headers()
            return

        try:
            body = cached_metrics().encode("utf-8")
            self.send_response(200)
        except Exception as error:
            body = f"# switchbot_exporter_error {json.dumps(str(error))}\n".encode("utf-8")
            self.send_response(500)

        self.send_header("Content-Type", "text/plain; version=0.0.4; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        return


if __name__ == "__main__":
    server = ThreadingHTTPServer((LISTEN_HOST, LISTEN_PORT), Handler)
    server.serve_forever()
