import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.authorize import authorize_path
from app.auth import Identity, AuthError
from app.dlp import dlp_engine


class TestAuthorize(unittest.TestCase):
    def test_viewer_can_chat(self):
        identity = Identity(user_id="u", tenant_id="t", project_id="p", workspace_id="w", role="viewer")
        authorize_path(identity, "/v1/chat")

    def test_viewer_cannot_agent(self):
        identity = Identity(user_id="u", tenant_id="t", project_id="p", workspace_id="w", role="viewer")
        with self.assertRaises(AuthError):
            authorize_path(identity, "/v1/agent")

    def test_admin_can_rag_index(self):
        identity = Identity(user_id="u", tenant_id="t", project_id="p", workspace_id="w", role="admin")
        authorize_path(identity, "/v1/rag/index")


class TestDlp(unittest.TestCase):
    def test_blocks_bearer_token_pattern(self):
        # 정책 기본값: bearer_token 룰이 block
        action, rid = dlp_engine.inspect_bytes(b"Authorization: Bearer abc.def.ghi")
        self.assertEqual(action, "block")
        self.assertEqual(rid, "bearer_token")

