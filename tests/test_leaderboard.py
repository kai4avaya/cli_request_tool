"""Tests for leaderboard module"""

import unittest
from unittest.mock import patch
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from leaderboard import fetch_leaderboard, submit_score


class TestLeaderboard(unittest.TestCase):
    
    @patch('requests.get')
    def test_fetch_leaderboard_success(self, mock_get):
        """Test successful leaderboard fetch"""
        mock_response = mock_get.return_value
        mock_response.json.return_value = {
            "success": True,
            "data": [
                {
                    "user_id": "user1",
                    "overall_score": 100.0,
                    "optimization_score": 80.0,
                    "accuracy_score": 0.95,
                    "successful_submissions": 10
                }
            ]
        }
        mock_response.raise_for_status = lambda: None
        
        result = fetch_leaderboard(limit=10)
        
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["user_id"], "user1")
        mock_get.assert_called_once()
    
    @patch('requests.get')
    def test_fetch_leaderboard_error(self, mock_get):
        """Test leaderboard fetch error"""
        mock_response = mock_get.return_value
        mock_response.json.return_value = {"error": "Server error"}
        mock_response.raise_for_status.side_effect = Exception("500")
        mock_response.text = "Internal Server Error"
        
        result = fetch_leaderboard()
        
        self.assertIsNone(result)
    
    @patch('leaderboard.get_token')
    @patch('requests.post')
    def test_submit_score_success(self, mock_post, mock_token):
        """Test successful score submission"""
        mock_token.return_value = "test_token"
        mock_response = mock_post.return_value
        mock_response.raise_for_status = lambda: None
        
        result = submit_score(overall_score=100.0)
        
        self.assertTrue(result)
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        self.assertIn("Authorization", call_args[1]["headers"])
        self.assertEqual(call_args[1]["json"]["overall_score"], 100.0)
    
    @patch('leaderboard.get_token')
    def test_submit_score_no_auth(self, mock_token):
        """Test score submission without authentication"""
        mock_token.return_value = None
        
        result = submit_score(overall_score=100.0)
        
        self.assertFalse(result)
    
    @patch('leaderboard.get_token')
    def test_submit_score_no_fields(self, mock_token):
        """Test score submission with no fields"""
        mock_token.return_value = "test_token"
        
        result = submit_score()
        
        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()
