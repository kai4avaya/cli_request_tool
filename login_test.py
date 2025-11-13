import sys
import getpass
import requests
from pathlib import Path
import os
import json
from config import API_BASE_URL, ENDPOINTS, DEFAULT_LEADERBOARD_LIMIT

# ============================================================================
# SESSION PERSISTENCE UTILITIES
# ============================================================================

def get_config_dir():
    """Get the config directory path"""
    home = Path.home()
    config_dir = home / ".tito"
    config_dir.mkdir(exist_ok=True, mode=0o700)  # Create with secure permissions
    return config_dir

def get_session_file_path():
    """Get the path to the session file"""
    return get_config_dir() / "session.json"

def get_old_token_file_path():
    """Get the path to the old token file (for migration)"""
    return get_config_dir() / "token"

def save_session(session_data):
    """Save session data to JSON file"""
    try:
        session_path = get_session_file_path()
        session_path.write_text(json.dumps(session_data, indent=2))
        os.chmod(session_path, 0o600)  # Secure file permissions
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
    except json.JSONDecodeError as e:
        print(f"Warning: Invalid session file format: {e}")
    except Exception as e:
        print(f"Could not load session: {e}")
    return None

def migrate_old_token():
    """Migrate old token file to new session format"""
    old_token_path = get_old_token_file_path()
    if old_token_path.exists():
        try:
            token = old_token_path.read_text().strip()
            if token:
                # Create session with token only (user_id will be set on next login)
                session_data = {
                    "access_token": token,
                    "user_id": None,
                    "expires_in": None
                }
                save_session(session_data)
                old_token_path.unlink()  # Remove old file
                return True
        except Exception as e:
            print(f"Warning: Could not migrate old token: {e}")
    return False

def get_token():
    """Get access token from session (backward compatibility)"""
    session = load_session()
    if session:
        return session.get("access_token")
    
    # Try migrating old token file
    if migrate_old_token():
        session = load_session()
        if session:
            return session.get("access_token")
    
    return None

def get_user_id():
    """Get user ID from session"""
    session = load_session()
    if session:
        return session.get("user_id")
    return None

def clear_session():
    """Clear session data"""
    try:
        session_path = get_session_file_path()
        if session_path.exists():
            session_path.unlink()
            return True
    except Exception as e:
        print(f"Could not clear session: {e}")
    return False

# ============================================================================
# API AUTHENTICATION
# ============================================================================

def api_login(email, password):
    """Authenticate with TinyTorch backend API and return session data"""
    try:
        response = requests.post(
            ENDPOINTS["login"],
            json={"email": email, "password": password}
        )
        response.raise_for_status()
        
        data = response.json()
        token = data.get("access_token")
        user_id = data.get("user", {}).get("id") if isinstance(data.get("user"), dict) else data.get("user_id")
        expires_in = data.get("expires_in")
        
        if not token:
            print("Login failed: No token in response.")
            return None
        
        # Return minimal session data
        session_data = {
            "access_token": token,
            "user_id": user_id,
            "expires_in": expires_in
        }
        
        return session_data
        
    except requests.exceptions.HTTPError as e:
        if e.response is not None:
            try:
                error_msg = e.response.json().get('detail', str(e))
            except:
                error_msg = e.response.text or str(e)
            print(f"Login Failed: {error_msg}")
        else:
            print(f"Login Failed: {e}")
        return None
        
    except requests.exceptions.JSONDecodeError as e:
        print(f"Login Failed: Invalid JSON response from server.")
        return None
        
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

# ============================================================================
# LEADERBOARD API (via Next.js endpoint)
# ============================================================================

def fetch_leaderboard(limit=DEFAULT_LEADERBOARD_LIMIT):
    """Fetch leaderboard data from Next.js API (public read, no auth required)"""
    url = ENDPOINTS["leaderboard"]
    
    params = {"limit": limit}
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        if e.response is not None:
            try:
                error_data = e.response.json()
                error_msg = error_data.get("error", error_data.get("message", str(error_data)))
            except:
                error_msg = e.response.text
            print(f"Error fetching leaderboard: {error_msg}")
        else:
            print(f"Error fetching leaderboard: {e}")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def upsert_leaderboard(successful_submissions=None, overall_score=None, 
                       optimization_score=None, accuracy_score=None):
    """Upsert leaderboard data via Next.js API (requires auth token)"""
    session = load_session()
    if not session:
        print("Error: Not logged in. Run 'tito login' first.")
        return False
    
    token = session.get("access_token")
    if not token:
        print("Error: Token not found in session. Please login again.")
        return False
    
    url = ENDPOINTS["leaderboard"]
    
    # Build payload with only provided fields (user_id handled by API)
    payload = {}
    if successful_submissions is not None:
        payload["successful_submissions"] = successful_submissions
    if overall_score is not None:
        payload["overall_score"] = float(overall_score)
    if optimization_score is not None:
        payload["optimization_score"] = float(optimization_score)
    if accuracy_score is not None:
        payload["accuracy_score"] = float(accuracy_score)
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return True
    except requests.exceptions.HTTPError as e:
        if e.response is not None:
            try:
                error_data = e.response.json()
                error_msg = error_data.get("error", error_data.get("message", str(error_data)))
            except:
                error_msg = e.response.text
            print(f"Error submitting score: {error_msg}")
        else:
            print(f"Error submitting score: {e}")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False

