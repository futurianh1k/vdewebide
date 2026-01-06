import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.provisioners.docker_provider import DockerProvisioner  # noqa: E402


class TestOpencodeConfigBuilder(unittest.TestCase):
    def test_build_opencode_config_contains_gateway_url(self):
        cfg = DockerProvisioner.build_opencode_config("http://gateway:8081")
        self.assertEqual(cfg["gateway"]["base_url"], "http://gateway:8081")
        self.assertFalse(cfg["security"]["store_tokens_in_config"])

