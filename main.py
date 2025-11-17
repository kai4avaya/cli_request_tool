"""Main entry point for Tito CLI"""

import sys
from cli import (
    cmd_login, cmd_logout, cmd_status, cmd_leaderboard, 
    cmd_submit, show_help
)
from config import DEFAULT_LEADERBOARD_LIMIT


def parse_submit_args(args):
    """Parse submit command arguments"""
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
    
    return {
        "successful_submissions": successful_submissions,
        "overall_score": overall_score,
        "optimization_score": optimization_score,
        "accuracy_score": accuracy_score,
    }


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        show_help()
        sys.exit(0)
    
    command = sys.argv[1]
    
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
        args = parse_submit_args(sys.argv[2:])
        cmd_submit(**args)
    elif command == "help":
        show_help()
    else:
        print(f"Error: Unknown command '{command}'")
        show_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
