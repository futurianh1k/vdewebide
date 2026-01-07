import unittest
import sys
from pathlib import Path

from fastapi.testclient import TestClient

# Allow running tests from repo root
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.main import app


class TestIdp(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_healthz(self):
        r = self.client.get("/healthz")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json().get("status"), "ok")

    def test_jwks_and_token(self):
        jwks = self.client.get("/.well-known/jwks.json").json()
        self.assertTrue(jwks.get("keys"))
        kid = jwks["keys"][0].get("kid")
        self.assertTrue(kid)

        r = self.client.post("/token", json={"sub": "u1", "tid": "t1", "pid": "p1", "wid": "w1", "role": "admin"})
        self.assertEqual(r.status_code, 200)
        token = r.json().get("access_token")
        self.assertTrue(token)


if __name__ == "__main__":
    unittest.main()