# ============================================================================
# CLI COMMANDS
# ============================================================================

def cmd_login():
    """Handle login command"""
    print(f"Create an account at: {API_BASE_URL}/login")
    
    username = input("Tito username: ")
    if not username:
        print("Username cannot be empty.")
        return
    
    password = getpass.getpass("Password: ")
    if not password:
        print("Password cannot be empty.")
        return
    
    session_data = api_login(username, password)
    if session_data:
        if save_session(session_data):
            print("Login successful! Session saved.")
        else:
            print("Login successful, but session could not be saved.")
    else:
        print("Login failed.")
        sys.exit(1)

def cmd_logout():
    """Handle logout command"""
    if clear_session():
        print("Logged out successfully.")
    else:
        print("No active session found.")

def cmd_status():
    """Check login status"""
    session = load_session()
    if session:
        token = session.get("access_token", "")
        user_id = session.get("user_id")
        if token:
            status = f"Logged in. Token: {token[:20]}..."
            if user_id:
                status += f" User ID: {user_id[:8]}..."
            print(status)
        else:
            print("Session file exists but is invalid.")
    else:
        # Try migrating old token
        token = get_token()
        if token:
            print(f"Logged in (migrated). Token: {token[:20]}...")
        else:
            print("Not logged in.")

def cmd_leaderboard(limit=DEFAULT_LEADERBOARD_LIMIT):
    """Display leaderboard"""
    data = fetch_leaderboard(limit=limit)
    if data is None:
        return
    
    if not data:
        print("Leaderboard is empty.")
        return
    
    print(f"\n{'Rank':<6} {'User ID':<12} {'Score':<12} {'Opt':<10} {'Acc':<10} {'Submissions':<12}")
    print("-" * 70)
    
    for idx, row in enumerate(data, 1):
        user_id = str(row.get("user_id", ""))[:8] + "..."
        overall = row.get("overall_score", 0)
        opt = row.get("optimization_score", 0)
        acc = row.get("accuracy_score", 0)
        subs = row.get("successful_submissions", 0)
        print(f"{idx:<6} {user_id:<12} {overall:<12.4f} {opt:<10.4f} {acc:<10.4f} {subs:<12}")
    print()

def cmd_submit(successful_submissions=None, overall_score=None, 
               optimization_score=None, accuracy_score=None):
    """Submit/update leaderboard score"""
    if all(x is None for x in [successful_submissions, overall_score, 
                                optimization_score, accuracy_score]):
        print("Error: At least one score field required.")
        print("Usage: tito submit --overall-score 100.5 --optimization-score 50.0")
        return
    
    if upsert_leaderboard(
        successful_submissions=successful_submissions,
        overall_score=overall_score,
        optimization_score=optimization_score,
        accuracy_score=accuracy_score
    ):
        print("Score submitted successfully!")
    else:
        print("Failed to submit score.")
        sys.exit(1)

def show_help():
    """Print help message"""
    print("Tito CLI Tool")
    print("Usage: python login_test.py [COMMAND] [OPTIONS]")
    print("\nCommands:")
    print("  login              : Login to Tito")
    print("  logout             : Logout from Tito")
    print("  status             : Check login status")
    print("  leaderboard [N]     : Display top N leaderboard entries (default: 10)")
    print("  submit             : Submit/update your leaderboard score")
    print("    --overall-score NUM          : Overall score")
    print("    --optimization-score NUM    : Optimization score")
    print("    --accuracy-score NUM        : Accuracy score")
    print("    --successful-submissions NUM: Number of successful submissions")
    print("  help               : Show this help message")
    print("\nExamples:")
    print("  tito leaderboard 20")
    print("  tito submit --overall-score 100.5 --optimization-score 50.0")

# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    """Main entry point for CLI"""
    try:
        command = sys.argv[1] if len(sys.argv) > 1 else "help"
    except IndexError:
        command = "help"
    
    if command == "login":
        cmd_login()
    elif command == "logout":
        cmd_logout()
    elif command == "status":
        cmd_status()
    elif command == "leaderboard":
        try:
            limit = int(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_LEADERBOARD_LIMIT
        except (IndexError, ValueError):
            limit = DEFAULT_LEADERBOARD_LIMIT
        cmd_leaderboard(limit=limit)
    elif command == "submit":
        # Parse arguments
        args = sys.argv[2:]
        successful_submissions = None
        overall_score = None
        optimization_score = None
        accuracy_score = None
        
        i = 0
        while i < len(args):
            if args[i] == "--successful-submissions" and i + 1 < len(args):
                successful_submissions = int(args[i + 1])
                i += 2
            elif args[i] == "--overall-score" and i + 1 < len(args):
                overall_score = float(args[i + 1])
                i += 2
            elif args[i] == "--optimization-score" and i + 1 < len(args):
                optimization_score = float(args[i + 1])
                i += 2
            elif args[i] == "--accuracy-score" and i + 1 < len(args):
                accuracy_score = float(args[i + 1])
                i += 2
            else:
                i += 1
        
        cmd_submit(
            successful_submissions=successful_submissions,
            overall_score=overall_score,
            optimization_score=optimization_score,
            accuracy_score=accuracy_score
        )
    elif command == "help":
        show_help()
    else:
        print(f"Error: Unknown command '{command}'")
        show_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
