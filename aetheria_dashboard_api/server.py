"""Aetheria Dashboard Backend REST API.

Live status for all 7 Knowledge Graphs.
"""

from __future__ import annotations

import json
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Any
from urllib.parse import urlparse


DASHBOARD_KGs = {
    "manufacturing": {"repo": "itsPremkumar/aetheria-manufacturing", "status": "active", "tests": 119},
    "healthcare": {"repo": "itsPremkumar/aetheria-healthcare", "status": "active", "tests": 120},
    "finance": {"repo": "itsPremkumar/aetheria-finance", "status": "active", "tests": 34},
    "education": {"repo": "itsPremkumar/aetheria-education", "status": "active", "tests": 65},
    "agriculture": {"repo": "itsPremkumar/aetheria-agriculture", "status": "active", "tests": 89},
    "legal": {"repo": "itsPremkumar/aetheria-legal", "status": "active", "tests": 42},
    "customer_service": {"repo": "itsPremkumar/aetheria-customer-service", "status": "active", "tests": 38},
}


class DashboardHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/api/v1/dashboard/health":
            self._json_response({"status": "healthy", "dashboard": "aetheria"})
        elif path == "/api/v1/dashboard/projects":
            self._json_response(self._list_projects())
        elif path.startswith("/api/v1/dashboard/project/"):
            name = path.split("/")[-1]
            self._json_response(self._get_project(name))
        elif path == "/api/v1/dashboard/metrics":
            self._json_response(self._get_metrics())
        else:
            self._json_response({"error": "Not found"}, status=404)

    def _list_projects(self) -> dict[str, Any]:
        return {
            "projects": list(DASHBOARD_KGs.keys()),
            "total": len(DASHBOARD_KGs),
        }

    def _get_project(self, name: str) -> dict[str, Any]:
        if name not in DASHBOARD_KGs:
            return {"error": f"Project '{name}' not found"}
        return DASHBOARD_KGs[name]

    def _get_metrics(self) -> dict[str, Any]:
        total_tests = sum(p["tests"] for p in DASHBOARD_KGs.values())
        return {
            "total_projects": len(DASHBOARD_KGs),
            "total_tests": total_tests,
            "active_projects": len(DASHBOARD_KGs),
        }

    def _json_response(self, data: dict[str, Any], status: int = 200) -> None:
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode())

    def log_message(self, format: str, *args: Any) -> None:
        pass


def run_dashboard(host: str = "0.0.0.0", port: int = 8081) -> None:
    server = HTTPServer((host, port), DashboardHandler)
    print(f"Aetheria Dashboard API running on http://{host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    run_dashboard()