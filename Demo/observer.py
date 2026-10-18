#!/usr/bin/env python3
"""
Local HTTP request observer for the anti-bot detection research project.

This server records basic HTTP request metadata so you can compare requests
from a normal Python HTTP client and a browser against your own local endpoint.

Safety and scope:
- Binds only to 127.0.0.1 (this device), not the public network.
- Does not record request bodies, cookies, or authorization values.
- Does not capture TLS ClientHello data and cannot calculate JA3/JA4.
- Intended for local educational experiments only.
"""

from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import uuid


HOST = "127.0.0.1"
PORT = 8080


class Observer(BaseHTTPRequestHandler):
    server_version = "LocalObserver"
    sys_version = ""

    def do_GET(self):
        # Avoid logging sensitive values if clients include them by mistake.
        sensitive_headers = {"authorization", "cookie", "proxy-authorization"}
        headers = []
        for name, value in self.headers.items():
            if name.lower() in sensitive_headers:
                value = "[REDACTED]"
            headers.append({"name": name, "value": value})

        record = {
            "request_id": str(uuid.uuid4()),
            "observed_at_utc": datetime.now(timezone.utc).isoformat(),
            "client_address": self.client_address[0],
            "method": self.command,
            "path": self.path,
            "http_version": self.request_version,
            # This is what Python's HTTP parser exposes, not a packet capture.
            "headers": headers,
        }

        print(json.dumps(record, indent=2), flush=True)

        body = json.dumps(
            {
                "ok": True,
                "request_id": record["request_id"],
                "header_count": len(headers),
                "note": "Local HTTP metadata only; no TLS fingerprint is captured.",
            }
        ).encode("utf-8")

        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_HEAD(self):
        # A minimal HEAD response helps when checking whether the server is up.
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", "0")
        self.end_headers()

    def log_message(self, fmt, *args):
        # The structured record above is the log for this demonstration.
        return


def main():
    server = ThreadingHTTPServer((HOST, PORT), Observer)
    print(f"Local observer listening at http://{HOST}:{PORT}")
    print("Only this device can connect. Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping local observer.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
