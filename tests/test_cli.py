"""Tests for CLI module"""

import unittest
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from cli import cmd_status, cmd_leaderboard
from auth import load_session


class TestCLI(unittest.TestCase):
    
    @patch('cli.load_session')
    def test_cmd_status_logged_in(self, mock_load):
        """Test status command when logged in"""
        mock_load.return_value = {
            "access_token": "token_12345678901234567890",
            "user_id": "user_12345678"
        }
        
        # Capture print output
        with patch('builtins.print') as mock_print:
            cmd_status()
        
        mock_print.assert_called()
        call_args = str(mock_print.call_args)
        self.assertIn("Logged in", call_args)
    
    @patch('cli.load_session')
    def test_cmd_status_not_logged_in(self, mock_load):
        """Test status command when not logged in"""
        mock_load.return_value = None
        
        with patch('builtins.print') as mock_print:
            cmd_status()
        
        mock_print.assert_called_with("Not logged in.")
    
    @patch('cli.fetch_leaderboard')
    def test_cmd_leaderboard_empty(self, mock_fetch):
        """Test leaderboard command with empty data"""
        mock_fetch.return_value = []
        
        with patch('builtins.print') as mock_print:
            cmd_leaderboard()
        
        mock_print.assert_any_call("Leaderboard is empty.")
    
    @patch('cli.fetch_leaderboard')
    def test_cmd_leaderboard_with_data(self, mock_fetch):
        """Test leaderboard command with data"""
        mock_fetch.return_value = [
            {
                "user_id": "user123",
                "overall_score": 100.0,
                "optimization_score": 80.0,
                "accuracy_score": 0.95,
                "successful_submissions": 10
            }
        ]
        
        with patch('builtins.print') as mock_print:
            cmd_leaderboard(limit=1)
        
        # Should print header and data
        self.assertTrue(mock_print.called)


if __name__ == '__main__':
    unittest.main()
