"""Shared configuration for Tito CLI"""

from pathlib import Path
import os

# API Configuration
API_BASE_URL = "https://tinytorch.netlify.app"

# API Endpoints
ENDPOINTS = {
    "login": f"{API_BASE_URL}/api/auth/login",
    "leaderboard": f"{API_BASE_URL}/api/leaderboard",
    # Web bridge used for CLI loopback/OAuth style login
    "cli_login": f"{API_BASE_URL}/cli-login",
}

# Defaults for CLI behavior and local auth server
LOCAL_SERVER_HOST = "127.0.0.1"
AUTH_START_PORT = 54321
AUTH_PORT_HUNT_RANGE = 100
AUTH_CALLBACK_PATH = "/callback"

# Credentials storage
# Can be overridden with environment variable TINOTORCH_CREDENTIALS_DIR
CREDENTIALS_DIR = os.getenv("TINOTORCH_CREDENTIALS_DIR", str(Path.home() / ".tinytorch"))
CREDENTIALS_FILE_NAME = "credentials.json"

# Defaults
DEFAULT_LEADERBOARD_LIMIT = 10
