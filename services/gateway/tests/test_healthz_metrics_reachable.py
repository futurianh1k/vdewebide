import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from fastapi.testclient import TestClient
from app.main import app


class TestNonProxiedEndpoints(unittest.TestCase):
    def test_healthz(self):
        c = TestClient(app)
        r = c.get("/healthz")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json().get("status"), "ok")

    def test_metrics(self):
        c = TestClient(app)
        r = c.get("/metrics")
        self.assertEqual(r.status_code, 200)
        self.assertIn("ai_gateway_requests_total", r.text)

