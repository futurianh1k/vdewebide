import unittest
from pathlib import Path
import sys

from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from fastapi.testclient import TestClient  # noqa: E402
from app.main import app  # noqa: E402


class DummyResponse:
    def __init__(self, status_code=200, json_data=None, headers=None, text=""):
        self.status_code = status_code
        self._json_data = json_data or {}
        self.headers = headers or {"content-type": "application/json"}
        self.text = text

    def json(self):
        return self._json_data


class DummyClient:
    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def request(self, method, url, content=None, headers=None):
        return DummyResponse(200, {"ok": True, "method": method, "url": url})


class TestIdpProxy(unittest.TestCase):
    def setUp(self):
        self.c = TestClient(app)
        self.h = {"X-Admin-Key": "dev-admin-key"}

    def test_proxy_idp_token(self):
        with patch("httpx.AsyncClient", return_value=DummyClient()):
            r = self.c.post("/api/idp/token", headers=self.h, json={"sub": "u1"})
            self.assertEqual(r.status_code, 200)
            self.assertTrue(r.json().get("ok"))


if __name__ == "__main__":
    unittest.main()

