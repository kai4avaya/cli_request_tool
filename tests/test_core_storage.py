"""Tests for core.storage module"""
import unittest
import tempfile
import json
import os
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "cli_draft2"))

from core import storage
from core import config


class TestCoreStorage(unittest.TestCase):
    def setUp(self):
        self.orig_dir = config.CREDENTIALS_DIR
        self.tempdir = tempfile.TemporaryDirectory()
        config.CREDENTIALS_DIR = self.tempdir.name

    def tearDown(self):
        config.CREDENTIALS_DIR = self.orig_dir
        self.tempdir.cleanup()

    def test_save_and_load_credentials(self):
        creds = {
            "access_token": "abc123",
            "refresh_token": "def456",
            "user_email": "test@example.com",
        }
        storage.save_credentials(creds)
        loaded = storage.load_credentials()
        self.assertEqual(loaded, creds)

    def test_delete_credentials(self):
        creds = {"access_token": "x"}
        storage.save_credentials(creds)
        p = Path(config.CREDENTIALS_DIR) / config.CREDENTIALS_FILE_NAME
        self.assertTrue(p.exists())
        storage.delete_credentials()
        self.assertFalse(p.exists())


if __name__ == "__main__":
    unittest.main()
