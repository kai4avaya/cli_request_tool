"""Tests for the CLI commands in cli_draft2/main.py using Typer runner."""
import unittest
from unittest.mock import patch
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from typer.testing import CliRunner
from main import app
from core import auth as core_auth
from core import leaderboard as core_leaderboard
from core import auth_server as core_auth_server


class TestCLICommands(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()

    @patch("core.auth.load_session")
    def test_status_logged_in(self, mock_load):
        mock_load.return_value = {"access_token": "t", "user_email": "a@b.c"}
        result = self.runner.invoke(app, ["status"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Logged in as", result.stdout)

    @patch("core.auth.load_session")
    def test_status_not_logged_in(self, mock_load):
        mock_load.return_value = None
        result = self.runner.invoke(app, ["status"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Not logged in.", result.stdout)

    @patch("core.auth.clear_session")
    def test_logout(self, mock_clear):
        mock_clear.return_value = True
        result = self.runner.invoke(app, ["logout"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Logged out.", result.stdout)

    @patch("core.leaderboard.fetch_leaderboard")
    def test_leaderboard_empty(self, mock_fetch):
        mock_fetch.return_value = []
        result = self.runner.invoke(app, ["leaderboard", "show"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Leaderboard is empty.", result.stdout)

    @patch("core.leaderboard.fetch_leaderboard")
    def test_leaderboard_with_data(self, mock_fetch):
        mock_fetch.return_value = [
            {"user_id": "u1", "overall_score": 12}
        ]
        result = self.runner.invoke(app, ["leaderboard", "show", "--limit", "1"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Leaderboard:", result.stdout)

    @patch("core.auth.get_token")
    @patch("core.leaderboard.submit_score")
    def test_leaderboard_submit(self, mock_submit, mock_get_token):
        mock_get_token.return_value = "token-abc"
        mock_submit.return_value = True
        result = self.runner.invoke(app, ["leaderboard", "submit", "--overall-score", "42"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Submitted leaderboard score.", result.stdout)

    @patch("core.auth.is_logged_in")
    @patch("core.auth.load_session")
    def test_login_already_logged_in(self, mock_load, mock_is_logged_in):
        mock_is_logged_in.return_value = True
        mock_load.return_value = {"access_token": "t", "user_email": "a@b.c"}
        result = self.runner.invoke(app, ["login"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Already logged in as", result.stdout)

    @patch("core.auth.is_logged_in")
    @patch("core.auth_server.AuthReceiver")
    @patch("webbrowser.open")
    def test_login_flow(self, mock_open, mock_receiver_class, mock_is_logged_in):
        mock_is_logged_in.return_value = False
        # Fake receiver instance
        receiver = mock_receiver_class.return_value
        receiver.start.return_value = 12345
        receiver.wait_for_tokens.return_value = {
            "access_token": "tk",
            "refresh_token": "rf",
            "user_email": "test@a.com"
        }
        result = self.runner.invoke(app, ["login"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Opening browser", result.stdout)
        self.assertIn("Success! Logged in", result.stdout)


if __name__ == "__main__":
    unittest.main()
