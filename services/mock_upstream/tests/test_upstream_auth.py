import os
import unittest
import sys
from pathlib import Path
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.main import app


class TestMockUpstreamAuth(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_no_auth_required_by_default(self):
        os.environ.pop("REQUIRE_UPSTREAM_AUTH", None)
        os.environ.pop("UPSTREAM_EXPECTED_BEARER", None)
        r = self.client.post("/v1/chat", json={"x": 1})
        self.assertEqual(r.status_code, 200)

    def test_auth_required(self):
        os.environ["REQUIRE_UPSTREAM_AUTH"] = "true"
        os.environ["UPSTREAM_EXPECTED_BEARER"] = "upstream-token"

        r = self.client.post("/v1/chat", json={"x": 1})
        self.assertEqual(r.status_code, 401)

        r2 = self.client.post("/v1/chat", json={"x": 1}, headers={"Authorization": "Bearer upstream-token"})
        self.assertEqual(r2.status_code, 200)


if __name__ == "__main__":
    unittest.main()

