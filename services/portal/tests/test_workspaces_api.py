import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from fastapi.testclient import TestClient  # noqa: E402
from app.main import app  # noqa: E402


class TestWorkspacesApi(unittest.TestCase):
    def setUp(self):
        self.c = TestClient(app)
        self.h = {"X-Admin-Key": "dev-admin-key"}

    def test_list_empty(self):
        r = self.c.get("/api/workspaces", headers=self.h)
        self.assertEqual(r.status_code, 200)
        self.assertIsInstance(r.json().get("items"), list)

    def test_create_workspace(self):
        r = self.c.post("/api/workspaces", headers=self.h, json={"name": "ws1"})
        self.assertEqual(r.status_code, 200)
        body = r.json()
        self.assertIn("id", body)
        self.assertEqual(body["name"], "ws1")

