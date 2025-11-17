"""Tests for core.leaderboard module in cli_draft2."""
import unittest
from unittest.mock import patch
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.leaderboard import fetch_leaderboard, submit_score


class TestCoreLeaderboard(unittest.TestCase):

    @patch('requests.get')
    def test_fetch_leaderboard_success(self, mock_get):
        mock_response = mock_get.return_value
        mock_response.json.return_value = {
            "success": True,
            "data": [
                {"user_id": "u1", "overall_score": 100.0}
            ]
        }
        mock_response.raise_for_status = lambda: None

        result = fetch_leaderboard(limit=10)
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 1)

    @patch('requests.get')
    def test_fetch_leaderboard_error(self, mock_get):
        mock_response = mock_get.return_value
        mock_response.raise_for_status.side_effect = Exception("500")
        result = fetch_leaderboard()
        self.assertIsNone(result)

    @patch('core.auth.get_token')
    @patch('requests.post')
    def test_submit_score_success(self, mock_post, mock_token):
        mock_token.return_value = "token-1"
        mock_response = mock_post.return_value
        mock_response.raise_for_status = lambda: None
        result = submit_score(overall_score=100.0)
        self.assertTrue(result)

    @patch('core.auth.get_token')
    def test_submit_score_no_auth(self, mock_token):
        mock_token.return_value = None
        result = submit_score(overall_score=100.0)
        self.assertFalse(result)

    @patch('core.auth.get_token')
    def test_submit_score_no_fields(self, mock_token):
        mock_token.return_value = "token-1"
        result = submit_score()
        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()
