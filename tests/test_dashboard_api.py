"""Tests for Aetheria Dashboard Backend REST API."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aetheria_dashboard_api.server import DashboardHandler


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


class TestDashboardHandler:
    def _create(self):
        handler = DashboardHandler.__new__(DashboardHandler)
        handler.request = MockRequest()
        handler.client_address = ("127.0.0.1", 8081)
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
        assert result["repo"] == "itsPremkumar/aetheria-manufacturing"
        assert result["status"] == "active"
        assert result["tests"] == 119

    def test_get_project_not_found(self):
        handler = self._create()
        result = handler._get_project("nonexistent")
        assert "error" in result

    def test_get_metrics(self):
        handler = self._create()
        result = handler._get_metrics()
        assert result["total_projects"] == 7
        assert result["total_tests"] > 0
        assert result["active_projects"] == 7