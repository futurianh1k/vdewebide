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

    def test_requires_admin_key(self):
        r = self.c.get("/api/workspaces")
        self.assertEqual(r.status_code, 403)

    def test_tenant_project_user_lifecycle(self):
        # tenant
        r = self.c.post("/api/tenants", headers=self.h, json={"name": "Acme"})
        self.assertEqual(r.status_code, 200)
        tid = r.json().get("id")
        self.assertTrue(tid)

        # project
        r = self.c.post("/api/projects", headers=self.h, json={"tenant_id": tid, "name": "P1"})
        self.assertEqual(r.status_code, 200)
        pid = r.json().get("id")
        self.assertTrue(pid)

        # user
        r = self.c.post(
            "/api/users",
            headers=self.h,
            json={"tenant_id": tid, "user_id": "u1", "display_name": "U1", "role": "admin"},
        )
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json().get("role"), "admin")

        # lists
        self.assertEqual(self.c.get("/api/tenants", headers=self.h).status_code, 200)
        self.assertEqual(self.c.get(f"/api/projects?tenant_id={tid}", headers=self.h).status_code, 200)
        self.assertEqual(self.c.get(f"/api/users?tenant_id={tid}", headers=self.h).status_code, 200)

    def test_poc_bootstrap(self):
        r = self.c.post("/api/poc/bootstrap", headers=self.h, json={})
        self.assertEqual(r.status_code, 200)
        body = r.json()
        self.assertIn("tenant", body)
        self.assertIn("project", body)
        self.assertIn("user", body)
        self.assertIn("workspace", body)
        self.assertTrue(body["workspace"].get("id"))

    def test_create_workspace(self):
        r = self.c.post("/api/workspaces", headers=self.h, json={"name": "ws1"})
        self.assertEqual(r.status_code, 200)
        body = r.json()
        self.assertIn("id", body)
        self.assertEqual(body["name"], "ws1")

