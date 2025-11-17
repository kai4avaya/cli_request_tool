"""CLI command handlers"""

import getpass
import sys
from auth import login, save_session, clear_session, load_session, get_token
from leaderboard import fetch_leaderboard, submit_score
from config import API_BASE_URL, DEFAULT_LEADERBOARD_LIMIT


def cmd_login():
    """Handle login command"""
    print(f"Create an account at: {API_BASE_URL}/login")
    
    email = input("Email: ")
    if not email:
        print("Email cannot be empty.")
        return
    
    password = getpass.getpass("Password: ")
    if not password:
        print("Password cannot be empty.")
        return
    
    session_data = login(email, password)
    if session_data:
        if save_session(session_data):
            print("Login successful!")
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


def cmd_submit(overall_score=None, optimization_score=None, 
               accuracy_score=None, successful_submissions=None):
    """Submit/update leaderboard score"""
    if submit_score(
        overall_score=overall_score,
        optimization_score=optimization_score,
        accuracy_score=accuracy_score,
        successful_submissions=successful_submissions
    ):
        print("Score submitted successfully!")
    else:
        print("Failed to submit score.")
        sys.exit(1)


def show_help():
    """Print help message"""
    print("Tito CLI Tool")
    print("Usage: tito [COMMAND] [OPTIONS]")
    print("\nCommands:")
    print("  login              : Login to Tito")
    print("  logout             : Logout from Tito")
    print("  status             : Check login status")
    print("  leaderboard [N]    : Display top N leaderboard entries (default: 10)")
    print("  submit             : Submit/update your leaderboard score")
    print("    --overall-score NUM          : Overall score")
    print("    --optimization-score NUM    : Optimization score")
    print("    --accuracy-score NUM        : Accuracy score")
    print("    --successful-submissions NUM: Number of successful submissions")
    print("  help               : Show this help message")
    print("\nExamples:")
    print("  tito leaderboard 20")
    print("  tito submit --overall-score 100.5 --optimization-score 50.0")
