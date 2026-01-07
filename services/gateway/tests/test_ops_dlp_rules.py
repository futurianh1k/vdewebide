import unittest
import sys
import tempfile
from pathlib import Path


class TestOpsDlpRules(unittest.TestCase):
    def setUp(self):
        # Import path (repo root 실행 대응)
        self.tmpdir = tempfile.TemporaryDirectory()
        tmp = Path(self.tmpdir.name)

        self.dlp_file = tmp / "dlp_rules.yaml"
        self.dlp_file.write_text("version: dlp-test\nrules: []\n", encoding="utf-8")

        ROOT = Path(__file__).resolve().parents[1]
        sys.path.insert(0, str(ROOT))

        # Configure settings at runtime (avoid env ordering issues in unittest discovery)
        from app.config import settings  # noqa: E402
        settings.jwt_dev_mode = True
        settings.ops_retention_purge_key = "dev-ops-key"
        settings.ops_policy_key = "dev-ops-key"
        settings.dlp_rules_path = str(self.dlp_file)

        from app.main import app  # noqa: E402
        from fastapi.testclient import TestClient  # noqa: E402

        self.client = TestClient(app)

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_get_requires_ops_key(self):
        r = self.client.get(
            "/ops/dlp/rules",
            headers={"Authorization": "Bearer dev-admin"},
        )
        self.assertEqual(r.status_code, 403)

    def test_put_and_get(self):
        new_rules = "version: dlp-test2\nrules:\n  - id: r1\n    kind: regex\n    pattern: \"Bearer\\\\s+[A-Za-z0-9._-]+\"\n    action: block\n"
        r = self.client.put(
            "/ops/dlp/rules",
            data=new_rules.encode("utf-8"),
            headers={"Authorization": "Bearer dev-admin", "X-Ops-Key": "dev-ops-key", "Content-Type": "text/yaml"},
        )
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.json().get("ok"))

        r2 = self.client.get(
            "/ops/dlp/rules",
            headers={"Authorization": "Bearer dev-admin", "X-Ops-Key": "dev-ops-key"},
        )
        self.assertEqual(r2.status_code, 200)
        self.assertEqual(r2.json().get("version"), "dlp-test2")
        self.assertIn("rules:", r2.json().get("raw", ""))


if __name__ == "__main__":
    unittest.main()

