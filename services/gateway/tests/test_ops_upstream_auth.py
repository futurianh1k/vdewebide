import sys
import unittest
from pathlib import Path


class TestOpsUpstreamAuth(unittest.TestCase):
    def setUp(self):
        ROOT = Path(__file__).resolve().parents[1]
        sys.path.insert(0, str(ROOT))

        from app.config import settings  # noqa: E402
        settings.jwt_dev_mode = True
        settings.ops_retention_purge_key = "dev-ops-key"
        settings.ops_policy_key = "dev-ops-key"

        from app.main import app  # noqa: E402
        from fastapi.testclient import TestClient  # noqa: E402

        self.c = TestClient(app)

    def test_get_and_put(self):
        h = {"Authorization": "Bearer dev-admin", "X-Ops-Key": "dev-ops-key"}

        r = self.c.get("/ops/upstream/auth", headers=h)
        self.assertEqual(r.status_code, 200)

        r2 = self.c.put("/ops/upstream/auth", headers=h, json={"upstream_auth_mode": "static_bearer", "upstream_bearer_token": "t"})
        self.assertEqual(r2.status_code, 200)
        self.assertEqual(r2.json().get("upstream_auth_mode"), "static_bearer")


if __name__ == "__main__":
    unittest.main()

