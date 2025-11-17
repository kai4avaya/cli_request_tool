"""Tests for authentication module"""

import unittest
from unittest.mock import patch, mock_open
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from auth import save_session, load_session, clear_session, get_token, login


class TestAuth(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_session = {
            "access_token": "test_token_123",
            "user_id": "test_user_456"
        }
    
    @patch('auth.get_session_file_path')
    @patch('builtins.open', new_callable=mock_open)
    @patch('os.chmod')
    def test_save_session(self, mock_chmod, mock_file, mock_path):
        """Test saving session"""
        mock_path.return_value = Path("/tmp/test_session.json")
        
        result = save_session(self.test_session)
        
        self.assertTrue(result)
        mock_file.assert_called_once()
        mock_chmod.assert_called_once()
    
    @patch('auth.get_session_file_path')
    def test_load_session_exists(self, mock_path):
        """Test loading existing session"""
        mock_path.return_value = Path("/tmp/test_session.json")
        
        with patch('builtins.open', mock_open(read_data=json.dumps(self.test_session))):
            result = load_session()
        
        self.assertEqual(result, self.test_session)
    
    @patch('auth.get_session_file_path')
    def test_load_session_not_exists(self, mock_path):
        """Test loading non-existent session"""
        mock_path.return_value = Path("/tmp/nonexistent.json")
        
        with patch('pathlib.Path.exists', return_value=False):
            result = load_session()
        
        self.assertIsNone(result)
    
    @patch('auth.get_session_file_path')
    def test_clear_session(self, mock_path):
        """Test clearing session"""
        mock_path.return_value = Path("/tmp/test_session.json")
        
        with patch('pathlib.Path.exists', return_value=True):
            with patch('pathlib.Path.unlink') as mock_unlink:
                result = clear_session()
        
        self.assertTrue(result)
        mock_unlink.assert_called_once()
    
    @patch('auth.load_session')
    def test_get_token(self, mock_load):
        """Test getting token from session"""
        mock_load.return_value = self.test_session
        
        token = get_token()
        
        self.assertEqual(token, "test_token_123")
    
    @patch('auth.load_session')
    def test_get_token_no_session(self, mock_load):
        """Test getting token when no session exists"""
        mock_load.return_value = None
        
        token = get_token()
        
        self.assertIsNone(token)
    
    @patch('requests.post')
    def test_login_success(self, mock_post):
        """Test successful login"""
        mock_response = mock_post.return_value
        mock_response.json.return_value = {
            "access_token": "new_token",
            "user": {"id": "user_123"}
        }
        mock_response.raise_for_status = lambda: None
        
        result = login("test@example.com", "password")
        
        self.assertIsNotNone(result)
        self.assertEqual(result["access_token"], "new_token")
        self.assertEqual(result["user_id"], "user_123")
    
    @patch('requests.post')
    def test_login_failure(self, mock_post):
        """Test failed login"""
        mock_response = mock_post.return_value
        mock_response.json.return_value = {"error": "Invalid credentials"}
        mock_response.raise_for_status.side_effect = Exception("401")
        mock_response.text = "Unauthorized"
        
        result = login("test@example.com", "wrong")
        
        self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()
