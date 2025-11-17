"""Integration tests for core.auth_server (local callback server)"""
import unittest
import tempfile
import time
import sys
from pathlib import Path
import requests

sys.path.insert(0, str(Path(__file__).parent.parent / "cli_draft2"))

from core import auth_server
from core import storage, config


class TestAuthServerIntegration(unittest.TestCase):
    def setUp(self):
        self.orig_dir = config.CREDENTIALS_DIR
        self.tempdir = tempfile.TemporaryDirectory()
        config.CREDENTIALS_DIR = self.tempdir.name

    def tearDown(self):
        config.CREDENTIALS_DIR = self.orig_dir
        self.tempdir.cleanup()

    def test_callback_and_persistence(self):
        receiver = auth_server.AuthReceiver(start_port=0)
        port = receiver.start()
        # Make sure the server is listening
        self.assertIsNotNone(port)
        self.assertGreater(port, 0)

        params = {
            "access_token": "token-abc",
            "refresh_token": "refresh-123",
            "email": "user@example.com",
        }
        url = f"http://{config.LOCAL_SERVER_HOST}:{port}{config.AUTH_CALLBACK_PATH}"
        r = requests.get(url, params=params)
        self.assertEqual(r.status_code, 200)

        tokens = receiver.wait_for_tokens(timeout=5)
        self.assertIsNotNone(tokens)
        self.assertEqual(tokens["access_token"], params["access_token"])
        self.assertEqual(tokens["refresh_token"], params["refresh_token"])

        # Storage should have persisted the credentials as a fail-safe
        loaded = storage.load_credentials()
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded.get("access_token"), params["access_token"])    


if __name__ == "__main__":
    unittest.main()
