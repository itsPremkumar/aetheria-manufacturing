"""Aetheria Unified API Gateway.

Routes requests to all 7 Knowledge Graph APIs.
"""

from __future__ import annotations

import json
import os
import urllib.request
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Any
from urllib.parse import urlparse, parse_qs


API_BACKENDS = {
    "manufacturing": "https://api.github.com/repos/itsPremkumar/aetheria-manufacturing",
    "healthcare": "https://api.github.com/repos/itsPremkumar/aetheria-healthcare",
    "finance": "https://api.github.com/repos/itsPremkumar/aetheria-finance",
    "education": "https://api.github.com/repos/itsPremkumar/aetheria-education",
    "agriculture": "https://api.github.com/repos/itsPremkumar/aetheria-agriculture",
    "legal": "https://api.github.com/repos/itsPremkumar/aetheria-legal",
    "customer_service": "https://api.github.com/repos/itsPremkumar/aetheria-customer-service",
}


class GatewayHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)

        if path == "/api/v1/gateway/health":
            self._json_response({"status": "healthy", "gateway": "aetheria"})
        elif path == "/api/v1/gateway/projects":
            self._json_response(self._list_projects())
        elif path.startswith("/api/v1/gateway/project/"):
            name = path.split("/")[-1]
            self._json_response(self._get_project(name))
        elif path == "/api/v1/gateway/metrics":
            self._json_response(self._get_metrics())
        else:
            self._json_response({"error": "Not found"}, status=404)

    def _list_projects(self) -> dict[str, Any]:
        return {
            "projects": list(API_BACKENDS.keys()),
            "total": len(API_BACKENDS),
        }

    def _get_project(self, name: str) -> dict[str, Any]:
        if name not in API_BACKENDS:
            return {"error": f"Project '{name}' not found"}
        return {
            "name": name,
            "api": API_BACKENDS[name],
            "status": "active",
        }

    def _get_metrics(self) -> dict[str, Any]:
        return {
            "total_projects": len(API_BACKENDS),
            "active_backends": len(API_BACKENDS),
            "gateway_version": "1.0.0",
        }

    def _json_response(self, data: dict[str, Any], status: int = 200) -> None:
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode())

    def log_message(self, format: str, *args: Any) -> None:
        pass  # Suppress default logging


def run_gateway(host: str = "0.0.0.0", port: int = 8080) -> None:
    server = HTTPServer((host, port), GatewayHandler)
    print(f"Aetheria API Gateway running on http://{host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    run_gateway()