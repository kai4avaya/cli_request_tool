"""Authentication and session management"""

import json
import os
from pathlib import Path
import requests
from config import ENDPOINTS


def get_config_dir():
    """Get the config directory path"""
    home = Path.home()
    config_dir = home / ".tito"
    config_dir.mkdir(exist_ok=True, mode=0o700)
    return config_dir


def get_session_file_path():
    """Get the path to the session file"""
    return get_config_dir() / "session.json"


def save_session(session_data):
    """Save session data to JSON file"""
    try:
        session_path = get_session_file_path()
        session_path.write_text(json.dumps(session_data, indent=2))
        os.chmod(session_path, 0o600)
        return True
    except Exception as e:
        print(f"Warning: Could not save session: {e}")
        return False


def load_session():
    """Load session data from JSON file"""
    try:
        session_path = get_session_file_path()
        if session_path.exists():
            return json.loads(session_path.read_text())
    except Exception as e:
        pass
    return None


def clear_session():
    """Clear session data"""
    try:
        session_path = get_session_file_path()
        if session_path.exists():
            session_path.unlink()
            return True
    except Exception:
        pass
    return False


def get_token():
    """Get access token from session"""
    session = load_session()
    if session:
        return session.get("access_token")
    return None


def login(email, password):
    """Authenticate and return session data"""
    try:
        response = requests.post(
            ENDPOINTS["login"],
            json={"email": email, "password": password}
        )
        response.raise_for_status()
        
        data = response.json()
        token = data.get("access_token")
        user_id = data.get("user", {}).get("id")
        
        if not token:
            print("Login failed: No token in response.")
            return None
        
        return {
            "access_token": token,
            "user_id": user_id,
        }
    except requests.exceptions.HTTPError as e:
        if e.response:
            try:
                error_msg = e.response.json().get("error", str(e))
            except:
                error_msg = e.response.text or str(e)
            print(f"Login failed: {error_msg}")
        else:
            print(f"Login failed: {e}")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None
