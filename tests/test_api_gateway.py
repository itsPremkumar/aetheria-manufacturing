"""Tests for Aetheria Unified API Gateway."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aetheria_api_gateway.server import GatewayHandler


class MockRequest:
    rfile = None
    wfile = None
    def makefile(self, *args, **kwargs):
        return None
    def close(self):
        pass


class MockConnection:
    rfile = None
    wfile = None
    def makefile(self, *args, **kwargs):
        return None
    def close(self):
        pass


class TestGatewayHandler:
    def _create(self):
        # Create handler without calling __init__ (avoids socket setup)
        handler = GatewayHandler.__new__(GatewayHandler)
        handler.request = MockRequest()
        handler.client_address = ("127.0.0.1", 8080)
        handler.server = None
        return handler

    def test_list_projects(self):
        handler = self._create()
        result = handler._list_projects()
        assert "projects" in result
        assert result["total"] == 7

    def test_get_project(self):
        handler = self._create()
        result = handler._get_project("manufacturing")
        assert result["name"] == "manufacturing"
        assert result["status"] == "active"

    def test_get_project_not_found(self):
        handler = self._create()
        result = handler._get_project("nonexistent")
        assert "error" in result

    def test_get_metrics(self):
        handler = self._create()
        result = handler._get_metrics()
        assert result["total_projects"] == 7
        assert result["gateway_version"] == "1.0.0"